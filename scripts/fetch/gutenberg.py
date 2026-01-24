#!/usr/bin/env python3
"""
Fetch texts from Project Gutenberg.

Uses the Gutenberg API and direct downloads.
"""

import argparse
import hashlib
import json
import re
from pathlib import Path

import requests

BASE_URL = "https://www.gutenberg.org"
GUTENDEX_URL = "https://gutendex.com/books"


def search_texts(query: str, topic: str = None) -> list[dict]:
    """
    Search Project Gutenberg using Gutendex API.

    Args:
        query: Search query (searches title and author)
        topic: Optional topic/subject filter
    """
    params = {"search": query}
    if topic:
        params["topic"] = topic

    response = requests.get(GUTENDEX_URL, params=params)
    response.raise_for_status()

    return response.json().get("results", [])


def get_book(book_id: int) -> dict:
    """Get full metadata for a book."""
    url = f"{GUTENDEX_URL}/{book_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_download_url(book: dict, format_pref: str = "text/plain") -> str | None:
    """
    Get the best download URL for a book.

    Args:
        book: Book metadata dict
        format_pref: Preferred format MIME type
    """
    formats = book.get("formats", {})

    # Priority order
    format_priority = [
        "text/plain; charset=utf-8",
        "text/plain; charset=us-ascii",
        "text/plain",
        "text/html; charset=utf-8",
        "text/html",
        "application/pdf",
    ]

    for fmt in format_priority:
        if fmt in formats:
            return formats[fmt]

    return None


def download_text(book_id: int, output_dir: Path) -> dict:
    """
    Download a text from Project Gutenberg.

    Returns metadata including checksum.
    """
    book = get_book(book_id)
    url = get_download_url(book)

    if not url:
        raise ValueError(f"No suitable download format for book {book_id}")

    response = requests.get(url)
    response.raise_for_status()

    # Determine filename
    title_slug = re.sub(r"[^\w\s-]", "", book.get("title", "unknown")).strip().lower()
    title_slug = re.sub(r"[-\s]+", "-", title_slug)[:50]

    if "pdf" in url.lower():
        ext = ".pdf"
    elif "html" in url.lower():
        ext = ".html"
    else:
        ext = ".txt"

    filename = f"pg{book_id}_{title_slug}{ext}"
    output_path = output_dir / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    content = response.content
    checksum = hashlib.sha256(content).hexdigest()

    with open(output_path, "wb") as f:
        f.write(content)

    return {
        "book_id": book_id,
        "title": book.get("title"),
        "authors": [a.get("name") for a in book.get("authors", [])],
        "subjects": book.get("subjects", []),
        "languages": book.get("languages", []),
        "filename": filename,
        "output_path": str(output_path),
        "checksum": checksum,
        "source_url": f"{BASE_URL}/ebooks/{book_id}",
        "download_url": url,
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch texts from Project Gutenberg")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for texts")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--topic", help="Filter by topic/subject")

    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Download a text by ID")
    fetch_parser.add_argument("book_id", type=int, help="Gutenberg book ID")
    fetch_parser.add_argument("--output", "-o", type=Path, default=Path("."), help="Output directory")

    args = parser.parse_args()

    if args.command == "search":
        results = search_texts(args.query, args.topic)
        for book in results:
            print(f"ID: {book.get('id')}")
            print(f"  Title: {book.get('title', 'N/A')}")
            authors = ", ".join(a.get("name", "") for a in book.get("authors", []))
            print(f"  Authors: {authors or 'N/A'}")
            print(f"  Languages: {', '.join(book.get('languages', []))}")
            print()

    elif args.command == "fetch":
        result = download_text(args.book_id, args.output)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
