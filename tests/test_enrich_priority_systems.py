#!/usr/bin/env python3
"""enrich_priority_systems finds its ACP files at the project root, whatever the cwd.

Dry runs only, against a tmp copy of ACP/; the tracked files are never written.
"""

import hashlib
import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def load():
    spec = importlib.util.spec_from_file_location("enrich_priority_systems_t", ROOT / "scripts" / "enrich_priority_systems.py")
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
def project(tmp_path_factory):
    project = tmp_path_factory.mktemp("project")
    shutil.copytree(ROOT / "ACP", project / "ACP")
    return project


def dry_run(mod, project, cwd, argv, monkeypatch, capsys):
    monkeypatch.chdir(cwd)
    monkeypatch.setattr(mod, "PROJECT_ROOT", project)
    monkeypatch.setattr(sys, "argv", ["enrich_priority_systems.py", *argv])
    mod.main()
    return capsys.readouterr().out


def test_project_root_is_anchored():
    assert load().PROJECT_ROOT == ROOT


@pytest.mark.parametrize("argv", [[], ["--all"]])
def test_dry_run_is_the_same_from_any_cwd(argv, project, tmp_path, monkeypatch, capsys):
    mod = load()
    before = tree_hash(project / "ACP")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    from_project = dry_run(mod, project, project, argv, monkeypatch, capsys)
    from_elsewhere = dry_run(mod, project, elsewhere, argv, monkeypatch, capsys)

    assert "not found" not in from_elsewhere
    assert from_elsewhere == from_project
    assert list(elsewhere.iterdir()) == []
    assert tree_hash(project / "ACP") == before
