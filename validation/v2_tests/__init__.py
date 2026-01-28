"""ACP v2 Validation Tests — Cross-cultural structural equivalence.

Shared utilities and constants used across all v2 test modules.
"""
import numpy as np

from integration.acp_loader import AXES


# ==============================================================================
# Empirical Axis Weights
# Derived from Phase 10 analysis: axes with higher discriminative power
# (measured by how strongly they differentiate relationship types) get higher
# weights. Weights are normalized so the mean weight = 1.0.
#
# Source: Phase 10 axis contribution analysis across CULTURAL_ECHO,
# POLAR_OPPOSITE, COMPLEMENT, and SHADOW relationship types.
# ==============================================================================
EMPIRICAL_AXIS_WEIGHTS = {
    "creation-destruction": 2.17,
    "order-chaos": 1.19,
    "individual-collective": 0.93,
    "light-shadow": 0.80,
    "active-receptive": 0.79,
    "voluntary-fated": 0.77,
    "stasis-transformation": 0.74,
    "ascent-descent": 0.20,
}

# Pre-computed weight vector in AXES order for fast numpy operations
WEIGHT_VECTOR = np.array([EMPIRICAL_AXIS_WEIGHTS[a] for a in AXES])

# Normalized so that unweighted distance is preserved in scale
# (sum of squared weights = n_axes for scale parity)
_norm_factor = np.sqrt(len(AXES) / np.sum(WEIGHT_VECTOR ** 2))
WEIGHT_VECTOR_NORMALIZED = WEIGHT_VECTOR * _norm_factor


def weighted_distance(c1: np.ndarray, c2: np.ndarray, normalized: bool = True) -> float:
    """Compute weighted Euclidean distance between two coordinate vectors.

    Args:
        c1: First coordinate vector (8D).
        c2: Second coordinate vector (8D).
        normalized: If True, use scale-normalized weights so that weighted
                    distances are comparable to unweighted distances.

    Returns:
        Weighted Euclidean distance as a float.
    """
    w = WEIGHT_VECTOR_NORMALIZED if normalized else WEIGHT_VECTOR
    diff = c1 - c2
    return float(np.sqrt(np.sum(w ** 2 * diff ** 2)))


def weighted_pdist(coords: np.ndarray, normalized: bool = True) -> np.ndarray:
    """Compute pairwise weighted distances for a matrix of coordinates.

    Args:
        coords: (N, 8) array of coordinate vectors.
        normalized: If True, use scale-normalized weights.

    Returns:
        Condensed distance matrix (like scipy.spatial.distance.pdist).
    """
    w = WEIGHT_VECTOR_NORMALIZED if normalized else WEIGHT_VECTOR
    n = coords.shape[0]
    dists = []
    for i in range(n):
        for j in range(i + 1, n):
            diff = coords[i] - coords[j]
            d = float(np.sqrt(np.sum(w ** 2 * diff ** 2)))
            dists.append(d)
    return np.array(dists)
