#!/usr/bin/env python3
"""
Generate download guides for each text in the catalog.
Creates a SOURCES.md file in each text's directory with download instructions.
"""

import csv
import json
from pathlib import Path

SOURCES_DIR = Path(__file__).parent.parent / "sources"
TEXTS_DIR = Path(__file__).parent.parent / "texts"
MASTER_CATALOG = SOURCES_DIR / "master_catalog.csv"
DISCOVERIES_FILE = SOURCES_DIR / "discoveries.json"


def load_catalog() -> list[dict]:
    with open(MASTER_CATALOG, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_discoveries() -> dict:
    with open(DISCOVERIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_guide(text: dict, sources: list[dict]) -> str:
    """Generate markdown guide for a text."""
    lines = [
        f"# {text['title']} - Source Guide",
        "",
        "## Overview",
        f"- **Origin**: {text.get('origin_raw', 'Unknown')}",
        f"- **Date**: {text.get('date_composed', 'Unknown')}",
        f"- **Type**: {text.get('material_type', 'Unknown')}",
        f"- **Author/Compiler**: {text.get('author', 'Unknown')}",
        "",
        "## Available Sources",
        "",
    ]

    for i, src in enumerate(sources, 1):
        tier = src.get("quality_tier", "standard").upper()
        translator = src.get("translator") or src.get("creator") or "Unknown"
        year = src.get("year", "")
        year_str = f" ({year})" if year else ""

        lines.extend([
            f"### {i}. {translator}{year_str} - {tier}",
            f"**URL**: {src['source_url']}",
            f"- **Source**: {src['source_name']}",
            f"- **Format**: {src.get('format', 'unknown').upper()}",
        ])

        if src.get("notes"):
            lines.append(f"- **Notes**: {src['notes']}")

        lines.append("")

    # Add instructions
    text_id = text["text_id"]
    lines.extend([
        "## Download Instructions",
        "",
        "1. Visit each URL above",
        "2. Download the text (PDF, TXT, or save HTML as text)",
        "3. Save to this directory with descriptive filename",
        "4. Run verification:",
        f"   ```",
        f"   python scripts/acquire.py fetch {text_id}",
        f"   ```",
        "",
        "## File Naming Convention",
        f"- `{text_id}-[translator]-[year].[ext]`",
        "",
    ])

    return "\n".join(lines)


def main():
    catalog = load_catalog()
    discoveries = load_discoveries()

    generated = 0
    skipped = 0

    for text in catalog:
        text_id = text["text_id"]
        tradition = text["tradition"]

        # Skip if no sources
        if text_id not in discoveries.get("texts", {}):
            skipped += 1
            continue

        sources = discoveries["texts"][text_id].get("sources", [])
        if not sources:
            skipped += 1
            continue

        # Create directory
        text_dir = TEXTS_DIR / tradition / text_id
        text_dir.mkdir(parents=True, exist_ok=True)

        # Check if guide already exists and is customized
        guide_path = text_dir / "SOURCES.md"
        if guide_path.exists():
            content = guide_path.read_text()
            if "## Verification Checklist" in content:
                # This is a customized guide, don't overwrite
                print(f"Skipping {text_id} (customized guide exists)")
                continue

        # Generate guide
        guide_content = generate_guide(text, sources)
        guide_path.write_text(guide_content)
        print(f"Generated: {text_dir.relative_to(TEXTS_DIR.parent)}/SOURCES.md")
        generated += 1

    print(f"\nGenerated {generated} guides, skipped {skipped}")


if __name__ == "__main__":
    main()
