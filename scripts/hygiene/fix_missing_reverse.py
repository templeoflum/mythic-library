#!/usr/bin/env python3
"""
fix_missing_reverse.py

Adds missing bidirectional reverse links for CULTURAL_ECHO relationships.
If archetype A has CULTURAL_ECHO -> B but B has no CULTURAL_ECHO -> A,
this script adds the reverse link to B with the same fidelity score.

Only processes CULTURAL_ECHO (the most common bidirectional relationship).

Usage (from project root):
    python scripts/hygiene/fix_missing_reverse.py --dry-run
    python scripts/hygiene/fix_missing_reverse.py --apply
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
# Analysis
# ---------------------------------------------------------------------------

def build_echo_map(root):
    """
    Build:
      - echo_pairs: set of (source, target) for all CULTURAL_ECHO rels
      - entry_index: entry_id -> (entry_dict, file_path)
      - file_data: path -> parsed JSON
    """
    echo_pairs = set()
    echo_fidelity = {}  # (source, target) -> fidelity
    entry_index = {}
    file_data = {}

    for path in discover_jsonld_files(root):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"  [WARN] Could not parse {path.relative_to(root)}: {e}")
            continue
        file_data[path] = data

        for entry in extract_entries(data):
            eid = entry.get("@id")
            if eid:
                entry_index[eid] = (entry, path)

            for rel in entry.get("relationships", []):
                rtype = rel.get("type", "")
                # Handle both with and without rel: prefix
                clean_type = rtype[4:] if rtype.startswith("rel:") else rtype
                if clean_type != "CULTURAL_ECHO":
                    continue

                target = rel.get("target", "")
                if not isinstance(target, str) or not target:
                    continue

                echo_pairs.add((eid, target))
                fid = rel.get("fidelity")
                if fid is not None:
                    echo_fidelity[(eid, target)] = fid

    return echo_pairs, echo_fidelity, entry_index, file_data


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Add missing CULTURAL_ECHO reverse links."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Report changes without writing.")
    group.add_argument("--apply", action="store_true", help="Apply fixes to JSONLD files.")
    args = parser.parse_args()
    apply_mode = args.apply

    print("=" * 70)
    print("  FIX MISSING CULTURAL_ECHO REVERSE LINKS")
    print("=" * 70)

    root = find_project_root()
    print(f"\nProject root: {root}")
    print(f"Mode: {'APPLY' if apply_mode else 'DRY RUN'}")

    echo_pairs, echo_fidelity, entry_index, file_data = build_echo_map(root)
    print(f"\nTotal CULTURAL_ECHO links: {len(echo_pairs)}")

    # Find missing reverse links
    missing = []
    for src, tgt in echo_pairs:
        if (tgt, src) not in echo_pairs:
            # Target must exist in the index to add a reverse link
            if tgt in entry_index:
                fidelity = echo_fidelity.get((src, tgt))
                missing.append({
                    "source": src,
                    "target": tgt,
                    "fidelity": fidelity,
                })

    print(f"Missing reverse links: {len(missing)}")

    # Find targets that don't exist in index
    orphan_reverse = []
    for src, tgt in echo_pairs:
        if (tgt, src) not in echo_pairs and tgt not in entry_index:
            orphan_reverse.append({"source": src, "target": tgt})

    if orphan_reverse:
        print(f"Skipped (target not in index): {len(orphan_reverse)}")

    if not missing:
        print("\nNo missing reverse links found!")
        return

    # Apply fixes
    modified_files = set()
    fixes = []

    for item in missing:
        src = item["source"]
        tgt = item["target"]
        fidelity = item["fidelity"]

        tgt_entry, tgt_path = entry_index[tgt]

        # Build the reverse relationship
        reverse_rel = {
            "type": "CULTURAL_ECHO",
            "target": src,
        }
        if fidelity is not None:
            reverse_rel["fidelity"] = fidelity

        action = "ADDED" if apply_mode else "WOULD ADD"
        fid_str = f" (fidelity: {fidelity})" if fidelity is not None else ""
        fixes.append({
            "source": src, "target": tgt,
            "added_to": tgt,
            "file": str(tgt_path.relative_to(root)),
            "fidelity": fidelity,
        })

        if apply_mode:
            if "relationships" not in tgt_entry:
                tgt_entry["relationships"] = []
            tgt_entry["relationships"].append(reverse_rel)
            modified_files.add(tgt_path)

    # Report
    print(f"\n{'─' * 70}")
    for fix in fixes:
        action = "ADDED" if apply_mode else "WOULD ADD"
        fid_str = f" (fidelity: {fix['fidelity']})" if fix["fidelity"] is not None else ""
        print(f"  {action}  {fix['target']} → CULTURAL_ECHO → {fix['source']}{fid_str}")
        print(f"         in {fix['file']}")

    # Write modified files
    if apply_mode and modified_files:
        print(f"\n{'─' * 70}")
        print(f"Writing {len(modified_files)} files...")
        for path in sorted(modified_files):
            data = file_data[path]
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")
            print(f"  Written: {path.relative_to(root)}")

    if orphan_reverse:
        print(f"\n{'─' * 70}")
        print("  SKIPPED (target entry not found in any file):")
        for item in orphan_reverse:
            print(f"    {item['source']} → {item['target']}")

    # Summary
    print(f"\n{'=' * 70}")
    print(f"  SUMMARY: {len(fixes)} reverse links added, {len(modified_files)} files")
    if orphan_reverse:
        print(f"           {len(orphan_reverse)} skipped (target not in index)")
    if not apply_mode:
        print(f"  ** DRY RUN — no files modified **")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()
