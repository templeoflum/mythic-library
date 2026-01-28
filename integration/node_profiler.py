"""Derive empirical Miroglyph node profiles from Library + ACP data.

Two independent approaches combined:
  - Condition profiles: position-based (segments binned by narrative position)
  - Arc profiles: motif-based (entities from pattern-tagged segments)
  - Node profiles: intersection of arc entity set with condition bin entity set
"""
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integration.unified_loader import UnifiedLoader
from integration.acp_loader import AXES

# Map named cross-cultural patterns to Miroglyph arcs.
# This is the initial hypothesis — Phase 3 validation tests whether it holds.
ARC_PATTERN_MAPPING = {
    "D": [  # Descent / Shadow
        "descent_to_underworld",
        "dying_and_rising_god",
        "world_destruction_renewal",
        "divine_conflict",
        "dragon_slaying",
        "forbidden_knowledge",
    ],
    "R": [  # Resonance / Mirror
        "transformation_metamorphosis",
        "trickster",
        "prophecy_fate",
        "hero_cycle",
    ],
    "E": [  # Emergence / Mythogenesis
        "cosmogony_creation",
        "creation_of_humanity",
        "theft_of_fire",
        "miraculous_birth",
        "abandoned_child_hero",
        "quest_for_immortality",
        "great_mother",
        "world_flood",
    ],
}

MIN_SEGMENTS_PER_TEXT = 6  # Texts must have >= 6 segments for condition binning


