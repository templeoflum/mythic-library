#!/usr/bin/env python3
"""
fix_broken_targets.py

Fixes broken relationship targets — references to @ids that don't exist in
any JSONLD file. Uses three strategies in order:

  1. Prefix correction (e.g. mesoamerican:quetzalcoatl -> arch:MA-QUETZALCOATL)
  2. ID format normalization (underscore/hyphen, case)
  3. Fuzzy match by suffix against the full ID index
  4. Removal if no match found (logged)

Builds a full @id index first, then tries each strategy.

Usage (from project root):
    python scripts/hygiene/fix_broken_targets.py --dry-run
    python scripts/hygiene/fix_broken_targets.py --apply
"""

import json
import argparse
from pathlib import Path


# ---------------------------------------------------------------------------
# Manual correction table for known broken patterns
# ---------------------------------------------------------------------------

# These are targets where the correct ID can be determined unambiguously
MANUAL_CORRECTIONS = {
    # Wrong prefix: mesoamerican: -> arch:MA-
    "mesoamerican:quetzalcoatl":     "arch:MA-QUETZALCOATL",
    "mesoamerican:tezcatlipoca":     "arch:MA-TEZCATLIPOCA",
    "mesoamerican:tlaloc":           "arch:MA-TLALOC",
    "mesoamerican:ehecatl":          "arch:MA-EHECATL",
    "mesoamerican:hero-twins":       "arch:MA-HERO-TWINS",
    "mesoamerican:mictlantecuhtli":  "arch:MA-MICTLANTECUHTLI",
    "mesoamerican:tlaltecuhtli":     "arch:MA-TLALTECUHTLI",
    # Wrong prefix: mesopotamian: -> arch:ME-
    "mesopotamian:inanna":           "arch:ME-INANNA",
    "mesopotamian:enki":             "arch:ME-ENKI",
    "mesopotamian:anu":              "arch:ME-ANU",
    "mesopotamian:nanna":            "arch:ME-NANNA",
    # Wrong prefix: chinese: -> arch:CN-
    "chinese:nuwa":                  "arch:CN-NUWA",
    "chinese:yellow-emperor":        "arch:CN-HUANGDI",
    # Wrong prefix: japanese: -> arch:JP-
    "japanese:jimmu":                "arch:JP-JIMMU",
    "japanese:kami":                  "arch:JP-AMATERASU",  # kami is a concept, closest specific
    # Wrong prefix: slavic: -> arch:SL-
    "slavic:perun":                  "arch:SL-PERUN",
    "slavic:leshy":                  "arch:SL-LESHY",
    # Wrong prefix: polynesian: -> arch:PL-
    "polynesian:matariki":           "arch:PL-MATARIKI",
    # Wrong prefix: persian: -> arch:PE- (but these reference specific sub-figures)
    "persian:aeshma":                "arch:PE-AESHMA-DAEVA",
    "persian:apaosha":               "arch:PE-APAOSHA",
    "persian:az":                    "arch:PE-AZ",
    "persian:druj":                  "arch:PE-DRUJ",
    "persian:spenta-mainyu":         "arch:PE-SPENTA-MAINYU",
    # Wrong prefix: roman: -> arch:RO-
    "roman:mithras":                 "arch:PE-MITHRA",  # Mithras is Persian Mithra
    # Wrong prefix: african: -> arch:AF-
    "african:yemoja":                "arch:AF-YEMOJA",
    # Wrong prefix: zodiac: -> astrology:
    "zodiac:aries":                  "astrology:aries",
    "zodiac:taurus":                 "astrology:taurus",
    "zodiac:gemini":                 "astrology:gemini",
    "zodiac:cancer":                 "astrology:cancer",
    "zodiac:leo":                    "astrology:leo",
    "zodiac:virgo":                  "astrology:virgo",
    "zodiac:libra":                  "astrology:libra",
    "zodiac:scorpio":                "astrology:scorpio",
    "zodiac:sagittarius":            "astrology:sagittarius",
    "zodiac:capricorn":              "astrology:capricorn",
    "zodiac:aquarius":               "astrology:aquarius",
    "zodiac:pisces":                 "astrology:pisces",
    # Wrong prefix: vedic: -> rashi: (vedic zodiac uses rashi IDs with Sanskrit names)
    # These can't be auto-mapped since vedic:aries != rashi:mesha without a lookup
    # Mark for removal
    # Wrong prefix: astro: -> astrology:
    "astro:venus":                   "astrology:venus",
    # heros_journey: -> journey: prefix
    "heros_journey:call":            "journey:call_to_adventure",
    "heros_journey:belly_of_whale":  "journey:belly_of_whale",
    "heros_journey:crossing_threshold": "journey:crossing_threshold",
    "heros_journey:road_of_trials":  "journey:road_of_trials",
    "heros_journey:ordeal":          "journey:road_of_trials",  # closest match
    "heros_journey:abyss":           "journey:belly_of_whale",  # closest match
    "heros_journey:resurrection":    "journey:crossing_return",  # closest match
    "heros_journey:return":          "journey:crossing_return",
    "heros_journey:departure":       "journey:call_to_adventure",  # closest match
    "heros_journey:mentor":          "journey:supernatural_aid",  # mentor = supernatural aid stage
    "heros_journey:shadow":          "journey:road_of_trials",  # shadow encounter during trials
    "heros_journey:temptation":      "journey:woman_temptress",
    # ogham spelling fixes
    "ogham:beth":                    "ogham:beith",
    "ogham:nion":                    "ogham:nuin",
    "ogham:huath":                   "ogham:huathe",
    # tarot: wrong naming convention (descriptive -> coded)
    "tarot:ace_of_cups":             "tarot:cups_ace",
    "tarot:four_of_cups":            "tarot:cups_04",
    "tarot:three_of_cups":           "tarot:cups_03",
    "tarot:seven_of_cups":           "tarot:cups_07",
    "tarot:four_of_pentacles":       "tarot:pentacles_04",
    "tarot:nine_of_pentacles":       "tarot:pentacles_09",
    "tarot:ten_of_pentacles":        "tarot:pentacles_10",
    "tarot:knight_of_swords":        "tarot:swords_knight",
    "tarot:six_of_swords":           "tarot:swords_06",
    "tarot:seven_of_wands":          "tarot:wands_07",
    "tarot:eight_of_wands":          "tarot:wands_08",
    # kwml shadow forms
    "kwml:addicted-lover":           "kwml:masochist",  # closest shadow
    "kwml:impotent-lover":           "kwml:masochist",  # closest shadow
    "kwml:innocent":                 "kwml:weakling",   # closest shadow
    "kwml:manipulator":              "shadow:magician_manipulator",
    # concept refs
    "concept:TABLET_OF_DESTINIES":   None,  # remove - no archetype equivalent
    "concept:VRITRA":                None,  # remove - no archetype equivalent
    # misc wrong prefixes or non-existent
    "christian:christ":              None,  # remove - not in ACP
    "christian:satan":               None,  # remove - not in ACP
    "jewish:messiah":                None,  # remove - not in ACP
    "modern:punch":                  None,  # remove - no match
    "system:TUATHA-DE-DANANN":       None,  # system ref, not archetype
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


def build_id_index(root):
    """Build set of all @ids across all JSONLD files."""
    all_ids = set()
    files = discover_jsonld_files(root)
    file_data = {}
    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        file_data[path] = data
        def scan(obj):
            if isinstance(obj, dict):
                eid = obj.get("@id")
                if eid:
                    all_ids.add(eid)
                for v in obj.values():
                    scan(v)
            elif isinstance(obj, list):
                for item in obj:
                    scan(item)
        scan(data)
    return all_ids, file_data


def try_auto_fix(target, all_ids):
    """Try automatic fixes: underscore->hyphen, case normalization."""
    # Strategy: normalize the suffix part and try common prefixes
    if ":" not in target:
        return None

    prefix, suffix = target.split(":", 1)

    # Try hyphen variant
    hyphen_suffix = suffix.replace("_", "-")
    candidates = [
        f"{prefix}:{hyphen_suffix}",
        f"{prefix}:{suffix.upper()}",
        f"{prefix}:{hyphen_suffix.upper()}",
    ]
    for c in candidates:
        if c in all_ids:
            return c

    # Try arch: prefix with system code guess
    prefix_map = {
        "incan": "arch:IC",
        "persian": "arch:PE",
    }
    if prefix in prefix_map:
        arch_prefix = prefix_map[prefix]
        for candidate_suffix in [suffix.upper(), hyphen_suffix.upper(),
                                  suffix.upper().replace("-", "_")]:
            candidate = f"{arch_prefix}-{candidate_suffix}"
            if candidate in all_ids:
                return candidate

    return None


# ---------------------------------------------------------------------------
# Fix logic
# ---------------------------------------------------------------------------

def fix_file(data, rel_path, all_ids, apply_mode):
    fixes = []
    removals = []
    unresolved = []

    for entry in extract_entries(data):
        eid = entry.get("@id", "?")
        rels = entry.get("relationships", [])
        to_remove = []

        for i, rel in enumerate(rels):
            target = rel.get("target", "")
            if not isinstance(target, str):
                continue
            # Skip primordial targets (handled by other script)
            if target.startswith("primordial:"):
                continue
            # Skip valid targets
            if target in all_ids:
                continue
            # Skip description-like strings
            if ":" not in target or len(target.split()) > 5:
                continue

            rtype = rel.get("type", "")

            # Try manual correction first
            if target in MANUAL_CORRECTIONS:
                new_target = MANUAL_CORRECTIONS[target]
                if new_target is None:
                    # Mark for removal
                    removals.append({
                        "file": rel_path, "entry": eid,
                        "target": target, "rel_type": rtype,
                        "reason": "No valid equivalent in ACP",
                    })
                    if apply_mode:
                        to_remove.append(i)
                    continue
                elif new_target in all_ids:
                    fixes.append({
                        "file": rel_path, "entry": eid,
                        "old": target, "new": new_target,
                        "strategy": "manual_correction",
                        "rel_type": rtype,
                    })
                    if apply_mode:
                        rel["target"] = new_target
                    continue
                else:
                    # Manual correction target also doesn't exist
                    unresolved.append({
                        "file": rel_path, "entry": eid,
                        "target": target, "rel_type": rtype,
                        "note": f"Manual correction {new_target} also not in index",
                    })
                    continue

            # Try automatic fix
            auto_fix = try_auto_fix(target, all_ids)
            if auto_fix:
                fixes.append({
                    "file": rel_path, "entry": eid,
                    "old": target, "new": auto_fix,
                    "strategy": "auto_normalize",
                    "rel_type": rtype,
                })
                if apply_mode:
                    rel["target"] = auto_fix
                continue

            # Unresolved
            unresolved.append({
                "file": rel_path, "entry": eid,
                "target": target, "rel_type": rtype,
                "note": "No fix found",
            })

        # Remove marked relationships (reverse order to preserve indices)
        if apply_mode and to_remove:
            for i in sorted(to_remove, reverse=True):
                rels.pop(i)

    return fixes, removals, unresolved


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Fix broken relationship targets in JSONLD files."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Report changes without writing.")
    group.add_argument("--apply", action="store_true", help="Apply fixes to JSONLD files.")
    args = parser.parse_args()
    apply_mode = args.apply

    print("=" * 70)
    print("  FIX BROKEN RELATIONSHIP TARGETS")
    print("=" * 70)

    root = find_project_root()
    print(f"\nProject root: {root}")
    print(f"Mode: {'APPLY' if apply_mode else 'DRY RUN'}")

    print("\nBuilding @id index...")
    all_ids, file_data = build_id_index(root)
    print(f"  {len(all_ids)} unique @ids across {len(file_data)} files")

    all_fixes = []
    all_removals = []
    all_unresolved = []
    modified_files = {}

    for path, data in file_data.items():
        rel_path = str(path.relative_to(root))
        fixes, removals, unresolved = fix_file(data, rel_path, all_ids, apply_mode)
        if fixes or removals:
            all_fixes.extend(fixes)
            all_removals.extend(removals)
            modified_files[path] = data
        all_unresolved.extend(unresolved)

    # Report fixes
    print(f"\nResults:")
    print(f"  Fixed:      {len(all_fixes)}")
    print(f"  Removed:    {len(all_removals)}")
    print(f"  Unresolved: {len(all_unresolved)}")
    print(f"  Files affected: {len(modified_files)}")

    if all_fixes:
        print(f"\n{'─' * 70}")
        print("  FIXES:")
        for fix in all_fixes:
            action = "FIXED" if apply_mode else "WOULD FIX"
            print(f"  {action}  [{fix['strategy']}]  {fix['entry']}")
            print(f"         {fix['old']} → {fix['new']}")

    if all_removals:
        print(f"\n{'─' * 70}")
        print("  REMOVALS:")
        for rem in all_removals:
            action = "REMOVED" if apply_mode else "WOULD REMOVE"
            print(f"  {action}  {rem['entry']}")
            print(f"         {rem['target']} ({rem['rel_type']})")
            print(f"         Reason: {rem['reason']}")

    if all_unresolved:
        print(f"\n{'─' * 70}")
        print("  UNRESOLVED (need manual review):")
        for u in all_unresolved:
            print(f"    {u['target']}  in  {u['entry']}  ({u['file']})")
            if u.get("note"):
                print(f"      Note: {u['note']}")

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
    total = len(all_fixes) + len(all_removals)
    print(f"\n{'=' * 70}")
    print(f"  SUMMARY: {total} resolved ({len(all_fixes)} fixed, {len(all_removals)} removed)")
    print(f"           {len(all_unresolved)} unresolved")
    print(f"           {len(modified_files)} files affected")
    if not apply_mode:
        print(f"  ** DRY RUN — no files modified **")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()
