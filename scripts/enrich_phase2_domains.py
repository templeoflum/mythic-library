#!/usr/bin/env python3
"""
Phase 2 Enrichment: Domain Vocabulary Expansion and Auto-Assignment

This script:
1. Extracts domains from descriptions and names
2. Adds system-appropriate domains
3. Normalizes existing domains to controlled vocabulary
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

# Expanded domain vocabulary with aliases
DOMAIN_VOCABULARY = {
    # Core concepts
    "death": ["death", "dying", "mortality", "dead", "deceased"],
    "rebirth": ["rebirth", "resurrection", "renewal", "reborn", "regeneration"],
    "underworld": ["underworld", "netherworld", "afterlife", "realm of dead", "land of dead"],
    "sky": ["sky", "heavens", "celestial", "aerial", "heavenly"],
    "sea": ["sea", "ocean", "water", "maritime", "marine", "aquatic"],
    "earth": ["earth", "land", "ground", "terrestrial", "earthly", "soil"],
    "fire": ["fire", "flame", "burning", "volcanic", "forge"],
    "water": ["water", "rain", "rivers", "streams", "moisture"],
    "air": ["air", "wind", "breath", "atmosphere", "storm"],
    "war": ["war", "battle", "combat", "conflict", "warfare", "martial"],
    "peace": ["peace", "harmony", "tranquility", "serenity"],
    "love": ["love", "romance", "passion", "desire", "affection", "eros"],
    "fertility": ["fertility", "fecundity", "abundance", "fruitful"],
    "harvest": ["harvest", "crops", "agriculture", "grain", "reaping"],
    "hunt": ["hunt", "hunting", "chase", "pursuit", "prey"],
    "wisdom": ["wisdom", "knowledge", "insight", "understanding", "sagacity"],
    "crafts": ["crafts", "craftsmanship", "artisanry", "making", "handiwork"],
    "smithing": ["smithing", "metalwork", "forging", "blacksmith", "metalworking"],
    "healing": ["healing", "medicine", "health", "cure", "restoration"],
    "prophecy": ["prophecy", "divination", "oracle", "foresight", "prediction"],
    "music": ["music", "song", "melody", "harmony", "musical"],
    "poetry": ["poetry", "verse", "bards", "poetic"],
    "dance": ["dance", "dancing", "movement", "choreography"],
    "threshold": ["threshold", "doorway", "gateway", "boundary", "liminal"],
    "boundaries": ["boundaries", "borders", "limits", "edges"],
    "travel": ["travel", "journey", "voyage", "wandering", "pilgrimage"],
    "commerce": ["commerce", "trade", "merchants", "business", "exchange"],
    "communication": ["communication", "messages", "messenger", "speech", "language"],
    "justice": ["justice", "judgment", "fairness", "law", "righteous"],
    "law": ["law", "legal", "order", "rules", "legislation"],
    "order": ["order", "structure", "organization", "hierarchy", "cosmos"],
    "chaos": ["chaos", "disorder", "entropy", "randomness", "anarchy"],
    "fate": ["fate", "destiny", "fortune", "doom", "wyrd"],
    "time": ["time", "temporal", "chronos", "ages", "eternity"],
    "memory": ["memory", "remembrance", "recollection", "ancestral"],
    "home": ["home", "household", "domestic", "dwelling"],
    "hearth": ["hearth", "fire", "warmth", "hospitality"],
    "family": ["family", "kinship", "lineage", "clan", "household"],
    "marriage": ["marriage", "wedding", "union", "matrimony", "conjugal"],
    "motherhood": ["motherhood", "maternal", "mother", "nurturing"],
    "fatherhood": ["fatherhood", "paternal", "father", "patriarchal"],
    "childhood": ["childhood", "youth", "innocence", "child", "young"],
    "transformation": ["transformation", "change", "metamorphosis", "transmutation"],
    "initiation": ["initiation", "rites", "passage", "transition"],
    "sacrifice": ["sacrifice", "offering", "devotion", "martyrdom"],
    "ecstasy": ["ecstasy", "rapture", "frenzy", "intoxication", "euphoria"],
    "madness": ["madness", "insanity", "frenzy", "delirium"],
    "sovereignty": ["sovereignty", "kingship", "rule", "dominion", "authority"],
    "protection": ["protection", "guardian", "defense", "shelter", "safety"],
    "destruction": ["destruction", "annihilation", "devastation", "ruin"],
    "creation": ["creation", "genesis", "making", "bringing forth", "creative"],
    "preservation": ["preservation", "maintenance", "continuity", "sustaining"],
    # Additional domains
    "thunder": ["thunder", "lightning", "storm", "tempest"],
    "sun": ["sun", "solar", "light", "radiance", "daylight"],
    "moon": ["moon", "lunar", "night", "phases"],
    "stars": ["stars", "stellar", "celestial", "constellation"],
    "agriculture": ["agriculture", "farming", "cultivation", "crops"],
    "wine": ["wine", "vine", "grapes", "intoxicant"],
    "animals": ["animals", "beasts", "fauna", "creatures"],
    "wilderness": ["wilderness", "wild", "nature", "untamed", "forest"],
    "magic": ["magic", "sorcery", "enchantment", "spellcraft", "arcane"],
    "trickster": ["trickster", "cunning", "mischief", "deception", "clever"],
    "messenger": ["messenger", "herald", "envoy", "go-between"],
    "wealth": ["wealth", "riches", "prosperity", "treasure", "abundance"],
    "beauty": ["beauty", "beautiful", "aesthetic", "grace", "lovely"],
    "truth": ["truth", "honesty", "veracity", "sincerity"],
    "intellect": ["intellect", "mind", "reason", "thought", "intelligence"],
    "courage": ["courage", "bravery", "valor", "heroism", "boldness"],
    "strength": ["strength", "power", "might", "force", "potency"],
    "speed": ["speed", "swiftness", "velocity", "quick", "fleet"],
    "dreams": ["dreams", "sleep", "visions", "unconscious"],
    "spirits": ["spirits", "ghosts", "souls", "ancestral spirits"],
    "ancestors": ["ancestors", "forebears", "ancestral", "lineage"],
}

# System-specific domain defaults
SYSTEM_DOMAINS = {
    # Pantheons
    "greek": ["mythology", "olympian"],
    "norse": ["mythology", "nordic"],
    "egyptian": ["mythology", "ancient-egypt"],
    "celtic": ["mythology", "celtic"],
    "hindu": ["mythology", "vedic"],
    "japanese": ["mythology", "shinto"],
    "chinese": ["mythology", "chinese"],
    "mesopotamian": ["mythology", "ancient-near-east"],
    "african": ["mythology", "yoruba"],
    "mesoamerican": ["mythology", "aztec-maya"],
    "slavic": ["mythology", "slavic"],
    "polynesian": ["mythology", "pacific"],
    "native_american": ["mythology", "indigenous-america"],
    "finnish": ["mythology", "kalevala"],
    "australian": ["mythology", "dreamtime"],
    "incan": ["mythology", "andean"],
    "persian": ["mythology", "zoroastrian"],
    "roman": ["mythology", "roman"],
    "buddhist": ["mythology", "buddhist"],
    "vodou": ["mythology", "vodou"],
    # Divination
    "tarot": ["divination", "tarot", "cards"],
    "iching": ["divination", "i-ching", "chinese-philosophy"],
    "runes": ["divination", "runes", "norse"],
    "astrology": ["divination", "astrology", "celestial"],
    "zodiac": ["divination", "zodiac"],
    "kabbalah": ["divination", "kabbalah", "jewish-mysticism"],
    "chakras": ["divination", "chakras", "energy"],
    "elements": ["divination", "elements", "classical"],
    "alchemy": ["divination", "alchemy", "transformation"],
    "ogham": ["divination", "ogham", "celtic"],
    "calendar": ["divination", "calendar", "time-cycles"],
    "totems": ["divination", "totems", "animal-spirits"],
    # Psychology
    "jungian": ["psychology", "jungian", "depth-psychology"],
    "enneagram": ["psychology", "enneagram", "personality"],
    "narrative": ["psychology", "narrative", "storytelling"],
    "developmental": ["psychology", "developmental"],
    "personality": ["psychology", "personality-types"],
    "archetypes": ["psychology", "archetypal"],
    "gendered": ["psychology", "gender-archetypes"],
    # Modern
    "brand": ["modern", "branding", "marketing"],
    "digital": ["modern", "internet", "digital-culture"],
    "superhero": ["modern", "pop-culture", "comics"],
    "angels": ["modern", "angelology", "spiritual"],
    "commedia": ["modern", "theater", "comedy"],
}


def normalize_domain(domain: str) -> str:
    """Normalize a domain to controlled vocabulary."""
    domain_lower = domain.lower().strip()

    # Direct match
    if domain_lower in DOMAIN_VOCABULARY:
        return domain_lower

    # Check aliases
    for canonical, aliases in DOMAIN_VOCABULARY.items():
        if domain_lower in aliases:
            return canonical

    # Return as-is if no match
    return domain_lower


def extract_domains_from_text(text: str) -> Set[str]:
    """Extract domains from description or name text."""
    if not text:
        return set()

    text_lower = text.lower()
    found = set()

    for canonical, aliases in DOMAIN_VOCABULARY.items():
        for alias in aliases:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, text_lower):
                found.add(canonical)
                break

    return found


def get_system_from_path(file_path: Path) -> str:
    """Extract system name from file path."""
    parts = file_path.parts
    for i, part in enumerate(parts):
        if part in ["archetypes", "divination", "psychology", "modern"]:
            if i + 1 < len(parts):
                return parts[i + 1].lower()
    return ""


def enrich_domains(acp_path: Path, dry_run: bool = True) -> Dict[str, int]:
    """Enrich domains across all archetype files."""
    stats = {
        "files_processed": 0,
        "entries_enriched": 0,
        "domains_added": 0,
        "domains_normalized": 0,
    }

    patterns = [
        "archetypes/**/*.jsonld",
        "divination/**/*.jsonld",
        "psychology/**/*.jsonld",
        "modern/**/*.jsonld",
    ]

    for pattern in patterns:
        for file_path in acp_path.glob(pattern):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"  Error loading {file_path}: {e}")
                continue

            system = get_system_from_path(file_path)
            system_defaults = SYSTEM_DOMAINS.get(system, [])

            modified = False

            # Get entries
            entries = data.get("entries", [])
            if "suits" in data:  # Tarot minor arcana
                for suit in data.get("suits", []):
                    entries.extend(suit.get("cards", []))

            for entry in entries:
                if not isinstance(entry, dict):
                    continue

                arch_id = entry.get("@id", "")
                if arch_id.startswith("system:"):
                    continue

                name = entry.get("name", "")
                description = entry.get("description", "")
                existing_domains = entry.get("domains", [])

                # Normalize existing domains
                normalized = []
                for d in existing_domains:
                    norm = normalize_domain(d)
                    if norm != d.lower():
                        stats["domains_normalized"] += 1
                    normalized.append(norm)

                # Extract from text
                text_domains = extract_domains_from_text(name + " " + description)

                # Combine: existing + text-extracted + system defaults
                all_domains = set(normalized) | text_domains

                # Add system defaults if entry has few domains
                if len(all_domains) < 3:
                    all_domains.update(system_defaults[:2])

                # Limit to 8 domains
                final_domains = sorted(list(all_domains))[:8]

                # Check if changed
                if set(final_domains) != set(existing_domains):
                    new_count = len(set(final_domains) - set(existing_domains))
                    if new_count > 0:
                        stats["domains_added"] += new_count
                        stats["entries_enriched"] += 1
                    entry["domains"] = final_domains
                    modified = True

            if modified:
                stats["files_processed"] += 1
                if not dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)

    return stats


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Phase 2: Domain Enrichment')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Show what would be changed without modifying files')
    parser.add_argument('--apply', action='store_true',
                        help='Actually apply the changes')
    args = parser.parse_args()

    dry_run = not args.apply

    print("=" * 70)
    print("PHASE 2: DOMAIN VOCABULARY ENRICHMENT")
    print("=" * 70)
    if dry_run:
        print("\n[DRY RUN - No files will be modified. Use --apply to save changes.]\n")

    acp_path = Path("ACP")
    stats = enrich_domains(acp_path, dry_run=dry_run)

    print("\n" + "=" * 40)
    print("SUMMARY")
    print("=" * 40)
    print(f"Files processed:     {stats['files_processed']}")
    print(f"Entries enriched:    {stats['entries_enriched']}")
    print(f"Domains added:       {stats['domains_added']}")
    print(f"Domains normalized:  {stats['domains_normalized']}")

    if dry_run:
        print("\n[DRY RUN complete. Run with --apply to save changes.]")
    else:
        print("\n[Changes saved successfully.]")


if __name__ == '__main__':
    main()
