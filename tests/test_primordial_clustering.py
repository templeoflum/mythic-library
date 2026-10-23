#!/usr/bin/env python3
"""Fixture tests for validation/v2_tests/primordial_clustering.py (Test 2).

The fixture is a hand-built ACP with two four-member clusters placed so that
every within- and between-cluster distance is known, plus two singletons and
two archetypes the test must leave out. Nothing here reads the ACP data.
"""
import math
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integration.acp_loader import ACPLoader, AXES  # noqa: E402
from validation.v2_tests.primordial_clustering import PrimordialClusteringTest  # noqa: E402


def coords(**values):
    """Spectral coordinates with every axis set (unset axes are 0.0, not the loader's 0.5)."""
    out = {axis: 0.0 for axis in AXES}
    for index, value in values.items():
        out[AXES[int(index[1:])]] = value
    return out


def archetype(name, coordinates, weights):
    arch = {"name": name, "instantiates": [{"primordial": p, "weight": w} for p, w in weights.items()]}
    if coordinates is not None:
        arch["spectralCoordinates"] = coordinates
    return arch


def fake_acp(n_singletons=2):
    # Cluster P1: axis 0 = 0, on a unit circle in axes 1-2.
    # Cluster P2: axis 0 = 2, on a unit circle in axes 3-4.
    # Every P1-P2 pair is sqrt(2^2 + 1 + 1) = sqrt(6) apart.
    circle = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    archetypes = {}
    for i, (a, b) in enumerate(circle):
        archetypes[f"arch:T-P1-{i}"] = archetype(
            f"One {i}", coords(a0=0.0, a1=a, a2=b), {"prim:P1": 0.9, "prim:P2": 0.1})
        archetypes[f"arch:T-P2-{i}"] = archetype(
            f"Two {i}", coords(a0=2.0, a3=a, a4=b), {"prim:P2": 0.8, "prim:P1": 0.2})
    for i in range(n_singletons):
        archetypes[f"arch:T-S{i}"] = archetype(
            f"Single {i}", coords(a5=3.0 + i), {f"prim:S{i}": 1.0})
    archetypes["arch:T-NOPRIM"] = archetype("No primordials", coords(a6=1.0), {})
    archetypes["arch:T-NOCOORD"] = archetype("No coordinates", None, {"prim:P1": 1.0})
    archetypes["arch:T-UNKNOWN"] = archetype("Unknown primordial", coords(a7=1.0), {"prim:NONE": 1.0})

    acp = ACPLoader.__new__(ACPLoader)  # skip loading files
    acp.archetypes = archetypes
    acp.primordials = {p: {} for p in ["prim:P1", "prim:P2"] + [f"prim:S{i}" for i in range(n_singletons)]}
    return acp


WITHIN = (4 * math.sqrt(2) + 2 * 2) / 6   # four sides and two diagonals of each square
BETWEEN = math.sqrt(6)


@pytest.fixture(scope="module")
def result():
    return PrimordialClusteringTest(fake_acp()).run(n_permutations=50)


def test_counts_leave_out_archetypes_without_data(result):
    # 8 cluster members + 2 singletons; no-primordial, no-coordinate and
    # unknown-primordial archetypes are left out
    assert result["n_archetypes"] == 10
    assert result["n_pairs"] == 45
    assert result["n_primordials_used"] == 4


def test_cluster_distances_and_separation_ratio(result):
    ca = result["cluster_analysis"]
    assert ca["n_clusters"] == 2                 # singletons don't form clusters
    assert ca["n_within_pairs"] == 12            # 6 per cluster
    assert ca["n_between_pairs"] == 5            # sampled, capped at 5 per cluster pair
    assert ca["within_cluster_mean"] == round(WITHIN, 4)
    assert ca["between_cluster_mean"] == round(BETWEEN, 4)
    assert ca["separation_ratio"] == round((BETWEEN - WITHIN) / BETWEEN, 4)


def test_cluster_verdict_uses_ten_percent(result):
    verdict = result["verdicts"]["cluster_test"]
    assert verdict["pass"] is (result["cluster_analysis"]["separation_ratio"] >= 0.10)
    assert "% separation" in verdict["result"]


def test_centroids_for_review(result):
    centroids = result["human_review"]["primordial_centroids"]
    assert set(centroids) == {"prim:P1", "prim:P2"}
    assert centroids["prim:P2"]["n_members"] == 4
    assert centroids["prim:P2"]["centroid"][AXES[0]] == 2.0
    assert centroids["prim:P1"]["within_cluster_mean_dist"] == round(WITHIN, 4)


def test_permutation_summary_shape(result):
    perm = result["permutation_test"]
    assert perm["n_permutations"] == 50
    assert 0.0 <= perm["empirical_p"] <= 1.0
    corr = result["verdicts"]["correlation_test"]
    assert corr["pass"] is (result["correlation"]["spearman_r"] < -0.15 and perm["empirical_p"] < 0.01)
    assert result["verdicts"]["overall_pass"] is (corr["pass"] and result["verdicts"]["cluster_test"]["pass"])


def test_same_seed_same_result(result):
    again = PrimordialClusteringTest(fake_acp()).run(n_permutations=50)
    assert again == result


def test_too_few_archetypes():
    acp = fake_acp()
    for aid in [a for a in acp.archetypes if a.startswith("arch:T-P2")]:
        del acp.archetypes[aid]
    out = PrimordialClusteringTest(acp).run(n_permutations=5)
    assert out == {"error": "Only 6 archetypes with both coordinates and primordial data"}
