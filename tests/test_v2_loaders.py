"""Tests for the inputs the v2 harness loads: LibraryLoader and MiroGlyphLoader.

validation/v2_run.py reads the library database through
integration/library_loader.py and the Miroglyph spec through
integration/miroglyph_loader.py. (The ACP loader has its own tests in
test_acp_loader.py.) These tests check the loaders only, never the
verdicts. The library tests run on a tiny hand-built database that uses
create_db.py's schema, and every expected value is worked out by hand
from it.
"""

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from integration.library_loader import (  # noqa: E402
    CooccurrencePair, Entity, LibraryLoader)
from integration.miroglyph_loader import MiroGlyphLoader, MiroNode  # noqa: E402


def _schema():
    spec = importlib.util.spec_from_file_location(
        "create_db_schema", ROOT / "scripts" / "database" / "create_db.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.SCHEMA


# ---------------------------------------------------------------------------
# LibraryLoader
# ---------------------------------------------------------------------------

TEXTS = [
    # text_id, title, tradition, author, material_type, word_count, usable
    ("t1", "Theogony", "greek", "Hesiod", "Epic", 100, 1),
    ("t2", "Voluspa", "norse", "Anon", "Poem", 50, 1),
    ("t3", "Hymn", "egyptian", "Anon", "Hymn", 10, 0),
]
SEGMENTS = [
    # segment_id, text_id, label, ordinal, word_count
    ("t1:s2", "t1", "Book Two", 2, 40),     # inserted out of order on purpose
    ("t1:s1", "t1", "Book One", 1, 60),
    ("t2:s1", "t2", "Stanza", 1, 50),
]
ENTITIES = [
    # entity_id, canonical_name, total_mentions
    (1, "Zeus", 5), (2, "Apollo", 3), (3, "Odin", 2), (4, "Hera", 0),
]
ALIASES = [(1, "Jove"), (1, "Dias"), (3, "Woden")]
MENTIONS = [
    # entity_id, segment_id
    (1, "t1:s1"), (1, "t1:s1"), (2, "t1:s1"),
    (1, "t1:s2"), (2, "t1:s2"),
    (3, "t2:s1"), (1, "t2:s1"),
]
MOTIFS = [("A1", "Creator", "A"), ("F81", "Descent", "F"), ("K0", "Trick", "K")]
TAGS = [
    # motif_code, segment_id, confidence
    ("A1", "t1:s1", 0.6),
    ("F81", "t1:s2", 0.3),     # exactly on the 0.3 floor: kept
    ("A1", "t1:s2", 0.29),     # under the floor: dropped
    ("K0", "t2:s1", 0.1),      # under the floor: dropped
    ("A1", "t2:s1", 0.5),
]
PATTERNS = [
    # pattern_name, motif_codes, attestation_count
    ("rare_pattern", ["F81"], 1),
    ("common_pattern", ["A1", "A600"], 3),
]


@pytest.fixture(scope="module")
def db_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("lib") / "tiny.db"
    conn = sqlite3.connect(str(path))
    conn.executescript(_schema())
    conn.executemany(
        "INSERT INTO texts (text_id, title, tradition, author, material_type, "
        "word_count, usable) VALUES (?,?,?,?,?,?,?)", TEXTS)
    conn.executemany(
        "INSERT INTO segments (segment_id, text_id, label, ordinal, word_count) "
        "VALUES (?,?,?,?,?)", SEGMENTS)
    conn.executemany(
        "INSERT INTO entities (entity_id, canonical_name, entity_type, "
        "primary_tradition, total_mentions, text_count, tradition_count) "
        "VALUES (?, ?, 'deity', 'x', ?, 1, 1)", ENTITIES)
    conn.executemany(
        "INSERT INTO entity_aliases (entity_id, alias_name) VALUES (?,?)", ALIASES)
    conn.executemany(
        "INSERT INTO entity_mentions (entity_id, segment_id) VALUES (?,?)", MENTIONS)
    conn.executemany(
        "INSERT INTO motifs (motif_code, label, category) VALUES (?,?,?)", MOTIFS)
    conn.executemany(
        "INSERT INTO motif_tags (motif_code, segment_id, confidence) VALUES (?,?,?)",
        TAGS)
    conn.executemany(
        "INSERT INTO patterns (pattern_name, description, motif_codes, "
        "attestation_count, tradition_count, confidence) "
        "VALUES (?, 'd', ?, ?, 1, 0.5)",
        [(n, json.dumps(c), a) for n, c, a in PATTERNS])
    conn.commit()
    conn.close()
    return path


@pytest.fixture
def lib(db_path):
    loader = LibraryLoader(str(db_path))
    yield loader
    loader.close()


def test_missing_database_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        LibraryLoader(str(tmp_path / "absent.db"))


def test_entities_by_mentions(lib):
    ents = lib.get_all_entities()
    assert [e.canonical_name for e in ents] == ["Zeus", "Apollo", "Odin", "Hera"]
    assert ents[0] == Entity(1, "Zeus", "deity", "x", 5, 1, 1)


def test_aliases_grouped_by_canonical_name(lib):
    aliases = lib.get_entity_aliases()
    assert {k: sorted(v) for k, v in aliases.items()} == {
        "Zeus": ["Dias", "Jove"], "Odin": ["Woden"]}


def test_cooccurrence_counts_distinct_segments(lib):
    # Zeus is mentioned twice in t1:s1, which still counts as one segment.
    assert lib.get_entity_cooccurrence("Zeus", "Apollo") == 2
    assert lib.get_entity_cooccurrence("Apollo", "Zeus") == 2
    assert lib.get_entity_cooccurrence("Odin", "Zeus") == 1
    assert lib.get_entity_cooccurrence("Apollo", "Odin") == 0
    assert lib.get_entity_cooccurrence("Hera", "Nobody") == 0


def test_all_cooccurrences_and_threshold(lib):
    assert lib.get_all_cooccurrences() == [
        CooccurrencePair("Zeus", "Apollo", 2, 1),
        CooccurrencePair("Zeus", "Odin", 1, 1),
    ]
    assert lib.get_all_cooccurrences(min_count=2) == [
        CooccurrencePair("Zeus", "Apollo", 2, 1)]


def test_motif_queries_apply_confidence_floor(lib):
    assert lib.get_all_motif_codes() == ["A1", "F81"]
    assert sorted(lib.get_motif_entities("A1")) == ["Apollo", "Odin", "Zeus"]
    assert sorted(lib.get_motif_entities("F81")) == ["Apollo", "Zeus"]
    assert lib.get_motif_entities("K0") == []
    assert lib.get_segment_motifs("t1:s2") == [
        {"motif_code": "F81", "confidence": 0.3}]
    assert lib.get_segment_motifs("t2:s1") == [
        {"motif_code": "A1", "confidence": 0.5}]


def test_counts_and_summary(lib):
    assert lib.get_segment_count() == 3
    assert lib.summary() == {
        "entities": 4, "entity_mentions": 7, "segments": 3,
        "motifs": 3, "motif_tags": 5,
        "traditions": 3,          # counts every text, usable or not
    }


def test_entity_traditions(lib):
    assert sorted(lib.get_entity_traditions("Zeus")) == ["greek", "norse"]
    assert lib.get_entity_traditions("Apollo") == ["greek"]
    assert lib.get_entity_traditions("Hera") == []


def test_texts_only_usable_sorted_by_tradition(lib):
    assert lib.get_all_texts() == [
        {"text_id": "t1", "title": "Theogony", "tradition": "greek",
         "author": "Hesiod", "material_type": "Epic", "word_count": 100},
        {"text_id": "t2", "title": "Voluspa", "tradition": "norse",
         "author": "Anon", "material_type": "Poem", "word_count": 50},
    ]
    assert lib.get_segments_per_text() == {"t1": 2, "t2": 1}


def test_text_segments_in_narrative_order(lib):
    segs = lib.get_text_segments_ordered("t1")
    assert [(s["segment_id"], s["label"], s["ordinal"], s["word_count"])
            for s in segs] == [("t1:s1", "Book One", 1, 60),
                               ("t1:s2", "Book Two", 2, 40)]
    assert sorted(segs[0]["entity_names"]) == ["Apollo", "Zeus"]   # deduplicated
    assert segs[0]["motif_codes"] == ["A1"]
    assert segs[1]["motif_codes"] == ["F81"]                        # 0.29 dropped
    assert lib.get_text_segments_ordered("t3") == []
    assert lib.get_text_segments_ordered("missing") == []


def test_segment_entities_distinct(lib):
    assert sorted(lib.get_segment_entities("t1:s1")) == ["Apollo", "Zeus"]
    assert lib.get_segment_entities("t9:s9") == []


def test_patterns(lib):
    pats = lib.get_all_patterns()
    assert [p["pattern_name"] for p in pats] == ["common_pattern", "rare_pattern"]
    assert pats[0]["motif_codes"] == ["A1", "A600"]                 # decoded JSON
    assert set(pats[0]) == {"pattern_name", "description", "motif_codes",
                            "attestation_count", "tradition_count", "confidence"}
    assert lib.get_pattern_motif_codes("rare_pattern") == ["F81"]
    assert lib.get_pattern_motif_codes("missing") == []
    assert lib.get_entities_for_motif_codes([]) == []
    assert sorted(lib.get_entities_for_motif_codes(["F81", "K0"])) == [
        "Apollo", "Zeus"]


# ---------------------------------------------------------------------------
# MiroGlyphLoader
# ---------------------------------------------------------------------------

def _node(arc, cond, title):
    return {
        "node_id": f"{arc}{cond}",
        "arc": {"code": arc, "name_primary": f"{arc}-primary",
                "name_secondary": f"{arc}-secondary"},
        "condition": {"code": cond, "name_primary": f"c{cond}",
                      "name_secondary": f"c{cond}-secondary"},
        "title": title,
        "role": f"role of {arc}{cond}",
        "tone": ["Quiet"],
    }


TINY_SPEC = {
    "nodes": [_node("R", 1, "Mirror One"), _node("D", 4, "Shadow Four"),
              _node("D", 1, "Shadow One"), _node("E", 4, "Emergence Four")],
    "nontion": {"node_id": "N"},
    "structural_relationships": {
        "polarity_pairs": {"pairs": [
            {"condition_pair": [1, 4]},
            {"condition_pair": [2]},            # malformed: skipped
        ]},
        "condition_resonance": {"groups": [
            {"condition": 1, "nodes": ["D1", "R1"]},
            {"condition": 4, "nodes": ["D4", "E4"]},
        ]},
    },
}


@pytest.fixture(params=["wrapped", "bare"])
def miro(request, tmp_path):
    data = TINY_SPEC
    if request.param == "wrapped":
        data = {"miroglyph_v4_technical_specification": TINY_SPEC}
    path = tmp_path / "spec.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return MiroGlyphLoader(str(path))


def test_miro_missing_spec_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        MiroGlyphLoader(str(tmp_path / "absent.json"))


def test_miro_nodes_parsed(miro):
    assert miro.get_node("D1") == MiroNode(
        "D1", "D", "D-primary", "D-secondary", 1, "c1", "c1-secondary",
        "Shadow One", "role of D1", ["Quiet"])
    assert miro.get_node("X9") is None
    assert miro.get_all_node_ids() == ["D1", "D4", "E4", "R1"]
    assert sorted(n.node_id for n in miro.get_arc_nodes("D")) == ["D1", "D4"]
    assert sorted(n.node_id for n in miro.get_condition_nodes(4)) == ["D4", "E4"]


def test_miro_relationships(miro):
    assert miro.polarity_pairs == [(1, 4)]
    assert miro.get_polarity_partner("D1") == "D4"
    assert miro.get_polarity_partner("E4") == "E1"
    assert miro.get_polarity_partner("X9") is None
    assert miro.get_resonance_group("R1") == ["D1", "R1"]
    assert miro.get_resonance_group("X9") == []


def test_miro_summary(miro):
    assert miro.summary() == {
        "nodes": 4, "arcs": 3, "conditions": 2, "polarity_pairs": 1,
        "resonance_groups": 2, "has_nontion": True,
    }


def test_tracked_spec_loads_full_grid():
    """The spec v2_run reads parses into the 3 x 6 grid the tests assume."""
    miro = MiroGlyphLoader(str(ROOT / "miroglyph" / "miroglyph_v4_technical_spec.json"))
    assert miro.summary() == {
        "nodes": 18, "arcs": 3, "conditions": 6, "polarity_pairs": 3,
        "resonance_groups": 6, "has_nontion": True,
    }
    assert miro.get_all_node_ids() == [
        f"{a}{c}" for a in ("D", "E", "R") for c in range(1, 7)]
    assert [miro.get_polarity_partner(f"D{c}") for c in range(1, 7)] == [
        "D4", "D5", "D6", "D1", "D2", "D3"]
    assert miro.get_resonance_group("R3") == ["D3", "R3", "E3"]
