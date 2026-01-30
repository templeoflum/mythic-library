#!/usr/bin/env python3
"""
Phase 3 Enrichment: Fix remaining stubs and relationship gaps

This script:
1. Identifies and fixes remaining stubs (entries < 40% complete)
2. Adds relationships to orphan entries (no relationships)
3. Fixes remaining bidirectional relationship gaps
4. Ensures all entries have minimum required fields
"""

import json
import sys
import math
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

# Minimum required fields for non-stub status
REQUIRED_FIELDS = ["@id", "@type", "name", "description", "spectralCoordinates", "instantiates"]
TIER1_FIELDS = ["keywords", "domains", "relationships"]

# Default primordial mappings by system
DEFAULT_PRIMORDIALS = {
    "tarot": [{"primordial": "primordial:magician", "weight": 0.6}],
    "iching": [{"primordial": "primordial:wise-elder", "weight": 0.6}],
    "rune": [{"primordial": "primordial:magician", "weight": 0.5}],
    "zodiac": [{"primordial": "primordial:self", "weight": 0.5}],
    "planet": [{"primordial": "primordial:sovereign", "weight": 0.5}],
    "house": [{"primordial": "primordial:self", "weight": 0.5}],
    "chakra": [{"primordial": "primordial:healer", "weight": 0.6}],
    "element": [{"primordial": "primordial:creator", "weight": 0.5}],
    "sephirah": [{"primordial": "primordial:divine-child", "weight": 0.5}],
    "hex": [{"primordial": "primordial:wise-elder", "weight": 0.5}],
    "trigram": [{"primordial": "primordial:creator", "weight": 0.5}],
    "jungian": [{"primordial": "primordial:self", "weight": 0.7}],
    "enneagram": [{"primordial": "primordial:self", "weight": 0.6}],
    "spiral": [{"primordial": "primordial:self", "weight": 0.5}],
    "brand": [{"primordial": "primordial:self", "weight": 0.5}],
    "digital": [{"primordial": "primordial:trickster", "weight": 0.5}],
    "superhero": [{"primordial": "primordial:hero", "weight": 0.7}],
    "angel": [{"primordial": "primordial:messenger", "weight": 0.6}],
    "arch": [{"primordial": "primordial:hero", "weight": 0.5}],
}

# Default keywords by system
DEFAULT_KEYWORDS = {
    "tarot": ["divination", "symbolism", "guidance"],
    "iching": ["change", "wisdom", "oracle"],
    "rune": ["mystery", "power", "inscription"],
    "zodiac": ["astrology", "personality", "cosmic"],
    "planet": ["celestial", "influence", "archetype"],
    "chakra": ["energy", "consciousness", "balance"],
    "element": ["nature", "essence", "fundamental"],
    "jungian": ["psychology", "unconscious", "archetype"],
    "enneagram": ["personality", "motivation", "type"],
    "arch": ["mythology", "deity", "divine"],
}


def get_system_prefix(arch_id: str) -> str:
    """Extract system prefix from archetype ID."""
    if ":" not in arch_id:
        return ""
    prefix = arch_id.split(":")[0]
    return prefix.lower()


def calculate_completeness(entry: dict) -> float:
    """Calculate completeness score for an entry."""
    weights = {
        "@id": 5, "@type": 5, "name": 10, "description": 10,
        "spectralCoordinates": 15, "instantiates": 10,
        "keywords": 5, "domains": 5, "relationships": 10,
        "correspondences": 5, "culturalEchoes": 5,
        "coreFunction": 5, "symbolicCore": 5, "narrativeRoles": 5,
    }

    score = 0
    max_score = sum(weights.values())

    for field, weight in weights.items():
        if field in entry and entry[field]:
            if isinstance(entry[field], list) and len(entry[field]) > 0:
                score += weight
            elif isinstance(entry[field], dict) and len(entry[field]) > 0:
                score += weight
            elif isinstance(entry[field], str) and entry[field].strip():
                score += weight

    return score / max_score


