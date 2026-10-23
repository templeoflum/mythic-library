#!/usr/bin/env python3
"""Fixture tests for integration/entity_mapper.py.

A small hand-built ACP and library stand in for the real ones, so each
mapping phase and matching rule can be checked by name. Nothing here reads
the ACP data or the database.
"""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integration.acp_loader import ACPLoader  # noqa: E402
from integration.entity_mapper import EntityMapper, _arch_matches_tradition  # noqa: E402

ARCHETYPES = {
    "arch:GR-ZEUS": {"name": "Zeus", "aliases": [{"name": "Jupiter", "fidelity": 0.6}]},
    "arch:RO-JUPITER": {"name": "Jupiter"},
    "arch:NO-ODIN": {"name": "Odin"},
    "arch:GR-HERMES": {"name": "Hermes", "aliases": [{"name": "Odin", "fidelity": 0.4}]},
    "arch:ME-INANNA": {"name": "Inanna", "aliases": [{"name": "Ishtar (Akkadian)", "fidelity": 0.9}]},
    "arch:CE-CUCHULAINN": {"name": "Cú Chulainn"},
    "arch:JP-AMATERASU": {"name": "Amaterasu-Ōmikami"},
    "arch:NO-BALDUR": {"name": "Baldur"},
    "arch:GR-HERAKLES": {"name": "Herakles"},
    "tarot:strength": {"name": "Herakleez"},  # divination: closest by spelling, never a fuzzy hero target
    "persian:ahura-mazda": {"name": "Ahura Mazda", "aliases": ["Ormazd"]},
}

ENTITIES = [
    ("Odin", "norse", "deity"),
    ("Jupiter", "roman", "deity"),
    ("Ishtar", "mesopotamian", "deity"),
    ("Cuchulainn", "celtic", "hero"),
    ("Amaterasu", "japanese", "deity"),
    ("Ormazd", "zoroastrian", "deity"),
    ("Wotan", "norse", "deity"),
    ("Balder", "norse", "deity"),
    ("Heraklees", "greek", "hero"),
    ("Finn", "celtic", "hero"),
    ("Xyzzy", "greek", "deity"),
]

LIBRARY_ALIASES = {
    "Wotan": ["Odin"],      # forward: an unmapped entity's alias is in the ACP
    "Baldur": ["Balder"],   # reverse: the entity is itself an alias of an ACP name
}


class FakeLibrary:
    def get_all_entities(self):
        return [SimpleNamespace(canonical_name=n, primary_tradition=t, entity_type=k)
                for n, t, k in ENTITIES]

    def get_entity_aliases(self):
        return LIBRARY_ALIASES


def fake_acp():
    acp = ACPLoader.__new__(ACPLoader)  # skip loading files
    acp.archetypes = json.loads(json.dumps(ARCHETYPES))
    return acp


@pytest.fixture
def mapper():
    m = EntityMapper(fake_acp(), FakeLibrary())
    m.summary = m.auto_map_all()
    return m


def mapped(mapper, name):
    m = mapper.get_mapping(name)
    return (m.acp_archetype_id, m.method, m.confidence) if m else None


def test_summary_counts(mapper):
    assert mapper.summary == {
        "tradition_aware_matches": 6,
        "library_alias_matches": 2,
        "fuzzy_hero_matches": 1,
        "total_mapped": 9,
        "total_entities": 11,
    }


def test_own_tradition_wins_over_a_foreign_alias(mapper):
    assert mapped(mapper, "Odin") == ("arch:NO-ODIN", "exact_name", 1.0)
    assert mapped(mapper, "Jupiter") == ("arch:RO-JUPITER", "exact_name", 1.0)


def test_alias_rules(mapper):
    assert mapped(mapper, "Ishtar") == ("arch:ME-INANNA", "acp_alias", 0.9)      # "Ishtar (Akkadian)"
    assert mapped(mapper, "Cuchulainn") == ("arch:CE-CUCHULAINN", "collapsed_name", 0.95)
    assert mapped(mapper, "Amaterasu") == ("arch:JP-AMATERASU", "word_boundary", 0.85)
    assert mapped(mapper, "Ormazd") == ("persian:ahura-mazda", "acp_alias", 0.7)  # plain-string alias


