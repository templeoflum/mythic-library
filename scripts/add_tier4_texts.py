#!/usr/bin/env python3
"""
Add Tier 4 texts to fill remaining gaps in the Mythic Library.
Focus on: Chinese classics, Japanese expansion, Oceanic, Central Asian.
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

# Tier 4 texts
TIER4_TEXTS = [
    # CHINESE - Tao Te Ching
    {
        "catalog": {
            "text_id": "tao-te-ching",
            "title": "Tao Te Ching",
            "author": "Lao Tzu",
            "tradition": "chinese",
            "origin_raw": "China",
            "date_composed": "c. 6th-4th century BCE",
            "material_type": "Philosophical scripture",
            "status": "pending",
            "notes": "81 verses - foundational Taoist text on the Way and its Power",
        },
        "sources": [
            {
                "source_name": "Sacred Texts (Legge)",
                "source_url": "https://sacred-texts.com/tao/taote.htm",
                "translator": "James Legge",
                "year": 1891,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Sacred Books of the East translation"
            },
            {
                "source_name": "Sacred Texts (Goddard)",
                "source_url": "https://sacred-texts.com/tao/ltw2/index.htm",
                "translator": "Dwight Goddard & Bhikshu Wai-Tao",
                "year": 1935,
                "format": "html",
                "quality_tier": "standard",
                "notes": "Buddhist Bible version"
            },
            {
                "source_name": "Project Gutenberg",
                "source_url": "https://www.gutenberg.org/ebooks/216",
                "translator": "James Legge",
                "format": "txt",
                "quality_tier": "scholarly",
                "notes": "Plain text version"
            },
        ]
    },

    # CHINESE - I Ching
    {
        "catalog": {
            "text_id": "i-ching",
            "title": "I Ching (Book of Changes)",
            "author": "Anonymous (attributed to Fu Xi, King Wen, Duke of Zhou)",
            "tradition": "chinese",
            "origin_raw": "China",
            "date_composed": "c. 9th century BCE (compiled)",
            "material_type": "Divination/philosophy",
            "status": "pending",
            "notes": "64 hexagrams - ancient Chinese divination and wisdom text",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/ich/index.htm",
                "translator": "James Legge",
                "year": 1882,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Sacred Books of the East Vol. 16"
            },
            {
                "source_name": "Project Gutenberg",
                "source_url": "https://www.gutenberg.org/ebooks/339",
                "translator": "James Legge",
                "format": "txt",
                "quality_tier": "scholarly",
                "notes": "Plain text version"
            },
        ]
    },

    # CHINESE - Chuang Tzu
    {
        "catalog": {
            "text_id": "chuang-tzu",
            "title": "Chuang Tzu (Zhuangzi)",
            "author": "Zhuang Zhou",
            "tradition": "chinese",
            "origin_raw": "China",
            "date_composed": "c. 4th century BCE",
            "material_type": "Philosophical text",
            "status": "pending",
            "notes": "Inner chapters - Taoist parables and philosophy, butterfly dream",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/tao/sbe39/index.htm",
                "translator": "James Legge",
                "year": 1891,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Sacred Books of the East Vol. 39"
            },
        ]
    },

    # JAPANESE - Tale of Genji
    {
        "catalog": {
            "text_id": "tale-of-genji",
            "title": "The Tale of Genji",
            "author": "Murasaki Shikibu",
            "tradition": "japanese",
            "origin_raw": "Japan",
            "date_composed": "c. 1000-1012 CE",
            "material_type": "Novel/court literature",
            "status": "pending",
            "notes": "World's first novel - Heian court life and aesthetics",
        },
        "sources": [
            {
                "source_name": "Internet Archive (Waley)",
                "source_url": "https://archive.org/details/taleofgenji00mura",
                "translator": "Arthur Waley",
                "year": 1935,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Classic Waley translation"
            },
            {
                "source_name": "Internet Archive (Suematsu)",
                "source_url": "https://archive.org/details/genji_monogatari_2008_librivox",
                "translator": "Suematsu Kencho",
                "format": "audio",
                "quality_tier": "standard",
                "notes": "LibriVox audiobook - first 17 chapters"
            },
        ]
    },

    # JAPANESE - Tale of the Heike
    {
        "catalog": {
            "text_id": "tale-of-heike",
            "title": "The Tale of the Heike (Heike Monogatari)",
            "author": "Anonymous",
            "tradition": "japanese",
            "origin_raw": "Japan",
            "date_composed": "c. 1240 CE",
            "material_type": "Epic/war tale",
            "status": "pending",
            "notes": "Genpei War - Taira vs Minamoto clans, Buddhist impermanence theme",
        },
        "sources": [
            {
                "source_name": "Internet Archive (Sadler)",
                "source_url": "https://archive.org/details/TheHeikeMonogatari",
                "translator": "A.L. Sadler",
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Complete translation"
            },
            {
                "source_name": "Internet Archive (Kitagawa/Tsuchida)",
                "source_url": "https://archive.org/details/taleofheikeh01toky",
                "translator": "Hiroshi Kitagawa & Bruce T. Tsuchida",
                "year": 1975,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "University of Tokyo Press - 2 volumes"
            },
        ]
    },

    # OCEANIC - The Melanesians (Codrington)
    {
        "catalog": {
            "text_id": "melanesians-codrington",
            "title": "The Melanesians: Studies in Their Anthropology and Folk-lore",
            "author": "R.H. Codrington",
            "tradition": "oceanic",
            "origin_raw": "Melanesia",
            "date_composed": "1891 (ancient oral traditions)",
            "material_type": "Ethnography/mythology",
            "status": "pending",
            "notes": "Classic study of Melanesian mana, spirits, mythology",
        },
        "sources": [
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/melanesiansstudi00codruoft",
                "translator": "R.H. Codrington",
                "year": 1891,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Original 1891 publication"
            },
        ]
    },

    # OCEANIC - Oceanic Mythology (Dixon)
    {
        "catalog": {
            "text_id": "oceanic-mythology-dixon",
            "title": "Oceanic Mythology",
            "author": "Roland B. Dixon",
            "tradition": "oceanic",
            "origin_raw": "Oceania (Pan-Pacific)",
            "date_composed": "1916 (comparative study)",
            "material_type": "Comparative mythology",
            "status": "pending",
            "notes": "Mythology of All Races Vol. 9 - comprehensive Oceanic coverage",
        },
        "sources": [
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/oceanicmytholog02dixogoog",
                "translator": "Roland B. Dixon",
                "year": 1916,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Mythology of All Races series"
            },
        ]
    },

    # TURKIC - Book of Dede Korkut
    {
        "catalog": {
            "text_id": "dede-korkut",
            "title": "The Book of Dede Korkut",
            "author": "Anonymous (Oghuz Turkic)",
            "tradition": "turkic",
            "origin_raw": "Central Asia/Anatolia",
            "date_composed": "c. 9th-15th century CE",
            "material_type": "Epic tales",
            "status": "pending",
            "notes": "12 stories of Oghuz heroes - foundational Turkic epic",
        },
        "sources": [
            {
                "source_name": "Internet Archive (Lewis)",
                "source_url": "https://archive.org/details/bookofdedekorkut00lewi",
                "translator": "Geoffrey Lewis",
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Penguin Classics translation"
            },
        ]
    },

    # MICRONESIAN - Pacific Island Legends
    {
        "catalog": {
            "text_id": "pacific-island-legends",
            "title": "Pacific Island Legends",
            "author": "Bo Flood (collector)",
            "tradition": "oceanic",
            "origin_raw": "Pacific Islands",
            "date_composed": "Ancient oral traditions",
            "material_type": "Mythology collection",
            "status": "pending",
            "notes": "Tales from Micronesia, Melanesia, Polynesia, Australia",
        },
        "sources": [
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/pacificislandleg00bofl",
                "translator": "Bo Flood et al.",
                "format": "pdf",
                "quality_tier": "standard",
                "notes": "Comprehensive Pacific collection"
            },
        ]
    },

    # CONFUCIAN - Analects
    {
        "catalog": {
            "text_id": "analects-confucius",
            "title": "The Analects of Confucius",
            "author": "Confucius (disciples compiled)",
            "tradition": "chinese",
            "origin_raw": "China",
            "date_composed": "c. 5th century BCE",
            "material_type": "Philosophical sayings",
            "status": "pending",
            "notes": "Core Confucian text - ethics, governance, self-cultivation",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/cfu/conf1.htm",
                "translator": "James Legge",
                "year": 1893,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Chinese Classics translation"
            },
            {
                "source_name": "Project Gutenberg",
                "source_url": "https://www.gutenberg.org/ebooks/4094",
                "translator": "James Legge",
                "format": "txt",
                "quality_tier": "scholarly",
                "notes": "Plain text version"
            },
        ]
    },

    # HINDU - Upanishads
    {
        "catalog": {
            "text_id": "upanishads",
            "title": "The Upanishads",
            "author": "Various sages",
            "tradition": "indian",
            "origin_raw": "India",
            "date_composed": "c. 800-200 BCE",
            "material_type": "Philosophical scripture",
            "status": "pending",
            "notes": "Principal Upanishads - Brahman, Atman, moksha philosophy",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/hin/sbe01/index.htm",
                "translator": "Max Müller",
                "year": 1879,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Sacred Books of the East Vol. 1 (Chandogya, Talavakara, etc.)"
            },
            {
                "source_name": "Sacred Texts (Vol 15)",
                "source_url": "https://sacred-texts.com/hin/sbe15/index.htm",
                "translator": "Max Müller",
                "year": 1884,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Sacred Books of the East Vol. 15 (more Upanishads)"
            },
        ]
    },

    # HINDU - Bhagavad Gita
    {
        "catalog": {
            "text_id": "bhagavad-gita",
            "title": "Bhagavad Gita",
            "author": "Vyasa (attributed)",
            "tradition": "indian",
            "origin_raw": "India",
            "date_composed": "c. 2nd century BCE - 2nd century CE",
            "material_type": "Philosophical scripture",
            "status": "pending",
            "notes": "18 chapters - Krishna's discourse on dharma, yoga, devotion",
        },
        "sources": [
            {
                "source_name": "Sacred Texts",
                "source_url": "https://sacred-texts.com/hin/sbe08/index.htm",
                "translator": "Kâshinâth Trimbak Telang",
                "year": 1882,
                "format": "html",
                "quality_tier": "scholarly",
                "notes": "Sacred Books of the East Vol. 8"
            },
            {
                "source_name": "Project Gutenberg",
                "source_url": "https://www.gutenberg.org/ebooks/2388",
                "translator": "Edwin Arnold",
                "format": "txt",
                "quality_tier": "standard",
                "notes": "Song Celestial poetic version"
            },
        ]
    },

    # EGYPTIAN - Coffin Texts
    {
        "catalog": {
            "text_id": "coffin-texts",
            "title": "The Egyptian Coffin Texts",
            "author": "Anonymous (Ancient Egyptian)",
            "tradition": "egyptian",
            "origin_raw": "Ancient Egypt",
            "date_composed": "c. 2134-1650 BCE (Middle Kingdom)",
            "material_type": "Funerary texts",
            "status": "pending",
            "notes": "Bridge between Pyramid Texts and Book of Dead - spells for afterlife",
        },
        "sources": [
            {
                "source_name": "Internet Archive",
                "source_url": "https://archive.org/details/egyptiancoffinte0001faulrich",
                "translator": "R.O. Faulkner",
                "year": 1973,
                "format": "pdf",
                "quality_tier": "scholarly",
                "notes": "Definitive Faulkner translation"
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
    print("ADDING TIER 4 TEXTS - CHINESE, JAPANESE, OCEANIC, INDIAN EXPANSION")
    print("=" * 70)

    catalog = load_catalog()
    curated = load_curated()

    existing_ids = set(t["text_id"] for t in catalog)

    added = 0
    skipped = 0

    for text in TIER4_TEXTS:
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
    print("  CHINESE: tao-te-ching, i-ching, chuang-tzu, analects-confucius")
    print("  JAPANESE: tale-of-genji, tale-of-heike")
    print("  OCEANIC: melanesians-codrington, oceanic-mythology-dixon, pacific-island-legends")
    print("  TURKIC: dede-korkut")
    print("  INDIAN: upanishads, bhagavad-gita")
    print("  EGYPTIAN: coffin-texts")


if __name__ == "__main__":
    main()
