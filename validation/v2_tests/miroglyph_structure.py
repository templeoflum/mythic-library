"""Tests 7-10: Miroglyph Structural Validity.

Tests whether Miroglyph's 3 arcs, 6 conditions, and polarity pairs are
empirically supported by the Library + ACP data, and surfaces alternatives
if a different structure fits better.

Philosophy: function first, everything else is negotiable.
"""
import numpy as np
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from scipy.stats import kruskal, mannwhitneyu, spearmanr, f_oneway
from scipy.spatial.distance import pdist, squareform

from integration.acp_loader import ACPLoader, AXES
from integration.library_loader import LibraryLoader
from integration.entity_mapper import EntityMapper
from integration.miroglyph_loader import MiroGlyphLoader
from integration.node_profiler import NodeProfiler, ARC_PATTERN_MAPPING, MIN_SEGMENTS_PER_TEXT


def _silhouette_score(coords: np.ndarray, labels: np.ndarray) -> float:
    """Compute mean silhouette score without sklearn dependency."""
    n = len(coords)
    if n < 3:
        return 0.0

    unique_labels = np.unique(labels)
    if len(unique_labels) < 2:
        return 0.0

    dist_matrix = squareform(pdist(coords))
    silhouettes = []

    for i in range(n):
        own_label = labels[i]
        own_mask = labels == own_label
        own_count = own_mask.sum()

        # a(i) = mean distance to same-cluster points
        if own_count > 1:
            a_i = dist_matrix[i][own_mask].sum() / (own_count - 1)
        else:
            a_i = 0.0

        # b(i) = min mean distance to any other cluster
        b_i = float("inf")
        for lbl in unique_labels:
            if lbl == own_label:
                continue
            other_mask = labels == lbl
            other_count = other_mask.sum()
            if other_count == 0:
                continue
            mean_dist = dist_matrix[i][other_mask].mean()
            b_i = min(b_i, mean_dist)

        if b_i == float("inf"):
            b_i = 0.0

        denom = max(a_i, b_i)
        s_i = (b_i - a_i) / denom if denom > 0 else 0.0
        silhouettes.append(s_i)

    return float(np.mean(silhouettes))


