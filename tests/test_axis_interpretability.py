#!/usr/bin/env python3
"""Fixture tests for validation/v2_tests/axis_interpretability.py (Test 5).

Five heroes and five deities, each mapped to its own archetype. Every axis
is 0.5 for everyone except individual-collective, where heroes sit low and
deities high, so exactly the individual-collective tests should pass.
Nothing here reads the ACP data or the database.
"""
import sys
import warnings
from pathlib import Path
from types import SimpleNamespace

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integration.acp_loader import ACPLoader, AXES  # noqa: E402
from validation.v2_tests import axis_interpretability as ai  # noqa: E402

HERO_IC = [0.10, 0.15, 0.20, 0.25, 0.30]
DEITY_IC = [0.70, 0.75, 0.80, 0.85, 0.90]


def entities():
    out = [("hero", i, v) for i, v in enumerate(HERO_IC)] + [("deity", i, v) for i, v in enumerate(DEITY_IC)]
    return [SimpleNamespace(canonical_name=f"{t}{i}", entity_type=t, ic=v) for t, i, v in out]


def fake_acp(spread=("individual-collective",)):
    archetypes = {}
    for e in entities():
        c = {axis: 0.5 for axis in AXES}
        for axis in spread:
            # heroes low / deities high on individual-collective; the other way
            # round elsewhere, which is the direction the hero-deity tests expect
            c[axis] = e.ic if axis == "individual-collective" else round(1 - e.ic, 2)
        archetypes[f"arch:T-{e.canonical_name}"] = {"name": e.canonical_name, "spectralCoordinates": c}
    acp = ACPLoader.__new__(ACPLoader)  # skip loading files
    acp.archetypes = archetypes
    return acp


class FakeLibrary:
    def __init__(self, motifs=None):
        self.motifs = motifs or {}

    def get_all_entities(self):
        return entities() + [SimpleNamespace(canonical_name="Unmapped", entity_type="hero", ic=None)]

    def get_all_motif_codes(self):
        return sorted(self.motifs)

    def get_motif_entities(self, code):
        return self.motifs.get(code, [])


class FakeMapper:
    def __init__(self):
        self.mappings = [SimpleNamespace(library_entity=e.canonical_name,
                                         acp_archetype_id=f"arch:T-{e.canonical_name}") for e in entities()]

    def get_mapping(self, name):
        return next((m for m in self.mappings if m.library_entity == name), None)


def run(library=None, spread=("individual-collective",)):
    test = ai.AxisInterpretabilityTest(fake_acp(spread), library or FakeLibrary(), FakeMapper())
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)  # t-tests on constant axes
        return test.run()


@pytest.fixture(scope="module")
def result():
    return run()


def passed(rows):
    return [(r.get("type_a", r.get("entity_type")), r["axis"]) for r in rows if r["pass"]]


def test_global_means(result):
    gm = result["global_means"]
    assert gm["individual-collective"] == round((sum(HERO_IC) + sum(DEITY_IC)) / 10, 4)
    assert gm["order-chaos"] == 0.5


def test_contrastive_tests(result):
    ct = result["contrastive_tests"]
    assert (ct["n_mappings"], ct["n_tested"], ct["n_passed"]) == (8, 8, 1)
    assert passed(ct["results"]) == [("hero", "individual-collective")]
    row = next(r for r in ct["results"] if r["axis"] == "individual-collective")
    assert (row["n_a"], row["n_b"]) == (5, 5)    # the unmapped hero is left out
    assert row["mean_a"] == 0.2 and row["mean_b"] == 0.8


def test_entity_type_tests(result):
    et = result["entity_type_tests"]
    assert (et["n_tested"], et["n_passed"]) == (6, 2)
    assert passed(et["results"]) == [("hero", "individual-collective"), ("deity", "individual-collective")]


def test_motif_tests_skip_without_data(result):
    mt = result["motif_tests"]
    assert (mt["n_tested"], mt["n_passed"]) == (0, 0)


def test_scores_and_verdicts(result):
    # primary = (1 contrastive + 2 entity-type) of (8 + 6)
    assert (result["n_passed"], result["n_mappings_tested"]) == (3, 14)
    assert result["interpretability_score"] == round(3 / 14, 4)
    assert result["axes_with_alignments"] == {
        "individual-collective": ["contrast:herovsdeity", "type:hero", "type:deity"]}
    assert result["top_3_axes_aligned"] == 1
    assert result["verdicts"]["interpretability_score"]["pass"] is True   # 21% >= 20%
    assert result["verdicts"]["top_3_alignment"]["pass"] is False         # 1 of the top 3
    assert result["verdicts"]["overall_pass"] is False


@pytest.mark.parametrize("spread, aligned, passes", [
    (("individual-collective", "order-chaos", "creation-destruction"), 3, True),
    (("individual-collective", "order-chaos"), 2, False),
])
def test_top_3_alignment_needs_each_of_the_top_3(spread, aligned, passes):
    # criterion: "Top 3 axes each have >=1 interpretable alignment"
    out = run(spread=spread)
    assert out["top_3_axes_aligned"] == aligned
    assert bool(out["verdicts"]["top_3_alignment"]["pass"]) is passes
    assert out["verdicts"]["top_3_alignment"]["result"] == f"{aligned}/3 top axes aligned"


def test_exact_code_lookup_does_not_take_sub_codes():
    lib = FakeLibrary({"A1": ["hero0"], "A10": ["hero1"], "A100": ["hero2"]})
    test = ai.AxisInterpretabilityTest(fake_acp(), lib, FakeMapper())
    assert test._get_entities_for_exact_code("a1") == ["hero0"]
    assert sorted(test._get_entities_for_motif_prefix("A1")) == ["hero0", "hero1", "hero2"]


def test_motif_mapping_with_data():
    # deities tagged A1 sit high on individual-collective; A1 is mapped to creation-destruction "low"
    lib = FakeLibrary({"A1": [f"deity{i}" for i in range(5)]})
    out = run(lib)
    row_codes = out["motif_tests"]
    assert row_codes["n_tested"] == 1   # only A1 has entities
    assert row_codes["n_passed"] == 0   # creation-destruction is flat at 0.5


def test_too_few_mapped_archetypes():
    mapper = FakeMapper()
    mapper.mappings = mapper.mappings[:9]
    out = ai.AxisInterpretabilityTest(fake_acp(), FakeLibrary(), mapper).run()
    assert out == {"error": "Insufficient mapped archetypes"}
