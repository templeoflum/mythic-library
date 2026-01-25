#!/usr/bin/env python3
"""
Analyze gaps in the Mythic Library collection.

This script identifies missing texts and underrepresented areas
to guide systematic collection expansion.
"""

import sys
import io
import csv
import json
from pathlib import Path
from collections import defaultdict

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SOURCES_DIR = Path(__file__).parent.parent / "sources"
MASTER_CATALOG = SOURCES_DIR / "master_catalog.csv"

# =============================================================================
# IDEAL COVERAGE FRAMEWORK
# =============================================================================

# Major world regions that should have mythic representation
IDEAL_REGIONS = {
    # Well-represented in Western collections
    "greco-roman": ["greek", "roman"],
    "near-eastern": ["mesopotamian", "egyptian", "levantine", "hebrew", "persian"],
    "european": ["norse", "celtic", "germanic", "slavic", "baltic", "finno-ugric"],
    "south-asian": ["indian", "tibetan"],
    "east-asian": ["chinese", "japanese", "korean"],
    "southeast-asian": ["southeast-asian"],  # Vietnam, Thailand, Indonesia, etc.

    # Often underrepresented
    "african": ["african"],  # Should break down: West, East, South, Central, North
    "oceanic": ["polynesian", "melanesian", "australian-aboriginal"],
    "americas-north": ["north-american"],  # Many distinct nations
    "americas-meso": ["mesoamerican"],  # Maya, Aztec, Olmec, etc.
    "americas-south": ["south-american"],  # Inca, Amazonian, etc.
    "central-asian": ["turkic", "mongol", "siberian"],
    "arctic": ["arctic"],  # Inuit, Sami, etc.
}

# Key myth TYPES that should be represented across cultures
MYTHIC_TYPES = {
    "cosmogony": {
        "description": "Creation myths - how the world began",
        "examples": ["Enuma Elish", "Genesis", "Popol Vuh", "Rigveda hymns"],
        "archetypes": ["primordial waters", "cosmic egg", "divine word", "sacrifice"],
    },
    "theogony": {
        "description": "Origin of gods and divine hierarchy",
        "examples": ["Theogony", "Prose Edda"],
        "archetypes": ["divine generations", "titanomachy", "divine council"],
    },
    "anthropogony": {
        "description": "Origin of humans",
        "examples": ["Genesis", "Popol Vuh", "various flood myths"],
        "archetypes": ["clay creation", "divine breath", "emergence", "descent"],
    },
    "cataclysm": {
        "description": "Flood and destruction myths",
        "examples": ["Gilgamesh (Tablet XI)", "Atra-Hasis", "Genesis flood", "Deucalion"],
        "archetypes": ["divine punishment", "chosen survivor", "renewal"],
    },
    "hero_journey": {
        "description": "Individual hero transformation",
        "examples": ["Gilgamesh", "Odyssey", "Ramayana"],
        "archetypes": ["call", "threshold", "trials", "return"],
    },
    "descent": {
        "description": "Journey to underworld/death realm",
        "examples": ["Inanna's Descent", "Orpheus", "Izanagi"],
        "archetypes": ["death gate", "stripping", "return transformed"],
    },
    "trickster": {
        "description": "Trickster cycles and culture heroes",
        "examples": ["Anansi", "Coyote", "Loki", "Hermes"],
        "archetypes": ["boundary crossing", "theft of fire/knowledge", "transformation"],
    },
    "dying_god": {
        "description": "Death and resurrection of divine figure",
        "examples": ["Osiris", "Baal", "Attis", "Dionysus"],
        "archetypes": ["sacrifice", "dismemberment", "renewal", "vegetation"],
    },
    "sacred_marriage": {
        "description": "Divine union and fertility",
        "examples": ["Inanna and Dumuzi", "various fertility myths"],
        "archetypes": ["hieros gamos", "seasonal cycle"],
    },
    "monster_slaying": {
        "description": "Combat with primordial chaos",
        "examples": ["Marduk vs Tiamat", "Thor vs Jormungandr", "Indra vs Vritra"],
        "archetypes": ["chaos dragon", "cosmic order", "warrior god"],
    },
    "eschatology": {
        "description": "End times and cosmic cycles",
        "examples": ["Ragnarok", "Revelation", "Kalki"],
        "archetypes": ["world destruction", "final battle", "renewal"],
    },
    "metamorphosis": {
        "description": "Transformation myths",
        "examples": ["Ovid's Metamorphoses", "various"],
        "archetypes": ["punishment", "escape", "transcendence"],
    },
}

