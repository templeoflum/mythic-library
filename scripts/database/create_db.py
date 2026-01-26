#!/usr/bin/env python3
"""
Pattern Database Creator for Mythic Library Phase 3.

Creates the SQLite database schema, imports all extracted data from
sub-phases 3.1-3.4, and builds the full-text search index.

Usage:
    python scripts/database/create_db.py          # Create and populate
    python scripts/database/create_db.py --reset   # Drop and recreate

Output: data/mythic_patterns.db
"""

import argparse
import csv
import io
import json
import os
import sqlite3
import sys

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
TEXTS_DIR = PROJECT_ROOT / "texts"
DATA_DIR = PROJECT_ROOT / "data"
SOURCES_DIR = PROJECT_ROOT / "sources"
DB_PATH = DATA_DIR / "mythic_patterns.db"

# ============================================================
# Schema
# ============================================================

SCHEMA = """
-- Core text metadata
CREATE TABLE IF NOT EXISTS texts (
    text_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    tradition TEXT NOT NULL,
    author TEXT,
    translator TEXT,
    date_composed TEXT,
    material_type TEXT,
    word_count INTEGER DEFAULT 0,
    best_file TEXT,
    usable BOOLEAN DEFAULT 1
);

-- Text segments
CREATE TABLE IF NOT EXISTS segments (
    segment_id TEXT PRIMARY KEY,      -- format: {text_id}:{seg_id}
    text_id TEXT NOT NULL REFERENCES texts(text_id),
    label TEXT,
    segment_type TEXT,
    ordinal INTEGER,
    word_count INTEGER DEFAULT 0,
    content TEXT
);

-- Named entities (canonical)
CREATE TABLE IF NOT EXISTS entities (
    entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_name TEXT NOT NULL UNIQUE,
    entity_type TEXT,
    primary_tradition TEXT,
    total_mentions INTEGER DEFAULT 0,
    text_count INTEGER DEFAULT 0,
    tradition_count INTEGER DEFAULT 0
);

-- Entity aliases
CREATE TABLE IF NOT EXISTS entity_aliases (
    alias_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER REFERENCES entities(entity_id),
    alias_name TEXT NOT NULL,
    source_tradition TEXT
);

-- Entity mentions in segments
CREATE TABLE IF NOT EXISTS entity_mentions (
    mention_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER REFERENCES entities(entity_id),
    segment_id TEXT REFERENCES segments(segment_id),
    mention_text TEXT,
    sentence_context TEXT,
    char_offset INTEGER
);

-- Thompson Motif Index reference
CREATE TABLE IF NOT EXISTS motifs (
    motif_code TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    parent_code TEXT,
    category TEXT,
    keywords TEXT    -- JSON array
);

-- Motif tags on segments
CREATE TABLE IF NOT EXISTS motif_tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    motif_code TEXT REFERENCES motifs(motif_code),
    segment_id TEXT REFERENCES segments(segment_id),
    confidence REAL,
    evidence TEXT,   -- JSON array of matched keywords
    method TEXT DEFAULT 'keyword_match'
);

-- Cross-cultural patterns
CREATE TABLE IF NOT EXISTS patterns (
    pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT NOT NULL UNIQUE,
    description TEXT,
    motif_codes TEXT,     -- JSON array of related Thompson codes
    attestation_count INTEGER DEFAULT 0,
    tradition_count INTEGER DEFAULT 0,
    confidence REAL DEFAULT 0.0
);

-- Pattern attestations
CREATE TABLE IF NOT EXISTS pattern_attestations (
    attestation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id INTEGER REFERENCES patterns(pattern_id),
    text_id TEXT REFERENCES texts(text_id),
    tradition TEXT,
    evidence_summary TEXT,
    confidence REAL DEFAULT 0.0
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_segments_text ON segments(text_id);
CREATE INDEX IF NOT EXISTS idx_entity_mentions_segment ON entity_mentions(segment_id);
CREATE INDEX IF NOT EXISTS idx_entity_mentions_entity ON entity_mentions(entity_id);
CREATE INDEX IF NOT EXISTS idx_motif_tags_segment ON motif_tags(segment_id);
CREATE INDEX IF NOT EXISTS idx_motif_tags_motif ON motif_tags(motif_code);
CREATE INDEX IF NOT EXISTS idx_pattern_attestations_pattern ON pattern_attestations(pattern_id);
CREATE INDEX IF NOT EXISTS idx_pattern_attestations_text ON pattern_attestations(text_id);
"""

