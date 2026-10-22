#!/usr/bin/env python3
"""Fixture tests for scripts/extract/extract_entities.py and scripts/motif/tag_motifs.py.

Each test builds a tiny texts/ tree under tmp_path and points the script's
TEXTS_DIR and DATA_DIR there, so nothing reads or writes the real corpus or
data/. Expected values are worked out by hand from the scripts' own rules,
so these pin what the scripts compute today.
"""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
EXTRACT = ROOT / "scripts" / "extract" / "extract_entities.py"
TAG = ROOT / "scripts" / "motif" / "tag_motifs.py"

SEGMENTS = {
    ("greek", "tiny-greek"): {
        "seg_001": "Zeus and Odin met. Zeus spoke.",
        "seg_002": "The creator god spoke to the animal.",
    },
    ("norse", "tiny-norse"): {
        "seg_001": "Thor and Loki walked on. Nothing else here.",
        "seg_002": "No names at all in this one.",
    },
}

MOTIF_INDEX = {
    "_metadata": {"source": "test fixture"},
    "motifs": {
        "A0": {"label": "Creator", "parent": None, "category": "A",
               "keywords": ["creator", "god"]},
        "B1": {"label": "Talking animal", "parent": None, "category": "B",
               "keywords": ["speaks", "animal", "beast"]},
        "Z9": {"label": "No keywords", "parent": None, "category": "Z",
               "keywords": []},
    },
}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def tree(tmp_path):
    texts = tmp_path / "texts"
    for (tradition, text_id), segs in SEGMENTS.items():
        seg_dir = texts / tradition / text_id / "segments"
        seg_dir.mkdir(parents=True)
        index = {"segments": []}
        for seg_id, content in segs.items():
            (seg_dir / f"{seg_id}.txt").write_text(content, encoding="utf-8")
            index["segments"].append({"id": seg_id, "label": seg_id.upper(), "file": f"{seg_id}.txt"})
        (seg_dir / "segments.json").write_text(json.dumps(index), encoding="utf-8")
    data = tmp_path / "data"
    data.mkdir()
    (data / "thompson_motif_index.json").write_text(json.dumps(MOTIF_INDEX), encoding="utf-8")
    return tmp_path


@pytest.fixture
def extract(tree, monkeypatch):
    module = load(EXTRACT, "extract_entities_under_test")
    monkeypatch.setattr(module, "TEXTS_DIR", tree / "texts")
    monkeypatch.setattr(module, "DATA_DIR", tree / "data")
    return module


@pytest.fixture
def tag(tree, monkeypatch):
    module = load(TAG, "tag_motifs_under_test")
    monkeypatch.setattr(module, "TEXTS_DIR", tree / "texts")
    monkeypatch.setattr(module, "DATA_DIR", tree / "data")
    monkeypatch.setattr(module, "MOTIF_INDEX_PATH", tree / "data" / "thompson_motif_index.json")
    return module


# ---------------------------------------------------------------- entities

def test_entity_mentions_and_offsets(extract):
    patterns = extract.build_regex_patterns()
    mentions = extract.extract_entities_from_text("Zeus and Odin met. Zeus spoke.", patterns)
    found = sorted((m["entity_name"], m["char_offset"]) for m in mentions)
    assert found == [("Odin", 9), ("Zeus", 0), ("Zeus", 19)]
    zeus = next(m for m in mentions if m["char_offset"] == 19)
    assert zeus["entity_type"] == "deity"
    assert zeus["tradition"] == "greek"
    assert zeus["sentence_context"] == "Zeus spoke."


