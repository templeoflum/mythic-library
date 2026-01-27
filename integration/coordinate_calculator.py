"""Weighted and reduced-dimension distance calculations for ACP coordinates.

Provides axis-weighted Euclidean distance, harmful axis removal,
and systematic dimensionality search (3D-7D) to find the optimal
axis subset for predicting narrative co-occurrence.
"""
import numpy as np
from itertools import combinations
from scipy.stats import spearmanr
from typing import Dict, List, Optional, Tuple

from integration.acp_loader import ACPLoader, AXES
from integration.library_loader import LibraryLoader
from integration.entity_mapper import EntityMapper


class WeightedDistanceCalculator:
    """Compute axis-weighted and reduced-dimension ACP distances."""

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
        n = len(valid_mappings)
        coocc = []
        for i in range(n):
            for j in range(i + 1, n):
                coocc.append(self.library.get_entity_cooccurrence(
                    valid_mappings[i].library_entity,
                    valid_mappings[j].library_entity,
                ))
        return np.array(coocc)

    def weighted_distance(
        self,
        c1: np.ndarray,
        c2: np.ndarray,
        weights: np.ndarray,
    ) -> float:
        """Compute weighted Euclidean distance between two coordinate vectors."""
        diff = c1 - c2
        return float(np.sqrt(np.sum(weights * diff ** 2)))

    def subset_distance(
        self,
        c1: np.ndarray,
        c2: np.ndarray,
        axis_indices: List[int],
    ) -> float:
        """Compute Euclidean distance using only specified axis indices."""
        diff = c1[axis_indices] - c2[axis_indices]
        return float(np.linalg.norm(diff))

    def compute_optimal_weights(
        self,
        exclude_entities: Optional[List[str]] = None,
        zero_harmful: bool = True,
    ) -> Dict:
        """Compute per-axis weights from individual correlations.

        Uses |spearman_r| per axis as weight. Optionally zeroes out
        axes whose removal improves correlation (harmful axes).
        """
        valid = self._get_valid_mappings(exclude_entities)
        n = len(valid)
        coocc_arr = self._get_cooccurrence_array(valid)

        if len(coocc_arr) < 10:
            return {"error": "Insufficient pairs"}

        # Per-axis absolute differences
        axis_correlations = {}
        for k, axis in enumerate(AXES):
            diffs = []
            for i in range(n):
                c1 = self.acp.get_coordinates(valid[i].acp_archetype_id)
                for j in range(i + 1, n):
                    c2 = self.acp.get_coordinates(valid[j].acp_archetype_id)
                    diffs.append(abs(float(c1[k] - c2[k])))
            diffs_arr = np.array(diffs)
            if len(set(diffs_arr)) < 2:
                axis_correlations[axis] = 0.0
            else:
                r, _ = spearmanr(diffs_arr, coocc_arr)
                axis_correlations[axis] = float(r)

        # Raw weights = |correlation|
        raw_weights = np.array([abs(axis_correlations[a]) for a in AXES])

        # Identify harmful axes via ablation
        harmful_axes = []
        if zero_harmful:
            # Full 8D baseline
            full_dists = []
            for i in range(n):
                c1 = self.acp.get_coordinates(valid[i].acp_archetype_id)
                for j in range(i + 1, n):
                    c2 = self.acp.get_coordinates(valid[j].acp_archetype_id)
                    full_dists.append(float(np.linalg.norm(c1 - c2)))
            full_r, _ = spearmanr(np.array(full_dists), coocc_arr)

            for k, axis in enumerate(AXES):
                reduced_dists = []
                for i in range(n):
                    c1 = self.acp.get_coordinates(valid[i].acp_archetype_id)
                    for j in range(i + 1, n):
                        c2 = self.acp.get_coordinates(valid[j].acp_archetype_id)
                        c1r = np.delete(c1, k)
                        c2r = np.delete(c2, k)
                        reduced_dists.append(float(np.linalg.norm(c1r - c2r)))
                red_r, _ = spearmanr(np.array(reduced_dists), coocc_arr)
                delta = float(red_r - full_r)
                if delta < -0.005:  # removing improves -> harmful
                    harmful_axes.append(axis)
                    raw_weights[k] = 0.0

        # Normalize weights: sum to len(active axes)
        active = raw_weights > 0
        n_active = active.sum()
        if n_active > 0 and raw_weights[active].sum() > 0:
            raw_weights[active] = raw_weights[active] * n_active / raw_weights[active].sum()

        # Compute weighted distance correlation
        weighted_dists = []
        for i in range(n):
            c1 = self.acp.get_coordinates(valid[i].acp_archetype_id)
            for j in range(i + 1, n):
                c2 = self.acp.get_coordinates(valid[j].acp_archetype_id)
                weighted_dists.append(self.weighted_distance(c1, c2, raw_weights))
        w_r, w_p = spearmanr(np.array(weighted_dists), coocc_arr)

        return {
            "weights": {axis: round(float(w), 4) for axis, w in zip(AXES, raw_weights)},
            "weights_array": raw_weights,
            "per_axis_r": {axis: round(axis_correlations[axis], 4) for axis in AXES},
            "harmful_axes": harmful_axes,
            "n_active_axes": int(n_active),
            "weighted_spearman_r": round(float(w_r), 4),
            "weighted_spearman_p": round(float(w_p), 6),
        }

    def evaluate_axis_subset(
        self,
        axis_indices: List[int],
        exclude_entities: Optional[List[str]] = None,
        _cache: Optional[Dict] = None,
    ) -> Dict:
        """Evaluate a specific axis subset's correlation with co-occurrence.

        Args:
            axis_indices: Which axes to include (0-7 corresponding to AXES).
            exclude_entities: Entities to skip.
            _cache: Optional pre-computed cache with 'valid', 'coocc_arr', 'coords'.

        Returns:
            Dict with spearman_r, spearman_p, n_pairs, axes used.
        """
        if _cache:
            valid = _cache["valid"]
            coocc_arr = _cache["coocc_arr"]
            coords = _cache["coords"]
        else:
            valid = self._get_valid_mappings(exclude_entities)
            coocc_arr = self._get_cooccurrence_array(valid)
            coords = [self.acp.get_coordinates(m.acp_archetype_id) for m in valid]

        if len(coocc_arr) < 10:
            return {"error": "Insufficient pairs"}

        n = len(valid)
        dists = []
        idx_arr = np.array(axis_indices)
        for i in range(n):
            for j in range(i + 1, n):
                diff = coords[i][idx_arr] - coords[j][idx_arr]
                dists.append(float(np.linalg.norm(diff)))

        r, p = spearmanr(np.array(dists), coocc_arr)

        return {
            "axis_indices": axis_indices,
            "axes": [AXES[i] for i in axis_indices],
            "n_dimensions": len(axis_indices),
            "spearman_r": round(float(r), 4),
            "spearman_p": round(float(p), 6),
            "n_pairs": len(dists),
        }

    def systematic_dimensionality_search(
        self,
        min_dims: int = 3,
        max_dims: int = 7,
        exclude_entities: Optional[List[str]] = None,
    ) -> Dict:
        """Test all axis subsets from min_dims to max_dims dimensions.

        Exhaustively evaluates every combination of axes at each
        dimensionality level. With 8 axes:
        - 3D: C(8,3) = 56 combos
        - 4D: C(8,4) = 70 combos
        - 5D: C(8,5) = 56 combos
        - 6D: C(8,6) = 28 combos
        - 7D: C(8,7) = 8 combos
        Total: 218 evaluations — feasible for small entity sets.
        """
        valid = self._get_valid_mappings(exclude_entities)
        coocc_arr = self._get_cooccurrence_array(valid)
        coords = [self.acp.get_coordinates(m.acp_archetype_id) for m in valid]

        if len(coocc_arr) < 10:
            return {"error": "Insufficient pairs"}

        cache = {"valid": valid, "coocc_arr": coocc_arr, "coords": coords}

        # Full 8D baseline
        baseline = self.evaluate_axis_subset(list(range(8)), _cache=cache)

        # Sweep all dimensionalities
        all_results = []
        best_per_dim = {}

        for ndim in range(min_dims, max_dims + 1):
            dim_results = []
            for combo in combinations(range(8), ndim):
                result = self.evaluate_axis_subset(list(combo), _cache=cache)
                if "error" not in result:
                    dim_results.append(result)
                    all_results.append(result)

            if dim_results:
                # Best = most negative r (strongest negative correlation)
                best = min(dim_results, key=lambda x: x["spearman_r"])
                best_per_dim[ndim] = best

        # Overall best across all dimensionalities
        if all_results:
            overall_best = min(all_results, key=lambda x: x["spearman_r"])
        else:
            overall_best = baseline

        # Top 10 across all dimensions
        all_results.sort(key=lambda x: x["spearman_r"])
        top_10 = all_results[:10]

        return {
            "baseline_8d": baseline,
            "best_per_dimensionality": {
                str(k): v for k, v in best_per_dim.items()
            },
            "overall_best": overall_best,
            "top_10_subsets": top_10,
            "total_combinations_tested": len(all_results),
            "improvement_over_8d": round(
                abs(overall_best["spearman_r"]) - abs(baseline["spearman_r"]), 4
            ) if "error" not in baseline else None,
        }
