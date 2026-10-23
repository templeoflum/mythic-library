#!/usr/bin/env python3
"""Tests for scripts/conduct_audit.py.

CASES_PATH and RESULTS_PATH are pointed at tmp_path, and the cases file is a
synthetic 40-case fixture, so the repo's outputs/ is never read or written.
"""
import copy
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
SCRIPT = ROOT / "scripts" / "conduct_audit.py"

from validation.v2_tests.human_audit import HumanAuditTest  # noqa: E402

# The order the case generator writes categories in.
CATEGORIES = (
    ["CULTURAL_ECHO (high fidelity)"] * 4
    + ["CULTURAL_ECHO (medium fidelity)"] * 3
    + ["CULTURAL_ECHO (low fidelity)"] * 3
    + ["POLAR_OPPOSITE"] * 5
    + ["COMPLEMENT"] * 5
    + ["NEAREST_NEIGHBOR"] * 15
    + ["DISTANT_SAME_PRIMORDIAL"] * 5
)


@pytest.fixture(scope="module")
def ca():
    spec = importlib.util.spec_from_file_location("conduct_audit_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_cases_doc(n=40):
    cases = []
    for i in range(n):
        cat = CATEGORIES[i % len(CATEGORIES)]
        cases.append({
            "category": cat,
            "claim": f"claim {i}",
            "source": {"id": f"test:src-{i}", "name": f"Source {i}", "system": "test"},
            "target": {"id": f"test:tgt-{i}", "name": f"Target {i}", "system": "test"},
            "distance_8d": round(0.01 * i, 4),
            "per_axis_difference": {},
            "reviewer_judgment": None,
            "reviewer_notes": "",
        })
    return {
        "n_cases": n,
        "cases_by_category": {
            "CULTURAL_ECHO": 10, "POLAR_OPPOSITE": 5, "COMPLEMENT": 5,
            "NEAREST_NEIGHBOR": 15, "DISTANT_SAME_PRIMORDIAL": 5,
        },
        "cases": cases,
        "scoring_instructions": "fixture",
        "verdicts": {
            "concordance": {"pass": None, "criterion": ">=80% concordance", "result": "Awaiting human review"},
            "overall_pass": None,
        },
    }


@pytest.fixture
def paths(ca, tmp_path, monkeypatch):
    cases_path = tmp_path / "audits" / "human_audit_cases.json"
    results_path = tmp_path / "audits" / "human_audit_results.json"
    monkeypatch.setattr(ca, "CASES_PATH", cases_path)
    monkeypatch.setattr(ca, "RESULTS_PATH", results_path)
    monkeypatch.setattr(ca, "ROOT", tmp_path)  # the usage message prints CASES_PATH relative to ROOT
    return cases_path, results_path


def write_cases(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc), encoding="utf-8")


@pytest.fixture
def ran(ca, paths):
    cases_path, results_path = paths
    write_cases(cases_path, make_cases_doc())
    ca.main()
    return (json.loads(cases_path.read_text(encoding="utf-8")),
            json.loads(results_path.read_text(encoding="utf-8")))


def test_judgments_are_well_formed(ca):
    assert len(ca.JUDGMENTS) == 40
    for judgment, notes in ca.JUDGMENTS:
        assert judgment in {"AGREE", "DISAGREE", "UNSURE"}
        assert notes.strip()


def test_scoring_matches_the_judgment_tally(ca, ran):
    _, results = ran
    tally = Counter(j for j, _ in ca.JUDGMENTS)
    s = results["scoring"]
    assert (s["agree"], s["disagree"], s["unsure"]) == (tally["AGREE"], tally["DISAGREE"], tally["UNSURE"])
    assert s["total_judged"] == 40
    assert s["concordance"] == round(tally["AGREE"] / 40, 4)
    assert s["pass"] == (tally["AGREE"] / 40 >= 0.80)


def test_scoring_agrees_with_the_v2_scorer(ran):
    cases_doc, results = ran
    scored = HumanAuditTest.__new__(HumanAuditTest).score_audit(cases_doc)
    assert scored == results["scoring"]


def test_cases_file_is_updated_in_place(ca, ran):
    cases_doc, results = ran
    for case, (judgment, notes) in zip(cases_doc["cases"], ca.JUDGMENTS):
        assert (case["reviewer_judgment"], case["reviewer_notes"]) == (judgment, notes)
    s = results["scoring"]
    assert cases_doc["verdicts"]["overall_pass"] == s["pass"]
    assert cases_doc["verdicts"]["concordance"]["pass"] == s["pass"]
    assert cases_doc["verdicts"]["concordance"]["result"].startswith(f"{s['agree']}/40 AGREE")


def test_by_category_breakdown(ca, ran):
    _, results = ran
    by_cat = results["by_category"]
    assert set(by_cat) == {"CULTURAL_ECHO", "POLAR_OPPOSITE", "COMPLEMENT",
                           "NEAREST_NEIGHBOR", "DISTANT_SAME_PRIMORDIAL"}  # fidelity suffix dropped
    assert sum(c["total"] for c in by_cat.values()) == 40
    expected = {}
    for cat, (judgment, _) in zip(CATEGORIES, ca.JUDGMENTS):
        row = expected.setdefault(cat.split(" (")[0], {"agree": 0, "disagree": 0, "unsure": 0, "total": 0})
        row[judgment.lower()] += 1
        row["total"] += 1
    assert by_cat == expected


def test_reviews_carry_each_case(ca, ran):
    _, results = ran
    reviews = results["reviews"]
    assert [r["case_index"] for r in reviews] == list(range(40))
    r = reviews[7]
    assert (r["source_id"], r["target_name"], r["distance_8d"]) == ("test:src-7", "Target 7", 0.07)
    assert r["judgment"] == ca.JUDGMENTS[7][0].lower()


def test_missing_cases_file_exits_with_usage(ca, paths):
    with pytest.raises(SystemExit) as exc:
        ca.main()
    assert "usage:" in str(exc.value)
    assert not paths[1].exists()


def test_wrong_case_count_is_refused(ca, paths):
    write_cases(paths[0], make_cases_doc(39))
    with pytest.raises(AssertionError, match="Expected 40 cases"):
        ca.main()
    assert not paths[1].exists()


@pytest.mark.xfail(strict=True, reason=(
    "judgments are applied by list position only, so a regenerated or reordered "
    "case list silently gets each judgment on a different pair instead of being refused"))
def test_reordered_cases_keep_their_judgments(ca, paths):
    cases_path, _ = paths
    doc = make_cases_doc()
    write_cases(cases_path, doc)
    ca.main()
    first = {c["source"]["id"]: c["reviewer_judgment"]
             for c in json.loads(cases_path.read_text(encoding="utf-8"))["cases"]}

    reordered = copy.deepcopy(doc)
    reordered["cases"].reverse()
    write_cases(cases_path, reordered)
    try:
        ca.main()
    except (SystemExit, AssertionError, ValueError):
        return  # refusing a list it wasn't written for is also correct
    second = {c["source"]["id"]: c["reviewer_judgment"]
              for c in json.loads(cases_path.read_text(encoding="utf-8"))["cases"]}
    assert second == first
