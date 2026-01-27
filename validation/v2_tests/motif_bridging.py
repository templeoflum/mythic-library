"""Test 4: Cross-Tradition Motif Bridging.

Tests whether entities from DIFFERENT traditions that share Thompson
motifs sit closer in ACP space — the properly reframed v1 test that
eliminates the tradition confound.
"""
import numpy as np
from scipy.stats import spearmanr, mannwhitneyu
from typing import Dict, List, Optional
from collections import defaultdict

from integration.acp_loader import ACPLoader, AXES
from integration.library_loader import LibraryLoader
from integration.entity_mapper import EntityMapper


class MotifBridgingTest:
    def __init__(self, acp: ACPLoader, library: LibraryLoader, mapper: EntityMapper):
        self.acp = acp
        self.library = library
        self.mapper = mapper

    def run(self) -> Dict:
        # Get valid mappings with coordinates and tradition info
        valid = []
        for m in self.mapper.mappings:
            c = self.acp.get_coordinates(m.acp_archetype_id)
            if c is not None:
                entity = self.library.get_entity_by_name(m.library_entity) if hasattr(self.library, 'get_entity_by_name') else None
                tradition = ""
                if entity:
                    tradition = entity.primary_tradition
                else:
                    # Fallback: try to get tradition from the entity list
                    for e in self.library.get_all_entities():
                        if e.canonical_name == m.library_entity:
                            tradition = e.primary_tradition
                            break
                valid.append({
                    "entity": m.library_entity,
                    "archetype_id": m.acp_archetype_id,
                    "tradition": tradition,
                    "coords": c,
                })

        if len(valid) < 10:
            return {"error": f"Only {len(valid)} mapped entities"}

        # Build entity motif sets
        all_motif_codes = self.library.get_all_motif_codes()
        entity_motifs = {}
        for v in valid:
            motifs = set()
            for code in all_motif_codes:
                if v["entity"] in self.library.get_motif_entities(code):
                    motifs.add(code)
            entity_motifs[v["entity"]] = motifs

        # Compute cross-tradition pairs only
        n = len(valid)
        cross_trad_distances = []
        cross_trad_jaccards = []
        cross_trad_pairs = []

        for i in range(n):
            for j in range(i + 1, n):
                # Skip same-tradition pairs
                if valid[i]["tradition"] == valid[j]["tradition"] and valid[i]["tradition"] != "":
                    continue

                dist = float(np.linalg.norm(valid[i]["coords"] - valid[j]["coords"]))
                s1 = entity_motifs.get(valid[i]["entity"], set())
                s2 = entity_motifs.get(valid[j]["entity"], set())
                union = len(s1 | s2)
                intersection = len(s1 & s2)
                jaccard = intersection / union if union > 0 else 0

                cross_trad_distances.append(dist)
                cross_trad_jaccards.append(jaccard)
                cross_trad_pairs.append({
                    "entity1": valid[i]["entity"],
                    "entity2": valid[j]["entity"],
                    "tradition1": valid[i]["tradition"],
                    "tradition2": valid[j]["tradition"],
                    "distance": round(dist, 4),
                    "jaccard": round(jaccard, 4),
                    "shared_motifs": len(s1 & s2),
                    "shared_motif_codes": sorted(list(s1 & s2))[:10],
                })

        if len(cross_trad_distances) < 10:
            return {"error": "Insufficient cross-tradition pairs"}

        dist_arr = np.array(cross_trad_distances)
        jac_arr = np.array(cross_trad_jaccards)

        # 1. Spearman correlation: distance vs Jaccard
        corr_r, corr_p = spearmanr(dist_arr, jac_arr)

        # 2. Mann-Whitney U: motif-sharing pairs vs non-sharing pairs
        sharing_mask = jac_arr > 0
        n_sharing = int(sharing_mask.sum())
        n_nonsharing = int((~sharing_mask).sum())

        if n_sharing >= 3 and n_nonsharing >= 3:
            u_stat, u_p = mannwhitneyu(
                dist_arr[sharing_mask], dist_arr[~sharing_mask],
                alternative="less",
            )
            sharing_mean = float(dist_arr[sharing_mask].mean())
            nonsharing_mean = float(dist_arr[~sharing_mask].mean())
        else:
            u_stat, u_p = 0.0, 1.0
            sharing_mean = 0.0
            nonsharing_mean = 0.0

        # 3. Test 3-axis subset vs full 8D
        subset_indices = [AXES.index("order-chaos"), AXES.index("creation-destruction"), AXES.index("individual-collective")]
        subset_dists = []
        for i in range(n):
            for j in range(i + 1, n):
                if valid[i]["tradition"] == valid[j]["tradition"] and valid[i]["tradition"] != "":
                    continue
                diff = valid[i]["coords"][subset_indices] - valid[j]["coords"][subset_indices]
                subset_dists.append(float(np.linalg.norm(diff)))

        subset_arr = np.array(subset_dists)
        if len(subset_arr) == len(jac_arr):
            subset_r, subset_p = spearmanr(subset_arr, jac_arr)
        else:
            subset_r, subset_p = 0.0, 1.0

        # 4. Verdicts
        corr_pass = float(corr_r) < -0.05 and corr_p < 0.05
        mw_pass = float(u_p) < 0.05

        # 5. Human review: top overlap pairs and closest cross-tradition pairs
        sorted_by_jaccard = sorted(cross_trad_pairs, key=lambda x: x["jaccard"], reverse=True)
        sorted_by_distance = sorted(cross_trad_pairs, key=lambda x: x["distance"])

        return {
            "n_cross_tradition_pairs": len(cross_trad_distances),
            "n_motif_sharing_pairs": n_sharing,
            "n_non_sharing_pairs": n_nonsharing,
            "correlation": {
                "spearman_r": round(float(corr_r), 4),
                "spearman_p": round(float(corr_p), 6),
            },
            "mann_whitney": {
                "sharing_mean_distance": round(sharing_mean, 4),
                "nonsharing_mean_distance": round(nonsharing_mean, 4),
                "u_statistic": round(float(u_stat), 2),
                "p_value": round(float(u_p), 6),
            },
            "three_axis_subset": {
                "axes": ["order-chaos", "creation-destruction", "individual-collective"],
                "spearman_r": round(float(subset_r), 4),
                "spearman_p": round(float(subset_p), 6),
                "improvement_over_8d": round(abs(float(subset_r)) - abs(float(corr_r)), 4),
            },
            "verdicts": {
                "correlation_test": {
                    "pass": corr_pass,
                    "criterion": "Cross-tradition ACP distance negatively correlates with motif Jaccard (r<-0.05, p<0.05)",
                    "result": f"r={corr_r:.4f}, p={corr_p:.4f}",
                },
                "group_test": {
                    "pass": mw_pass,
                    "criterion": "Motif-sharing pairs are closer than non-sharing (Mann-Whitney p<0.05)",
                    "result": f"sharing={sharing_mean:.4f} vs non={nonsharing_mean:.4f}, p={u_p:.4f}",
                },
                "overall_pass": corr_pass and mw_pass,
            },
            "human_review": {
                "highest_motif_overlap": sorted_by_jaccard[:10],
                "closest_cross_tradition": sorted_by_distance[:10],
            },
        }
