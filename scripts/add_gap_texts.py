#!/usr/bin/env python3
"""
Add texts to fill remaining regional gaps in the Mythic Library.
Focus on: Australian Aboriginal, Melanesian, Mongol, and additional sources.
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

# New texts to fill gaps
NEW_TEXTS = [
    # AUSTRALIAN ABORIGINAL - Critical gap
    {
        "catalog": {
            "text_id": "australian-legendary-tales",
            "title": "Australian Legendary Tales",
            "author": "K. Langloh Parker",
            "tradition": "australian-aboriginal",
            "origin_raw": "Australia (Noongahburrah)",
            "date_composed": "1896 (oral tradition ancient)",
            "material_type": "Folk tales",
            "status": "pending",
            "notes": "Dreamtime stories from Narran tribe - earliest major collection",
        },
        "sources": [
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/cu31924029909060",
                "translator": "K. Langloh Parker (collector)",
                "year": 1896,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Cornell University copy - no copyright restrictions in US"
            },
            {
                "source_name": "Project Gutenberg",
                "source_url": "https://www.gutenberg.org/ebooks/3833",
                "translator": "K. Langloh Parker (collector)",
                "year": 1896,
                "format": "txt",
                "quality_tier": "scholarly",
                "notes": "Full text version"
            },
        ]
    },
    {
        "catalog": {
            "text_id": "more-australian-legendary-tales",
            "title": "More Australian Legendary Tales",
            "author": "K. Langloh Parker",
            "tradition": "australian-aboriginal",
            "origin_raw": "Australia (Various tribes)",
            "date_composed": "1898 (oral tradition ancient)",
            "material_type": "Folk tales",
            "status": "pending",
            "notes": "Sequel with additional Dreamtime stories",
        },
        "sources": [
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/moreaustralianl00parkgoog",
                "translator": "K. Langloh Parker (collector)",
                "year": 1898,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Harvard University digitized copy"
            },
        ]
    },

    # MELANESIAN - Pacific gap
    {
        "catalog": {
            "text_id": "oceanic-mythology",
            "title": "Oceanic Mythology (Mythology of All Races Vol. IX)",
            "author": "Roland B. Dixon",
            "tradition": "oceanic",
            "origin_raw": "Polynesia/Melanesia/Micronesia/Indonesia",
            "date_composed": "1916",
            "material_type": "Mythology handbook",
            "status": "pending",
            "notes": "Comprehensive survey - covers Melanesia, Polynesia, Micronesia, Indonesia",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/pac/om/index.htm",
                "translator": "Roland B. Dixon",
                "year": 1916,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Full text with Melanesia section (Part II)"
            },
        ]
    },

    # MONGOL - Central Asian gap
    {
        "catalog": {
            "text_id": "secret-history-mongols",
            "title": "The Secret History of the Mongols",
            "author": "Anonymous",
            "tradition": "mongol",
            "origin_raw": "Mongolia",
            "date_composed": "c. 1240 CE",
            "material_type": "Epic chronicle",
            "status": "pending",
            "notes": "Chinggis Khan biography - foundational Mongol text",
        },
        "sources": [
            {
                "source_name": "Internet Archive (Cleaves)",
                "source_url": "https://archive.org/details/Cleaves1982SecretHistoryMongols",
                "translator": "Francis Woodman Cleaves",
                "year": 1982,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Standard scholarly translation - 342 pages"
            },
            {
                "source_name": "Internet Archive (Rachewiltz)",
                "source_url": "https://archive.org/details/the-secret-history-of-the-mongols-a-mongolian-epic-chronicle-of",
                "translator": "Igor de Rachewiltz",
                "year": 2015,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Most recent authoritative translation"
            },
        ]
    },

    # SIBERIAN - Shamanic tradition
    {
        "catalog": {
            "text_id": "siberian-mythology",
            "title": "Siberian Mythology (Mythology of All Races Vol. IV)",
            "author": "Uno Holmberg",
            "tradition": "siberian",
            "origin_raw": "Siberia/Finno-Ugric",
            "date_composed": "1927",
            "material_type": "Mythology handbook",
            "status": "pending",
            "notes": "Covers Finno-Ugric and Siberian shamanic traditions",
        },
        "sources": [
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/finnougric04holmuoft",
                "translator": "Uno Holmberg",
                "year": 1927,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Mythology of All Races series"
            },
        ]
    },

    # BALTIC - Lithuanian mythology
    {
        "catalog": {
            "text_id": "lithuanian-mythology",
            "title": "Lithuanian Folk-Lore",
            "author": "Various",
            "tradition": "baltic",
            "origin_raw": "Lithuania",
            "date_composed": "1930s (oral tradition ancient)",
            "material_type": "Folk tales",
            "status": "pending",
            "notes": "Baltic mythology and folk traditions",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/neu/lith/index.htm",
                "translator": "Various",
                "format": "html",
                "quality_tier": "standard",
                "notes": "Lithuanian folk stories and mythology"
            },
        ]
    },

    # CHINESE - Shan Hai Jing (critical missing)
    {
        "catalog": {
            "text_id": "shan-hai-jing",
            "title": "Shan Hai Jing (Classic of Mountains and Seas)",
            "author": "Anonymous",
            "tradition": "chinese",
            "origin_raw": "China",
            "date_composed": "4th century BCE - 1st century CE",
            "material_type": "Mythical geography",
            "status": "pending",
            "notes": "Mythical creatures, geography, deities - foundational Chinese mythology",
        },
        "sources": [
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/shanhaiching00unse",
                "translator": "Various",
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Classic of Mountains and Seas translations"
            },
        ]
    },

    # EGYPTIAN - Pyramid Texts (deep time)
    {
        "catalog": {
            "text_id": "pyramid-texts",
            "title": "The Pyramid Texts",
            "author": "Anonymous",
            "tradition": "egyptian",
            "origin_raw": "Ancient Egypt",
            "date_composed": "c. 2400-2300 BCE",
            "material_type": "Funerary texts",
            "status": "pending",
            "notes": "Oldest religious texts in world - pharaonic afterlife spells",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/egy/pyt/index.htm",
                "translator": "Samuel A.B. Mercer",
                "year": 1952,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Complete translation of Pyramid Texts"
            },
        ]
    },

    # IRISH - Lebor Gabala
    {
        "catalog": {
            "text_id": "lebor-gabala",
            "title": "Lebor Gabála Érenn (Book of Invasions)",
            "author": "Anonymous",
            "tradition": "celtic",
            "origin_raw": "Ireland",
            "date_composed": "11th century (oral tradition older)",
            "material_type": "Mythic history",
            "status": "pending",
            "notes": "Irish mythological history - Tuatha Dé Danann",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/neu/celt/gafm/index.htm",
                "translator": "Lady Augusta Gregory",
                "year": 1904,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Gods and Fighting Men - covers Lebor Gabála material"
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
    print("ADDING TEXTS TO FILL REGIONAL GAPS")
    print("=" * 70)

    catalog = load_catalog()
    curated = load_curated()

    existing_ids = set(t["text_id"] for t in catalog)

    added = 0
    skipped = 0

    for text in NEW_TEXTS:
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

    # Print coverage improvements
    print("\nNew regional coverage:")
    traditions_added = set(t["catalog"]["tradition"] for t in NEW_TEXTS
                          if t["catalog"]["text_id"] not in existing_ids)
    for t in sorted(traditions_added):
        print(f"  + {t}")


if __name__ == "__main__":
    main()
