"""Tests for integration/acp_loader.py on a small ACP tree built in tmp_path.

Nothing here reads the real ACP data.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integration.acp_loader import ACPLoader, AXES  # noqa: E402


def coords(**over):
    c = {a: 0.5 for a in AXES}
    for k, v in over.items():
        c[k.replace("_", "-")] = v
    return c


FILES = {
    "schema/primordials.jsonld": {"entries": [
        {"@id": "primordial:trickster", "name": "Trickster"},
        {"@id": "primordial:creator", "name": "Creator"},
    ]},
    "archetypes/greek/GR.jsonld": {"entries": [
        {"@id": "system:greek", "@type": "System", "name": "Greek"},
        {"@id": "arch:GR-ZEUS", "name": "Zeus",
         "spectralCoordinates": coords(order_chaos=0.1),
         "aliases": [{"name": "Jupiter", "fidelity": 0.8}, "Dias", 7, {"name": ""}],
         "instantiates": [{"primordial": "primordial:creator", "weight": 0.9}],
         "relationships": [
             {"type": "CULTURAL_ECHO", "target": "arch:NO-ODIN", "fidelity": 0.7},
             {"type": "POLAR_OPPOSITE", "target": "arch:GR-HERA", "axis": "axis:order-chaos"},
         ]},
        {"@id": "arch:GR-HERA", "name": "Hera",
         "spectralCoordinates": coords(order_chaos=0.4),
         "relationships": [{"type": "CULTURAL_ECHO", "target": "arch:GR-ZEUS"}]},
        {"@id": "arch:GR-NOCOORDS", "name": "No Coordinates"},
    ]},
    "archetypes/norse/NO.jsonld": {"@graph": [
        {"@id": "arch:NO-ODIN", "name": "Odin",
         "spectralCoordinates": {"order-chaos": 0.9},  # other axes default to 0.5
         "aliases": ["Odin Allfather", "Wotan"]},
        {"@id": "arch:NO-RAGNAROK", "name": "Ragnarok", "spectralCoordinates": coords()},
    ]},
    "divination/tarot/minor.jsonld": {"@id": "system:minor", "@type": "skos:ConceptScheme",
        "suits": [
            {"name": "Cups", "cards": [
                {"@id": "tarot:cups-ace", "name": "Ace of Cups", "spectralCoordinates": coords()},
                {"@id": "tarot:cups-two", "name": "Two of Cups"},  # no coordinates
                {"name": "Unnamed card", "spectralCoordinates": coords()},  # no @id
            ]},
            {"name": "Swords", "cards": [
                {"@id": "tarot:swords-ace", "name": "Ace of Swords", "spectralCoordinates": coords()},
            ]},
        ]},
    "modern/journey.jsonld": {"entries": [], "acts": [
        {"name": "Departure", "stages": [
            {"@id": "journey:call", "name": "The Call", "spectralCoordinates": coords()},
            {"@id": "journey:refusal", "name": "Refusal"},
            {"name": "Unnamed stage", "spectralCoordinates": coords()},  # no @id
        ]},
    ]},
    "psychology/single.jsonld": {"@id": "psych:shadow", "name": "Shadow",
                                  "spectralCoordinates": coords(light_shadow=1.0)},
    "calibration/origin.jsonld": {"entries": [
        {"@id": "calibration:origin", "name": "Origin", "spectralCoordinates": coords()},
    ]},
    # Not one of the loaded domains:
    "tools/ignored.jsonld": {"entries": [
        {"@id": "arch:IGNORED", "name": "Ignored", "spectralCoordinates": coords()},
    ]},
}


@pytest.fixture(scope="module")
def acp(tmp_path_factory):
    root = tmp_path_factory.mktemp("ACP")
    for rel, doc in FILES.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(doc), encoding="utf-8")
    (root / "archetypes" / "broken.jsonld").write_text("{not json", encoding="utf-8")
    return ACPLoader(str(root))


# ── Loading and nested entries ───────────────────────────────

class TestLoading:
    def test_archetype_ids(self, acp):
        assert sorted(acp.archetypes) == [
            "arch:GR-HERA", "arch:GR-ZEUS", "arch:NO-ODIN", "arch:NO-RAGNAROK",
            "calibration:origin", "journey:call", "psych:shadow",
            "tarot:cups-ace", "tarot:swords-ace",
        ]

    def test_suits_cards_need_id_and_coordinates(self, acp):
        assert "tarot:cups-ace" in acp.archetypes
        assert "tarot:swords-ace" in acp.archetypes
        assert "tarot:cups-two" not in acp.archetypes

    def test_acts_stages_need_id_and_coordinates(self, acp):
        assert "journey:call" in acp.archetypes
        assert "journey:refusal" not in acp.archetypes

    def test_graph_and_single_entry_files(self, acp):
        assert "arch:NO-ODIN" in acp.archetypes
        assert "psych:shadow" in acp.archetypes

    def test_entry_without_coordinates_is_not_an_archetype(self, acp):
        assert "arch:GR-NOCOORDS" not in acp.archetypes

    def test_other_folders_not_loaded(self, acp):
        assert "arch:IGNORED" not in acp.archetypes

    def test_primordials_and_systems(self, acp):
        assert acp.get_primordial_ids() == ["primordial:creator", "primordial:trickster"]
        assert sorted(acp.systems) == ["system:greek", "system:minor"]

    def test_summary(self, acp):
        assert acp.summary() == {
            "archetypes": 9,
            "primordials": 2,
            "systems": 2,
            "alias_entries": 6,
            "with_coordinates": 9,
        }


# ── Relationships ────────────────────────────────────────────

class TestRelationships:
    def test_all(self, acp):
        rels = acp.get_all_relationships()
        assert len(rels) == 3
        assert sorted((r["source"], r["type"], r["target"]) for r in rels) == [
            ("arch:GR-HERA", "CULTURAL_ECHO", "arch:GR-ZEUS"),
            ("arch:GR-ZEUS", "CULTURAL_ECHO", "arch:NO-ODIN"),
            ("arch:GR-ZEUS", "POLAR_OPPOSITE", "arch:GR-HERA"),
        ]

    def test_filter_and_properties_kept(self, acp):
        echoes = acp.get_all_relationships("CULTURAL_ECHO")
        assert len(echoes) == 2
        polar = acp.get_all_relationships("POLAR_OPPOSITE")
        assert polar == [{"source": "arch:GR-ZEUS", "type": "POLAR_OPPOSITE",
                          "target": "arch:GR-HERA", "axis": "axis:order-chaos"}]
        assert acp.get_all_relationships("SHADOW") == []

    def test_source_data_not_mutated(self, acp):
        acp.get_all_relationships()
        assert "source" not in acp.archetypes["arch:GR-ZEUS"]["relationships"][0]


# ── ID resolution and coordinates ────────────────────────────

class TestResolution:
    def test_coordinates_in_axes_order(self, acp):
        c = acp.get_coordinates("arch:GR-ZEUS")
        assert c.tolist() == [0.1] + [0.5] * 7

    def test_missing_axis_defaults_to_half(self, acp):
        assert acp.get_coordinates("arch:NO-ODIN").tolist() == [0.9] + [0.5] * 7

    def test_unknown_id(self, acp):
        assert acp.get_coordinates("arch:NOPE") is None
        assert acp.calculate_distance("arch:GR-ZEUS", "arch:NOPE") is None
        assert acp.get_nearby("arch:NOPE") == []
        assert acp.get_alias_info("arch:NOPE") == []
        assert acp.get_instantiations("arch:NOPE") == []

    def test_distance(self, acp):
        assert acp.calculate_distance("arch:GR-ZEUS", "arch:NO-ODIN") == pytest.approx(0.8)
        assert acp.calculate_distance("psych:shadow", "tarot:cups-ace") == pytest.approx(0.5)
        # Euclidean over two axes: sqrt(0.4^2 + 0.5^2)
        assert acp.calculate_distance("arch:GR-ZEUS", "psych:shadow") == pytest.approx(math.sqrt(0.41))

    def test_nearby_sorted_and_thresholded(self, acp):
        near = acp.get_nearby("arch:GR-HERA", threshold=0.35)
        ids = [i for i, _ in near]
        assert len(near) == 6
        assert [d for _, d in near] == sorted(d for _, d in near)
        assert "arch:GR-HERA" not in ids
        assert "arch:NO-ODIN" not in ids  # 0.5 away
        assert "psych:shadow" not in ids  # ~0.51 away
        assert ids[-1] == "arch:GR-ZEUS"
        assert dict(near)["arch:GR-ZEUS"] == pytest.approx(0.3)
        assert dict(near)["tarot:cups-ace"] == pytest.approx(0.1)

    def test_alias_and_instantiation_info(self, acp):
        assert acp.get_alias_info("arch:GR-ZEUS")[0] == {"name": "Jupiter", "fidelity": 0.8}
        assert acp.get_instantiations("arch:GR-ZEUS") == [
            {"primordial": "primordial:creator", "weight": 0.9}]

    def test_all_names(self, acp):
        names = acp.get_all_names()
        assert names["arch:GR-ZEUS"] == "Zeus"
        assert len(names) == 9


class TestFindByName:
    def ids(self, acp, name):
        return [(r["id"], r["match_type"]) for r in acp.find_by_name(name)]

    @pytest.mark.parametrize("name", ["Zeus", "  zeus ", "JUPITER", "dias"])
    def test_exact_name_and_aliases(self, acp, name):
        assert self.ids(acp, name) == [("arch:GR-ZEUS", "exact")]

    def test_non_string_and_empty_aliases_ignored(self, acp):
        assert acp.find_by_name("7") == []
        assert acp.find_by_name("") == []

    def test_word_substring_match(self, acp):
        # "allfather" is a whole word inside the alias "odin allfather".
        assert self.ids(acp, "Allfather") == [("arch:NO-ODIN", "substring")]
        # The alias "wotan" is a whole word inside the query.
        assert self.ids(acp, "Wotan the Wanderer") == [("arch:NO-ODIN", "substring")]

    def test_partial_word_does_not_match(self, acp):
        assert acp.find_by_name("father") == []
        assert acp.find_by_name("Ragna") == []

    def test_short_key_no_substring(self, acp):
        # Under 4 characters only exact hits count (prevents Ra -> Ragnarok).
        assert acp.find_by_name("Ace") == []

    def test_exact_hit_suppresses_substring(self, acp):
        # "odin" is exact; "odin allfather" would also match as a word.
        assert self.ids(acp, "Odin") == [("arch:NO-ODIN", "exact")]

    def test_dedup_across_aliases(self, acp):
        # Several aliases of one archetype match; it is listed once.
        assert self.ids(acp, "cups") == [("tarot:cups-ace", "substring")]
        res = acp.find_by_name("Odin Allfather Wotan")
        assert [r["id"] for r in res] == ["arch:NO-ODIN"]
