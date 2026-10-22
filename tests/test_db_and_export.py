"""Fixture tests for scripts/database/create_db.py and scripts/export_explorer_data.py.

A tiny corpus (three texts, three segments, three entities, three motifs)
is built under tmp_path. The tests check that the database build and the
explorer catalogs are deterministic, and pin the catalog shape. Every
expected value below is worked out by hand from the fixture.
"""

import csv
import importlib.util
import json
import sqlite3
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


create_db = _load("create_db_under_test", "scripts/database/create_db.py")
export = _load("export_explorer_under_test", "scripts/export_explorer_data.py")

from integration.entity_mapper import EntityMapping  # noqa: E402  (path set by export)
from integration.library_loader import LibraryLoader  # noqa: E402


# ---------------------------------------------------------------------------
# Fixture corpus
# ---------------------------------------------------------------------------

def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _segment_dir(texts, tradition, text_id, segs):
    seg_dir = texts / tradition / text_id / "segments"
    seg_dir.mkdir(parents=True)
    index = []
    for seg_id, label, body in segs:
        name = f"{seg_id}_{label.lower().replace(' ', '-')}.txt"
        (seg_dir / name).write_text(body, encoding="utf-8")
        index.append({"id": seg_id, "label": label, "segment_type": "book",
                      "file": name, "word_count": len(body.split())})
    _write_json(seg_dir / "segments.json",
                {"text_id": text_id, "tradition": tradition, "segments": index})


def _mention(name, offset):
    return {"entity_name": name, "matched_text": name,
            "sentence_context": f"... {name} ...", "char_offset": offset}


def build_fixture(base: Path):
    sources, texts, data = base / "sources", base / "texts", base / "data"
    sources.mkdir(parents=True)
    data.mkdir(parents=True)

    with open(sources / "master_catalog.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["text_id", "title", "author", "tradition", "origin_raw",
                    "date_composed", "material_type", "status", "notes"])
        w.writerow(["t-greek", "Greek Text", "Anon", "greek", "Greece",
                    "c. 700 BCE", "Epic", "pending", ""])
        w.writerow(["t-norse", "Norse Text", "Anon", "norse", "Iceland",
                    "c. 1220", "Prose", "pending", ""])
        w.writerow(["t-unused", "Unused Text", "Anon", "egyptian", "Egypt",
                    "", "Hymn", "pending", ""])
    _write_json(sources / "best_versions.json", {"best_versions": {
        "t-greek": {"status": "selected", "word_count": 120, "best_file": "g.txt"},
        "t-norse": {"status": "selected", "word_count": 80, "best_file": "n.txt"},
        "t-unused": {"status": "rejected", "word_count": 5, "best_file": ""},
    }})

    _segment_dir(texts, "greek", "t-greek", [
        ("seg_001", "Book One", "Zeus made the world from chaos. Zeus ruled."),
        ("seg_002", "Book Two", "Hades kept the dead below; Zeus sent a hero down."),
    ])
    _segment_dir(texts, "norse", "t-norse", [
        ("seg_001", "Voluspa", "Odin shaped the world. Odin watched it."),
    ])

    _write_json(data / "entity_catalog.json", {
        "Zeus": {"entity_type": "deity", "primary_tradition": "greek",
                 "total_mentions": 3, "text_count": 1, "tradition_count": 1},
        "Odin": {"entity_type": "deity", "primary_tradition": "norse",
                 "total_mentions": 2, "text_count": 1, "tradition_count": 1},
        "Hades": {"entity_type": "deity", "primary_tradition": "greek",
                  "total_mentions": 1, "text_count": 1, "tradition_count": 1},
    })
    _write_json(data / "entity_aliases.json", {"aliases": {
        "Zeus": ["Jove"],
        "Odin": ["Woden", "Wotan"],
        "Nobody": ["Ghost"],          # not in the catalog: skipped
    }})
    _write_json(data / "entities.json", [
        {"text_id": "t-greek", "status": "extracted", "segments": [
            {"segment_id": "seg_001",
             "mentions": [_mention("Zeus", 0), _mention("Zeus", 32),
                          _mention("Nobody", 40)]},       # unknown: skipped
            {"segment_id": "seg_002",
             "mentions": [_mention("Hades", 0), _mention("Zeus", 26)]},
        ]},
        {"text_id": "t-norse", "status": "extracted", "segments": [
            {"segment_id": "seg_001",
             "mentions": [_mention("Odin", 0), _mention("Odin", 22)]},
        ]},
        {"text_id": "t-unused", "status": "error", "segments": [
            {"segment_id": "seg_001", "mentions": [_mention("Zeus", 0)]},
        ]},
    ])

    _write_json(data / "thompson_motif_index.json", {"motifs": {
        "A1": {"label": "Creator", "category": "A", "keywords": ["made"]},
        "F81": {"label": "Descent to the dead", "parent": "F80",
                "category": "F", "keywords": ["dead"]},
        "K0": {"label": "Trickery", "category": "K", "keywords": []},
    }})
    _write_json(data / "motif_tags.json", [
        {"text_id": "t-greek", "status": "tagged", "segments": [
            {"segment_id": "seg_001",
             "tags": [{"code": "A1", "confidence": 0.6, "evidence": ["made"]}]},
            {"segment_id": "seg_002",
             "tags": [{"code": "F81", "confidence": 0.5, "evidence": ["dead"]},
                      {"code": "A1", "confidence": 0.2, "evidence": []}]},
        ]},
        {"text_id": "t-norse", "status": "tagged", "segments": [
            {"segment_id": "seg_001",
             "tags": [{"code": "A1", "confidence": 0.4, "evidence": ["shaped"]},
                      {"code": "K0", "confidence": 0.25, "evidence": []}]},
        ]},
        {"text_id": "t-unused", "status": "no_segments", "segments": [
            {"segment_id": "seg_001",
             "tags": [{"code": "K0", "confidence": 0.9, "evidence": []}]},
        ]},
    ])
    return sources, texts, data


