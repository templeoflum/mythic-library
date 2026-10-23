#!/usr/bin/env python3
"""Tests for scripts/motif/build_motif_index.py.

build_index() is pointed at tmp_path, so the repo's data/ is only read.
"""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "motif" / "build_motif_index.py"
TRACKED = ROOT / "data" / "thompson_motif_index.json"


@pytest.fixture(scope="module")
def bmi():
    spec = importlib.util.spec_from_file_location("build_motif_index_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def built(bmi, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(bmi, "DATA_DIR", tmp_path)
    bmi.build_index()
    return tmp_path / "thompson_motif_index.json"


def test_metadata_matches_entries(bmi, built):
    data = json.loads(built.read_text(encoding="utf-8"))
    meta = data["_metadata"]
    assert meta["total_entries"] == len(data["motifs"]) == len(bmi.MOTIF_INDEX)
    assert meta["categories"] == sorted({m["category"] for m in bmi.MOTIF_INDEX.values()})


def test_build_is_deterministic(bmi, built):
    first = built.read_bytes()
    bmi.build_index()
    assert built.read_bytes() == first


def test_tracked_index_is_what_the_script_builds(built):
    # The tracked file is generated; a hand edit to either side shows up here.
    assert built.read_bytes() == TRACKED.read_bytes()


def test_entry_shape(bmi):
    for code, motif in bmi.MOTIF_INDEX.items():
        assert set(motif) == {"label", "parent", "category", "keywords"}, code
        assert code.startswith(motif["category"]), code
        assert motif["label"], code
        assert motif["keywords"] and all(isinstance(k, str) and k.strip() for k in motif["keywords"]), code


def test_parents_exist_and_share_a_category(bmi):
    for code, motif in bmi.MOTIF_INDEX.items():
        parent = motif["parent"]
        if parent is not None:
            assert parent in bmi.MOTIF_INDEX, code
            assert bmi.MOTIF_INDEX[parent]["category"] == motif["category"], code