# Key ARCHETYPES that should appear across the collection
KEY_ARCHETYPES = {
    "hero": "The one who undertakes the journey",
    "trickster": "Boundary-crosser, transformer",
    "wise_elder": "Guide, mentor, wisdom keeper",
    "great_mother": "Fertility, nurture, devouring",
    "sky_father": "Order, law, authority",
    "shadow": "The rejected, the enemy, the other",
    "anima_animus": "Contrasexual inner figure",
    "child": "Potential, innocence, new beginning",
    "threshold_guardian": "Tests the hero",
    "shapeshifter": "Changes form, allegiance unclear",
    "herald": "Announces change, calls to adventure",
}

# Specific MISSING TEXTS that are critically important
CRITICAL_MISSING = [
    # Mesopotamian
    {"title": "Inanna's Descent", "tradition": "mesopotamian", "type": "descent",
     "importance": "CRITICAL - archetypal descent narrative, pre-Orpheus"},
    {"title": "Inanna and Dumuzi", "tradition": "mesopotamian", "type": "sacred_marriage",
     "importance": "Foundational sacred marriage myth"},
    {"title": "Descent of Ishtar", "tradition": "mesopotamian", "type": "descent",
     "importance": "Akkadian version of descent"},

    # Egyptian
    {"title": "Pyramid Texts", "tradition": "egyptian", "type": "funerary",
     "importance": "Oldest religious texts in the world"},
    {"title": "Coffin Texts", "tradition": "egyptian", "type": "funerary",
     "importance": "Bridge between Pyramid Texts and Book of Dead"},
    {"title": "Contendings of Horus and Seth", "tradition": "egyptian", "type": "theogony",
     "importance": "Major Egyptian mythological narrative"},

    # Greek - filling gaps
    {"title": "Homeric Hymns", "tradition": "greek", "type": "theogony",
     "importance": "Major source for Greek myth - Demeter, Apollo, Hermes, Aphrodite"},
    {"title": "Orphic Hymns", "tradition": "greek", "type": "mystery",
     "importance": "Mystery tradition, different cosmogony"},
    {"title": "Metamorphoses (Ovid)", "tradition": "roman", "type": "metamorphosis",
     "importance": "CRITICAL - comprehensive transformation myths"},
    {"title": "Aeneid", "tradition": "roman", "type": "hero_journey",
     "importance": "Roman foundation myth, descent narrative"},
    {"title": "Argonautica", "tradition": "greek", "type": "hero_journey",
     "importance": "Jason quest, pre-Odyssey pattern"},

    # Norse - filling gaps
    {"title": "Völsunga saga", "tradition": "norse", "type": "hero_journey",
     "importance": "Sigurd cycle, source for Wagner"},
    {"title": "Hervarar saga", "tradition": "norse", "type": "heroic",
     "importance": "Legendary saga with mythological elements"},

    # Celtic
    {"title": "Lebor Gabála Érenn", "tradition": "celtic", "type": "cosmogony",
     "importance": "Irish Book of Invasions - Irish mythological history"},
    {"title": "Cath Maige Tuired", "tradition": "celtic", "type": "theogony",
     "importance": "Battle of Moytura - Tuatha Dé Danann"},

    # Slavic (MAJOR GAP)
    {"title": "Russian Byliny", "tradition": "slavic", "type": "heroic",
     "importance": "Epic songs - Ilya Muromets, etc."},
    {"title": "Slavic Folk Tales (Afanasyev expanded)", "tradition": "slavic", "type": "folklore",
     "importance": "Baba Yaga, Koschei, firebird"},

    # South American (MAJOR GAP)
    {"title": "Inca Creation Myths", "tradition": "south-american", "type": "cosmogony",
     "importance": "Viracocha, Inti - Andean cosmology"},
    {"title": "Guarani Creation Myth", "tradition": "south-american", "type": "cosmogony",
     "importance": "Tupã, Amazonian mythology"},
    {"title": "Mapuche Mythology", "tradition": "south-american", "type": "cosmogony",
     "importance": "Chilean indigenous tradition"},

    # Australian (MAJOR GAP)
    {"title": "Dreamtime Stories", "tradition": "australian-aboriginal", "type": "cosmogony",
     "importance": "CRITICAL GAP - oldest continuous culture"},

    # African (needs more specificity)
    {"title": "Dogon Cosmogony", "tradition": "african-west", "type": "cosmogony",
     "importance": "Complex creation myth - Amma, Nommo"},
    {"title": "Fon/Dahomey Mythology", "tradition": "african-west", "type": "theogony",
     "importance": "Mawu-Lisa, vodun origins"},
    {"title": "Zulu Creation Myth", "tradition": "african-south", "type": "cosmogony",
     "importance": "Unkulunkulu"},
    {"title": "Egyptian Mythology (Heliopolitan)", "tradition": "egyptian", "type": "cosmogony",
     "importance": "Atum, Ennead - missing separate from Book of Dead"},

    # Chinese (expansion)
    {"title": "Shan Hai Jing", "tradition": "chinese", "type": "geography/mythology",
     "importance": "Classic of Mountains and Seas - mythical bestiary"},
    {"title": "Huainanzi", "tradition": "chinese", "type": "cosmogony",
     "importance": "Daoist cosmology, creation myths"},

    # Japanese (expansion)
    {"title": "Nihon Shoki", "tradition": "japanese", "type": "chronicle",
     "importance": "Second oldest chronicle, variant myths"},
    {"title": "Fudoki", "tradition": "japanese", "type": "local mythology",
     "importance": "Regional myths and legends"},

    # Korean (MAJOR GAP)
    {"title": "Dangun Myth", "tradition": "korean", "type": "cosmogony",
     "importance": "Korean foundation myth"},
    {"title": "Samguk Yusa", "tradition": "korean", "type": "legendary history",
     "importance": "Memorabilia of the Three Kingdoms"},

    # Oceanic expansion
    {"title": "Maui Cycle", "tradition": "polynesian", "type": "trickster",
     "importance": "Polynesian trickster-hero"},
    {"title": "Melanesian Myths", "tradition": "melanesian", "type": "various",
     "importance": "Distinct from Polynesian tradition"},

    # Central Asian
    {"title": "Mongol Secret History", "tradition": "mongol", "type": "legendary history",
     "importance": "Chinggis Khan origins, steppe mythology"},
    {"title": "Siberian Shamanic Texts", "tradition": "siberian", "type": "shamanic",
     "importance": "Circumpolar shamanism"},

    # Mystery/Esoteric traditions
    {"title": "Hermetic Corpus", "tradition": "greco-egyptian", "type": "esoteric",
     "importance": "Hermeticism foundation"},
    {"title": "Chaldean Oracles", "tradition": "greco-near-eastern", "type": "esoteric",
     "importance": "Neoplatonic mysticism"},
]


