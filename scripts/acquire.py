#!/usr/bin/env python3
"""
Acquire and verify texts one at a time.

Usage:
    python scripts/acquire.py next          # Show next text to process
    python scripts/acquire.py fetch <id>    # Fetch a specific text
    python scripts/acquire.py verify <id>   # Verify a fetched text
    python scripts/acquire.py status        # Show acquisition progress
"""

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime

SOURCES_DIR = Path(__file__).parent.parent / "sources"
TEXTS_DIR = Path(__file__).parent.parent / "texts"
MASTER_CATALOG = SOURCES_DIR / "master_catalog.csv"
DISCOVERIES_FILE = SOURCES_DIR / "discoveries.json"
ACQUISITIONS_FILE = SOURCES_DIR / "acquisitions.json"


def load_catalog() -> list[dict]:
    with open(MASTER_CATALOG, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_discoveries() -> dict:
    if DISCOVERIES_FILE.exists():
        with open(DISCOVERIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"texts": {}}


def load_acquisitions() -> dict:
    if ACQUISITIONS_FILE.exists():
        with open(ACQUISITIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"texts": {}}


def save_acquisitions(data: dict):
    with open(ACQUISITIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_text_dir(text_id: str, tradition: str) -> Path:
    """Get the directory for storing a text's files."""
    return TEXTS_DIR / tradition / text_id


def show_next():
    """Show the next text that needs processing."""
    catalog = load_catalog()
    discoveries = load_discoveries()
    acquisitions = load_acquisitions()

    for text in catalog:
        text_id = text["text_id"]

        # Skip if already acquired
        if text_id in acquisitions.get("texts", {}):
            acq = acquisitions["texts"][text_id]
            if acq.get("status") == "complete":
                continue

        # Check if we have sources
        if text_id not in discoveries.get("texts", {}):
            continue

        sources = discoveries["texts"][text_id].get("sources", [])
        if not sources:
            continue

        # This is the next one to process
        print(f"\n{'='*60}")
        print(f"NEXT TEXT: {text['title']}")
        print(f"{'='*60}")
        print(f"ID: {text_id}")
        print(f"Tradition: {text['tradition']}")
        print(f"Author: {text.get('author', 'Unknown')}")
        print(f"Date: {text.get('date_composed', 'Unknown')}")
        print(f"Type: {text.get('material_type', 'Unknown')}")
        print()
        print("Available sources:")
        for i, src in enumerate(sources, 1):
            tier = src.get("quality_tier", "unknown")
            translator = src.get("translator") or src.get("creator") or "N/A"
            print(f"  [{i}] {src['source_name']} ({tier})")
            print(f"      Translator: {translator}")
            print(f"      Format: {src.get('format', 'unknown')}")
            print(f"      URL: {src['source_url']}")
            if src.get("notes"):
                print(f"      Notes: {src['notes']}")
            print()

        print(f"To fetch: python scripts/acquire.py fetch {text_id}")
        return

    print("All texts have been processed!")


def show_text_info(text_id: str):
    """Show detailed info about a specific text."""
    catalog = load_catalog()
    discoveries = load_discoveries()
    acquisitions = load_acquisitions()

    text = next((t for t in catalog if t["text_id"] == text_id), None)
    if not text:
        print(f"Text '{text_id}' not found in catalog")
        return

    print(f"\n{'='*60}")
    print(f"{text['title']}")
    print(f"{'='*60}")
    print(f"ID: {text_id}")
    print(f"Tradition: {text['tradition']}")
    print(f"Origin: {text.get('origin_raw', 'Unknown')}")
    print(f"Author: {text.get('author', 'Unknown')}")
    print(f"Date: {text.get('date_composed', 'Unknown')}")
    print(f"Type: {text.get('material_type', 'Unknown')}")

    # Acquisition status
    if text_id in acquisitions.get("texts", {}):
        acq = acquisitions["texts"][text_id]
        print(f"\nAcquisition Status: {acq.get('status', 'unknown')}")
        if acq.get("files"):
            print("Downloaded files:")
            for f in acq["files"]:
                print(f"  - {f['path']} ({f.get('source_name', 'unknown')})")
    else:
        print(f"\nAcquisition Status: not started")

    # Available sources
    if text_id in discoveries.get("texts", {}):
        sources = discoveries["texts"][text_id].get("sources", [])
        print(f"\nAvailable sources ({len(sources)}):")
        for i, src in enumerate(sources, 1):
            tier = src.get("quality_tier", "unknown")
            print(f"  [{i}] {src['source_name']} - {src.get('translator', 'N/A')} ({tier})")
            print(f"      {src['source_url']}")
    else:
        print("\nNo sources discovered yet")


def record_manual_acquisition(text_id: str, source_index: int = None, notes: str = ""):
    """Record that a text was manually acquired (downloaded by user)."""
    catalog = load_catalog()
    discoveries = load_discoveries()
    acquisitions = load_acquisitions()

    text = next((t for t in catalog if t["text_id"] == text_id), None)
    if not text:
        print(f"Text '{text_id}' not found")
        return

    tradition = text["tradition"]
    text_dir = get_text_dir(text_id, tradition)

    # Check what files exist in the directory
    if not text_dir.exists():
        text_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {text_dir}")
        print("Please download files to this directory, then run this command again.")
        return

    files = list(text_dir.glob("*"))
    files = [f for f in files if f.is_file() and f.name != ".gitkeep"]

    if not files:
        print(f"No files found in {text_dir}")
        print("Please download files to this directory first.")

        # Show sources
        if text_id in discoveries.get("texts", {}):
            sources = discoveries["texts"][text_id].get("sources", [])
            print("\nAvailable sources:")
            for src in sources:
                print(f"  - {src['source_url']}")
        return

    # Record the acquisition
    file_records = []
    for f in files:
        # Compute checksum
        with open(f, "rb") as fp:
            checksum = hashlib.sha256(fp.read()).hexdigest()

        file_records.append({
            "path": str(f.relative_to(TEXTS_DIR.parent)),
            "filename": f.name,
            "size": f.stat().st_size,
            "checksum": checksum,
            "source_name": "manual",
        })
        print(f"Recorded: {f.name} ({f.stat().st_size} bytes)")

    if "texts" not in acquisitions:
        acquisitions["texts"] = {}

    acquisitions["texts"][text_id] = {
        "title": text["title"],
        "tradition": tradition,
        "status": "complete",
        "acquired_date": datetime.now().isoformat(),
        "files": file_records,
        "notes": notes,
    }

    save_acquisitions(acquisitions)
    print(f"\nRecorded acquisition of {text['title']}")


def show_status():
    """Show overall acquisition status."""
    catalog = load_catalog()
    discoveries = load_discoveries()
    acquisitions = load_acquisitions()

    total = len(catalog)
    with_sources = sum(1 for t in catalog if t["text_id"] in discoveries.get("texts", {}))
    acquired = sum(1 for t in catalog if t["text_id"] in acquisitions.get("texts", {})
                   and acquisitions["texts"][t["text_id"]].get("status") == "complete")

    print(f"\n{'='*60}")
    print("ACQUISITION STATUS")
    print(f"{'='*60}")
    print(f"Total texts in catalog: {total}")
    print(f"Texts with sources:     {with_sources}")
    print(f"Texts acquired:         {acquired}")
    print(f"Remaining:              {with_sources - acquired}")
    print()

    # By tradition
    by_tradition = {}
    for text in catalog:
        trad = text["tradition"]
        if trad not in by_tradition:
            by_tradition[trad] = {"total": 0, "acquired": 0}
        by_tradition[trad]["total"] += 1
        if text["text_id"] in acquisitions.get("texts", {}):
            if acquisitions["texts"][text["text_id"]].get("status") == "complete":
                by_tradition[trad]["acquired"] += 1

    print("By tradition:")
    for trad, counts in sorted(by_tradition.items()):
        pct = (counts["acquired"] / counts["total"] * 100) if counts["total"] > 0 else 0
        bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
        print(f"  {trad:20} {bar} {counts['acquired']}/{counts['total']}")


def main():
    parser = argparse.ArgumentParser(description="Acquire mythic texts")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Next command
    subparsers.add_parser("next", help="Show next text to process")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show text info")
    info_parser.add_argument("text_id", help="Text ID")

    # Fetch command (records manual acquisition)
    fetch_parser = subparsers.add_parser("fetch", help="Record text acquisition")
    fetch_parser.add_argument("text_id", help="Text ID")
    fetch_parser.add_argument("--source", type=int, help="Source index to use")
    fetch_parser.add_argument("--notes", default="", help="Acquisition notes")

    # Status command
    subparsers.add_parser("status", help="Show acquisition progress")

    args = parser.parse_args()

    if args.command == "next":
        show_next()
    elif args.command == "info":
        show_text_info(args.text_id)
    elif args.command == "fetch":
        record_manual_acquisition(args.text_id,
                                  getattr(args, 'source', None),
                                  getattr(args, 'notes', ''))
    elif args.command == "status":
        show_status()


if __name__ == "__main__":
    main()