class NodeProfiler:
    def __init__(self, unified: UnifiedLoader):
        self.unified = unified
        self._entity_coord_cache: Dict[str, Optional[np.ndarray]] = {}

    def _get_entity_coords(self, entity_name: str) -> Optional[np.ndarray]:
        """Get ACP coordinates for a library entity via mapping. Cached."""
        if entity_name in self._entity_coord_cache:
            return self._entity_coord_cache[entity_name]

        coords = self.unified.get_entity_coordinates(entity_name)
        self._entity_coord_cache[entity_name] = coords
        return coords

    def _entities_to_coords(self, entity_names: List[str]) -> np.ndarray:
        """Convert a list of entity names to an array of 8D coordinates.

        Returns (N, 8) array for entities that have ACP mappings.
        """
        coords = []
        for name in entity_names:
            c = self._get_entity_coords(name)
            if c is not None:
                coords.append(c)
        if not coords:
            return np.empty((0, len(AXES)))
        return np.array(coords)

    def _compute_profile(self, coords: np.ndarray, entity_names: List[str]) -> dict:
        """Compute a profile dict from coordinate array."""
        if len(coords) == 0:
            return {
                "mean_coordinates": [0.5] * len(AXES),
                "std_coordinates": [0.0] * len(AXES),
                "n_entities": 0,
                "sample_entities": [],
                "confidence": 0.0,
            }

        mean = np.mean(coords, axis=0)
        std = np.std(coords, axis=0) if len(coords) > 1 else np.zeros(len(AXES))

        # Collect the names of entities that actually had coordinates
        mapped_names = [n for n in entity_names if self._get_entity_coords(n) is not None]

        return {
            "mean_coordinates": mean.tolist(),
            "std_coordinates": std.tolist(),
            "n_entities": len(coords),
            "sample_entities": mapped_names[:10],
            "confidence": min(1.0, len(coords) / 10.0),  # Saturates at 10 entities
        }

    # ── Condition Profiles (position-based) ──

    def compute_condition_profiles(self, n_bins: int = 6) -> Dict[int, dict]:
        """Bin segments by narrative position across all texts.

        For each text with >= MIN_SEGMENTS_PER_TEXT segments, divides ordered
        segments into n_bins equal bins and collects entities per bin.
        Returns {condition_code: profile_dict}.
        """
        seg_counts = self.unified.library.get_segments_per_text()
        eligible_texts = [
            tid for tid, cnt in seg_counts.items() if cnt >= MIN_SEGMENTS_PER_TEXT
        ]

        # Collect entities per bin across all texts
        bin_entities: Dict[int, List[str]] = defaultdict(list)

        for text_id in eligible_texts:
            segments = self.unified.library.get_text_segments_ordered(text_id)
            if not segments:
                continue
            total = len(segments)
            for seg in segments:
                ordinal = seg["ordinal"]
                # Map ordinal (1-based) to bin (1-indexed)
                ratio = (ordinal - 1) / max(total - 1, 1)
                bin_idx = min(n_bins, int(ratio * n_bins) + 1)
                bin_entities[bin_idx].extend(seg["entity_names"])

        # Compute profiles per bin
        profiles = {}
        condition_names = {
            1: "Dawn/Initiation",
            2: "Immersion/Encounter",
            3: "Crucible/Crisis",
            4: "Alignment/Harmony",
            5: "Unveiling/Wisdom",
            6: "Return/Integration",
        }

        for bin_idx in range(1, n_bins + 1):
            entities = list(set(bin_entities.get(bin_idx, [])))
            coords = self._entities_to_coords(entities)
            profile = self._compute_profile(coords, entities)
            profile["label"] = condition_names.get(bin_idx, f"Bin {bin_idx}")
            profile["n_texts"] = len(eligible_texts)
            profile["total_entity_mentions"] = len(bin_entities.get(bin_idx, []))
            profiles[bin_idx] = profile

        return profiles

    # ── Arc Profiles (motif-based) ──

    def compute_arc_profiles(self) -> Dict[str, dict]:
        """Derive arc centroids from entities in pattern-tagged segments.

        Uses ARC_PATTERN_MAPPING to classify named patterns into arcs,
        then collects entities from segments tagged with those patterns' motifs.
        """
        arc_labels = {
            "D": "Descent/Shadow",
            "R": "Resonance/Mirror",
            "E": "Emergence/Mythogenesis",
        }

        profiles = {}
        for arc_code, pattern_names in ARC_PATTERN_MAPPING.items():
            # Collect all motif codes for this arc's patterns
            all_motif_codes = []
            patterns_used = []
            for pname in pattern_names:
                codes = self.unified.library.get_pattern_motif_codes(pname)
                if codes:
                    all_motif_codes.extend(codes)
                    patterns_used.append(pname)

            all_motif_codes = list(set(all_motif_codes))

            # Get entities from segments tagged with these motifs
            entities = self.unified.library.get_entities_for_motif_codes(all_motif_codes)
            entities = list(set(entities))
            coords = self._entities_to_coords(entities)
            profile = self._compute_profile(coords, entities)
            profile["label"] = arc_labels.get(arc_code, arc_code)
            profile["patterns_used"] = patterns_used
            profile["motif_codes"] = all_motif_codes
            profiles[arc_code] = profile

        return profiles

    # ── Combined Node Profiles ──

    def compute_node_profiles(
        self,
        condition_profiles: Optional[Dict] = None,
        arc_profiles: Optional[Dict] = None,
    ) -> Dict[str, dict]:
        """Combine arc and condition profiles to get 18 node profiles.

        For each node (arc x condition):
        - Intersect the arc's entity set with the condition's position bin
        - If intersection has 3+ mapped entities, compute direct centroid
        - Otherwise, use weighted average of arc and condition centroids
        """
        if condition_profiles is None:
            condition_profiles = self.compute_condition_profiles()
        if arc_profiles is None:
            arc_profiles = self.compute_arc_profiles()

        # Rebuild entity sets per arc
        arc_entity_sets: Dict[str, set] = {}
        for arc_code, pattern_names in ARC_PATTERN_MAPPING.items():
            all_motif_codes = []
            for pname in pattern_names:
                codes = self.unified.library.get_pattern_motif_codes(pname)
                all_motif_codes.extend(codes)
            entities = self.unified.library.get_entities_for_motif_codes(
                list(set(all_motif_codes))
            )
            arc_entity_sets[arc_code] = set(entities)

        # Rebuild entity sets per condition bin
        seg_counts = self.unified.library.get_segments_per_text()
        eligible_texts = [
            tid for tid, cnt in seg_counts.items() if cnt >= MIN_SEGMENTS_PER_TEXT
        ]
        bin_entity_sets: Dict[int, set] = defaultdict(set)
        for text_id in eligible_texts:
            segments = self.unified.library.get_text_segments_ordered(text_id)
            if not segments:
                continue
            total = len(segments)
            for seg in segments:
                ordinal = seg["ordinal"]
                ratio = (ordinal - 1) / max(total - 1, 1)
                bin_idx = min(6, int(ratio * 6) + 1)
                for ent in seg["entity_names"]:
                    bin_entity_sets[bin_idx].add(ent)

        # Compute profiles for each of the 18 nodes
        node_profiles = {}
        for node_id in self.unified.miroglyph.get_all_node_ids():
            node = self.unified.miroglyph.get_node(node_id)
            arc_code = node.arc_code
            cond = node.condition_code

            # Intersect
            arc_ents = arc_entity_sets.get(arc_code, set())
            cond_ents = bin_entity_sets.get(cond, set())
            intersection = arc_ents & cond_ents
            intersection_list = list(intersection)

            coords = self._entities_to_coords(intersection_list)

            if len(coords) >= 3:
                # Direct profile from intersection
                profile = self._compute_profile(coords, intersection_list)
                profile["method"] = "direct"
            else:
                # Weighted blend of arc and condition centroids
                arc_mean = np.array(arc_profiles[arc_code]["mean_coordinates"])
                cond_mean = np.array(condition_profiles[cond]["mean_coordinates"])
                arc_conf = arc_profiles[arc_code]["confidence"]
                cond_conf = condition_profiles[cond]["confidence"]

                # Weight by relative confidence
                total_conf = arc_conf + cond_conf
                if total_conf > 0:
                    w_arc = arc_conf / total_conf
                    w_cond = cond_conf / total_conf
                else:
                    w_arc = w_cond = 0.5

                blended_mean = w_arc * arc_mean + w_cond * cond_mean

                # Use entities from both sets for sample names
                combined_ents = list(arc_ents | cond_ents)[:10]
                profile = {
                    "mean_coordinates": blended_mean.tolist(),
                    "std_coordinates": [0.0] * len(AXES),
                    "n_entities": len(coords),
                    "sample_entities": [
                        n for n in intersection_list
                        if self._get_entity_coords(n) is not None
                    ][:10],
                    "confidence": min(arc_conf, cond_conf) * 0.5,
                    "method": "interpolated",
                    "blend_weights": {"arc": round(w_arc, 3), "condition": round(w_cond, 3)},
                }

            # Add node metadata
            profile["node_id"] = node_id
            profile["arc"] = node.arc_primary
            profile["condition"] = node.condition_primary
            profile["title"] = node.title

            # Compute dominant primordials from the intersection entities
            profile["dominant_primordials"] = self._compute_primordials(intersection_list)

            node_profiles[node_id] = profile

        return node_profiles

    def _compute_primordials(self, entity_names: List[str]) -> List[dict]:
        """Find dominant primordial archetypes for a set of entities."""
        primordial_weights: Dict[str, List[float]] = defaultdict(list)

        for name in entity_names:
            mapping = self.unified.mapper.get_mapping(name)
            if not mapping:
                continue
            instantiations = self.unified.acp.get_instantiations(mapping.acp_archetype_id)
            for inst in instantiations:
                pid = inst.get("primordial", "")
                weight = inst.get("weight", 0.5)
                primordial_weights[pid].append(weight)

        # Average weights and sort
        results = []
        for pid, weights in primordial_weights.items():
            results.append({
                "primordial_id": pid,
                "mean_weight": round(float(np.mean(weights)), 3),
                "count": len(weights),
            })
        results.sort(key=lambda x: -x["mean_weight"] * x["count"])
        return results[:5]

    # ── Output ──

    def compute_all(self) -> dict:
        """Run full profiling pipeline. Returns complete output dict."""
        print("  Computing condition profiles (position-based)...")
        condition_profiles = self.compute_condition_profiles()

        print("  Computing arc profiles (motif-based)...")
        arc_profiles = self.compute_arc_profiles()

        print("  Computing node profiles (intersection)...")
        node_profiles = self.compute_node_profiles(condition_profiles, arc_profiles)

        # Count methods
        direct = sum(1 for p in node_profiles.values() if p.get("method") == "direct")
        interp = sum(1 for p in node_profiles.values() if p.get("method") == "interpolated")

        output = {
            "version": "1.0",
            "method": "position_bin_x_motif_cluster",
            "axes": AXES,
            "stats": {
                "direct_profiles": direct,
                "interpolated_profiles": interp,
                "total_nodes": len(node_profiles),
            },
            "condition_profiles": {
                str(k): v for k, v in condition_profiles.items()
            },
            "arc_profiles": arc_profiles,
            "node_profiles": node_profiles,
        }
        return output

    def save(self, output_path: str) -> dict:
        """Compute profiles and save to JSON."""
        output = self.compute_all()

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        return output


