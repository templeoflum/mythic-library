"""Fixture tests for scripts/normalize/select_best.py.

select_best.py picks which normalized version of each text goes on to
segmentation. It writes {text_id}_best.txt and sources/best_versions.json,
which create_db.py reads to set `usable`. These tests pin how it scores
and picks today, on a tiny texts/ tree under tmp_path. They test the
current behaviour; they do not change it.
"""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "select_best_under_test", ROOT / "scripts" / "normalize" / "select_best.py")
sb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sb)


# ---------------------------------------------------------------------------
# score_version
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("meta, expected", [
    ({"source_format": "gutenberg", "word_count": 10}, (5, 10)),
    ({"source_format": "sacred-texts", "word_count": 7}, (2, 7)),
    ({"source_format": "etcsl"}, (2, 0)),
    ({"source_format": "something-new", "word_count": 3}, (1, 3)),
    ({"word_count": 4}, (2, 4)),                       # missing format counts as "other"
    ({"source_format": "pdf", "extraction_quality": "good", "word_count": 1}, (3.0, 1)),
    ({"source_format": "pdf", "extraction_quality": "fair", "word_count": 1},
     (3 * 0.7, 1)),
    ({"source_format": "pdf", "extraction_quality": "poor", "word_count": 1},
     (3 * 0.1, 1)),
    ({"source_format": "pdf", "extraction_quality": "failed", "word_count": 1}, (0.0, 1)),
    ({"source_format": "pdf", "word_count": 1}, (1.5, 1)),   # unknown quality: x0.5
])
def test_score_version(meta, expected):
    fmt, words = sb.score_version(meta)
    assert fmt == pytest.approx(expected[0])
    assert words == expected[1]


def test_format_outranks_length():
    """A short Gutenberg file beats a much longer good PDF: format is compared first."""
    short_gutenberg = sb.score_version({"source_format": "gutenberg", "word_count": 50})
    long_pdf = sb.score_version({"source_format": "pdf", "extraction_quality": "good",
                                 "word_count": 100_000})
    assert short_gutenberg > long_pdf


# ---------------------------------------------------------------------------
# Fixture tree
# ---------------------------------------------------------------------------

def _version(norm_dir: Path, stem: str, meta: dict, body: str = "text",
             with_txt: bool = True):
    norm_dir.mkdir(parents=True, exist_ok=True)
    (norm_dir / f"{stem}_metadata.json").write_text(json.dumps(meta), encoding="utf-8")
    if with_txt:
        (norm_dir / f"{stem}.txt").write_text(body, encoding="utf-8")


@pytest.fixture
def tree(tmp_path, monkeypatch):
    texts = tmp_path / "texts"
    sources = tmp_path / "sources"
    sources.mkdir()

    # Two versions: Gutenberg wins on format although the PDF is longer.
    norm = texts / "greek" / "t-two" / "normalized"
    _version(norm, "a_pdf", {"source_format": "pdf", "extraction_quality": "good",
                             "word_count": 900, "original_file": "a.pdf"}, "PDF BODY")
    _version(norm, "b_gut", {"source_format": "gutenberg", "word_count": 100,
                             "original_file": "b.txt"}, "GUTENBERG BODY")

    # Same format: the longer one wins.
    norm = texts / "greek" / "t-length" / "normalized"
    _version(norm, "short", {"source_format": "sacred-texts", "word_count": 10}, "SHORT")
    _version(norm, "long", {"source_format": "sacred-texts", "word_count": 20}, "LONG")

    # Exact tie: the first metadata file by name wins (stable sort).
    norm = texts / "norse" / "t-tie" / "normalized"
    _version(norm, "x_first", {"source_format": "etcsl", "word_count": 5}, "FIRST")
    _version(norm, "y_second", {"source_format": "etcsl", "word_count": 5}, "SECOND")

    # Only unusable versions: broken JSON, and metadata with no .txt beside it.
    norm = texts / "norse" / "t-broken" / "normalized"
    norm.mkdir(parents=True)
    (norm / "bad_metadata.json").write_text("{not json", encoding="utf-8")
    _version(norm, "orphan", {"source_format": "gutenberg", "word_count": 1},
             with_txt=False)

    # No normalized folder at all.
    (texts / "norse" / "t-empty").mkdir(parents=True)

    # Stray files at tradition and text level are ignored.
    (texts / "README.txt").write_text("not a tradition", encoding="utf-8")
    (texts / "greek" / "notes.txt").write_text("not a text", encoding="utf-8")

    monkeypatch.setattr(sb, "TEXTS_DIR", texts)
    monkeypatch.setattr(sb, "SOURCES_DIR", sources)
    monkeypatch.setattr(sb, "OUTPUT_FILE", sources / "best_versions.json")
    return tmp_path


