#!/usr/bin/env python3
"""
Add regional texts to fill coverage gaps: South American, Korean, and Slavic.
"""

import sys
import io
import csv
import json
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SOURCES_DIR = Path(__file__).parent.parent / "sources"
TEXTS_DIR = Path(__file__).parent.parent / "texts"
MASTER_CATALOG = SOURCES_DIR / "master_catalog.csv"
CURATED_SOURCES = SOURCES_DIR / "curated_sources.json"

# New texts to add for regional coverage gaps
NEW_TEXTS = [
    # SOUTH AMERICAN - Inca/Andean
    {
        "catalog": {
            "text_id": "apu-ollantay",
            "title": "Apu Ollantay",
            "author": "Anonymous",
            "tradition": "south-american",
            "origin_raw": "Inca Peru",
            "date_composed": "Pre-Columbian (written 18th c.)",
            "material_type": "Drama",
            "status": "pending",
            "notes": "Only known Native American dramatic composition - Inca love story",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/nam/inca/oll/index.htm",
                "translator": "Clements R. Markham",
                "year": 1871,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Full English translation of Inca drama"
            },
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/stream/apuollantay09068gut/apuol10.txt",
                "translator": "Clements R. Markham",
                "format": "txt",
                "quality_tier": "scholarly",
                "notes": "Plain text version"
            },
        ]
    },

    # SOUTH AMERICAN - Guarani
    {
        "catalog": {
            "text_id": "guarani-creation-myths",
            "title": "Guarani Creation Myths",
            "author": "Oral tradition",
            "tradition": "south-american",
            "origin_raw": "Paraguay/Argentina (Guarani)",
            "date_composed": "Pre-Columbian (collected 19th-20th c.)",
            "material_type": "Creation mythology",
            "status": "pending",
            "notes": "Tupã, Ñande Ramõi creation narratives - key South American cosmogony",
        },
        "sources": [
            {
                "source_name": "Universidad Nacional de Misiones",
                "source_url": "https://www.native-languages.org/guarani-legends.htm",
                "translator": "Various",
                "format": "html",
                "quality_tier": "standard",
                "notes": "Collection of Guarani legends and creation stories"
            },
        ]
    },

    # Pre-Columbian America comprehensive
    {
        "catalog": {
            "text_id": "pre-columbian-myths",
            "title": "Pre-Columbian America: Myths and Legends",
            "author": "Donald A. Mackenzie",
            "tradition": "anthology",
            "origin_raw": "Mesoamerica & South America",
            "date_composed": "1923",
            "material_type": "Mythology handbook",
            "status": "pending",
            "notes": "Comprehensive coverage of Aztec, Maya, Inca mythologies",
        },
        "sources": [
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/precolumbianamer0000mack",
                "translator": "N/A (original English)",
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "329 pages covering all major pre-Columbian traditions"
            },
        ]
    },

    # KOREAN - Foundation myth
    {
        "catalog": {
            "text_id": "samguk-yusa",
            "title": "Samguk Yusa (Memorabilia of the Three Kingdoms)",
            "author": "Il-yeon",
            "tradition": "korean",
            "origin_raw": "Korea (Goryeo)",
            "date_composed": "c. 1280 CE",
            "material_type": "Mythic chronicle",
            "status": "pending",
            "notes": "Earliest record of Dangun legend - Korean foundation myth",
        },
        "sources": [
            {
                "source_name": "Terebess Asia Online",
                "source_url": "https://terebess.hu/zen/mesterek/samguk-yusa.pdf",
                "translator": "Tae-Hung Ha & Grafton K. Mintz",
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Yonsei University Press translation"
            },
            {
                "source_name": "HSE Russia",
                "source_url": "https://www.hse.ru/data/2012/04/01/1265173068/SAMGUK%20YUSA_selected.pdf",
                "translator": "Various",
                "format": "pdf",
                "quality_tier": "standard",
                "notes": "Selected portions"
            },
        ]
    },

    # SLAVIC - Russian folk tales (expand existing)
    {
        "catalog": {
            "text_id": "byliny-russian-epics",
            "title": "Byliny (Russian Epic Songs)",
            "author": "Oral tradition",
            "tradition": "slavic",
            "origin_raw": "Russia",
            "date_composed": "11th-19th century (collected)",
            "material_type": "Epic poetry",
            "status": "pending",
            "notes": "Heroic epics of Ilya Muromets, Dobrynya Nikitich, Alyosha Popovich",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/neu/rus/index.htm",
                "translator": "Various",
                "format": "html",
                "quality_tier": "standard",
                "notes": "Russian mythology and folklore collection"
            },
        ]
    },

    # Lewis Spence - North American myths (fills gap)
    {
        "catalog": {
            "text_id": "myths-north-american-indians",
            "title": "The Myths of the North American Indians",
            "author": "Lewis Spence",
            "tradition": "north-american",
            "origin_raw": "North America (various tribes)",
            "date_composed": "1914",
            "material_type": "Mythology handbook",
            "status": "pending",
            "notes": "Comprehensive survey of North American indigenous myths",
        },
        "sources": [
            {
                "source_name": "Project Gutenberg",
                "source_url": "https://www.gutenberg.org/ebooks/42390",
                "translator": "N/A (original English)",
                "format": "txt",
                "quality_tier": "scholarly",
                "notes": "Full text with illustrations"
            },
        ]
    },

    # Popol Vuh - additional translations (we have it but add Gutenberg source)
    # Note: Already in catalog, just adding source

    # Introduction to Mythology - Lewis Spence (comparative)
    {
        "catalog": {
            "text_id": "introduction-to-mythology",
            "title": "An Introduction to Mythology",
            "author": "Lewis Spence",
            "tradition": "anthology",
            "origin_raw": "Global survey",
            "date_composed": "1921",
            "material_type": "Mythology handbook",
            "status": "pending",
            "notes": "Theoretical framework for comparative mythology study",
        },
        "sources": [
            {
                "source_name": "Project Gutenberg",
                "source_url": "https://www.gutenberg.org/ebooks/45048",
                "translator": "N/A (original English)",
                "format": "txt",
                "quality_tier": "scholarly",
                "notes": "Methodology and classification of myths"
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

    # Create SOURCES.md placeholder
    sources_md = text_dir / "SOURCES.md"
    if not sources_md.exists():
        sources_md.write_text(f"# {text_id} - Source Guide\n\n(To be generated)\n")

    return text_dir


def main():
    print("Adding regional texts to fill coverage gaps...")
    print("=" * 60)

    catalog = load_catalog()
    curated = load_curated()

    existing_ids = set(t["text_id"] for t in catalog)

    added = 0
    skipped = 0

    for text in NEW_TEXTS:
        text_id = text["catalog"]["text_id"]
        tradition = text["catalog"]["tradition"]

        if text_id in existing_ids:
            print(f"  SKIP: {text_id} (already exists)")
            skipped += 1
            continue

        # Add to catalog
        catalog.append(text["catalog"])

        # Add to curated sources
        curated["texts"][text_id] = {
            "title": text["catalog"]["title"],
            "sources": text["sources"]
        }

        # Create directory
        text_dir = create_text_directory(text_id, tradition)

        print(f"  ADDED: {text_id}")
        print(f"         Tradition: {tradition}")
        print(f"         Sources: {len(text['sources'])}")
        added += 1

    # Save updates
    save_catalog(catalog)
    save_curated(curated)

    print("=" * 60)
    print(f"Added {added} new texts, skipped {skipped}")
    print(f"Total catalog size: {len(catalog)} texts")
    print(f"Total curated sources: {len(curated['texts'])} texts")

    # Print coverage summary
    print("\nNew coverage added:")
    print("  - South American: Apu Ollantay (Inca), Guarani creation myths")
    print("  - Korean: Samguk Yusa (Dangun foundation myth)")
    print("  - Slavic: Byliny (Russian heroic epics)")
    print("  - North American: Lewis Spence comprehensive survey")
    print("  - Comparative: Introduction to Mythology framework")


if __name__ == "__main__":
    main()