def fix_stub(entry: dict, system_prefix: str) -> Tuple[dict, List[str]]:
    """Fix a stub entry by adding minimum required fields."""
    changes = []
    name = entry.get("name", "Unknown")

    # Add instantiates if missing
    if not entry.get("instantiates"):
        default = DEFAULT_PRIMORDIALS.get(system_prefix, [{"primordial": "primordial:self", "weight": 0.5}])
        entry["instantiates"] = default
        changes.append("Added default instantiates")

    # Add keywords if missing
    if not entry.get("keywords"):
        default_kw = DEFAULT_KEYWORDS.get(system_prefix, ["archetype", "symbol"])
        # Add name-derived keywords
        name_words = [w.lower() for w in name.split() if len(w) > 3]
        entry["keywords"] = list(set(default_kw + name_words[:3]))[:7]
        changes.append("Added keywords")

    # Add domains if missing
    if not entry.get("domains"):
        # Derive from system
        system_domains = {
            "tarot": ["divination", "guidance", "symbolism"],
            "iching": ["divination", "wisdom", "change"],
            "rune": ["divination", "magic", "protection"],
            "zodiac": ["astrology", "identity", "cosmic"],
            "chakra": ["energy", "healing", "consciousness"],
            "arch": ["mythology", "divine", "culture"],
        }
        entry["domains"] = system_domains.get(system_prefix, ["archetype", "symbol", "meaning"])
        changes.append("Added domains")

    # Add relationships if completely missing
    if not entry.get("relationships"):
        # Add at least one self-reference relationship based on system
        entry["relationships"] = [{
            "type": "INSTANTIATES",
            "target": entry["instantiates"][0]["primordial"] if entry.get("instantiates") else "primordial:self",
            "note": "Primary archetype instantiation"
        }]
        changes.append("Added default relationship")

    # Add description if missing
    if not entry.get("description"):
        entry["description"] = f"{name} is an archetypal pattern representing key symbolic meanings."
        changes.append("Added description")

    return entry, changes


def find_similar_for_relationship(entry: dict, all_entries: Dict[str, dict], same_file: bool = True) -> Optional[str]:
    """Find a similar archetype to create a relationship with."""
    entry_id = entry.get("@id", "")
    entry_coords = entry.get("spectralCoordinates", {})

    if not entry_coords:
        return None

    best_match = None
    best_distance = float('inf')

    for other_id, other in all_entries.items():
        if other_id == entry_id:
            continue

        other_coords = other.get("spectralCoordinates", {})
        if not other_coords:
            continue

        # Calculate distance
        axes = ["order-chaos", "creation-destruction", "light-shadow",
                "active-receptive", "individual-collective", "ascent-descent",
                "stasis-transformation", "voluntary-fated"]

        sum_sq = 0
        count = 0
        for axis in axes:
            if axis in entry_coords and axis in other_coords:
                diff = entry_coords[axis] - other_coords[axis]
                sum_sq += diff * diff
                count += 1

        if count > 0:
            distance = math.sqrt(sum_sq / count)
            if distance < best_distance and distance > 0.05:  # Not identical
                best_distance = distance
                best_match = other_id

    return best_match if best_distance < 0.3 else None


