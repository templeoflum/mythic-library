#!/usr/bin/env python3
"""Find entity names that are likely common English words causing false positive matches."""
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "data" / "mythic_patterns.db"

# Inline the gazetteer traditions to avoid import conflicts
ENTITY_HOME_TRADITION = {
    "Set": "egyptian", "Nut": "egyptian", "Geb": "egyptian", "Isis": "egyptian",
    "Horus": "egyptian", "Osiris": "egyptian", "Thoth": "egyptian", "Anubis": "egyptian",
    "Ra": "egyptian", "Amun": "egyptian", "Hathor": "egyptian", "Nephthys": "egyptian",
    "Ptah": "egyptian", "Atum": "egyptian", "Sekhmet": "egyptian", "Sobek": "egyptian",
    "Khepri": "egyptian",
    "Eve": "hebrew", "Adam": "hebrew", "Moses": "hebrew",
    "Mars": "roman", "Venus": "roman", "Mercury": "roman", "Saturn": "roman",
    "Jupiter": "roman", "Juno": "roman", "Neptune": "roman", "Minerva": "roman",
    "Pluto": "roman", "Jove": "roman",
    "Finn": "celtic", "Tuatha": "celtic", "Brigid": "celtic", "Danu": "celtic",
    "Soma": "indian", "Kali": "indian", "Rama": "indian", "Sita": "indian",
    "Agni": "indian", "Indra": "indian", "Arjuna": "indian", "Krishna": "indian",
    "Troy": "greek", "Ajax": "greek", "Helen": "greek", "Jason": "greek",
    "Medea": "greek", "Titans": "greek", "Styx": "greek",
    "Tyr": "norse", "Loki": "norse", "Thor": "norse", "Odin": "norse",
    "Tane": "polynesian", "Pele": "polynesian", "Maui": "polynesian",
    "Kur": "mesopotamian", "Anu": "mesopotamian",
    "Satan": "christian", "Virgil": "roman", "Dante": "roman", "Beatrice": "roman",
}

def main():
    db = sqlite3.connect(str(DB_PATH))

    rows = db.execute("""
        SELECT e.canonical_name, e.entity_type, e.total_mentions
        FROM entities e ORDER BY e.total_mentions DESC
    """).fetchall()

    suspects = []
    for name, etype, total in rows:
        home_trad = ENTITY_HOME_TRADITION.get(name)
        if not home_trad:
            continue  # Only check entities we know the home tradition for

        home_row = db.execute("""
            SELECT COUNT(*) FROM entity_mentions em
            JOIN segments s ON em.segment_id = s.segment_id
            JOIN texts t ON s.text_id = t.text_id
            JOIN entities e ON em.entity_id = e.entity_id
            WHERE e.canonical_name = ? AND t.tradition = ?
        """, (name, home_trad)).fetchone()

        trad_row = db.execute("""
            SELECT COUNT(DISTINCT t.tradition) FROM entity_mentions em
            JOIN segments s ON em.segment_id = s.segment_id
            JOIN texts t ON s.text_id = t.text_id
            JOIN entities e ON em.entity_id = e.entity_id
            WHERE e.canonical_name = ?
        """, (name,)).fetchone()

        home_count = home_row[0]
        other_count = total - home_count
        home_pct = (home_count / total * 100) if total > 0 else 0
        num_trads = trad_row[0]

        is_suspect = False
        reason = ""
        if home_pct < 15 and total > 50:
            is_suspect = True
            reason = "common word (very low home %)"
        elif home_pct < 25 and total > 100:
            is_suspect = True
            reason = "likely common word"
        elif len(name) <= 3 and total > 20:
            is_suspect = True
            reason = "short name risk"

        if is_suspect:
            suspects.append((name, total, home_count, other_count, home_pct, num_trads, reason))

    print("SUSPECT ENTITIES (likely false positive matches):")
    print("=" * 95)
    for name, total, home, other, pct, trads, reason in sorted(suspects, key=lambda x: x[4]):
        print(f"  {name:20s} total={total:5d}  home={home:4d} ({pct:4.1f}%)  false~={other:4d}  trads={trads:2d}  {reason}")
    print(f"\nTotal suspects: {len(suspects)}")
    db.close()


if __name__ == "__main__":
    main()
