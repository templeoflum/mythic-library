"""Test 3: Typed Relationship Geometric Signatures.

Tests whether POLAR_OPPOSITE, COMPLEMENT, SHADOW, and EVOLUTION relationships
produce distinct geometric patterns in ACP 8D space.
"""
import numpy as np
from scipy.stats import kruskal, mannwhitneyu
from typing import Dict, List, Optional

from integration.acp_loader import ACPLoader, AXES


class RelationshipGeometryTest:
    def __init__(self, acp: ACPLoader):
        self.acp = acp

    def _parse_axis_name(self, axis_ref: str) -> Optional[int]:
        """Convert axis reference like 'axis:ascent-descent' to index."""
        name = axis_ref.replace("axis:", "").strip()
        if name in AXES:
            return AXES.index(name)
        # Try partial match
        for i, a in enumerate(AXES):
            if name in a or a in name:
                return i
        return None

    def run(self, seed: int = 42) -> Dict:
        rng = np.random.default_rng(seed)

        # Collect relationships by type
        type_groups = {}
        for rel_type in ["POLAR_OPPOSITE", "COMPLEMENT", "SHADOW", "EVOLUTION", "ANTAGONIST"]:
            rels = self.acp.get_all_relationships(type_filter=rel_type)
            valid = []
            for rel in rels:
                c1 = self.acp.get_coordinates(rel["source"])
                c2 = self.acp.get_coordinates(rel.get("target", ""))
                if c1 is not None and c2 is not None:
                    dist = float(np.linalg.norm(c1 - c2))
                    per_axis = {
                        AXES[k]: round(abs(float(c1[k] - c2[k])), 4)
                        for k in range(len(AXES))
                    }
                    max_axis_idx = int(np.argmax(np.abs(c1 - c2)))
                    valid.append({
                        "source": rel["source"],
                        "target": rel.get("target", ""),
                        "source_name": self.acp.archetypes.get(rel["source"], {}).get("name", ""),
                        "target_name": self.acp.archetypes.get(rel.get("target", ""), {}).get("name", ""),
                        "distance": dist,
                        "per_axis_diff": per_axis,
                        "max_diff_axis": AXES[max_axis_idx],
                        "max_diff_value": round(abs(float(c1[max_axis_idx] - c2[max_axis_idx])), 4),
                        "declared_axis": rel.get("axis", None),
                        "strength": rel.get("strength", None),
                        "fidelity": rel.get("fidelity", None),
                    })
            type_groups[rel_type] = valid

        # --- POLAR_OPPOSITE specific tests ---
        polar = type_groups.get("POLAR_OPPOSITE", [])
        polar_axis_pass_count = 0
        polar_axis_max_match = 0
        polar_with_axis = [p for p in polar if p["declared_axis"]]

        for p in polar_with_axis:
            axis_idx = self._parse_axis_name(p["declared_axis"])
            if axis_idx is not None:
                axis_name = AXES[axis_idx]
                diff_on_axis = p["per_axis_diff"].get(axis_name, 0)
                if diff_on_axis > 0.5:
                    polar_axis_pass_count += 1
                if p["max_diff_axis"] == axis_name:
                    polar_axis_max_match += 1

        n_polar_with_axis = len(polar_with_axis)
        polar_axis_pct = (polar_axis_pass_count / n_polar_with_axis * 100) if n_polar_with_axis > 0 else 0
        polar_max_pct = (polar_axis_max_match / n_polar_with_axis * 100) if n_polar_with_axis > 0 else 0

        # --- Cross-type distance comparison ---
        type_distances = {}
        for t, pairs in type_groups.items():
            if pairs:
                dists = [p["distance"] for p in pairs]
                type_distances[t] = {
                    "n_pairs": len(pairs),
                    "mean": round(float(np.mean(dists)), 4),
                    "median": round(float(np.median(dists)), 4),
                    "std": round(float(np.std(dists)), 4),
                }

        # Random baseline
        all_ids = [aid for aid in self.acp.archetypes if self.acp.get_coordinates(aid) is not None]
        random_dists = []
        for _ in range(500):
            i, j = rng.choice(len(all_ids), size=2, replace=False)
            c1 = self.acp.get_coordinates(all_ids[i])
            c2 = self.acp.get_coordinates(all_ids[j])
            random_dists.append(float(np.linalg.norm(c1 - c2)))
        random_arr = np.array(random_dists)
        type_distances["RANDOM"] = {
            "n_pairs": len(random_dists),
            "mean": round(float(random_arr.mean()), 4),
            "median": round(float(np.median(random_arr)), 4),
            "std": round(float(random_arr.std()), 4),
        }

        # Kruskal-Wallis test across all types
        group_arrays = []
        group_labels = []
        for t, pairs in type_groups.items():
            if len(pairs) >= 3:
                group_arrays.append([p["distance"] for p in pairs])
                group_labels.append(t)

        kw_stat, kw_p = (0, 1.0)
        if len(group_arrays) >= 2:
            kw_stat, kw_p = kruskal(*group_arrays)

        # --- EVOLUTION direction test ---
        evolution = type_groups.get("EVOLUTION", [])
        evo_transform_idx = AXES.index("stasis-transformation")
        evo_correct_direction = 0
        for e in evolution:
            c1 = self.acp.get_coordinates(e["source"])
            c2 = self.acp.get_coordinates(e["target"])
            if c1 is not None and c2 is not None:
                # Target should be more toward transformation (higher value)
                if c2[evo_transform_idx] > c1[evo_transform_idx]:
                    evo_correct_direction += 1
        evo_dir_pct = (evo_correct_direction / len(evolution) * 100) if evolution else 0

        # --- Verdicts ---
        polar_axis_pass = polar_axis_pct >= 70
        polar_max_pass = polar_max_pct >= 50
        kw_pass = float(kw_p) < 0.05

        # Human review samples
        human_review = {}
        for t, pairs in type_groups.items():
            sorted_pairs = sorted(pairs, key=lambda x: x["distance"])
            human_review[t] = {
                "examples": sorted_pairs[:5],
                "worst_violators": sorted_pairs[-5:] if len(sorted_pairs) > 5 else [],
            }

        return {
            "relationship_counts": {t: len(p) for t, p in type_groups.items()},
            "polar_opposite_tests": {
                "n_with_declared_axis": n_polar_with_axis,
                "axis_diff_gt_05_count": polar_axis_pass_count,
                "axis_diff_gt_05_pct": round(polar_axis_pct, 1),
                "max_diff_matches_declared_count": polar_axis_max_match,
                "max_diff_matches_declared_pct": round(polar_max_pct, 1),
            },
            "distance_by_type": type_distances,
            "kruskal_wallis": {
                "statistic": round(float(kw_stat), 4),
                "p_value": round(float(kw_p), 6),
                "groups_tested": group_labels,
            },
            "evolution_direction": {
                "n_pairs": len(evolution),
                "correct_direction_count": evo_correct_direction,
                "correct_direction_pct": round(evo_dir_pct, 1),
            },
            "verdicts": {
                "polar_axis_diff": {
                    "pass": polar_axis_pass,
                    "criterion": ">=70% POLAR_OPPOSITE pairs have axis diff >0.5 on declared axis",
                    "result": f"{polar_axis_pct:.1f}% ({polar_axis_pass_count}/{n_polar_with_axis})",
                },
                "polar_max_axis": {
                    "pass": polar_max_pass,
                    "criterion": ">=50% POLAR_OPPOSITE declared axis = axis of max difference",
                    "result": f"{polar_max_pct:.1f}% ({polar_axis_max_match}/{n_polar_with_axis})",
                },
                "type_differentiation": {
                    "pass": kw_pass,
                    "criterion": "Kruskal-Wallis p<0.05 across relationship types",
                    "result": f"H={kw_stat:.2f}, p={kw_p:.4f}",
                },
                "overall_pass": polar_axis_pass and kw_pass,
            },
            "human_review": human_review,
        }