FTS_SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS segments_fts USING fts5(
    segment_id,
    text_id,
    label,
    content
);
"""


def create_database(reset: bool = False):
    """Create the database schema."""
    if reset and DB_PATH.exists():
        os.remove(DB_PATH)
        print("Removed existing database.")

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    # Create tables
    for statement in SCHEMA.split(';'):
        statement = statement.strip()
        if statement:
            conn.execute(statement)

    # Create FTS table
    conn.execute(FTS_SCHEMA)
    conn.commit()
    print("Schema created.")
    return conn


def import_texts(conn: sqlite3.Connection):
    """Import text metadata from master catalog and best versions."""
    catalog_path = SOURCES_DIR / "master_catalog.csv"
    best_path = SOURCES_DIR / "best_versions.json"

    # Load catalog
    catalog = {}
    with open(catalog_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            catalog[row["text_id"]] = row

    # Load best versions
    best = {}
    if best_path.exists():
        with open(best_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            best = data.get("best_versions", {})

    count = 0
    for text_id, row in catalog.items():
        best_info = best.get(text_id, {})
        word_count = best_info.get("word_count", 0)
        best_file = best_info.get("best_file", "")
        usable = 1 if best_info.get("status") == "selected" else 0

        conn.execute(
            """INSERT OR REPLACE INTO texts
               (text_id, title, tradition, author, date_composed,
                material_type, word_count, best_file, usable)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (text_id, row.get("title", text_id), row.get("tradition", ""),
             row.get("author", ""), row.get("date_composed", ""),
             row.get("material_type", ""), word_count, best_file, usable)
        )
        count += 1

    conn.commit()
    print(f"Imported {count} texts.")
    return count


def import_segments(conn: sqlite3.Connection):
    """Import segments from all segmented texts."""
    count = 0
    fts_data = []

    for tradition_dir in sorted(TEXTS_DIR.iterdir()):
        if not tradition_dir.is_dir():
            continue
        for text_dir in sorted(tradition_dir.iterdir()):
            if not text_dir.is_dir():
                continue
            text_id = text_dir.name
            seg_index_path = text_dir / "segments" / "segments.json"
            if not seg_index_path.exists():
                continue

            with open(seg_index_path, "r", encoding="utf-8") as f:
                seg_index = json.load(f)

            for i, seg in enumerate(seg_index.get("segments", [])):
                seg_file = text_dir / "segments" / seg["file"]
                content = ""
                if seg_file.exists():
                    with open(seg_file, "r", encoding="utf-8") as f:
                        content = f.read()

                segment_id = f"{text_id}:{seg['id']}"
                conn.execute(
                    """INSERT OR REPLACE INTO segments
                       (segment_id, text_id, label, segment_type, ordinal,
                        word_count, content)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (segment_id, text_id, seg.get("label", ""),
                     seg.get("segment_type", ""), i + 1,
                     seg.get("word_count", 0), content)
                )
                fts_data.append((segment_id, text_id,
                                seg.get("label", ""), content))
                count += 1

    # Populate FTS index
    conn.executemany(
        "INSERT INTO segments_fts (segment_id, text_id, label, content) VALUES (?, ?, ?, ?)",
        fts_data
    )
    conn.commit()
    print(f"Imported {count} segments (with FTS index).")
    return count


def import_entities(conn: sqlite3.Connection):
    """Import entities and mentions."""
    catalog_path = DATA_DIR / "entity_catalog.json"
    entities_path = DATA_DIR / "entities.json"
    aliases_path = DATA_DIR / "entity_aliases.json"

    if not catalog_path.exists():
        print("No entity catalog found, skipping.")
        return 0

    # Import entity catalog
    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    entity_count = 0
    entity_id_map = {}
    for name, info in catalog.items():
        conn.execute(
            """INSERT OR REPLACE INTO entities
               (canonical_name, entity_type, primary_tradition,
                total_mentions, text_count, tradition_count)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, info.get("entity_type", "unknown"),
             info.get("primary_tradition", "unknown"),
             info.get("total_mentions", 0),
             info.get("text_count", 0),
             info.get("tradition_count", 0))
        )
        entity_id_map[name] = conn.execute(
            "SELECT entity_id FROM entities WHERE canonical_name = ?",
            (name,)
        ).fetchone()[0]
        entity_count += 1

    # Import aliases
    alias_count = 0
    if aliases_path.exists():
        with open(aliases_path, "r", encoding="utf-8") as f:
            alias_data = json.load(f)
        for canonical, aliases in alias_data.get("aliases", {}).items():
            eid = entity_id_map.get(canonical)
            if eid is None:
                continue
            for alias in aliases:
                conn.execute(
                    """INSERT INTO entity_aliases
                       (entity_id, alias_name, source_tradition)
                       VALUES (?, ?, ?)""",
                    (eid, alias, "")
                )
                alias_count += 1

    # Import mentions (from per-text extraction data)
    mention_count = 0
    if entities_path.exists():
        with open(entities_path, "r", encoding="utf-8") as f:
            all_extractions = json.load(f)

        for text_result in all_extractions:
            if text_result.get("status") != "extracted":
                continue
            text_id = text_result["text_id"]

            for seg_data in text_result.get("segments", []):
                segment_id = f"{text_id}:{seg_data['segment_id']}"

                for mention in seg_data.get("mentions", []):
                    eid = entity_id_map.get(mention["entity_name"])
                    if eid is None:
                        continue

                    conn.execute(
                        """INSERT INTO entity_mentions
                           (entity_id, segment_id, mention_text,
                            sentence_context, char_offset)
                           VALUES (?, ?, ?, ?, ?)""",
                        (eid, segment_id, mention.get("matched_text", ""),
                         mention.get("sentence_context", "")[:200],
                         mention.get("char_offset", 0))
                    )
                    mention_count += 1

    conn.commit()
    print(f"Imported {entity_count} entities, {alias_count} aliases, "
          f"{mention_count} mentions.")
    return entity_count


