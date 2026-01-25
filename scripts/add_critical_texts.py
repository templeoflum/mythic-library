#!/usr/bin/env python3
"""
Add critical missing texts to the Mythic Library catalog.
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

# New texts to add
NEW_TEXTS = [
    # CRITICAL: Inanna's Descent
    {
        "catalog": {
            "text_id": "inannas-descent",
            "title": "Inanna's Descent to the Underworld",
            "author": "Anonymous",
            "tradition": "mesopotamian",
            "origin_raw": "Sumer",
            "date_composed": "c. 1900-1600 BCE",
            "material_type": "Descent myth",
            "status": "pending",
            "notes": "THE archetypal descent narrative",
        },
        "sources": [
            {
                "source_name": "ETCSL (Oxford)",
                "source_url": "https://etcsl.orinst.ox.ac.uk/section1/tr141.htm",
                "translator": "ETCSL composite",
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Composite translation from 50+ cuneiform tablets"
            },
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/InannasDescentToTheNetherworldCentennialSurvey",
                "translator": "Various (survey)",
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Centennial survey of scholarship and translations"
            },
        ]
    },

    # CRITICAL: Ovid's Metamorphoses
    {
        "catalog": {
            "text_id": "metamorphoses",
            "title": "Metamorphoses",
            "author": "Ovid",
            "tradition": "roman",
            "origin_raw": "Rome",
            "date_composed": "8 CE",
            "material_type": "Transformation myths",
            "status": "pending",
            "notes": "Comprehensive catalog of 250+ transformation myths",
        },
        "sources": [
            {
                "source_name": "Project Gutenberg",
                "source_url": "https://www.gutenberg.org/ebooks/21765",
                "translator": "Henry T. Riley",
                "year": 1851,
                "format": "txt",
                "quality_tier": "scholarly",
                "notes": "Books I-VII"
            },
            {
                "source_name": "Project Gutenberg",
                "source_url": "https://www.gutenberg.org/ebooks/26073",
                "translator": "Henry T. Riley",
                "year": 1851,
                "format": "txt",
                "quality_tier": "scholarly",
                "notes": "Books VIII-XV"
            },
            {
                "source_name": "Project Gutenberg",
                "source_url": "https://www.gutenberg.org/ebooks/28621",
                "translator": "J.J. Howard",
                "format": "txt",
                "quality_tier": "standard",
                "notes": "English blank verse translation"
            },
        ]
    },

    # CRITICAL: Homeric Hymns
    {
        "catalog": {
            "text_id": "homeric-hymns",
            "title": "Homeric Hymns",
            "author": "Anonymous (attributed to Homer)",
            "tradition": "greek",
            "origin_raw": "Ancient Greece",
            "date_composed": "7th-6th century BCE",
            "material_type": "Religious hymns",
            "status": "pending",
            "notes": "Major hymns to Demeter, Apollo, Hermes, Aphrodite",
        },
        "sources": [
            {
                "source_name": "Project Gutenberg",
                "source_url": "https://www.gutenberg.org/ebooks/348",
                "translator": "Hugh G. Evelyn-White",
                "year": 1914,
                "format": "txt",
                "quality_tier": "scholarly",
                "notes": "Loeb Classical Library translation (also includes Hesiod)"
            },
            {
                "source_name": "Perseus Digital Library",
                "source_url": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0138",
                "translator": "Hugh G. Evelyn-White",
                "year": 1914,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "With Greek text available"
            },
            {
                "source_name": "Theoi.com",
                "source_url": "https://www.theoi.com/Text/HomericHymns1.html",
                "translator": "Hugh G. Evelyn-White",
                "format": "html",
                "quality_tier": "standard",
                "notes": "Well-formatted with annotations"
            },
        ]
    },

    # HIGH: Aeneid
    {
        "catalog": {
            "text_id": "aeneid",
            "title": "Aeneid",
            "author": "Virgil",
            "tradition": "roman",
            "origin_raw": "Rome",
            "date_composed": "29-19 BCE",
            "material_type": "Epic poetry",
            "status": "pending",
            "notes": "Roman foundation myth, includes katabasis (descent to underworld)",
        },
        "sources": [
            {
                "source_name": "Project Gutenberg",
                "source_url": "https://www.gutenberg.org/ebooks/228",
                "translator": "John Dryden",
                "year": 1697,
                "format": "txt",
                "quality_tier": "scholarly",
                "notes": "Classic verse translation"
            },
            {
                "source_name": "Perseus Digital Library",
                "source_url": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.02.0054",
                "translator": "Theodore C. Williams",
                "year": 1910,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "With Latin text available"
            },
        ]
    },

    # HIGH: Argonautica
    {
        "catalog": {
            "text_id": "argonautica",
            "title": "Argonautica",
            "author": "Apollonius of Rhodes",
            "tradition": "greek",
            "origin_raw": "Hellenistic Egypt",
            "date_composed": "3rd century BCE",
            "material_type": "Epic poetry",
            "status": "pending",
            "notes": "Jason and the Golden Fleece - quest narrative",
        },
        "sources": [
            {
                "source_name": "Project Gutenberg",
                "source_url": "https://www.gutenberg.org/ebooks/830",
                "translator": "R.C. Seaton",
                "year": 1912,
                "format": "txt",
                "quality_tier": "scholarly",
                "notes": "Loeb Classical Library"
            },
            {
                "source_name": "Theoi.com",
                "source_url": "https://www.theoi.com/Text/ApolloniusRhodius1.html",
                "translator": "R.C. Seaton",
                "format": "html",
                "quality_tier": "standard",
                "notes": "Well-formatted"
            },
        ]
    },

    # HIGH: Volsunga Saga
    {
        "catalog": {
            "text_id": "volsunga-saga",
            "title": "Völsunga saga",
            "author": "Anonymous",
            "tradition": "norse",
            "origin_raw": "Iceland",
            "date_composed": "13th century",
            "material_type": "Legendary saga",
            "status": "pending",
            "notes": "Sigurd/Siegfried cycle - source for Wagner's Ring",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/neu/vlsng/",
                "translator": "Eirikr Magnusson & William Morris",
                "year": 1888,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Classic translation"
            },
            {
                "source_name": "Project Gutenberg",
                "source_url": "https://www.gutenberg.org/ebooks/1152",
                "translator": "Eirikr Magnusson & William Morris",
                "format": "txt",
                "quality_tier": "scholarly",
                "notes": "Plain text version"
            },
        ]
    },

    # Descent of Ishtar (Akkadian version)
    {
        "catalog": {
            "text_id": "descent-of-ishtar",
            "title": "Descent of Ishtar",
            "author": "Anonymous",
            "tradition": "mesopotamian",
            "origin_raw": "Akkad/Babylonia",
            "date_composed": "c. 1200 BCE",
            "material_type": "Descent myth",
            "status": "pending",
            "notes": "Akkadian version of Inanna's Descent",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/ane/ishtar.htm",
                "translator": "M. Jastrow",
                "year": 1915,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "From Religion of Babylonia and Assyria"
            },
        ]
    },

    # Orphic Hymns
    {
        "catalog": {
            "text_id": "orphic-hymns",
            "title": "Orphic Hymns",
            "author": "Anonymous (Orphic tradition)",
            "tradition": "greek",
            "origin_raw": "Ancient Greece",
            "date_composed": "2nd-3rd century CE",
            "material_type": "Religious hymns",
            "status": "pending",
            "notes": "Mystery tradition hymns to 87 deities",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/cla/hoo/",
                "translator": "Thomas Taylor",
                "year": 1792,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "First complete English translation"
            },
            {
                "source_name": "Theoi.com",
                "source_url": "https://www.theoi.com/Text/OrphicHymns1.html",
                "translator": "Thomas Taylor",
                "format": "html",
                "quality_tier": "standard",
                "notes": "Well-formatted"
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
    print("Adding critical texts to Mythic Library...")

    catalog = load_catalog()
    curated = load_curated()

    existing_ids = set(t["text_id"] for t in catalog)

    added = 0
    for text in NEW_TEXTS:
        text_id = text["catalog"]["text_id"]

        if text_id in existing_ids:
            print(f"  SKIP: {text_id} (already exists)")
            continue

        # Add to catalog
        catalog.append(text["catalog"])

        # Add to curated sources
        curated["texts"][text_id] = {
            "title": text["catalog"]["title"],
            "sources": text["sources"]
        }

        # Create directory
        tradition = text["catalog"]["tradition"]
        text_dir = create_text_directory(text_id, tradition)

        print(f"  ADDED: {text_id} ({tradition})")
        added += 1

    # Save updates
    save_catalog(catalog)
    save_curated(curated)

    print(f"\nAdded {added} new texts")
    print(f"Total catalog size: {len(catalog)} texts")
    print(f"Total curated sources: {len(curated['texts'])} texts")


if __name__ == "__main__":
    main()