class MiroStructureTest:
    """Tests 7-10: Miroglyph structural validity."""

    def __init__(
        self,
        acp: ACPLoader,
        library: LibraryLoader,
        mapper: EntityMapper,
        miroglyph: MiroGlyphLoader,
        profiler: NodeProfiler,
    ):
        self.acp = acp
        self.library = library
        self.mapper = mapper
        self.miroglyph = miroglyph
        self.profiler = profiler

    def run(self) -> Dict:
        """Run all 4 Miroglyph structure tests."""
        results = {}

        print("    Test 7: Arc Separation...")
        results["test7_arc_separation"] = self._test_arc_separation()

        print("    Test 8: Condition Progression...")
        results["test8_condition_progression"] = self._test_condition_progression()

        print("    Test 9: Polarity Pair Opposition...")
        results["test9_polarity_pairs"] = self._test_polarity_pairs()

        print("    Test 10: Structural Optimality...")
        results["test10_structural_optimality"] = self._test_structural_optimality()

        # Compute verdicts
        results["verdicts"] = self._compute_verdicts(results)

        return results

    # ── Test 7: Arc Separation ──

    def _test_arc_separation(self) -> dict:
        """Test whether the 3 arcs occupy distinct regions in ACP space."""
        # Get entity coordinates grouped by arc
        arc_coords = {}  # arc_code -> (N, 8) array
        arc_labels_list = []
        all_coords_list = []

        for arc_code, pattern_names in ARC_PATTERN_MAPPING.items():
            motif_codes = []
            for pname in pattern_names:
                codes = self.library.get_pattern_motif_codes(pname)
                motif_codes.extend(codes)
            motif_codes = list(set(motif_codes))

            entities = self.library.get_entities_for_motif_codes(motif_codes)
            coords = []
            for ent in entities:
                mapping = self.mapper.get_mapping(ent)
                if mapping:
                    c = self.acp.get_coordinates(mapping.acp_archetype_id)
                    if c is not None:
                        coords.append(c)
                        arc_labels_list.append(arc_code)
                        all_coords_list.append(c)

            arc_coords[arc_code] = np.array(coords) if coords else np.empty((0, len(AXES)))

        all_coords = np.array(all_coords_list) if all_coords_list else np.empty((0, len(AXES)))
        all_labels = np.array(arc_labels_list)

        if len(all_coords) < 10:
            return {"error": "Too few entities with coordinates", "pass": False}

        # Within-arc vs between-arc distances
        within_dists = []
        between_dists = []
        label_to_idx = defaultdict(list)
        for i, lbl in enumerate(all_labels):
            label_to_idx[lbl].append(i)

        dist_matrix = squareform(pdist(all_coords))

        for lbl, indices in label_to_idx.items():
            for i in range(len(indices)):
                for j in range(i + 1, len(indices)):
                    within_dists.append(dist_matrix[indices[i]][indices[j]])

        labels_list = list(label_to_idx.keys())
        for a in range(len(labels_list)):
            for b in range(a + 1, len(labels_list)):
                for i in label_to_idx[labels_list[a]]:
                    for j in label_to_idx[labels_list[b]]:
                        between_dists.append(dist_matrix[i][j])

        within_arr = np.array(within_dists)
        between_arr = np.array(between_dists)

        # Mann-Whitney: are between-arc distances > within-arc distances?
        if len(within_arr) > 0 and len(between_arr) > 0:
            stat_mw, p_mw = mannwhitneyu(between_arr, within_arr, alternative="greater")
        else:
            stat_mw, p_mw = 0.0, 1.0

        # Kruskal-Wallis across arc groups (per-entity centroid distances)
        groups = [arc_coords[k] for k in ["D", "R", "E"] if len(arc_coords[k]) > 0]
        if len(groups) >= 2:
            # Test each axis separately
            axis_kw = {}
            for ax_idx, ax_name in enumerate(AXES):
                ax_groups = [g[:, ax_idx] for g in groups if len(g) > 0]
                if len(ax_groups) >= 2 and all(len(g) > 1 for g in ax_groups):
                    stat_kw, p_kw = kruskal(*ax_groups)
                    axis_kw[ax_name] = {"H": float(stat_kw), "p": float(p_kw)}
                else:
                    axis_kw[ax_name] = {"H": 0.0, "p": 1.0}
        else:
            axis_kw = {}

        # Silhouette score for k=3
        label_map = {"D": 0, "R": 1, "E": 2}
        numeric_labels = np.array([label_map[l] for l in all_labels])
        silhouette_3 = _silhouette_score(all_coords, numeric_labels)

        # Test alternative k values
        alt_silhouettes = {}
        for k in [2, 4, 5]:
            # Simple k-means via iterative assignment
            s = self._quick_kmeans_silhouette(all_coords, k)
            alt_silhouettes[k] = s

        significant_axes = [ax for ax, v in axis_kw.items() if v["p"] < 0.05]

        result = {
            "n_entities": {"D": len(arc_coords["D"]), "R": len(arc_coords["R"]),
                           "E": len(arc_coords["E"])},
            "within_arc_mean_dist": float(within_arr.mean()) if len(within_arr) > 0 else None,
            "between_arc_mean_dist": float(between_arr.mean()) if len(between_arr) > 0 else None,
            "mann_whitney_p": float(p_mw),
            "axis_kruskal_wallis": axis_kw,
            "significant_axes": significant_axes,
            "silhouette_k3": float(silhouette_3),
            "alternative_silhouettes": {str(k): float(v) for k, v in alt_silhouettes.items()},
            "best_k": max(
                [(3, silhouette_3)] + [(k, v) for k, v in alt_silhouettes.items()],
                key=lambda x: x[1]
            )[0],
        }

        # Pass if significant separation AND positive silhouette
        result["pass"] = p_mw < 0.05 and silhouette_3 > 0.0

        return result

    def _quick_kmeans_silhouette(self, coords: np.ndarray, k: int, max_iter: int = 20) -> float:
        """Quick k-means + silhouette (no sklearn)."""
        n = len(coords)
        if n < k:
            return -1.0

        rng = np.random.default_rng(42)
        centroids = coords[rng.choice(n, k, replace=False)]

        labels = np.zeros(n, dtype=int)
        for _ in range(max_iter):
            # Assign
            dists = np.array([np.linalg.norm(coords - c, axis=1) for c in centroids])
            new_labels = dists.argmin(axis=0)
            if np.array_equal(new_labels, labels):
                break
            labels = new_labels
            # Update centroids
            for j in range(k):
                mask = labels == j
                if mask.sum() > 0:
                    centroids[j] = coords[mask].mean(axis=0)

        return _silhouette_score(coords, labels)

    # ── Test 8: Condition Progression ──

    def _test_condition_progression(self) -> dict:
        """Test whether conditions 1-6 map to identifiable narrative phases."""
        seg_counts = self.library.get_segments_per_text()
        eligible_texts = [
            tid for tid, cnt in seg_counts.items() if cnt >= MIN_SEGMENTS_PER_TEXT
        ]

        # For each text, get per-bin entity coordinates
        # Test with multiple bin counts
        best_result = None
        results_by_bins = {}

        for n_bins in [4, 5, 6, 7, 8]:
            bin_coords: Dict[int, List[np.ndarray]] = defaultdict(list)

            for text_id in eligible_texts:
                segments = self.library.get_text_segments_ordered(text_id)
                if not segments:
                    continue
                total = len(segments)
                for seg in segments:
                    ordinal = seg["ordinal"]
                    ratio = (ordinal - 1) / max(total - 1, 1)
                    bin_idx = min(n_bins, int(ratio * n_bins) + 1)
                    for ent_name in seg["entity_names"]:
                        mapping = self.mapper.get_mapping(ent_name)
                        if mapping:
                            c = self.acp.get_coordinates(mapping.acp_archetype_id)
                            if c is not None:
                                bin_coords[bin_idx].append(c)

            # Test per-axis ANOVA across bins
            axis_results = {}
            significant_count = 0
            for ax_idx, ax_name in enumerate(AXES):
                groups = []
                for b in range(1, n_bins + 1):
                    vals = [c[ax_idx] for c in bin_coords.get(b, [])]
                    if vals:
                        groups.append(vals)

                if len(groups) >= 2 and all(len(g) > 1 for g in groups):
                    stat_f, p_f = f_oneway(*groups)
                    # Test monotonic trend (Spearman of bin_index vs axis_value)
                    all_bins_for_axis = []
                    all_vals_for_axis = []
                    for b in range(1, n_bins + 1):
                        for c in bin_coords.get(b, []):
                            all_bins_for_axis.append(b)
                            all_vals_for_axis.append(c[ax_idx])
                    if len(all_bins_for_axis) > 10:
                        r_s, p_s = spearmanr(all_bins_for_axis, all_vals_for_axis)
                    else:
                        r_s, p_s = 0.0, 1.0

                    axis_results[ax_name] = {
                        "F": float(stat_f), "p_anova": float(p_f),
                        "spearman_r": float(r_s), "p_trend": float(p_s),
                        "significant": p_f < 0.05,
                    }
                    if p_f < 0.05:
                        significant_count += 1
                else:
                    axis_results[ax_name] = {
                        "F": 0.0, "p_anova": 1.0,
                        "spearman_r": 0.0, "p_trend": 1.0,
                        "significant": False,
                    }

            bin_sizes = {b: len(bin_coords.get(b, [])) for b in range(1, n_bins + 1)}
            results_by_bins[n_bins] = {
                "n_bins": n_bins,
                "bin_sizes": bin_sizes,
                "axis_results": axis_results,
                "significant_axes": significant_count,
            }

        # Find optimal bin count (most significant axes)
        optimal_bins = max(results_by_bins.values(), key=lambda x: x["significant_axes"])

        result = {
            "n_texts": len(eligible_texts),
            "current_bins_6": results_by_bins.get(6, {}),
            "all_bin_counts": {
                str(k): {
                    "n_bins": v["n_bins"],
                    "significant_axes": v["significant_axes"],
                }
                for k, v in results_by_bins.items()
            },
            "optimal_bins": optimal_bins["n_bins"],
            "optimal_significant_axes": optimal_bins["significant_axes"],
        }

        # Pass if >= 2 axes show significant condition effect at n_bins=6
        current = results_by_bins.get(6, {})
        result["pass"] = current.get("significant_axes", 0) >= 2

        return result

    # ── Test 9: Polarity Pair Opposition ──

    def _test_polarity_pairs(self) -> dict:
        """Test whether polarity pairs show more opposition than non-polarity pairs."""
        condition_profiles = self.profiler.compute_condition_profiles()

        # Compute distances between all condition pairs
        cond_centroids = {}
        for cond_code in range(1, 7):
            profile = condition_profiles.get(cond_code, {})
            coords = profile.get("mean_coordinates", [0.5] * 8)
            cond_centroids[cond_code] = np.array(coords)

        # Polarity pairs: 1-6, 2-5, 3-4
        polarity_dists = []
        polarity_details = []
        for c1, c2 in [(1, 6), (2, 5), (3, 4)]:
            d = float(np.linalg.norm(cond_centroids[c1] - cond_centroids[c2]))
            polarity_dists.append(d)
            polarity_details.append({"pair": f"{c1}-{c2}", "distance": d})

        # Non-polarity pairs (adjacent and other)
        non_polarity_dists = []
        non_polarity_details = []
        polarity_set = {(1, 6), (6, 1), (2, 5), (5, 2), (3, 4), (4, 3)}
        for c1 in range(1, 7):
            for c2 in range(c1 + 1, 7):
                if (c1, c2) not in polarity_set:
                    d = float(np.linalg.norm(cond_centroids[c1] - cond_centroids[c2]))
                    non_polarity_dists.append(d)
                    non_polarity_details.append({"pair": f"{c1}-{c2}", "distance": d})

        polarity_arr = np.array(polarity_dists)
        non_polarity_arr = np.array(non_polarity_dists)

        # Mann-Whitney: polarity pairs more distant?
        if len(polarity_arr) > 0 and len(non_polarity_arr) > 0:
            stat, p_val = mannwhitneyu(polarity_arr, non_polarity_arr, alternative="greater")
        else:
            stat, p_val = 0.0, 1.0

        # Per-axis analysis: which axes show strongest polarity opposition?
        axis_polarity = {}
        for ax_idx, ax_name in enumerate(AXES):
            diffs = []
            for c1, c2 in [(1, 6), (2, 5), (3, 4)]:
                diff = abs(cond_centroids[c1][ax_idx] - cond_centroids[c2][ax_idx])
                diffs.append(float(diff))
            axis_polarity[ax_name] = {
                "mean_polarity_diff": float(np.mean(diffs)),
                "max_polarity_diff": float(np.max(diffs)),
                "pairs": {f"{c1}-{c2}": float(abs(cond_centroids[c1][ax_idx] - cond_centroids[c2][ax_idx]))
                          for c1, c2 in [(1, 6), (2, 5), (3, 4)]},
            }

        # Test alternative pairings
        from itertools import combinations
        all_pairings = []
        conditions = [1, 2, 3, 4, 5, 6]
        # Generate all possible 3-pair perfect matchings of 6 items
        for p1 in combinations(conditions, 2):
            remaining = [c for c in conditions if c not in p1]
            for p2 in combinations(remaining, 2):
                p3 = tuple(c for c in remaining if c not in p2)
                pairing = tuple(sorted([tuple(sorted(p1)), tuple(sorted(p2)), tuple(sorted(p3))]))
                if pairing not in all_pairings:
                    all_pairings.append(pairing)

        best_pairing = None
        best_pairing_dist = 0.0
        for pairing in all_pairings:
            total_dist = sum(
                float(np.linalg.norm(cond_centroids[p[0]] - cond_centroids[p[1]]))
                for p in pairing
            )
            if total_dist > best_pairing_dist:
                best_pairing_dist = total_dist
                best_pairing = pairing

        current_pairing_dist = sum(polarity_dists)

        result = {
            "polarity_pairs": polarity_details,
            "non_polarity_pairs": non_polarity_details,
            "polarity_mean_dist": float(polarity_arr.mean()) if len(polarity_arr) > 0 else 0.0,
            "non_polarity_mean_dist": float(non_polarity_arr.mean()) if len(non_polarity_arr) > 0 else 0.0,
            "mann_whitney_p": float(p_val),
            "axis_polarity": axis_polarity,
            "current_pairing_total_dist": float(current_pairing_dist),
            "best_pairing": [list(p) for p in best_pairing] if best_pairing else None,
            "best_pairing_total_dist": float(best_pairing_dist),
            "current_is_optimal": best_pairing == ((1, 6), (2, 5), (3, 4)),
        }

        result["pass"] = p_val < 0.05 or (
            float(polarity_arr.mean()) > float(non_polarity_arr.mean())
            if len(polarity_arr) > 0 and len(non_polarity_arr) > 0 else False
        )

        return result

    # ── Test 10: Structural Optimality ──

    def _test_structural_optimality(self) -> dict:
        """Synthesize findings: is 3x6 optimal or would something else be better?"""
        # Gather results from the other tests (we call their core logic)
        # Arc count analysis
        arc_result = self._test_arc_separation()
        silhouette_3 = arc_result.get("silhouette_k3", 0.0)
        alt_silhouettes = arc_result.get("alternative_silhouettes", {})
        best_k = arc_result.get("best_k", 3)

        # Condition count analysis
        cond_result = self._test_condition_progression()
        optimal_bins = cond_result.get("optimal_bins", 6)
        bins_comparison = cond_result.get("all_bin_counts", {})

        # Polarity analysis
        polarity_result = self._test_polarity_pairs()
        current_polarity_optimal = polarity_result.get("current_is_optimal", False)
        best_pairing = polarity_result.get("best_pairing", None)

        # Axis relevance for arc separation
        axis_kw = arc_result.get("axis_kruskal_wallis", {})
        relevant_axes = [ax for ax, v in axis_kw.items() if v.get("p", 1.0) < 0.05]
        irrelevant_axes = [ax for ax in AXES if ax not in relevant_axes]

        # Recommendations
        recommendations = []

        if best_k != 3:
            recommendations.append(
                f"DATA SUGGESTS {best_k} ARCS (silhouette {alt_silhouettes.get(str(best_k), 0):.3f}) "
                f"vs current 3 arcs (silhouette {silhouette_3:.3f})"
            )
        else:
            recommendations.append(
                f"3 arcs confirmed as optimal (silhouette {silhouette_3:.3f})"
            )

        if optimal_bins != 6:
            sig_6 = bins_comparison.get("6", {}).get("significant_axes", 0)
            sig_opt = bins_comparison.get(str(optimal_bins), {}).get("significant_axes", 0)
            recommendations.append(
                f"DATA SUGGESTS {optimal_bins} CONDITIONS "
                f"({sig_opt} significant axes) vs current 6 ({sig_6} significant axes)"
            )
        else:
            recommendations.append("6 conditions confirmed as optimal")

        if not current_polarity_optimal and best_pairing:
            recommendations.append(
                f"ALTERNATIVE POLARITY PAIRING may be stronger: {best_pairing}"
            )
        else:
            recommendations.append("Current polarity pairs (1-6, 2-5, 3-4) confirmed")

        if irrelevant_axes:
            recommendations.append(
                f"Axes not contributing to arc separation: {irrelevant_axes}"
            )

        structure_confirmed = (best_k == 3 and optimal_bins == 6)

        result = {
            "optimal_arcs": best_k,
            "current_arcs": 3,
            "arc_silhouettes": {"3": float(silhouette_3), **{str(k): float(v) for k, v in alt_silhouettes.items()}},
            "optimal_conditions": optimal_bins,
            "current_conditions": 6,
            "condition_comparison": bins_comparison,
            "polarity_optimal": current_polarity_optimal,
            "best_polarity_pairing": [list(p) for p in best_pairing] if best_pairing else None,
            "relevant_axes": relevant_axes,
            "irrelevant_axes": irrelevant_axes,
            "structure_confirmed": structure_confirmed,
            "recommendations": recommendations,
        }

        return result

    # ── Verdicts ──

    def _compute_verdicts(self, results: dict) -> dict:
        """Compute pass/fail verdicts for Tier C."""
        t7 = results.get("test7_arc_separation", {})
        t8 = results.get("test8_condition_progression", {})
        t9 = results.get("test9_polarity_pairs", {})
        t10 = results.get("test10_structural_optimality", {})

        verdicts = {
            "test7_arc_separation": {
                "pass": t7.get("pass", False),
                "criterion": "Between-arc distances > within-arc (p<0.05) AND silhouette > 0",
                "detail": f"p={t7.get('mann_whitney_p', 1.0):.4f}, "
                          f"silhouette={t7.get('silhouette_k3', 0.0):.4f}",
            },
            "test8_condition_progression": {
                "pass": t8.get("pass", False),
                "criterion": ">=2 axes show significant condition effect at 6 bins",
                "detail": f"{t8.get('current_bins_6', {}).get('significant_axes', 0)} significant axes",
            },
            "test9_polarity_pairs": {
                "pass": t9.get("pass", False),
                "criterion": "Polarity pairs more distant than non-polarity (p<0.05 or mean comparison)",
                "detail": f"polarity mean={t9.get('polarity_mean_dist', 0):.4f}, "
                          f"non-polarity mean={t9.get('non_polarity_mean_dist', 0):.4f}",
            },
            "test10_structural_optimality": {
                "structure_confirmed": t10.get("structure_confirmed", False),
                "recommendations": t10.get("recommendations", []),
            },
        }

        # Tier C overall
        tier_c_pass = (
            verdicts["test7_arc_separation"]["pass"]
            and verdicts["test8_condition_progression"]["pass"]
        )
        verdicts["tier_c_overall"] = {
            "pass": tier_c_pass,
            "label": "PASS" if tier_c_pass else "FAIL",
            "detail": "Arc separation + condition progression confirmed"
                      if tier_c_pass else "Structural claims not fully supported",
        }

        return verdicts
