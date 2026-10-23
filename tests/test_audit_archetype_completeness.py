#!/usr/bin/env python3
"""audit_archetype_completeness reads and writes ACP/ at the project root, whatever the cwd."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load():
    spec = importlib.util.spec_from_file_location(
        "audit_completeness_t", ROOT / "scripts" / "audit_archetype_completeness.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_acp_dir_is_anchored_to_project_root():
    audit = load()
    assert audit.ACP_DIR == ROOT / "ACP"


def test_main_from_another_cwd_uses_acp_dir(tmp_path, monkeypatch):
    audit = load()
    acp_dir = tmp_path / "project" / "ACP"
    (acp_dir / "tools").mkdir(parents=True)
    cwd = tmp_path / "elsewhere"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    monkeypatch.setattr(audit, "ACP_DIR", acp_dir)

    seen = []

    class FakeLoader:
        def __init__(self, path):
            seen.append(Path(path))
            self.archetypes = {
                "gr:zeus": {"@id": "gr:zeus", "name": "Zeus", "description": "Sky father"},
            }

    monkeypatch.setattr(audit, "ACPLoader", FakeLoader)
    audit.main()

    assert seen == [acp_dir]
    assert list(cwd.iterdir()) == []
    assert json.loads((acp_dir / "tools" / "completeness_audit.json").read_text())
