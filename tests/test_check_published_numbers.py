#!/usr/bin/env python3
"""Tests for scripts/check_published_numbers.py.

Small fixture trees only; nothing here reads the real corpus or README.
"""

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "check_published_numbers.py"

README = """\
| Pattern database | 3 segments, 2 entities, 4 mentions, 9 motifs |
Built ... (2 motifs, 3 tags), ...
| `motifs` | 9 | Thompson Motif Index |
| `motif_tags` | 3 | Motif assignments |
│   └── entity_mapper.py   # Map 1/2 library entities to ACP archetypes
cluster in 8D space (21% separation ratio)
"""


@pytest.fixture(scope="module")
def cpn():
    spec = importlib.util.spec_from_file_location("check_published_numbers", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


@pytest.fixture
def tree(tmp_path):
    (tmp_path / "README.md").write_text(README, encoding="utf-8")
    write_json(tmp_path / "texts/greek/a/segments/segments.json",
               {"segments": [{"id": "seg_001"}, {"id": "seg_002"}]})
    write_json(tmp_path / "texts/norse/b/segments/segments.json",
               {"segments": [{"id": "seg_001"}]})
    write_json(tmp_path / "data/entity_catalog.json", {"Zeus": {}, "Odin": {}})
    write_json(tmp_path / "data/entities.json", [
        {"text_id": "a", "segments": [{"mentions": [{}, {}]}, {"mentions": [{}]}]},
        {"text_id": "b", "segments": [{"mentions": []}]},
    ])
    write_json(tmp_path / "data/motif_tags.json", [
        {"text_id": "a", "segments": [{"tags": [{"code": "A1"}, {"code": "B2"}]}]},
        {"text_id": "b", "segments": [{"tags": [{"code": "A1"}]}]},
    ])
    write_json(tmp_path / "data/thompson_motif_index.json",
               {"_metadata": {}, "motifs": {f"M{i}": {} for i in range(9)}})
    return tmp_path


def test_reads_readme_figures(cpn):
    found = cpn.read_readme_figures(README)
    assert found["segments"] == [3]
    assert found["entities"] == [2]
    assert found["mentions"] == [4]
    assert found["motif tags"] == [3]
    assert found["motifs (index)"] == [9]
    assert found["motifs (tagged)"] == [2]
    assert found["mapped entities"] == [1]
    assert found["separation ratio %"] == [21]


def test_reads_numbers_with_commas(cpn):
    found = cpn.read_readme_figures("4,000 segments and 28,104 mentions")
    assert found["segments"] == [4000]
    assert found["mentions"] == [28104]


def test_counts_from_data(cpn, tree):
    assert cpn.count_segments(tree) == 3
    assert cpn.count_entities(tree) == 2
    assert cpn.count_mentions(tree) == 3
    assert cpn.count_motif_tags(tree) == 3
    assert cpn.count_tagged_motifs(tree) == 2
    assert cpn.count_index_motifs(tree) == 9


def test_compare_marks_same_and_differs(cpn, tree):
    rows = {r["figure"]: r for r in cpn.compare(tree, skip_slow=True)}
    assert rows["segments"]["note"] == "same"
    assert rows["mentions"]["note"] == "DIFFERS"          # README 4, data 3
    assert rows["motifs (tagged)"]["note"] == "same"
    assert rows["mapped entities"]["note"].startswith("not computed")  # no database
    assert rows["separation ratio %"]["note"] == "not computed: skipped (--skip-slow)"


def test_main_exits_0_and_writes_nothing(cpn, tree, capsys):
    before = sorted(p.relative_to(tree) for p in tree.rglob("*"))
    contents = {p: p.read_bytes() for p in tree.rglob("*") if p.is_file()}
    assert cpn.main(["--root", str(tree), "--skip-slow"]) == 0
    assert sorted(p.relative_to(tree) for p in tree.rglob("*")) == before
    assert all(p.read_bytes() == b for p, b in contents.items())
    assert "figures differ from the README" in capsys.readouterr().out


def test_main_exits_0_when_readme_is_missing(cpn, tmp_path, capsys):
    assert cpn.main(["--root", str(tmp_path), "--skip-slow"]) == 0
    assert "could not run" in capsys.readouterr().out
