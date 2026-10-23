#!/usr/bin/env python3
"""Fixture tests for validation/v2_tests/echo_coherence.py (Test 1).

Two hand-built traditions, AA and BB. Each echo pair sits a known, small
distance apart, and every non-echo cross-tradition pair is at least 1.0
apart, so the echo distances and the verdicts can be worked out by hand.
Nothing here reads the ACP data.
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integration.acp_loader import ACPLoader, AXES  # noqa: E402
from validation.saved_json import json_default  # noqa: E402
from validation.v2_tests.echo_coherence import EchoCoherenceTest  # noqa: E402

N = 6
GAPS = [0.05 * (i + 1) for i in range(N)]            # echo distance of pair i
FIDELITY = [round(0.95 - 0.1 * i, 2) for i in range(N)]  # falls as the gap grows


def coords(a0=0.0, a1=0.0):
    out = {axis: 0.0 for axis in AXES}
    out[AXES[0]], out[AXES[1]] = a0, a1
    return out


def fake_acp(n_pairs=N):
    archetypes = {}
    for i in range(N):
        archetypes[f"arch:AA-{i}"] = {"name": f"A{i}", "systemCode": "AA",
                                      "spectralCoordinates": coords(0.0, float(i)), "relationships": []}
        archetypes[f"arch:BB-{i}"] = {"name": f"B{i}", "belongsToSystem": "BB",
                                      "spectralCoordinates": coords(GAPS[i], float(i)), "relationships": []}
    for i in range(n_pairs):
        archetypes[f"arch:AA-{i}"]["relationships"].append(
            {"type": "CULTURAL_ECHO", "target": f"arch:BB-{i}", "fidelity": FIDELITY[i]})
    # left out: an echo to an archetype with no coordinates, and a different type
    archetypes["arch:AA-0"]["relationships"] += [
        {"type": "CULTURAL_ECHO", "target": "arch:CC-NOCOORD", "fidelity": 0.9},
        {"type": "POLAR_OPPOSITE", "target": "arch:BB-5", "axis": AXES[0]},
    ]
    archetypes["arch:CC-NOCOORD"] = {"name": "No coordinates", "systemCode": "CC"}

    acp = ACPLoader.__new__(ACPLoader)  # skip loading files
    acp.archetypes = archetypes
    return acp


@pytest.fixture(scope="module")
def result():
    return EchoCoherenceTest(fake_acp()).run()


def test_echo_pairs_and_distances(result):
    assert result["n_echo_pairs"] == N
    assert result["echo_distance"]["mean"] == round(sum(GAPS) / N, 4)
    assert result["echo_distance"]["median"] == round((GAPS[2] + GAPS[3]) / 2, 4)


def test_control_pairs_are_cross_tradition_non_echo(result):
    assert result["n_control_pairs"] == 3 * N
    # every non-echo AA-BB pair differs by at least 1.0 on axis 1
    assert result["control_distance"]["mean"] >= 1.0


def test_verdicts(result):
    assert result["mann_whitney"]["p_value"] < 0.05
    assert result["mann_whitney"]["cohens_d"] > 0.3
    assert bool(result["verdicts"]["distance_test"]["pass"]) is True
    # fidelity falls exactly as distance rises
    assert result["fidelity_correlation"]["n_pairs_with_fidelity"] == N
    assert result["fidelity_correlation"]["spearman_r"] == -1.0
    assert bool(result["verdicts"]["fidelity_test"]["pass"]) is True
    assert bool(result["verdicts"]["overall_pass"]) is True


def test_verdicts_save_as_plain_bools(result):
    # Verdicts are numpy bools in memory; validation/v2_run.py saves them
    # through json_default so the file holds real booleans, not "True"/"False".
    saved = json.loads(json.dumps(result, default=json_default))
    for verdict in ("distance_test", "fidelity_test"):
        assert type(saved["verdicts"][verdict]["pass"]) is bool
    assert type(saved["verdicts"]["overall_pass"]) is bool


def test_review_tables(result):
    review = result["human_review"]
    assert [e["source"] for e in review["closest_echoes"]] == [f"arch:AA-{i}" for i in range(N)]
    assert review["highest_fidelity"][0]["fidelity"] == FIDELITY[0]
    # fidelity >= 0.7, farthest first
    assert [e["target"] for e in review["worst_violators"]] == ["arch:BB-2", "arch:BB-1", "arch:BB-0"]


def test_same_seed_same_result(result):
    assert EchoCoherenceTest(fake_acp()).run() == result


def test_too_few_echo_pairs():
    out = EchoCoherenceTest(fake_acp(n_pairs=4)).run()
    assert out == {"error": "Only 4 valid echo pairs found", "pass": False}
