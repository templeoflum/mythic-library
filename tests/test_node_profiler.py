"""Fixture tests for integration/node_profiler.py.

NodeProfiler turns the library into the condition, arc and node centroids
that Miroglyph Tests 7-10 in validation/v2_run.py read. These tests check
the profiler only, never the verdicts. The library, mapper and ACP are
small stubs. The node grid comes from the tracked Miroglyph spec. Every
expected value is worked out by hand from the stubs below.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from integration.miroglyph_loader import MiroGlyphLoader  # noqa: E402
from integration.node_profiler import (  # noqa: E402
    AXES, MIN_SEGMENTS_PER_TEXT, NodeProfiler, round_half_up)

SPEC = ROOT / "miroglyph" / "miroglyph_v4_technical_spec.json"


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------
#
# Three texts. "six" has 6 segments; segment o mentions S<o>.
# "twelve" has 12 segments; segment o mentions T<o>. "five" has 5 segments
# and is below MIN_SEGMENTS_PER_TEXT, so it is ignored.
#
# Position bins (6 bins): "six" puts ordinal o in bin o. "twelve" puts
# ordinals 2k-1 and 2k in bin k. So bin k holds S<k>, T<2k-1> and T<2k>.

SEGMENTS = {
    "six": [[f"S{o}"] for o in range(1, 7)],
    "twelve": [[f"T{o}"] for o in range(1, 13)],
    "five": [[f"F{o}"] for o in range(1, 6)],
}


def _coord(value):
    return np.full(len(AXES), value)


# Every S<k> sits at 0.1, odd T at 0.2, even T at 0.6. T12 and X have no
# mapping, and neither do the F entities.
COORDS = {f"S{k}": _coord(0.1) for k in range(1, 7)}
COORDS.update({f"T{o}": _coord(0.2 if o % 2 else 0.6) for o in range(1, 12)})

PATTERN_CODES = {
    "descent_to_underworld": ["F81"],      # arc D
    "trickster": ["K0"],                   # arc R
    "cosmogony_creation": ["A1"],          # arc E (tags nothing)
}
MOTIF_ENTITIES = {
    "F81": ["S1", "T1", "T2", "S4"],
    "K0": ["S1", "X"],
    "A1": [],
}

INSTANTIATIONS = {
    "arc:S1": [{"primordial": "p:a", "weight": 0.9}],
    "arc:T1": [{"primordial": "p:a", "weight": 0.7},
               {"primordial": "p:b", "weight": 0.8}],
    "arc:T2": [{"primordial": "p:b"}],                 # weight defaults to 0.5
}


class StubLibrary:
    def get_segments_per_text(self):
        return {tid: len(segs) for tid, segs in SEGMENTS.items()}

    def get_text_segments_ordered(self, text_id):
        return [{"segment_id": f"{text_id}:{i}", "ordinal": i,
                 "entity_names": list(names)}
                for i, names in enumerate(SEGMENTS[text_id], start=1)]

    def get_pattern_motif_codes(self, name):
        return list(PATTERN_CODES.get(name, []))

    def get_entities_for_motif_codes(self, codes):
        out = []
        for c in codes:
            out.extend(MOTIF_ENTITIES.get(c, []))
        return out


class StubMapper:
    def get_mapping(self, name):
        if name in COORDS:
            return SimpleNamespace(acp_archetype_id=f"arc:{name}")
        return None


class StubACP:
    def get_instantiations(self, archetype_id):
        return INSTANTIATIONS.get(archetype_id, [])


class StubUnified:
    def __init__(self):
        self.library = StubLibrary()
        self.mapper = StubMapper()
        self.acp = StubACP()
        self.miroglyph = MiroGlyphLoader(str(SPEC))
        self.coordinate_lookups = 0

    def get_entity_coordinates(self, name):
        self.coordinate_lookups += 1
        return COORDS.get(name)


@pytest.fixture
def profiler():
    return NodeProfiler(StubUnified())


def _mean(profile):
    return np.array(profile["mean_coordinates"])


# ---------------------------------------------------------------------------
# Condition profiles
# ---------------------------------------------------------------------------

def test_min_segments_threshold():
    assert MIN_SEGMENTS_PER_TEXT == 6


def test_condition_bins_by_narrative_position(profiler):
    cond = profiler.compute_condition_profiles()
    assert sorted(cond) == [1, 2, 3, 4, 5, 6]
    for k in range(1, 7):
        p = cond[k]
        assert p["n_texts"] == 2                    # "five" is too short
        assert p["total_entity_mentions"] == 3      # S<k>, T<2k-1>, T<2k>
        assert sorted(p["sample_entities"]) == sorted(
            n for n in (f"S{k}", f"T{2*k-1}", f"T{2*k}") if n in COORDS)
    assert cond[1]["label"] == "Dawn/Initiation"
    assert cond[6]["label"] == "Return/Integration"


def test_condition_profile_statistics(profiler):
    cond = profiler.compute_condition_profiles()
    # Bin 1: 0.1, 0.2, 0.6.
    assert cond[1]["n_entities"] == 3
    assert np.allclose(_mean(cond[1]), 0.3)
    assert np.allclose(cond[1]["std_coordinates"], np.sqrt(0.14 / 3))
    assert cond[1]["confidence"] == pytest.approx(0.3)
    # Bin 6: T12 has no mapping, so only S6 (0.1) and T11 (0.2) count.
    assert cond[6]["n_entities"] == 2
    assert cond[6]["total_entity_mentions"] == 3
    assert np.allclose(_mean(cond[6]), 0.15)
    assert cond[6]["confidence"] == pytest.approx(0.2)


def test_profile_of_nothing_is_neutral(profiler):
    p = profiler._compute_profile(np.empty((0, len(AXES))), [])
    assert p == {"mean_coordinates": [0.5] * 8, "std_coordinates": [0.0] * 8,
                 "n_entities": 0, "sample_entities": [], "confidence": 0.0}


def test_single_entity_has_zero_std_and_confidence_saturates(profiler):
    one = profiler._compute_profile(np.array([_coord(0.4)]), ["S1"])
    assert one["std_coordinates"] == [0.0] * 8
    assert one["confidence"] == pytest.approx(0.1)
    names = [f"T{o}" for o in range(1, 12)]
    many = profiler._compute_profile(profiler._entities_to_coords(names), names)
    assert many["n_entities"] == 11
    assert many["confidence"] == 1.0                 # capped at 10 entities
    assert many["sample_entities"] == names[:10]


def test_coordinates_are_looked_up_once_per_entity():
    unified = StubUnified()
    prof = NodeProfiler(unified)
    prof._entities_to_coords(["S1", "S1", "X", "X"])
    prof._entities_to_coords(["S1", "X"])
    assert unified.coordinate_lookups == 2           # cached, including misses


# ---------------------------------------------------------------------------
# Arc profiles
# ---------------------------------------------------------------------------

def test_arc_profiles_from_pattern_motifs(profiler):
    arcs = profiler.compute_arc_profiles()
    assert sorted(arcs) == ["D", "E", "R"]

    d = arcs["D"]
    assert d["label"] == "Descent/Shadow"
    assert d["patterns_used"] == ["descent_to_underworld"]
    assert d["motif_codes"] == ["F81"]
    assert d["n_entities"] == 4                      # S1, T1, T2, S4
    assert np.allclose(_mean(d), (0.1 + 0.2 + 0.6 + 0.1) / 4)

    r = arcs["R"]
    assert r["patterns_used"] == ["trickster"]
    assert r["n_entities"] == 1                      # X has no mapping
    assert np.allclose(_mean(r), 0.1)

    e = arcs["E"]
    assert e["patterns_used"] == ["cosmogony_creation"]
    assert e["n_entities"] == 0 and e["confidence"] == 0.0
    assert e["mean_coordinates"] == [0.5] * 8


# ---------------------------------------------------------------------------
# Node profiles
# ---------------------------------------------------------------------------

def test_node_profiles_cover_the_grid(profiler):
    nodes = profiler.compute_node_profiles()
    assert sorted(nodes) == sorted(profiler.unified.miroglyph.get_all_node_ids())
    assert len(nodes) == 18
    d1 = nodes["D1"]
    assert (d1["node_id"], d1["arc"], d1["condition"]) == ("D1", "Descent", "Dawn")
    assert d1["title"] == profiler.unified.miroglyph.get_node("D1").title


def test_direct_profile_when_three_mapped_entities_overlap(profiler):
    # Arc D {S1, T1, T2, S4} meets bin 1 {S1, T1, T2}: three mapped entities.
    d1 = profiler.compute_node_profiles()["D1"]
    assert d1["method"] == "direct"
    assert d1["n_entities"] == 3
    assert np.allclose(_mean(d1), 0.3)
    assert "blend_weights" not in d1


def test_interpolated_profile_blends_by_confidence(profiler):
    nodes = profiler.compute_node_profiles()
    # Arc R {S1, X} meets bin 1 in S1 only. Arc confidence 0.1 (mean 0.1),
    # bin confidence 0.3 (mean 0.3): weights 0.25 / 0.75.
    r1 = nodes["R1"]
    assert r1["method"] == "interpolated"
    assert r1["n_entities"] == 1
    assert r1["sample_entities"] == ["S1"]
    assert r1["blend_weights"] == {"arc": 0.25, "condition": 0.75}
    assert np.allclose(_mean(r1), 0.25 * 0.1 + 0.75 * 0.3)
    assert r1["std_coordinates"] == [0.0] * 8
    assert r1["confidence"] == pytest.approx(min(0.1, 0.3) * 0.5)
    # Arc E is empty (confidence 0): the bin centroid is used as is.
    e1 = nodes["E1"]
    assert e1["blend_weights"] == {"arc": 0.0, "condition": 1.0}
    assert np.allclose(_mean(e1), 0.3)
    assert e1["confidence"] == 0.0


def test_blend_falls_back_to_even_weights_when_both_are_empty(profiler):
    cond = profiler.compute_condition_profiles()
    arcs = profiler.compute_arc_profiles()
    cond[6] = profiler._compute_profile(np.empty((0, 8)), [])
    cond[6]["mean_coordinates"] = [0.9] * 8
    e6 = profiler.compute_node_profiles(cond, arcs)["E6"]
    assert e6["blend_weights"] == {"arc": 0.5, "condition": 0.5}
    assert np.allclose(_mean(e6), 0.5 * 0.5 + 0.5 * 0.9)


def test_dominant_primordials(profiler):
    d1 = profiler.compute_node_profiles()["D1"]
    # p:a: 0.9 and 0.7 (mean 0.8, count 2). p:b: 0.8 and 0.5 (mean 0.65, count 2).
    assert d1["dominant_primordials"] == [
        {"primordial_id": "p:a", "mean_weight": 0.8, "count": 2},
        {"primordial_id": "p:b", "mean_weight": 0.65, "count": 2},
    ]
    assert profiler._compute_primordials(["X", "nobody"]) == []


def test_compute_all_shape(profiler):
    out = profiler.compute_all()
    assert set(out) == {"version", "method", "axes", "stats",
                        "condition_profiles", "arc_profiles", "node_profiles"}
    assert out["axes"] == AXES
    assert sorted(out["condition_profiles"]) == ["1", "2", "3", "4", "5", "6"]
    stats = out["stats"]
    assert stats["total_nodes"] == 18
    assert stats["direct_profiles"] + stats["interpolated_profiles"] == 18


def test_save_writes_compute_all(profiler, tmp_path):
    path = tmp_path / "nested" / "node_profiles.json"
    out = profiler.save(str(path))
    assert json.loads(path.read_text(encoding="utf-8")) == json.loads(json.dumps(out))


# ---------------------------------------------------------------------------
# Byte-stable output across hash seeds
# ---------------------------------------------------------------------------
#
# A wider fixture than the one above: one 6-segment text whose segments
# mention 15 entities each, so bins and arcs hold more than the 10 names
# kept in sample_entities, and coordinates vary, so summation order would
# show in the last bits of the means. Primordial "p:tie-a" and "p:tie-b"
# get the same score, so their order depends on the tie-break alone.

WIDE = {f"W{seg}_{i}": seg for seg in range(1, 7) for i in range(15)}


class WideLibrary(StubLibrary):
    def get_segments_per_text(self):
        return {"wide": 6}

    def get_text_segments_ordered(self, text_id):
        return [{"segment_id": f"wide:{seg}", "ordinal": seg,
                 "entity_names": [n for n, s in WIDE.items() if s == seg]}
                for seg in range(1, 7)]

    def get_entities_for_motif_codes(self, codes):
        names = list(WIDE)
        if "F81" in codes:
            return names[::2]
        if "K0" in codes:
            return names[1::3]
        return names[::5]


class WideMapper:
    def get_mapping(self, name):
        return SimpleNamespace(acp_archetype_id=name) if name in WIDE else None


class WideACP:
    def get_instantiations(self, archetype_id):
        i = int(archetype_id.split("_")[1])
        return [{"primordial": "p:tie-b" if i % 2 else "p:tie-a", "weight": 0.5},
                {"primordial": f"p:{i % 4}", "weight": 0.1 + (i % 7) / 10}]


class WideUnified(StubUnified):
    def __init__(self):
        super().__init__()
        self.library = WideLibrary()
        self.mapper = WideMapper()
        self.acp = WideACP()

    def get_entity_coordinates(self, name):
        if name not in WIDE:
            return None
        seg, i = WIDE[name], int(name.split("_")[1])
        return np.array([((seg * 31 + i * 17 + a * 7) % 97) / 97 for a in range(8)])


_RUNNER = """
import json, sys
sys.path.insert(0, sys.argv[1])
import test_node_profiler as t
for unified in (t.StubUnified(), t.WideUnified()):
    print(json.dumps(t.NodeProfiler(unified).compute_all()))
