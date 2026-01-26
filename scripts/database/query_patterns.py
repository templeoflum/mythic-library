#!/usr/bin/env python3
"""
Pattern Database Query Tool for Mythic Library Phase 3.

Pre-built queries demonstrating the mythic patterns database.

Usage:
    python scripts/database/query_patterns.py                    # Run all queries
    python scripts/database/query_patterns.py --query flood      # Specific query
    python scripts/database/query_patterns.py --sql "SELECT ..."  # Custom SQL
"""

import argparse
import io
import json
import sqlite3
import sys

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "mythic_patterns.db"


def get_conn():
    """Get database connection."""
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        print("Run: python scripts/database/create_db.py")
        sys.exit(1)
    return sqlite3.connect(str(DB_PATH))


def query_cross_cultural_patterns(conn):
    """Show all cross-cultural patterns ranked by tradition count."""
    print(f"\n{'='*70}")
    print("CROSS-CULTURAL MYTHIC PATTERNS")
    print(f"{'='*70}")

    rows = conn.execute("""
        SELECT pattern_name, description, attestation_count,
               tradition_count, confidence
        FROM patterns
        ORDER BY tradition_count DESC, attestation_count DESC
    """).fetchall()

    for name, desc, att_count, trad_count, conf in rows:
        print(f"\n  {name}")
        print(f"    {desc}")
        print(f"    Attestations: {att_count} texts across "
              f"{trad_count} traditions (confidence: {conf:.3f})")

        # Top traditions
        traditions = conn.execute("""
            SELECT tradition, COUNT(*) as count, AVG(confidence) as avg_conf
            FROM pattern_attestations
            WHERE pattern_id = (SELECT pattern_id FROM patterns WHERE pattern_name = ?)
            GROUP BY tradition
            ORDER BY count DESC
            LIMIT 10
        """, (name,)).fetchall()

        if traditions:
            trad_str = ", ".join(f"{t}({c})" for t, c, _ in traditions)
            print(f"    Traditions: {trad_str}")


def query_flood_narratives(conn):
    """Find all flood narratives across traditions."""
    print(f"\n{'='*70}")
    print("FLOOD NARRATIVES (Motif A1010: Deluge)")
    print(f"{'='*70}")

    rows = conn.execute("""
        SELECT DISTINCT t.text_id, t.title, t.tradition, t.date_composed,
               mt.confidence, s.label
        FROM motif_tags mt
        JOIN segments s ON mt.segment_id = s.segment_id
        JOIN texts t ON s.text_id = t.text_id
        WHERE mt.motif_code = 'A1010'
          AND mt.confidence >= 0.3
        ORDER BY mt.confidence DESC, t.tradition
    """).fetchall()

    for text_id, title, tradition, date, conf, seg_label in rows:
        print(f"  [{conf:.2f}] {tradition:20s} | {title:40s} | {seg_label}")


def query_descent_underworld(conn):
    """Find all descent-to-underworld narratives."""
    print(f"\n{'='*70}")
    print("DESCENT TO UNDERWORLD (Motifs F80, F81, F100)")
    print(f"{'='*70}")

    rows = conn.execute("""
        SELECT DISTINCT t.text_id, t.title, t.tradition,
               MAX(mt.confidence) as max_conf,
               GROUP_CONCAT(DISTINCT mt.motif_code) as motifs
        FROM motif_tags mt
        JOIN segments s ON mt.segment_id = s.segment_id
        JOIN texts t ON s.text_id = t.text_id
        WHERE mt.motif_code IN ('F80', 'F81', 'F90', 'F100', 'F110')
          AND mt.confidence >= 0.3
        GROUP BY t.text_id
        ORDER BY max_conf DESC
    """).fetchall()

    for text_id, title, tradition, conf, motifs in rows:
        print(f"  [{conf:.2f}] {tradition:20s} | {title:40s} | {motifs}")


def query_cross_tradition_entities(conn):
    """Find entities appearing across 3+ traditions."""
    print(f"\n{'='*70}")
    print("ENTITIES ACROSS 3+ TRADITIONS (excluding common-word false positives)")
    print(f"{'='*70}")

    # Exclude known false positives (common English words)
    exclude = "('Set', 'Eve', 'Nut', 'Mars', 'Soma', 'Finn', 'Kali')"

    rows = conn.execute(f"""
        SELECT canonical_name, entity_type, primary_tradition,
               total_mentions, text_count, tradition_count
        FROM entities
        WHERE tradition_count >= 3
          AND canonical_name NOT IN {exclude}
        ORDER BY tradition_count DESC, total_mentions DESC
        LIMIT 30
    """).fetchall()

    for name, etype, tradition, mentions, texts, traditions in rows:
        print(f"  {name:20s} | {etype:10s} | {traditions:2d} traditions, "
              f"{texts:3d} texts, {mentions:5d} mentions")


def query_hero_cycle(conn):
    """Find texts with hero cycle patterns."""
    print(f"\n{'='*70}")
    print("HERO CYCLE ATTESTATIONS")
    print(f"{'='*70}")

    rows = conn.execute("""
        SELECT t.title, t.tradition, pa.confidence
        FROM pattern_attestations pa
        JOIN patterns p ON pa.pattern_id = p.pattern_id
        JOIN texts t ON pa.text_id = t.text_id
        WHERE p.pattern_name = 'hero_cycle'
        ORDER BY pa.confidence DESC
        LIMIT 20
    """).fetchall()

    for title, tradition, conf in rows:
        print(f"  [{conf:.2f}] {tradition:20s} | {title}")


