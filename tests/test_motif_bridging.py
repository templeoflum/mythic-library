#!/usr/bin/env python3
"""Fixture tests for validation/v2_tests/motif_bridging.py (Test 4).

Ten mapped entities alternate between two traditions and sit 0.1 apart on
one axis. Entity i carries motifs M{i}..M{i+3}, so motif overlap falls as
distance grows and every Jaccard value is known by hand. Nothing here reads
the ACP data or the database.
"""
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integration.acp_loader import ACPLoader, AXES  # noqa: E402
from validation.v2_tests.motif_bridging import MotifBridgingTest  # noqa: E402

N = 10
WINDOW = 4


def name(i):
    return f"E{i}"


def fake_acp():
    archetypes = {}
    for i in range(N):
        c = {axis: 0.0 for axis in AXES}
        c["order-chaos"] = round(0.1 * i, 1)
        archetypes[f"arch:T-{i}"] = {"name": name(i), "spectralCoordinates": c}
    archetypes["arch:T-NOCOORD"] = {"name": "No coordinates"}
    acp = ACPLoader.__new__(ACPLoader)  # skip loading files
    acp.archetypes = archetypes
    return acp


class FakeLibrary:
    def __init__(self, n=N):
        self.n = n

    def get_all_entities(self):
        ents = [SimpleNamespace(canonical_name=name(i), primary_tradition="AA" if i % 2 == 0 else "BB")
                for i in range(self.n)]
        return ents + [SimpleNamespace(canonical_name="Unplaced", primary_tradition="AA")]

    def get_all_motif_codes(self):
        return [f"M{k}" for k in range(self.n + WINDOW)]

    def get_motif_entities(self, code):
        k = int(code[1:])
        return [name(i) for i in range(self.n) if i <= k < i + WINDOW]


def fake_mapper(n=N):
    mappings = [SimpleNamespace(library_entity=name(i), acp_archetype_id=f"arch:T-{i}") for i in range(n)]
    mappings.append(SimpleNamespace(library_entity="Unplaced", acp_archetype_id="arch:T-NOCOORD"))
    return SimpleNamespace(mappings=mappings)


@pytest.fixture(scope="module")
def result():
    return MotifBridgingTest(fake_acp(), FakeLibrary(), fake_mapper()).run()


def test_only_cross_tradition_pairs(result):
    # alternating traditions: pairs an odd number of steps apart, 9+7+5+3+1
    assert result["n_cross_tradition_pairs"] == 25


def test_jaccard_values(result):
    # 1 step: 3 shared of 5 = 0.6; 3 steps: 1 of 7; 5+ steps: none
    top = result["human_review"]["highest_motif_overlap"]
    assert {p["jaccard"] for p in top[:9]} == {0.6}
    assert top[0]["shared_motifs"] == 3
    diag = result["binary_sharing_diagnostic"]
    assert (diag["n_sharing"], diag["n_nonsharing"], diag["sharing_pct"]) == (16, 9, 64.0)


def test_quartile_comparison(result):
    jd = result["jaccard_distribution"]
    assert (jd["q25"], jd["q75"], jd["n_high_overlap"], jd["n_low_overlap"]) == (0.0, 0.6, 9, 9)
    qc = result["quartile_comparison"]
    assert qc["high_overlap_mean_distance"] == 0.1
    assert qc["low_overlap_mean_distance"] == round((5 * 0.5 + 3 * 0.7 + 1 * 0.9) / 9, 4)


def test_verdicts(result):
    assert result["correlation"]["spearman_r"] < -0.05
    assert bool(result["verdicts"]["correlation_test"]["pass"]) is True
    assert bool(result["verdicts"]["quartile_test"]["pass"]) is True
    assert bool(result["verdicts"]["overall_pass"]) is True


def test_three_axis_subset_matches_when_only_a_subset_axis_varies(result):
    # the only axis that varies is order-chaos, which is in the subset
    assert result["three_axis_subset"]["spearman_r"] == result["correlation"]["spearman_r"]


def test_closest_pairs_first(result):
    closest = result["human_review"]["closest_cross_tradition"]
    assert closest[0]["distance"] == 0.1
    assert {closest[0]["tradition1"], closest[0]["tradition2"]} == {"AA", "BB"}


def test_too_few_mapped_entities():
    out = MotifBridgingTest(fake_acp(), FakeLibrary(), fake_mapper(n=8)).run()
    assert out == {"error": "Only 8 mapped entities"}
