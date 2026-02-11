#!/usr/bin/env python3
"""
audit_hygiene.py

Read-only audit of all ACP JSONLD files. Reports every data quality issue
across six categories:

  1. Primordial ID format (underscore vs hyphen)
  2. rel: prefix on relationship types
  3. Undefined primordial references
  4. Broken relationship targets
  5. Missing bidirectional reverse links (CULTURAL_ECHO)
  6. Missing instantiates field

Outputs a structured JSON report to outputs/hygiene_audit.json.

Usage (from project root):
    python scripts/hygiene/audit_hygiene.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CANONICAL_PRIMORDIALS = {
    "primordial:creator", "primordial:destroyer", "primordial:preserver",
    "primordial:trickster", "primordial:hero", "primordial:self",
    "primordial:great-mother", "primordial:great-father", "primordial:divine-child",
    "primordial:lover", "primordial:warrior", "primordial:magician",
    "primordial:sovereign", "primordial:maiden", "primordial:crone",
    "primordial:wise-elder", "primordial:psychopomp", "primordial:healer",
    "primordial:rebel", "primordial:shadow", "primordial:outcast",
    "primordial:ancestor", "primordial:monster", "primordial:twin",
}

UNDERSCORE_PRIMORDIALS = {
    "primordial:divine_child": "primordial:divine-child",
    "primordial:great_mother": "primordial:great-mother",
    "primordial:great_father": "primordial:great-father",
    "primordial:wise_elder": "primordial:wise-elder",
}


# ---------------------------------------------------------------------------
# File discovery & loading
# ---------------------------------------------------------------------------

def find_project_root():
    script_dir = Path(__file__).resolve().parent
    for candidate in [script_dir.parent.parent, Path.cwd()]:
        if (candidate / "ACP").is_dir():
            return candidate
    raise FileNotFoundError("Cannot find project root (directory containing ACP/).")


def discover_jsonld_files(root):
    return sorted((root / "ACP").rglob("*.jsonld"))


def load_jsonld(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_entries(data):
    if isinstance(data, dict):
        if "entries" in data and isinstance(data["entries"], list):
            for entry in data["entries"]:
                if isinstance(entry, dict):
                    yield entry
        elif "@graph" in data and isinstance(data["@graph"], list):
            for entry in data["@graph"]:
                if isinstance(entry, dict):
                    yield entry
        elif "@id" in data:
            yield data
    elif isinstance(data, list):
        for item in data:
            yield from extract_entries(item)


# ---------------------------------------------------------------------------
# Audit logic
# ---------------------------------------------------------------------------

def audit_all(root):
    files = discover_jsonld_files(root)
    all_ids = set()
    file_data = {}

    # Issue collectors
    issue1_underscore_ids = []     # {file, entry_id, field, old_value}
    issue2_rel_prefix = []         # {file, entry_id, type_value}
    issue3_undefined_primordials = []  # {file, entry_id, primordial}
    issue4_broken_targets = []     # {file, entry_id, target, rel_type}
    issue5_missing_reverse = []    # will be computed after full scan
    issue6_missing_instantiates = []  # {file, entry_id, name}

    # For reverse-link analysis
    echo_pairs = set()   # (source, target) for CULTURAL_ECHO
    entry_ids_with_rels = {}  # entry_id -> file path

    # Pass 1: collect all @ids
    for path in files:
        try:
            data = load_jsonld(path)
        except Exception as e:
            print(f"  [WARN] Could not parse {path.relative_to(root)}: {e}")
            continue
        file_data[path] = data
        for entry in extract_entries(data):
            eid = entry.get("@id")
            if eid:
                all_ids.add(eid)

    # Pass 2: check issues
    for path, data in file_data.items():
        rel_path = str(path.relative_to(root))
        for entry in extract_entries(data):
            eid = entry.get("@id", "?")

            # Issue 1: Underscore primordial IDs in instantiates
            for inst in entry.get("instantiates", []):
                if isinstance(inst, dict):
                    p = inst.get("primordial", "")
                    if p in UNDERSCORE_PRIMORDIALS:
                        issue1_underscore_ids.append({
                            "file": rel_path, "entry_id": eid,
                            "field": "instantiates[].primordial",
                            "old_value": p,
                            "fix": UNDERSCORE_PRIMORDIALS[p],
                        })

            # Check relationships
            for rel in entry.get("relationships", []):
                rtype = rel.get("type", "")
                target = rel.get("target", "")

                # Issue 1: Underscore primordial IDs in relationship targets
                if isinstance(target, str) and target in UNDERSCORE_PRIMORDIALS:
                    issue1_underscore_ids.append({
                        "file": rel_path, "entry_id": eid,
                        "field": "relationships[].target",
                        "old_value": target,
                        "fix": UNDERSCORE_PRIMORDIALS[target],
                    })

                # Issue 2: rel: prefix on type
                if isinstance(rtype, str) and rtype.startswith("rel:"):
                    issue2_rel_prefix.append({
                        "file": rel_path, "entry_id": eid,
                        "type_value": rtype,
                        "fix": rtype[4:],  # strip "rel:"
                    })

                # Issue 3: Undefined primordial references in targets
                if isinstance(target, str) and target.startswith("primordial:"):
                    normed = UNDERSCORE_PRIMORDIALS.get(target, target)
                    if normed not in CANONICAL_PRIMORDIALS:
                        issue3_undefined_primordials.append({
                            "file": rel_path, "entry_id": eid,
                            "primordial": target,
                        })

                # Issue 4: Broken relationship targets
                if isinstance(target, str) and not target.startswith("primordial:"):
                    if target not in all_ids:
                        # Filter out description-like strings
                        if ":" in target and len(target.split()) <= 5:
                            issue4_broken_targets.append({
                                "file": rel_path, "entry_id": eid,
                                "target": target,
                                "rel_type": rtype.replace("rel:", "") if rtype.startswith("rel:") else rtype,
                            })

                # Issue 5: Collect CULTURAL_ECHO pairs
                clean_type = rtype[4:] if rtype.startswith("rel:") else rtype
                if clean_type == "CULTURAL_ECHO" and isinstance(target, str):
                    echo_pairs.add((eid, target))
                    entry_ids_with_rels[eid] = rel_path

            # Issue 3: Undefined primordials in instantiates
            for inst in entry.get("instantiates", []):
                if isinstance(inst, dict):
                    p = inst.get("primordial", "")
                    normed = UNDERSCORE_PRIMORDIALS.get(p, p)
                    if p.startswith("primordial:") and normed not in CANONICAL_PRIMORDIALS:
                        issue3_undefined_primordials.append({
                            "file": rel_path, "entry_id": eid,
                            "primordial": p,
                        })

            # Issue 6: Missing instantiates
            if entry.get("@type") == "Archetype" and eid and not eid.startswith("primordial:"):
                inst = entry.get("instantiates")
                if not inst or (isinstance(inst, list) and len(inst) == 0):
                    issue6_missing_instantiates.append({
                        "file": rel_path, "entry_id": eid,
                        "name": entry.get("name", "?"),
                    })

    # Issue 5: Find missing reverse links
    for src, tgt in echo_pairs:
        if (tgt, src) not in echo_pairs:
            src_file = entry_ids_with_rels.get(src, "?")
            tgt_file = entry_ids_with_rels.get(tgt, "?")
            issue5_missing_reverse.append({
                "source": src, "target": tgt,
                "source_file": src_file, "target_file": tgt_file,
            })

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files_scanned": len(file_data),
        "total_ids": len(all_ids),
        "summary": {
            "1_underscore_primordial_ids": len(issue1_underscore_ids),
            "2_rel_type_prefix": len(issue2_rel_prefix),
            "3_undefined_primordials": len(issue3_undefined_primordials),
            "4_broken_targets": len(issue4_broken_targets),
            "5_missing_reverse_links": len(issue5_missing_reverse),
            "6_missing_instantiates": len(issue6_missing_instantiates),
            "total_issues": (
                len(issue1_underscore_ids) + len(issue2_rel_prefix) +
                len(issue3_undefined_primordials) + len(issue4_broken_targets) +
                len(issue5_missing_reverse) + len(issue6_missing_instantiates)
            ),
        },
        "issues": {
            "1_underscore_primordial_ids": issue1_underscore_ids,
            "2_rel_type_prefix": issue2_rel_prefix,
            "3_undefined_primordials": issue3_undefined_primordials,
            "4_broken_targets": issue4_broken_targets,
            "5_missing_reverse_links": issue5_missing_reverse,
            "6_missing_instantiates": issue6_missing_instantiates,
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("  ACP DATA HYGIENE AUDIT")
    print("=" * 70)

    root = find_project_root()
    print(f"\nProject root: {root}")

    report = audit_all(root)

    print(f"\nFiles scanned: {report['files_scanned']}")
    print(f"Total @ids:    {report['total_ids']}")
    print()

    s = report["summary"]
    print("Issue Summary:")
    print(f"  1. Underscore primordial IDs:  {s['1_underscore_primordial_ids']}")
    print(f"  2. rel: type prefix:           {s['2_rel_type_prefix']}")
    print(f"  3. Undefined primordials:       {s['3_undefined_primordials']}")
    print(f"  4. Broken relationship targets: {s['4_broken_targets']}")
    print(f"  5. Missing reverse links:       {s['5_missing_reverse_links']}")
    print(f"  6. Missing instantiates:        {s['6_missing_instantiates']}")
    print(f"  ----------------------------------------")
    print(f"  TOTAL:                          {s['total_issues']}")

    # Write report
    out_dir = root / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "hygiene_audit.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"\nReport written to: {out_path.relative_to(root)}")
    print()


if __name__ == "__main__":
    main()
