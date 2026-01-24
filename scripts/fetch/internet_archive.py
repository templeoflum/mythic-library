#!/usr/bin/env python3
"""
Fetch texts from Internet Archive.

Uses the Internet Archive API to search and download public domain texts.
https://archive.org/developers/
"""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import quote_plus

import requests

BASE_URL = "https://archive.org"
SEARCH_URL = f"{BASE_URL}/advancedsearch.php"
METADATA_URL = f"{BASE_URL}/metadata"
DOWNLOAD_URL = f"{BASE_URL}/download"

# Rate limiting
REQUEST_DELAY = 1.0  # seconds between requests


def search_texts(query: str, mediatype: str = "texts", rows: int = 50) -> list[dict]:
    """
    Search Internet Archive for texts.

    Args:
        query: Search query
        mediatype: Type of media (default: texts)
        rows: Max results to return

    Returns:
        List of result dictionaries
    """
    params = {
        "q": f"{query} AND mediatype:{mediatype}",
        "fl[]": ["identifier", "title", "creator", "date", "description", "subject"],
        "rows": rows,
        "output": "json",
    }

    response = requests.get(SEARCH_URL, params=params)
    response.raise_for_status()

    data = response.json()
    return data.get("response", {}).get("docs", [])


def get_metadata(identifier: str) -> dict:
    """Get full metadata for an item."""
    url = f"{METADATA_URL}/{identifier}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def list_files(identifier: str, formats: list[str] = None) -> list[dict]:
    """
    List available files for an item.

    Args:
        identifier: Internet Archive identifier
        formats: Optional list of formats to filter (e.g., ["PDF", "Text"])
    """
    metadata = get_metadata(identifier)
    files = metadata.get("files", [])

    if formats:
        formats_lower = [f.lower() for f in formats]
        files = [f for f in files if f.get("format", "").lower() in formats_lower]

    return files


def download_file(identifier: str, filename: str, output_dir: Path) -> tuple[Path, str]:
    """
    Download a file from Internet Archive.

    Returns:
        Tuple of (output_path, sha256_checksum)
    """
    url = f"{DOWNLOAD_URL}/{identifier}/{quote_plus(filename)}"
    output_path = output_dir / filename

    response = requests.get(url, stream=True)
    response.raise_for_status()

    hasher = hashlib.sha256()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            hasher.update(chunk)

    return output_path, hasher.hexdigest()


def fetch_text(identifier: str, output_dir: Path, prefer_pdf: bool = True) -> dict:
    """
    Fetch a text by identifier.

    Returns metadata about the download including checksum.
    """
    metadata = get_metadata(identifier)
    files = metadata.get("files", [])

    # Prefer PDF, then plain text
    formats_priority = ["PDF", "Text"] if prefer_pdf else ["Text", "PDF"]

    target_file = None
    for fmt in formats_priority:
        for f in files:
            if f.get("format", "").upper() == fmt.upper():
                target_file = f
                break
        if target_file:
            break

    if not target_file:
        raise ValueError(f"No suitable file found for {identifier}")

    filename = target_file["name"]
    output_path, checksum = download_file(identifier, filename, output_dir)

    return {
        "identifier": identifier,
        "title": metadata.get("metadata", {}).get("title", "Unknown"),
        "creator": metadata.get("metadata", {}).get("creator", "Unknown"),
        "date": metadata.get("metadata", {}).get("date", "Unknown"),
        "filename": filename,
        "format": target_file.get("format"),
        "size": target_file.get("size"),
        "output_path": str(output_path),
        "checksum": checksum,
        "source_url": f"{BASE_URL}/details/{identifier}",
        "download_url": f"{DOWNLOAD_URL}/{identifier}/{filename}",
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch texts from Internet Archive")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for texts")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--rows", type=int, default=20, help="Max results")

    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Download a text by identifier")
    fetch_parser.add_argument("identifier", help="Internet Archive identifier")
    fetch_parser.add_argument("--output", "-o", type=Path, default=Path("."), help="Output directory")
    fetch_parser.add_argument("--text", action="store_true", help="Prefer text format over PDF")

    # List command
    list_parser = subparsers.add_parser("list", help="List files for an item")
    list_parser.add_argument("identifier", help="Internet Archive identifier")

    args = parser.parse_args()

    if args.command == "search":
        results = search_texts(args.query, rows=args.rows)
        for r in results:
            print(f"ID: {r.get('identifier')}")
            print(f"  Title: {r.get('title', 'N/A')}")
            print(f"  Creator: {r.get('creator', 'N/A')}")
            print(f"  Date: {r.get('date', 'N/A')}")
            print()

    elif args.command == "fetch":
        result = fetch_text(args.identifier, args.output, prefer_pdf=not args.text)
        print(json.dumps(result, indent=2))

    elif args.command == "list":
        files = list_files(args.identifier)
        for f in files:
            print(f"{f.get('name')} ({f.get('format')}, {f.get('size')} bytes)")


if __name__ == "__main__":
    main()
