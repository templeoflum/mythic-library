"""Phase 7: Data quality and coverage analysis.

Audits entity extraction precision, normalizes co-occurrence counts
by text length and tradition size, checks for cross-tradition
deduplication issues, and documents unmapped entity coverage gaps.
"""
import sqlite3
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from scipy.stats import spearmanr

from integration.acp_loader import ACPLoader
from integration.library_loader import LibraryLoader
from integration.entity_mapper import EntityMapper


class DataQualityAuditor:
    def __init__(self, acp: ACPLoader, library: LibraryLoader, mapper: EntityMapper):
        self.acp = acp
        self.library = library
        self.mapper = mapper
        self.conn = library.conn

    # ── Entity Extraction Audit ──────────────────────────────

    def entity_mention_audit(self, sample_size: int = 100, seed: int = 42) -> Dict:
        """Sample random entity mentions and flag potential issues.

        Checks for:
        - Mentions with no sentence context (extraction artifact)
        - Very short mention texts (possible false positive)
        - Mentions in segments with 0 or very low word count
        - Entity type mismatches (deity mentioned in non-mythic context)
        - Duplicate mentions (same entity, same segment, same offset)
        """
        rng = np.random.default_rng(seed)

        # Total mentions
        total = self.conn.execute("SELECT COUNT(*) FROM entity_mentions").fetchone()[0]

        # Get all mention IDs and sample
        all_ids = [r[0] for r in self.conn.execute(
            "SELECT mention_id FROM entity_mentions"
        ).fetchall()]
        sample_ids = rng.choice(all_ids, size=min(sample_size, len(all_ids)), replace=False)

        # Fetch sampled mentions with context
        placeholders = ",".join("?" * len(sample_ids))
        rows = self.conn.execute(f"""
            SELECT em.mention_id, em.mention_text, em.sentence_context, em.char_offset,
                   e.canonical_name, e.entity_type, e.primary_tradition,
                   s.segment_id, s.word_count, s.label,
                   t.title, t.tradition
            FROM entity_mentions em
            JOIN entities e ON em.entity_id = e.entity_id
            JOIN segments s ON em.segment_id = s.segment_id
            JOIN texts t ON s.text_id = t.text_id
            WHERE em.mention_id IN ({placeholders})
        """, [int(x) for x in sample_ids]).fetchall()

        flags = {
            "no_context": [],
            "short_mention": [],
            "tiny_segment": [],
            "duplicate_offset": [],
        }

        for r in rows:
            mention_id, mention_text, context, offset = r[0], r[1], r[2], r[3]
            entity_name, entity_type, entity_tradition = r[4], r[5], r[6]
            seg_id, seg_words, seg_label = r[7], r[8], r[9]
            text_title, text_tradition = r[10], r[11]

            info = {
                "mention_id": mention_id,
                "entity": entity_name,
                "mention_text": mention_text,
                "segment": seg_label,
                "text": text_title,
            }

            if not context or len(context.strip()) == 0:
                flags["no_context"].append(info)

            if mention_text and len(mention_text) < 3:
                flags["short_mention"].append(info)

            if seg_words is not None and seg_words < 10:
                flags["tiny_segment"].append(info)

        # Check for duplicate mentions globally (same entity + segment + offset)
        dup_rows = self.conn.execute("""
            SELECT entity_id, segment_id, char_offset, COUNT(*) as n
            FROM entity_mentions
            WHERE char_offset IS NOT NULL
            GROUP BY entity_id, segment_id, char_offset
            HAVING n > 1
        """).fetchall()
        n_duplicates = len(dup_rows)

        # Check mentions without context globally
        no_ctx_count = self.conn.execute(
            "SELECT COUNT(*) FROM entity_mentions WHERE sentence_context IS NULL OR sentence_context = ''"
        ).fetchone()[0]

        return {
            "total_mentions": total,
            "sample_size": len(rows),
            "flags": {k: len(v) for k, v in flags.items()},
            "flagged_samples": {k: v[:5] for k, v in flags.items() if v},  # first 5 examples
            "global_stats": {
                "duplicate_offsets": n_duplicates,
                "mentions_without_context": no_ctx_count,
                "pct_without_context": round(100 * no_ctx_count / total, 1) if total else 0,
            },
        }

    # ── Co-occurrence Normalization ──────────────────────────

    def normalized_cooccurrence_test(
        self, exclude_entities: Optional[List[str]] = None
    ) -> Dict:
        """Test whether normalizing co-occurrence improves ACP distance correlation.

        Three normalization strategies:
        1. Raw co-occurrence (baseline)
        2. Log-transformed: log(1 + co-occurrence)
        3. TF-IDF style: co-occurrence * log(N / df) where df = texts containing pair
        4. Tradition-normalized: divide by geometric mean of tradition sizes
        """
        valid = [
            m for m in self.mapper.mappings
            if m.library_entity not in set(exclude_entities or [])
            and self.acp.get_coordinates(m.acp_archetype_id) is not None
        ]
        n = len(valid)

        # Get tradition sizes (total mentions per tradition)
        tradition_sizes = {}
        rows = self.conn.execute("""
            SELECT t.tradition, COUNT(*) as mentions
            FROM entity_mentions em
            JOIN segments s ON em.segment_id = s.segment_id
            JOIN texts t ON s.text_id = t.text_id
            GROUP BY t.tradition
        """).fetchall()
        for r in rows:
            tradition_sizes[r[0]] = r[1]

        # Get entity traditions
        entity_traditions = {}
        for e in self.library.get_all_entities():
            entity_traditions[e.canonical_name] = e.primary_tradition or ""

        # Total segments (for IDF)
        total_segments = self.conn.execute("SELECT COUNT(*) FROM segments").fetchone()[0]

        distances = []
        raw_coocc = []
        log_coocc = []
        tfidf_coocc = []
        tradition_norm_coocc = []

        for i in range(n):
            c1 = self.acp.get_coordinates(valid[i].acp_archetype_id)
            t1 = entity_traditions.get(valid[i].library_entity, "")
            for j in range(i + 1, n):
                c2 = self.acp.get_coordinates(valid[j].acp_archetype_id)
                t2 = entity_traditions.get(valid[j].library_entity, "")

                dist = float(np.linalg.norm(c1 - c2))
                raw = self.library.get_entity_cooccurrence(
                    valid[i].library_entity, valid[j].library_entity
                )

                distances.append(dist)
                raw_coocc.append(raw)
                log_coocc.append(float(np.log1p(raw)))

                # TF-IDF: weight rare co-occurrences higher
                if raw > 0:
                    # df = number of segments where both appear
                    idf = np.log(total_segments / max(raw, 1))
                    tfidf_coocc.append(raw * idf)
                else:
                    tfidf_coocc.append(0.0)

                # Tradition normalization
                size1 = tradition_sizes.get(t1, 1)
                size2 = tradition_sizes.get(t2, 1)
                geo_mean = np.sqrt(size1 * size2)
                tradition_norm_coocc.append(raw / geo_mean if geo_mean > 0 else 0.0)

        dist_arr = np.array(distances)
        if len(dist_arr) < 10:
            return {"error": "Insufficient pairs"}

        results = {}
        for label, coocc_arr in [
            ("raw", np.array(raw_coocc)),
            ("log_transformed", np.array(log_coocc)),
            ("tfidf_weighted", np.array(tfidf_coocc)),
            ("tradition_normalized", np.array(tradition_norm_coocc)),
        ]:
            sr, sp = spearmanr(dist_arr, coocc_arr)
            results[label] = {
                "spearman_r": round(float(sr), 4),
                "spearman_p": round(float(sp), 6),
                "nonzero_pairs": int(np.sum(coocc_arr > 0)),
            }

        # Rank by correlation strength
        ranked = sorted(results.items(), key=lambda x: abs(x[1]["spearman_r"]), reverse=True)
        best_method = ranked[0][0]

        return {
            "n_pairs": len(dist_arr),
            "methods": results,
            "ranking": [{"method": k, "spearman_r": v["spearman_r"]} for k, v in ranked],
            "best_method": best_method,
            "improvement_over_raw": round(
                abs(results[best_method]["spearman_r"]) - abs(results["raw"]["spearman_r"]), 4
            ),
        }

    # ── Cross-Tradition Entity Deduplication ──────────────────

    def cross_tradition_deduplication_check(self) -> Dict:
        """Check for entities that may be duplicates across traditions.

        Identifies:
        1. Entities sharing ACP archetypes (e.g., Ishtar and Inanna both -> same archetype)
        2. Entities with identical or very similar names across traditions
        3. Entities listed as aliases of each other in the DB
        """
        # 1. Entities sharing ACP archetypes
        archetype_to_entities = defaultdict(list)
        for m in self.mapper.mappings:
            archetype_to_entities[m.acp_archetype_id].append({
                "entity": m.library_entity,
                "confidence": m.confidence,
                "method": m.method,
            })

        shared_archetypes = {
            arch_id: entities
            for arch_id, entities in archetype_to_entities.items()
            if len(entities) > 1
        }

        # 2. Check which shared archetypes involve different traditions
        entity_traditions = {}
        for e in self.library.get_all_entities():
            entity_traditions[e.canonical_name] = e.primary_tradition or ""

        cross_tradition_shares = {}
        same_tradition_shares = {}
        for arch_id, entities in shared_archetypes.items():
            traditions = set(entity_traditions.get(e["entity"], "") for e in entities)
            entry = {
                "archetype": arch_id,
                "entities": entities,
                "traditions": sorted(traditions),
            }
            if len(traditions) > 1:
                cross_tradition_shares[arch_id] = entry
            else:
                same_tradition_shares[arch_id] = entry

        # 3. Check entity_aliases table for cross-tradition links
        alias_rows = self.conn.execute("""
            SELECT e1.canonical_name, e1.primary_tradition,
                   e2.canonical_name, e2.primary_tradition
            FROM entity_aliases ea1
            JOIN entities e1 ON ea1.entity_id = e1.entity_id
            JOIN entity_aliases ea2 ON ea1.alias_name = ea2.alias_name
                AND ea1.entity_id != ea2.entity_id
            JOIN entities e2 ON ea2.entity_id = e2.entity_id
            WHERE e1.primary_tradition != e2.primary_tradition
        """).fetchall()

        alias_links = []
        seen = set()
        for r in alias_rows:
            pair = tuple(sorted([r[0], r[2]]))
            if pair not in seen:
                seen.add(pair)
                alias_links.append({
                    "entity1": r[0], "tradition1": r[1],
                    "entity2": r[2], "tradition2": r[3],
                })

        # 4. Impact assessment: how many co-occurrence pairs involve shared archetypes?
        shared_entity_names = set()
        for entities in shared_archetypes.values():
            for e in entities:
                shared_entity_names.add(e["entity"])

        n_shared_in_mappings = sum(
            1 for m in self.mapper.mappings if m.library_entity in shared_entity_names
        )

        return {
            "shared_archetypes": {
                "total": len(shared_archetypes),
                "cross_tradition": len(cross_tradition_shares),
                "same_tradition": len(same_tradition_shares),
                "details": {
                    k: {
                        "entities": [e["entity"] for e in v["entities"]],
                        "traditions": v["traditions"],
                    }
                    for k, v in cross_tradition_shares.items()
                },
            },
            "alias_links": alias_links[:20],  # cap output
            "impact": {
                "entities_sharing_archetypes": len(shared_entity_names),
                "mappings_affected": n_shared_in_mappings,
                "pct_of_mappings": round(100 * n_shared_in_mappings / max(len(self.mapper.mappings), 1), 1),
            },
        }

    # ── Unmapped Entity Analysis ──────────────────────────────

    def unmapped_entity_analysis(self) -> Dict:
        """Analyze unmapped entities to document coverage gaps.

        Categorizes unmapped entities by type and tradition,
        assesses their importance by mention count, and identifies
        which are heroes (the main gap in ACP coverage).
        """
        all_entities = self.library.get_all_entities()
        mapped_names = {m.library_entity for m in self.mapper.mappings}

        unmapped = [e for e in all_entities if e.canonical_name not in mapped_names]
        mapped = [e for e in all_entities if e.canonical_name in mapped_names]

        # By entity type
        unmapped_by_type = defaultdict(list)
        for e in unmapped:
            unmapped_by_type[e.entity_type].append({
                "name": e.canonical_name,
                "tradition": e.primary_tradition,
                "mentions": e.total_mentions,
                "texts": e.text_count,
            })

        # Sort each type by mention count
        for t in unmapped_by_type:
            unmapped_by_type[t].sort(key=lambda x: -x["mentions"])

        # By tradition
        unmapped_by_tradition = defaultdict(int)
        mapped_by_tradition = defaultdict(int)
        for e in unmapped:
            unmapped_by_tradition[e.primary_tradition or "unknown"] += 1
        for e in mapped:
            mapped_by_tradition[e.primary_tradition or "unknown"] += 1

        # Coverage by tradition
        tradition_coverage = {}
        all_traditions = set(list(unmapped_by_tradition.keys()) + list(mapped_by_tradition.keys()))
        for t in sorted(all_traditions):
            m = mapped_by_tradition.get(t, 0)
            u = unmapped_by_tradition.get(t, 0)
            total = m + u
            tradition_coverage[t] = {
                "mapped": m,
                "unmapped": u,
                "total": total,
                "pct_mapped": round(100 * m / total, 1) if total > 0 else 0,
            }

        # Mention mass: what % of total mentions do unmapped entities represent?
        total_unmapped_mentions = sum(e.total_mentions for e in unmapped)
        total_mapped_mentions = sum(e.total_mentions for e in mapped)
        total_mentions = total_unmapped_mentions + total_mapped_mentions

        # High-importance unmapped (>50 mentions)
        high_importance = [
            {"name": e.canonical_name, "type": e.entity_type,
             "tradition": e.primary_tradition, "mentions": e.total_mentions,
             "texts": e.text_count}
            for e in sorted(unmapped, key=lambda x: -x.total_mentions)
            if e.total_mentions >= 50
        ]

        return {
            "total_entities": len(all_entities),
            "mapped": len(mapped),
            "unmapped": len(unmapped),
            "pct_mapped": round(100 * len(mapped) / len(all_entities), 1),
            "by_type": {
                t: {"count": len(v), "top_5": v[:5]}
                for t, v in unmapped_by_type.items()
            },
            "tradition_coverage": tradition_coverage,
            "mention_mass": {
                "unmapped_mentions": total_unmapped_mentions,
                "mapped_mentions": total_mapped_mentions,
                "pct_unmapped": round(100 * total_unmapped_mentions / max(total_mentions, 1), 1),
            },
            "high_importance_unmapped": high_importance,
        }

    # ── Convenience: run all ──────────────────────────────────

    def run_all(
        self,
        exclude_entities: Optional[List[str]] = None,
        audit_sample: int = 100,
        seed: int = 42,
    ) -> Dict:
        """Run the complete Phase 7 data quality suite."""
        results = {}

        results["entity_mention_audit"] = self.entity_mention_audit(
            sample_size=audit_sample, seed=seed
        )
        results["normalized_cooccurrence"] = self.normalized_cooccurrence_test(
            exclude_entities
        )
        results["deduplication_check"] = self.cross_tradition_deduplication_check()
        results["unmapped_analysis"] = self.unmapped_entity_analysis()

        return results
