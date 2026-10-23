#!/usr/bin/env python3
"""enrich_minor_arcana reads and writes ACP/ at the project root, whatever the cwd.

Runs against a tmp copy of the minor arcana file; the tracked file is never written.
"""

import importlib.util
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REL = Path("divination") / "tarot" / "minor_arcana.jsonld"


def load():
    spec = importlib.util.spec_from_file_location("enrich_minor_arcana_t", ROOT / "scripts" / "enrich_minor_arcana.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def setup(tmp_path, monkeypatch, mod, argv):
    acp_dir = tmp_path / "project" / "ACP"
    target = acp_dir / REL
    target.parent.mkdir(parents=True)
    shutil.copy(ROOT / "ACP" / REL, target)
    cwd = tmp_path / "elsewhere"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    monkeypatch.setattr(mod, "ACP_DIR", acp_dir)
    monkeypatch.setattr(sys, "argv", ["enrich_minor_arcana.py", *argv])
    return target, cwd


def test_acp_dir_is_anchored_to_project_root():
    assert load().ACP_DIR == ROOT / "ACP"


def test_dry_run_from_another_cwd_reads_acp_dir(tmp_path, monkeypatch, capsys):
    mod = load()
    target, cwd = setup(tmp_path, monkeypatch, mod, [])
    before = target.read_bytes()
    mod.main()
    assert "Total cards enriched:" in capsys.readouterr().out
    assert target.read_bytes() == before
    assert list(cwd.iterdir()) == []


def test_apply_from_another_cwd_writes_under_acp_dir(tmp_path, monkeypatch, capsys):
    mod = load()
    target, cwd = setup(tmp_path, monkeypatch, mod, ["--apply"])
    mod.main()
    assert f"[Changes saved to {target}]" in capsys.readouterr().out
    assert list(cwd.iterdir()) == []