def test_library_alias_phases(mapper):
    assert mapped(mapper, "Wotan") == ("arch:NO-ODIN", "library_alias", 0.8)
    assert mapped(mapper, "Balder") == ("arch:NO-BALDUR", "reverse_alias", 0.75)


def test_fuzzy_heroes_skip_divination_and_short_names(mapper):
    m = mapper.get_mapping("Heraklees")
    assert (m.acp_archetype_id, m.method, m.confidence) == ("arch:GR-HERAKLES", "fuzzy_hero", 1.0)
    assert mapper.get_mapping("Finn") is None    # under 4 characters
    assert mapper.get_unmapped_entities() == ["Finn", "Xyzzy"]


def test_mapped_pairs_follow_phase_order(mapper):
    pairs = mapper.get_mapped_pairs()
    assert [p[0] for p in pairs] == [
        "Odin", "Jupiter", "Ishtar", "Cuchulainn", "Amaterasu", "Ormazd",
        "Wotan", "Balder", "Heraklees",
    ]


def test_with_no_tradition_an_exact_name_beats_an_alias():
    m = EntityMapper(fake_acp(), FakeLibrary())
    best = m._pick_best_candidate(m._find_all_candidates("Jupiter"), "")
    assert (best["arch_id"], best["method"]) == ("arch:RO-JUPITER", "exact_name")
    best = m._pick_best_candidate(m._find_all_candidates("Odin"), "greek")
    assert (best["arch_id"], best["method"]) == ("arch:GR-HERMES", "acp_alias")  # native alias first


@pytest.mark.parametrize("arch_id, tradition, expected", [
    ("arch:NO-ODIN", "norse", True),
    ("arch:NO-ODIN", "greek", False),
    ("arch:GR-ZEUS", "atlantean", False),   # tradition with no prefix
])
def test_tradition_prefix(arch_id, tradition, expected):
    assert _arch_matches_tradition(arch_id, tradition) is expected


def test_scheme_prefix_traditions_match():
    # TRADITION_TO_PREFIX maps persian/zoroastrian/christian to an ID scheme
    # (persian:ahura-mazda) rather than an arch: prefix (arch:GR-ZEUS).
    assert _arch_matches_tradition("persian:ahura-mazda", "zoroastrian")
    assert _arch_matches_tradition("persian:ahura-mazda", "persian")
    assert _arch_matches_tradition("christian:michael", "christian")
    assert not _arch_matches_tradition("persian:ahura-mazda", "christian")
    assert not _arch_matches_tradition("christian:michael", "greek")


def test_native_scheme_prefixed_candidate_beats_a_foreign_exact_name():
    # Two scheme-prefixed candidates: the native one should win even though
    # the foreign one is an exact name match.
    m = EntityMapper(fake_acp(), FakeLibrary())
    candidates = [
        {"arch_id": "christian:michael", "method": "exact_name", "fidelity": 1.0},
        {"arch_id": "persian:mithra", "method": "acp_alias", "fidelity": 0.8},
    ]
    best = m._pick_best_candidate(candidates, "zoroastrian")
    assert best["arch_id"] == "persian:mithra"
    best = m._pick_best_candidate(candidates, "christian")
    assert best["arch_id"] == "christian:michael"


def test_word_boundary_rules():
    wb = EntityMapper._is_word_boundary_match
    assert wb("dagda", "the dagda")
    assert wb("izanagi", "izanagi-no-mikoto")
    assert not wb("thor", "thorvald")       # inside a longer word
    assert not wb("ra", "amun-ra")          # under 4 characters


def test_save_and_load_round_trip(mapper, tmp_path):
    path = tmp_path / "mappings.json"
    mapper.save_mappings(str(path))
    fresh = EntityMapper(fake_acp(), FakeLibrary())
    fresh.load_mappings(str(path))
    assert fresh.get_mapped_pairs() == mapper.get_mapped_pairs()
    assert fresh.get_unmapped_entities() == ["Finn", "Xyzzy"]