def import_motifs(conn: sqlite3.Connection):
    """Import motif index and tags."""
    index_path = DATA_DIR / "thompson_motif_index.json"
    tags_path = DATA_DIR / "motif_tags.json"

    if not index_path.exists():
        print("No motif index found, skipping.")
        return 0

    # Import motif index
    with open(index_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    motif_count = 0
    for code, motif in data.get("motifs", {}).items():
        conn.execute(
            """INSERT OR REPLACE INTO motifs
               (motif_code, label, parent_code, category, keywords)
               VALUES (?, ?, ?, ?, ?)""",
            (code, motif["label"], motif.get("parent"),
             motif.get("category", ""),
             json.dumps(motif.get("keywords", [])))
        )
        motif_count += 1

    # Import tags
    tag_count = 0
    if tags_path.exists():
        with open(tags_path, "r", encoding="utf-8") as f:
            all_tags = json.load(f)

        for text_result in all_tags:
            if text_result.get("status") != "tagged":
                continue
            text_id = text_result["text_id"]

            for seg_data in text_result.get("segments", []):
                segment_id = f"{text_id}:{seg_data['segment_id']}"

                for tag in seg_data.get("tags", []):
                    conn.execute(
                        """INSERT INTO motif_tags
                           (motif_code, segment_id, confidence, evidence, method)
                           VALUES (?, ?, ?, ?, ?)""",
                        (tag["code"], segment_id, tag.get("confidence", 0),
                         json.dumps(tag.get("evidence", [])),
                         tag.get("method", "keyword_match"))
                    )
                    tag_count += 1

    conn.commit()
    print(f"Imported {motif_count} motifs, {tag_count} tags.")
    return motif_count


def build_cross_cultural_patterns(conn: sqlite3.Connection):
    """
    Identify and store cross-cultural patterns based on motif co-occurrence
    across multiple traditions.
    """
    # Define key mythic patterns and their associated motifs
    pattern_defs = [
        {
            "name": "cosmogony_creation",
            "description": "Creation of the universe from primordial chaos or void",
            "motif_codes": ["A1", "A600", "A610", "A620", "A700", "A800"],
        },
        {
            "name": "creation_of_humanity",
            "description": "Creation of the first humans from clay, wood, or other materials",
            "motif_codes": ["A1200", "A1210", "A1240", "A1270"],
        },
        {
            "name": "world_flood",
            "description": "Global deluge destroying humanity with survivors",
            "motif_codes": ["A1010", "A1000"],
        },
        {
            "name": "theft_of_fire",
            "description": "Culture hero stealing or obtaining fire for humanity",
            "motif_codes": ["A1415", "A1400", "A540"],
        },
        {
            "name": "descent_to_underworld",
            "description": "Hero or deity journeying to the land of the dead",
            "motif_codes": ["F80", "F81", "F90", "F100", "F110"],
        },
        {
            "name": "dying_and_rising_god",
            "description": "Deity who dies and returns to life, often seasonal",
            "motif_codes": ["Z300", "E0", "E100", "A560"],
        },
        {
            "name": "hero_cycle",
            "description": "Hero's journey: departure, initiation, return",
            "motif_codes": ["Z210", "Z200", "H300", "H1200", "H1220"],
        },
        {
            "name": "trickster",
            "description": "Cunning figure who breaks rules and boundaries",
            "motif_codes": ["Z310", "K0", "K100", "K200", "K300"],
        },
        {
            "name": "divine_conflict",
            "description": "War between gods or cosmic forces",
            "motif_codes": ["A150", "A151", "A162"],
        },
        {
            "name": "great_mother",
            "description": "Earth mother or fertility goddess figure",
            "motif_codes": ["A410", "A431", "A400"],
        },
        {
            "name": "world_destruction_renewal",
            "description": "Cyclic destruction and renewal of the world",
            "motif_codes": ["A1000", "A1020", "A1030", "A1050"],
        },
        {
            "name": "dragon_slaying",
            "description": "Hero defeating a dragon, serpent, or chaos monster",
            "motif_codes": ["G300", "A530", "G500"],
        },
        {
            "name": "transformation_metamorphosis",
            "description": "Shape-shifting, transformation between forms",
            "motif_codes": ["D0", "D10", "D100", "D200", "D610"],
        },
        {
            "name": "forbidden_knowledge",
            "description": "Punishment for acquiring or transgressing knowledge",
            "motif_codes": ["Q220", "Q240", "Q260", "A1310"],
        },
        {
            "name": "quest_for_immortality",
            "description": "Hero seeking eternal life or the water of life",
            "motif_codes": ["H1200", "E50", "D1500"],
        },
        {
            "name": "abandoned_child_hero",
            "description": "Exposed or abandoned child who becomes a hero",
            "motif_codes": ["S300", "S310", "L100"],
        },
        {
            "name": "miraculous_birth",
            "description": "Hero born through supernatural means",
            "motif_codes": ["T500", "T510", "T540"],
        },
        {
            "name": "prophecy_fate",
            "description": "Unavoidable destiny foretold by oracle or prophecy",
            "motif_codes": ["M300", "M340", "M370"],
        },
    ]

    pattern_count = 0
    attestation_count = 0

    for pdef in pattern_defs:
        # Find which texts have these motifs with significant confidence
        codes_str = ",".join(f"'{c}'" for c in pdef["motif_codes"])
        rows = conn.execute(f"""
            SELECT DISTINCT s.text_id, t.tradition,
                   AVG(mt.confidence) as avg_conf,
                   COUNT(DISTINCT mt.motif_code) as motif_variety
            FROM motif_tags mt
            JOIN segments s ON mt.segment_id = s.segment_id
            JOIN texts t ON s.text_id = t.text_id
            WHERE mt.motif_code IN ({codes_str})
              AND mt.confidence >= 0.3
            GROUP BY s.text_id
            HAVING motif_variety >= 1
            ORDER BY avg_conf DESC
        """).fetchall()

        traditions = set(r[1] for r in rows)

        conn.execute(
            """INSERT INTO patterns
               (pattern_name, description, motif_codes,
                attestation_count, tradition_count, confidence)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (pdef["name"], pdef["description"],
             json.dumps(pdef["motif_codes"]),
             len(rows), len(traditions),
             round(sum(r[2] for r in rows) / max(len(rows), 1), 3))
        )
        pattern_id = conn.execute(
            "SELECT last_insert_rowid()"
        ).fetchone()[0]
        pattern_count += 1

        for text_id, tradition, avg_conf, motif_variety in rows:
            conn.execute(
                """INSERT INTO pattern_attestations
                   (pattern_id, text_id, tradition, confidence)
                   VALUES (?, ?, ?, ?)""",
                (pattern_id, text_id, tradition, round(avg_conf, 3))
            )
            attestation_count += 1

    conn.commit()
    print(f"Built {pattern_count} cross-cultural patterns "
          f"with {attestation_count} attestations.")
    return pattern_count


def print_summary(conn: sqlite3.Connection):
    """Print database summary statistics."""
    print(f"\n{'='*60}")
    print(f"MYTHIC PATTERNS DATABASE SUMMARY")
    print(f"{'='*60}")

    tables = [
        ("texts", "SELECT COUNT(*) FROM texts"),
        ("texts (usable)", "SELECT COUNT(*) FROM texts WHERE usable = 1"),
        ("segments", "SELECT COUNT(*) FROM segments"),
        ("entities", "SELECT COUNT(*) FROM entities"),
        ("entity_aliases", "SELECT COUNT(*) FROM entity_aliases"),
        ("entity_mentions", "SELECT COUNT(*) FROM entity_mentions"),
        ("motifs", "SELECT COUNT(*) FROM motifs"),
        ("motif_tags", "SELECT COUNT(*) FROM motif_tags"),
        ("patterns", "SELECT COUNT(*) FROM patterns"),
        ("pattern_attestations", "SELECT COUNT(*) FROM pattern_attestations"),
    ]

    for name, query in tables:
        count = conn.execute(query).fetchone()[0]
        print(f"  {name:25s} {count:>8,}")

    # DB file size
    db_size = DB_PATH.stat().st_size / (1024 * 1024)
    print(f"\n  Database size: {db_size:.1f} MB")
    print(f"  Path: {DB_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Create mythic patterns database")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate")
    args = parser.parse_args()

    print("Creating mythic patterns database...")
    conn = create_database(reset=args.reset)

    print("\nImporting data...")
    import_texts(conn)
    import_segments(conn)
    import_entities(conn)
    import_motifs(conn)

    print("\nBuilding cross-cultural patterns...")
    build_cross_cultural_patterns(conn)

    print_summary(conn)
    conn.close()


if __name__ == "__main__":
    main()
