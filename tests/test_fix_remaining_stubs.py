#!/usr/bin/env python3
"""fix_remaining_stubs reads and writes ACP/ at the project root, whatever the cwd."""

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load():
    spec = importlib.util.spec_from_file_location("fix_remaining_stubs_t", ROOT / "scripts" / "fix_remaining_stubs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path, entries):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"entries": entries}))


def make_acp(acp_dir, frs):
    house_id = next(iter(frs.HOUSE_COORDINATES))
    greek_id = next(iter(frs.GREEK_ASPECTS))
    houses = acp_dir / "divination" / "astrology" / "houses.jsonld"
    greek = acp_dir / "archetypes" / "greek" / "GR_OLYMPIANS.jsonld"
    write(houses, [{"@id": house_id}])
    write(greek, [{"@id": greek_id}])
    return houses, greek


def test_acp_dir_is_anchored_to_project_root():
    assert load().ACP_DIR == ROOT / "ACP"


def test_dry_run_from_another_cwd_finds_the_files(tmp_path, monkeypatch, capsys):
    frs = load()
    acp_dir = tmp_path / "project" / "ACP"
    houses, greek = make_acp(acp_dir, frs)
    before = (houses.read_text(), greek.read_text())
    cwd = tmp_path / "elsewhere"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    monkeypatch.setattr(frs, "ACP_DIR", acp_dir)
    monkeypatch.setattr(sys, "argv", ["fix_remaining_stubs.py"])

    frs.main()

    out = capsys.readouterr().out
    assert "Houses fixed: 1" in out
    assert "Greek aspects fixed: 1" in out
    assert (houses.read_text(), greek.read_text()) == before
    assert list(cwd.iterdir()) == []


def test_apply_from_another_cwd_writes_under_acp_dir(tmp_path, monkeypatch):
    frs = load()
    acp_dir = tmp_path / "project" / "ACP"
    houses, greek = make_acp(acp_dir, frs)
    cwd = tmp_path / "elsewhere"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    monkeypatch.setattr(frs, "ACP_DIR", acp_dir)
    monkeypatch.setattr(sys, "argv", ["fix_remaining_stubs.py", "--apply"])

    frs.main()

    assert "spectralCoordinates" in json.loads(houses.read_text())["entries"][0]
    assert "spectralCoordinates" in json.loads(greek.read_text())["entries"][0]
    assert list(cwd.iterdir()) == []
