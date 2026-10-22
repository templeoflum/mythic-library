"""Tests for the pure scoring and statistics helpers in validation/.

Small hand-worked fixtures only; nothing here reads the ACP data or the
database. Each expected value is worked out by hand from the helper's own
definition, so these pin what the helpers compute today.
"""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integration.acp_loader import AXES  # noqa: E402
from validation import fix_polar_coordinates as fpc  # noqa: E402
from validation.statistical_tests import StatisticalTests  # noqa: E402
from validation.v2_tests import (  # noqa: E402
    EMPIRICAL_AXIS_WEIGHTS,
    weighted_distance,
    weighted_pdist,
)
from validation.v2_tests.human_audit import HumanAuditTest  # noqa: E402
from validation.v2_tests.miroglyph_structure import _silhouette_score  # noqa: E402
from validation.v2_tests.relationship_geometry import RelationshipGeometryTest  # noqa: E402


def unit(axis, size=1.0):
    v = np.zeros(len(AXES))
    v[AXES.index(axis)] = size
    return v


# ── weighted_distance / weighted_pdist ───────────────────────

class TestWeightedDistance:
    def test_zero_for_identical(self):
        c = np.linspace(0.1, 0.8, 8)
        assert weighted_distance(c, c) == 0.0

    def test_symmetric(self):
        a, b = np.linspace(0, 1, 8), np.linspace(1, 0, 8)
        assert weighted_distance(a, b) == weighted_distance(b, a)

    @pytest.mark.parametrize("axis", AXES)
    def test_raw_weight_is_per_axis(self, axis):
        # A unit step on one axis costs exactly that axis's raw weight.
        d = weighted_distance(np.zeros(8), unit(axis), normalized=False)
        assert d == pytest.approx(EMPIRICAL_AXIS_WEIGHTS[axis])

    def test_normalized_keeps_scale(self):
        # Weights are normalised so sum(w^2) == n_axes: a unit step on
        # every axis has the same length as unweighted, sqrt(8).
        d = weighted_distance(np.zeros(8), np.ones(8))
        assert d == pytest.approx(math.sqrt(8))

    def test_normalized_ratio(self):
        a = weighted_distance(np.zeros(8), unit("creation-destruction"))
        b = weighted_distance(np.zeros(8), unit("ascent-descent"))
        assert a / b == pytest.approx(2.17 / 0.20)

    def test_pdist_matches_pairwise_in_condensed_order(self):
        rng = np.random.default_rng(0)
        coords = rng.random((4, 8))
        expected = [weighted_distance(coords[i], coords[j])
                    for i in range(4) for j in range(i + 1, 4)]
        got = weighted_pdist(coords)
        assert got.shape == (6,)
        assert got == pytest.approx(expected)

    def test_pdist_unnormalized(self):
        coords = np.stack([np.zeros(8), unit("order-chaos"), unit("order-chaos", 3)])
        assert weighted_pdist(coords, normalized=False) == pytest.approx([1.19, 3.57, 2.38])


# ── Benjamini-Hochberg ───────────────────────────────────────

class TestBenjaminiHochberg:
    PVALS = {"a": 0.01, "b": 0.04, "c": 0.03, "d": 0.5}

    def test_adjusted_values(self):
        # Sorted: .01 .03 .04 .5 ; raw p*n/rank: .04 .06 .0533 .5 ;
        # step-up minimum from the top: .04 .0533 .0533 .5
        r = StatisticalTests.benjamini_hochberg(self.PVALS)["bh_results"]
        assert r["a"]["adjusted_p"] == 0.04
        assert r["c"]["adjusted_p"] == pytest.approx(0.053333, abs=1e-6)
        assert r["b"]["adjusted_p"] == pytest.approx(0.053333, abs=1e-6)
        assert r["d"]["adjusted_p"] == 0.5
        assert [k for k, v in r.items() if v["significant_after_correction"]] == ["a"]

    def test_summary_and_bonferroni(self):
        out = StatisticalTests.benjamini_hochberg(self.PVALS)
        assert out["n_tests"] == 4
        assert out["n_significant_bh"] == 1
        bon = out["bonferroni_results"]
        assert bon["a"]["adjusted_p"] == 0.04
        assert bon["c"]["adjusted_p"] == 0.12
        assert bon["d"]["adjusted_p"] == 1.0  # capped
        assert out["n_significant_bonferroni"] == 1

    def test_alpha_is_used(self):
        out = StatisticalTests.benjamini_hochberg(self.PVALS, alpha=0.06)
        assert out["n_significant_bh"] == 3

    def test_original_p_kept(self):
        r = StatisticalTests.benjamini_hochberg(self.PVALS)["bh_results"]
        assert {k: v["original_p"] for k, v in r.items()} == self.PVALS


# ── Silhouette ───────────────────────────────────────────────

class TestSilhouette:
    def test_too_few_points(self):
        assert _silhouette_score(np.array([[0.0], [1.0]]), np.array([0, 1])) == 0.0

    def test_single_cluster(self):
        assert _silhouette_score(np.array([[0.0], [1.0], [2.0]]), np.array([0, 0, 0])) == 0.0

    def test_hand_worked_two_clusters(self):
        # 1-D points 0,1 | 10,11. For 0: a=1, b=10.5 ; for 1: a=1, b=9.5 ;
        # the other cluster mirrors this.
        coords = np.array([[0.0], [1.0], [10.0], [11.0]])
        labels = np.array([0, 0, 1, 1])
        expected = (9.5 / 10.5 + 8.5 / 9.5) / 2
        assert _silhouette_score(coords, labels) == pytest.approx(expected)

    def test_singleton_cluster_scores_one(self):
        # A singleton has a(i)=0, so s(i)=1 when b(i)>0.
        coords = np.array([[0.0], [1.0], [10.0]])
        labels = np.array([0, 0, 1])
        expected = ((10 - 1) / 10 + (9 - 1) / 9 + 1.0) / 3
        assert _silhouette_score(coords, labels) == pytest.approx(expected)


