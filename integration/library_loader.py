"""Load and query the mythic library pattern database."""
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class Entity:
    entity_id: int
    canonical_name: str
    entity_type: str
    primary_tradition: str
    total_mentions: int
    text_count: int
    tradition_count: int


@dataclass
class CooccurrencePair:
    entity1: str
    entity2: str
    shared_segments: int
    shared_texts: int


class LibraryLoader:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._cooccurrence_cache: Optional[Dict[Tuple[str, str], int]] = None

    def get_all_entities(self) -> List[Entity]:
        """Retrieve all entities."""
        rows = self.conn.execute("""
            SELECT entity_id, canonical_name, entity_type, primary_tradition,
                   total_mentions, text_count, tradition_count
            FROM entities
            ORDER BY total_mentions DESC
        """).fetchall()

        return [
            Entity(
                entity_id=r["entity_id"],
                canonical_name=r["canonical_name"],
                entity_type=r["entity_type"],
                primary_tradition=r["primary_tradition"],
                total_mentions=r["total_mentions"],
                text_count=r["text_count"],
                tradition_count=r["tradition_count"],
            )
            for r in rows
        ]

    def get_entity_aliases(self) -> Dict[str, List[str]]:
        """Get canonical_name -> [alias_names] mapping from DB."""
        rows = self.conn.execute("""
            SELECT e.canonical_name, ea.alias_name
            FROM entity_aliases ea
            JOIN entities e ON ea.entity_id = e.entity_id
        """).fetchall()

        aliases: Dict[str, List[str]] = {}
        for r in rows:
            aliases.setdefault(r["canonical_name"], []).append(r["alias_name"])
        return aliases

    def _ensure_cooccurrence_cache(self) -> Dict[Tuple[str, str], int]:
        """Build co-occurrence cache with a single bulk SQL query.

        Returns a dict mapping (entity1, entity2) -> shared_segment_count
        where entity1 < entity2 lexicographically. Pairs with zero
        co-occurrence are not stored (defaulting to 0 on lookup).
        """
        if self._cooccurrence_cache is not None:
            return self._cooccurrence_cache

        rows = self.conn.execute("""
            SELECT e1.canonical_name as name1, e2.canonical_name as name2,
                   COUNT(DISTINCT em1.segment_id) as shared_segments
            FROM entity_mentions em1
            JOIN entity_mentions em2 ON em1.segment_id = em2.segment_id
            JOIN entities e1 ON em1.entity_id = e1.entity_id
            JOIN entities e2 ON em2.entity_id = e2.entity_id
            WHERE e1.entity_id < e2.entity_id
            GROUP BY e1.entity_id, e2.entity_id
        """).fetchall()

        cache: Dict[Tuple[str, str], int] = {}
        for r in rows:
            key = tuple(sorted((r["name1"], r["name2"])))
            cache[key] = r["shared_segments"]

        self._cooccurrence_cache = cache
        return cache

    def get_entity_cooccurrence(self, entity1_name: str, entity2_name: str) -> int:
        """Count segments where both entities appear (cached)."""
        cache = self._ensure_cooccurrence_cache()
        key = tuple(sorted((entity1_name, entity2_name)))
        return cache.get(key, 0)

    def get_all_cooccurrences(self, min_count: int = 1) -> List[CooccurrencePair]:
        """Get all entity co-occurrence pairs above threshold."""
        rows = self.conn.execute("""
            SELECT e1.canonical_name as name1, e2.canonical_name as name2,
                   COUNT(DISTINCT em1.segment_id) as shared_segments,
                   COUNT(DISTINCT s.text_id) as shared_texts
            FROM entity_mentions em1
            JOIN entity_mentions em2 ON em1.segment_id = em2.segment_id
            JOIN entities e1 ON em1.entity_id = e1.entity_id
            JOIN entities e2 ON em2.entity_id = e2.entity_id
            JOIN segments s ON em1.segment_id = s.segment_id
            WHERE e1.entity_id < e2.entity_id
            GROUP BY e1.entity_id, e2.entity_id
            HAVING shared_segments >= ?
            ORDER BY shared_segments DESC
        """, (min_count,)).fetchall()

        return [
            CooccurrencePair(
                entity1=r["name1"],
                entity2=r["name2"],
                shared_segments=r["shared_segments"],
                shared_texts=r["shared_texts"],
            )
            for r in rows
        ]

    def get_motif_entities(self, motif_code: str) -> List[str]:
        """Get entity names that appear in segments tagged with a motif."""
        rows = self.conn.execute("""
            SELECT DISTINCT e.canonical_name
            FROM motif_tags mt
            JOIN entity_mentions em ON mt.segment_id = em.segment_id
            JOIN entities e ON em.entity_id = e.entity_id
            WHERE mt.motif_code = ?
              AND mt.confidence >= 0.3
        """, (motif_code,)).fetchall()

        return [r["canonical_name"] for r in rows]

    def get_all_motif_codes(self) -> List[str]:
        """Get all unique motif codes that have tags."""
        rows = self.conn.execute("""
            SELECT DISTINCT motif_code
            FROM motif_tags
            WHERE confidence >= 0.3
            ORDER BY motif_code
        """).fetchall()

        return [r["motif_code"] for r in rows]

    def get_segment_count(self) -> int:
        """Total number of segments."""
        row = self.conn.execute("SELECT COUNT(*) as c FROM segments").fetchone()
        return row["c"]

    def get_entity_traditions(self, entity_name: str) -> List[str]:
        """Get traditions where an entity appears."""
        rows = self.conn.execute("""
            SELECT DISTINCT t.tradition
            FROM entity_mentions em
            JOIN entities e ON em.entity_id = e.entity_id
            JOIN segments s ON em.segment_id = s.segment_id
            JOIN texts t ON s.text_id = t.text_id
            WHERE e.canonical_name = ?
        """, (entity_name,)).fetchall()

        return [r["tradition"] for r in rows]

    def summary(self) -> dict:
        """Return summary statistics."""
        stats = {}
        for label, query in [
            ("entities", "SELECT COUNT(*) FROM entities"),
            ("entity_mentions", "SELECT COUNT(*) FROM entity_mentions"),
            ("segments", "SELECT COUNT(*) FROM segments"),
            ("motifs", "SELECT COUNT(*) FROM motifs"),
            ("motif_tags", "SELECT COUNT(*) FROM motif_tags"),
            ("traditions", "SELECT COUNT(DISTINCT tradition) FROM texts"),
        ]:
            stats[label] = self.conn.execute(query).fetchone()[0]
        return stats

    def close(self):
        self.conn.close()