"""


def _run_with_seed(seed):
    env = dict(os.environ, PYTHONHASHSEED=seed)
    done = subprocess.run(
        [sys.executable, "-c", _RUNNER, str(Path(__file__).parent)],
        capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL,
        check=True)
    # Drop the progress lines; keep the two JSON documents.
    return [line for line in done.stdout.splitlines() if line.startswith("{")]


def test_output_is_byte_identical_across_hash_seeds():
    first = _run_with_seed("0")
    assert len(first) == 2
    for seed in ("1", "2", "3"):
        assert _run_with_seed(seed) == first, f"PYTHONHASHSEED={seed}"


def test_lists_are_sorted():
    out = NodeProfiler(WideUnified()).compute_all()
    for p in list(out["condition_profiles"].values()) + list(out["arc_profiles"].values()):
        assert p["sample_entities"] == sorted(p["sample_entities"])
    for p in out["arc_profiles"].values():
        assert p["motif_codes"] == sorted(p["motif_codes"])
    for p in out["node_profiles"].values():
        assert p["sample_entities"] == sorted(p["sample_entities"])


def test_primordial_ties_break_by_id():
    wide = NodeProfiler(WideUnified())
    names = [f"W1_{i}" for i in range(4)]     # tie-a: i 0, 2; tie-b: i 1, 3
    ranked = wide._compute_primordials(names)
    ties = [r["primordial_id"] for r in ranked if r["primordial_id"].startswith("p:tie")]
    assert ties == ["p:tie-a", "p:tie-b"]
    assert wide._compute_primordials(list(reversed(names))) == ranked


@pytest.mark.parametrize("value, expected", [
    (0.7525, 0.753),        # the E3 case: Python's round() gives 0.752 here
    (0.7535, 0.754),
    (0.6524999, 0.652),
    (0.8, 0.8),
    (1 / 3, 0.333),
])
def test_round_half_up(value, expected):
    assert round_half_up(value, 3) == expected
