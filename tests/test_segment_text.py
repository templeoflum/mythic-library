#!/usr/bin/env python3
"""Fixture tests for scripts/segment/segment_text.py.

Small hand-made texts only; process_text runs on a text folder under
tmp_path. Expected values are worked out by hand from the script's own
rules, so these pin what segmentation does today.
"""

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "segment" / "segment_text.py"


@pytest.fixture(scope="module")
def seg():
    spec = importlib.util.spec_from_file_location("segment_text_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PREAMBLE = " ".join(["word"] * 60)  # over the 50-word preamble threshold

EPIC = "\n".join([
    PREAMBLE,           # 0
    "",                 # 1
    "BOOK I",           # 2
    "Sing, goddess.",   # 3
    "",                 # 4
    "BOOK II.",         # 5
    "More song.",       # 6
    "CHAPTER 3",        # 7
    "The end.",         # 8
])


def test_slugify(seg):
    assert seg.slugify("Book I: The Wrath!") == "book-i-the-wrath"
    assert seg.slugify("  Hymn  to   Demeter  ") == "hymn-to-demeter"
    assert seg.slugify("x" * 50) == "x" * 40


@pytest.mark.parametrize("line,expected", [
    ("BOOK I", ("book", "I")),
    ("Book the First.", ("book", "First")),
    ("THE FIRST TABLET", ("tablet", "THE FIRST TABLET")),
    ("CANTO XII", ("canto", "CANTO XII")),
    ("RUNE 3", ("rune", "RUNE 3")),
    ("HYMN TO DEMETER", ("hymn", "HYMN TO DEMETER")),
    ("CHAPTER THE FIRST", ("chapter", "CHAPTER THE FIRST")),
    ("PART TWO", ("part", "PART TWO")),
    ("THE STORY OF THE FLOOD", ("tale", "THE STORY OF THE FLOOD")),
    ("1-5", ("line_range", "1-5")),
    ("IV.", ("section", "IV")),
])
def test_detects_each_division_type(seg, line, expected):
    assert seg.detect_divisions(line) == [(0, *expected)]


def test_ignores_plain_and_long_lines(seg):
    text = "\n".join([
        "Just a sentence about a book.",
        "CHAPTER I " + "x" * 100,  # over 100 characters: not a header
        "",
    ])
    assert seg.detect_divisions(text) == []


def test_detect_divisions_on_epic(seg):
    assert seg.detect_divisions(EPIC) == [
        (2, "book", "I"),
        (5, "book", "II"),
        (7, "chapter", "CHAPTER 3"),
    ]


def test_segment_by_divisions_keeps_long_preamble(seg):
    segments = seg.segment_by_divisions(EPIC, seg.detect_divisions(EPIC))
    assert [(s["label"], s["segment_type"], s["start_line"], s["end_line"]) for s in segments] == [
        ("preamble", "preamble", 0, 1),
        ("I", "book", 2, 4),
        ("II", "book", 5, 6),
        ("CHAPTER 3", "chapter", 7, 8),
    ]
    assert segments[1]["content"] == "BOOK I\nSing, goddess."


def test_segment_by_divisions_drops_short_preamble(seg):
    text = "Short intro.\nBOOK I\nOne.\nBOOK II\nTwo."
    segments = seg.segment_by_divisions(text, seg.detect_divisions(text))
    assert [s["label"] for s in segments] == ["I", "II"]


def test_no_divisions_is_one_segment(seg):
    segments = seg.segment_by_divisions("a\nb", [])
    assert segments == [{"label": "full_text", "segment_type": "full",
                         "start_line": 0, "end_line": 1, "content": "a\nb"}]


def test_segment_by_blank_lines_groups_and_appends_tail(seg):
    text = "one two three\n\n\nfour five six\n\n\nseven"
    segments = seg.segment_by_blank_lines(text, min_segment_words=3)
    # each 3-word section closes a segment; the 1-word tail joins the last one
    assert [s["label"] for s in segments] == ["section_1", "section_2"]
    assert segments[0]["content"] == "one two three"
    assert segments[1]["content"] == "four five six\n\nseven"


def make_text(tmp_path, text_id, content):
    text_dir = tmp_path / "greek" / text_id
    (text_dir / "normalized").mkdir(parents=True)
    (text_dir / "normalized" / f"{text_id}_best.txt").write_text(content, encoding="utf-8")
    return text_dir


def test_process_text_structural(seg, tmp_path):
    body = " ".join(["verse"] * 40)
    content = f"{PREAMBLE}\n\nBOOK I\n{body}\n\nBOOK II\n{body}\n"
    text_dir = make_text(tmp_path, "tiny-epic", content)

    result = seg.process_text(text_dir, "tiny-epic", "greek")
    assert result["status"] == "segmented"
    assert result["strategy"] == "structural"
    assert result["segment_count"] == 3

    index = json.loads((text_dir / "segments" / "segments.json").read_text(encoding="utf-8"))
    assert [(s["id"], s["label"], s["file"], s["word_count"]) for s in index["segments"]] == [
        ("seg_001", "preamble", "seg_001_preamble.txt", 60),
        ("seg_002", "I", "seg_002_i.txt", 42),
        ("seg_003", "II", "seg_003_ii.txt", 42),
    ]
    assert (text_dir / "segments" / "seg_002_i.txt").read_text(encoding="utf-8").startswith("BOOK I\n")


def test_process_text_short_and_too_short(seg, tmp_path):
    short = make_text(tmp_path, "short", " ".join(["word"] * 150))
    result = seg.process_text(short, "short", "greek")
    assert result["strategy"] == "single"
    assert result["segment_count"] == 1

    tiny = make_text(tmp_path, "tiny", "only a few words")
    assert seg.process_text(tiny, "tiny", "greek") == {"status": "too_short", "text_id": "tiny"}


def test_process_text_is_deterministic(seg, tmp_path):
    body = " ".join(["verse"] * 60)  # 120+ words in all, over the 100-word minimum
    text_dir = make_text(tmp_path, "again", f"BOOK I\n{body}\nBOOK II\n{body}\n")

    def snapshot():
        return {p.name: p.read_bytes() for p in sorted((text_dir / "segments").iterdir())}

    seg.process_text(text_dir, "again", "greek")
    first = snapshot()
    seg.process_text(text_dir, "again", "greek")
    assert snapshot() == first


def test_rerun_clears_old_segment_files(seg, tmp_path):
    body = " ".join(["verse"] * 60)
    text_dir = make_text(tmp_path, "shrinks", f"BOOK I\n{body}\nBOOK II\n{body}\nBOOK III\n{body}\n")
    seg.process_text(text_dir, "shrinks", "greek")
    seg_dir = text_dir / "segments"
    (seg_dir / "notes.md").write_text("not a segment file", encoding="utf-8")
    assert sorted(p.name for p in seg_dir.glob("seg_*.txt")) == [
        "seg_001_i.txt", "seg_002_ii.txt", "seg_003_iii.txt"]

    # second run: one fewer book, and the labels change
    (text_dir / "normalized" / "shrinks_best.txt").write_text(
        f"CANTO I\n{body}\nCANTO II\n{body}\n", encoding="utf-8")
    seg.process_text(text_dir, "shrinks", "greek")
    assert sorted(p.name for p in seg_dir.glob("seg_*.txt")) == [
        "seg_001_canto-i.txt", "seg_002_canto-ii.txt"]
    assert (seg_dir / "notes.md").exists()
    index = json.loads((seg_dir / "segments.json").read_text(encoding="utf-8"))
    assert [s["file"] for s in index["segments"]] == ["seg_001_canto-i.txt", "seg_002_canto-ii.txt"]


def test_source_file_is_relative_to_repo_root(seg, tmp_path, monkeypatch):
    monkeypatch.setattr(seg, "PROJECT_ROOT", tmp_path)
    text_dir = make_text(tmp_path, "rel", " ".join(["word"] * 150))
    seg.process_text(text_dir, "rel", "greek")
    index = json.loads((text_dir / "segments" / "segments.json").read_text(encoding="utf-8"))
    assert index["source_file"] == "greek/rel/normalized/rel_best.txt"


def test_repo_relative_outside_root_stays_absolute(seg, tmp_path, monkeypatch):
    monkeypatch.setattr(seg, "PROJECT_ROOT", tmp_path / "repo")
    outside = tmp_path / "elsewhere" / "x.txt"
    assert seg.repo_relative(outside) == str(outside)