def query_creation_myths(conn):
    """Find creation myths across traditions."""
    print(f"\n{'='*70}")
    print("CREATION MYTHS (COSMOGONY)")
    print(f"{'='*70}")

    rows = conn.execute("""
        SELECT t.title, t.tradition, pa.confidence
        FROM pattern_attestations pa
        JOIN patterns p ON pa.pattern_id = p.pattern_id
        JOIN texts t ON pa.text_id = t.text_id
        WHERE p.pattern_name = 'cosmogony_creation'
        ORDER BY pa.confidence DESC
        LIMIT 20
    """).fetchall()

    for title, tradition, conf in rows:
        print(f"  [{conf:.2f}] {tradition:20s} | {title}")


def query_trickster(conn):
    """Find trickster narratives."""
    print(f"\n{'='*70}")
    print("TRICKSTER NARRATIVES")
    print(f"{'='*70}")

    rows = conn.execute("""
        SELECT t.title, t.tradition, pa.confidence
        FROM pattern_attestations pa
        JOIN patterns p ON pa.pattern_id = p.pattern_id
        JOIN texts t ON pa.text_id = t.text_id
        WHERE p.pattern_name = 'trickster'
        ORDER BY pa.confidence DESC
        LIMIT 20
    """).fetchall()

    for title, tradition, conf in rows:
        print(f"  [{conf:.2f}] {tradition:20s} | {title}")


def query_fts_search(conn, search_term: str):
    """Full-text search across all segments."""
    print(f"\n{'='*70}")
    print(f"FULL-TEXT SEARCH: '{search_term}'")
    print(f"{'='*70}")

    rows = conn.execute("""
        SELECT s.text_id, s.label, t.tradition,
               snippet(segments_fts, 3, '>>>', '<<<', '...', 30) as snippet
        FROM segments_fts fts
        JOIN segments s ON fts.segment_id = s.segment_id
        JOIN texts t ON s.text_id = t.text_id
        WHERE segments_fts MATCH ?
        LIMIT 15
    """, (search_term,)).fetchall()

    for text_id, label, tradition, snippet in rows:
        print(f"  {tradition:20s} | {text_id:30s} | {label}")
        print(f"    {snippet[:120]}")


def query_database_stats(conn):
    """Show comprehensive database statistics."""
    print(f"\n{'='*70}")
    print("DATABASE STATISTICS")
    print(f"{'='*70}")

    stats = {
        "Total texts": "SELECT COUNT(*) FROM texts",
        "Usable texts": "SELECT COUNT(*) FROM texts WHERE usable = 1",
        "Total segments": "SELECT COUNT(*) FROM segments",
        "Total word count": "SELECT SUM(word_count) FROM segments",
        "Unique entities": "SELECT COUNT(*) FROM entities",
        "Entity mentions": "SELECT COUNT(*) FROM entity_mentions",
        "Thompson motifs": "SELECT COUNT(*) FROM motifs",
        "Motif tags": "SELECT COUNT(*) FROM motif_tags",
        "Cross-cultural patterns": "SELECT COUNT(*) FROM patterns",
        "Pattern attestations": "SELECT COUNT(*) FROM pattern_attestations",
        "Traditions": "SELECT COUNT(DISTINCT tradition) FROM texts",
    }

    for label, query in stats.items():
        val = conn.execute(query).fetchone()[0] or 0
        print(f"  {label:30s} {val:>10,}")


def run_all_queries(conn):
    """Run all demonstration queries."""
    query_database_stats(conn)
    query_cross_cultural_patterns(conn)
    query_flood_narratives(conn)
    query_descent_underworld(conn)
    query_cross_tradition_entities(conn)
    query_hero_cycle(conn)
    query_creation_myths(conn)
    query_trickster(conn)
    query_fts_search(conn, "underworld OR descent OR netherworld")
    query_fts_search(conn, "flood OR deluge OR waters")


def main():
    parser = argparse.ArgumentParser(description="Query the mythic patterns database")
    parser.add_argument("--query", help="Run a specific query (flood, descent, entities, hero, creation, trickster, stats)")
    parser.add_argument("--sql", help="Run custom SQL query")
    parser.add_argument("--search", help="Full-text search term")
    args = parser.parse_args()

    conn = get_conn()

    if args.sql:
        rows = conn.execute(args.sql).fetchall()
        for row in rows:
            print(row)
    elif args.search:
        query_fts_search(conn, args.search)
    elif args.query:
        queries = {
            "flood": query_flood_narratives,
            "descent": query_descent_underworld,
            "entities": query_cross_tradition_entities,
            "hero": query_hero_cycle,
            "creation": query_creation_myths,
            "trickster": query_trickster,
            "stats": query_database_stats,
            "patterns": query_cross_cultural_patterns,
        }
        func = queries.get(args.query)
        if func:
            func(conn)
        else:
            print(f"Unknown query: {args.query}")
            print(f"Available: {', '.join(queries.keys())}")
    else:
        run_all_queries(conn)

    conn.close()


if __name__ == "__main__":
    main()