# ── fix_polar_coordinates helpers ────────────────────────────

class TestNormaliseAxis:
    @pytest.mark.parametrize("raw,expected", [
        ("axis:order-chaos", "order-chaos"),
        ("order-chaos", "order-chaos"),
        ("", ""),
        (None, None),
    ])
    def test_strips_prefix(self, raw, expected):
        assert fpc.normalise_axis(raw) == expected


class TestComputeAdjustment:
    def test_already_apart(self):
        assert fpc.compute_adjustment(0.1, 0.9, "order-chaos") == (0.0, 0.0, True)

    def test_even_split_achievable(self):
        # diff .3, needs .25 more: .125 each way.
        sa, sb, ok = fpc.compute_adjustment(0.35, 0.65, "order-chaos")
        assert (sa, sb) == pytest.approx((-0.125, 0.125))
        assert ok is True

    def test_order_of_arguments(self):
        sa, sb, ok = fpc.compute_adjustment(0.65, 0.35, "order-chaos")
        assert (sa, sb) == pytest.approx((0.125, -0.125))
        assert ok is True

    def test_capped_by_max_shift(self):
        # diff .2, needs .35: each side capped at .15, reaching only .5.
        sa, sb, ok = fpc.compute_adjustment(0.4, 0.6, "order-chaos")
        assert (sa, sb) == pytest.approx((-0.15, 0.15))
        assert ok is False

    def test_room_limited_side_hands_over_to_other(self):
        # Low side has .02 room; high side takes its .135 plus .015 extra
        # up to max_shift.
        sa, sb, ok = fpc.compute_adjustment(0.02, 0.3, "order-chaos")
        assert (sa, sb) == pytest.approx((-0.02, 0.15))
        assert ok is False

    def test_custom_threshold_and_cap(self):
        sa, sb, ok = fpc.compute_adjustment(0.4, 0.6, "order-chaos", threshold=0.6, max_shift=0.3)
        assert (sa, sb) == pytest.approx((-0.2, 0.2))
        assert ok is True


class TestApplyShift:
    def test_shift_and_round(self):
        entry = {"spectralCoordinates": {"order-chaos": 0.333}}
        assert fpc.apply_shift(entry, "order-chaos", 0.1) == (0.333, 0.43)
        assert entry["spectralCoordinates"]["order-chaos"] == 0.43

    @pytest.mark.parametrize("start,shift,end", [(0.05, -0.15, 0.0), (0.95, 0.15, 1.0)])
    def test_clamped(self, start, shift, end):
        entry = {"spectralCoordinates": {"light-shadow": start}}
        assert fpc.apply_shift(entry, "light-shadow", shift) == (start, end)


class TestFindPolarPairs:
    def index(self):
        def rec(rels):
            return {"entry": {"relationships": rels}}
        return {
            "arch:A": rec([
                {"type": "POLAR_OPPOSITE", "target": "arch:B", "axis": "axis:order-chaos"},
                {"type": "CULTURAL_ECHO", "target": "arch:C"},
                {"type": "POLAR_OPPOSITE", "target": "arch:C", "axis": "axis:not-an-axis"},
                {"type": "POLAR_OPPOSITE", "target": "arch:C"},
            ]),
            "arch:B": rec([
                {"type": "POLAR_OPPOSITE", "target": "arch:A", "axis": "order-chaos"},
                {"type": "POLAR_OPPOSITE", "target": "arch:A", "axis": "light-shadow"},
            ]),
        }

    def test_dedupes_and_filters(self, capsys):
        pairs = list(fpc.find_polar_pairs(self.index()))
        assert pairs == [
            ("arch:A", "arch:B", "order-chaos"),
            ("arch:B", "arch:A", "light-shadow"),
        ]
        assert "Unknown axis 'not-an-axis'" in capsys.readouterr().out


# ── human_audit.score_audit ──────────────────────────────────

class TestScoreAudit:
    def score(self, judgments):
        cases = [{"reviewer_judgment": j} for j in judgments]
        return HumanAuditTest(acp=None).score_audit({"cases": cases})

    def test_no_judgments(self):
        assert self.score([None, ""]) == {"error": "No judgments recorded"}

    def test_counts_and_concordance(self):
        r = self.score(["AGREE"] * 3 + ["DISAGREE", "UNSURE", None])
        assert (r["agree"], r["disagree"], r["unsure"], r["total_judged"]) == (3, 1, 1, 5)
        assert r["concordance"] == 0.6

    @pytest.mark.parametrize("agree,other,passed,partial", [
        (4, 1, True, False),    # 0.80: pass boundary
        (3, 1, False, True),    # 0.75
        (3, 2, False, True),    # 0.60: partial boundary
        (1, 1, False, False),   # 0.50
    ])
    def test_thresholds(self, agree, other, passed, partial):
        r = self.score(["AGREE"] * agree + ["DISAGREE"] * other)
        assert (r["pass"], r["partial"]) == (passed, partial)


# ── relationship_geometry._parse_axis_name ───────────────────

class TestParseAxisName:
    @pytest.mark.parametrize("ref,expected", [
        ("axis:order-chaos", 0),
        ("voluntary-fated", 7),
        (" axis:ascent-descent ", 5),
        ("axis:light", 2),           # partial match
        ("axis:not-an-axis", None),
    ])
    def test_parse(self, ref, expected):
        assert RelationshipGeometryTest(acp=None)._parse_axis_name(ref) == expected
