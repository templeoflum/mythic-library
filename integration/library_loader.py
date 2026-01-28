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

    # ── Segment-level queries for narrative position analysis ──

    def get_all_texts(self) -> List[Dict]:
        """Get all text metadata."""
        rows = self.conn.execute("""
            SELECT text_id, title, tradition, author, material_type, word_count
            FROM texts
            WHERE usable = 1
            ORDER BY tradition, title
        """).fetchall()
        return [dict(r) for r in rows]

    def get_segments_per_text(self) -> Dict[str, int]:
        """Get {text_id: segment_count} for all texts."""
        rows = self.conn.execute("""
            SELECT text_id, COUNT(*) as cnt
            FROM segments
            GROUP BY text_id
        """).fetchall()
        return {r["text_id"]: r["cnt"] for r in rows}

    def get_text_segments_ordered(self, text_id: str) -> List[Dict]:
        """Get segments for a text in narrative order with entities and motifs.

        Returns list of dicts sorted by ordinal, each with:
          segment_id, label, ordinal, word_count, entity_names, motif_codes
        """
        # Get segments in order
        seg_rows = self.conn.execute("""
            SELECT segment_id, label, ordinal, word_count
            FROM segments
            WHERE text_id = ?
            ORDER BY ordinal
        """, (text_id,)).fetchall()

        if not seg_rows:
            return []

        seg_ids = [r["segment_id"] for r in seg_rows]

        # Batch-load entity mentions for all segments in this text
        placeholders = ",".join("?" * len(seg_ids))
        ent_rows = self.conn.execute(f"""
            SELECT em.segment_id, e.canonical_name
            FROM entity_mentions em
            JOIN entities e ON em.entity_id = e.entity_id
            WHERE em.segment_id IN ({placeholders})
        """, seg_ids).fetchall()

        seg_entities: Dict[str, List[str]] = {}
        for r in ent_rows:
            seg_entities.setdefault(r["segment_id"], []).append(r["canonical_name"])

        # Batch-load motif tags
        mt_rows = self.conn.execute(f"""
            SELECT segment_id, motif_code
            FROM motif_tags
            WHERE segment_id IN ({placeholders})
              AND confidence >= 0.3
        """, seg_ids).fetchall()

        seg_motifs: Dict[str, List[str]] = {}
        for r in mt_rows:
            seg_motifs.setdefault(r["segment_id"], []).append(r["motif_code"])

        # Assemble results
        results = []
        for r in seg_rows:
            sid = r["segment_id"]
            results.append({
                "segment_id": sid,
                "label": r["label"],
                "ordinal": r["ordinal"],
                "word_count": r["word_count"],
                "entity_names": list(set(seg_entities.get(sid, []))),
                "motif_codes": list(set(seg_motifs.get(sid, []))),
            })
        return results

    def get_segment_entities(self, segment_id: str) -> List[str]:
        """Get entity names mentioned in a specific segment."""
        rows = self.conn.execute("""
            SELECT DISTINCT e.canonical_name
            FROM entity_mentions em
            JOIN entities e ON em.entity_id = e.entity_id
            WHERE em.segment_id = ?
        """, (segment_id,)).fetchall()
        return [r["canonical_name"] for r in rows]

    def get_segment_motifs(self, segment_id: str) -> List[Dict]:
        """Get motif tags for a segment."""
        rows = self.conn.execute("""
            SELECT motif_code, confidence
            FROM motif_tags
            WHERE segment_id = ?
              AND confidence >= 0.3
            ORDER BY confidence DESC
        """, (segment_id,)).fetchall()
        return [dict(r) for r in rows]

    def get_pattern_motif_codes(self, pattern_name: str) -> List[str]:
        """Get motif codes for a named cross-cultural pattern."""
        row = self.conn.execute("""
            SELECT motif_codes FROM patterns WHERE pattern_name = ?
        """, (pattern_name,)).fetchone()
        if not row:
            return []
        import json as _json
        return _json.loads(row["motif_codes"])

    def get_all_patterns(self) -> List[Dict]:
        """Get all named cross-cultural patterns."""
        rows = self.conn.execute("""
            SELECT pattern_name, description, motif_codes, attestation_count,
                   tradition_count, confidence
            FROM patterns
            ORDER BY attestation_count DESC
        """).fetchall()
        result = []
        import json as _json
        for r in rows:
            d = dict(r)
            d["motif_codes"] = _json.loads(d["motif_codes"])
            result.append(d)
        return result

    def get_entities_for_motif_codes(self, motif_codes: List[str]) -> List[str]:
        """Get distinct entity names appearing in segments tagged with any of the given motifs."""
        if not motif_codes:
            return []
        placeholders = ",".join("?" * len(motif_codes))
        rows = self.conn.execute(f"""
            SELECT DISTINCT e.canonical_name
            FROM motif_tags mt
            JOIN entity_mentions em ON mt.segment_id = em.segment_id
            JOIN entities e ON em.entity_id = e.entity_id
            WHERE mt.motif_code IN ({placeholders})
              AND mt.confidence >= 0.3
        """, motif_codes).fetchall()
        return [r["canonical_name"] for r in rows]

    def close(self):
        self.conn.close()
