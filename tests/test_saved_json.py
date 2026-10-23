#!/usr/bin/env python3
"""Tests for validation/saved_json.py and the readers of saved v2 results.

Results files written before json_default existed hold verdicts as the
strings "True"/"False"; the readers must treat "False" as a failure.
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from validation.saved_json import is_pass, json_default  # noqa: E402
from validation.unified_report import generate_unified_report  # noqa: E402


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


export = _load("export_explorer_saved_json_under_test", "scripts/export_explorer_data.py")


def test_numpy_bools_save_as_json_booleans():
    doc = {"a": np.True_, "b": np.False_, "c": True, "nested": [{"pass": np.bool_(False)}]}
    loaded = json.loads(json.dumps(doc, default=json_default))
    assert loaded == {"a": True, "b": False, "c": True, "nested": [{"pass": False}]}
    assert all(type(v) is bool for v in (loaded["a"], loaded["b"], loaded["nested"][0]["pass"]))


def test_other_unserialisable_values_still_become_strings():
    assert json.loads(json.dumps({"p": Path("x/y")}, default=json_default)) == {"p": "x/y"}


@pytest.mark.parametrize("value, expected", [
    (True, True), (False, False), (np.True_, True), (np.False_, False),
    ("True", True), ("False", False), ("true", True), ("false", False),
    (None, False), (1, True), (0, False),
])
def test_is_pass(value, expected):
    assert is_pass(value) is expected


def results_with(t1_pass, t7_pass):
    return {
        "verdict": {
            "tier_a": {"tests": [{"name": "Test 1: Echo Coherence", "pass": t1_pass}]},
            "tier_b": {"tests": [{"name": "Test 4: Motif Bridging", "pass": "True"}]},
        },
        "miroglyph_structure": {"verdicts": {
            "test7_arc_separation": {"pass": t7_pass, "criterion": "c", "detail": "d"},
            "test8_condition_progression": {"pass": True},
            "test9_polarity_pairs": {"pass": False},
        }},
    }


@pytest.mark.parametrize("t1, t7", [("False", "False"), (False, False)])
def test_unified_report_shows_a_saved_false_as_fail(t1, t7):
    report = generate_unified_report(results_with(t1, t7))
    assert "- Test 1: Echo Coherence: **FAIL**" in report
    assert "### Test 7: Arc Separation: **FAIL**" in report
    assert "- Test 4: Motif Bridging: **PASS**" in report
    assert "### Test 8: Condition Progression: **PASS**" in report
    assert "### Test 9: Polarity Pairs: **FAIL**" in report


def test_explorer_summary_reads_string_verdicts(tmp_path, monkeypatch):
    outputs, out_dir = tmp_path / "outputs", tmp_path / "data"
    (outputs / "metrics").mkdir(parents=True)
    out_dir.mkdir()
    raw = {
        "verdict": {},
        "test1_echo_coherence": {"verdicts": {"overall_pass": "False"}},
        "test2_primordial_clustering": {"verdicts": {"overall_pass": "True"}},
        "miroglyph_structure": {"verdicts": {
            "test8_condition_progression": {"pass": "False"},
            "test9_polarity_pairs": {"pass": "True"},
        }},
    }
    (outputs / "metrics" / "v2_validation_results.json").write_text(json.dumps(raw), encoding="utf-8")
    monkeypatch.setattr(export, "OUTPUTS", outputs)
    monkeypatch.setattr(export, "OUTPUT_DIR", out_dir)
    export.export_validation_summary()
    summary = json.loads((out_dir / "validation_summary.json").read_text(encoding="utf-8"))
    tiers = {t["id"]: t for t in summary["tiers"]}
    a = {t["name"]: t["pass"] for t in tiers["A"]["tests"]}
    assert a["Echo Coherence"] is False and a["Primordial Clustering"] is True
    c = {t["name"]: t["pass"] for t in tiers["C"]["tests"]}
    assert c["Condition Progression"] is False and c["Polarity Pairs"] is True
    assert (tiers["C"]["passed"], tiers["C"]["total"], tiers["C"]["verdict"]) == (1, 2, "PARTIAL")
