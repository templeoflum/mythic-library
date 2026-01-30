#!/usr/bin/env python3
"""
Phase 3 Enrichment: Aliases, Correspondences, and Description Generation

This script:
1. Generates aliases from names (alternative spellings, epithets)
2. Adds correspondences based on primordial-to-system mappings
3. Generates basic descriptions for entries missing them
4. Fixes remaining stubs by ensuring minimum required fields
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

# Primordial to correspondence mappings
PRIMORDIAL_CORRESPONDENCES = {
    "primordial:hero": {
        "tarot": ["tarot:chariot", "tarot:strength"],
        "planet": ["planet:mars", "planet:sun"],
        "element": ["element:fire"],
    },
    "primordial:great-mother": {
        "tarot": ["tarot:empress", "tarot:moon"],
        "planet": ["planet:moon", "planet:venus"],
        "element": ["element:water", "element:earth"],
    },
    "primordial:great-father": {
        "tarot": ["tarot:emperor", "tarot:hierophant"],
        "planet": ["planet:jupiter", "planet:saturn"],
        "element": ["element:air", "element:fire"],
    },
    "primordial:trickster": {
        "tarot": ["tarot:fool", "tarot:magician"],
        "planet": ["planet:mercury"],
        "element": ["element:air"],
    },
    "primordial:wise-elder": {
        "tarot": ["tarot:hermit", "tarot:hierophant"],
        "planet": ["planet:saturn"],
        "element": ["element:earth"],
    },
    "primordial:lover": {
        "tarot": ["tarot:lovers", "tarot:empress"],
        "planet": ["planet:venus"],
        "element": ["element:water"],
    },
    "primordial:warrior": {
        "tarot": ["tarot:chariot", "tarot:strength", "tarot:tower"],
        "planet": ["planet:mars"],
        "element": ["element:fire"],
    },
    "primordial:magician": {
        "tarot": ["tarot:magician", "tarot:high_priestess"],
        "planet": ["planet:mercury", "planet:pluto"],
        "element": ["element:air", "element:spirit"],
    },
    "primordial:sovereign": {
        "tarot": ["tarot:emperor", "tarot:justice"],
        "planet": ["planet:sun", "planet:jupiter"],
        "element": ["element:fire"],
    },
    "primordial:destroyer": {
        "tarot": ["tarot:tower", "tarot:death"],
        "planet": ["planet:pluto", "planet:mars"],
        "element": ["element:fire"],
    },
    "primordial:creator": {
        "tarot": ["tarot:magician", "tarot:empress"],
        "planet": ["planet:sun", "planet:venus"],
        "element": ["element:fire", "element:earth"],
    },
    "primordial:preserver": {
        "tarot": ["tarot:temperance", "tarot:star"],
        "planet": ["planet:jupiter"],
        "element": ["element:water"],
    },
    "primordial:psychopomp": {
        "tarot": ["tarot:death", "tarot:judgement"],
        "planet": ["planet:pluto", "planet:mercury"],
        "element": ["element:spirit"],
    },
    "primordial:healer": {
        "tarot": ["tarot:temperance", "tarot:star"],
        "planet": ["planet:chiron", "planet:neptune"],
        "element": ["element:water"],
    },
    "primordial:divine-child": {
        "tarot": ["tarot:fool", "tarot:sun"],
        "planet": ["planet:sun"],
        "element": ["element:fire", "element:spirit"],
    },
    "primordial:crone": {
        "tarot": ["tarot:high_priestess", "tarot:moon"],
        "planet": ["planet:saturn", "planet:moon"],
        "element": ["element:earth", "element:water"],
    },
    "primordial:maiden": {
        "tarot": ["tarot:star", "tarot:high_priestess"],
        "planet": ["planet:moon", "planet:venus"],
        "element": ["element:water", "element:air"],
    },
    "primordial:rebel": {
        "tarot": ["tarot:tower", "tarot:devil"],
        "planet": ["planet:uranus", "planet:pluto"],
        "element": ["element:fire"],
    },
    "primordial:outcast": {
        "tarot": ["tarot:hermit", "tarot:hanged_man"],
        "planet": ["planet:saturn", "planet:neptune"],
        "element": ["element:water"],
    },
}

# System-specific alias patterns
SYSTEM_ALIAS_PATTERNS = {
    # Greek - add Roman equivalents
    "greek": {
        "ZEUS": ["Jupiter (Roman)", "Jove"],
        "HERA": ["Juno (Roman)"],
        "ATHENA": ["Minerva (Roman)", "Pallas"],
        "APHRODITE": ["Venus (Roman)"],
        "ARES": ["Mars (Roman)"],
        "ARTEMIS": ["Diana (Roman)"],
        "APOLLO": ["Phoebus"],
        "HERMES": ["Mercury (Roman)"],
        "POSEIDON": ["Neptune (Roman)"],
        "HADES": ["Pluto (Roman)", "Dis Pater"],
        "DEMETER": ["Ceres (Roman)"],
        "HEPHAESTUS": ["Vulcan (Roman)"],
        "DIONYSUS": ["Bacchus (Roman)"],
        "HESTIA": ["Vesta (Roman)"],
        "PERSEPHONE": ["Proserpina (Roman)"],
        "EROS": ["Cupid (Roman)"],
        "CRONUS": ["Saturn (Roman)"],
    },
    # Norse - add Germanic equivalents
    "norse": {
        "ODIN": ["Wotan (Germanic)", "Woden (Anglo-Saxon)", "Allfather"],
        "THOR": ["Donar (Germanic)", "Thunor (Anglo-Saxon)"],
        "FREYA": ["Freyja", "Vanadis"],
        "FREYR": ["Frey", "Yngvi"],
        "TYR": ["Tiw (Anglo-Saxon)", "Ziu (Germanic)"],
        "LOKI": ["Lopt"],
        "FRIGG": ["Frigga", "Frige"],
        "BALDUR": ["Balder", "Baldr"],
        "HEL": ["Hela"],
    },
    # Egyptian - add transliteration variants
    "egyptian": {
        "RA": ["Re", "Ra-Horakhty"],
        "ISIS": ["Aset", "Eset"],
        "OSIRIS": ["Usir", "Wesir"],
        "HORUS": ["Heru", "Hor"],
        "THOTH": ["Djehuty", "Tehuti"],
        "ANUBIS": ["Anpu", "Inpu"],
        "SEKHMET": ["Sachmet", "Sakhmet"],
        "HATHOR": ["Het-Heru", "Hwt-Hr"],
        "SET": ["Seth", "Sutekh"],
        "NEPHTHYS": ["Nebet-Het"],
        "PTAH": ["Peteh"],
        "BASTET": ["Bast", "Ubasti"],
        "MA'AT": ["Maat", "Mayet"],
    },
    # Hindu - add Sanskrit variants
    "hindu": {
        "VISHNU": ["Narayana", "Hari", "The Preserver"],
        "SHIVA": ["Mahadeva", "Nataraja", "The Destroyer"],
        "BRAHMA": ["Prajapati", "The Creator"],
        "LAKSHMI": ["Shri", "Mahalakshmi"],
        "SARASWATI": ["Vani", "Sharada"],
        "PARVATI": ["Uma", "Gauri", "Shakti"],
        "GANESHA": ["Ganapati", "Vinayaka"],
        "DURGA": ["Devi", "Ambika"],
        "KALI": ["Kalika", "Dark Mother"],
        "KRISHNA": ["Govinda", "Vasudeva"],
        "RAMA": ["Ramachandra"],
        "HANUMAN": ["Anjaneya", "Maruti"],
        "INDRA": ["Shakra", "King of Devas"],
    },
    # Celtic - add variants
    "celtic": {
        "DAGDA": ["The Good God", "Eochaid Ollathair"],
        "BRIGID": ["Brighid", "Bride", "Brigit"],
        "MORRIGAN": ["Morrígan", "Phantom Queen"],
        "CERNUNNOS": ["The Horned One"],
        "LUGH": ["Lug", "Lugus"],
        "DANU": ["Dana", "Anu"],
        "NUADA": ["Nuadu", "Nodens"],
        "OGMA": ["Ogmios"],
    },
    # Japanese - add romanization variants
    "japanese": {
        "AMATERASU": ["Amaterasu-Omikami", "Ohirume-no-muchi"],
        "SUSANOO": ["Susano-o", "Susanowo"],
        "TSUKUYOMI": ["Tsukiyomi", "Tsuki-yomi"],
        "IZANAGI": ["Izanaki"],
        "IZANAMI": ["Izanami-no-Mikoto"],
        "INARI": ["O-Inari-sama"],
        "RAIJIN": ["Raiden"],
        "FUJIN": ["Futen"],
    },
}

# Description templates by primordial type
DESCRIPTION_TEMPLATES = {
    "primordial:hero": "{name} embodies the archetypal hero, representing courage, adventure, and the triumph over adversity.",
    "primordial:great-mother": "{name} represents the nurturing, life-giving aspect of the feminine divine, associated with fertility, abundance, and protection.",
    "primordial:great-father": "{name} embodies paternal authority, order, and cosmic law, representing structure and protection.",
    "primordial:trickster": "{name} is a trickster figure who crosses boundaries, challenges conventions, and brings change through cunning and mischief.",
    "primordial:wise-elder": "{name} represents wisdom, knowledge, and guidance, serving as a teacher and keeper of sacred traditions.",
    "primordial:lover": "{name} embodies love, passion, and connection, representing the transformative power of emotional bonds.",
    "primordial:warrior": "{name} represents martial prowess, courage in battle, and the protective use of force.",
    "primordial:magician": "{name} embodies the power of transformation, hidden knowledge, and the manipulation of natural forces.",
    "primordial:sovereign": "{name} represents divine kingship, justice, and the right ordering of society and cosmos.",
    "primordial:destroyer": "{name} embodies the necessary forces of destruction and transformation that clear the way for renewal.",
    "primordial:creator": "{name} represents the creative principle, the power to bring new forms and realities into being.",
    "primordial:preserver": "{name} embodies the sustaining forces that maintain cosmic order and protect existence.",
    "primordial:psychopomp": "{name} serves as a guide between worlds, conducting souls through transitions and thresholds.",
    "primordial:healer": "{name} represents the power of healing, restoration, and the mending of wounds both physical and spiritual.",
    "primordial:divine-child": "{name} embodies innocence, potential, and the promise of new beginnings and renewal.",
    "primordial:crone": "{name} represents the wisdom of age, knowledge of mysteries, and power over life's transitions.",
    "primordial:maiden": "{name} embodies youthful vitality, purity, and the potential of new growth.",
    "primordial:rebel": "{name} challenges established order, breaks boundaries, and catalyzes revolutionary change.",
    "primordial:outcast": "{name} exists at the margins, representing those excluded from society who gain unique perspective.",
}


def get_system_from_id(arch_id: str) -> str:
    """Extract system from archetype ID."""
    if ":" not in arch_id:
        return ""
    parts = arch_id.split(":")[-1].split("-")
    if len(parts) > 1:
        prefix = parts[0].upper()
        system_map = {
            "GR": "greek", "NO": "norse", "EG": "egyptian",
            "CE": "celtic", "IN": "hindu", "JP": "japanese",
            "CN": "chinese", "ME": "mesopotamian", "AF": "african",
            "MA": "mesoamerican", "SL": "slavic", "PL": "polynesian",
            "NA": "native_american", "FI": "finnish", "AU": "australian",
            "IC": "incan", "PE": "persian", "RO": "roman",
            "BU": "buddhist", "VO": "vodou",
        }
        return system_map.get(prefix, "")
    return ""


def generate_aliases(arch_id: str, name: str, existing: List) -> List[str]:
    """Generate aliases for an archetype."""
    # Handle mixed alias formats (strings and dicts)
    aliases = []
    for a in (existing or []):
        if isinstance(a, str):
            aliases.append(a)
        elif isinstance(a, dict):
            aliases.append(a.get("name", str(a)))
        else:
            aliases.append(str(a))

    existing_lower = {a.lower() for a in aliases if isinstance(a, str)}

    system = get_system_from_id(arch_id)

    # Check system-specific aliases
    if system in SYSTEM_ALIAS_PATTERNS:
        # Extract the deity name part
        parts = arch_id.split(":")[-1].split("-")
        if len(parts) > 1:
            deity_key = "-".join(parts[1:]).upper()
            if deity_key in SYSTEM_ALIAS_PATTERNS[system]:
                for alias in SYSTEM_ALIAS_PATTERNS[system][deity_key]:
                    if alias.lower() not in existing_lower:
                        aliases.append(alias)
                        existing_lower.add(alias.lower())

    # Generate from name variations
    # Remove parenthetical qualifiers for base name
    base_name = re.sub(r'\s*\([^)]+\)', '', name).strip()

    # Add "The X" variant if name is a single word
    if " " not in base_name and not base_name.startswith("The "):
        the_variant = f"The {base_name}"
        if the_variant.lower() not in existing_lower:
            aliases.append(the_variant)

    return aliases[:8]  # Limit to 8 aliases


def generate_correspondences(instantiates: List[dict], existing: dict) -> dict:
    """Generate correspondences based on primordial types."""
    if existing and len(existing) > 1:  # Has more than just empty fields
        return existing

    correspondences = dict(existing) if existing else {}

    for inst in instantiates:
        primordial = inst.get("primordial", "")
        weight = inst.get("weight", 0.5)

        if weight < 0.5:  # Only use strong instantiations
            continue

        if primordial in PRIMORDIAL_CORRESPONDENCES:
            corr = PRIMORDIAL_CORRESPONDENCES[primordial]

            # Add tarot correspondence if not present
            if "tarot" not in correspondences and "tarot" in corr:
                correspondences["tarot"] = corr["tarot"][0]

            # Add planet if not present
            if "planet" not in correspondences and "planet" in corr:
                correspondences["planet"] = corr["planet"][0]

            # Add element if not present
            if "element" not in correspondences and "element" in corr:
                correspondences["element"] = corr["element"][0]

    return correspondences if correspondences else None


def generate_description(name: str, instantiates: List[dict], system: str) -> str:
    """Generate a basic description based on primordial types."""
    if not instantiates:
        return f"{name} is an archetypal figure in the {system} tradition."

    # Use the strongest primordial for the template
    strongest = max(instantiates, key=lambda x: x.get("weight", 0))
    primordial = strongest.get("primordial", "")

    if primordial in DESCRIPTION_TEMPLATES:
        return DESCRIPTION_TEMPLATES[primordial].format(name=name)

    # Fallback
    return f"{name} is an archetypal figure embodying key patterns in the {system} tradition."


def enrich_file(file_path: Path, dry_run: bool = True) -> Dict[str, int]:
    """Enrich a single file with aliases, correspondences, and descriptions."""
    stats = {"aliases": 0, "correspondences": 0, "descriptions": 0, "entries": 0}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"  Error loading {file_path}: {e}")
        return stats

    # Get entries
    entries = data.get("entries", [])
    if "suits" in data:  # Tarot minor arcana
        for suit in data.get("suits", []):
            entries.extend(suit.get("cards", []))

    modified = False

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        arch_id = entry.get("@id", "")
        if arch_id.startswith("system:"):
            continue

        name = entry.get("name", "")
        system = get_system_from_id(arch_id)
        instantiates = entry.get("instantiates", [])

        # Enrich aliases
        existing_aliases = entry.get("aliases", [])
        new_aliases = generate_aliases(arch_id, name, existing_aliases)
        if len(new_aliases) > len(existing_aliases):
            entry["aliases"] = new_aliases
            stats["aliases"] += len(new_aliases) - len(existing_aliases)
            modified = True

        # Enrich correspondences
        existing_corr = entry.get("correspondences", {})
        new_corr = generate_correspondences(instantiates, existing_corr)
        if new_corr and new_corr != existing_corr:
            entry["correspondences"] = new_corr
            stats["correspondences"] += 1
            modified = True

        # Generate description if missing
        if not entry.get("description"):
            desc = generate_description(name, instantiates, system or "mythological")
            entry["description"] = desc
            stats["descriptions"] += 1
            modified = True

        stats["entries"] += 1

    if modified and not dry_run:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return stats


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Phase 3: Aliases, Correspondences, Descriptions')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Show what would be changed without modifying files')
    parser.add_argument('--apply', action='store_true',
                        help='Actually apply the changes')
    args = parser.parse_args()

    dry_run = not args.apply

    print("=" * 70)
    print("PHASE 3: ALIASES, CORRESPONDENCES & DESCRIPTIONS")
    print("=" * 70)
    if dry_run:
        print("\n[DRY RUN - No files will be modified. Use --apply to save changes.]\n")

    acp_path = Path("ACP")

    patterns = [
        "archetypes/**/*.jsonld",
        "divination/**/*.jsonld",
        "psychology/**/*.jsonld",
        "modern/**/*.jsonld",
    ]

    total_stats = {"aliases": 0, "correspondences": 0, "descriptions": 0, "files": 0}

    for pattern in patterns:
        for file_path in acp_path.glob(pattern):
            stats = enrich_file(file_path, dry_run)
            if stats["aliases"] > 0 or stats["correspondences"] > 0 or stats["descriptions"] > 0:
                total_stats["files"] += 1
                total_stats["aliases"] += stats["aliases"]
                total_stats["correspondences"] += stats["correspondences"]
                total_stats["descriptions"] += stats["descriptions"]

    print("\n" + "=" * 40)
    print("SUMMARY")
    print("=" * 40)
    print(f"Files modified:        {total_stats['files']}")
    print(f"Aliases added:         {total_stats['aliases']}")
    print(f"Correspondences added: {total_stats['correspondences']}")
    print(f"Descriptions added:    {total_stats['descriptions']}")

    if dry_run:
        print("\n[DRY RUN complete. Run with --apply to save changes.]")
    else:
        print("\n[Changes saved successfully.]")


if __name__ == '__main__':
    main()
