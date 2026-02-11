#!/usr/bin/env python3
"""
fix_undefined_primordials.py

Maps undefined primordial references to the canonical 24. Each mapping
preserves the original weight and adds an aspects[] field noting the
specific role the non-canonical primordial described.

Operates on both instantiates[].primordial and relationships[].target.

Usage (from project root):
    python scripts/hygiene/fix_undefined_primordials.py --dry-run
    python scripts/hygiene/fix_undefined_primordials.py --apply
"""

import json
import argparse
from pathlib import Path


# ---------------------------------------------------------------------------
# Mapping table: undefined -> canonical + aspect annotation
# ---------------------------------------------------------------------------

PRIMORDIAL_MAP = {
    # Role-specific variants -> canonical primordials
    "primordial:artisan":              ("primordial:creator",       "craftsmanship"),
    "primordial:berserker":            ("primordial:warrior",       "battle-frenzy"),
    "primordial:cruel-perfectionist":  ("primordial:sovereign",     "perfectionism"),
    "primordial:culture-hero":         ("primordial:hero",          "civilization-bringer"),
    "primordial:deceiver":             ("primordial:trickster",     "deception"),
    "primordial:devouring-mother":     ("primordial:great-mother",  "devouring"),
    "primordial:dying-rising-god":     ("primordial:hero",          "death-rebirth"),
    "primordial:father":               ("primordial:great-father",  None),
    "primordial:fool":                 ("primordial:trickster",     "sacred-foolishness"),
    "primordial:giant":                ("primordial:monster",       "primeval-giant"),
    "primordial:guardian":             ("primordial:warrior",       "protection"),
    "primordial:hermit":               ("primordial:wise-elder",    "solitude"),
    "primordial:jealous-destroyer":    ("primordial:destroyer",     "jealousy"),
    "primordial:judge":                ("primordial:sovereign",     "judgment"),
    "primordial:martyr":               ("primordial:hero",          "self-sacrifice"),
    "primordial:messenger":            ("primordial:psychopomp",    "communication"),
    "primordial:mystic":               ("primordial:magician",      "mysticism"),
    "primordial:nature-spirit":        ("primordial:preserver",     "nature"),
    "primordial:nurturer":             ("primordial:great-mother",  "nurturance"),
    "primordial:primeval-waters":      ("primordial:great-mother",  "primeval-waters"),
    "primordial:sadist":               ("primordial:shadow",        "cruelty"),
    "primordial:sage":                 ("primordial:wise-elder",    None),
    "primordial:seductress-destroyer": ("primordial:destroyer",     "seduction"),
    "primordial:seeker":               ("primordial:hero",          "seeking"),
    "primordial:shade":                ("primordial:shadow",        "ghost"),
    "primordial:sky-father":           ("primordial:great-father",  "sky"),
    "primordial:sorceress":            ("primordial:magician",      "sorcery"),
    "primordial:storyteller":          ("primordial:wise-elder",    "storytelling"),
    "primordial:temptress":            ("primordial:trickster",     "temptation"),
    "primordial:transformer":          ("primordial:magician",      "transformation"),
    "primordial:tyrant":               ("primordial:sovereign",     "tyranny"),
    "primordial:underworld-lord":      ("primordial:psychopomp",    "underworld-rule"),
    "primordial:wild-man":             ("primordial:monster",       "wild-nature"),
    "primordial:witness":              ("primordial:wise-elder",    "witnessing"),
    "primordial:wounded-healer":       ("primordial:healer",        "wounded-healing"),
}


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
    unmapped = []

    for entry in extract_entries(data):
        eid = entry.get("@id", "?")

        # Fix instantiates[].primordial
        for inst in entry.get("instantiates", []):
            if not isinstance(inst, dict):
                continue
            p = inst.get("primordial", "")
            if not p.startswith("primordial:") or p in CANONICAL_PRIMORDIALS:
                continue

            if p in PRIMORDIAL_MAP:
                new_p, aspect = PRIMORDIAL_MAP[p]
                fixes.append({
                    "file": rel_path, "entry": eid,
                    "field": "instantiates[].primordial",
                    "old": p, "new": new_p, "aspect": aspect,
                })
                if apply_mode:
                    inst["primordial"] = new_p
                    if aspect:
                        existing = inst.get("aspects", [])
                        if aspect not in existing:
                            inst["aspects"] = existing + [aspect]
            else:
                unmapped.append({
                    "file": rel_path, "entry": eid,
                    "field": "instantiates[].primordial",
                    "value": p,
                })

        # Fix relationship targets
        for rel in entry.get("relationships", []):
            target = rel.get("target", "")
            if not isinstance(target, str):
                continue
            if not target.startswith("primordial:") or target in CANONICAL_PRIMORDIALS:
                continue

            if target in PRIMORDIAL_MAP:
                new_t, aspect = PRIMORDIAL_MAP[target]
                fixes.append({
                    "file": rel_path, "entry": eid,
                    "field": "relationships[].target",
                    "old": target, "new": new_t, "aspect": aspect,
                })
                if apply_mode:
                    rel["target"] = new_t
                    if aspect and "note" not in rel:
                        rel["note"] = f"Originally: {target} (aspect: {aspect})"
            else:
                unmapped.append({
                    "file": rel_path, "entry": eid,
                    "field": "relationships[].target",
                    "value": target,
                })

    return fixes, unmapped


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Map undefined primordial references to canonical 24."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Report changes without writing.")
    group.add_argument("--apply", action="store_true", help="Apply fixes to JSONLD files.")
    args = parser.parse_args()
    apply_mode = args.apply

    print("=" * 70)
    print("  FIX UNDEFINED PRIMORDIAL REFERENCES")
    print("=" * 70)

    root = find_project_root()
    print(f"\nProject root: {root}")
    print(f"Mode: {'APPLY' if apply_mode else 'DRY RUN'}")
    print(f"Mapping table: {len(PRIMORDIAL_MAP)} entries")

    files = discover_jsonld_files(root)
    all_fixes = []
    all_unmapped = []
    modified_files = {}

    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"  [WARN] Could not parse {path.relative_to(root)}: {e}")
            continue

        rel_path = str(path.relative_to(root))
        fixes, unmapped = fix_file(data, rel_path, apply_mode)
        if fixes:
            all_fixes.extend(fixes)
            modified_files[path] = data
        all_unmapped.extend(unmapped)

    # Report fixes
    print(f"\nFiles scanned:  {len(files)}")
    print(f"Issues found:   {len(all_fixes)}")
    print(f"Files affected: {len(modified_files)}")
    if all_unmapped:
        print(f"UNMAPPED (no mapping entry): {len(all_unmapped)}")

    if all_fixes:
        print(f"\n{'─' * 70}")
        for fix in all_fixes:
            action = "FIXED" if apply_mode else "WOULD FIX"
            aspect_str = f" (aspect: {fix['aspect']})" if fix["aspect"] else ""
            print(f"  {action}  {fix['entry']}")
            print(f"         {fix['old']} → {fix['new']}{aspect_str}")
            print(f"         in {fix['file']}")
            print()

    if all_unmapped:
        print(f"\n{'─' * 70}")
        print("  UNMAPPED PRIMORDIALS (need manual review):")
        for u in all_unmapped:
            print(f"    {u['value']}  in  {u['entry']}  ({u['file']})")

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
    print(f"  SUMMARY: {len(all_fixes)} fixes, {len(all_unmapped)} unmapped, {len(modified_files)} files")
    if not apply_mode:
        print(f"  ** DRY RUN — no files modified **")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()
