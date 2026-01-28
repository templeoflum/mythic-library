"""Archetype-Node affinity scoring.

For each ACP archetype, compute its affinity to each of the 18 Miroglyph nodes
based on Gaussian proximity to the node's empirical centroid in 8D space.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integration.acp_loader import ACPLoader, AXES
from integration.node_profiler import NodeProfiler
from integration.unified_loader import UnifiedLoader


class NodeAffinityScorer:
    """Score archetypes against Miroglyph node profiles."""

    def __init__(self, acp: ACPLoader, node_profiles: Dict[str, dict], sigma: float = None):
        self.acp = acp
        self.node_profiles = node_profiles
        self.node_centroids: Dict[str, np.ndarray] = {}

        # Build centroids
        for nid, profile in node_profiles.items():
            self.node_centroids[nid] = np.array(profile["mean_coordinates"])

        # Auto-calibrate sigma from average node std if not provided
        if sigma is None:
            stds = []
            for profile in node_profiles.values():
                stds.extend(profile.get("std_coordinates", []))
            self.sigma = float(np.mean(stds)) if stds else 0.3
            if self.sigma < 0.05:
                self.sigma = 0.15  # Floor to avoid degenerate scores
        else:
            self.sigma = sigma

    def score_archetype(self, archetype_id: str) -> Optional[dict]:
        """Score one archetype against all 18 nodes.

        Returns dict with per-node affinities, best node, and arc affinities.
        """
        coords = self.acp.get_coordinates(archetype_id)
        if coords is None:
            return None

        scores = {}
        for nid, centroid in self.node_centroids.items():
            distance = float(np.linalg.norm(coords - centroid))
            affinity = float(np.exp(-distance ** 2 / (2 * self.sigma ** 2)))
            scores[nid] = {"distance": round(distance, 4), "affinity": round(affinity, 4)}

        # Rank nodes by affinity
        ranked = sorted(scores.items(), key=lambda x: -x[1]["affinity"])
        for rank, (nid, _) in enumerate(ranked, 1):
            scores[nid]["rank"] = rank

        best_node = ranked[0][0] if ranked else None

        # Arc affinities (average of each arc's 6 nodes)
        arc_affinities = {}
        for arc in ["D", "R", "E"]:
            arc_nodes = [nid for nid in scores if nid.startswith(arc)]
            if arc_nodes:
                arc_affinities[arc] = round(
                    float(np.mean([scores[n]["affinity"] for n in arc_nodes])), 4
                )

        return {
            "archetype_id": archetype_id,
            "name": self.acp.archetypes.get(archetype_id, {}).get("name", archetype_id),
            "best_node": best_node,
            "best_affinity": scores[best_node]["affinity"] if best_node else 0.0,
            "arc_affinities": arc_affinities,
            "node_scores": scores,
        }

    def score_all_archetypes(self) -> Dict[str, dict]:
        """Score all archetypes. Returns archetype_id -> score dict."""
        results = {}
        for arch_id in self.acp.archetypes:
            score = self.score_archetype(arch_id)
            if score:
                results[arch_id] = score
        return results

    def get_node_rankings(self, all_scores: Dict[str, dict], top_n: int = 20) -> Dict[str, list]:
        """For each node, get top-N archetypes ranked by affinity."""
        node_archetypes: Dict[str, list] = defaultdict(list)

        for arch_id, score in all_scores.items():
            for nid, node_score in score["node_scores"].items():
                node_archetypes[nid].append({
                    "archetype_id": arch_id,
                    "name": score["name"],
                    "affinity": node_score["affinity"],
                    "distance": node_score["distance"],
                })

        rankings = {}
        for nid in sorted(node_archetypes.keys(), key=lambda x: (x[0], int(x[1:]))):
            entries = sorted(node_archetypes[nid], key=lambda x: -x["affinity"])
            rankings[nid] = entries[:top_n]

        return rankings

    def get_archetype_rankings(self, all_scores: Dict[str, dict], top_n: int = 5) -> Dict[str, dict]:
        """For each archetype, get top-N nodes ranked by affinity."""
        rankings = {}
        for arch_id, score in all_scores.items():
            ranked_nodes = sorted(
                score["node_scores"].items(),
                key=lambda x: -x[1]["affinity"]
            )
            rankings[arch_id] = {
                "name": score["name"],
                "best_node": score["best_node"],
                "best_affinity": score["best_affinity"],
                "arc_affinities": score["arc_affinities"],
                "top_nodes": [
                    {"node_id": nid, "affinity": ns["affinity"], "distance": ns["distance"]}
                    for nid, ns in ranked_nodes[:top_n]
                ],
            }
        return rankings

    def save(self, all_scores: Dict[str, dict], output_path: str):
        """Save complete affinity data to JSON."""
        node_rankings = self.get_node_rankings(all_scores)
        archetype_rankings = self.get_archetype_rankings(all_scores)

        output = {
            "version": "1.0",
            "sigma": round(self.sigma, 4),
            "n_archetypes_scored": len(all_scores),
            "n_nodes": len(self.node_centroids),
            "node_rankings": node_rankings,
            "archetype_rankings": archetype_rankings,
        }

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        return output


if __name__ == "__main__":
    print("=" * 60)
    print("Archetype-Node Affinity Scorer")
    print("=" * 60)

    print("\n[Init] Loading unified system...")
    unified = UnifiedLoader()

    print("[Profile] Loading node profiles...")
    profiles_path = PROJECT_ROOT / "outputs" / "miroglyph" / "node_profiles.json"
    with open(profiles_path, "r", encoding="utf-8") as f:
        profiles_data = json.load(f)
    node_profiles = profiles_data["node_profiles"]

    print(f"[Score] Scoring {len(unified.acp.archetypes)} archetypes against {len(node_profiles)} nodes...")
    scorer = NodeAffinityScorer(unified.acp, node_profiles)
    all_scores = scorer.score_all_archetypes()

    output_path = str(PROJECT_ROOT / "outputs" / "miroglyph" / "archetype_affinities.json")
    result = scorer.save(all_scores, output_path)

    print(f"\n[Done] Saved to {output_path}")
    print(f"  Sigma: {result['sigma']}")
    print(f"  Archetypes scored: {result['n_archetypes_scored']}")

    # Print top 5 archetypes for each node
    print("\n── Top 5 Archetypes per Node ──")
    for nid in sorted(result["node_rankings"].keys(), key=lambda x: (x[0], int(x[1:]))):
        entries = result["node_rankings"][nid][:5]
        names = ", ".join(f"{e['name']}({e['affinity']:.2f})" for e in entries)
        print(f"  {nid}: {names}")

    unified.close()
