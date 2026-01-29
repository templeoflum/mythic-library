#!/usr/bin/env python3
"""Diagnose arc entity overlap and test exclusive assignment strategies.

This script answers:
1. How much do the 3 arc entity sets overlap?
2. What do per-pattern centroids look like in ACP space?
3. Does exclusive entity assignment produce separable arcs?
4. Would remapping patterns to different arcs help?
"""
import io
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integration.acp_loader import ACPLoader, AXES
from integration.library_loader import LibraryLoader
from integration.entity_mapper import EntityMapper
from integration.node_profiler import ARC_PATTERN_MAPPING

ACP_PATH = PROJECT_ROOT / "ACP"
DB_PATH = PROJECT_ROOT / "data" / "mythic_patterns.db"


def silhouette_score(coords, labels):
    """Simple silhouette score (no sklearn)."""
    unique = np.unique(labels)
    if len(unique) < 2 or len(coords) < 3:
        return -1.0
    scores = []
    for i in range(len(coords)):
        same = labels == labels[i]
        same_dists = np.linalg.norm(coords[same] - coords[i], axis=1)
        a_i = same_dists[same_dists > 0].mean() if same_dists[same_dists > 0].size > 0 else 0.0

        min_other = float("inf")
        for lbl in unique:
            if lbl == labels[i]:
                continue
            other = labels == lbl
            other_dists = np.linalg.norm(coords[other] - coords[i], axis=1)
            mean_other = other_dists.mean() if other_dists.size > 0 else float("inf")
            min_other = min(min_other, mean_other)

        s_i = (min_other - a_i) / max(a_i, min_other) if max(a_i, min_other) > 0 else 0.0
        scores.append(s_i)
    return float(np.mean(scores))


def quick_kmeans(coords, k, max_iter=50, seed=42):
    """Simple k-means returning labels."""
    rng = np.random.default_rng(seed)
    n = len(coords)
    # Init: random choice
    center_idx = rng.choice(n, size=k, replace=False)
    centers = coords[center_idx].copy()
    labels = np.zeros(n, dtype=int)
    for _ in range(max_iter):
        # Assign
        for i in range(n):
            dists = np.linalg.norm(centers - coords[i], axis=1)
            labels[i] = np.argmin(dists)
        # Update
        new_centers = np.zeros_like(centers)
        for c in range(k):
            mask = labels == c
            if mask.sum() > 0:
                new_centers[c] = coords[mask].mean(axis=0)
            else:
                new_centers[c] = centers[c]
        if np.allclose(new_centers, centers):
            break
        centers = new_centers
    return labels, centers


