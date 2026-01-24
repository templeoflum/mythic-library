#!/usr/bin/env python3
"""
Catalog management for the Mythic Library.

Provides tools to:
- Import texts from CSV/spreadsheet
- Add new texts to the catalog
- Update translation records
- Generate reports
"""

import argparse
import csv
import json
from pathlib import Path
from datetime import datetime

SOURCES_DIR = Path(__file__).parent.parent / "sources"
MASTER_CATALOG = SOURCES_DIR / "master_catalog.csv"
TRANSLATIONS_CSV = SOURCES_DIR / "translations.csv"
SOURCES_JSON = SOURCES_DIR / "sources.json"


def load_master_catalog() -> list[dict]:
    """Load the master catalog CSV."""
    if not MASTER_CATALOG.exists():
        return []

    with open(MASTER_CATALOG, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def save_master_catalog(records: list[dict]):
    """Save records to master catalog CSV."""
    if not records:
        return

    fieldnames = ["text_id", "title", "author", "tradition", "origin_raw",
                  "date_composed", "material_type", "status", "notes"]

    with open(MASTER_CATALOG, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


# Map origin strings to our tradition categories
TRADITION_MAPPINGS = {
    # Mesopotamian
    "mesopotamia": "mesopotamian",
    "babylonia": "mesopotamian",
    "sumeria": "mesopotamian",
    "akkadia": "mesopotamian",
    "assyria": "mesopotamian",
    # Canaanite/Levantine
    "canaanite": "levantine",
    "ugarit": "levantine",
    "ancient israel": "hebrew",
    # Egyptian
    "ancient egypt": "egyptian",
    "egypt": "egyptian",
    # Greek
    "ancient greece": "greek",
    "greece": "greek",
    # Roman/Latin
    "rome": "roman",
    "roman": "roman",
    "italy": "roman",
    # Norse/Germanic
    "iceland": "norse",
    "scandinavia": "norse",
    "anglo-saxon": "norse",
    "germany": "germanic",
    # Celtic
    "wales": "celtic",
    "ireland": "celtic",
    "scotland": "celtic",
    # Indian
    "india": "indian",
    "south asia": "indian",
    # Persian
    "persia": "persian",
    "iran": "persian",
    # Chinese
    "china": "chinese",
    # Japanese
    "japan": "japanese",
    # Turkic/Central Asian
    "oghuz turkic": "turkic",
    "kyrgyz": "turkic",
    "tibet": "tibetan",
    "central asia": "central-asian",
    # Mesoamerican
    "maya": "mesoamerican",
    "guatemala": "mesoamerican",
    "mesoamerica": "mesoamerican",
    "andes": "andean",
    # African
    "mali": "african",
    "west africa": "african",
    "ghana": "african",
    "nigeria": "african",
    "south africa": "african",
    "xhosa": "african",
    "zanzibar": "african",
    "swahili": "african",
    "sub-saharan africa": "african",
    "caribbean": "african",
    # North American
    "north america": "north-american",
    "cherokee nation": "north-american",
    # Pacific/Oceanian
    "philippines": "southeast-asian",
    "malaysia": "southeast-asian",
    "laos": "southeast-asian",
    "thailand": "southeast-asian",
    "hawaii": "polynesian",
    "new zealand": "polynesian",
    "māori": "polynesian",
    "polynesian": "polynesian",
    "greenland": "arctic",
    "inuit": "arctic",
    # European
    "england": "european",
    "france": "european",
    "uk": "european",
    "russian empire": "european",
    "finland": "european",
    "karelia": "european",
    # Middle Eastern
    "middle east": "middle-eastern",
    # Christian/Gnostic
    "early christian": "gnostic",
    # Global/Compilations
    "global sources": "anthology",
    "united states": "anthology",
}


def normalize_tradition(origin: str) -> str:
    """Map an origin string to a normalized tradition category."""
    if not origin:
        return "other"

    origin_lower = origin.lower()

    # Check for exact matches first
    for key, value in TRADITION_MAPPINGS.items():
        if key in origin_lower:
            return value

    return "other"


def import_from_csv(csv_path: Path) -> list[dict]:
    """
    Import texts from an external CSV file.

    Expects columns that can be mapped to our schema.
    """
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Try to map common column names
    column_mappings = {
        "text_id": ["id", "text_id", "identifier", "slug"],
        "title": ["title", "name", "text_name", "work"],
        "author": ["author", "compiler/author", "compiler", "writer", "attributed"],
        "origin": ["origin", "tradition", "culture", "region"],
        "date_composed": ["date", "date_composed", "period", "era", "year", "date/period"],
        "material_type": ["material/type", "type", "material", "genre", "form"],
        "notes": ["notes", "description", "comments"],
    }

    def find_column(row: dict, target: str) -> str | None:
        """Find the value for a target column using mappings."""
        possible_names = column_mappings.get(target, [target])
        for name in possible_names:
            # Case-insensitive matching
            for key in row.keys():
                if key.lower() == name.lower():
                    return row[key]
        return None

    imported = []
    for row in rows:
        origin_raw = find_column(row, "origin") or ""
        record = {
            "text_id": find_column(row, "text_id") or "",
            "title": find_column(row, "title") or "",
            "author": find_column(row, "author") or "",
            "tradition": normalize_tradition(origin_raw),
            "origin_raw": origin_raw,
            "date_composed": find_column(row, "date_composed") or "",
            "material_type": find_column(row, "material_type") or "",
            "status": "pending",
            "notes": find_column(row, "notes") or "",
        }

        # Generate text_id from title if not provided
        if not record["text_id"] and record["title"]:
            import re
            slug = re.sub(r"[^\w\s-]", "", record["title"].lower())
            slug = re.sub(r"[-\s]+", "-", slug).strip("-")
            record["text_id"] = slug[:50]

        if record["title"]:  # Only import if we have at least a title
            imported.append(record)

    return imported


def add_text(text_id: str, title: str, tradition: str, author: str = "",
             origin: str = "", date: str = "", material_type: str = "", notes: str = ""):
    """Add a single text to the catalog."""
    records = load_master_catalog()

    # Check for duplicates
    if any(r["text_id"] == text_id for r in records):
        print(f"Text with ID '{text_id}' already exists")
        return False

    records.append({
        "text_id": text_id,
        "title": title,
        "author": author,
        "tradition": tradition,
        "origin_raw": origin,
        "date_composed": date,
        "material_type": material_type,
        "status": "pending",
        "notes": notes,
    })

    save_master_catalog(records)
    return True


def list_texts(tradition: str = None, status: str = None):
    """List texts in the catalog with optional filtering."""
    records = load_master_catalog()

    if tradition:
        records = [r for r in records if r.get("tradition", "").lower() == tradition.lower()]
    if status:
        records = [r for r in records if r.get("status", "").lower() == status.lower()]

    return records


def update_status(text_id: str, status: str):
    """Update the status of a text."""
    records = load_master_catalog()

    for r in records:
        if r["text_id"] == text_id:
            r["status"] = status
            save_master_catalog(records)
            return True

    return False


def generate_report() -> dict:
    """Generate a summary report of the catalog."""
    records = load_master_catalog()

    by_tradition = {}
    by_status = {}

    for r in records:
        trad = r.get("tradition", "unknown")
        stat = r.get("status", "unknown")

        by_tradition[trad] = by_tradition.get(trad, 0) + 1
        by_status[stat] = by_status.get(stat, 0) + 1

    return {
        "total_texts": len(records),
        "by_tradition": by_tradition,
        "by_status": by_status,
        "generated": datetime.now().isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description="Manage the Mythic Library catalog")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Import command
    import_parser = subparsers.add_parser("import", help="Import from CSV")
    import_parser.add_argument("csv_file", type=Path, help="CSV file to import")
    import_parser.add_argument("--merge", action="store_true", help="Merge with existing catalog")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a text")
    add_parser.add_argument("--id", required=True, help="Text ID")
    add_parser.add_argument("--title", required=True, help="Title")
    add_parser.add_argument("--tradition", required=True, help="Tradition category")
    add_parser.add_argument("--author", default="", help="Author/compiler")
    add_parser.add_argument("--origin", default="", help="Original origin description")
    add_parser.add_argument("--date", default="", help="Date composed")
    add_parser.add_argument("--type", default="", help="Material type")
    add_parser.add_argument("--notes", default="", help="Notes")

    # List command
    list_parser = subparsers.add_parser("list", help="List texts")
    list_parser.add_argument("--tradition", help="Filter by tradition")
    list_parser.add_argument("--status", help="Filter by status")

    # Status command
    status_parser = subparsers.add_parser("status", help="Update text status")
    status_parser.add_argument("text_id", help="Text ID")
    status_parser.add_argument("new_status", help="New status")

    # Report command
    subparsers.add_parser("report", help="Generate summary report")

    args = parser.parse_args()

    if args.command == "import":
        imported = import_from_csv(args.csv_file)

        if args.merge:
            existing = load_master_catalog()
            existing_ids = {r["text_id"] for r in existing}
            new_records = [r for r in imported if r["text_id"] not in existing_ids]
            existing.extend(new_records)
            save_master_catalog(existing)
            print(f"Merged {len(new_records)} new records (skipped {len(imported) - len(new_records)} duplicates)")
        else:
            save_master_catalog(imported)
            print(f"Imported {len(imported)} records")

    elif args.command == "add":
        if add_text(args.id, args.title, args.tradition, args.author,
                   args.origin, args.date, args.type, args.notes):
            print(f"Added: {args.title}")
        else:
            print("Failed to add text")

    elif args.command == "list":
        records = list_texts(args.tradition, args.status)
        for r in records:
            print(f"{r['text_id']}: {r['title']} ({r['tradition']}) [{r.get('status', 'pending')}]")
        print(f"\nTotal: {len(records)}")

    elif args.command == "status":
        if update_status(args.text_id, args.new_status):
            print(f"Updated {args.text_id} to {args.new_status}")
        else:
            print(f"Text '{args.text_id}' not found")

    elif args.command == "report":
        report = generate_report()
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
