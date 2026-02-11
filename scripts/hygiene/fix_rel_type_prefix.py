#!/usr/bin/env python3
"""
fix_rel_type_prefix.py

Strips the "rel:" prefix from relationship type values.
  e.g. "type": "rel:CULTURAL_ECHO" -> "type": "CULTURAL_ECHO"

Usage (from project root):
    python scripts/hygiene/fix_rel_type_prefix.py --dry-run
    python scripts/hygiene/fix_rel_type_prefix.py --apply
"""

import json
import argparse
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_project_root():
    script_dir = Path(__file__).resolve().parent
    for candidate in [script_dir.parent.parent, Path.cwd()]:
        if (candidate / "ACP").is_dir():
            return candidate
    raise FileNotFoundError("Cannot find project root (directory containing ACP/).")


def discover_jsonld_files(root):
    return sorted((root / "ACP").rglob("*.jsonld"))


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
# Fix logic
# ---------------------------------------------------------------------------

def fix_file(data, rel_path, apply_mode):
    fixes = []
    for entry in extract_entries(data):
        eid = entry.get("@id", "?")
        for rel in entry.get("relationships", []):
            rtype = rel.get("type", "")
            if isinstance(rtype, str) and rtype.startswith("rel:"):
                new_type = rtype[4:]
                fixes.append({
                    "file": rel_path, "entry": eid,
                    "old": rtype, "new": new_type,
                })
                if apply_mode:
                    rel["type"] = new_type
    return fixes


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Strip rel: prefix from relationship type values."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Report changes without writing.")
    group.add_argument("--apply", action="store_true", help="Apply fixes to JSONLD files.")
    args = parser.parse_args()
    apply_mode = args.apply

    print("=" * 70)
    print("  FIX REL: TYPE PREFIX")
    print("=" * 70)

    root = find_project_root()
    print(f"\nProject root: {root}")
    print(f"Mode: {'APPLY' if apply_mode else 'DRY RUN'}")

    files = discover_jsonld_files(root)
    all_fixes = []
    modified_files = {}

    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"  [WARN] Could not parse {path.relative_to(root)}: {e}")
            continue

        rel_path = str(path.relative_to(root))
        fixes = fix_file(data, rel_path, apply_mode)
        if fixes:
            all_fixes.extend(fixes)
            modified_files[path] = data

    # Report
    print(f"\nFiles scanned: {len(files)}")
    print(f"Issues found:  {len(all_fixes)}")
    print(f"Files affected: {len(modified_files)}")

    if all_fixes:
        # Group by file for compact display
        by_file = {}
        for fix in all_fixes:
            by_file.setdefault(fix["file"], []).append(fix)

        print(f"\n{'─' * 70}")
        for file, fixes in by_file.items():
            action = "FIXED" if apply_mode else "WOULD FIX"
            print(f"  {action}  {file}  ({len(fixes)} occurrences)")
            # Show unique type changes
            types_seen = set()
            for fix in fixes:
                key = (fix["old"], fix["new"])
                if key not in types_seen:
                    types_seen.add(key)
                    print(f"         {fix['old']} → {fix['new']}")

    # Write modified files
    if apply_mode and modified_files:
        print(f"\n{'─' * 70}")
        print(f"Writing {len(modified_files)} files...")
        for path, data in modified_files.items():
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")
            print(f"  Written: {path.relative_to(root)}")

    # Summary
    print(f"\n{'=' * 70}")
    print(f"  SUMMARY: {len(all_fixes)} fixes across {len(modified_files)} files")
    if not apply_mode:
        print(f"  ** DRY RUN — no files modified **")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()
