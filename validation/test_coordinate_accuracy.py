"""Test if ACP coordinate distances predict narrative co-occurrence."""
import numpy as np
from scipy.stats import pearsonr, spearmanr
from typing import Dict, List, Tuple

from integration.acp_loader import ACPLoader
from integration.library_loader import LibraryLoader
from integration.entity_mapper import EntityMapper


class CoordinateValidation:
    def __init__(self, acp: ACPLoader, library: LibraryLoader, mapper: EntityMapper):
        self.acp = acp
        self.library = library
        self.mapper = mapper

    def test_distance_correlation(self, exclude_entities: List[str] = None) -> Dict:
        """
        Core hypothesis: Smaller ACP distance -> Higher narrative co-occurrence.

        Uses all mapped entity pairs (not sampling) since the dataset
        is small enough to compute exhaustively.

        exclude_entities: list of entity names to skip (e.g., ["Set"] for known false positives)
        """
        exclude = set(exclude_entities or [])

        # Get all mapped entities that have ACP coordinates
        valid_mappings = []
        for m in self.mapper.mappings:
            if m.library_entity in exclude:
                continue
            coords = self.acp.get_coordinates(m.acp_archetype_id)
            if coords is not None:
                valid_mappings.append(m)

        if len(valid_mappings) < 2:
            return {
                "error": "Insufficient mapped entities with coordinates",
                "valid_count": len(valid_mappings),
            }

        distances = []
        cooccurrences = []
        pairs = []

        for i, m1 in enumerate(valid_mappings):
            for m2 in valid_mappings[i + 1:]:
                dist = self.acp.calculate_distance(
                    m1.acp_archetype_id, m2.acp_archetype_id
                )
                if dist is None:
                    continue

                coocc = self.library.get_entity_cooccurrence(
                    m1.library_entity, m2.library_entity
                )

                distances.append(dist)
                cooccurrences.append(coocc)
                pairs.append((m1.library_entity, m2.library_entity))

        if len(distances) < 10:
            return {
                "error": "Insufficient valid pairs for correlation",
                "valid_pairs": len(distances),
            }

        # Filter to pairs with nonzero co-occurrence for a second analysis
        nonzero_mask = [c > 0 for c in cooccurrences]
        nonzero_distances = [d for d, nz in zip(distances, nonzero_mask) if nz]
        nonzero_coocc = [c for c, nz in zip(cooccurrences, nonzero_mask) if nz]

        # Full correlation (includes zero co-occurrence)
        pearson_r, pearson_p = pearsonr(distances, cooccurrences)
        spearman_r, spearman_p = spearmanr(distances, cooccurrences)

        result = {
            "total_pairs": len(distances),
            "pairs_with_cooccurrence": sum(nonzero_mask),
            "pairs_without_cooccurrence": len(distances) - sum(nonzero_mask),
            "all_pairs": {
                "pearson_r": round(float(pearson_r), 4),
                "pearson_p": round(float(pearson_p), 6),
                "spearman_r": round(float(spearman_r), 4),
                "spearman_p": round(float(spearman_p), 6),
            },
            "stats": {
                "mean_distance": round(float(np.mean(distances)), 4),
                "std_distance": round(float(np.std(distances)), 4),
                "mean_cooccurrence": round(float(np.mean(cooccurrences)), 4),
                "max_cooccurrence": int(max(cooccurrences)),
                "median_cooccurrence": round(float(np.median(cooccurrences)), 1),
            },
        }

        # Non-zero only correlation
        if len(nonzero_distances) >= 10:
            nz_pearson_r, nz_pearson_p = pearsonr(nonzero_distances, nonzero_coocc)
            nz_spearman_r, nz_spearman_p = spearmanr(nonzero_distances, nonzero_coocc)
            result["nonzero_pairs"] = {
                "count": len(nonzero_distances),
                "pearson_r": round(float(nz_pearson_r), 4),
                "pearson_p": round(float(nz_pearson_p), 6),
                "spearman_r": round(float(nz_spearman_r), 4),
                "spearman_p": round(float(nz_spearman_p), 6),
            }

        # Hypothesis evaluation
        r = pearson_r
        p = pearson_p
        if p >= 0.05:
            result["hypothesis"] = "INCONCLUSIVE"
            result["interpretation"] = (
                "No statistically significant correlation between "
                "ACP distance and narrative co-occurrence"
            )
        elif r < -0.4:
            result["hypothesis"] = "STRONGLY SUPPORTED"
            result["interpretation"] = (
                "Strong negative correlation: closer archetypes "
                "co-occur significantly more in narratives"
            )
        elif r < -0.2:
            result["hypothesis"] = "SUPPORTED"
            result["interpretation"] = (
                "Moderate negative correlation: ACP coordinates "
                "have some predictive power for co-occurrence"
            )
        elif r > 0.2:
            result["hypothesis"] = "CONTRADICTED"
            result["interpretation"] = (
                "Unexpected positive correlation: distant archetypes "
                "co-occur more often (investigate outliers)"
            )
        else:
            result["hypothesis"] = "WEAK"
            result["interpretation"] = (
                "Weak correlation: ACP coordinates may need "
                "calibration against empirical data"
            )

        # Find outliers
        result["outliers"] = self._find_outliers(distances, cooccurrences, pairs)

        # Top co-occurring pairs
        top_pairs = sorted(
            zip(distances, cooccurrences, pairs),
            key=lambda x: -x[1],
        )[:15]
        result["top_cooccurring"] = [
            {
                "entities": list(p),
                "distance": round(d, 4),
                "cooccurrence": c,
            }
            for d, c, p in top_pairs
        ]

        return result

    def _find_outliers(
        self,
        distances: List[float],
        cooccurrences: List[int],
        pairs: List[Tuple[str, str]],
        threshold: float = 2.0,
    ) -> List[Dict]:
        """Find pairs with unexpected distance/co-occurrence ratios."""
        if not distances:
            return []

        mean_d = np.mean(distances)
        std_d = np.std(distances)
        mean_c = np.mean(cooccurrences)
        std_c = np.std(cooccurrences)

        outliers = []
        for dist, coocc, pair in zip(distances, cooccurrences, pairs):
            z_d = (dist - mean_d) / std_d if std_d > 0 else 0
            z_c = (coocc - mean_c) / std_c if std_c > 0 else 0

            # Outlier: high distance + high co-occurrence, or low distance + low co-occurrence
            anomaly = abs(z_d + z_c)  # same sign = anomalous
            if z_d > 0 and z_c > 1:  # far apart but co-occur heavily
                outliers.append({
                    "entities": list(pair),
                    "distance": round(dist, 4),
                    "cooccurrence": int(coocc),
                    "anomaly_type": "far_but_cooccur",
                    "anomaly_score": round(float(anomaly), 3),
                })
            elif z_d < -1 and coocc == 0:  # close but never co-occur
                outliers.append({
                    "entities": list(pair),
                    "distance": round(dist, 4),
                    "cooccurrence": 0,
                    "anomaly_type": "close_but_absent",
                    "anomaly_score": round(float(abs(z_d)), 3),
                })

        return sorted(outliers, key=lambda x: -x["anomaly_score"])[:20]

    def test_per_tradition_correlation(self, min_entities: int = 3) -> Dict:
        """Test distance-vs-co-occurrence correlation within each tradition.

        For each tradition with at least min_entities mapped entities,
        compute Spearman correlation on intra-tradition entity pairs.
        This reveals whether ACP coordinates are better calibrated for
        some traditions than others.
        """
        # Group mappings by tradition
        from collections import defaultdict
        tradition_mappings = defaultdict(list)
        for m in self.mapper.mappings:
            # Look up tradition from library
            entities = self.library.get_all_entities()
            entity_dict = {e.canonical_name: e for e in entities}
            e = entity_dict.get(m.library_entity)
            if e and e.primary_tradition:
                coords = self.acp.get_coordinates(m.acp_archetype_id)
                if coords is not None:
                    tradition_mappings[e.primary_tradition].append(m)

        results = {}
        for tradition, mappings in sorted(tradition_mappings.items()):
            if len(mappings) < min_entities:
                continue

            distances = []
            cooccurrences = []

            for i, m1 in enumerate(mappings):
                for m2 in mappings[i + 1:]:
                    dist = self.acp.calculate_distance(
                        m1.acp_archetype_id, m2.acp_archetype_id
                    )
                    if dist is None:
                        continue
                    coocc = self.library.get_entity_cooccurrence(
                        m1.library_entity, m2.library_entity
                    )
                    distances.append(dist)
                    cooccurrences.append(coocc)

            if len(distances) < 3:
                continue

            # Check if all values are constant (can't compute correlation)
            if len(set(distances)) < 2 or len(set(cooccurrences)) < 2:
                results[tradition] = {
                    "entity_count": len(mappings),
                    "pair_count": len(distances),
                    "note": "Insufficient variance for correlation",
                }
                continue

            spearman_r, spearman_p = spearmanr(distances, cooccurrences)
            pairs_with_coocc = sum(1 for c in cooccurrences if c > 0)

            results[tradition] = {
                "entity_count": len(mappings),
                "pair_count": len(distances),
                "pairs_with_cooccurrence": pairs_with_coocc,
                "spearman_r": round(float(spearman_r), 4),
                "spearman_p": round(float(spearman_p), 6),
                "mean_distance": round(float(np.mean(distances)), 4),
                "mean_cooccurrence": round(float(np.mean(cooccurrences)), 2),
            }

        return results

    def test_primordial_clustering(self) -> Dict:
        """Test if archetypes sharing the same primordial cluster together."""
        primordial_groups: Dict[str, List[str]] = {}

        for m in self.mapper.mappings:
            instantiations = self.acp.get_instantiations(m.acp_archetype_id)
            for inst in instantiations:
                prim = inst.get("primordial", "")
                if prim:
                    primordial_groups.setdefault(prim, []).append(m.acp_archetype_id)

        results = {}
        for prim, arch_ids in primordial_groups.items():
            unique_ids = list(set(arch_ids))
            if len(unique_ids) < 2:
                continue

            within_distances = []
            for i, a1 in enumerate(unique_ids):
                for a2 in unique_ids[i + 1:]:
                    d = self.acp.calculate_distance(a1, a2)
                    if d is not None:
                        within_distances.append(d)

            if within_distances:
                prim_name = prim.split(":")[-1] if ":" in prim else prim
                results[prim_name] = {
                    "archetype_count": len(unique_ids),
                    "mean_distance": round(float(np.mean(within_distances)), 4),
                    "std_distance": round(float(np.std(within_distances)), 4),
                    "min_distance": round(float(min(within_distances)), 4),
                    "max_distance": round(float(max(within_distances)), 4),
                }

        return results