if __name__ == "__main__":
    from datetime import datetime, timezone

    print("=" * 60)
    print("Miroglyph Node Profiler")
    print("=" * 60)

    print("\n[Init] Loading unified system...")
    unified = UnifiedLoader()

    print("[Profile] Deriving node profiles...")
    profiler = NodeProfiler(unified)
    output_path = str(PROJECT_ROOT / "outputs" / "miroglyph" / "node_profiles.json")
    result = profiler.save(output_path)

    print(f"\n[Done] Saved to {output_path}")
    print(f"  Profiles: {result['stats']['direct_profiles']} direct, "
          f"{result['stats']['interpolated_profiles']} interpolated")

    # Print summary
    print("\n── Arc Centroids ──")
    for arc_code in ["D", "R", "E"]:
        p = result["arc_profiles"][arc_code]
        coords = p["mean_coordinates"]
        print(f"  {arc_code} ({p['label']}): n={p['n_entities']}, "
              f"conf={p['confidence']:.2f}")
        for i, axis in enumerate(AXES):
            print(f"    {axis}: {coords[i]:.3f}")

    print("\n── Node Summary ──")
    for nid in sorted(result["node_profiles"].keys(),
                      key=lambda x: (x[0], int(x[1:]))):
        p = result["node_profiles"][nid]
        print(f"  {nid} ({p['title']}): n={p['n_entities']}, "
              f"method={p['method']}, conf={p['confidence']:.2f}")

    unified.close()