def build_db(base: Path, monkeypatch) -> Path:
    """Run create_db.main's steps against the fixture under base."""
    sources, texts, data = build_fixture(base)
    db_path = data / "mythic_patterns.db"
    monkeypatch.setattr(create_db, "SOURCES_DIR", sources)
    monkeypatch.setattr(create_db, "TEXTS_DIR", texts)
    monkeypatch.setattr(create_db, "DATA_DIR", data)
    monkeypatch.setattr(create_db, "DB_PATH", db_path)

    conn = create_db.create_database(reset=True)
    create_db.import_texts(conn)
    create_db.import_segments(conn)
    create_db.import_entities(conn)
    create_db.import_motifs(conn)
    create_db.build_cross_cultural_patterns(conn)
    conn.close()
    return db_path


TABLES = ["texts", "segments", "segments_fts", "entities", "entity_aliases",
          "entity_mentions", "motifs", "motif_tags", "patterns",
          "pattern_attestations"]


def dump(db_path: Path) -> dict:
    conn = sqlite3.connect(str(db_path))
    try:
        return {t: conn.execute(f"SELECT * FROM {t} ORDER BY rowid").fetchall()
                for t in TABLES}
    finally:
        conn.close()


@pytest.fixture
def db(tmp_path, monkeypatch):
    return build_db(tmp_path / "a", monkeypatch)


# ---------------------------------------------------------------------------
# create_db.py
# ---------------------------------------------------------------------------

def test_build_is_deterministic(tmp_path, monkeypatch):
    first = dump(build_db(tmp_path / "a", monkeypatch))
    second = dump(build_db(tmp_path / "b", monkeypatch))
    assert first == second


