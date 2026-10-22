#!/usr/bin/env python3
"""Tests for the Gutenberg Title/Author header check in scripts/bulk_download.py.

Small fixture files only; nothing here downloads or reads the real corpus.
"""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "bulk_download.py"


@pytest.fixture(scope="module")
def bd():
    spec = importlib.util.spec_from_file_location("bulk_download", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def gutenberg_file(tmp_path, title, author, name="pg1.txt"):
    lines = ["﻿The Project Gutenberg eBook of " + (title or "a book"), ""]
    if title is not None:
        lines += [f"Title: {title}", ""]
    if author is not None:
        lines += [f"Author: {author}", ""]
    lines += ["Release date: January 1, 2000 [eBook #1]", "",
              "*** START OF THE PROJECT GUTENBERG EBOOK ***", ""]
    lines += ["Once upon a time there was a story. " * 40]
    path = tmp_path / name
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


CATALOG = {
    "eskimo-folk-tales": {"title": "Eskimo Folk-Tales", "author": "Knud Rasmussen"},
    "anansi-tales": {"title": "Anansi Tales", "author": "Oral tradition"},
    "the-mabinogion": {"title": "The Mabinogion", "author": "Anonymous"},
    "theogony": {"title": "Theogony", "author": "Hesiod"},
    "jātaka-tales": {"title": "Jātaka Tales", "author": "Anonymous"},
}


def expected(bd, text_id, source=None):
    return bd.expected_identity(text_id, {}, CATALOG, source)


def test_matching_header_passes(bd, tmp_path):
    path = gutenberg_file(tmp_path, "Eskimo Folk-Tales", "Knud Rasmussen")
    result = bd.validate_download(path, "eskimo-folk-tales", expected(bd, "eskimo-folk-tales"))
    assert result["checks"]["header_matches_catalog"] is True
    assert result["valid"] is True


def test_wrong_book_fails(bd, tmp_path):
    path = gutenberg_file(tmp_path, "Journal des Goncourt", "Edmond de Goncourt")
    result = bd.validate_download(path, "eskimo-folk-tales", expected(bd, "eskimo-folk-tales"))
    assert result["checks"]["header_matches_catalog"] is False
    assert result["valid"] is False
    assert "Wrong book" in result["error"]


def test_wrong_book_fails_when_catalog_has_no_author(bd, tmp_path):
    path = gutenberg_file(tmp_path, "The History of Sulu", "Najeeb M. Saleeby")
    result = bd.validate_download(path, "anansi-tales", expected(bd, "anansi-tales"))
    assert result["valid"] is False


def test_author_match_is_enough(bd, tmp_path):
    path = gutenberg_file(tmp_path, "Hesiod, The Homeric Hymns, and Homerica", "Homer and Hesiod")
    result = bd.validate_download(path, "theogony", expected(bd, "theogony"))
    assert result["checks"]["header_matches_catalog"] is True


def test_translator_counts_as_author(bd, tmp_path):
    path = gutenberg_file(tmp_path, "Something Else Entirely", "Lady Charlotte Guest")
    source = {"translator": "Lady Charlotte Guest"}
    result = bd.validate_download(path, "the-mabinogion", expected(bd, "the-mabinogion", source))
    assert result["checks"]["header_matches_catalog"] is True


def test_accents_are_folded(bd, tmp_path):
    path = gutenberg_file(tmp_path, "Jataka tales", "Ellen C. Babbitt")
    result = bd.validate_download(path, "jātaka-tales", expected(bd, "jātaka-tales"))
    assert result["checks"]["header_matches_catalog"] is True


def test_shared_common_word_is_not_a_match(bd, tmp_path):
    # "Folk-Tales" alone must not make a different book look right
    path = gutenberg_file(tmp_path, "Russian Folk-Tales", "Someone Else")
    result = bd.validate_download(path, "eskimo-folk-tales", expected(bd, "eskimo-folk-tales"))
    assert result["checks"]["header_matches_catalog"] is False


def test_no_header_is_skipped(bd, tmp_path):
    path = tmp_path / "plain.txt"
    path.write_text("A plain text with no Gutenberg header. " * 40, encoding="utf-8")
    result = bd.validate_download(path, "eskimo-folk-tales", expected(bd, "eskimo-folk-tales"))
    assert "header_matches_catalog" not in result["checks"]
    assert result["valid"] is True


def test_title_in_another_script_is_a_warning(bd, tmp_path):
    path = gutenberg_file(tmp_path, "山海經", "Anonymous")
    result = bd.validate_download(path, "eskimo-folk-tales", expected(bd, "eskimo-folk-tales"))
    assert "header_matches_catalog" not in result["checks"]
    assert any("Could not compare" in w for w in result["warnings"])


def test_without_expected_nothing_changes(bd, tmp_path):
    path = gutenberg_file(tmp_path, "Journal des Goncourt", "Edmond de Goncourt")
    result = bd.validate_download(path, "eskimo-folk-tales")
    assert "header_matches_catalog" not in result["checks"]
    assert result["valid"] is True
