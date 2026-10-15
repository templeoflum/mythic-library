#!/usr/bin/env python3
"""Offline negative regression checks for an explicitly supplied edition candidate.

A clean, isolated positive control must pass first. Every deliberate defect is
then applied to a fresh local copy and must fail at its expected gate. No source
fixture, edition identifier, title count, or machine-specific path is embedded.
"""
from pathlib import Path
import argparse
import copy
import json
import shutil
import sys
import tempfile

from edition_pipeline import GateError, dump, pin, protected_files, read, require, validate


class NotApplicable(Exception):
    """A valid candidate lacks the baseline fixture needed by one negative case."""


def clone_candidate(source, target):
    """Copy only the reader/check inputs; never copy Git or private audit trees."""
    for folder in ("dist", "scripts", "tests", ".openai", "maintenance"):
        if (source / folder).is_dir():
            shutil.copytree(source / folder, target / folder)
    if (source / ".gitignore").is_file():
        shutil.copy2(source / ".gitignore", target / ".gitignore")


def change_json(root, relative, mutation):
    data = read(root / relative)
    mutation(data)
    dump(root / relative, data)


def damage_file(path):
    """Guarantee a changed pin, including for empty or arbitrary binary files."""
    raw = path.read_bytes()
    path.write_bytes(bytes([raw[0] ^ 1]) + raw[1:] if raw else b"!")


def old_book(baseline):
    if not baseline["catalog"]:
        raise NotApplicable("The baseline contains no prior editions")
    return baseline["catalog"][0]


def change_old_source(root, baseline, imports):
    damage_file(root / "dist" / old_book(baseline)["path"])


def change_old_metadata(root, baseline, imports):
    old_book(baseline)
    change_json(root, "dist/catalog.json", lambda data: data[0].update(
        author=str(data[0].get("author", "")) + " [unreviewed negative fixture]"))


def change_bookmark(root, baseline, imports):
    book = next((book for book in baseline["catalog"]
                 if baseline["sections"]["books"][book["id"]]["sections"]), None)
    if book is None:
        raise NotApplicable("The baseline contains no prior section bookmarks")
    def mutate(data):
        section = data["books"][book["id"]]["sections"][0]
        section["end"] += 1
    change_json(root, "dist/sections.json", mutate)


def change_ui(root, baseline, imports):
    relative = next((path for path in sorted(baseline["files"])
                     if path.startswith("dist/") and not path.startswith("dist/books/")
                     and Path(path).suffix in (".js", ".css", ".html")), None)
    if relative is None:
        raise NotApplicable("The baseline contains no protected UI file")
    damage_file(root / relative)


def add_runtime_file(root, baseline, imports):
    path = root / "dist" / "negative-gate-unapproved.js"
    while path.exists():
        path = path.with_name("extra-" + path.name)
    path.write_text("// Deliberate unapproved runtime fixture.\n", encoding="utf-8")


def damage_new_source(root, baseline, imports):
    damage_file(root / "dist" / imports[0]["catalog"]["path"])


def unavailable_stub(root, baseline, imports):
    imports[0]["catalog"]["available"] = False


def wrong_primary_count(root, baseline, imports):
    imports[0]["spec"]["primarySectionCount"] += 1


def unsafe_path(root, baseline, imports):
    imports[0]["runtime_assets"][0]["target"] = "../negative-gate-outside.txt"


def missing_anchor(root, baseline, imports):
    # The first anchored boundary starts at source offset zero and may have no
    # line. Pick an actual later line anchor instead of a fixed section index.
    choice = next(((imp, section) for imp in imports
                   for section in imp["spec"]["sections"][1:] if "line" in section), None)
    if choice is None:
        raise NotApplicable("The imports contain no noninitial line anchor")
    imp, section = choice
    source = (root / "dist" / imp["catalog"]["path"]).read_text(encoding="utf-8")
    absent = "NEGATIVE_GATE_NONEXISTENT_ANCHOR"
    while absent in source:
        absent += "_X"
    section["line"] = absent
    change_json(root, "scripts/edition_specs.json",
                lambda data: data["editions"].update({imp["catalog"]["id"]: imp["spec"]}))


