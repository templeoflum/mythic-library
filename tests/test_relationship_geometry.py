#!/usr/bin/env python3
"""Fixture tests for validation/v2_tests/relationship_geometry.py (Test 3).

Hand-built archetypes. Every coordinate is 0.5 except the one or two axes
a pair is meant to differ on, so each pair's per-axis difference, its axis
of largest difference and the polar-axis counts can be worked out by hand.
Nothing here reads the ACP data.
"""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integration.acp_loader import ACPLoader, AXES  # noqa: E402
from validation.v2_tests.relationship_geometry import RelationshipGeometryTest  # noqa: E402

OC, LS, AD, ST = "order-chaos", "light-shadow", "ascent-descent", "stasis-transformation"


def coords(**diff):
    out = {axis: 0.5 for axis in AXES}
    for key, value in diff.items():
        out[key.replace("_", "-")] = value
    return out


def fake_acp(third_pair_diff=0.3):
    """Four POLAR_OPPOSITE pairs with a declared axis, plus pairs that are left out.

    p1: 0.8 apart on its declared axis (order-chaos), which is also its largest difference.
    p2: 0.6 apart on its declared axis (light-shadow), also its largest difference.
    p3: `third_pair_diff` apart on its declared axis (ascent-descent), 0.7 apart on order-chaos.
    p4: declared axis "axis:not-an-axis", which matches no ACP axis.
    """
    a = {}

    def pair(name, src, tgt, rel):
        a[f"t:{name}-s"] = {"name": f"{name} source", "spectralCoordinates": src,
                            "relationships": [dict(rel, target=f"t:{name}-t")]}
        a[f"t:{name}-t"] = {"name": f"{name} target", "spectralCoordinates": tgt, "relationships": []}

    polar = {"type": "POLAR_OPPOSITE"}
    pair("p1", coords(order_chaos=0.1), coords(order_chaos=0.9), dict(polar, axis=f"axis:{OC}"))
    pair("p2", coords(light_shadow=0.2), coords(light_shadow=0.8), dict(polar, axis=LS))
    pair("p3", coords(ascent_descent=0.5, order_chaos=0.15),
         coords(ascent_descent=0.5 + third_pair_diff, order_chaos=0.85), dict(polar, axis=f"axis:{AD}"))
    pair("p4", coords(order_chaos=0.0), coords(order_chaos=1.0), dict(polar, axis="axis:not-an-axis"))
    pair("p5", coords(light_shadow=0.0), coords(light_shadow=0.95), polar)  # no declared axis

    # COMPLEMENT pairs sit close together, so the two types separate cleanly.
    for i, gap in enumerate([0.01, 0.02, 0.03]):
        pair(f"c{i}", coords(order_chaos=0.5), coords(order_chaos=0.5 + gap), {"type": "COMPLEMENT"})

    # EVOLUTION: e0 moves toward transformation, e1 away from it.
    pair("e0", coords(stasis_transformation=0.3), coords(stasis_transformation=0.7), {"type": "EVOLUTION"})
    pair("e1", coords(stasis_transformation=0.7), coords(stasis_transformation=0.4), {"type": "EVOLUTION"})

    # Left out: a relationship whose target has no coordinates.
    a["t:p1-s"]["relationships"].append({"type": "POLAR_OPPOSITE", "target": "t:nocoord", "axis": OC})
    a["t:nocoord"] = {"name": "No coordinates"}

    acp = ACPLoader.__new__(ACPLoader)  # skip loading files
    acp.archetypes = a
    return acp


@pytest.fixture(scope="module")
def result():
    return RelationshipGeometryTest(fake_acp()).run()


def test_relationship_counts_skip_pairs_without_coordinates(result):
    assert result["relationship_counts"] == {
        "POLAR_OPPOSITE": 5, "COMPLEMENT": 3, "SHADOW": 0, "EVOLUTION": 2, "ANTAGONIST": 0,
    }


def test_polar_axis_counts(result):
    polar = result["polar_opposite_tests"]
    # p1-p4 declare an axis; p5 doesn't. A declared axis that matches no ACP axis
    # (p4) stays in the denominator and counts toward neither figure.
    assert polar["n_with_declared_axis"] == 4
    assert polar["axis_diff_gt_05_count"] == 2          # p1, p2
    assert polar["axis_diff_gt_05_pct"] == 50.0
    assert polar["max_diff_matches_declared_count"] == 2  # p1, p2
    assert polar["max_diff_matches_declared_pct"] == 50.0


def test_distance_by_type(result):
    d = result["distance_by_type"]
    assert d["COMPLEMENT"] == {"n_pairs": 3, "mean": 0.02, "median": 0.02, "std": 0.0082}
    assert d["POLAR_OPPOSITE"]["n_pairs"] == 5
    assert d["RANDOM"]["n_pairs"] == 500
    assert "SHADOW" not in d


def test_kruskal_wallis_uses_types_with_three_or_more_pairs(result):
    kw = result["kruskal_wallis"]
    assert kw["groups_tested"] == ["POLAR_OPPOSITE", "COMPLEMENT"]
    # 5 POLAR distances all above 3 COMPLEMENT ones: H = 5.0, p = 0.0253
    assert kw["statistic"] == 5.0
    assert kw["p_value"] == pytest.approx(0.025347, abs=1e-6)


def test_evolution_direction(result):
    assert result["evolution_direction"] == {
        "n_pairs": 2, "correct_direction_count": 1, "correct_direction_pct": 50.0,
    }


def test_verdicts_at_50_percent(result):
    v = result["verdicts"]
    assert v["polar_axis_diff"]["pass"] is False      # needs >= 70%
    assert v["polar_axis_diff"]["result"] == "50.0% (2/4)"
    assert v["polar_max_axis"]["pass"] is True        # needs >= 50%
    assert v["type_differentiation"]["pass"] is True
    assert v["overall_pass"] is False


def test_overall_pass_needs_polar_axis_and_type_differentiation():
    # p3 now 0.6 apart on its declared axis: 3/4 = 75% clear the 0.5 bar.
    v = RelationshipGeometryTest(fake_acp(third_pair_diff=0.6)).run()["verdicts"]
    assert v["polar_axis_diff"]["result"] == "75.0% (3/4)"
    assert v["polar_axis_diff"]["pass"] is True
    assert v["overall_pass"] is True


def test_the_diff_must_exceed_half():
    # exactly 0.5 apart on the declared axis does not count
    polar = RelationshipGeometryTest(fake_acp(third_pair_diff=0.5)).run()["polar_opposite_tests"]
    assert polar["axis_diff_gt_05_count"] == 2


def test_same_seed_same_result():
    one = RelationshipGeometryTest(fake_acp()).run(seed=7)
    two = RelationshipGeometryTest(fake_acp()).run(seed=7)
    assert one["distance_by_type"]["RANDOM"] == two["distance_by_type"]["RANDOM"]
