"""Test Thompson motif clustering in ACP spectral space."""
import numpy as np
from collections import defaultdict
from typing import Dict, List

from integration.acp_loader import ACPLoader, AXES
from integration.library_loader import LibraryLoader
from integration.entity_mapper import EntityMapper


class MotifClustering:
    def __init__(self, acp: ACPLoader, library: LibraryLoader, mapper: EntityMapper):
        self.acp = acp
        self.library = library
        self.mapper = mapper

    def analyze_motif_signatures(self) -> Dict:
        """
        For each Thompson motif, compute:
        1. Which mapped entities are associated with it
        2. Their centroid in 8D space
        3. Variance (how tightly do they cluster?)
        """
        motif_codes = self.library.get_all_motif_codes()
        signatures = {}

        for motif in motif_codes:
            entities = self.library.get_motif_entities(motif)

            coords_list = []
            mapped_entities = []

            for entity_name in entities:
                mapping = self.mapper.get_mapping(entity_name)
                if mapping:
                    coords = self.acp.get_coordinates(mapping.acp_archetype_id)
                    if coords is not None:
                        coords_list.append(coords)
                        mapped_entities.append(entity_name)

            if len(coords_list) < 2:
                continue

            coords_array = np.array(coords_list)
            centroid = np.mean(coords_array, axis=0)
            variance = np.var(coords_array, axis=0)
            total_variance = float(np.sum(variance))

            signatures[motif] = {
                "entity_count": len(mapped_entities),
                "entities": mapped_entities,
                "centroid": {
                    axis: round(float(centroid[i]), 4) for i, axis in enumerate(AXES)
                },
                "variance_per_axis": {
                    axis: round(float(variance[i]), 4) for i, axis in enumerate(AXES)
                },
                "total_variance": round(total_variance, 4),
                "is_clustered": total_variance < 0.5,
            }

        return signatures

    def find_motif_category_patterns(self) -> Dict:
        """
        Group motifs by Thompson category letter and find
        which ACP axes correlate with which motif categories.
        """
        signatures = self.analyze_motif_signatures()

        # Group by first character of motif code
        categories: Dict[str, List[np.ndarray]] = defaultdict(list)
        for motif, data in signatures.items():
            if motif and len(motif) > 0:
                cat = motif[0]
                centroid_array = np.array(
                    [data["centroid"][axis] for axis in AXES]
                )
                categories[cat].append(centroid_array)

        # Compute average centroid per category
        category_centroids = {}
        for cat, centroid_list in sorted(categories.items()):
            if len(centroid_list) >= 2:
                avg = np.mean(centroid_list, axis=0)
                std = np.std(centroid_list, axis=0)
                category_centroids[cat] = {
                    "motif_count": len(centroid_list),
                    "centroid": {
                        axis: round(float(avg[i]), 4) for i, axis in enumerate(AXES)
                    },
                    "std": {
                        axis: round(float(std[i]), 4) for i, axis in enumerate(AXES)
                    },
                    "dominant_axis": AXES[int(np.argmax(np.abs(avg - 0.5)))],
                }

        return {
            "motif_signatures": signatures,
            "category_centroids": category_centroids,
            "summary": {
                "total_motifs_analyzed": len(signatures),
                "clustered_count": sum(
                    1 for s in signatures.values() if s["is_clustered"]
                ),
                "spread_count": sum(
                    1 for s in signatures.values() if not s["is_clustered"]
                ),
                "categories_analyzed": len(category_centroids),
            },
        }
