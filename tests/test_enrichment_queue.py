#!/usr/bin/env python3
"""enrichment_queue reads and writes under ACP/ at the project root, whatever the cwd."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load():
    spec = importlib.util.spec_from_file_location("enrichment_queue_t", ROOT / "scripts" / "enrichment_queue.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_acp_dir_is_anchored_to_project_root():
    eq = load()
    assert eq.ACP_DIR == ROOT / "ACP"


def test_main_from_another_cwd_writes_only_under_acp_dir(tmp_path, monkeypatch):
    eq = load()
    acp_dir = tmp_path / "project" / "ACP"
    cwd = tmp_path / "elsewhere"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    monkeypatch.setattr(eq, "ACP_DIR", acp_dir)

    seen = []

    class FakeLoader:
        def __init__(self, path):
            seen.append(Path(path))
            self.archetypes = {
                "gr:zeus": {"@id": "gr:zeus", "name": "Zeus", "description": "Sky father"},
            }

    monkeypatch.setattr(eq, "ACPLoader", FakeLoader)
    eq.main()

    assert seen == [acp_dir]
    assert list(cwd.iterdir()) == []
    queue = json.loads((acp_dir / "tools" / "enrichment_queue.json").read_text())
    assert queue["total_archetypes"] == 1
    compact = json.loads((acp_dir / "tools" / "enrichment_priority.json").read_text())
    assert compact["priority_order"][0]["id"] == "gr:zeus"