def test_row_counts(db):
    counts = {t: len(rows) for t, rows in dump(db).items()}
    assert counts == {
        "texts": 3,
        "segments": 3,
        "segments_fts": 3,
        "entities": 3,
        "entity_aliases": 3,        # Nobody's alias is skipped
        "entity_mentions": 6,       # unknown entity and non-extracted text skipped
        "motifs": 3,
        "motif_tags": 5,            # all tags of tagged texts, any confidence
        "patterns": 18,             # every pattern definition, attested or not
        "pattern_attestations": 3,
    }


def test_texts_usable_follows_best_versions(db):
    conn = sqlite3.connect(str(db))
    rows = conn.execute(
        "SELECT text_id, tradition, word_count, best_file, usable "
        "FROM texts ORDER BY text_id").fetchall()
    conn.close()
    assert rows == [
        ("t-greek", "greek", 120, "g.txt", 1),
        ("t-norse", "norse", 80, "n.txt", 1),
        ("t-unused", "egyptian", 5, "", 0),
    ]


def test_segments_ids_ordinals_and_content(db):
    conn = sqlite3.connect(str(db))
    rows = conn.execute(
        "SELECT segment_id, text_id, label, ordinal, content "
        "FROM segments ORDER BY segment_id").fetchall()
    fts = conn.execute(
        "SELECT segment_id FROM segments_fts WHERE segments_fts MATCH 'Hades'"
    ).fetchall()
    conn.close()
    assert [r[:4] for r in rows] == [
        ("t-greek:seg_001", "t-greek", "Book One", 1),
        ("t-greek:seg_002", "t-greek", "Book Two", 2),
        ("t-norse:seg_001", "t-norse", "Voluspa", 1),
    ]
    assert rows[0][4].startswith("Zeus made the world")
    assert fts == [("t-greek:seg_002",)]


def test_patterns_from_tags_at_or_above_threshold(db):
    conn = sqlite3.connect(str(db))
    pats = {r[0]: r[1:] for r in conn.execute(
        "SELECT pattern_name, motif_codes, attestation_count, tradition_count, "
        "confidence FROM patterns")}
    atts = conn.execute(
        "SELECT p.pattern_name, a.text_id, a.tradition, a.confidence "
        "FROM pattern_attestations a JOIN patterns p USING (pattern_id) "
        "ORDER BY a.attestation_id").fetchall()
    conn.close()

    # A1 at 0.6 (greek) and 0.4 (norse); the 0.2 tag is under the 0.3 floor.
    assert pats["cosmogony_creation"][1:] == (2, 2, 0.5)
    assert json.loads(pats["cosmogony_creation"][0])[0] == "A1"
    assert pats["descent_to_underworld"][1:] == (1, 1, 0.5)
    # K0 at 0.25 is under the floor; the 0.9 tag belongs to an untagged text.
    assert pats["trickster"][1:] == (0, 0, 0.0)
    assert atts == [
        ("cosmogony_creation", "t-greek", "greek", 0.6),
        ("cosmogony_creation", "t-norse", "norse", 0.4),
        ("descent_to_underworld", "t-greek", "greek", 0.5),
    ]


# ---------------------------------------------------------------------------
# export_explorer_data.py
# ---------------------------------------------------------------------------

class StubACP:
    """Coordinates for one archetype; none for the other."""

    def get_coordinates(self, archetype_id):
        if archetype_id == "arc:sky-father":
            return np.array([0.123456, 1.0, -0.33333])
        return None


class StubMapper:
    MAPPINGS = {
        "Zeus": EntityMapping("Zeus", "arc:sky-father", "Sky Father", 0.9,
                              "exact", fidelity=0.8),
        "Hades": EntityMapping("Hades", "arc:unplaced", "Underworld King", 0.7,
                               "fuzzy"),
    }

    def get_mapping(self, name):
        return self.MAPPINGS.get(name)