# ---------------------------------------------------------------------------
# find_normalized_versions
# ---------------------------------------------------------------------------

def test_find_versions_pairs_metadata_with_text(tree):
    versions = sb.find_normalized_versions(tree / "texts" / "greek" / "t-two")
    assert [Path(v["_norm_path"]).name for v in versions] == ["a_pdf.txt", "b_gut.txt"]
    assert Path(versions[0]["_meta_path"]).name == "a_pdf_metadata.json"
    assert versions[1]["source_format"] == "gutenberg"


def test_find_versions_skips_broken_and_orphaned(tree):
    assert sb.find_normalized_versions(tree / "texts" / "norse" / "t-broken") == []
    assert sb.find_normalized_versions(tree / "texts" / "norse" / "t-empty") == []


# ---------------------------------------------------------------------------
# run_selection
# ---------------------------------------------------------------------------

def test_selection_summary_and_statuses(tree):
    out = sb.run_selection()
    assert out["summary"] == {"texts_processed": 5, "texts_with_content": 3,
                              "texts_without_content": 2}
    best = out["best_versions"]
    # Traditions in name order, then texts in name order.
    assert list(best) == ["t-length", "t-two", "t-broken", "t-empty", "t-tie"]
    for tid in ("t-broken", "t-empty"):
        assert best[tid] == {"text_id": tid, "tradition": "norse",
                             "status": "no_normalized_content", "versions_found": 0}


def test_selection_picks_and_copies_best(tree):
    best = sb.run_selection()["best_versions"]
    norm = tree / "texts" / "greek" / "t-two" / "normalized"

    two = best["t-two"]
    assert two == {
        "text_id": "t-two",
        "tradition": "greek",
        "status": "selected",
        "best_file": str(norm / "t-two_best.txt"),     # absolute path, as written today
        "source_file": "b.txt",
        "source_format": "gutenberg",
        "word_count": 100,
        "versions_found": 2,
        "selection_reason": "format=gutenberg, words=100",
    }
    assert (norm / "t-two_best.txt").read_text(encoding="utf-8") == "GUTENBERG BODY"

    length_dir = tree / "texts" / "greek" / "t-length" / "normalized"
    assert best["t-length"]["word_count"] == 20
    assert best["t-length"]["source_file"] == ""        # no original_file in metadata
    assert (length_dir / "t-length_best.txt").read_text(encoding="utf-8") == "LONG"

    tie_dir = tree / "texts" / "norse" / "t-tie" / "normalized"
    assert (tie_dir / "t-tie_best.txt").read_text(encoding="utf-8") == "FIRST"


def test_output_file_matches_return_value(tree):
    out = sb.run_selection()
    written = json.loads((tree / "sources" / "best_versions.json").read_text(encoding="utf-8"))
    assert written == out
    assert set(written) == {"summary", "best_versions"}


def test_rerun_is_stable(tree):
    """A second run sees the same versions (the _best.txt copy has no metadata) and
    writes the same file."""
    sb.run_selection()
    first = (tree / "sources" / "best_versions.json").read_bytes()
    sb.run_selection()
    assert (tree / "sources" / "best_versions.json").read_bytes() == first
