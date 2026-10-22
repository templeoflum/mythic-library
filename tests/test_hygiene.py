#!/usr/bin/env python3
"""Tests for the ACP hygiene scripts in scripts/hygiene/.

Small fixtures only; nothing here reads the real ACP data.
"""

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

HYGIENE_DIR = Path(__file__).parent.parent / "scripts" / "hygiene"
SCRIPTS = [
    "audit_hygiene",
    "fix_broken_targets",
    "fix_missing_reverse",
    "fix_primordial_ids",
    "fix_rel_type_prefix",
    "fix_undefined_primordials",
]


def load_script(name):
    spec = importlib.util.spec_from_file_location(f"hygiene_{name}", HYGIENE_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# A minor-arcana-shaped file: suits[].cards[]
SUITS_DOC = {
    "@context": {},
    "@id": "tarot:minor",
    "suits": [
        {
            "@id": "tarot:cups",
            "name": "Cups",
            "cards": [
                {
                    "@id": "tarot:cups_ace",
                    "relationships": [
                        {"type": "CULTURAL_ECHO", "target": "tarot:cups_02", "fidelity": 0.7},
                    ],
                },
                {
                    "@id": "tarot:cups_02",
                    "relationships": [
                        {"type": "CULTURAL_ECHO", "target": "tarot:cups_ace", "fidelity": 0.7},
                    ],
                },
                "not an entry",
            ],
        },
        "not a suit",
    ],
}

# A hero's-journey-shaped file: acts[].stages[]
ACTS_DOC = {
    "@id": "journey:monomyth",
    "acts": [
        {
            "@id": "journey:departure",
            "stages": [
                {
                    "@id": "journey:call",
                    "relationships": [
                        {"type": "CULTURAL_ECHO", "target": "tarot:cups_ace", "fidelity": 0.6},
                    ],
                },
                {"name": "a stage without an @id"},
            ],
        },
        {"stages": [{"@id": "journey:return"}]},
    ],
}


@pytest.mark.parametrize("name", SCRIPTS)
def test_extract_entries_reads_suits_and_cards(name):
    ids = [e["@id"] for e in load_script(name).extract_entries(copy.deepcopy(SUITS_DOC))]
    assert ids == ["tarot:minor", "tarot:cups", "tarot:cups_ace", "tarot:cups_02"]


@pytest.mark.parametrize("name", SCRIPTS)
def test_extract_entries_reads_acts_and_stages(name):
    ids = [e["@id"] for e in load_script(name).extract_entries(copy.deepcopy(ACTS_DOC))]
    assert ids == ["journey:monomyth", "journey:departure", "journey:call", "journey:return"]


@pytest.mark.parametrize("name", SCRIPTS)
def test_extract_entries_flat_shapes_unchanged(name):
    extract = load_script(name).extract_entries
    entries_doc = {"entries": [{"@id": "a:1"}, "skip", {"@id": "a:2"}]}
    graph_doc = {"@graph": [{"@id": "g:1"}]}
    assert [e["@id"] for e in extract(entries_doc)] == ["a:1", "a:2"]
    assert [e["@id"] for e in extract(graph_doc)] == ["g:1"]
    assert [e["@id"] for e in extract([entries_doc, graph_doc])] == ["a:1", "a:2", "g:1"]
    assert list(extract({"name": "no entries here"})) == []


@pytest.mark.parametrize("name", SCRIPTS)
def test_extract_entries_yields_live_objects(name):
    """Fixers edit what extract_entries yields, so it must not copy."""
    doc = copy.deepcopy(SUITS_DOC)
    card = next(e for e in load_script(name).extract_entries(doc) if e["@id"] == "tarot:cups_ace")
    assert card is doc["suits"][0]["cards"][0]


def write_acp(root, files):
    for rel, data in files.items():
        path = root / "ACP" / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def test_fix_broken_targets_leaves_valid_nested_links(tmp_path):
    fbt = load_script("fix_broken_targets")
    write_acp(tmp_path, {"tarot/minor.jsonld": SUITS_DOC, "journey/journey.jsonld": ACTS_DOC})
    all_ids, file_data = fbt.build_id_index(tmp_path)
    assert {"tarot:cups_ace", "tarot:cups_02", "journey:call"} <= all_ids

    for path, data in file_data.items():
        before = copy.deepcopy(data)
        fixes, removals, unresolved = fbt.fix_file(data, str(path), all_ids, apply_mode=True)
        assert (fixes, removals, unresolved) == ([], [], [])
        assert data == before


def test_fix_broken_targets_reaches_nested_broken_links(tmp_path):
    """A broken link inside a card is seen and fixed; its valid sibling is not touched."""
    fbt = load_script("fix_broken_targets")
    doc = copy.deepcopy(SUITS_DOC)
    doc["suits"][0]["cards"][0]["relationships"].append(
        {"type": "CULTURAL_ECHO", "target": "spiral:sun_gold"}
    )
    write_acp(tmp_path, {
        "tarot/minor.jsonld": doc,
        "spiral/spiral.jsonld": {"entries": [{"@id": "spiral:sun-gold"}]},
    })
    all_ids, file_data = fbt.build_id_index(tmp_path)
    data = file_data[tmp_path / "ACP" / "tarot" / "minor.jsonld"]

    fixes, removals, unresolved = fbt.fix_file(data, "tarot/minor.jsonld", all_ids, apply_mode=True)

    assert removals == [] and unresolved == []
    assert [(f["entry"], f["old"], f["new"]) for f in fixes] == [
        ("tarot:cups_ace", "spiral:sun_gold", "spiral:sun-gold")
    ]
    rels = data["suits"][0]["cards"][0]["relationships"]
    assert rels[0] == {"type": "CULTURAL_ECHO", "target": "tarot:cups_02", "fidelity": 0.7}
    assert rels[1] == {"type": "CULTURAL_ECHO", "target": "spiral:sun-gold"}
    assert data["suits"][0]["cards"][1] == SUITS_DOC["suits"][0]["cards"][1]


def test_fix_broken_targets_apply_writes_nothing_when_nested_links_valid(tmp_path, monkeypatch, capsys):
    fbt = load_script("fix_broken_targets")
    write_acp(tmp_path, {"tarot/minor.jsonld": SUITS_DOC, "journey/journey.jsonld": ACTS_DOC})
    before = {p: p.read_bytes() for p in (tmp_path / "ACP").rglob("*.jsonld")}

    monkeypatch.setattr(fbt, "find_project_root", lambda: tmp_path)
    monkeypatch.setattr(sys, "argv", ["fix_broken_targets.py", "--apply"])
    fbt.main()

    out = capsys.readouterr().out
    assert "Fixed:      0" in out and "Removed:    0" in out and "Unresolved: 0" in out
    assert {p: p.read_bytes() for p in (tmp_path / "ACP").rglob("*.jsonld")} == before


def test_audit_counts_nested_links(tmp_path):
    """The audit sees links inside cards and stages. A broken echo also counts
    as a missing reverse, as it does on the real data."""
    audit = load_script("audit_hygiene")
    acts = copy.deepcopy(ACTS_DOC)
    acts["acts"][0]["stages"][0]["relationships"].append(
        {"type": "CULTURAL_ECHO", "target": "tarot:nowhere"}
    )
    write_acp(tmp_path, {"tarot/minor.jsonld": SUITS_DOC, "journey/journey.jsonld": acts})

    result = audit.audit_all(tmp_path)
    broken = result["issues"]["4_broken_targets"]
    missing = result["issues"]["5_missing_reverse_links"]
    assert [(b["entry_id"], b["target"]) for b in broken] == [("journey:call", "tarot:nowhere")]
    assert sorted((m["source"], m["target"]) for m in missing) == [
        ("journey:call", "tarot:cups_ace"),
        ("journey:call", "tarot:nowhere"),
    ]


# ---------------------------------------------------------------------------
# Repeatable output: the same input gives byte-identical output whatever the
# hash seed. Each run is a fresh interpreter with its own PYTHONHASHSEED.
# ---------------------------------------------------------------------------

RUNNER = r"""
import importlib.util, io, json, sys, contextlib
from pathlib import Path
name, root, mode = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
spec = importlib.util.spec_from_file_location(name, Path(sys.argv[4]) / f"{name}.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if mode == "audit":
    result = mod.audit_all(root)
    result.pop("generated_at", None)
    print(json.dumps(result, indent=1))
else:
    mod.find_project_root = lambda: root
    sys.argv = [name, "--dry-run"]
    mod.main()
"""


def echo_fixture():
    """Twelve one-way echoes to entries that exist, and twelve to ones that don't."""
    entries = [{"@id": f"x:{i:02d}", "relationships": []} for i in range(24)]
    for i in range(12):
        entries[i]["relationships"].append({"type": "CULTURAL_ECHO", "target": f"x:{i + 12:02d}", "fidelity": 0.5})
        entries[i]["relationships"].append({"type": "CULTURAL_ECHO", "target": f"y:missing-{i:02d}"})
    return {"x/x.jsonld": {"entries": entries}}


def run_with_seed(name, root, mode, seed):
    import os
    import subprocess
    env = dict(os.environ, PYTHONHASHSEED=str(seed))
    proc = subprocess.run(
        [sys.executable, "-c", RUNNER, name, str(root), mode, str(HYGIENE_DIR)],
        env=env, capture_output=True, text=True, check=True, stdin=subprocess.DEVNULL,
    )
    return proc.stdout


@pytest.mark.parametrize("name,mode", [("audit_hygiene", "audit"), ("fix_missing_reverse", "main")])
def test_output_is_repeatable_across_hash_seeds(tmp_path, name, mode):
    write_acp(tmp_path, echo_fixture())
    outputs = {seed: run_with_seed(name, tmp_path, mode, seed) for seed in (0, 1, 2, 3)}
    assert len(set(outputs.values())) == 1, f"{name} output depends on the hash seed"


def test_audit_missing_reverse_items_unchanged_by_sorting(tmp_path):
    write_acp(tmp_path, echo_fixture())
    result = load_script("audit_hygiene").audit_all(tmp_path)
    missing = result["issues"]["5_missing_reverse_links"]
    assert len(missing) == 24
    assert result["summary"]["5_missing_reverse_links"] == 24
    assert missing == sorted(missing, key=lambda m: (m["source"], m["target"]))
