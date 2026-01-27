"""Phase 6: Alternative distance metrics and hypothesis tests.

Tests whether different ways of measuring ACP distance or co-occurrence
improve predictive power. Answers: is Euclidean the right metric?
Which axes carry signal? Does motif overlap predict better?
"""
import numpy as np
from scipy.stats import spearmanr, pearsonr
from scipy.spatial.distance import cosine as cosine_dist
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from integration.acp_loader import ACPLoader, AXES
from integration.library_loader import LibraryLoader
from integration.entity_mapper import EntityMapper


class AlternativeMetrics:
    def __init__(self, acp: ACPLoader, library: LibraryLoader, mapper: EntityMapper):
        self.acp = acp
        self.library = library
        self.mapper = mapper

    def _get_valid_mappings(self, exclude_entities: Optional[List[str]] = None):
        exclude = set(exclude_entities or [])
        return [
            m for m in self.mapper.mappings
            if m.library_entity not in exclude
            and self.acp.get_coordinates(m.acp_archetype_id) is not None
        ]

    def _get_cooccurrence_array(self, valid_mappings) -> np.ndarray:
        """Pre-compute all pairwise co-occurrences."""
        n = len(valid_mappings)
        coocc = []
        for i in range(n):
            for j in range(i + 1, n):
                c = self.library.get_entity_cooccurrence(
                    valid_mappings[i].library_entity,
                    valid_mappings[j].library_entity,
                )
                coocc.append(c)
        return np.array(coocc)

    # ── Cosine Similarity ─────────────────────────────────────

    def cosine_similarity_test(
        self, exclude_entities: Optional[List[str]] = None
    ) -> Dict:
        """Test cosine distance (angular) instead of Euclidean.

        Cosine distance measures angle between coordinate vectors,
        ignoring magnitude. If ACP archetypes' directions matter more
        than their positions, cosine should outperform Euclidean.
        """
        valid = self._get_valid_mappings(exclude_entities)
        n = len(valid)
        coocc_array = self._get_cooccurrence_array(valid)

        euclidean_dists = []
        cosine_dists = []

        for i in range(n):
            c1 = self.acp.get_coordinates(valid[i].acp_archetype_id)
            for j in range(i + 1, n):
                c2 = self.acp.get_coordinates(valid[j].acp_archetype_id)
                euclidean_dists.append(float(np.linalg.norm(c1 - c2)))
                # scipy cosine_dist returns 1 - cosine_similarity
                cosine_dists.append(float(cosine_dist(c1, c2)))

        euc_arr = np.array(euclidean_dists)
        cos_arr = np.array(cosine_dists)

        if len(euc_arr) < 10:
            return {"error": "Insufficient pairs"}

        euc_sr, euc_sp = spearmanr(euc_arr, coocc_array)
        cos_sr, cos_sp = spearmanr(cos_arr, coocc_array)

        return {
            "n_pairs": len(euc_arr),
            "euclidean": {
                "spearman_r": round(float(euc_sr), 4),
                "spearman_p": round(float(euc_sp), 6),
            },
            "cosine": {
                "spearman_r": round(float(cos_sr), 4),
                "spearman_p": round(float(cos_sp), 6),
            },
            "winner": "cosine" if abs(cos_sr) > abs(euc_sr) else "euclidean",
            "improvement": round(abs(cos_sr) - abs(euc_sr), 4),
        }

    # ── Per-Axis Correlation ──────────────────────────────────

    def per_axis_correlation(
        self, exclude_entities: Optional[List[str]] = None
    ) -> Dict:
        """Test which individual axes predict co-occurrence.

        For each axis, compute |diff| on that axis alone vs co-occurrence.
        Reveals which dimensions carry signal and which are noise.
        """
        valid = self._get_valid_mappings(exclude_entities)
        n = len(valid)
        coocc_array = self._get_cooccurrence_array(valid)

        # Compute per-axis absolute differences
        axis_diffs = {axis: [] for axis in AXES}

        for i in range(n):
            c1 = self.acp.get_coordinates(valid[i].acp_archetype_id)
            for j in range(i + 1, n):
                c2 = self.acp.get_coordinates(valid[j].acp_archetype_id)
                for k, axis in enumerate(AXES):
                    axis_diffs[axis].append(abs(float(c1[k] - c2[k])))

        results = {}
        for axis in AXES:
            diffs = np.array(axis_diffs[axis])
            if len(set(diffs)) < 2:
                results[axis] = {"note": "No variance"}
                continue
            sr, sp = spearmanr(diffs, coocc_array)
            results[axis] = {
                "spearman_r": round(float(sr), 4),
                "spearman_p": round(float(sp), 6),
                "mean_diff": round(float(diffs.mean()), 4),
            }

        # Rank axes by predictive power
        ranked = sorted(
            [(a, d) for a, d in results.items() if "spearman_r" in d],
            key=lambda x: abs(x[1]["spearman_r"]),
            reverse=True,
        )

        return {
            "per_axis": results,
            "ranking": [
                {"axis": a, "spearman_r": d["spearman_r"], "spearman_p": d["spearman_p"]}
                for a, d in ranked
            ],
            "strongest_axis": ranked[0][0] if ranked else None,
            "weakest_axis": ranked[-1][0] if ranked else None,
        }

    # ── Axis-Weighted Distance ────────────────────────────────

    def axis_weighted_distance_test(
        self, exclude_entities: Optional[List[str]] = None
    ) -> Dict:
        """Weight axes by their individual predictive power, then recompute distance.

        Uses per-axis |r| as weights. If some axes carry more signal,
        weighting should improve overall correlation.
        """
        valid = self._get_valid_mappings(exclude_entities)
        n = len(valid)
        coocc_array = self._get_cooccurrence_array(valid)

        # First get per-axis correlations to use as weights
        per_axis = self.per_axis_correlation(exclude_entities)
        weights = np.array([
            abs(per_axis["per_axis"].get(axis, {}).get("spearman_r", 0))
            for axis in AXES
        ])

        # Normalize weights so they sum to len(AXES) (preserves scale)
        weight_sum = weights.sum()
        if weight_sum > 0:
            weights = weights * len(AXES) / weight_sum
        else:
            weights = np.ones(len(AXES))

        # Compute weighted Euclidean distances
        weighted_dists = []
        unweighted_dists = []

        for i in range(n):
            c1 = self.acp.get_coordinates(valid[i].acp_archetype_id)
            for j in range(i + 1, n):
                c2 = self.acp.get_coordinates(valid[j].acp_archetype_id)
                diff = c1 - c2
                weighted_dists.append(float(np.sqrt(np.sum(weights * diff ** 2))))
                unweighted_dists.append(float(np.linalg.norm(diff)))

        w_arr = np.array(weighted_dists)
        u_arr = np.array(unweighted_dists)

        if len(w_arr) < 10:
            return {"error": "Insufficient pairs"}

        w_sr, w_sp = spearmanr(w_arr, coocc_array)
        u_sr, u_sp = spearmanr(u_arr, coocc_array)

        return {
            "n_pairs": len(w_arr),
            "weights": {axis: round(float(w), 4) for axis, w in zip(AXES, weights)},
            "weighted": {
                "spearman_r": round(float(w_sr), 4),
                "spearman_p": round(float(w_sp), 6),
            },
            "unweighted": {
                "spearman_r": round(float(u_sr), 4),
                "spearman_p": round(float(u_sp), 6),
            },
            "winner": "weighted" if abs(w_sr) > abs(u_sr) else "unweighted",
            "improvement": round(abs(w_sr) - abs(u_sr), 4),
        }

    # ── Mantel Test ───────────────────────────────────────────

    def mantel_test(
        self,
        n_permutations: int = 1000,
        exclude_entities: Optional[List[str]] = None,
        seed: int = 42,
    ) -> Dict:
        """Mantel test: proper matrix-level correlation for distance matrices.

        Computes Pearson correlation between the ACP distance matrix and
        co-occurrence matrix, then permutes rows/columns to get null distribution.
        More appropriate than pairwise Spearman for spatial data.
        """
        rng = np.random.default_rng(seed)
        valid = self._get_valid_mappings(exclude_entities)
        n = len(valid)

        if n < 5:
            return {"error": f"Insufficient entities ({n}) for Mantel test"}

        # Build distance and co-occurrence matrices
        dist_matrix = np.zeros((n, n))
        coocc_matrix = np.zeros((n, n))

        for i in range(n):
            c1 = self.acp.get_coordinates(valid[i].acp_archetype_id)
            for j in range(i + 1, n):
                c2 = self.acp.get_coordinates(valid[j].acp_archetype_id)
                d = float(np.linalg.norm(c1 - c2))
                c = self.library.get_entity_cooccurrence(
                    valid[i].library_entity, valid[j].library_entity
                )
                dist_matrix[i, j] = d
                dist_matrix[j, i] = d
                coocc_matrix[i, j] = c
                coocc_matrix[j, i] = c

        # Extract upper triangles as flat arrays
        tri_idx = np.triu_indices(n, k=1)
        dist_flat = dist_matrix[tri_idx]
        coocc_flat = coocc_matrix[tri_idx]

        # Observed Pearson correlation
        observed_r, observed_p = pearsonr(dist_flat, coocc_flat)

        # Permutation test: shuffle row/column labels of one matrix
        null_rs = []
        for _ in range(n_permutations):
            perm = rng.permutation(n)
            perm_dist = dist_matrix[np.ix_(perm, perm)]
            perm_flat = perm_dist[tri_idx]
            r, _ = pearsonr(perm_flat, coocc_flat)
            null_rs.append(float(r))

        null_arr = np.array(null_rs)
        empirical_p = float(np.mean(null_arr <= observed_r))

        return {
            "n_entities": n,
            "n_pairs": len(dist_flat),
            "observed_pearson_r": round(float(observed_r), 4),
            "observed_pearson_p": round(float(observed_p), 6),
            "n_permutations": n_permutations,
            "empirical_p_value": round(empirical_p, 4),
            "null_distribution": {
                "mean": round(float(null_arr.mean()), 4),
                "std": round(float(null_arr.std()), 4),
                "percentile_5": round(float(np.percentile(null_arr, 5)), 4),
                "percentile_95": round(float(np.percentile(null_arr, 95)), 4),
            },
        }

    # ── Motif-Mediated Similarity ─────────────────────────────

    def motif_similarity_test(
        self, exclude_entities: Optional[List[str]] = None
    ) -> Dict:
        """Test if shared Thompson motifs predict ACP distance.

        For each entity pair, compute Jaccard similarity of their motif sets.
        Entities sharing many motifs should be closer in ACP space.
        """
        valid = self._get_valid_mappings(exclude_entities)
        n = len(valid)

        # Get motif sets for each entity
        all_motif_codes = self.library.get_all_motif_codes()
        entity_motifs = {}
        for m in valid:
            motifs = set()
            for code in all_motif_codes:
                entities_for_motif = self.library.get_motif_entities(code)
                if m.library_entity in entities_for_motif:
                    motifs.add(code)
            entity_motifs[m.library_entity] = motifs

        # Compute Jaccard similarity and ACP distance for all pairs
        distances = []
        jaccard_sims = []
        coocc_array = []

        for i in range(n):
            m1 = valid[i]
            s1 = entity_motifs.get(m1.library_entity, set())
            c1 = self.acp.get_coordinates(m1.acp_archetype_id)
            for j in range(i + 1, n):
                m2 = valid[j]
                s2 = entity_motifs.get(m2.library_entity, set())
                c2 = self.acp.get_coordinates(m2.acp_archetype_id)

                # Jaccard
                union = len(s1 | s2)
                intersection = len(s1 & s2)
                jaccard = intersection / union if union > 0 else 0

                dist = float(np.linalg.norm(c1 - c2))
                coocc = self.library.get_entity_cooccurrence(
                    m1.library_entity, m2.library_entity
                )

                distances.append(dist)
                jaccard_sims.append(jaccard)
                coocc_array.append(coocc)

        dist_arr = np.array(distances)
        jac_arr = np.array(jaccard_sims)
        coocc_arr = np.array(coocc_array)

        if len(dist_arr) < 10:
            return {"error": "Insufficient pairs"}

        # Distance vs co-occurrence (baseline)
        dist_coocc_r, dist_coocc_p = spearmanr(dist_arr, coocc_arr)

        # Jaccard vs co-occurrence (motif-mediated)
        jac_coocc_r, jac_coocc_p = spearmanr(jac_arr, coocc_arr)

        # Distance vs Jaccard (does ACP distance predict motif overlap?)
        dist_jac_r, dist_jac_p = spearmanr(dist_arr, jac_arr)

        # Pairs with non-zero Jaccard
        nonzero_jac = jac_arr > 0
        n_with_shared_motifs = int(nonzero_jac.sum())

        return {
            "n_pairs": len(dist_arr),
            "pairs_with_shared_motifs": n_with_shared_motifs,
            "mean_jaccard": round(float(jac_arr.mean()), 4),
            "max_jaccard": round(float(jac_arr.max()), 4),
            "distance_vs_cooccurrence": {
                "spearman_r": round(float(dist_coocc_r), 4),
                "spearman_p": round(float(dist_coocc_p), 6),
            },
            "jaccard_vs_cooccurrence": {
                "spearman_r": round(float(jac_coocc_r), 4),
                "spearman_p": round(float(jac_coocc_p), 6),
            },
            "distance_vs_jaccard": {
                "spearman_r": round(float(dist_jac_r), 4),
                "spearman_p": round(float(dist_jac_p), 6),
            },
            "better_predictor_of_cooccurrence": (
                "motif_jaccard" if abs(jac_coocc_r) > abs(dist_coocc_r) else "acp_distance"
            ),
        }

    # ── Convenience: run all ──────────────────────────────────

    def run_all(
        self,
        exclude_entities: Optional[List[str]] = None,
        n_permutations: int = 1000,
        seed: int = 42,
    ) -> Dict:
        """Run the complete Phase 6 alternative metrics suite."""
        results = {}

        results["cosine_similarity"] = self.cosine_similarity_test(exclude_entities)
        results["per_axis_correlation"] = self.per_axis_correlation(exclude_entities)
        results["axis_weighted_distance"] = self.axis_weighted_distance_test(exclude_entities)
        results["mantel_test"] = self.mantel_test(
            n_permutations=n_permutations, exclude_entities=exclude_entities, seed=seed
        )
        results["motif_similarity"] = self.motif_similarity_test(exclude_entities)

        return results
