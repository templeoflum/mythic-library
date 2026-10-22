#!/usr/bin/env python3
"""
Report how the README's published figures compare with the current data.

For each figure, reads the value printed in README.md and recomputes it
from the repo's data, then prints both side by side. Report only: it edits
nothing and always exits 0. A figure that can't be computed (for example,
data/mythic_patterns.db is missing) is shown as "not computed" with the reason.

Figures and where they come from:
  segments          texts/*/*/segments/segments.json
  entities          data/entity_catalog.json
  mentions          data/entities.json
  motif tags        data/motif_tags.json
  motifs (index)    data/thompson_motif_index.json
  motifs (tagged)   distinct codes in data/motif_tags.json
  mapped entities   integration/entity_mapper.py over ACP/ and
                    data/mythic_patterns.db, as validation/v2_run.py does
  separation ratio  Test 2 (primordial clustering), 1000 permutations, as
                    `python -m validation.v2_run --full` does (about a minute)

Usage:
    python scripts/check_published_numbers.py
    python scripts/check_published_numbers.py --skip-slow   # skip the separation ratio
"""

import argparse
import glob
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _num(text: str) -> float:
    return float(text.replace(",", ""))


# name -> (regex on README.md, how to turn the match into a value)
README_FIGURES = {
    "segments": (r"(\d[\d,]*) segments", lambda m: _num(m.group(1))),
    "entities": (r"(\d[\d,]*) entities, [\d,]+ mentions", lambda m: _num(m.group(1))),
    "mentions": (r"(\d[\d,]*) mentions", lambda m: _num(m.group(1))),
    "motif tags": (r"`motif_tags` \| (\d[\d,]*)", lambda m: _num(m.group(1))),
    "motifs (index)": (r"`motifs` \| (\d[\d,]*)", lambda m: _num(m.group(1))),
    "motifs (tagged)": (r"\((\d[\d,]*) motifs, [\d,]+ tags\)", lambda m: _num(m.group(1))),
    "mapped entities": (r"Map (\d+)/\d+ library entities", lambda m: _num(m.group(1))),
    "separation ratio %": (r"\((\d+(?:\.\d+)?)% separation ratio\)", lambda m: _num(m.group(1))),
}


def read_readme_figures(readme_text: str) -> dict:
    """Every value the README prints for each figure, in order of appearance."""
    found = {}
    for name, (pattern, convert) in README_FIGURES.items():
        found[name] = [convert(m) for m in re.finditer(pattern, readme_text)]
    return found


def _load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def count_segments(root: Path) -> int:
    total = 0
    for path in sorted(glob.glob(str(root / "texts" / "*" / "*" / "segments" / "segments.json"))):
        total += len(_load_json(Path(path)).get("segments", []))
    return total


def count_entities(root: Path) -> int:
    return len(_load_json(root / "data" / "entity_catalog.json"))


def count_mentions(root: Path) -> int:
    data = _load_json(root / "data" / "entities.json")
    return sum(len(seg.get("mentions", [])) for text in data for seg in text.get("segments", []))


def _motif_tags(root: Path):
    data = _load_json(root / "data" / "motif_tags.json")
    for text in data:
        for seg in text.get("segments", []):
            yield from seg.get("tags", [])


def count_motif_tags(root: Path) -> int:
    return sum(1 for _ in _motif_tags(root))


def count_tagged_motifs(root: Path) -> int:
    return len({tag["code"] for tag in _motif_tags(root)})


def count_index_motifs(root: Path) -> int:
    return len(_load_json(root / "data" / "thompson_motif_index.json").get("motifs", {}))


def _import_repo(root: Path):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def count_mapped_entities(root: Path) -> int:
    db = root / "data" / "mythic_patterns.db"
    if not db.exists():
        raise FileNotFoundError("data/mythic_patterns.db is missing (build it with scripts/database/create_db.py)")
    _import_repo(root)
    from integration.acp_loader import ACPLoader
    from integration.entity_mapper import EntityMapper
    from integration.library_loader import LibraryLoader

    mapper = EntityMapper(ACPLoader(str(root / "ACP")), LibraryLoader(str(db)))
    return mapper.auto_map_all()["total_mapped"]


def separation_ratio_percent(root: Path) -> float:
    _import_repo(root)
    from integration.acp_loader import ACPLoader
    from validation.v2_tests.primordial_clustering import PrimordialClusteringTest

    result = PrimordialClusteringTest(ACPLoader(str(root / "ACP"))).run(n_permutations=1000)
    return round(result["cluster_analysis"]["separation_ratio"] * 100, 1)


COMPUTERS = {
    "segments": count_segments,
    "entities": count_entities,
    "mentions": count_mentions,
    "motif tags": count_motif_tags,
    "motifs (index)": count_index_motifs,
    "motifs (tagged)": count_tagged_motifs,
    "mapped entities": count_mapped_entities,
    "separation ratio %": separation_ratio_percent,
}

SLOW = {"separation ratio %"}


def compare(root: Path, skip_slow: bool = False) -> list[dict]:
    """One row per figure: README values, current value, and whether they agree."""
    readme = read_readme_figures((root / "README.md").read_text(encoding="utf-8"))
    rows = []
    for name, compute in COMPUTERS.items():
        row = {"figure": name, "readme": readme.get(name, []), "current": None, "note": ""}
        if skip_slow and name in SLOW:
            row["note"] = "not computed: skipped (--skip-slow)"
        else:
            try:
                row["current"] = compute(root)
            except Exception as exc:  # report, never fail
                row["note"] = f"not computed: {exc}"
        if row["current"] is not None:
            if not row["readme"]:
                row["note"] = "not found in README"
            else:
                # The README rounds the separation ratio to a whole percent
                current = round(row["current"]) if name == "separation ratio %" else row["current"]
                row["note"] = "same" if all(v == current for v in row["readme"]) else "DIFFERS"
        rows.append(row)
    return rows


def _fmt(value) -> str:
    if value is None:
        return "-"
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return f"{value:,}" if isinstance(value, int) else str(value)


def format_report(rows: list[dict]) -> str:
    lines = [f"{'figure':<20} {'README':<16} {'current':<10} note", "-" * 60]
    for row in rows:
        readme = " / ".join(_fmt(v) for v in row["readme"]) or "-"
        lines.append(f"{row['figure']:<20} {readme:<16} {_fmt(row['current']):<10} {row['note']}")
    differs = sum(1 for r in rows if r["note"] == "DIFFERS")
    lines.append("")
    lines.append(f"{differs} of {len(rows)} figures differ from the README. Report only; nothing was changed.")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--skip-slow", action="store_true",
                        help="skip the separation ratio (Test 2 with 1000 permutations)")
    parser.add_argument("--root", default=str(PROJECT_ROOT), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        print(format_report(compare(Path(args.root), skip_slow=args.skip_slow)))
    except Exception as exc:  # report only: never fail the caller
        print(f"check_published_numbers: could not run: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
