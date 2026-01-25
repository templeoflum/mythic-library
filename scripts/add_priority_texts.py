#!/usr/bin/env python3
"""
Add priority texts to fill critical gaps in the Mythic Library.
Focus on: Zoroastrian, Dying God pattern, Japanese expansion, Yoruba/Ifa.
"""

import sys
import io
import csv
import json
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SOURCES_DIR = Path(__file__).parent.parent / "sources"
TEXTS_DIR = Path(__file__).parent.parent / "texts"
MASTER_CATALOG = SOURCES_DIR / "master_catalog.csv"
CURATED_SOURCES = SOURCES_DIR / "curated_sources.json"

# Priority texts to fill critical gaps
PRIORITY_TEXTS = [
    # ZOROASTRIAN - Tier 1 Critical (Persian cosmology, eschatology, dualism)
    {
        "catalog": {
            "text_id": "zend-avesta",
            "title": "Zend Avesta (Sacred Books of the East)",
            "author": "Anonymous (Zoroaster attributed)",
            "tradition": "zoroastrian",
            "origin_raw": "Persia (Iran)",
            "date_composed": "c. 1500-500 BCE (compiled later)",
            "material_type": "Religious scripture",
            "status": "pending",
            "notes": "Complete 3-part translation: Vendidad, Sirozahs/Yasts/Nyayis, Yasna/Visparad/Afrinagans",
        },
        "sources": [
            {
                "source_name": "Sacred Texts (Part I - Vendidad)",
                "source_url": "https://sacred-texts.com/zor/sbe04/index.htm",
                "translator": "James Darmesteter",
                "year": 1880,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Sacred Books of the East Vol. 4 - Vendidad (purity laws)"
            },
            {
                "source_name": "Sacred Texts (Part II - Sirozahs/Yasts)",
                "source_url": "https://sacred-texts.com/zor/sbe23/index.htm",
                "translator": "James Darmesteter",
                "year": 1883,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Sacred Books of the East Vol. 23 - Hymns to deities"
            },
            {
                "source_name": "Sacred Texts (Part III - Yasna)",
                "source_url": "https://sacred-texts.com/zor/sbe31/index.htm",
                "translator": "L.H. Mills",
                "year": 1887,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Sacred Books of the East Vol. 31 - Liturgical texts"
            },
        ]
    },

    # EGYPTIAN - Osiris myth (Tier 1 Critical for Dying God archetype)
    {
        "catalog": {
            "text_id": "legends-of-egyptian-gods",
            "title": "Legends of the Gods: The Egyptian Texts",
            "author": "E.A. Wallis Budge (editor/translator)",
            "tradition": "egyptian",
            "origin_raw": "Ancient Egypt",
            "date_composed": "Various ancient sources",
            "material_type": "Mythology compilation",
            "status": "pending",
            "notes": "Contains Isis and Osiris narrative - fills Dying God archetype gap",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/egy/leg/index.htm",
                "translator": "E.A. Wallis Budge",
                "year": 1912,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Includes History of Isis and Osiris (40+ sections)"
            },
        ]
    },

    # JAPANESE - Nihon Shoki (Tier 1 Critical for validation with Kojiki)
    {
        "catalog": {
            "text_id": "nihongi",
            "title": "Nihongi (Chronicles of Japan)",
            "author": "Prince Toneri et al.",
            "tradition": "japanese",
            "origin_raw": "Japan",
            "date_composed": "720 CE",
            "material_type": "Mythic chronicle",
            "status": "pending",
            "notes": "Second oldest Japanese chronicle - complements Kojiki for validation",
        },
        "sources": [
            {
                "source_name": "Sacred Texts (Part 1)",
                "source_url": "https://sacred-texts.com/shi/nihon0.htm",
                "translator": "W.G. Aston",
                "year": 1896,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Nihongi Part 1 - Age of Gods"
            },
            {
                "source_name": "Sacred Texts (Part 2)",
                "source_url": "https://sacred-texts.com/shi/nihon1.htm",
                "translator": "W.G. Aston",
                "year": 1896,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Nihongi Part 2"
            },
            {
                "source_name": "Sacred Texts (Part 3)",
                "source_url": "https://sacred-texts.com/shi/nihon2.htm",
                "translator": "W.G. Aston",
                "year": 1896,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Nihongi Part 3"
            },
            {
                "source_name": "Sacred Texts (Part 4)",
                "source_url": "https://sacred-texts.com/shi/nihon3.htm",
                "translator": "W.G. Aston",
                "year": 1896,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Nihongi Part 4"
            },
        ]
    },

    # YORUBA/IFA - Tier 2 High (Major African tradition, Eshu trickster)
    {
        "catalog": {
            "text_id": "myths-of-ife",
            "title": "Myths of Ife",
            "author": "John Wyndham (collector)",
            "tradition": "african",
            "origin_raw": "Nigeria (Yoruba)",
            "date_composed": "Ancient oral tradition (collected 1921)",
            "material_type": "Creation mythology",
            "status": "pending",
            "notes": "Yoruba creation myth from Ife priests - War of Gods, cosmogony",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/afr/ife/index.htm",
                "translator": "John Wyndham",
                "year": 1921,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Recited by high priests of Ife - creation, gods, sacred city"
            },
        ]
    },
    {
        "catalog": {
            "text_id": "yoruba-speaking-peoples",
            "title": "The Yoruba-Speaking Peoples of the Slave Coast of West Africa",
            "author": "A.B. Ellis",
            "tradition": "african",
            "origin_raw": "Nigeria/Benin (Yoruba)",
            "date_composed": "1894 (oral tradition ancient)",
            "material_type": "Ethnography/Mythology",
            "status": "pending",
            "notes": "Comprehensive Yoruba religion and mythology including Eshu, Ogun, Shango",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/afr/yor/index.htm",
                "translator": "A.B. Ellis",
                "year": 1894,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Detailed account of Yoruba deities and religious practices"
            },
        ]
    },

    # GREEK - Bacchae (Tier 2 for Dying God - Dionysus/Zagreus)
    {
        "catalog": {
            "text_id": "bacchae",
            "title": "The Bacchae",
            "author": "Euripides",
            "tradition": "greek",
            "origin_raw": "Ancient Greece",
            "date_composed": "c. 405 BCE",
            "material_type": "Tragedy",
            "status": "pending",
            "notes": "Dionysus mythology - fills Dying God archetype gap",
        },
        "sources": [
            {
                "source_name": "Project Gutenberg",
                "source_url": "https://www.gutenberg.org/ebooks/35173",
                "translator": "Gilbert Murray",
                "format": "txt",
                "quality_tier": "scholarly",
                "notes": "Gilbert Murray verse translation"
            },
            {
                "source_name": "Project Gutenberg (with Hippolytus)",
                "source_url": "https://www.gutenberg.org/ebooks/8418",
                "translator": "Gilbert Murray",
                "format": "txt",
                "quality_tier": "scholarly",
                "notes": "Combined Hippolytus and Bacchae"
            },
        ]
    },

    # JAPANESE - Kogoshui (additional Shinto source)
    {
        "catalog": {
            "text_id": "kogoshui",
            "title": "Kogoshui: Gleanings from Ancient Stories",
            "author": "Imibe no Hironari",
            "tradition": "japanese",
            "origin_raw": "Japan",
            "date_composed": "807 CE",
            "material_type": "Mythic chronicle",
            "status": "pending",
            "notes": "Third major Shinto text - supplements Kojiki and Nihongi",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/shi/kgsh/index.htm",
                "translator": "Genchi Kato & Hikoshiro Hoshino",
                "year": 1926,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Legendary Shinto tales from primary source"
            },
        ]
    },

    # EGYPTIAN - Burden of Isis (Hymns to Isis)
    {
        "catalog": {
            "text_id": "burden-of-isis",
            "title": "The Burden of Isis",
            "author": "Anonymous (Ancient Egyptian)",
            "tradition": "egyptian",
            "origin_raw": "Ancient Egypt",
            "date_composed": "Ancient (various periods)",
            "material_type": "Religious hymns",
            "status": "pending",
            "notes": "Hymns to Isis - Great Mother archetype",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/egy/boi/index.htm",
                "translator": "James Teackle Dennis",
                "year": 1910,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Hymns to the goddess Isis"
            },
        ]
    },

    # HESIOD - Works and Days (complements Theogony)
    {
        "catalog": {
            "text_id": "works-and-days",
            "title": "Works and Days",
            "author": "Hesiod",
            "tradition": "greek",
            "origin_raw": "Ancient Greece",
            "date_composed": "c. 700 BCE",
            "material_type": "Didactic poetry",
            "status": "pending",
            "notes": "Five Ages of Man, Prometheus myth - complements Theogony",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/cla/hesiod/works.htm",
                "translator": "Hugh G. Evelyn-White",
                "year": 1914,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Loeb Classical Library translation"
            },
        ]
    },
]


