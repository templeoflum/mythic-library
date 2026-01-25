#!/usr/bin/env python3
"""
Add Tier 3 texts to fill remaining gaps in the Mythic Library.
Focus on: Buddhist expansion, Slavic, African expansion, more regional.
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

# Tier 3 texts
TIER3_TEXTS = [
    # BUDDHIST - Jataka Tales (complete Cowell edition)
    {
        "catalog": {
            "text_id": "jataka-cowell",
            "title": "The Jataka (Cowell Edition - Complete)",
            "author": "Anonymous (Buddhist)",
            "tradition": "indian",
            "origin_raw": "India (Buddhist)",
            "date_composed": "c. 4th century BCE onward",
            "material_type": "Birth stories",
            "status": "pending",
            "notes": "547 birth stories of the Buddha - complete 6 volume Cowell/Cambridge edition",
        },
        "sources": [
            {
                "source_name": "Internet Archive (Vol 1)",
                "source_url": "https://archive.org/details/jatakaorstoriesofb01cowe",
                "translator": "Robert Chalmers",
                "year": 1895,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Cambridge University Press Vol. 1"
            },
            {
                "source_name": "Internet Archive (Vols 1-2)",
                "source_url": "https://archive.org/details/in.gov.ignca.5753",
                "translator": "E.B. Cowell et al.",
                "year": 1895,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Volumes 1-2 combined"
            },
            {
                "source_name": "Internet Archive (Vols 3-4)",
                "source_url": "https://archive.org/details/in.gov.ignca.5756",
                "translator": "E.B. Cowell et al.",
                "year": 1897,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Volumes 3-4 combined"
            },
        ]
    },

    # BUDDHIST - Dhammapada
    {
        "catalog": {
            "text_id": "dhammapada",
            "title": "The Dhammapada",
            "author": "Anonymous (Buddhist)",
            "tradition": "indian",
            "origin_raw": "India (Buddhist)",
            "date_composed": "c. 3rd century BCE",
            "material_type": "Wisdom literature",
            "status": "pending",
            "notes": "423 verses - Buddha's Path of Wisdom - core Buddhist scripture",
        },
        "sources": [
            {
                "source_name": "Internet Archive (Bomhard bilingual)",
                "source_url": "https://archive.org/details/dhammapada-english-and-pali",
                "translator": "Allan R. Bomhard",
                "year": 2022,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "English and Pali parallel text"
            },
            {
                "source_name": "Internet Archive (Narada)",
                "source_url": "https://archive.org/details/DhammapadaWithNotes",
                "translator": "Narada Mahathera",
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "With explanatory notes"
            },
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/bud/sbe10/index.htm",
                "translator": "Max Müller",
                "year": 1881,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Sacred Books of the East Vol. 10"
            },
        ]
    },

    # SLAVIC - Songs of the Russian People
    {
        "catalog": {
            "text_id": "songs-russian-people",
            "title": "Songs of the Russian People",
            "author": "W.R.S. Ralston (collector)",
            "tradition": "slavic",
            "origin_raw": "Russia",
            "date_composed": "Ancient oral tradition (collected 1872)",
            "material_type": "Mythology/folklore",
            "status": "pending",
            "notes": "Slavonic mythology and Russian social life - Perun, Veles, domovoy, rusalka",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/neu/srp/index.htm",
                "translator": "W.R.S. Ralston",
                "year": 1872,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Complete text with mythology chapters"
            },
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/songsrussianpeo01ralsgoog",
                "translator": "W.R.S. Ralston",
                "year": 1872,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Original publication"
            },
        ]
    },

    # SLAVIC - Sixty Folk-Tales from Slavonic Sources
    {
        "catalog": {
            "text_id": "sixty-slavonic-folktales",
            "title": "Sixty Folk-Tales from Exclusively Slavonic Sources",
            "author": "A.H. Wratislaw (collector)",
            "tradition": "slavic",
            "origin_raw": "Slavic regions",
            "date_composed": "Ancient oral tradition (collected 1890)",
            "material_type": "Folktales",
            "status": "pending",
            "notes": "Pan-Slavic collection including Earth-Diver creation myth variant",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/neu/sfs/index.htm",
                "translator": "A.H. Wratislaw",
                "year": 1890,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Complete 60 tales"
            },
        ]
    },

    # SLAVIC - Byliny (Russian Hero Tales)
    {
        "catalog": {
            "text_id": "byliny-hero-tales",
            "title": "Byliny Book: Hero Tales of Russia",
            "author": "Marion Chilton Harrison (reteller)",
            "tradition": "slavic",
            "origin_raw": "Russia",
            "date_composed": "Medieval oral tradition (collected 1915)",
            "material_type": "Epic poetry",
            "status": "pending",
            "notes": "Ilya Muromets, Dobrynya Nikitich, Alyosha Popovich - bogatyri cycle",
        },
        "sources": [
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/bylinybookherota00harr",
                "translator": "Marion Chilton Harrison",
                "year": 1915,
                "format": "pdf",
                "quality_tier": "standard",
                "notes": "Seven hero tales retold"
            },
        ]
    },

    # SLAVIC - Folk Tales from the Russian (Baba Yaga)
    {
        "catalog": {
            "text_id": "folk-tales-russian",
            "title": "Folk Tales from the Russian",
            "author": "Various (collectors)",
            "tradition": "slavic",
            "origin_raw": "Russia",
            "date_composed": "Ancient oral tradition",
            "material_type": "Folktales",
            "status": "pending",
            "notes": "Includes Baba Yaga, Vasilisa - classic Russian fairy tales",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/neu/ftr/index.htm",
                "translator": "Various",
                "format": "html",
                "quality_tier": "standard",
                "notes": "Baba Yaga and other tales"
            },
        ]
    },

    # AFRICAN - Myths and Legends of the Bantu (Werner)
    {
        "catalog": {
            "text_id": "myths-legends-bantu",
            "title": "Myths and Legends of the Bantu",
            "author": "Alice Werner",
            "tradition": "african",
            "origin_raw": "Sub-Saharan Africa (Bantu)",
            "date_composed": "Ancient oral tradition (collected 1933)",
            "material_type": "Mythology compilation",
            "status": "pending",
            "notes": "Comprehensive Bantu mythology - creation, tricksters, ancestors",
        },
        "sources": [
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/in.ernet.dli.2015.57033",
                "translator": "Alice Werner",
                "year": 1933,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "409 pages - comprehensive collection"
            },
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/afr/mlb/index.htm",
                "translator": "Alice Werner",
                "year": 1933,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Complete text online"
            },
        ]
    },

    # AFRICAN - Treasury of African Folklore (Courlander)
    {
        "catalog": {
            "text_id": "treasury-african-folklore",
            "title": "A Treasury of African Folklore",
            "author": "Harold Courlander (collector)",
            "tradition": "african",
            "origin_raw": "Pan-African",
            "date_composed": "Ancient oral traditions (collected 1975)",
            "material_type": "Folklore anthology",
            "status": "pending",
            "notes": "Comprehensive - Mwindo epic, Anansi, oral literature across Africa",
        },
        "sources": [
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/treasuryofafrica00cour",
                "translator": "Harold Courlander",
                "year": 1975,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Definitive African folklore anthology"
            },
        ]
    },

    # CELTIC - Lebor Gabála Érenn expansion (if not already covered)
    {
        "catalog": {
            "text_id": "cuchulain-of-muirthemne",
            "title": "Cuchulain of Muirthemne",
            "author": "Lady Augusta Gregory (reteller)",
            "tradition": "celtic",
            "origin_raw": "Ireland",
            "date_composed": "Medieval (retold 1902)",
            "material_type": "Hero cycle",
            "status": "pending",
            "notes": "Ulster Cycle - Cú Chulainn saga, complements Táin Bó Cúailnge",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/neu/celt/cuch/index.htm",
                "translator": "Lady Gregory",
                "year": 1902,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Complete Ulster Cycle retelling"
            },
            {
                "source_name": "Project Gutenberg",
                "source_url": "https://www.gutenberg.org/ebooks/14749",
                "translator": "Lady Gregory",
                "year": 1902,
                "format": "txt",
                "quality_tier": "standard",
                "notes": "Plain text version"
            },
        ]
    },

    # CELTIC - Gods and Fighting Men
    {
        "catalog": {
            "text_id": "gods-fighting-men",
            "title": "Gods and Fighting Men",
            "author": "Lady Augusta Gregory (reteller)",
            "tradition": "celtic",
            "origin_raw": "Ireland",
            "date_composed": "Medieval (retold 1904)",
            "material_type": "Mythology",
            "status": "pending",
            "notes": "Tuatha Dé Danann and Fianna cycles - Irish divine mythology",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/neu/celt/gafm/index.htm",
                "translator": "Lady Gregory",
                "year": 1904,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Tuatha Dé Danann mythology"
            },
            {
                "source_name": "Project Gutenberg",
                "source_url": "https://www.gutenberg.org/ebooks/14465",
                "translator": "Lady Gregory",
                "year": 1904,
                "format": "txt",
                "quality_tier": "standard",
                "notes": "Plain text version"
            },
        ]
    },

    # GREEK - Apollodorus Bibliotheca (mythological handbook)
    {
        "catalog": {
            "text_id": "bibliotheca-apollodorus",
            "title": "The Library (Bibliotheca)",
            "author": "Pseudo-Apollodorus",
            "tradition": "greek",
            "origin_raw": "Ancient Greece",
            "date_composed": "c. 1st-2nd century CE",
            "material_type": "Mythological compendium",
            "status": "pending",
            "notes": "Comprehensive Greek mythology handbook - all major myths systematized",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/cla/apollod/index.htm",
                "translator": "J.G. Frazer",
                "year": 1921,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Loeb Classical Library translation"
            },
        ]
    },

    # ROMAN - Fasti (Ovid's Roman calendar/mythology)
    {
        "catalog": {
            "text_id": "fasti-ovid",
            "title": "Fasti",
            "author": "Ovid",
            "tradition": "roman",
            "origin_raw": "Ancient Rome",
            "date_composed": "c. 8 CE",
            "material_type": "Religious calendar",
            "status": "pending",
            "notes": "Roman festivals and their mythological origins - complements Metamorphoses",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/cla/ovid/lboo/index.htm",
                "translator": "H.T. Riley",
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Complete Fasti"
            },
        ]
    },

    # MESOPOTAMIAN - Descent of Ishtar (Akkadian version)
    {
        "catalog": {
            "text_id": "descent-of-ishtar",
            "title": "The Descent of Ishtar",
            "author": "Anonymous (Akkadian)",
            "tradition": "mesopotamian",
            "origin_raw": "Mesopotamia (Akkadian)",
            "date_composed": "c. 1900-1600 BCE",
            "material_type": "Descent myth",
            "status": "pending",
            "notes": "Akkadian version of Inanna's Descent - death and resurrection theme",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/ane/ishtar.htm",
                "translator": "M. Jastrow",
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Akkadian text translation"
            },
        ]
    },

    # TIBETAN - Bardo Thodol expansion
    {
        "catalog": {
            "text_id": "tibetan-book-of-dead-evans",
            "title": "The Tibetan Book of the Dead (Evans-Wentz)",
            "author": "Padmasambhava (attributed)",
            "tradition": "tibetan",
            "origin_raw": "Tibet",
            "date_composed": "8th century CE (compiled later)",
            "material_type": "Funerary text",
            "status": "pending",
            "notes": "Bardo Thodol - liberation through hearing in the intermediate state",
        },
        "sources": [
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/tibetanbookofthedead",
                "translator": "W.Y. Evans-Wentz & Lama Kazi Dawa-Samdup",
                "year": 1927,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Classic Evans-Wentz translation"
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
    print("ADDING TIER 3 TEXTS - BUDDHIST, SLAVIC, AFRICAN, CLASSICAL EXPANSION")
    print("=" * 70)

    catalog = load_catalog()
    curated = load_curated()

    existing_ids = set(t["text_id"] for t in catalog)

    added = 0
    skipped = 0

    for text in TIER3_TEXTS:
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

    print("\nGaps filled:")
    print("  BUDDHIST: jataka-cowell (complete 6 vols), dhammapada")
    print("  SLAVIC: songs-russian-people, sixty-slavonic-folktales, byliny-hero-tales, folk-tales-russian")
    print("  AFRICAN: myths-legends-bantu, treasury-african-folklore")
    print("  CELTIC: cuchulain-of-muirthemne, gods-fighting-men")
    print("  GREEK: bibliotheca-apollodorus")
    print("  ROMAN: fasti-ovid")
    print("  MESOPOTAMIAN: descent-of-ishtar")
    print("  TIBETAN: tibetan-book-of-dead-evans")


if __name__ == "__main__":
    main()
