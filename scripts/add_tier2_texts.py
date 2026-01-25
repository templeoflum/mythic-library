#!/usr/bin/env python3
"""
Add Tier 2 priority texts to fill remaining gaps in the Mythic Library.
Focus on: Mesoamerican, Andean, Polynesian expansion, Native American regional.
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

# Tier 2 texts to fill remaining gaps
TIER2_TEXTS = [
    # MESOAMERICAN - Aztec Five Suns (Critical gap)
    {
        "catalog": {
            "text_id": "codex-chimalpopoca",
            "title": "Codex Chimalpopoca (History and Mythology of the Aztecs)",
            "author": "Anonymous (Nahua)",
            "tradition": "mesoamerican",
            "origin_raw": "Mexico (Aztec)",
            "date_composed": "16th century (oral tradition ancient)",
            "material_type": "Mythic chronicle",
            "status": "pending",
            "notes": "Contains Legend of the Suns (Five Suns) and Annals of Cuauhtitlan - Quetzalcoatl premier source",
        },
        "sources": [
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/historymythology0000unse",
                "translator": "John Bierhorst",
                "year": 1992,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "First complete English translation including Legend of the Suns"
            },
        ]
    },

    # SOUTH AMERICAN - Huarochiri Manuscript (Andean bible)
    {
        "catalog": {
            "text_id": "huarochiri-manuscript",
            "title": "The Huarochiri Manuscript",
            "author": "Anonymous (Quechua)",
            "tradition": "south-american",
            "origin_raw": "Peru (Andean)",
            "date_composed": "c. 1598 (oral tradition ancient)",
            "material_type": "Mythology compilation",
            "status": "pending",
            "notes": "Only surviving Andean religious text in indigenous language - Paryaqaqa, Cuniraya, mountain deities",
        },
        "sources": [
            {
                "source_name": "Internet Archive (English)",
                "source_url": "https://archive.org/details/huarochirimanusc0000unse",
                "translator": "Frank Salomon & George Urioste",
                "year": 1991,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "English and Quechua bilingual edition"
            },
            {
                "source_name": "Internet Archive (Spanish/Arguedas)",
                "source_url": "https://archive.org/details/ManuscritoDeHuarochiriJMArguedasCompleto",
                "translator": "José María Arguedas",
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Spanish translation by noted Peruvian author"
            },
        ]
    },

    # POLYNESIAN - Legends of Maui (Trickster/Culture hero)
    {
        "catalog": {
            "text_id": "legends-of-maui",
            "title": "Legends of Maui - A Demi-God of Polynesia",
            "author": "W.D. Westervelt (collector)",
            "tradition": "polynesian",
            "origin_raw": "Hawaii/Polynesia",
            "date_composed": "Ancient oral tradition (collected 1910)",
            "material_type": "Hero myths",
            "status": "pending",
            "notes": "Maui trickster cycle - snaring the sun, fishing up islands, stealing fire",
        },
        "sources": [
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/legendsofmauid00west",
                "translator": "W.D. Westervelt",
                "year": 1910,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Hawaiian Gazette publication - 181 pages"
            },
            {
                "source_name": "Project Gutenberg",
                "source_url": "https://www.gutenberg.org/ebooks/22384",
                "translator": "W.D. Westervelt",
                "year": 1910,
                "format": "txt",
                "quality_tier": "standard",
                "notes": "Plain text version"
            },
        ]
    },

    # POLYNESIAN - Maui of a Thousand Tricks (scholarly study)
    {
        "catalog": {
            "text_id": "maui-thousand-tricks",
            "title": "Maui of a Thousand Tricks",
            "author": "Katharine Luomala",
            "tradition": "polynesian",
            "origin_raw": "Pan-Polynesian",
            "date_composed": "1949 (analysis of ancient traditions)",
            "material_type": "Comparative mythology",
            "status": "pending",
            "notes": "Comprehensive Maui scholarship - oceanic trickster comparative study",
        },
        "sources": [
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/in.ernet.dli.2015.78688",
                "translator": "Katharine Luomala",
                "year": 1949,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Bishop Museum - 306 pages comparative study"
            },
        ]
    },

    # NATIVE AMERICAN - Tlingit (Northwest/Raven trickster)
    {
        "catalog": {
            "text_id": "tlingit-myths-texts",
            "title": "Tlingit Myths and Texts",
            "author": "John R. Swanton (collector)",
            "tradition": "north-american",
            "origin_raw": "Alaska (Tlingit)",
            "date_composed": "Ancient oral tradition (collected 1909)",
            "material_type": "Mythology collection",
            "status": "pending",
            "notes": "Raven trickster cycle - Northwest Coast creation myths",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/nam/nw/tmt/index.htm",
                "translator": "John R. Swanton",
                "year": 1909,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Bureau of American Ethnology Bulletin 39"
            },
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/taboram00teletext",
                "translator": "John R. Swanton",
                "year": 1909,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "BAE Bulletin 39 - original publication"
            },
        ]
    },

    # NATIVE AMERICAN - Navaho Origin Myths
    {
        "catalog": {
            "text_id": "navaho-origin-myths",
            "title": "Origin Myths of the Navaho Indians",
            "author": "Aileen O'Bryan (collector)",
            "tradition": "north-american",
            "origin_raw": "Southwest USA (Navajo)",
            "date_composed": "Ancient oral tradition (collected 1956)",
            "material_type": "Creation mythology",
            "status": "pending",
            "notes": "Navajo emergence myth - journey through four worlds",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/nam/nav/omni/index.htm",
                "translator": "Aileen O'Bryan",
                "year": 1956,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Bureau of American Ethnology Bulletin 163"
            },
        ]
    },

    # NATIVE AMERICAN - Hopi Traditions
    {
        "catalog": {
            "text_id": "traditions-of-hopi",
            "title": "The Traditions of the Hopi",
            "author": "H.R. Voth (collector)",
            "tradition": "north-american",
            "origin_raw": "Southwest USA (Hopi)",
            "date_composed": "Ancient oral tradition (collected 1905)",
            "material_type": "Mythology collection",
            "status": "pending",
            "notes": "100 Hopi folk tales - emergence from underworld, clan wanderings",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/nam/hopi/toth/index.htm",
                "translator": "H.R. Voth",
                "year": 1905,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Field Columbian Museum Publication 96"
            },
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/traditionsofhopi00voth",
                "translator": "H.R. Voth",
                "year": 1905,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Original Field Museum publication"
            },
        ]
    },

    # NATIVE AMERICAN - Seneca Myths (Iroquois)
    {
        "catalog": {
            "text_id": "seneca-myths",
            "title": "Seneca Indian Myths",
            "author": "Jeremiah Curtin (collector)",
            "tradition": "north-american",
            "origin_raw": "Northeast USA (Seneca/Iroquois)",
            "date_composed": "Ancient oral tradition (collected 1923)",
            "material_type": "Mythology collection",
            "status": "pending",
            "notes": "500 pages of Iroquois mythology - extensive collection",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/nam/iro/sim/index.htm",
                "translator": "Jeremiah Curtin",
                "year": 1923,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "E.P. Dutton publication"
            },
        ]
    },

    # NATIVE AMERICAN - Southeastern Myths (Creek, Natchez)
    {
        "catalog": {
            "text_id": "southeastern-myths-tales",
            "title": "Myths and Tales of the Southeastern Indians",
            "author": "John R. Swanton (collector)",
            "tradition": "north-american",
            "origin_raw": "Southeast USA (Creek, Natchez, etc.)",
            "date_composed": "Ancient oral tradition (collected 1929)",
            "material_type": "Mythology collection",
            "status": "pending",
            "notes": "Creek, Hitchiti, Alabama, Kosati, Natchez mythology",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/nam/se/mtsi/index.htm",
                "translator": "John R. Swanton",
                "year": 1929,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Bureau of American Ethnology Bulletin 88"
            },
        ]
    },

    # MAORI - Grey's Polynesian Mythology (foundational)
    {
        "catalog": {
            "text_id": "polynesian-mythology-grey",
            "title": "Polynesian Mythology (Grey)",
            "author": "Sir George Grey (collector)",
            "tradition": "polynesian",
            "origin_raw": "New Zealand (Maori)",
            "date_composed": "Ancient oral tradition (collected 1855)",
            "material_type": "Mythology compilation",
            "status": "pending",
            "notes": "Foundational Maori mythology - Rangi and Papa, Maui, Tawhaki",
        },
        "sources": [
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/polynesianmythol00greyuoft",
                "translator": "Sir George Grey",
                "year": 1855,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Original John Murray publication"
            },
            {
                "source_name": "Internet Archive (DLI)",
                "source_url": "https://archive.org/details/in.ernet.dli.2015.219427",
                "translator": "Sir George Grey",
                "year": 1855,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Digital Library of India scan"
            },
        ]
    },

    # HAWAIIAN - Legends of Gods and Ghosts
    {
        "catalog": {
            "text_id": "hawaiian-legends-gods-ghosts",
            "title": "Legends of Gods and Ghosts (Hawaiian Mythology)",
            "author": "W.D. Westervelt (collector)",
            "tradition": "polynesian",
            "origin_raw": "Hawaii",
            "date_composed": "Ancient oral tradition (collected 1915)",
            "material_type": "Mythology collection",
            "status": "pending",
            "notes": "Hawaiian deities, ghost stories, sacred places",
        },
        "sources": [
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/cu31924029908781",
                "translator": "W.D. Westervelt",
                "year": 1915,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Cornell University Library digitization"
            },
            {
                "source_name": "Project Gutenberg",
                "source_url": "https://www.gutenberg.org/ebooks/게12",
                "translator": "W.D. Westervelt",
                "year": 1915,
                "format": "txt",
                "quality_tier": "standard",
                "notes": "Plain text version"
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
    print("ADDING TIER 2 TEXTS TO FILL REMAINING GAPS")
    print("=" * 70)

    catalog = load_catalog()
    curated = load_curated()

    existing_ids = set(t["text_id"] for t in catalog)

    added = 0
    skipped = 0

    for text in TIER2_TEXTS:
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
    print("\nGaps filled by region/type:")
    print("  MESOAMERICAN: codex-chimalpopoca (Aztec Five Suns, Quetzalcoatl)")
    print("  ANDEAN: huarochiri-manuscript (Quechua 'bible')")
    print("  POLYNESIAN: legends-of-maui, maui-thousand-tricks, polynesian-mythology-grey")
    print("  HAWAIIAN: hawaiian-legends-gods-ghosts")
    print("  NATIVE AMERICAN:")
    print("    - Northwest: tlingit-myths-texts (Raven trickster)")
    print("    - Southwest: navaho-origin-myths, traditions-of-hopi")
    print("    - Northeast: seneca-myths (Iroquois)")
    print("    - Southeast: southeastern-myths-tales (Creek, Natchez)")


if __name__ == "__main__":
    main()
