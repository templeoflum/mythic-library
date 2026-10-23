#!/usr/bin/env python3
"""Tests for validation/v2_run.compute_verdict, the tiered verdict over Tests 1-6.

Synthetic result dicts only; nothing here runs a test or reads repo data.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validation.v2_run import compute_verdict  # noqa: E402

TIER_A = ["test1_echo_coherence", "test2_primordial_clustering", "test3_relationship_geometry"]
TIER_B = ["test4_motif_bridging", "test5_axis_interpretability"]


def results(a=(True, True, True), b=(True, True), audit=None):
    r = {}
    for key, ok in zip(TIER_A + TIER_B, list(a) + list(b)):
        r[key] = {"verdicts": {"overall_pass": ok}}
    if audit is not None:
        r["test6_human_audit"] = {"scoring": audit}
    return r


AUDIT_PASS = {"pass": True, "concordance": 0.875, "agree": 35, "total_judged": 40}


@pytest.mark.parametrize("a, expected", [
    ((True, True, True), "PASS"),
    ((True, True, False), "PARTIAL"),
    ((False, True, False), "FAIL"),
    ((False, False, False), "FAIL"),
])
def test_tier_a_counts_passes(a, expected):
    v = compute_verdict(results(a=a))["tier_a"]
    assert v["verdict"] == expected
    assert v["passed"] == sum(a)
    assert v["total"] == 3


@pytest.mark.parametrize("b, expected", [
    ((True, True), "PASS"),
    ((True, False), "PARTIAL"),
    ((False, False), "FAIL"),
])
def test_tier_b_counts_passes(b, expected):
    v = compute_verdict(results(b=b))["tier_b"]
    assert v["verdict"] == expected
    assert v["passed"] == sum(b)


@pytest.mark.parametrize("a, b, expected", [
    ((True, True, True), (True, True), "STRONG"),
    ((True, True, True), (True, False), "PROMISING"),
    ((True, True, True), (False, False), "SELF-CONSISTENT BUT UNGROUNDED"),
    ((True, True, False), (True, True), "MIXED"),
    ((True, True, False), (False, False), "MIXED"),
    ((True, False, False), (True, True), "REVISE"),
])
def test_overall_follows_tiers_a_and_b(a, b, expected):
    assert compute_verdict(results(a=a, b=b))["overall"]["verdict"] == expected


def test_missing_test_counts_as_not_passed():
    r = results()
    del r["test3_relationship_geometry"]
    v = compute_verdict(r)
    assert v["tier_a"]["verdict"] == "PARTIAL"
    assert v["overall"]["verdict"] == "MIXED"


def test_audit_pending_without_scoring():
    v = compute_verdict(results())
    assert v["tier_e"]["verdict"] == "PENDING"
    assert v["tier_e"]["tests"][0]["pass"] is None
    assert v["overall"]["label"].endswith("(pending expert review)")


def test_audit_scoring_error_is_pending():
    v = compute_verdict(results(audit={"error": "no judgments"}))
    assert v["tier_e"]["verdict"] == "PENDING"


def test_audit_pass_label_and_suffix():
    v = compute_verdict(results(audit=AUDIT_PASS))
    assert v["tier_e"]["verdict"] == "PASS"
    assert v["tier_e"]["label"] == "Expert concordance 87.5% (35/40 AGREE)"
    assert v["tier_e"]["passed"] == 1
    assert v["overall"]["verdict"] == "STRONG"
    assert v["overall"]["label"].endswith("+ expert concordance confirmed")


@pytest.mark.parametrize("scoring, tier_e, suffix", [
    ({"pass": False, "partial": True, "concordance": 0.6}, "PARTIAL", "(expert concordance partial)"),
    ({"pass": False, "concordance": 0.3}, "FAIL", "(expert concordance failed)"),
])
def test_audit_does_not_change_the_overall_verdict(scoring, tier_e, suffix):
    v = compute_verdict(results(audit=scoring))
    assert v["tier_e"]["verdict"] == tier_e
    assert v["tier_e"]["passed"] == 0
    # Tier E only adds a suffix to the label; the overall verdict comes from tiers A and B.
    assert v["overall"]["verdict"] == "STRONG"
    assert v["overall"]["label"].endswith(suffix)


def test_empty_results():
    v = compute_verdict({})
    assert v["tier_a"]["verdict"] == "FAIL"
    assert v["tier_b"]["verdict"] == "FAIL"
    assert v["tier_e"]["verdict"] == "PENDING"
    assert v["overall"]["verdict"] == "REVISE"
