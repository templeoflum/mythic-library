#!/usr/bin/env python3
"""
Load curated sources into the discoveries file.

Merges hand-verified source URLs from curated_sources.json into
the main discoveries.json tracking file.
"""

import json
from pathlib import Path

SOURCES_DIR = Path(__file__).parent.parent / "sources"
CURATED_FILE = SOURCES_DIR / "curated_sources.json"
DISCOVERIES_FILE = SOURCES_DIR / "discoveries.json"
MASTER_CATALOG = SOURCES_DIR / "master_catalog.csv"


def load_json(path: Path) -> dict:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    curated = load_json(CURATED_FILE)
    discoveries = load_json(DISCOVERIES_FILE)

    if "texts" not in discoveries:
        discoveries["texts"] = {}

    # Load catalog for metadata
    import csv
    catalog = {}
    with open(MASTER_CATALOG, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            catalog[row["text_id"]] = row

    merged_count = 0
    new_sources = 0

    for text_id, text_data in curated.get("texts", {}).items():
        if text_id not in discoveries["texts"]:
            discoveries["texts"][text_id] = {
                "title": text_data.get("title", catalog.get(text_id, {}).get("title", "")),
                "tradition": catalog.get(text_id, {}).get("tradition", ""),
                "sources": [],
            }

        existing_urls = {s.get("source_url") for s in discoveries["texts"][text_id].get("sources", [])}

        for source in text_data.get("sources", []):
            if source.get("source_url") not in existing_urls:
                source["text_id"] = text_id
                source["curated"] = True
                discoveries["texts"][text_id]["sources"].append(source)
                new_sources += 1

        merged_count += 1

    save_json(DISCOVERIES_FILE, discoveries)

    # Generate report
    print(f"Merged {merged_count} texts with {new_sources} new sources")
    print()

    # Summary by source
    by_source = {}
    total_sources = 0
    for text_data in discoveries["texts"].values():
        for source in text_data.get("sources", []):
            name = source.get("source_name", "Unknown")
            by_source[name] = by_source.get(name, 0) + 1
            total_sources += 1

    print(f"Total texts with sources: {len(discoveries['texts'])}")
    print(f"Total source URLs: {total_sources}")
    print()
    print("By repository:")
    for name, count in sorted(by_source.items(), key=lambda x: -x[1]):
        print(f"  {name}: {count}")

    # Show texts without sources
    import csv
    with open(MASTER_CATALOG, "r", encoding="utf-8") as f:
        all_texts = {row["text_id"]: row["title"] for row in csv.DictReader(f)}

    missing = [
        (tid, title) for tid, title in all_texts.items()
        if tid not in discoveries["texts"] or not discoveries["texts"][tid].get("sources")
    ]

    if missing:
        print()
        print(f"Texts still needing sources ({len(missing)}):")
        for tid, title in missing[:20]:
            print(f"  - {title}")
        if len(missing) > 20:
            print(f"  ... and {len(missing) - 20} more")


if __name__ == "__main__":
    main()
