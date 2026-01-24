#!/usr/bin/env python3
"""
Automated source discovery for mythic texts.

Searches multiple repositories to find available versions of texts in our catalog:
- Internet Archive
- Project Gutenberg
- Sacred Texts
- Perseus Digital Library
- And more

Outputs discovered sources to a JSON file for review and acquisition.
"""

import argparse
import csv
import json
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

import requests

SOURCES_DIR = Path(__file__).parent.parent / "sources"
MASTER_CATALOG = SOURCES_DIR / "master_catalog.csv"
DISCOVERIES_FILE = SOURCES_DIR / "discoveries.json"

# Rate limiting between requests
REQUEST_DELAY = 1.0


@dataclass
class DiscoveredSource:
    """A discovered source for a text."""
    text_id: str
    title: str
    source_name: str
    source_url: str
    format: str  # pdf, txt, html, etc.
    translator: Optional[str] = None
    year: Optional[int] = None
    publisher: Optional[str] = None
    quality_notes: str = ""
    verified: bool = False


def load_catalog() -> list[dict]:
    """Load the master catalog."""
    with open(MASTER_CATALOG, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_discoveries() -> dict:
    """Load existing discoveries."""
    if DISCOVERIES_FILE.exists():
        with open(DISCOVERIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"texts": {}}


def save_discoveries(data: dict):
    """Save discoveries to file."""
    with open(DISCOVERIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# =============================================================================
# Internet Archive Search
# =============================================================================

def search_internet_archive(title: str, author: str = "") -> list[dict]:
    """Search Internet Archive for a text."""
    # Build search query
    query_parts = [f'title:"{title}"']
    if author and author.lower() not in ["anonymous", "various", "unknown", "oral tradition", "multiple authors"]:
        query_parts.append(f'creator:"{author}"')
    query_parts.append("mediatype:texts")

    query = " AND ".join(query_parts)

    params = {
        "q": query,
        "fl[]": ["identifier", "title", "creator", "date", "description", "format"],
        "rows": 20,
        "output": "json",
    }

    try:
        response = requests.get(
            "https://archive.org/advancedsearch.php",
            params=params,
            timeout=30
        )
        response.raise_for_status()
        results = response.json().get("response", {}).get("docs", [])

        sources = []
        for r in results:
            # Try to extract year from date
            year = None
            date_str = r.get("date", "")
            if date_str:
                year_match = re.search(r"\b(1[5-9]\d{2}|20[0-2]\d)\b", str(date_str))
                if year_match:
                    year = int(year_match.group(1))

            sources.append({
                "source_name": "Internet Archive",
                "source_url": f"https://archive.org/details/{r.get('identifier')}",
                "identifier": r.get("identifier"),
                "title": r.get("title"),
                "creator": r.get("creator"),
                "year": year,
                "format": "pdf/txt",
                "description": r.get("description", "")[:200] if r.get("description") else "",
            })

        return sources
    except Exception as e:
        print(f"  Internet Archive error: {e}")
        return []


# =============================================================================
# Project Gutenberg Search
# =============================================================================

def search_gutenberg(title: str, author: str = "") -> list[dict]:
    """Search Project Gutenberg using Gutendex API."""
    params = {"search": title}

    try:
        response = requests.get(
            "https://gutendex.com/books",
            params=params,
            timeout=30
        )
        response.raise_for_status()
        results = response.json().get("results", [])

        sources = []
        for r in results:
            # Check if this matches our search
            r_title = r.get("title", "").lower()
            if title.lower() not in r_title and r_title not in title.lower():
                # Try partial match
                title_words = set(title.lower().split())
                r_title_words = set(r_title.split())
                if len(title_words & r_title_words) < 2:
                    continue

            authors = [a.get("name", "") for a in r.get("authors", [])]

            # Determine best format available
            formats = r.get("formats", {})
            best_format = "txt"
            if any("pdf" in k.lower() for k in formats):
                best_format = "pdf"
            elif any("html" in k.lower() for k in formats):
                best_format = "html"

            sources.append({
                "source_name": "Project Gutenberg",
                "source_url": f"https://www.gutenberg.org/ebooks/{r.get('id')}",
                "identifier": str(r.get("id")),
                "title": r.get("title"),
                "creator": ", ".join(authors) if authors else None,
                "year": None,  # Gutenberg doesn't provide publication year
                "format": best_format,
                "languages": r.get("languages", []),
            })

        return sources
    except Exception as e:
        print(f"  Project Gutenberg error: {e}")
        return []


# =============================================================================
# Sacred Texts Search
# =============================================================================

# Known texts available on sacred-texts.com
SACRED_TEXTS_CATALOG = {
    "epic-of-gilgamesh": {
        "url": "https://sacred-texts.com/ane/gilgamesh/",
        "title": "The Epic of Gilgamesh",
        "translator": "Various (public domain translations)",
        "format": "html",
    },
    "rigveda": {
        "url": "https://sacred-texts.com/hin/rigveda/",
        "title": "Rig Veda",
        "translator": "Ralph T.H. Griffith",
        "format": "html",
    },
    "book-of-the-dead": {
        "url": "https://sacred-texts.com/egy/ebod/",
        "title": "The Egyptian Book of the Dead",
        "translator": "E.A. Wallis Budge",
        "format": "html",
    },
    "poetic-edda": {
        "url": "https://sacred-texts.com/neu/poe/",
        "title": "The Poetic Edda",
        "translator": "Henry Adams Bellows",
        "format": "html",
    },
    "prose-edda": {
        "url": "https://sacred-texts.com/neu/pre/",
        "title": "The Prose Edda",
        "translator": "Arthur Gilchrist Brodeur",
        "format": "html",
    },
    "beowulf": {
        "url": "https://sacred-texts.com/neu/beo/",
        "title": "Beowulf",
        "translator": "Francis B. Gummere",
        "format": "html",
    },
    "the-mabinogion": {
        "url": "https://sacred-texts.com/neu/celt/mab/",
        "title": "The Mabinogion",
        "translator": "Lady Charlotte Guest",
        "format": "html",
    },
    "kalevala": {
        "url": "https://sacred-texts.com/neu/kveng/",
        "title": "The Kalevala",
        "translator": "John Martin Crawford",
        "format": "html",
    },
    "popol-vuh": {
        "url": "https://sacred-texts.com/nam/pvuheng.htm",
        "title": "Popol Vuh",
        "translator": "Lewis Spence",
        "format": "html",
    },
    "theogony": {
        "url": "https://sacred-texts.com/cla/hesiod/theogony.htm",
        "title": "Theogony",
        "translator": "Hugh G. Evelyn-White",
        "format": "html",
    },
    "aesops-fables": {
        "url": "https://sacred-texts.com/cla/aesop/",
        "title": "Aesop's Fables",
        "translator": "George Fyler Townsend",
        "format": "html",
    },
    "one-thousand-and-one-nights": {
        "url": "https://sacred-texts.com/neu/burt1k1/",
        "title": "The Book of the Thousand Nights and a Night",
        "translator": "Richard F. Burton",
        "format": "html",
    },
    "shāhnāmeh": {
        "url": "https://sacred-texts.com/neu/shahnama.txt",
        "title": "The Shah Namah (selections)",
        "translator": "Helen Zimmern",
        "format": "txt",
    },
    "kojiki": {
        "url": "https://sacred-texts.com/shi/kj/",
        "title": "The Kojiki",
        "translator": "Basil Hall Chamberlain",
        "format": "html",
    },
    "the-pilgrims-progress": {
        "url": "https://sacred-texts.com/chr/bunyan/",
        "title": "The Pilgrim's Progress",
        "translator": "N/A (original English)",
        "format": "html",
    },
    "the-conference-of-the-birds": {
        "url": "https://sacred-texts.com/isl/bp/",
        "title": "Bird Parliament",
        "translator": "Edward FitzGerald",
        "format": "html",
    },
}


def search_sacred_texts(text_id: str) -> list[dict]:
    """Check if text is available on sacred-texts.com."""
    if text_id in SACRED_TEXTS_CATALOG:
        entry = SACRED_TEXTS_CATALOG[text_id]
        return [{
            "source_name": "Sacred Texts",
            "source_url": entry["url"],
            "title": entry["title"],
            "creator": entry.get("translator"),
            "format": entry["format"],
            "quality_notes": "Public domain translation, HTML format",
        }]
    return []


# =============================================================================
# Perseus Digital Library (for Greek/Latin texts)
# =============================================================================

PERSEUS_CATALOG = {
    "the-iliad": {
        "url": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0134",
        "original_url": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0133",
        "title": "Iliad",
        "translator": "Samuel Butler",
        "has_original": True,
    },
    "the-odyssey": {
        "url": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0136",
        "original_url": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0135",
        "title": "Odyssey",
        "translator": "Samuel Butler",
        "has_original": True,
    },
    "theogony": {
        "url": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0130",
        "original_url": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0129",
        "title": "Theogony",
        "translator": "Hugh G. Evelyn-White",
        "has_original": True,
    },
}


def search_perseus(text_id: str) -> list[dict]:
    """Check if text is available on Perseus Digital Library."""
    sources = []
    if text_id in PERSEUS_CATALOG:
        entry = PERSEUS_CATALOG[text_id]
        sources.append({
            "source_name": "Perseus Digital Library",
            "source_url": entry["url"],
            "title": entry["title"],
            "creator": entry["translator"],
            "format": "html",
            "quality_notes": "Scholarly translation with original Greek available",
        })
        if entry.get("has_original"):
            sources.append({
                "source_name": "Perseus Digital Library (Original Greek)",
                "source_url": entry["original_url"],
                "title": f"{entry['title']} (Greek)",
                "format": "html",
                "quality_notes": "Original Greek text",
            })
    return sources


# =============================================================================
# Main Discovery Functions
# =============================================================================

def discover_sources_for_text(text: dict, existing: list = None) -> list[dict]:
    """
    Discover all available sources for a single text.

    Returns list of discovered sources.
    """
    text_id = text["text_id"]
    title = text["title"]
    author = text.get("author", "")

    print(f"Searching for: {title}")

    all_sources = []
    existing_urls = {s.get("source_url") for s in (existing or [])}

    # Search each repository
    # 1. Sacred Texts (curated catalog)
    for source in search_sacred_texts(text_id):
        if source["source_url"] not in existing_urls:
            source["text_id"] = text_id
            all_sources.append(source)
    time.sleep(REQUEST_DELAY / 2)

    # 2. Perseus (curated catalog for Greek/Latin)
    for source in search_perseus(text_id):
        if source["source_url"] not in existing_urls:
            source["text_id"] = text_id
            all_sources.append(source)
    time.sleep(REQUEST_DELAY / 2)

    # 3. Internet Archive (search)
    for source in search_internet_archive(title, author):
        if source["source_url"] not in existing_urls:
            source["text_id"] = text_id
            all_sources.append(source)
    time.sleep(REQUEST_DELAY)

    # 4. Project Gutenberg (search)
    for source in search_gutenberg(title, author):
        if source["source_url"] not in existing_urls:
            source["text_id"] = text_id
            all_sources.append(source)
    time.sleep(REQUEST_DELAY)

    print(f"  Found {len(all_sources)} new sources")
    return all_sources


def discover_all(limit: int = None, tradition: str = None):
    """
    Run discovery for all texts in catalog.

    Args:
        limit: Maximum number of texts to process
        tradition: Filter by tradition
    """
    catalog = load_catalog()
    discoveries = load_discoveries()

    if tradition:
        catalog = [t for t in catalog if t.get("tradition", "").lower() == tradition.lower()]

    if limit:
        catalog = catalog[:limit]

    print(f"Running discovery for {len(catalog)} texts...")
    print("=" * 60)

    total_found = 0
    for text in catalog:
        text_id = text["text_id"]
        existing = discoveries["texts"].get(text_id, {}).get("sources", [])

        sources = discover_sources_for_text(text, existing)

        if sources:
            if text_id not in discoveries["texts"]:
                discoveries["texts"][text_id] = {
                    "title": text["title"],
                    "tradition": text.get("tradition"),
                    "sources": [],
                }
            discoveries["texts"][text_id]["sources"].extend(sources)
            total_found += len(sources)

        # Save after each text in case of interruption
        save_discoveries(discoveries)

    print("=" * 60)
    print(f"Discovery complete. Found {total_found} total sources.")
    print(f"Results saved to: {DISCOVERIES_FILE}")


def report_discoveries():
    """Generate a summary report of discoveries."""
    discoveries = load_discoveries()

    total_texts = len(discoveries.get("texts", {}))
    total_sources = sum(
        len(t.get("sources", []))
        for t in discoveries.get("texts", {}).values()
    )

    by_source = {}
    for text_data in discoveries.get("texts", {}).values():
        for source in text_data.get("sources", []):
            name = source.get("source_name", "Unknown")
            by_source[name] = by_source.get(name, 0) + 1

    print(f"Total texts with sources: {total_texts}")
    print(f"Total sources found: {total_sources}")
    print("\nBy repository:")
    for name, count in sorted(by_source.items(), key=lambda x: -x[1]):
        print(f"  {name}: {count}")


def main():
    parser = argparse.ArgumentParser(description="Discover sources for mythic texts")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Discover command
    discover_parser = subparsers.add_parser("run", help="Run discovery")
    discover_parser.add_argument("--limit", type=int, help="Max texts to process")
    discover_parser.add_argument("--tradition", help="Filter by tradition")

    # Single text discovery
    single_parser = subparsers.add_parser("single", help="Discover for single text")
    single_parser.add_argument("text_id", help="Text ID to discover")

    # Report command
    subparsers.add_parser("report", help="Show discovery report")

    args = parser.parse_args()

    if args.command == "run":
        discover_all(args.limit, args.tradition)
    elif args.command == "single":
        catalog = load_catalog()
        text = next((t for t in catalog if t["text_id"] == args.text_id), None)
        if text:
            sources = discover_sources_for_text(text)
            discoveries = load_discoveries()
            if args.text_id not in discoveries["texts"]:
                discoveries["texts"][args.text_id] = {
                    "title": text["title"],
                    "tradition": text.get("tradition"),
                    "sources": [],
                }
            discoveries["texts"][args.text_id]["sources"].extend(sources)
            save_discoveries(discoveries)
            print(json.dumps(sources, indent=2, ensure_ascii=False))
        else:
            print(f"Text '{args.text_id}' not found in catalog")
    elif args.command == "report":
        report_discoveries()


if __name__ == "__main__":
    main()