def load_catalog():
    """Load current catalog."""
    with open(MASTER_CATALOG, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_catalog(catalog):
    """Save updated catalog."""
    fieldnames = ["text_id", "title", "author", "tradition", "origin_raw",
                  "date_composed", "material_type", "status", "notes"]
    with open(MASTER_CATALOG, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(catalog)


def load_curated():
    """Load curated sources."""
    with open(CURATED_SOURCES, "r", encoding="utf-8") as f:
        return json.load(f)


def save_curated(curated):
    """Save curated sources."""
    with open(CURATED_SOURCES, "w", encoding="utf-8") as f:
        json.dump(curated, f, indent=2, ensure_ascii=False)


def create_text_directory(text_id, tradition):
    """Create directory structure for new text."""
    text_dir = TEXTS_DIR / tradition / text_id
    text_dir.mkdir(parents=True, exist_ok=True)
    return text_dir


def main():
    print("=" * 70)
    print("ADDING PRIORITY TEXTS TO FILL CRITICAL GAPS")
    print("=" * 70)

    catalog = load_catalog()
    curated = load_curated()

    existing_ids = set(t["text_id"] for t in catalog)

    added = 0
    skipped = 0

    for text in PRIORITY_TEXTS:
        text_id = text["catalog"]["text_id"]
        tradition = text["catalog"]["tradition"]
        title = text["catalog"]["title"]

        if text_id in existing_ids:
            print(f"SKIP: {text_id} (already exists)")
            skipped += 1
            continue

        # Add to catalog
        catalog.append(text["catalog"])

        # Add to curated sources
        curated["texts"][text_id] = {
            "title": title,
            "sources": text["sources"]
        }

        # Create directory
        create_text_directory(text_id, tradition)

        print(f"ADD:  {text_id}")
        print(f"      Title: {title}")
        print(f"      Tradition: {tradition}")
        print(f"      Sources: {len(text['sources'])}")
        added += 1

    # Save updates
    save_catalog(catalog)
    save_curated(curated)

    print("=" * 70)
    print(f"Added {added} new texts, skipped {skipped}")
    print(f"Total catalog size: {len(catalog)} texts")
    print("=" * 70)

    # Print gap fills by category
    print("\nGaps filled:")
    print("  DYING GOD: legends-of-egyptian-gods (Osiris), bacchae (Dionysus)")
    print("  ZOROASTRIAN: zend-avesta (3-part complete)")
    print("  JAPANESE: nihongi, kogoshui (validates Kojiki)")
    print("  YORUBA/IFA: myths-of-ife, yoruba-speaking-peoples")
    print("  GREAT MOTHER: burden-of-isis")
    print("  GREEK EXPANSION: works-and-days")


if __name__ == "__main__":
    main()
