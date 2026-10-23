#!/usr/bin/env python3
"""Fixture tests for validation/falsification.py (Phase 9 criteria).

Stub ACP, library and mapper objects stand in for the real ones. Entity i
sits at i/8 on the first axis (exact in binary, so equal gaps tie), and
pairs closer on that axis co-occur more, so the first axis carries all
the signal. The second axis is noise, or a second copy of the signal
with signal_twice=True, and the other six are constant. Nothing reads the ACP data or the database.
"""
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integration.acp_loader import AXES  # noqa: E402
from validation.falsification import FalsificationTests  # noqa: E402

N = 8
NOISE = [0.9, 0.1, 0.7, 0.3, 0.0, 0.8, 0.2, 0.6]
TRADITIONS = ["A", "A", "A", "A", "A", "B", "B", ""]


class StubACP:
    def __init__(self, coords):
        self.coords = coords

    def get_coordinates(self, arch_id):
        c = self.coords.get(arch_id)
        return None if c is None else np.array(c, dtype=float)


class StubLibrary:
    def get_all_entities(self):
        return [SimpleNamespace(canonical_name=f"e{i}", primary_tradition=t)
                for i, t in enumerate(TRADITIONS)]

    def get_entity_cooccurrence(self, a, b):
        return 10 - abs(int(a[1:]) - int(b[1:]))


def make(n=N, signal_twice=False, extra_unmapped=True):
    coords = {}
    for i in range(n):
        c = [0.5] * 8
        c[0] = i / 8
        c[1] = i / 8 if signal_twice else NOISE[i]
        coords[f"a{i}"] = c
    mappings = [SimpleNamespace(library_entity=f"e{i}", acp_archetype_id=f"a{i}") for i in range(n)]
    if extra_unmapped:   # mapped to an archetype with no coordinates
        mappings.append(SimpleNamespace(library_entity="e99", acp_archetype_id="missing"))
    return FalsificationTests(StubACP(coords), StubLibrary(), SimpleNamespace(mappings=mappings))


# ── shared helpers ──

def test_valid_mappings_drop_missing_coordinates_and_exclusions():
    f = make()
    assert [m.library_entity for m in f._get_valid_mappings()] == [f"e{i}" for i in range(N)]
    assert len(f._get_valid_mappings(exclude_entities=["e0", "e1"])) == N - 2


def test_pairs_data():
    f = make(signal_twice=True)
    d, c = f._get_pairs_data(f._get_valid_mappings())
    assert len(d) == len(c) == N * (N - 1) // 2
    assert d[0] == pytest.approx(2 ** 0.5 / 8)   # e0-e1
    assert c[0] == 9


def test_formal_hypothesis_lists_four_criteria():
    h = make().formal_hypothesis()
    assert len(h["falsification_criteria"]) == 4
    assert h["success_threshold"]["maximum_p_value"] == 0.05


# ── tradition similarity ──

def test_tradition_similarity_counts():
    r = make().tradition_similarity_test()
    assert r["n_pairs"] == 28
    # five A's give 10 pairs, two B's give 1; the blank tradition never matches
    assert r["same_tradition_pairs"] == 11
    assert r["diff_tradition_pairs"] == 17
    assert r["intra_tradition_acp"]["n_pairs"] == 11
    assert r["intra_tradition_acp"]["spearman_r"] is not None


def test_tradition_similarity_winner_follows_the_larger_r():
    r = make(signal_twice=True).tradition_similarity_test()
    assert r["acp_8d_distance"]["spearman_r"] == -1.0
    acp, trad = r["acp_8d_distance"]["spearman_r"], r["tradition_similarity_1d"]["spearman_r"]
    assert r["acp_beats_tradition"] == (abs(acp) > abs(trad))
    assert r["acp_beats_tradition"] is True


def test_tradition_subsets_under_ten_pairs_are_none():
    r = make().tradition_similarity_test(exclude_entities=["e0", "e1"])
    assert r["same_tradition_pairs"] == 4
    assert r["intra_tradition_acp"]["spearman_r"] is None


@pytest.mark.parametrize("method", [
    "tradition_similarity_test", "axis_ablation_study", "coordinate_sensitivity",
])
def test_fewer_than_ten_pairs_is_an_error(method):
    assert getattr(make(n=4), method)() == {"error": "Insufficient pairs"}


# ── axis ablation ──

@pytest.fixture(scope="module")
def ablation():
    return make().axis_ablation_study()


def test_ablation_baseline_is_negative(ablation):
    assert ablation["n_pairs"] == 28
    assert -1.0 < ablation["full_8d_baseline"]["spearman_r"] < 0


def test_removing_the_signal_axis_hurts(ablation):
    first = ablation["ablation"][AXES[0]]
    assert first["delta_r"] > 0.005
    assert first["impact"].startswith("beneficial")


def test_removing_the_noise_axis_improves_and_is_flagged(ablation):
    second = ablation["ablation"][AXES[1]]
    assert second["reduced_spearman_r"] == -1.0
    assert second["delta_r"] < -0.005
    assert second["impact"].startswith("harmful")
    assert ablation["harmful_axes"] == [AXES[1]]
    assert ablation["falsification_check"].startswith("WARNING: 1 axis")


def test_constant_axes_are_noise(ablation):
    for axis in AXES[2:]:
        assert ablation["ablation"][axis]["delta_r"] == 0.0
        assert ablation["ablation"][axis]["impact"].startswith("noise")