def test_extraction_outputs(extract, tree, capsys):
    results, catalog = extract.run_extraction()
    by_id = {r["text_id"]: r for r in results}

    greek = by_id["tiny-greek"]
    assert greek["total_mentions"] == 3
    assert greek["entity_summary"] == {"Zeus": 2, "Odin": 1}
    assert greek["unique_entities"] == ["Odin", "Zeus"]
    assert [s["segment_id"] for s in greek["segments"]] == ["seg_001"]

    norse = by_id["tiny-norse"]
    assert norse["entity_summary"] == {"Thor": 1, "Loki": 1}

    assert list(catalog)[0] == "Zeus"  # most mentions first
    assert catalog["Odin"]["traditions"] == ["greek"]
    assert catalog["Zeus"]["total_mentions"] == 2

    written = json.loads((tree / "data" / "entities.json").read_text(encoding="utf-8"))
    assert written == results


def test_extraction_is_deterministic(extract, tree, capsys):
    extract.run_extraction()
    first = {p: (tree / "data" / p).read_bytes() for p in ("entities.json", "entity_catalog.json")}
    extract.run_extraction()
    second = {p: (tree / "data" / p).read_bytes() for p in ("entities.json", "entity_catalog.json")}
    assert first == second


# ---------------------------------------------------------------- motifs

def test_motif_scores(tag):
    prepared = tag.prepare_keyword_patterns(tag.load_motif_index())
    assert [m["code"] for m in prepared] == ["A0", "B1"]  # Z9 has no keywords

    matches = tag.score_segment("The creator god spoke to the animal.", prepared)
    # A0: 2 of 2 keywords -> min(0.8, 0.3 + 1.0*0.5) = 0.8, short text * 0.7 = 0.56
    # B1: 1 of 3 keywords -> min(0.5, 0.1 + (1/3)*0.4) = 0.2333, * 0.7 = 0.163
    assert [(m["code"], m["confidence"], m["evidence"]) for m in matches] == [
        ("A0", 0.56, ["creator", "god"]),
        ("B1", 0.163, ["animal"]),
    ]


def test_tagging_outputs(tag, tree, capsys):
    results = tag.run_tagging()
    by_id = {r["text_id"]: r for r in results}
    assert by_id["tiny-greek"]["total_tags"] == 2
    assert by_id["tiny-greek"]["unique_motifs"] == ["A0", "B1"]
    assert by_id["tiny-norse"]["total_tags"] == 0

    written = json.loads((tree / "data" / "motif_tags.json").read_text(encoding="utf-8"))
    assert written == results
    dist = json.loads((tree / "data" / "motif_distribution.json").read_text(encoding="utf-8"))
    assert dist["A0"]["traditions"] == ["greek"]
    assert dist["A0"]["max_confidence"] == 0.56


def test_tagging_is_deterministic(tag, tree, capsys):
    tag.run_tagging()
    first = {p: (tree / "data" / p).read_bytes() for p in ("motif_tags.json", "motif_distribution.json")}
    tag.run_tagging()
    second = {p: (tree / "data" / p).read_bytes() for p in ("motif_tags.json", "motif_distribution.json")}
    assert first == second


# ---------------------------------------------------------------- hash seed

RUNNER = """
import importlib.util, sys
from pathlib import Path
script, name, root = sys.argv[1], sys.argv[2], Path(sys.argv[3])
spec = importlib.util.spec_from_file_location(name, script)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.TEXTS_DIR = root / "texts"
m.DATA_DIR = root / "data"
if hasattr(m, "MOTIF_INDEX_PATH"):
    m.MOTIF_INDEX_PATH = root / "data" / "thompson_motif_index.json"
(m.run_extraction if hasattr(m, "run_extraction") else m.run_tagging)()
"""


@pytest.mark.parametrize("script,outputs", [
    (EXTRACT, ("entities.json", "entity_catalog.json")),
    (TAG, ("motif_tags.json", "motif_distribution.json")),
])
def test_same_output_under_different_hash_seeds(tree, script, outputs):
    seen = []
    for seed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=seed)
        subprocess.run([sys.executable, "-c", RUNNER, str(script), script.stem, str(tree)],
                       env=env, check=True, capture_output=True, stdin=subprocess.DEVNULL)
        seen.append({p: (tree / "data" / p).read_bytes() for p in outputs})
    assert seen[0] == seen[1]
