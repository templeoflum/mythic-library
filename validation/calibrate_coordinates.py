"""Calibrate ACP coordinates using empirical co-occurrence data.

Uses gradient descent to nudge 8D coordinates so that Euclidean distances
better predict narrative co-occurrence. Applies small perturbations to
preserve ACP's theoretical structure while improving empirical fit.
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
from integration.acp_loader import ACPLoader, AXES
from integration.library_loader import LibraryLoader
from integration.entity_mapper import EntityMapper


class CoordinateCalibrator:
    def __init__(self, acp: ACPLoader, library: LibraryLoader, mapper: EntityMapper):
        self.acp = acp
        self.library = library
        self.mapper = mapper

    def _build_training_data(self, exclude_entities: Optional[List[str]] = None) -> Tuple[
        List[str], np.ndarray, np.ndarray
    ]:
        """Build arrays of archetype IDs, coordinates, and pairwise target similarities.

        Returns:
            arch_ids: list of archetype IDs (one per mapped entity)
            coords: (N, 8) array of current coordinates
            targets: (N, N) symmetric matrix of target similarities
                     (higher = should be closer together)
        """
        exclude = set(exclude_entities or [])

        # Get valid mappings
        valid = []
        for m in self.mapper.mappings:
            if m.library_entity in exclude:
                continue
            c = self.acp.get_coordinates(m.acp_archetype_id)
            if c is not None:
                valid.append(m)

        # Deduplicate by archetype ID (keep first entity per archetype)
        seen_arch = {}
        for m in valid:
            if m.acp_archetype_id not in seen_arch:
                seen_arch[m.acp_archetype_id] = m

        mappings = list(seen_arch.values())
        n = len(mappings)

        arch_ids = [m.acp_archetype_id for m in mappings]
        coords = np.array([self.acp.get_coordinates(aid) for aid in arch_ids])

        # Build co-occurrence matrix using all entity names mapped to each archetype
        # (an archetype may have multiple library entities)
        arch_entities = {}
        for m in valid:
            arch_entities.setdefault(m.acp_archetype_id, []).append(m.library_entity)

        coocc_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                total = 0
                for e1 in arch_entities.get(arch_ids[i], []):
                    for e2 in arch_entities.get(arch_ids[j], []):
                        total += self.library.get_entity_cooccurrence(e1, e2)
                coocc_matrix[i, j] = total
                coocc_matrix[j, i] = total

        # Convert co-occurrence to target similarity
        # Use log(1 + coocc) to compress the scale, then normalize to [0, 1]
        log_coocc = np.log1p(coocc_matrix)
        max_val = log_coocc.max()
        if max_val > 0:
            targets = log_coocc / max_val
        else:
            targets = log_coocc

        return arch_ids, coords, targets

    def calibrate(
        self,
        learning_rate: float = 0.005,
        max_steps: int = 200,
        max_shift: float = 0.10,
        exclude_entities: Optional[List[str]] = None,
        axis_weights: Optional[np.ndarray] = None,
    ) -> Dict:
        """Run gradient descent to calibrate coordinates.

        Parameters:
            learning_rate: Step size for gradient updates.
            max_steps: Maximum optimization iterations.
            max_shift: Maximum allowed coordinate shift per dimension (preserves ACP structure).
            exclude_entities: Entities to exclude (e.g., ["Set"]).
            axis_weights: Optional (8,) array of per-axis weights. Axes with
                weight 0 are frozen and excluded from distance computation.
                Default: equal weights (all 1.0).

        Returns:
            Dict with calibrated coordinates, before/after metrics, and shift statistics.
        """
        arch_ids, original_coords, targets = self._build_training_data(exclude_entities)
        n, d = original_coords.shape
        coords = original_coords.copy()

        # Axis weights: default to uniform
        if axis_weights is None:
            w = np.ones(d)
        else:
            w = np.asarray(axis_weights, dtype=float)

        # Target distance = 1 - similarity (scaled)
        target_distances = 1.0 - targets

        # Pre-compute upper triangle indices for vectorized operations
        idx_i, idx_j = np.triu_indices(n, k=1)
        target_upper = target_distances[idx_i, idx_j]
        n_pairs = len(idx_i)

        def compute_loss(coords):
            # Vectorized: compute all pairwise weighted distances at once
            diffs = coords[idx_i] - coords[idx_j]  # (n_pairs, d)
            dists = np.sqrt(np.sum(w * diffs ** 2, axis=1))  # (n_pairs,)
            return float(np.mean((dists - target_upper) ** 2))

        initial_loss = compute_loss(coords)

        # Gradient descent (vectorized)
        for step in range(max_steps):
            diffs = coords[idx_i] - coords[idx_j]  # (n_pairs, d)
            dists = np.sqrt(np.sum(w * diffs ** 2, axis=1)) + 1e-8  # (n_pairs,)
            scales = 2.0 * (dists - target_upper) / dists  # (n_pairs,)
            # Per-pair gradient contribution: scales[:, None] * w * diffs
            pair_grads = scales[:, None] * w * diffs  # (n_pairs, d)

            # Accumulate gradients using np.add.at for both i and j indices
            grad = np.zeros_like(coords)
            np.add.at(grad, idx_i, pair_grads)
            np.add.at(grad, idx_j, -pair_grads)

            grad /= n_pairs
            coords -= learning_rate * grad

            # Clamp coordinates to [0, 1]
            coords = np.clip(coords, 0.0, 1.0)

            # Clamp shift to max_shift
            shift = coords - original_coords
            shift = np.clip(shift, -max_shift, max_shift)
            coords = original_coords + shift

        final_loss = compute_loss(coords)

        # Compute shift statistics
        shifts = coords - original_coords
        shift_magnitudes = np.sqrt(np.sum(shifts ** 2, axis=1))

        # Build calibrated coordinate dict
        calibrated = {}
        for i, arch_id in enumerate(arch_ids):
            calibrated[arch_id] = {
                axis: round(float(coords[i, j]), 4)
                for j, axis in enumerate(AXES)
            }

        # Build shift details
        shift_details = {}
        for i, arch_id in enumerate(arch_ids):
            name = self.acp.archetypes[arch_id].get("name", arch_id)
            shift_details[arch_id] = {
                "name": name,
                "magnitude": round(float(shift_magnitudes[i]), 4),
                "per_axis": {
                    axis: round(float(shifts[i, j]), 4)
                    for j, axis in enumerate(AXES)
                }
            }

        return {
            "entity_count": n,
            "dimensions": d,
            "initial_loss": round(float(initial_loss), 6),
            "final_loss": round(float(final_loss), 6),
            "loss_reduction_pct": round((1 - final_loss / initial_loss) * 100, 1) if initial_loss > 0 else 0,
            "mean_shift": round(float(np.mean(shift_magnitudes)), 4),
            "max_shift": round(float(np.max(shift_magnitudes)), 4),
            "calibrated_coordinates": calibrated,
            "shift_details": shift_details,
            "params": {
                "learning_rate": learning_rate,
                "max_steps": max_steps,
                "max_shift_per_dim": max_shift,
            }
        }

    def apply_calibration(self, calibrated: Dict[str, Dict[str, float]]) -> int:
        """Apply calibrated coordinates back to the ACP loader (in-memory only).

        Returns the number of archetypes updated.
        """
        updated = 0
        for arch_id, new_coords in calibrated.items():
            if arch_id in self.acp.archetypes:
                self.acp.archetypes[arch_id]["spectralCoordinates"] = new_coords
                updated += 1
        return updated