def test_ranking_is_sorted_by_delta(ablation):
    deltas = [row["delta_r"] for row in ablation["ranking"]]
    assert deltas == sorted(deltas)
    assert len(deltas) == 8


def test_ablation_passes_without_a_harmful_axis():
    r = make(signal_twice=True).axis_ablation_study()
    assert r["harmful_axes"] == []
    assert r["falsification_check"].startswith("PASS")


# ── coordinate sensitivity ──

def test_zero_noise_reproduces_the_baseline():
    r = make().coordinate_sensitivity(noise_level=0.0, n_trials=5)
    base = r["baseline_spearman_r"]
    assert r["perturbed_distribution"]["min"] == r["perturbed_distribution"]["max"] == base
    assert r["pct_negative"] == 100.0
    assert r["robust"] is True
    assert r["falsification_check"].startswith("PASS")


def test_heavy_noise_is_not_robust():
    r = make().coordinate_sensitivity(noise_level=5.0, n_trials=40)
    assert r["robust"] is False
    assert r["falsification_check"].startswith("FAIL")


def test_sensitivity_is_seeded():
    one = make().coordinate_sensitivity(noise_level=0.2, n_trials=10, seed=7)
    two = make().coordinate_sensitivity(noise_level=0.2, n_trials=10, seed=7)
    assert one == two


def test_sensitivity_does_not_change_the_coordinates():
    f = make()
    before = {k: list(v) for k, v in f.acp.coords.items()}
    f.coordinate_sensitivity(noise_level=0.5, n_trials=3)
    assert f.acp.coords == before


# ── weighted variants ──

def test_unit_weights_match_the_unweighted_test():
    f = make()
    plain = f.tradition_similarity_test()
    weighted = f.tradition_similarity_test_weighted(np.ones(8))
    assert weighted["acp_weighted_distance"] == plain["acp_8d_distance"]
    assert weighted["n_dimensions"] == 8 and weighted["zeroed_axes"] == []


def test_zeroed_axis_is_dropped_from_weighted_runs():
    w = np.ones(8)
    w[1] = 0.0
    f = make()
    trad = f.tradition_similarity_test_weighted(w)
    assert trad["zeroed_axes"] == [AXES[1]] and trad["n_dimensions"] == 7
    assert trad["acp_weighted_distance"]["spearman_r"] == -1.0


def test_weighted_ablation_only_ablates_active_axes():
    w = np.ones(8)
    w[2] = 0.0
    abl = make(signal_twice=True).axis_ablation_study_weighted(w)
    assert abl["zeroed_axes"] == [AXES[2]] and abl["n_dimensions"] == 7
    assert set(abl["ablation"]) == set(AXES) - {AXES[2]}
    assert abl["weighted_baseline"]["spearman_r"] == -1.0
    assert abl["harmful_axes"] == []
    assert abl["falsification_check"].startswith("PASS")


def test_weighted_ablation_flags_a_harmful_axis():
    abl = make().axis_ablation_study_weighted(np.ones(8))
    assert abl["harmful_axes"] == [AXES[1]]
    assert abl["falsification_check"].startswith("WARNING: 1 axis")


# ── verdicts ──

GOOD = dict(
    tradition_result={"acp_beats_tradition": True},
    ablation_result={"harmful_axes": []},
    sensitivity_result={"robust": True, "pct_negative": 100.0},
)


@pytest.mark.parametrize("changes, passed, verdict_start", [
    ({}, 4, "ACP hypothesis SURVIVES"),
    ({"mantel_p": 0.2}, 3, "ACP hypothesis MOSTLY SURVIVES"),
    ({"mantel_p": 0.2, "tradition_result": {}}, 2, "ACP hypothesis PARTIALLY SURVIVES"),
    ({"mantel_p": 0.2, "tradition_result": {}, "ablation_result": {"harmful_axes": ["x"]}},
     1, "ACP hypothesis FAILS"),
])
def test_falsification_verdict_tiers(changes, passed, verdict_start):
    args = dict(GOOD, permutation_p=0.2, mantel_p=0.01)
    args.update(changes)
    v = make().falsification_verdict(**args)
    assert v["passed"] == passed and v["total"] == 4
    assert v["overall_verdict"].startswith(verdict_start)


def test_either_p_value_passes_significance():
    f = make()
    for perm, mantel, ok in [(0.01, 0.2, True), (0.2, 0.01, True), (0.05, 0.05, False)]:
        v = f.falsification_verdict(permutation_p=perm, mantel_p=mantel, **GOOD)
        assert v["criteria"][0]["pass"] is ok


def test_optimized_verdict_compares_with_original():
    f = make()
    v = f.optimized_verdict(
        permutation_p=0.2, mantel_p=0.01,
        weighted_tradition_result={"acp_beats_tradition": True, "n_dimensions": 7},
        weighted_ablation_result={"harmful_axes": []},
        sensitivity_result={"robust": True, "pct_negative": 100.0},
        original_verdict={"passed": 2},
    )
    assert v["passed"] == 4
    assert v["overall_verdict"] == "SURVIVES all falsification tests"
    assert v["vs_original"]["improvement"] == 2
    assert v["vs_original"]["summary"] == "Improved from 2/4 to 4/4"
    assert v["criteria"][1]["criterion"].startswith("Optimized 7D")

    same = f.optimized_verdict(0.2, 0.2, {}, {"harmful_axes": []}, {"robust": False},
                               original_verdict={"passed": 1})
    assert same["passed"] == 1 and same["vs_original"]["summary"] == "No change: 1/4"
