"""Test 5: Axis Interpretability Audit.

Tests whether the 8 ACP axes have interpretable meanings when checked
against external semantic categories from the Thompson Motif Index.
"""
import numpy as np
from scipy.stats import ttest_1samp
from typing import Dict, List, Optional
from collections import defaultdict

from integration.acp_loader import ACPLoader, AXES
from integration.library_loader import LibraryLoader
from integration.entity_mapper import EntityMapper


# Mapping of Thompson motif letter categories to expected ACP axis behavior.
# Each entry: (motif_prefix, axis_name, expected_direction)
# expected_direction: "low" means entities with this motif should have LOW values on the axis,
#                     "high" means HIGH values.
AXIS_MOTIF_MAPPINGS = [
    ("A", "creation-destruction", "low", "Creation/cosmogony motifs → creation end"),
    ("D", "stasis-transformation", "high", "Magic/transformation motifs → transformation end"),
    ("E", "creation-destruction", "high", "Death/resurrection motifs → destruction end"),
    ("Q", "order-chaos", "low", "Rewards/punishments motifs → order end"),
    ("K", "order-chaos", "high", "Deception/trickster motifs → chaos end"),
    ("H", "individual-collective", "low", "Tests/quests motifs → individual end"),
    ("T", "stasis-transformation", "high", "Transformation motifs → transformation end"),
    ("F", "light-shadow", "high", "Marvels/wonders motifs → shadow/hidden end"),
    ("B", "ascent-descent", "low", "Animal/nature motifs → descent/earth end"),
    ("L", "voluntary-fated", "high", "Chance/fate motifs → fated end"),
]


class AxisInterpretabilityTest:
    def __init__(self, acp: ACPLoader, library: LibraryLoader, mapper: EntityMapper):
        self.acp = acp
        self.library = library
        self.mapper = mapper

    def _get_entities_for_motif_prefix(self, prefix: str) -> List[str]:
        """Get all library entity names tagged with motifs starting with prefix."""
        entities = set()
        for code in self.library.get_all_motif_codes():
            if code.upper().startswith(prefix.upper()):
                for e in self.library.get_motif_entities(code):
                    entities.add(e)
        return list(entities)

    def _entity_to_coordinate(self, entity_name: str) -> Optional[np.ndarray]:
        """Map a library entity to ACP coordinates via the entity mapper."""
        mapping = self.mapper.get_mapping(entity_name)
        if mapping is None:
            return None
        return self.acp.get_coordinates(mapping.acp_archetype_id)

    def run(self) -> Dict:
        # Compute global mean coordinates across all mapped archetypes
        all_coords = []
        for m in self.mapper.mappings:
            c = self.acp.get_coordinates(m.acp_archetype_id)
            if c is not None:
                all_coords.append(c)

        if len(all_coords) < 10:
            return {"error": "Insufficient mapped archetypes"}

        global_mean = np.mean(all_coords, axis=0)

        # Test each axis-motif mapping
        test_results = []
        axes_with_pass = defaultdict(list)

        for prefix, axis_name, direction, description in AXIS_MOTIF_MAPPINGS:
            axis_idx = AXES.index(axis_name)

            # Get entities for this motif category
            entities = self._get_entities_for_motif_prefix(prefix)

            # Map to coordinates
            coords = []
            mapped_names = []
            for e in entities:
                c = self._entity_to_coordinate(e)
                if c is not None:
                    coords.append(c)
                    mapped_names.append(e)

            if len(coords) < 3:
                test_results.append({
                    "motif_prefix": prefix,
                    "axis": axis_name,
                    "direction": direction,
                    "description": description,
                    "n_entities": len(entities),
                    "n_mapped": len(coords),
                    "result": "SKIPPED (insufficient data)",
                    "pass": False,
                })
                continue

            # Extract values on the target axis
            axis_values = np.array([c[axis_idx] for c in coords])
            group_mean = float(axis_values.mean())
            global_axis_mean = float(global_mean[axis_idx])

            # One-sample t-test: does group mean differ from global mean?
            t_stat, t_p = ttest_1samp(axis_values, global_axis_mean)

            # Check direction
            if direction == "low":
                correct_direction = group_mean < global_axis_mean
            else:
                correct_direction = group_mean > global_axis_mean

            # Pass = significant AND correct direction
            passed = t_p < 0.05 and correct_direction

            if passed:
                axes_with_pass[axis_name].append(prefix)

            test_results.append({
                "motif_prefix": prefix,
                "axis": axis_name,
                "direction": direction,
                "description": description,
                "n_entities": len(entities),
                "n_mapped": len(coords),
                "group_mean": round(group_mean, 4),
                "global_mean": round(global_axis_mean, 4),
                "delta": round(group_mean - global_axis_mean, 4),
                "correct_direction": correct_direction,
                "t_statistic": round(float(t_stat), 4),
                "p_value": round(float(t_p), 6),
                "pass": passed,
                "result": "PASS" if passed else "FAIL",
                "sample_entities": mapped_names[:5],
            })

        # Compute interpretability score
        testable = [t for t in test_results if t["result"] != "SKIPPED (insufficient data)"]
        n_passed = sum(1 for t in testable if t["pass"])
        n_testable = len(testable)
        score = n_passed / n_testable if n_testable > 0 else 0

        # Check top 3 axes
        top_3 = ["order-chaos", "creation-destruction", "individual-collective"]
        top_3_have_alignment = sum(1 for a in top_3 if a in axes_with_pass)

        # Verdicts
        score_pass = score >= 0.50
        top3_pass = top_3_have_alignment >= 1  # At least 1 of top 3 has alignment

        return {
            "n_mappings_tested": n_testable,
            "n_passed": n_passed,
            "interpretability_score": round(score, 4),
            "axes_with_alignments": {k: v for k, v in axes_with_pass.items()},
            "top_3_axes_aligned": top_3_have_alignment,
            "global_means": {AXES[i]: round(float(global_mean[i]), 4) for i in range(len(AXES))},
            "test_results": test_results,
            "verdicts": {
                "interpretability_score": {
                    "pass": score_pass,
                    "criterion": ">=50% of axis-category pairings show significant deviation in predicted direction",
                    "result": f"{n_passed}/{n_testable} ({score*100:.0f}%)",
                },
                "top_3_alignment": {
                    "pass": top3_pass,
                    "criterion": "Top 3 axes each have >=1 interpretable alignment",
                    "result": f"{top_3_have_alignment}/3 top axes aligned",
                },
                "overall_pass": score_pass and top3_pass,
            },
        }