def load_catalog():
    """Load the master catalog."""
    with open(MASTER_CATALOG, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def analyze_regional_coverage(catalog):
    """Analyze coverage by world region."""
    print("\n" + "=" * 70)
    print("REGIONAL COVERAGE ANALYSIS")
    print("=" * 70)

    traditions_present = set(t["tradition"] for t in catalog)

    for region, traditions in IDEAL_REGIONS.items():
        covered = [t for t in traditions if t in traditions_present]
        missing = [t for t in traditions if t not in traditions_present]

        count = sum(1 for t in catalog if t["tradition"] in traditions)

        if missing:
            status = "⚠️  GAPS"
        elif count < 3:
            status = "📉 THIN"
        else:
            status = "✅ OK"

        print(f"\n{region.upper()} ({status})")
        print(f"  Traditions present: {', '.join(covered) if covered else 'NONE'}")
        print(f"  Texts: {count}")
        if missing:
            print(f"  MISSING traditions: {', '.join(missing)}")


def analyze_typological_coverage(catalog):
    """Analyze coverage by myth type."""
    print("\n" + "=" * 70)
    print("TYPOLOGICAL COVERAGE ANALYSIS")
    print("=" * 70)

    # This is harder to automate - would need to tag each text by type
    # For now, just list the types and note obvious gaps

    print("\nMythic types that should be represented:")
    for mtype, info in MYTHIC_TYPES.items():
        print(f"\n{mtype.upper()}: {info['description']}")
        print(f"  Key examples: {', '.join(info['examples'][:3])}")
        print(f"  Core archetypes: {', '.join(info['archetypes'][:3])}")


def list_critical_missing(catalog):
    """List critically important missing texts."""
    print("\n" + "=" * 70)
    print("CRITICAL MISSING TEXTS")
    print("=" * 70)

    existing_titles = set(t["title"].lower() for t in catalog)

    by_priority = {"CRITICAL": [], "HIGH": [], "MEDIUM": []}

    for text in CRITICAL_MISSING:
        if text["title"].lower() not in existing_titles:
            importance = text.get("importance", "")
            if "CRITICAL" in importance.upper():
                by_priority["CRITICAL"].append(text)
            elif "MAJOR" in importance.upper():
                by_priority["HIGH"].append(text)
            else:
                by_priority["MEDIUM"].append(text)

    for priority, texts in by_priority.items():
        if texts:
            print(f"\n{priority} PRIORITY:")
            for t in texts:
                print(f"  • {t['title']} ({t['tradition']})")
                print(f"    Type: {t['type']}")
                print(f"    Why: {t['importance']}")


def suggest_research_queries(catalog):
    """Suggest specific research queries to fill gaps."""
    print("\n" + "=" * 70)
    print("RESEARCH QUERIES TO FILL GAPS")
    print("=" * 70)

    queries = [
        # Regional gaps
        ("Korean mythology texts public domain", "korean"),
        ("Australian Aboriginal dreamtime stories public domain text", "australian-aboriginal"),
        ("South American Inca mythology texts translation", "south-american"),
        ("Slavic mythology Byliny English translation", "slavic"),
        ("Dogon creation myth Griaule translation", "african"),

        # Typological gaps
        ("Inanna descent Wolkstein Kramer translation", "mesopotamian"),
        ("Homeric Hymns Evelyn-White", "greek"),
        ("Ovid Metamorphoses public domain", "roman"),
        ("Shan Hai Jing Classic Mountains Seas translation", "chinese"),

        # Archival sources
        ("Internet Archive mythology folklore public domain", "various"),
        ("Sacred Texts archive comparative mythology", "various"),
        ("Project Gutenberg folklore myths", "various"),
    ]

    print("\nSuggested searches:")
    for query, tradition in queries:
        print(f"\n  [{tradition}]")
        print(f"  Query: {query}")
        print(f"  archive.org: https://archive.org/search?query={query.replace(' ', '+')}")


def main():
    catalog = load_catalog()

    print("=" * 70)
    print("MYTHIC LIBRARY GAP ANALYSIS")
    print("=" * 70)
    print(f"\nCurrent collection: {len(catalog)} texts")

    analyze_regional_coverage(catalog)
    analyze_typological_coverage(catalog)
    list_critical_missing(catalog)
    suggest_research_queries(catalog)

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("""
1. IMMEDIATE: Fill critical gaps (Inanna's Descent, Metamorphoses, Homeric Hymns)
2. SHORT-TERM: Add underrepresented regions (Korean, Slavic, South American)
3. MEDIUM-TERM: Tag existing texts by mythic type for better coverage analysis
4. LONG-TERM: Build archetypal index across all texts
    """)


if __name__ == "__main__":
    main()
