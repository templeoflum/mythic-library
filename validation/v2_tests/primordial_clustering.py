"""Test 2: Primordial Profile Clustering.

Tests whether archetypes sharing primordial instantiation profiles
(e.g. both strongly instantiate Trickster + Psychopomp) cluster
together in ACP 8D spectral space.
"""
import numpy as np
from scipy.stats import spearmanr
from scipy.spatial.distance import pdist, squareform
from typing import Dict, List
from collections import defaultdict

from integration.acp_loader import ACPLoader, AXES


class PrimordialClusteringTest:
    def __init__(self, acp: ACPLoader):
        self.acp = acp

    def _build_primordial_vectors(self) -> Dict[str, np.ndarray]:
        """Build a primordial vector for each archetype.

        Each dimension is the instantiation weight for one primordial
        (0.0 if not instantiated).
        """
        primordial_ids = self.acp.get_primordial_ids()
        prim_index = {pid: i for i, pid in enumerate(primordial_ids)}
        n_prims = len(primordial_ids)

        vectors = {}
        for arch_id in self.acp.archetypes:
            vec = np.zeros(n_prims)
            for inst in self.acp.get_instantiations(arch_id):
                pid = inst.get("primordial", "")
                weight = inst.get("weight", 0.0)
                if pid in prim_index:
                    vec[prim_index[pid]] = weight
            if vec.sum() > 0:
                vectors[arch_id] = vec

        return vectors, primordial_ids

    def run(self, n_permutations: int = 1000, seed: int = 42) -> Dict:
        rng = np.random.default_rng(seed)

        prim_vectors, primordial_ids = self._build_primordial_vectors()

        valid_ids = [
            aid for aid in prim_vectors
            if self.acp.get_coordinates(aid) is not None
        ]

        if len(valid_ids) < 10:
            return {"error": f"Only {len(valid_ids)} archetypes with both coordinates and primordial data"}

        coords = np.array([self.acp.get_coordinates(aid) for aid in valid_ids])
        prim_vecs = np.array([prim_vectors[aid] for aid in valid_ids])
        n = len(valid_ids)

        # 1. Vectorized pairwise distances
        # Spectral distances (Euclidean in 8D)
        sd_arr = pdist(coords, metric="euclidean")

        # Primordial cosine similarity (1 - cosine_distance)
        # pdist returns distances; we want similarity = 1 - distance
        prim_cos_dists = pdist(prim_vecs, metric="cosine")
        # Replace NaN (from zero vectors) with 1.0 (max distance = 0 similarity)
        prim_cos_dists = np.nan_to_num(prim_cos_dists, nan=1.0)
        ps_arr = 1.0 - prim_cos_dists

        obs_r, obs_p = spearmanr(ps_arr, sd_arr)

        # 2. Vectorized permutation test: shuffle rows of primordial matrix
        # Pre-compute the full cosine similarity matrix for permutation reindexing
        prim_sim_matrix = 1.0 - squareform(prim_cos_dists)
        np.fill_diagonal(prim_sim_matrix, 1.0)
        idx_i, idx_j = np.triu_indices(n, k=1)

        null_rs = []
        for _ in range(n_permutations):
            perm = rng.permutation(n)
            shuffled_sims = prim_sim_matrix[np.ix_(perm, perm)][idx_i, idx_j]
            r, _ = spearmanr(shuffled_sims, sd_arr)
            null_rs.append(float(r))

        null_arr = np.array(null_rs)
        perm_p = float(np.mean(null_arr <= float(obs_r)))

        # 3. Cluster by dominant primordial
        dominant = {}
        for aid in valid_ids:
            vec = prim_vectors[aid]
            dom_idx = int(np.argmax(vec))
            dom_prim = primordial_ids[dom_idx]
            dominant.setdefault(dom_prim, []).append(aid)

        within_dists = []
        between_dists = []
        for prim, members in dominant.items():
            if len(members) < 2:
                continue
            member_coords = [self.acp.get_coordinates(m) for m in members]
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    within_dists.append(float(np.linalg.norm(member_coords[i] - member_coords[j])))

        # Between-cluster: sample pairs from different clusters
        cluster_keys = [k for k in dominant if len(dominant[k]) >= 2]
        for ci in range(len(cluster_keys)):
            for cj in range(ci + 1, len(cluster_keys)):
                m1 = dominant[cluster_keys[ci]]
                m2 = dominant[cluster_keys[cj]]
                # Sample up to 5 pairs per cluster pair
                for _ in range(min(5, len(m1) * len(m2))):
                    a1 = m1[rng.integers(len(m1))]
                    a2 = m2[rng.integers(len(m2))]
                    c1 = self.acp.get_coordinates(a1)
                    c2 = self.acp.get_coordinates(a2)
                    between_dists.append(float(np.linalg.norm(c1 - c2)))

        within_mean = float(np.mean(within_dists)) if within_dists else 0
        between_mean = float(np.mean(between_dists)) if between_dists else 0
        cluster_ratio = (between_mean - within_mean) / between_mean if between_mean > 0 else 0

        # 4. Per-primordial centroid analysis (for human review)
        primordial_centroids = {}
        for prim, members in dominant.items():
            if len(members) < 2:
                continue
            member_coords = np.array([self.acp.get_coordinates(m) for m in members])
            centroid = member_coords.mean(axis=0)
            member_names = [
                self.acp.archetypes.get(m, {}).get("name", m) for m in members
            ]
            primordial_centroids[prim] = {
                "n_members": len(members),
                "centroid": {AXES[k]: round(float(centroid[k]), 4) for k in range(len(AXES))},
                "members": member_names[:10],  # Cap at 10 for readability
                "within_cluster_mean_dist": round(float(np.mean([
                    np.linalg.norm(member_coords[i] - member_coords[j])
                    for i in range(len(members))
                    for j in range(i + 1, len(members))
                ])), 4) if len(members) >= 2 else 0,
            }

        # 5. Verdicts
        correlation_pass = float(obs_r) < -0.15 and perm_p < 0.01
        cluster_pass = cluster_ratio >= 0.10

        return {
            "n_archetypes": n,
            "n_pairs": len(sd_arr),
            "n_primordials_used": len(primordial_ids),
            "correlation": {
                "spearman_r": round(float(obs_r), 4),
                "spearman_p": round(float(obs_p), 6),
            },
            "permutation_test": {
                "n_permutations": n_permutations,
                "empirical_p": round(perm_p, 4),
                "null_mean": round(float(null_arr.mean()), 4),
                "null_std": round(float(null_arr.std()), 4),
            },
            "cluster_analysis": {
                "n_clusters": len([k for k in dominant if len(dominant[k]) >= 2]),
                "within_cluster_mean": round(within_mean, 4),
                "between_cluster_mean": round(between_mean, 4),
                "separation_ratio": round(cluster_ratio, 4),
                "n_within_pairs": len(within_dists),
                "n_between_pairs": len(between_dists),
            },
            "verdicts": {
                "correlation_test": {
                    "pass": correlation_pass,
                    "criterion": "Spearman r < -0.15 (permutation p < 0.01)",
                    "result": f"r={obs_r:.4f}, perm_p={perm_p:.4f}",
                },
                "cluster_test": {
                    "pass": cluster_pass,
                    "criterion": "Within-cluster distance >=10% smaller than between-cluster",
                    "result": f"ratio={cluster_ratio:.4f} ({cluster_ratio*100:.1f}% separation)",
                },
                "overall_pass": correlation_pass and cluster_pass,
            },
            "human_review": {
                "primordial_centroids": primordial_centroids,
            },
        }
