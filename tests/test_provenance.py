#!/usr/bin/env python3
"""Tests for integration/provenance.py and the inputs section of
scripts/check_published_numbers.py.

Small fixture trees only; nothing here reads or writes the real data.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from integration import provenance  # noqa: E402

SCRIPT = ROOT / "scripts" / "check_published_numbers.py"


@pytest.fixture(scope="module")
def cpn():
    spec = importlib.util.spec_from_file_location("check_published_numbers", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data):
    write(path, json.dumps(data))


@pytest.fixture
def tree(tmp_path):
    write(tmp_path / "texts/greek/a/segments/seg_001.txt", "Zeus spoke.\n")
    write(tmp_path / "texts/norse/b/segments/seg_001.txt", "Odin rode.\n")
    write_json(tmp_path / "data/thompson_motif_index.json",
               {"_metadata": {}, "motifs": {"A0": {}, "B1": {}}})
    write(tmp_path / "scripts/motif/tag_motifs.py", "# tagger\n")
    write(tmp_path / "scripts/extract/extract_entities.py", "# extractor\n")
    write_json(tmp_path / "data/motif_tags.json", [])
    write_json(tmp_path / "data/motif_distribution.json", {})
    write_json(tmp_path / "data/entities.json", [])
    write_json(tmp_path / "data/entity_catalog.json", {})
    write(tmp_path / "ACP/README.md", "[![Version](https://img.shields.io/badge/version-0.3.0-yellow)]()\n")
    write(tmp_path / "ACP/schema/primordials.jsonld", "{}\n")
    write(tmp_path / "ACP/archetypes/greek/zeus.jsonld", "{}\n")
    return tmp_path


def sections_by_name(cpn, root):
    return {s["name"]: s for s in cpn.check_inputs(root)}


# ---------------------------------------------------------------- fingerprints

def test_file_hash_ignores_line_endings(tmp_path):
    (tmp_path / "unix.txt").write_bytes(b"a\nb\n")
    (tmp_path / "windows.txt").write_bytes(b"a\r\nb\r\n")
    assert provenance.file_sha256(tmp_path / "unix.txt") == provenance.file_sha256(tmp_path / "windows.txt")


def test_tree_hash_changes_on_edit_and_rename(tree):
    before = provenance.segments_input(tree)
    assert before["files"] == 2
    seg = tree / "texts/greek/a/segments/seg_001.txt"
    seg.write_text("Zeus spoke twice.\n", encoding="utf-8")
    edited = provenance.segments_input(tree)
    assert edited["sha256"] != before["sha256"]
    seg.rename(seg.with_name("seg_002.txt"))
    assert provenance.segments_input(tree)["sha256"] != edited["sha256"]


def test_motif_index_records_its_size(tree):
    assert provenance.motif_index_input(tree)["motifs"] == 2


def test_acp_covers_loader_files_and_reads_version(tree):
    record = provenance.acp_input(tree)
    assert record["files"] == 2
    assert record["version"] == "0.3.0"
    write(tree / "ACP/legacy/old.jsonld", "{}\n")  # not read by the loader
    assert provenance.acp_input(tree)["sha256"] == record["sha256"]
    write(tree / "ACP/archetypes/greek/zeus.jsonld", '{"changed": true}\n')
    assert provenance.acp_input(tree)["sha256"] != record["sha256"]


def test_missing_input_is_recorded_as_missing(tmp_path):
    current = provenance.current_inputs(tmp_path, {"index": provenance.motif_index_input})
    assert current == {"index": {"missing": True}}


def test_compare_inputs_statuses():
    rows = {r["input"]: r["status"] for r in provenance.compare_inputs(
        {"a": {"sha256": "1"}, "b": {"sha256": "2"}, "c": {"sha256": "3"}},
        {"a": {"sha256": "1"}, "b": {"sha256": "9"}, "d": {"sha256": "4"}},
    )}
    assert rows == {"a": "same", "b": "CHANGED", "c": "missing now", "d": "not recorded"}


def test_record_is_deterministic(tree):
    first = provenance.write_record(tree, "motif tags").read_bytes()
    second = provenance.write_record(tree, "motif tags").read_bytes()
    assert first == second
    record = json.loads(first)
    assert record["generator"] == "scripts/motif/tag_motifs.py"
    assert set(record["outputs"]) == {"data/motif_tags.json", "data/motif_distribution.json"}
    assert record["inputs"]["data/thompson_motif_index.json"]["motifs"] == 2


# ---------------------------------------------------------------- the check

def test_no_records(cpn, tree):
    sections = sections_by_name(cpn, tree)
    assert sections["motif tags"]["note"].startswith("no provenance record")
    assert sections["entities"]["note"].startswith("no provenance record")
    assert sections["v2 validation results"]["note"].startswith("no results file")
    assert not any(cpn._is_stale(s) for s in sections.values())


def test_fresh_record_is_all_same(cpn, tree):
    provenance.write_record(tree, "motif tags")
    section = sections_by_name(cpn, tree)["motif tags"]
    assert section["note"] == ""
    assert {r["status"] for r in section["inputs"]} == {"same"}
    assert {r["status"] for r in section["outputs"]} == {"same"}
    assert not cpn._is_stale(section)


def test_index_change_is_reported(cpn, tree):
    provenance.write_record(tree, "motif tags")
    write_json(tree / "data/thompson_motif_index.json",
               {"_metadata": {}, "motifs": {"A0": {}, "B1": {}, "C2": {}}})
    section = sections_by_name(cpn, tree)["motif tags"]
    row = next(r for r in section["inputs"] if r["input"] == "data/thompson_motif_index.json")
    assert row["status"] == "CHANGED"
    assert (row["recorded"]["motifs"], row["current"]["motifs"]) == (2, 3)
    assert cpn._is_stale(section)


def test_segment_change_reaches_both_records(cpn, tree):
    provenance.write_record(tree, "motif tags")
    provenance.write_record(tree, "entities")
    write(tree / "texts/greek/a/segments/seg_002.txt", "Hera.\n")
    sections = sections_by_name(cpn, tree)
    assert cpn._is_stale(sections["motif tags"])
    assert cpn._is_stale(sections["entities"])


def test_replaced_output_is_reported(cpn, tree):
    provenance.write_record(tree, "entities")
    write_json(tree / "data/entity_catalog.json", {"Zeus": {}})
    section = sections_by_name(cpn, tree)["entities"]
    statuses = {r["output"]: r["status"] for r in section["outputs"]}
    assert statuses["data/entity_catalog.json"] == "CHANGED since the record"
    assert statuses["data/entities.json"] == "same"


def test_partial_run_is_noted(cpn, tree):
    provenance.write_record(tree, "motif tags", text_filter="tiny-greek")
    assert "--text tiny-greek" in sections_by_name(cpn, tree)["motif tags"]["note"]


def test_v2_results_inputs(cpn, tree):
    results = tree / provenance.V2_RESULTS
    write_json(results, {"version": "v2"})
    section = sections_by_name(cpn, tree)["v2 validation results"]
    assert section["note"].startswith("no inputs recorded")

    write_json(results, {"version": "v2",
                         "inputs": provenance.current_inputs(tree, provenance.V2_INPUTS)})
    section = sections_by_name(cpn, tree)["v2 validation results"]
    assert {r["status"] for r in section["inputs"]} == {"same"}

    write(tree / "ACP/archetypes/greek/hera.jsonld", "{}\n")
    section = sections_by_name(cpn, tree)["v2 validation results"]
    acp = next(r for r in section["inputs"] if r["input"] == "ACP")
    assert acp["status"] == "CHANGED"
    assert (acp["recorded"]["files"], acp["current"]["files"]) == (2, 3)


def test_report_text(cpn, tree):
    provenance.write_record(tree, "motif tags")
    write_json(tree / "data/thompson_motif_index.json", {"motifs": {"A0": {}}})
    text = cpn.format_inputs(cpn.check_inputs(tree))
    assert "input data/thompson_motif_index.json: CHANGED" in text
    assert "motifs 2" in text and "motifs 1" in text
    assert "1 of 3 derived files were built from inputs that have changed since; 2 have no record" in text


def test_main_reports_inputs_and_writes_nothing(cpn, tree, capsys):
    provenance.write_record(tree, "motif tags")
    contents = {p: p.read_bytes() for p in tree.rglob("*") if p.is_file()}
    assert cpn.main(["--root", str(tree), "--skip-slow"]) == 0
    assert {p: p.read_bytes() for p in tree.rglob("*") if p.is_file()} == contents
    out = capsys.readouterr().out
    assert "Inputs of derived files" in out
    assert "Report only; nothing was rebuilt." in out