def run_export(db_path: Path, out_dir: Path, monkeypatch):
    out_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(export, "OUTPUT_DIR", out_dir)
    library = LibraryLoader(str(db_path))
    try:
        export.export_entities_catalog(StubACP(), library, StubMapper())
        export.export_patterns_catalog(library)
    finally:
        library.close()
    return out_dir / "entities_catalog.json", out_dir / "patterns_catalog.json"


def test_export_is_deterministic(tmp_path, monkeypatch):
    db_a = build_db(tmp_path / "a", monkeypatch)
    db_b = build_db(tmp_path / "b", monkeypatch)
    first = run_export(db_a, tmp_path / "out1", monkeypatch)
    second = run_export(db_b, tmp_path / "out2", monkeypatch)
    for one, two in zip(first, second):
        assert one.read_bytes() == two.read_bytes()


def test_entities_catalog_shape(db, tmp_path, monkeypatch):
    path, _ = run_export(db, tmp_path / "out", monkeypatch)
    cat = json.loads(path.read_text(encoding="utf-8"))

    assert set(cat) == {"version", "total", "mapped", "unmapped", "entities"}
    assert (cat["version"], cat["total"], cat["mapped"], cat["unmapped"]) == \
        ("1.0", 3, 2, 1)
    # Mapped first by mentions descending, then unmapped.
    assert [e["name"] for e in cat["entities"]] == ["Zeus", "Hades", "Odin"]
    for e in cat["entities"]:
        assert set(e) == {"name", "type", "primary_tradition", "total_mentions",
                          "text_count", "tradition_count", "mapping",
                          "coordinates"}

    zeus, hades, odin = cat["entities"]
    assert zeus["mapping"] == {"archetype_id": "arc:sky-father",
                               "archetype_name": "Sky Father",
                               "confidence": 0.9, "method": "exact",
                               "fidelity": 0.8}
    assert zeus["coordinates"] == [0.1235, 1.0, -0.3333]
    assert hades["mapping"]["fidelity"] == 1.0
    assert hades["coordinates"] is None
    assert odin["mapping"] is None and odin["coordinates"] is None
    assert (odin["type"], odin["primary_tradition"], odin["total_mentions"]) == \
        ("deity", "norse", 2)


def test_patterns_catalog_shape(db, tmp_path, monkeypatch):
    _, path = run_export(db, tmp_path / "out", monkeypatch)
    cat = json.loads(path.read_text(encoding="utf-8"))

    assert set(cat) == {"version", "count", "arc_assignments", "patterns",
                        "motifs"}
    assert cat["version"] == "1.0"
    assert cat["count"] == len(cat["patterns"]) == 18
    assert set(cat["arc_assignments"]) == {"D", "R", "E"}
    for p in cat["patterns"]:
        assert set(p) == {"name", "description", "arc", "attestation_count",
                          "tradition_count", "confidence", "motif_codes",
                          "traditions", "related_entities"}
        assert p["arc"] in {"D", "R", "E"}

    # Most attested first.
    first, second = cat["patterns"][:2]
    assert first == {
        "name": "cosmogony_creation",
        "description": first["description"],
        "arc": "E",
        "attestation_count": 2,
        "tradition_count": 2,
        "confidence": 0.5,
        "motif_codes": ["A1", "A600", "A610", "A620", "A700", "A800"],
        "traditions": ["greek", "norse"],
        "related_entities": ["Odin", "Zeus"],
    }
    assert (second["name"], second["arc"], second["traditions"],
            second["related_entities"]) == \
        ("descent_to_underworld", "D", ["greek"], ["Hades", "Zeus"])
    assert all(p["attestation_count"] == 0 and p["related_entities"] == []
               for p in cat["patterns"][2:])

    assert cat["motifs"] == {
        "A1": {"label": "Creator", "category": "A"},
        "F81": {"label": "Descent to the dead", "category": "F"},
        "K0": {"label": "Trickery", "category": "K"},
    }
