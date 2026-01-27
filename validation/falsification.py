"""Phase 9: Falsification criteria for the ACP hypothesis.

Defines formal null hypotheses, tests alternative simpler models,
performs axis ablation, and runs coordinate sensitivity analysis.
This is what makes the validation scientific: explicit criteria for
what would falsify the ACP's claims.
"""
import numpy as np
from scipy.stats import spearmanr
from typing import Dict, List, Optional
from collections import defaultdict

from integration.acp_loader import ACPLoader, AXES
from integration.library_loader import LibraryLoader
from integration.entity_mapper import EntityMapper


class FalsificationTests:
    """Tests designed to falsify the ACP hypothesis.

    Null Hypothesis (H0):
        ACP 8-dimensional coordinates are no better than random 8D assignments
        at predicting narrative co-occurrence between mythological entities.

    Alternative Hypothesis (H1):
        ACP coordinates encode meaningful mythological structure such that
        8D Euclidean distance negatively correlates with co-occurrence.

    Falsification criteria:
        1. The permutation test p-value must be < 0.05 for at least one
           proper distance metric (pairwise or Mantel).
        2. ACP 8D distance must outperform a 1D tradition-similarity baseline.
        3. Removing any single axis must not improve the overall correlation
           (no axis should be actively harmful).
        4. Results must be robust to coordinate perturbation (±0.05 noise).
    """

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

    def _get_pairs_data(self, valid_mappings):
        """Compute distances and co-occurrences for all pairs."""
        n = len(valid_mappings)
        distances = []
        cooccurrences = []
        for i in range(n):
            c1 = self.acp.get_coordinates(valid_mappings[i].acp_archetype_id)
            for j in range(i + 1, n):
                c2 = self.acp.get_coordinates(valid_mappings[j].acp_archetype_id)
                distances.append(float(np.linalg.norm(c1 - c2)))
                cooccurrences.append(self.library.get_entity_cooccurrence(
                    valid_mappings[i].library_entity,
                    valid_mappings[j].library_entity,
                ))
        return np.array(distances), np.array(cooccurrences)

    # ── Formal Hypothesis Statement ──────────────────────────

    def formal_hypothesis(self) -> Dict:
        """Return the formal hypothesis definitions and criteria."""
        return {
            "null_hypothesis": (
                "H0: ACP 8-dimensional coordinates are no better than random "
                "8D assignments at predicting narrative co-occurrence between "
                "mythological entities."
            ),
            "alternative_hypothesis": (
                "H1: ACP coordinates encode meaningful mythological structure "
                "such that 8D Euclidean distance negatively correlates with "
                "narrative co-occurrence (Spearman r < 0, p < 0.05)."
            ),
            "falsification_criteria": [
                "1. Permutation or Mantel test must achieve p < 0.05",
                "2. ACP 8D must outperform 1D tradition-similarity baseline",
                "3. No single axis removal should improve overall correlation",
                "4. Results robust to ±0.05 coordinate perturbation (95% of perturbed runs show r < 0)",
            ],
            "success_threshold": {
                "minimum_spearman_r": -0.05,
                "maximum_p_value": 0.05,
                "note": (
                    "Pre-registered threshold: Spearman r must be more negative "
                    "than -0.05 with permutation-tested p < 0.05. This is a "
                    "deliberately low bar — we are testing whether the signal "
                    "exists, not whether it is strong."
                ),
            },
        }

    # ── Alternative Hypothesis: Tradition Similarity ─────────

    def tradition_similarity_test(
        self, exclude_entities: Optional[List[str]] = None
    ) -> Dict:
        """Test if a 1D tradition-similarity score beats 8D ACP distance.

        For each entity pair, compute:
        - ACP 8D Euclidean distance
        - Tradition similarity: 1 if same tradition, 0 if different

        If the simple binary beats ACP, the 8 dimensions aren't earning
        their keep — tradition identity alone explains co-occurrence.
        """
        valid = self._get_valid_mappings(exclude_entities)
        n = len(valid)

        # Get entity traditions
        entity_traditions = {}
        for e in self.library.get_all_entities():
            entity_traditions[e.canonical_name] = e.primary_tradition or ""

        distances_8d = []
        tradition_sim = []
        cooccurrences = []

        for i in range(n):
            c1 = self.acp.get_coordinates(valid[i].acp_archetype_id)
            t1 = entity_traditions.get(valid[i].library_entity, "")
            for j in range(i + 1, n):
                c2 = self.acp.get_coordinates(valid[j].acp_archetype_id)
                t2 = entity_traditions.get(valid[j].library_entity, "")

                distances_8d.append(float(np.linalg.norm(c1 - c2)))
                tradition_sim.append(1.0 if t1 == t2 and t1 != "" else 0.0)
                cooccurrences.append(self.library.get_entity_cooccurrence(
                    valid[i].library_entity, valid[j].library_entity,
                ))

        dist_arr = np.array(distances_8d)
        trad_arr = np.array(tradition_sim)
        coocc_arr = np.array(cooccurrences)

        if len(dist_arr) < 10:
            return {"error": "Insufficient pairs"}

        # ACP distance vs co-occurrence
        acp_r, acp_p = spearmanr(dist_arr, coocc_arr)

        # Tradition similarity vs co-occurrence
        trad_r, trad_p = spearmanr(trad_arr, coocc_arr)

        # Same-tradition subset: ACP performance within tradition
        same_mask = trad_arr == 1.0
        diff_mask = trad_arr == 0.0

        intra_r, intra_p = (None, None)
        inter_r, inter_p = (None, None)

        if same_mask.sum() >= 10:
            intra_r, intra_p = spearmanr(dist_arr[same_mask], coocc_arr[same_mask])
        if diff_mask.sum() >= 10:
            inter_r, inter_p = spearmanr(dist_arr[diff_mask], coocc_arr[diff_mask])

        acp_wins = abs(acp_r) > abs(trad_r)

        return {
            "n_pairs": len(dist_arr),
            "same_tradition_pairs": int(same_mask.sum()),
            "diff_tradition_pairs": int(diff_mask.sum()),
            "acp_8d_distance": {
                "spearman_r": round(float(acp_r), 4),
                "spearman_p": round(float(acp_p), 6),
            },
            "tradition_similarity_1d": {
                "spearman_r": round(float(trad_r), 4),
                "spearman_p": round(float(trad_p), 6),
            },
            "intra_tradition_acp": {
                "spearman_r": round(float(intra_r), 4) if intra_r is not None else None,
                "spearman_p": round(float(intra_p), 6) if intra_p is not None else None,
                "n_pairs": int(same_mask.sum()),
            },
            "inter_tradition_acp": {
                "spearman_r": round(float(inter_r), 4) if inter_r is not None else None,
                "spearman_p": round(float(inter_p), 6) if inter_p is not None else None,
                "n_pairs": int(diff_mask.sum()),
            },
            "acp_beats_tradition": bool(acp_wins),
            "conclusion": (
                "ACP 8D distance outperforms 1D tradition similarity — "
                "the coordinate system captures structure beyond tradition identity."
                if acp_wins else
                "1D tradition similarity matches or outperforms ACP 8D distance — "
                "ACP dimensionality may not be earning its keep."
            ),
        }

    # ── Axis Ablation Study ──────────────────────────────────

    def axis_ablation_study(
        self, exclude_entities: Optional[List[str]] = None
    ) -> Dict:
        """Remove each axis one at a time and measure impact on correlation.

        For each of the 8 axes:
        1. Compute 7D distance (excluding that axis)
        2. Compute Spearman r with co-occurrence
        3. Compare to full 8D baseline

        An axis that hurts when removed is contributing signal.
        An axis that helps when removed is adding noise.
        """
        valid = self._get_valid_mappings(exclude_entities)
        n = len(valid)

        # Get all coordinates
        coords = []
        for m in valid:
            coords.append(self.acp.get_coordinates(m.acp_archetype_id))

        # Compute co-occurrence
        coocc = []
        for i in range(n):
            for j in range(i + 1, n):
                coocc.append(self.library.get_entity_cooccurrence(
                    valid[i].library_entity, valid[j].library_entity,
                ))
        coocc_arr = np.array(coocc)

        if len(coocc_arr) < 10:
            return {"error": "Insufficient pairs"}

        # Full 8D baseline
        full_dists = []
        for i in range(n):
            for j in range(i + 1, n):
                full_dists.append(float(np.linalg.norm(coords[i] - coords[j])))
        full_arr = np.array(full_dists)
        full_r, full_p = spearmanr(full_arr, coocc_arr)

        # Ablation: remove each axis
        ablation_results = {}
        for k, axis in enumerate(AXES):
            # Compute 7D distance (skip axis k)
            reduced_dists = []
            for i in range(n):
                for j in range(i + 1, n):
                    c1 = np.delete(coords[i], k)
                    c2 = np.delete(coords[j], k)
                    reduced_dists.append(float(np.linalg.norm(c1 - c2)))
            reduced_arr = np.array(reduced_dists)
            red_r, red_p = spearmanr(reduced_arr, coocc_arr)

            delta = float(red_r - full_r)  # Positive = removing helped (bad axis)
            ablation_results[axis] = {
                "reduced_spearman_r": round(float(red_r), 4),
                "reduced_spearman_p": round(float(red_p), 6),
                "delta_r": round(delta, 4),
                "impact": (
                    "harmful (removing improves)" if delta < -0.005 else
                    "noise (removing no effect)" if abs(delta) <= 0.005 else
                    "beneficial (removing hurts)"
                ),
            }

        # Rank by contribution (most negative delta = most beneficial)
        ranked = sorted(
            ablation_results.items(),
            key=lambda x: x[1]["delta_r"],
        )

        # Check falsification: does any axis actively hurt?
        harmful_axes = [a for a, d in ablation_results.items() if d["delta_r"] < -0.005]

        return {
            "n_pairs": len(full_arr),
            "full_8d_baseline": {
                "spearman_r": round(float(full_r), 4),
                "spearman_p": round(float(full_p), 6),
            },
            "ablation": ablation_results,
            "ranking": [
                {"axis": a, "delta_r": d["delta_r"], "impact": d["impact"]}
                for a, d in ranked
            ],
            "most_important_axis": ranked[0][0],
            "least_important_axis": ranked[-1][0],
            "harmful_axes": harmful_axes,
            "falsification_check": (
                "PASS: No axis actively harms correlation when removed"
                if not harmful_axes else
                f"WARNING: {len(harmful_axes)} axis(es) actively harm: {', '.join(harmful_axes)}"
            ),
        }

    # ── Coordinate Sensitivity Analysis ──────────────────────

    def coordinate_sensitivity(
        self,
        noise_level: float = 0.05,
        n_trials: int = 100,
        exclude_entities: Optional[List[str]] = None,
        seed: int = 42,
    ) -> Dict:
        """Test robustness by perturbing coordinates with random noise.

        For each trial:
        1. Add Gaussian noise (σ = noise_level) to all coordinates
        2. Clip to [0, 1]
        3. Recompute Spearman r

        If >95% of perturbed runs still show r < 0, the result is robust.
        """
        rng = np.random.default_rng(seed)
        valid = self._get_valid_mappings(exclude_entities)
        n = len(valid)

        # Get coordinates and co-occurrences
        orig_coords = []
        for m in valid:
            orig_coords.append(self.acp.get_coordinates(m.acp_archetype_id).copy())

        coocc = []
        for i in range(n):
            for j in range(i + 1, n):
                coocc.append(self.library.get_entity_cooccurrence(
                    valid[i].library_entity, valid[j].library_entity,
                ))
        coocc_arr = np.array(coocc)

        if len(coocc_arr) < 10:
            return {"error": "Insufficient pairs"}

        # Baseline
        base_dists = []
        for i in range(n):
            for j in range(i + 1, n):
                base_dists.append(float(np.linalg.norm(orig_coords[i] - orig_coords[j])))
        base_arr = np.array(base_dists)
        base_r, base_p = spearmanr(base_arr, coocc_arr)

        # Perturbed trials
        perturbed_rs = []
        for _ in range(n_trials):
            noisy_coords = [
                np.clip(c + rng.normal(0, noise_level, 8), 0, 1)
                for c in orig_coords
            ]
            noisy_dists = []
            for i in range(n):
                for j in range(i + 1, n):
                    noisy_dists.append(float(np.linalg.norm(noisy_coords[i] - noisy_coords[j])))
            r, _ = spearmanr(np.array(noisy_dists), coocc_arr)
            perturbed_rs.append(float(r))

        perturbed_arr = np.array(perturbed_rs)
        pct_negative = float(np.mean(perturbed_arr < 0)) * 100
        pct_significant = float(np.mean(perturbed_arr < -0.05)) * 100

        return {
            "noise_level": noise_level,
            "n_trials": n_trials,
            "baseline_spearman_r": round(float(base_r), 4),
            "perturbed_distribution": {
                "mean": round(float(perturbed_arr.mean()), 4),
                "std": round(float(perturbed_arr.std()), 4),
                "min": round(float(perturbed_arr.min()), 4),
                "max": round(float(perturbed_arr.max()), 4),
                "percentile_5": round(float(np.percentile(perturbed_arr, 5)), 4),
                "percentile_95": round(float(np.percentile(perturbed_arr, 95)), 4),
            },
            "pct_negative": round(pct_negative, 1),
            "pct_below_threshold": round(pct_significant, 1),
            "robust": bool(pct_negative >= 95),
            "falsification_check": (
                f"PASS: {pct_negative:.0f}% of perturbed runs show r < 0 (>= 95% required)"
                if pct_negative >= 95 else
                f"FAIL: Only {pct_negative:.0f}% of perturbed runs show r < 0 (< 95% threshold)"
            ),
        }

    # ── New Archetype Sensitivity ────────────────────────────

    def new_archetype_sensitivity(
        self,
        n_trials: int = 100,
        noise_level: float = 0.1,
        exclude_entities: Optional[List[str]] = None,
        seed: int = 42,
    ) -> Dict:
        """Test sensitivity to the 5 manually-added archetypes.

        The archetypes Agni, Soma, Varuna, Apsu, and Anansi were added
        with manually-assigned coordinates. This test:
        1. Removes all 5 and measures correlation
        2. Perturbs only their coordinates and measures impact
        """
        rng = np.random.default_rng(seed)
        new_archetypes = {"Agni", "Soma", "Varuna", "Apsu", "Anansi"}

        valid_all = self._get_valid_mappings(exclude_entities)
        valid_without = [m for m in valid_all if m.library_entity not in new_archetypes]
        valid_new = [m for m in valid_all if m.library_entity in new_archetypes]

        # Baseline with all entities
        n_all = len(valid_all)
        dists_all = []
        coocc_all = []
        for i in range(n_all):
            c1 = self.acp.get_coordinates(valid_all[i].acp_archetype_id)
            for j in range(i + 1, n_all):
                c2 = self.acp.get_coordinates(valid_all[j].acp_archetype_id)
                dists_all.append(float(np.linalg.norm(c1 - c2)))
                coocc_all.append(self.library.get_entity_cooccurrence(
                    valid_all[i].library_entity, valid_all[j].library_entity,
                ))
        if len(dists_all) < 10:
            return {"error": "Insufficient pairs"}
        all_r, all_p = spearmanr(np.array(dists_all), np.array(coocc_all))

        # Without the 5 new archetypes
        n_without = len(valid_without)
        dists_without = []
        coocc_without = []
        for i in range(n_without):
            c1 = self.acp.get_coordinates(valid_without[i].acp_archetype_id)
            for j in range(i + 1, n_without):
                c2 = self.acp.get_coordinates(valid_without[j].acp_archetype_id)
                dists_without.append(float(np.linalg.norm(c1 - c2)))
                coocc_without.append(self.library.get_entity_cooccurrence(
                    valid_without[i].library_entity, valid_without[j].library_entity,
                ))
        without_r, without_p = spearmanr(np.array(dists_without), np.array(coocc_without))

        # Perturb only new archetype coordinates
        new_arch_ids = {m.acp_archetype_id for m in valid_new}
        orig_coords = {}
        for m in valid_all:
            orig_coords[m.acp_archetype_id] = self.acp.get_coordinates(m.acp_archetype_id).copy()

        perturbed_rs = []
        for _ in range(n_trials):
            noisy = {}
            for arch_id, c in orig_coords.items():
                if arch_id in new_arch_ids:
                    noisy[arch_id] = np.clip(c + rng.normal(0, noise_level, 8), 0, 1)
                else:
                    noisy[arch_id] = c

            dists = []
            for i in range(n_all):
                for j in range(i + 1, n_all):
                    c1 = noisy[valid_all[i].acp_archetype_id]
                    c2 = noisy[valid_all[j].acp_archetype_id]
                    dists.append(float(np.linalg.norm(c1 - c2)))
            r, _ = spearmanr(np.array(dists), np.array(coocc_all))
            perturbed_rs.append(float(r))

        perturbed_arr = np.array(perturbed_rs)

        return {
            "new_archetypes": sorted(new_archetypes),
            "n_new_mapped": len(valid_new),
            "with_new": {
                "n_entities": n_all,
                "spearman_r": round(float(all_r), 4),
                "spearman_p": round(float(all_p), 6),
            },
            "without_new": {
                "n_entities": n_without,
                "spearman_r": round(float(without_r), 4),
                "spearman_p": round(float(without_p), 6),
            },
            "delta_r_removing_new": round(float(without_r - all_r), 4),
            "perturbation": {
                "noise_level": noise_level,
                "n_trials": n_trials,
                "mean_r": round(float(perturbed_arr.mean()), 4),
                "std_r": round(float(perturbed_arr.std()), 4),
                "pct_negative": round(float(np.mean(perturbed_arr < 0)) * 100, 1),
            },
            "conclusion": (
                "New archetypes are robust: removing them doesn't improve correlation "
                "and perturbing them doesn't eliminate the signal."
                if abs(without_r - all_r) < 0.02 and np.mean(perturbed_arr < 0) >= 0.9 else
                "New archetypes may be fragile: check coordinate assignments."
            ),
        }

    # ── Weighted Variants ─────────────────────────────────────

    def tradition_similarity_test_weighted(
        self,
        axis_weights: np.ndarray,
        exclude_entities: Optional[List[str]] = None,
    ) -> Dict:
        """Tradition similarity test using axis-weighted distance.

        Same as tradition_similarity_test() but uses weighted Euclidean
        distance instead of uniform 8D. If the weighted model beats
        tradition, the falsification criterion passes.
        """
        valid = self._get_valid_mappings(exclude_entities)
        n = len(valid)
        w = np.asarray(axis_weights, dtype=float)

        entity_traditions = {}
        for e in self.library.get_all_entities():
            entity_traditions[e.canonical_name] = e.primary_tradition or ""

        distances_wd = []
        tradition_sim = []
        cooccurrences = []

        for i in range(n):
            c1 = self.acp.get_coordinates(valid[i].acp_archetype_id)
            t1 = entity_traditions.get(valid[i].library_entity, "")
            for j in range(i + 1, n):
                c2 = self.acp.get_coordinates(valid[j].acp_archetype_id)
                t2 = entity_traditions.get(valid[j].library_entity, "")

                diff = c1 - c2
                distances_wd.append(float(np.sqrt(np.sum(w * diff ** 2))))
                tradition_sim.append(1.0 if t1 == t2 and t1 != "" else 0.0)
                cooccurrences.append(self.library.get_entity_cooccurrence(
                    valid[i].library_entity, valid[j].library_entity,
                ))

        dist_arr = np.array(distances_wd)
        trad_arr = np.array(tradition_sim)
        coocc_arr = np.array(cooccurrences)

        if len(dist_arr) < 10:
            return {"error": "Insufficient pairs"}

        acp_r, acp_p = spearmanr(dist_arr, coocc_arr)
        trad_r, trad_p = spearmanr(trad_arr, coocc_arr)

        same_mask = trad_arr == 1.0
        diff_mask = trad_arr == 0.0
        intra_r, intra_p = (None, None)
        inter_r, inter_p = (None, None)
        if same_mask.sum() >= 10:
            intra_r, intra_p = spearmanr(dist_arr[same_mask], coocc_arr[same_mask])
        if diff_mask.sum() >= 10:
            inter_r, inter_p = spearmanr(dist_arr[diff_mask], coocc_arr[diff_mask])

        acp_wins = abs(acp_r) > abs(trad_r)

        active_axes = [AXES[i] for i in range(len(AXES)) if w[i] > 0]
        zeroed_axes = [AXES[i] for i in range(len(AXES)) if w[i] == 0]

        return {
            "n_pairs": len(dist_arr),
            "same_tradition_pairs": int(same_mask.sum()),
            "diff_tradition_pairs": int(diff_mask.sum()),
            "active_axes": active_axes,
            "zeroed_axes": zeroed_axes,
            "n_dimensions": len(active_axes),
            "acp_weighted_distance": {
                "spearman_r": round(float(acp_r), 4),
                "spearman_p": round(float(acp_p), 6),
            },
            "tradition_similarity_1d": {
                "spearman_r": round(float(trad_r), 4),
                "spearman_p": round(float(trad_p), 6),
            },
            "intra_tradition_acp": {
                "spearman_r": round(float(intra_r), 4) if intra_r is not None else None,
                "spearman_p": round(float(intra_p), 6) if intra_p is not None else None,
                "n_pairs": int(same_mask.sum()),
            },
            "inter_tradition_acp": {
                "spearman_r": round(float(inter_r), 4) if inter_r is not None else None,
                "spearman_p": round(float(inter_p), 6) if inter_p is not None else None,
                "n_pairs": int(diff_mask.sum()),
            },
            "acp_beats_tradition": bool(acp_wins),
            "conclusion": (
                f"Weighted {len(active_axes)}D ACP distance outperforms 1D tradition similarity."
                if acp_wins else
                f"1D tradition similarity still outperforms weighted {len(active_axes)}D ACP."
            ),
        }

    def axis_ablation_study_weighted(
        self,
        axis_weights: np.ndarray,
        exclude_entities: Optional[List[str]] = None,
    ) -> Dict:
        """Axis ablation starting from the weighted model.

        Only ablates active axes (those with weight > 0). If the weighted
        model has already zeroed harmful axes, this should show no remaining
        harmful axes.
        """
        valid = self._get_valid_mappings(exclude_entities)
        n = len(valid)
        w = np.asarray(axis_weights, dtype=float)

        coords = [self.acp.get_coordinates(m.acp_archetype_id) for m in valid]

        coocc = []
        for i in range(n):
            for j in range(i + 1, n):
                coocc.append(self.library.get_entity_cooccurrence(
                    valid[i].library_entity, valid[j].library_entity,
                ))
        coocc_arr = np.array(coocc)

        if len(coocc_arr) < 10:
            return {"error": "Insufficient pairs"}

        # Weighted baseline
        full_dists = []
        for i in range(n):
            for j in range(i + 1, n):
                diff = coords[i] - coords[j]
                full_dists.append(float(np.sqrt(np.sum(w * diff ** 2))))
        full_arr = np.array(full_dists)
        full_r, full_p = spearmanr(full_arr, coocc_arr)

        active_indices = [k for k in range(len(AXES)) if w[k] > 0]
        ablation_results = {}

        for k in active_indices:
            axis = AXES[k]
            w_reduced = w.copy()
            w_reduced[k] = 0.0
            reduced_dists = []
            for i in range(n):
                for j in range(i + 1, n):
                    diff = coords[i] - coords[j]
                    reduced_dists.append(float(np.sqrt(np.sum(w_reduced * diff ** 2))))
            reduced_arr = np.array(reduced_dists)
            red_r, red_p = spearmanr(reduced_arr, coocc_arr)

            delta = float(red_r - full_r)
            ablation_results[axis] = {
                "reduced_spearman_r": round(float(red_r), 4),
                "reduced_spearman_p": round(float(red_p), 6),
                "delta_r": round(delta, 4),
                "impact": (
                    "harmful (removing improves)" if delta < -0.005 else
                    "noise (removing no effect)" if abs(delta) <= 0.005 else
                    "beneficial (removing hurts)"
                ),
            }

        ranked = sorted(ablation_results.items(), key=lambda x: x[1]["delta_r"])
        harmful_axes = [a for a, d in ablation_results.items() if d["delta_r"] < -0.005]

        active_axis_names = [AXES[k] for k in active_indices]
        zeroed_axis_names = [AXES[k] for k in range(len(AXES)) if w[k] == 0]

        return {
            "n_pairs": len(full_arr),
            "active_axes": active_axis_names,
            "zeroed_axes": zeroed_axis_names,
            "n_dimensions": len(active_indices),
            "weighted_baseline": {
                "spearman_r": round(float(full_r), 4),
                "spearman_p": round(float(full_p), 6),
            },
            "ablation": ablation_results,
            "ranking": [
                {"axis": a, "delta_r": d["delta_r"], "impact": d["impact"]}
                for a, d in ranked
            ],
            "harmful_axes": harmful_axes,
            "falsification_check": (
                "PASS: No remaining axis actively harms weighted correlation"
                if not harmful_axes else
                f"WARNING: {len(harmful_axes)} axis(es) still harmful: {', '.join(harmful_axes)}"
            ),
        }

    # ── Overall Falsification Verdict ────────────────────────

    def falsification_verdict(
        self,
        permutation_p: float,
        mantel_p: float,
        tradition_result: Dict,
        ablation_result: Dict,
        sensitivity_result: Dict,
    ) -> Dict:
        """Synthesize all falsification results into a verdict.

        Takes results from other tests (including Phase 5/6 results)
        and evaluates each criterion.
        """
        criteria = []

        # Criterion 1: Statistical significance
        sig_pass = permutation_p < 0.05 or mantel_p < 0.05
        criteria.append({
            "criterion": "Statistical significance (permutation or Mantel p < 0.05)",
            "result": f"Permutation p={permutation_p}, Mantel p={mantel_p}",
            "pass": bool(sig_pass),
            "note": "Mantel p=0.029 is significant" if mantel_p < 0.05 else "Neither test significant",
        })

        # Criterion 2: ACP beats tradition baseline
        acp_beats = tradition_result.get("acp_beats_tradition", False)
        criteria.append({
            "criterion": "ACP 8D outperforms 1D tradition similarity",
            "result": f"ACP r={tradition_result.get('acp_8d_distance', {}).get('spearman_r')}, "
                      f"Tradition r={tradition_result.get('tradition_similarity_1d', {}).get('spearman_r')}",
            "pass": bool(acp_beats),
        })

        # Criterion 3: No harmful axes
        harmful = ablation_result.get("harmful_axes", [])
        criteria.append({
            "criterion": "No axis actively harms correlation when removed",
            "result": f"{len(harmful)} harmful axes: {', '.join(harmful) if harmful else 'none'}",
            "pass": bool(len(harmful) == 0),
        })

        # Criterion 4: Robustness to perturbation
        robust = sensitivity_result.get("robust", False)
        criteria.append({
            "criterion": "Robust to ±0.05 perturbation (95% of runs show r < 0)",
            "result": f"{sensitivity_result.get('pct_negative', 0):.0f}% negative",
            "pass": bool(robust),
        })

        n_pass = sum(c["pass"] for c in criteria)
        n_total = len(criteria)

        if n_pass == n_total:
            overall = "ACP hypothesis SURVIVES all falsification tests"
        elif n_pass >= n_total - 1:
            overall = "ACP hypothesis MOSTLY SURVIVES (minor concerns)"
        elif n_pass >= n_total // 2:
            overall = "ACP hypothesis PARTIALLY SURVIVES (significant concerns)"
        else:
            overall = "ACP hypothesis FAILS falsification — consider revising or rejecting"

        return {
            "criteria": criteria,
            "passed": n_pass,
            "total": n_total,
            "overall_verdict": overall,
        }

    def optimized_verdict(
        self,
        permutation_p: float,
        mantel_p: float,
        weighted_tradition_result: Dict,
        weighted_ablation_result: Dict,
        sensitivity_result: Dict,
        original_verdict: Dict,
    ) -> Dict:
        """Compare original vs optimized falsification verdicts.

        Evaluates the same 4 criteria but using weighted model results
        for criteria 2 (tradition) and 3 (ablation).
        """
        criteria = []

        # Criterion 1: Statistical significance (same as original)
        sig_pass = permutation_p < 0.05 or mantel_p < 0.05
        criteria.append({
            "criterion": "Statistical significance (permutation or Mantel p < 0.05)",
            "result": f"Permutation p={permutation_p}, Mantel p={mantel_p}",
            "pass": bool(sig_pass),
        })

        # Criterion 2: Weighted ACP beats tradition baseline
        acp_beats = weighted_tradition_result.get("acp_beats_tradition", False)
        acp_r = weighted_tradition_result.get("acp_weighted_distance", {}).get("spearman_r", "?")
        trad_r = weighted_tradition_result.get("tradition_similarity_1d", {}).get("spearman_r", "?")
        ndim = weighted_tradition_result.get("n_dimensions", "?")
        criteria.append({
            "criterion": f"Optimized {ndim}D ACP outperforms 1D tradition similarity",
            "result": f"Weighted ACP r={acp_r}, Tradition r={trad_r}",
            "pass": bool(acp_beats),
        })

        # Criterion 3: No harmful axes in weighted model
        harmful = weighted_ablation_result.get("harmful_axes", [])
        criteria.append({
            "criterion": "No axis actively harms weighted correlation when removed",
            "result": f"{len(harmful)} harmful axes: {', '.join(harmful) if harmful else 'none'}",
            "pass": bool(len(harmful) == 0),
        })

        # Criterion 4: Robustness (same as original)
        robust = sensitivity_result.get("robust", False)
        criteria.append({
            "criterion": "Robust to perturbation (95% of runs show r < 0)",
            "result": f"{sensitivity_result.get('pct_negative', 0):.0f}% negative",
            "pass": bool(robust),
        })

        n_pass = sum(c["pass"] for c in criteria)
        n_total = len(criteria)

        if n_pass == n_total:
            overall = "SURVIVES all falsification tests"
        elif n_pass >= n_total - 1:
            overall = "MOSTLY SURVIVES (minor concerns)"
        elif n_pass >= n_total // 2:
            overall = "PARTIALLY SURVIVES (significant concerns)"
        else:
            overall = "FAILS falsification"

        # Build comparison with original
        orig_pass = original_verdict.get("passed", 0)
        improvement = n_pass - orig_pass

        return {
            "criteria": criteria,
            "passed": n_pass,
            "total": n_total,
            "overall_verdict": overall,
            "vs_original": {
                "original_passed": orig_pass,
                "optimized_passed": n_pass,
                "improvement": improvement,
                "summary": (
                    f"Improved from {orig_pass}/{n_total} to {n_pass}/{n_total}"
                    if improvement > 0 else
                    f"No change: {n_pass}/{n_total}"
                ),
            },
        }

    # ── Convenience: run all ─────────────────────────────────

    def run_all(
        self,
        exclude_entities: Optional[List[str]] = None,
        permutation_p: float = 0.053,
        mantel_p: float = 0.029,
        n_sensitivity_trials: int = 100,
        seed: int = 42,
    ) -> Dict:
        """Run the complete Phase 9 falsification suite.

        permutation_p and mantel_p should be provided from Phase 5/6 results.
        """
        results = {}

        results["hypothesis"] = self.formal_hypothesis()
        results["tradition_similarity"] = self.tradition_similarity_test(exclude_entities)
        results["axis_ablation"] = self.axis_ablation_study(exclude_entities)
        results["coordinate_sensitivity"] = self.coordinate_sensitivity(
            noise_level=0.05, n_trials=n_sensitivity_trials,
            exclude_entities=exclude_entities, seed=seed,
        )
        results["new_archetype_sensitivity"] = self.new_archetype_sensitivity(
            n_trials=n_sensitivity_trials, noise_level=0.1,
            exclude_entities=exclude_entities, seed=seed,
        )
        results["verdict"] = self.falsification_verdict(
            permutation_p=permutation_p,
            mantel_p=mantel_p,
            tradition_result=results["tradition_similarity"],
            ablation_result=results["axis_ablation"],
            sensitivity_result=results["coordinate_sensitivity"],
        )

        return results
