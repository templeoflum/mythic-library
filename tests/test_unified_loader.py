#!/usr/bin/env python3
"""Fixture tests for integration/unified_loader.py.

The four loaders are replaced with stubs, so these tests check only the
wiring: which paths are opened, how the summary is put together, and the
entity-to-coordinates lookup. Nothing reads the ACP data, the database or
the Miroglyph spec.
"""
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import integration.unified_loader as ul  # noqa: E402


class StubACP:
    def __init__(self, path):
        self.path = path

    def summary(self):
        return {"archetypes": 3}

    def get_coordinates(self, arch_id):
        return {"a1": [0.1] * 8}.get(arch_id)


class StubLibrary:
    def __init__(self, path):
        self.path = path
        self.closed = False

    def summary(self):
        return {"entities": 4}

    def close(self):
        self.closed = True


class StubMiroglyph:
    def __init__(self, path):
        self.path = path

    def summary(self):
        return {"nodes": 5}


class StubMapper:
    result = {"total_entities": 8, "total_mapped": 3}

    def __init__(self, acp, library):
        self.acp, self.library = acp, library
        self.auto_map_calls = 0

    def auto_map_all(self):
        self.auto_map_calls += 1
        return dict(self.result)

    def get_mapping(self, name):
        return SimpleNamespace(acp_archetype_id={"Zeus": "a1", "Hera": "a2"}[name]) \
            if name in ("Zeus", "Hera") else None


@pytest.fixture
def stubbed(monkeypatch):
    monkeypatch.setattr(ul, "ACPLoader", StubACP)
    monkeypatch.setattr(ul, "LibraryLoader", StubLibrary)
    monkeypatch.setattr(ul, "MiroGlyphLoader", StubMiroglyph)
    monkeypatch.setattr(ul, "EntityMapper", StubMapper)


def test_paths_follow_project_root(stubbed, tmp_path):
    u = ul.UnifiedLoader(str(tmp_path))
    assert Path(u.acp.path) == tmp_path / "ACP"
    assert Path(u.library.path) == tmp_path / "data" / "mythic_patterns.db"
    assert Path(u.miroglyph.path) == tmp_path / "miroglyph" / "miroglyph_v4_technical_spec.json"


def test_default_root_is_the_repo(stubbed):
    u = ul.UnifiedLoader()
    assert Path(u.acp.path) == ul.PROJECT_ROOT / "ACP"
    assert ul.PROJECT_ROOT.resolve() == PROJECT_ROOT.resolve()


def test_mapper_gets_the_same_loaders_and_maps_once(stubbed, tmp_path):
    u = ul.UnifiedLoader(str(tmp_path))
    assert u.mapper.acp is u.acp and u.mapper.library is u.library
    assert u.mapper.auto_map_calls == 1
    assert u.map_result == StubMapper.result


def test_summary_combines_the_three_systems(stubbed, tmp_path):
    s = ul.UnifiedLoader(str(tmp_path)).summary()
    assert s["acp"] == {"archetypes": 3}
    assert s["library"] == {"entities": 4}
    assert s["miroglyph"] == {"nodes": 5}
    assert s["mapping"] == {"total_entities": 8, "mapped": 3, "rate": 37.5}


@pytest.mark.parametrize("result, rate", [
    ({"total_entities": 3, "total_mapped": 1}, 33.3),
    ({"total_entities": 0, "total_mapped": 0}, 0.0),
    ({}, 0.0),
])
def test_mapping_rate_rounding_and_empty(stubbed, tmp_path, monkeypatch, result, rate):
    monkeypatch.setattr(StubMapper, "result", result)
    m = ul.UnifiedLoader(str(tmp_path)).summary()["mapping"]
    assert m["rate"] == rate
    assert m["mapped"] == result.get("total_mapped", 0)


def test_entity_coordinates_go_through_the_mapping(stubbed, tmp_path):
    u = ul.UnifiedLoader(str(tmp_path))
    assert u.get_entity_coordinates("Zeus") == [0.1] * 8
    assert u.get_entity_coordinates("Hera") is None      # mapped, no coordinates
    assert u.get_entity_coordinates("Nobody") is None    # not mapped


def test_close_closes_the_library(stubbed, tmp_path):
    u = ul.UnifiedLoader(str(tmp_path))
    u.close()
    assert u.library.closed is True