def private_metadata(root, baseline, imports):
    imports[0]["catalog"]["edition_note"] = "See file:///negative-gate-private-audit"



def private_reader_attribution(root, baseline, imports):
    choice = next(((imp, section) for imp in imports
                   for section in imp["spec"]["sections"]
                   if section.get("kind") == "primary" and "line" in section), None)
    if choice is None:
        raise NotApplicable("The imports contain no primary line anchor")
    imp, section = choice
    attribution = copy.deepcopy(section.get("readerAttribution") or {})
    attribution.update(display="See file:///negative-gate-private-attribution",
                       sourceEvidence=section["line"])
    section["readerAttribution"] = attribution
    change_json(root, "scripts/edition_specs.json",
                lambda data: data["editions"].update({imp["catalog"]["id"]: imp["spec"]}))
    def mutate_manifest(data):
        installed = next(item for item in data["books"][imp["catalog"]["id"]]["sections"]
                         if item["id"] == section["id"])
        installed["sourceAttribution"] = copy.deepcopy(attribution)
    change_json(root, "dist/sections.json", mutate_manifest)


def executable_asset(root, baseline, imports):
    imports[0]["runtime_assets"][0]["target"] = "books/negative-gate-hidden.js"



def need_collection(baseline):
    if not baseline.get("collections"):
        raise NotApplicable("This historical baseline predates the collected catalog")


def unrelated_collection_change(root, baseline, imports):
    need_collection(baseline)
    mapped={imp.get("collection_entry_id") for imp in imports}
    key=next(e["id"] for e in baseline["collections"]["entries"] if e["id"] not in mapped)
    def mutate(data):
        next(e for e in data["entries"] if e["id"]==key)["title"] += " UNREVIEWED"
    change_json(root,"dist/collections.json",mutate)


def missing_collection_mapping(root, baseline, imports):
    need_collection(baseline);imports[0].pop("collection_entry_id",None)


def duplicate_collection_mapping(root, baseline, imports):
    need_collection(baseline)
    if len(imports)<2:raise NotApplicable("This candidate has fewer than two new editions")
    imports[1]["collection_entry_id"]=imports[0]["collection_entry_id"]


def unknown_collection_mapping(root, baseline, imports):
    need_collection(baseline);imports[0]["collection_entry_id"]="negative-gate-nonexistent-entry"


def dishonest_collection_count(root, baseline, imports):
    need_collection(baseline)
    change_json(root,"dist/collections.json",lambda data:data["summary"].update(readable_editions=data["summary"]["readable_editions"]+1))


# Match intended gate diagnostics; an unrelated exception is never a passing test.
CASES = (
    ("old_source_corruption", change_old_source, ("Prior file ", "hash/byte mismatch")),
    ("old_metadata_change", change_old_metadata, ("Prior catalog metadata/order/shelves changed",)),
    ("old_bookmark_drift", change_bookmark, ("Prior sections/bookmark anchors changed:",)),
    ("ui_change", change_ui, ("Prior file ", "hash/byte mismatch")),
    ("unexpected_runtime_file", add_runtime_file, ("Hosted runtime allowlist mismatch:",)),
    ("new_source_corruption", damage_new_source, ("Installed source ", "hash/byte mismatch")),
    ("unavailable_stub", unavailable_stub, ("Stub/unavailable catalog entry forbidden",)),
    ("incorrect_primary_count", wrong_primary_count, ("Primary section count mismatch",)),
    ("path_traversal", unsafe_path, ("Unsafe relative path:",)),
    ("missing_source_anchor", missing_anchor, ("Check failed:", "anchors", "got 0")),
    ("private_metadata_leak", private_metadata, ("Private audit paths in hosted catalog",)),
    ("private_reader_attribution_leak", private_reader_attribution, ("Private audit paths in hosted catalog",)),
    ("executable_source_asset", executable_asset, ("Executable/unapproved source asset type",)),
    ("unrelated_collection_change", unrelated_collection_change, ("Collected catalog differs from exact mapped promotions",)),
    ("missing_collection_mapping", missing_collection_mapping, ("Collected catalog requires explicit collection_entry_id",)),
    ("duplicate_collection_mapping", duplicate_collection_mapping, ("Two editions cannot silently promote the same catalog entry",)),
    ("unknown_collection_mapping", unknown_collection_mapping, ("Mapped collected entry missing or ambiguous",)),
    ("dishonest_collection_count", dishonest_collection_count, ("Collected catalog differs from exact mapped promotions",)),
)


