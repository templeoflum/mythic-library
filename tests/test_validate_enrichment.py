#!/usr/bin/env python3
"""validate_enrichment loads ACP/ from the project root, whatever the cwd."""

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def load():
    spec = importlib.util.spec_from_file_location("validate_enrichment_t", ROOT / "scripts" / "validate_enrichment.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Loaded(Exception):
    pass


def test_acp_dir_is_anchored_to_project_root():
    ve = load()
    assert ve.ACP_DIR == ROOT / "ACP"


def test_main_from_another_cwd_loads_acp_dir(tmp_path, monkeypatch):
    ve = load()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["validate_enrichment.py"])
    seen = []

    def fake_loader(path):
        seen.append(Path(path))
        raise Loaded

    monkeypatch.setattr(ve, "ACPLoader", fake_loader)
    with pytest.raises(Loaded):
        ve.main()
    assert seen == [ROOT / "ACP"]