def main():
    print("=" * 65)
    print("  Arc Overlap Diagnostic")
    print("=" * 65)

    # Load data
    acp = ACPLoader(str(ACP_PATH))
    library = LibraryLoader(str(DB_PATH))
    mapper = EntityMapper(acp, library)
    mapper.auto_map_all()

    # ── 1. Current arc entity sets ───────────────────────────────
    print("\n── 1. Current Arc Entity Sets ──")

    arc_entities = {}  # arc -> set of entity names
    arc_entity_coords = {}  # arc -> list of (entity, coords)

    for arc_code, pattern_names in ARC_PATTERN_MAPPING.items():
        motif_codes = []
        for pname in pattern_names:
            codes = library.get_pattern_motif_codes(pname)
            motif_codes.extend(codes)
        motif_codes = list(set(motif_codes))

        entities = set(library.get_entities_for_motif_codes(motif_codes))
        arc_entities[arc_code] = entities

        coords_list = []
        for ent in entities:
            mapping = mapper.get_mapping(ent)
            if mapping:
                c = acp.get_coordinates(mapping.acp_archetype_id)
                if c is not None:
                    coords_list.append((ent, c))
        arc_entity_coords[arc_code] = coords_list

    for arc, ents in arc_entities.items():
        patterns = ARC_PATTERN_MAPPING[arc]
        n_with_coords = len(arc_entity_coords[arc])
        print(f"  Arc {arc}: {len(ents)} entities ({n_with_coords} with ACP coords)")
        print(f"    Patterns: {', '.join(patterns)}")

    # Overlap analysis
    print("\n  Pairwise Jaccard overlap:")
    arcs = list(arc_entities.keys())
    for i in range(len(arcs)):
        for j in range(i + 1, len(arcs)):
            a, b = arcs[i], arcs[j]
            intersection = arc_entities[a] & arc_entities[b]
            union = arc_entities[a] | arc_entities[b]
            jaccard = len(intersection) / len(union) if union else 0
            print(f"    {a} ∩ {b}: {len(intersection)}/{len(union)} entities = Jaccard {jaccard:.3f}")

    total = arc_entities["D"] | arc_entities["R"] | arc_entities["E"]
    in_all = arc_entities["D"] & arc_entities["R"] & arc_entities["E"]
    print(f"  In ALL 3 arcs: {len(in_all)}/{len(total)} ({len(in_all)/len(total)*100:.0f}%)")

    # ── 2. Per-pattern centroids ─────────────────────────────────
    print("\n── 2. Per-Pattern Centroids ──")

    pattern_centroids = {}
    for arc_code, pattern_names in ARC_PATTERN_MAPPING.items():
        for pname in pattern_names:
            codes = library.get_pattern_motif_codes(pname)
            entities = library.get_entities_for_motif_codes(codes)
            coords = []
            for ent in entities:
                mapping = mapper.get_mapping(ent)
                if mapping:
                    c = acp.get_coordinates(mapping.acp_archetype_id)
                    if c is not None:
                        coords.append(c)
            if coords:
                centroid = np.mean(coords, axis=0)
                pattern_centroids[pname] = {"arc": arc_code, "centroid": centroid, "n_entities": len(coords)}

    print(f"  {'Pattern':35s} {'Arc':>3s} {'N':>4s}  ", end="")
    for ax in AXES[:4]:
        print(f"  {ax[:6]:>6s}", end="")
    print()
    for pname, data in sorted(pattern_centroids.items(), key=lambda x: x[1]["arc"]):
        c = data["centroid"]
        print(f"  {pname:35s} {data['arc']:>3s} {data['n_entities']:4d}  ", end="")
        for i in range(4):
            print(f"  {c[i]:6.3f}", end="")
        print()

    # ── 3. K-means on pattern centroids ──────────────────────────
    print("\n── 3. K-Means on Pattern Centroids ──")

    centroid_matrix = np.array([v["centroid"] for v in pattern_centroids.values()])
    pnames = list(pattern_centroids.keys())

    for k in [2, 3, 4]:
        labels, centers = quick_kmeans(centroid_matrix, k)
        sil = silhouette_score(centroid_matrix, labels)
        print(f"\n  k={k}: silhouette = {sil:.4f}")
        for c in range(k):
            members = [pnames[i] for i in range(len(pnames)) if labels[i] == c]
            print(f"    Cluster {c}: {', '.join(members)}")

    # ── 4. Exclusive entity assignment ───────────────────────────
    print("\n── 4. Exclusive Entity Assignment ──")

    # For each entity, count segment appearances per arc's pattern motifs
    arc_motif_codes = {}
    for arc_code, pattern_names in ARC_PATTERN_MAPPING.items():
        codes = set()
        for pname in pattern_names:
            codes.update(library.get_pattern_motif_codes(pname))
        arc_motif_codes[arc_code] = codes

    # Count per-entity, per-arc segment appearances
    entity_arc_counts = defaultdict(lambda: defaultdict(int))  # entity -> {arc -> count}

    for arc_code, motif_codes_set in arc_motif_codes.items():
        if not motif_codes_set:
            continue
        codes_list = list(motif_codes_set)
        placeholders = ",".join("?" * len(codes_list))
        rows = library.conn.execute(f"""
            SELECT e.canonical_name, COUNT(DISTINCT mt.segment_id) as seg_count
            FROM motif_tags mt
            JOIN entity_mentions em ON mt.segment_id = em.segment_id
            JOIN entities e ON em.entity_id = e.entity_id
            WHERE mt.motif_code IN ({placeholders})
              AND mt.confidence >= 0.3
            GROUP BY e.canonical_name
        """, codes_list).fetchall()
        for row in rows:
            entity_arc_counts[row["canonical_name"]][arc_code] = row["seg_count"]

    # Assign each entity to its strongest arc
    exclusive_arc_entities = defaultdict(set)
    exclusive_arc_coords = defaultdict(list)

    for entity, arc_counts in entity_arc_counts.items():
        if not arc_counts:
            continue
        best_arc = max(arc_counts.items(), key=lambda x: x[1])[0]
        exclusive_arc_entities[best_arc].add(entity)

        mapping = mapper.get_mapping(entity)
        if mapping:
            c = acp.get_coordinates(mapping.acp_archetype_id)
            if c is not None:
                exclusive_arc_coords[best_arc].append(c)

    print("  Exclusive assignment results (current mapping):")
    for arc in ["D", "R", "E"]:
        n_ents = len(exclusive_arc_entities[arc])
        n_coords = len(exclusive_arc_coords[arc])
        print(f"    Arc {arc}: {n_ents} entities ({n_coords} with coords)")

    # Overlap check (should be zero)
    excl_overlap = exclusive_arc_entities["D"] & exclusive_arc_entities["R"] & exclusive_arc_entities["E"]
    print(f"  Entities in ALL 3: {len(excl_overlap)} (should be 0)")

    # Silhouette on exclusive sets
    all_coords_excl = []
    all_labels_excl = []
    label_map = {"D": 0, "R": 1, "E": 2}
    for arc in ["D", "R", "E"]:
        for c in exclusive_arc_coords[arc]:
            all_coords_excl.append(c)
            all_labels_excl.append(label_map[arc])

    if len(all_coords_excl) > 10:
        coords_arr = np.array(all_coords_excl)
        labels_arr = np.array(all_labels_excl)
        sil_excl = silhouette_score(coords_arr, labels_arr)
        print(f"\n  Silhouette (exclusive, 3 arcs): {sil_excl:.4f}")
        print(f"    (was -0.009 with overlapping sets)")

        # Also test k=2 exclusive
        km_labels, _ = quick_kmeans(coords_arr, 2)
        sil_km2 = silhouette_score(coords_arr, km_labels)
        print(f"  Silhouette (k-means k=2 on exclusive): {sil_km2:.4f}")

        # Per-axis Kruskal-Wallis on exclusive sets
        from scipy.stats import kruskal
        print("\n  Per-axis Kruskal-Wallis (exclusive):")
        groups = [np.array(exclusive_arc_coords[a]) for a in ["D", "R", "E"] if len(exclusive_arc_coords[a]) > 1]
        if len(groups) >= 2:
            for ax_idx, ax_name in enumerate(AXES):
                ax_groups = [g[:, ax_idx] for g in groups if g.shape[0] > 1]
                if len(ax_groups) >= 2:
                    stat, p = kruskal(*ax_groups)
                    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
                    print(f"    {ax_name:25s}  H={stat:7.2f}  p={p:.6f} {sig}")

        # Mann-Whitney on exclusive
        from scipy.stats import mannwhitneyu
        from scipy.spatial.distance import pdist, squareform
        dist_matrix = squareform(pdist(coords_arr))
        within_dists = []
        between_dists = []
        for a in range(len(labels_arr)):
            for b in range(a + 1, len(labels_arr)):
                if labels_arr[a] == labels_arr[b]:
                    within_dists.append(dist_matrix[a][b])
                else:
                    between_dists.append(dist_matrix[a][b])
        if within_dists and between_dists:
            stat_mw, p_mw = mannwhitneyu(
                np.array(between_dists), np.array(within_dists), alternative="greater"
            )
            print(f"\n  Mann-Whitney (between > within): p={p_mw:.6f}")
            print(f"    Within-arc mean:  {np.mean(within_dists):.4f}")
            print(f"    Between-arc mean: {np.mean(between_dists):.4f}")

    # ── 5. Check what k-means remapping would look like ──────────
    print("\n── 5. K-Means Remapping of Patterns ──")

    # Try k-means on the exclusive entity coords to find natural clusters
    # Then see which patterns best correspond to which cluster

    # Per-pattern exclusive entity coords
    pattern_excl_centroids = {}
    for pname, pdata in pattern_centroids.items():
        codes = library.get_pattern_motif_codes(pname)
        entities = library.get_entities_for_motif_codes(codes)
        # Only use entities exclusively assigned to this pattern's arc
        excl_coords_for_pattern = []
        arc = pdata["arc"]
        for ent in entities:
            if ent in exclusive_arc_entities[arc]:
                mapping = mapper.get_mapping(ent)
                if mapping:
                    c = acp.get_coordinates(mapping.acp_archetype_id)
                    if c is not None:
                        excl_coords_for_pattern.append(c)
        if excl_coords_for_pattern:
            pattern_excl_centroids[pname] = {
                "arc": arc,
                "centroid": np.mean(excl_coords_for_pattern, axis=0),
                "n_entities": len(excl_coords_for_pattern),
            }

    if pattern_excl_centroids:
        excl_centroid_matrix = np.array([v["centroid"] for v in pattern_excl_centroids.values()])
        excl_pnames = list(pattern_excl_centroids.keys())

        for k in [2, 3]:
            labels, centers = quick_kmeans(excl_centroid_matrix, k)
            sil = silhouette_score(excl_centroid_matrix, labels)
            print(f"\n  k={k} (exclusive centroids): silhouette = {sil:.4f}")
            for c_idx in range(k):
                members = [excl_pnames[i] for i in range(len(excl_pnames)) if labels[i] == c_idx]
                current_arcs = [pattern_excl_centroids[p]["arc"] for p in members]
                print(f"    Cluster {c_idx}: {', '.join(members)}")
                print(f"      Current arcs: {', '.join(current_arcs)}")

    # ── 6. Summary ──────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  SUMMARY")
    print("=" * 65)
    print(f"  Current overlap: {len(in_all)}/{len(total)} entities in all 3 arcs ({len(in_all)/len(total)*100:.0f}%)")
    print(f"  Current silhouette (k=3): -0.009")
    if len(all_coords_excl) > 10:
        print(f"  Exclusive silhouette (k=3): {sil_excl:.4f}")
        improvement = "IMPROVED" if sil_excl > 0 else "STILL NEGATIVE"
        print(f"  Status: {improvement}")
    print("=" * 65)

    library.close()


if __name__ == "__main__":
    main()