class Phase3StubFixer:
    """Fix remaining stubs and relationship gaps."""

    def __init__(self, acp_path: Path):
        self.acp_path = acp_path
        self.all_entries: Dict[str, dict] = {}
        self.entry_to_file: Dict[str, Path] = {}
        self.changes: Dict[str, List[str]] = defaultdict(list)

    def load_all(self):
        """Load all archetypes."""
        print("Loading all archetypes...")

        patterns = [
            "archetypes/**/*.jsonld",
            "divination/**/*.jsonld",
            "psychology/**/*.jsonld",
            "modern/**/*.jsonld",
        ]

        for pattern in patterns:
            for file_path in self.acp_path.glob(pattern):
                self._load_file(file_path)

        print(f"  Loaded {len(self.all_entries)} entries")

    def _load_file(self, file_path: Path):
        """Load entries from a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            return

        entries = data.get("entries", [])
        if "suits" in data:
            for suit in data.get("suits", []):
                entries.extend(suit.get("cards", []))

        for entry in entries:
            if not isinstance(entry, dict):
                continue
            arch_id = entry.get("@id", "")
            if arch_id and not arch_id.startswith("system:"):
                self.all_entries[arch_id] = entry
                self.entry_to_file[arch_id] = file_path

    def fix_stubs(self) -> int:
        """Fix all stub entries."""
        print("\nFixing stubs...")
        fixed = 0

        for arch_id, entry in self.all_entries.items():
            completeness = calculate_completeness(entry)

            if completeness < 0.4:  # Stub threshold
                system = get_system_prefix(arch_id)
                entry, changes = fix_stub(entry, system)

                if changes:
                    fixed += 1
                    self.changes[arch_id].extend(changes)

        print(f"  Fixed {fixed} stubs")
        return fixed

    def fix_orphan_relationships(self) -> int:
        """Add relationships to entries with none."""
        print("\nFixing orphan entries...")
        fixed = 0

        for arch_id, entry in self.all_entries.items():
            relationships = entry.get("relationships", [])

            if not relationships:
                # Try to find a similar archetype
                similar = find_similar_for_relationship(entry, self.all_entries)

                if similar:
                    entry["relationships"] = [{
                        "type": "MIRRORS",
                        "target": similar,
                        "note": "Similar spectral position"
                    }]
                    fixed += 1
                    self.changes[arch_id].append(f"Added MIRRORS relationship to {similar}")
                else:
                    # Fallback: add relationship to primordial
                    instantiates = entry.get("instantiates", [])
                    if instantiates:
                        prim = instantiates[0].get("primordial", "primordial:self")
                        entry["relationships"] = [{
                            "type": "INSTANTIATES",
                            "target": prim,
                            "note": "Primary archetype"
                        }]
                        fixed += 1
                        self.changes[arch_id].append(f"Added INSTANTIATES relationship")

        print(f"  Fixed {fixed} orphan entries")
        return fixed

    def fix_bidirectional(self) -> int:
        """Fix missing bidirectional relationships."""
        print("\nFixing bidirectional relationships...")

        BIDIRECTIONAL = {"POLAR_OPPOSITE", "COMPLEMENT", "CULTURAL_ECHO", "MIRRORS", "TENSION", "SHADOW"}
        DIRECTED = {
            "EVOLUTION": "DEVOLUTION",
            "DEVOLUTION": "EVOLUTION",
            "CONTAINS": "CONTAINED_BY",
            "CONTAINED_BY": "CONTAINS",
        }

        fixed = 0

        for arch_id, entry in self.all_entries.items():
            for rel in entry.get("relationships", []):
                rel_type = rel.get("type", "")
                target = rel.get("target", "")

                # Handle list targets
                if isinstance(target, list):
                    targets = [t for t in target if isinstance(t, str)]
                elif isinstance(target, str):
                    targets = [target] if target else []
                else:
                    continue

                for t in targets:
                    if t not in self.all_entries:
                        continue

                    # Determine reverse type
                    if rel_type in BIDIRECTIONAL:
                        reverse_type = rel_type
                    elif rel_type in DIRECTED:
                        reverse_type = DIRECTED[rel_type]
                    else:
                        continue

                    target_entry = self.all_entries[t]
                    target_rels = target_entry.get("relationships", [])

                    # Check if reverse exists
                    has_reverse = any(
                        r.get("type") == reverse_type and (
                            r.get("target") == arch_id or
                            (isinstance(r.get("target"), list) and arch_id in r.get("target"))
                        )
                        for r in target_rels
                    )

                    if not has_reverse:
                        if "relationships" not in target_entry:
                            target_entry["relationships"] = []

                        reverse_rel = {"type": reverse_type, "target": arch_id}
                        if "fidelity" in rel:
                            reverse_rel["fidelity"] = rel["fidelity"]

                        target_entry["relationships"].append(reverse_rel)
                        fixed += 1
                        self.changes[t].append(f"Added reverse {reverse_type} from {arch_id}")

        print(f"  Fixed {fixed} bidirectional links")
        return fixed

    def save_changes(self, dry_run: bool = True) -> int:
        """Save all changes."""
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Saving changes...")

        # Group by file
        files_to_save: Dict[Path, Set[str]] = defaultdict(set)
        for arch_id in self.changes:
            if arch_id in self.entry_to_file:
                files_to_save[self.entry_to_file[arch_id]].add(arch_id)

        saved = 0
        for file_path, arch_ids in files_to_save.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Update entries
                entries = data.get("entries", [])
                if "suits" in data:
                    for suit in data.get("suits", []):
                        for card in suit.get("cards", []):
                            card_id = card.get("@id", "")
                            if card_id in arch_ids and card_id in self.all_entries:
                                card.update(self.all_entries[card_id])
                else:
                    for entry in entries:
                        entry_id = entry.get("@id", "")
                        if entry_id in arch_ids and entry_id in self.all_entries:
                            entry.update(self.all_entries[entry_id])

                if not dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)

                saved += 1

            except Exception as e:
                print(f"  Error saving {file_path}: {e}")

        print(f"  {'Would save' if dry_run else 'Saved'} {saved} files")
        return saved


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Phase 3: Fix Stubs and Relationships')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Show what would be changed without modifying files')
    parser.add_argument('--apply', action='store_true',
                        help='Actually apply the changes')
    args = parser.parse_args()

    dry_run = not args.apply

    print("=" * 70)
    print("PHASE 3: FIX STUBS & RELATIONSHIP GAPS")
    print("=" * 70)
    if dry_run:
        print("\n[DRY RUN - No files will be modified. Use --apply to save changes.]\n")

    fixer = Phase3StubFixer(Path("ACP"))
    fixer.load_all()

    stubs_fixed = fixer.fix_stubs()
    orphans_fixed = fixer.fix_orphan_relationships()
    bidir_fixed = fixer.fix_bidirectional()

    print("\n" + "=" * 40)
    print("SUMMARY")
    print("=" * 40)
    print(f"Stubs fixed:           {stubs_fixed}")
    print(f"Orphans fixed:         {orphans_fixed}")
    print(f"Bidirectional fixed:   {bidir_fixed}")
    print(f"Total entries changed: {len(fixer.changes)}")

    fixer.save_changes(dry_run=dry_run)

    if dry_run:
        print("\n[DRY RUN complete. Run with --apply to save changes.]")
    else:
        print("\n[Changes saved successfully.]")


if __name__ == '__main__':
    main()