def run_suite(candidate, baseline, imports):
    before = protected_files(candidate)
    with tempfile.TemporaryDirectory(prefix="edition-positive-") as temporary:
        root = Path(temporary)
        clone_candidate(candidate, root)
        positive = validate(root, baseline, copy.deepcopy(imports), True)
    print("positive_control PASSED", flush=True)
    results = []
    for name, mutation, expected in CASES:
        with tempfile.TemporaryDirectory(prefix="edition-negative-") as temporary:
            root = Path(temporary)
            clone_candidate(candidate, root)
            changed_imports = copy.deepcopy(imports)
            try:
                mutation(root, baseline, changed_imports)
            except NotApplicable as error:
                result = {"case": name, "status": "not_applicable", "rejected": False,
                          "reason": str(error)}
            else:
                try:
                    validate(root, baseline, changed_imports, False)
                except GateError as error:
                    reason = str(error)
                    matched = all(fragment in reason for fragment in expected)
                    result = {"case": name, "status": "rejected" if matched else "wrong_gate",
                              "rejected": matched, "reason": reason}
                except Exception as error:
                    result = {"case": name, "status": "unexpected_error", "rejected": False,
                              "reason": type(error).__name__ + ": " + str(error)}
                else:
                    result = {"case": name, "status": "accepted_defect", "rejected": False,
                              "reason": "Gate accepted the deliberate defect"}
            results.append(result)
            print(name, result["status"].upper(), flush=True)
    unchanged = protected_files(candidate) == before
    skipped = sum(result["status"] == "not_applicable" for result in results)
    rejected = sum(result["rejected"] for result in results)
    return {
        "schema_version": 1,
        "passed": unchanged and rejected + skipped == len(results),
        "publication_allowed": False,
        "review_required": True,
        "candidate_unchanged": unchanged,
        "complete_negative_coverage": skipped == 0,
        "positive_control": {key: positive[key] for key in (
            "passed", "baseline_editions", "candidate_editions", "new_editions",
            "preserved_bookmark_endpoints", "full_reader_checks", "checks",
            "baseline_content_sha256", "import_content_sha256")},
        "total_cases": len(results),
        "rejected_cases": rejected,
        "not_applicable_cases": skipped,
        "cases": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--import-json", required=True, action="append", type=Path,
                        help="Verified import; repeat in candidate catalog order for a batch")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    candidate, output = args.candidate.resolve(), args.output.resolve()
    baseline = read(args.baseline)
    imports = [read(path) for path in args.import_json]
    input_paths = [args.baseline, *args.import_json]
    input_paths += [Path(imp["verification"]["report"]) for imp in imports]
    input_paths += [Path(asset["source"]) for imp in imports for asset in imp["runtime_assets"]]
    require(not output.is_relative_to(candidate), "Test output must be outside the candidate")
    require(output not in {path.resolve() for path in input_paths},
            "Test output must not overwrite any input file")
    # Retained source/report and baseline/import files are read-only throughout.
    input_pins = {path.resolve(): pin(path) for path in input_paths}
    result = run_suite(candidate, baseline, imports)
    result["external_inputs_unchanged"] = all(pin(path) == expected
                                             for path, expected in input_pins.items())
    result["passed"] = result["passed"] and result["external_inputs_unchanged"]
    dump(output, result)
    print(json.dumps({key: result[key] for key in (
        "passed", "rejected_cases", "not_applicable_cases", "candidate_unchanged",
        "external_inputs_unchanged", "publication_allowed", "review_required")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (GateError, KeyError, ValueError, OSError) as error:
        print("NEGATIVE SUITE BLOCKED: " + str(error), file=sys.stderr)
        sys.exit(1)
