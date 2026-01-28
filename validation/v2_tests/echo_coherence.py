"""Test 1: CULTURAL_ECHO Distance Coherence.

Tests whether archetypes labeled as cultural echoes (e.g. Zeus<->Jupiter)
are geometrically close in ACP 8D space, and whether fidelity scores
predict coordinate distance.
"""
import numpy as np
from scipy.stats import mannwhitneyu, spearmanr
from typing import Dict, List, Optional

from integration.acp_loader import ACPLoader
from validation.v2_tests import weighted_distance


class EchoCoherenceTest:
    def __init__(self, acp: ACPLoader):
        self.acp = acp

    def run(self, seed: int = 42) -> Dict:
        """Run the CULTURAL_ECHO distance coherence test.

        Returns dict with echo distances, control distances, statistical
        tests, pass/fail verdicts, and human review tables.
        """
        rng = np.random.default_rng(seed)

        # 1. Extract all CULTURAL_ECHO relationships
        echoes = self.acp.get_all_relationships(type_filter="CULTURAL_ECHO")

        # Filter to pairs where both source and target have coordinates
        valid_echoes = []
        for rel in echoes:
            c1 = self.acp.get_coordinates(rel["source"])
            c2 = self.acp.get_coordinates(rel.get("target", ""))
            if c1 is not None and c2 is not None:
                dist = float(np.linalg.norm(c1 - c2))
                fidelity = rel.get("fidelity", None)
                valid_echoes.append({
                    "source": rel["source"],
                    "target": rel["target"],
                    "source_name": self.acp.archetypes.get(rel["source"], {}).get("name", rel["source"]),
                    "target_name": self.acp.archetypes.get(rel.get("target", ""), {}).get("name", rel.get("target", "")),
                    "fidelity": fidelity,
                    "distance": dist,
                })

        if len(valid_echoes) < 5:
            return {"error": f"Only {len(valid_echoes)} valid echo pairs found", "pass": False}

        echo_distances = np.array([e["distance"] for e in valid_echoes])

        # 2. Build control group: random cross-tradition pairs with no echo relationship
        echo_pair_set = set()
        for e in valid_echoes:
            echo_pair_set.add((e["source"], e["target"]))
            echo_pair_set.add((e["target"], e["source"]))

        # Get all archetypes with coordinates grouped by tradition
        arch_traditions = {}
        for aid, arch in self.acp.archetypes.items():
            if self.acp.get_coordinates(aid) is not None:
                system = arch.get("systemCode", arch.get("belongsToSystem", "unknown"))
                arch_traditions[aid] = system

        all_ids = list(arch_traditions.keys())
        n_control = len(valid_echoes) * 3  # 3x oversampling for statistical power

        control_distances = []
        attempts = 0
        while len(control_distances) < n_control and attempts < n_control * 20:
            i, j = rng.choice(len(all_ids), size=2, replace=False)
            id1, id2 = all_ids[i], all_ids[j]
            # Must be cross-tradition and not an echo pair
            if arch_traditions[id1] == arch_traditions[id2]:
                attempts += 1
                continue
            if (id1, id2) in echo_pair_set:
                attempts += 1
                continue
            c1 = self.acp.get_coordinates(id1)
            c2 = self.acp.get_coordinates(id2)
            control_distances.append(float(np.linalg.norm(c1 - c2)))
            attempts += 1

        control_arr = np.array(control_distances)

        # 3. Mann-Whitney U test: echo pairs vs control
        if len(control_arr) < 5:
            return {"error": "Could not generate enough control pairs", "pass": False}

        u_stat, u_p = mannwhitneyu(echo_distances, control_arr, alternative="less")
        # Cohen's d
        pooled_std = np.sqrt((echo_distances.std()**2 + control_arr.std()**2) / 2)
        cohens_d = (control_arr.mean() - echo_distances.mean()) / pooled_std if pooled_std > 0 else 0.0

        # 4. Fidelity-distance correlation (among echo pairs with fidelity scores)
        fidelity_pairs = [(e["fidelity"], e["distance"]) for e in valid_echoes if e["fidelity"] is not None]
        if len(fidelity_pairs) >= 5:
            fids = np.array([p[0] for p in fidelity_pairs])
            dists = np.array([p[1] for p in fidelity_pairs])
            fid_r, fid_p = spearmanr(fids, dists)
        else:
            fid_r, fid_p = 0.0, 1.0

        # 5. Weighted distance comparison
        w_echo_dists = []
        for rel in echoes:
            c1 = self.acp.get_coordinates(rel["source"])
            c2 = self.acp.get_coordinates(rel.get("target", ""))
            if c1 is not None and c2 is not None:
                w_echo_dists.append(weighted_distance(c1, c2))

        w_control_dists = []
        rng2 = np.random.default_rng(seed)
        attempts2 = 0
        while len(w_control_dists) < n_control and attempts2 < n_control * 20:
            i, j = rng2.choice(len(all_ids), size=2, replace=False)
            id1, id2 = all_ids[i], all_ids[j]
            if arch_traditions[id1] == arch_traditions[id2]:
                attempts2 += 1
                continue
            if (id1, id2) in echo_pair_set:
                attempts2 += 1
                continue
            c1 = self.acp.get_coordinates(id1)
            c2 = self.acp.get_coordinates(id2)
            w_control_dists.append(weighted_distance(c1, c2))
            attempts2 += 1

        w_echo_arr = np.array(w_echo_dists) if w_echo_dists else np.array([0.0])
        w_ctrl_arr = np.array(w_control_dists) if w_control_dists else np.array([0.0])

        if len(w_echo_arr) >= 5 and len(w_ctrl_arr) >= 5:
            w_u, w_p = mannwhitneyu(w_echo_arr, w_ctrl_arr, alternative="less")
            w_pool_std = np.sqrt((w_echo_arr.std()**2 + w_ctrl_arr.std()**2) / 2)
            w_d = (w_ctrl_arr.mean() - w_echo_arr.mean()) / w_pool_std if w_pool_std > 0 else 0.0
        else:
            w_u, w_p, w_d = 0.0, 1.0, 0.0

        weighted_section = {
            "echo_mean": round(float(w_echo_arr.mean()), 4),
            "control_mean": round(float(w_ctrl_arr.mean()), 4),
            "mann_whitney_p": round(float(w_p), 6),
            "cohens_d": round(float(w_d), 4),
            "improvement_over_unweighted": round(float(w_d) - float(cohens_d), 4),
        }

        # 6. Pass/fail criteria
        distance_pass = u_p < 0.05 and cohens_d > 0.3
        fidelity_pass = float(fid_r) < -0.2 and fid_p < 0.05

        # 7. Human review tables
        sorted_by_fidelity = sorted(
            [e for e in valid_echoes if e["fidelity"] is not None],
            key=lambda x: x["fidelity"], reverse=True,
        )
        sorted_by_distance = sorted(valid_echoes, key=lambda x: x["distance"])

        # Worst violators: high fidelity but large distance
        worst_violators = sorted(
            [e for e in valid_echoes if e["fidelity"] is not None and e["fidelity"] >= 0.7],
            key=lambda x: x["distance"], reverse=True,
        )

        return {
            "n_echo_pairs": len(valid_echoes),
            "n_control_pairs": len(control_distances),
            "echo_distance": {
                "mean": round(float(echo_distances.mean()), 4),
                "median": round(float(np.median(echo_distances)), 4),
                "std": round(float(echo_distances.std()), 4),
            },
            "control_distance": {
                "mean": round(float(control_arr.mean()), 4),
                "median": round(float(np.median(control_arr)), 4),
                "std": round(float(control_arr.std()), 4),
            },
            "mann_whitney": {
                "u_statistic": round(float(u_stat), 2),
                "p_value": round(float(u_p), 6),
                "cohens_d": round(float(cohens_d), 4),
            },
            "fidelity_correlation": {
                "n_pairs_with_fidelity": len(fidelity_pairs),
                "spearman_r": round(float(fid_r), 4),
                "spearman_p": round(float(fid_p), 6),
            },
            "verdicts": {
                "distance_test": {
                    "pass": distance_pass,
                    "criterion": "Echo pairs significantly closer than random (p<0.05, d>0.3)",
                    "result": f"p={u_p:.4f}, d={cohens_d:.4f}",
                },
                "fidelity_test": {
                    "pass": fidelity_pass,
                    "criterion": "Fidelity predicts distance (r<-0.2, p<0.05)",
                    "result": f"r={fid_r:.4f}, p={fid_p:.4f}",
                },
                "overall_pass": distance_pass and fidelity_pass,
            },
            "weighted_comparison": weighted_section,
            "human_review": {
                "highest_fidelity": sorted_by_fidelity[:10],
                "lowest_fidelity": sorted_by_fidelity[-10:] if len(sorted_by_fidelity) > 10 else sorted_by_fidelity,
                "closest_echoes": sorted_by_distance[:10],
                "worst_violators": worst_violators[:10],
            },
        }
