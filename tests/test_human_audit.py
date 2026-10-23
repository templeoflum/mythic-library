#!/usr/bin/env python3
"""Fixture tests for validation/v2_tests/human_audit.py (Test 6 case generation).

Hand-built archetypes, each group in its own region of the space (10 or
more apart on the first axis), so which archetypes count as nearest
neighbours, and which same-primordial pairs are farthest apart, can be
worked out by hand. Only the generated case set is checked here, never the
order of the cases. Nothing here reads the ACP data.
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integration.acp_loader import ACPLoader, AXES  # noqa: E402
from validation.v2_tests.human_audit import HumanAuditTest  # noqa: E402


def coords(x, y=0.0):
    out = {axis: 0.0 for axis in AXES}
    out[AXES[0]], out[AXES[1]] = float(x), float(y)
    return out


def fake_acp():
    a = {}
    region = iter(range(10, 10_000, 10))

    def pair(name, rel, gap=0.1):
        x = next(region)
        a[f"t:{name}-s"] = {"name": f"{name} s", "spectralCoordinates": coords(x),
                            "relationships": [dict(rel, target=f"t:{name}-t")]}
        a[f"t:{name}-t"] = {"name": f"{name} t", "spectralCoordinates": coords(x, gap), "relationships": []}

    # CULTURAL_ECHO: 5 high, 2 medium, 1 low fidelity, plus two that are left out
    for i, fid in enumerate([0.9, 0.95, 0.85, 0.99, 0.88]):
        pair(f"eh{i}", {"type": "CULTURAL_ECHO", "fidelity": fid})
    for i, fid in enumerate([0.5, 0.84]):
        pair(f"em{i}", {"type": "CULTURAL_ECHO", "fidelity": fid})
    pair("el0", {"type": "CULTURAL_ECHO", "fidelity": 0.2})
    pair("enofid", {"type": "CULTURAL_ECHO"})
    a["t:eh0-s"]["relationships"].append({"type": "CULTURAL_ECHO", "target": "t:nocoord", "fidelity": 0.9})
    a["t:nocoord"] = {"name": "No coordinates"}

    # POLAR_OPPOSITE: three pairs on order-chaos, two on light-shadow, one with no axis
    for i, axis in enumerate(["order-chaos"] * 3 + ["light-shadow"] * 2 + [None]):
        rel = {"type": "POLAR_OPPOSITE"}
        if axis:
            rel["axis"] = axis
        pair(f"po{i}", rel)

    # COMPLEMENT: six pairs, five are sampled
    for i in range(6):
        pair(f"co{i}", {"type": "COMPLEMENT", "dynamic": f"d{i}"})

    # Nearest neighbours: Zeus has four archetypes within 0.5 and one just outside.
    # Odin is alone, so contributes no case. Isis, Quetzalcoatl and Shiva are absent.
    a["t:zeus"] = {"name": "Zeus", "spectralCoordinates": coords(5000)}
    for i, d in enumerate([0.4, 0.1, 0.3, 0.2, 0.6]):
        a[f"t:zn{i}"] = {"name": f"zn{i}", "spectralCoordinates": coords(5000, d)}
    a["t:odin"] = {"name": "Odin", "spectralCoordinates": coords(6000)}

    # Same dominant primordial: six primordials, the members of P{k} are k apart.
    for k in range(1, 7):
        x = 7000 + 100 * k
        inst = [{"primordial": f"P{k}", "weight": 0.9}, {"primordial": "P-minor", "weight": 0.1}]
        a[f"t:m{k}a"] = {"name": f"m{k}a", "spectralCoordinates": coords(x), "instantiates": inst}
        a[f"t:m{k}b"] = {"name": f"m{k}b", "spectralCoordinates": coords(x, k), "instantiates": inst}
    # a lone member of its primordial gives no pair
    a["t:lone"] = {"name": "lone", "spectralCoordinates": coords(9000),
                   "instantiates": [{"primordial": "P-lone", "weight": 1.0}]}

    acp = ACPLoader.__new__(ACPLoader)  # skip loading files
    acp.archetypes = a
    acp._alias_index = {}
    acp._build_alias_index()
    return acp


@pytest.fixture(scope="module")
def result():
    return HumanAuditTest(fake_acp()).run()


def by_category(result, prefix):
    return [c for c in result["cases"] if c["category"].startswith(prefix)]


def pair_ids(cases):
    return {(c["source"]["id"], c["target"]["id"]) for c in cases}


def test_case_counts(result):
    assert result["n_cases"] == 24
    assert result["cases_by_category"] == {
        "CULTURAL_ECHO": 6, "POLAR_OPPOSITE": 5, "COMPLEMENT": 5,
        "NEAREST_NEIGHBOR": 3, "DISTANT_SAME_PRIMORDIAL": 5,
    }


def test_echoes_are_stratified_by_fidelity(result):
    cats = [c["category"] for c in by_category(result, "CULTURAL_ECHO")]
    assert cats.count("CULTURAL_ECHO (high fidelity)") == 3
    assert cats.count("CULTURAL_ECHO (medium fidelity)") == 2   # both, fewer than 4
    assert cats.count("CULTURAL_ECHO (low fidelity)") == 1
    for c in by_category(result, "CULTURAL_ECHO (high"):
        assert c["fidelity"] >= 0.85


def test_echoes_without_fidelity_or_coordinates_are_left_out(result):
    ids = pair_ids(by_category(result, "CULTURAL_ECHO"))
    assert ("t:enofid-s", "t:enofid-t") not in ids
    assert all(t != "t:nocoord" for _, t in ids)


def test_polar_pairs_span_every_declared_axis(result):
    polar = by_category(result, "POLAR_OPPOSITE")
    assert len(pair_ids(polar)) == 5          # no pair picked twice
    axes = {c["declared_axis"] for c in polar}
    assert {"order-chaos", "light-shadow", ""} <= axes


def test_complements_are_sampled(result):
    comp = by_category(result, "COMPLEMENT")
    assert len(pair_ids(comp)) == 5
    assert all(c["claim"].startswith("These archetypes complement each other: d") for c in comp)


def test_nearest_neighbours_are_the_three_closest_within_half(result):
    nn = by_category(result, "NEAREST_NEIGHBOR")
    assert pair_ids(nn) == {("t:zeus", "t:zn1"), ("t:zeus", "t:zn3"), ("t:zeus", "t:zn2")}
    assert sorted(c["distance_8d"] for c in nn) == [0.1, 0.2, 0.3]


def test_distant_same_primordial_takes_the_five_farthest(result):
    ds = by_category(result, "DISTANT_SAME_PRIMORDIAL")
    assert {c["primordial"] for c in ds} == {"P2", "P3", "P4", "P5", "P6"}
    for c in ds:
        k = int(c["primordial"][1:])
        assert c["distance_8d"] == float(k)
        assert {c["source"]["id"], c["target"]["id"]} == {f"t:m{k}a", f"t:m{k}b"}


def test_cases_start_unjudged(result):
    assert all(c["reviewer_judgment"] is None for c in result["cases"])
    assert result["verdicts"]["overall_pass"] is None
    assert result["verdicts"]["concordance"]["pass"] is None


def test_pair_entry_figures():
    audit = HumanAuditTest(fake_acp())
    e = audit._pair_entry("t:m3a", "t:m3b", category="X", claim="c", extra=1)
    assert e["distance_8d"] == 3.0
    assert e["per_axis_difference"][AXES[1]] == 3.0
    assert e["per_axis_difference"][AXES[0]] == 0.0
    assert e["source"]["primordials"][0] == {"primordial": "P3", "weight": 0.9}
    assert e["extra"] == 1


def test_pair_entry_without_coordinates():
    e = HumanAuditTest(fake_acp())._pair_entry("t:eh0-s", "t:nocoord", category="X", claim="c")
    assert e["distance_8d"] is None
    assert e["per_axis_difference"] == {}
    assert e["target"]["coordinates"] is None


def test_same_seed_same_case_set():
    one = HumanAuditTest(fake_acp()).run(seed=3)
    two = HumanAuditTest(fake_acp()).run(seed=3)
    assert pair_ids(one["cases"]) == pair_ids(two["cases"])


def test_save_audit_round_trips(result, tmp_path):
    path = HumanAuditTest(fake_acp()).save_audit(result, str(tmp_path / "audits"))
    assert Path(path) == tmp_path / "audits" / "human_audit_cases.json"
    assert json.loads(Path(path).read_text())["n_cases"] == 24
