#!/usr/bin/env python3
"""The enrich_* scripts find ACP/ at the project root, whatever the cwd.

Each script does a dry run against a tmp copy of ACP/; the tracked files are never written.
"""

import hashlib
import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = [
    "enrich_from_correspondences",
    "enrich_phase2_domains",
    "enrich_phase2_echoes",
    "enrich_phase3_aliases",
    "enrich_phase3_stubs",
]


def load(name):
    spec = importlib.util.spec_from_file_location(f"{name}_t", ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tree_hash(path):
    h = hashlib.sha256()
    for f in sorted(p for p in path.rglob("*") if p.is_file()):
        h.update(str(f.relative_to(path)).encode())
        h.update(f.read_bytes())
    return h.hexdigest()


@pytest.fixture(scope="module")
def acp_copy(tmp_path_factory):
    acp_dir = tmp_path_factory.mktemp("project") / "ACP"
    shutil.copytree(ROOT / "ACP", acp_dir)
    return acp_dir


def dry_run(mod, acp_dir, cwd, monkeypatch, capsys):
    monkeypatch.chdir(cwd)
    monkeypatch.setattr(mod, "ACP_DIR", acp_dir)
    monkeypatch.setattr(sys, "argv", [f"{mod.__name__}.py"])
    mod.main()
    return capsys.readouterr().out


@pytest.mark.parametrize("name", SCRIPTS)
def test_acp_dir_is_anchored_to_project_root(name):
    assert load(name).ACP_DIR == ROOT / "ACP"


@pytest.mark.parametrize("name", SCRIPTS)
def test_dry_run_is_the_same_from_any_cwd(name, acp_copy, tmp_path, monkeypatch, capsys):
    mod = load(name)
    before = tree_hash(acp_copy)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    from_project = dry_run(mod, acp_copy, acp_copy.parent, monkeypatch, capsys)
    from_elsewhere = dry_run(mod, acp_copy, elsewhere, monkeypatch, capsys)

    assert from_elsewhere == from_project
    assert list(elsewhere.iterdir()) == []
    assert tree_hash(acp_copy) == before
