#!/usr/bin/env python3
"""Validation scripts save under the project root, whatever the working directory."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_miroglyph_structure_v2_saves_under_project_root(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mod = load("validation/v2_tests/miroglyph_structure_v2.py", "miro_v2_paths")
    assert mod.PROJECT_ROOT == ROOT
    assert mod.OUTPUT_PATH == ROOT / "outputs" / "validation" / "miroglyph_structure_v2.json"
    assert mod.OUTPUT_PATH.is_absolute()


def test_miroglyph_structure_v2_has_no_cwd_relative_output():
    source = (ROOT / "validation/v2_tests/miroglyph_structure_v2.py").read_text()
    assert 'Path("outputs' not in source
