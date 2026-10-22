#!/usr/bin/env python3
"""Fixture tests for scripts/normalize/normalize_text.py.

Small hand-made inputs only; nothing here reads the real corpus. Expected
values are worked out by hand from the script's own rules, so these pin
what normalization does today.
"""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "normalize" / "normalize_text.py"


@pytest.fixture(scope="module")
def nt():
    spec = importlib.util.spec_from_file_location("normalize_text_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GUTENBERG = (
    "﻿The Project Gutenberg eBook of Tales of Old\r\n\r\n"
    "Title: Tales of Old\r\n\r\n"
    "Author: Some One\r\n\r\n"
    "Translator: Another Person\r\n\r\n"
    "Release date: May 1, 2001 [eBook #123]\r\n\r\n"
    "Language: English\r\n\r\n"
    "Credits: Volunteers\r\n\r\n"
    "*** START OF THE PROJECT GUTENBERG EBOOK TALES OF OLD ***\r\n\r\n"
    "First line.  \r\n"
    "[Illustration: a cat]\r\n\r\n\r\n\r\n\r\n"
    "Second line.\r\n"
    "*** END OF THE PROJECT GUTENBERG EBOOK TALES OF OLD ***\r\n"
    "License text that must not appear.\r\n"
)


# ---------------------------------------------------------------- reading

def test_read_text_file_strips_bom(nt, tmp_path):
    path = tmp_path / "bom.txt"
    path.write_bytes("﻿hello".encode("utf-8"))
    assert nt.read_text_file(path) == "hello"


def test_read_text_file_falls_back_to_latin1(nt, tmp_path):
    path = tmp_path / "latin1.txt"
    path.write_bytes("café".encode("latin-1"))
    assert nt.read_text_file(path) == "café"


# ---------------------------------------------------------------- gutenberg

def test_normalize_gutenberg_body(nt):
    body, _ = nt.normalize_gutenberg(GUTENBERG, "tales")
    # markers and licence dropped, illustration removed, CRLF -> LF,
    # 6 newlines collapsed to 3, trailing spaces stripped
    assert body == "First line.\n\n\nSecond line."


def test_normalize_gutenberg_metadata(nt):
    _, meta = nt.normalize_gutenberg(GUTENBERG, "tales")
    assert meta == {
        "title": "Tales of Old",
        "author": "Some One",
        "translator": "Another Person",
        "language": "English",
        "release_date": "May 1, 2001",
        "ebook_id": "123",
        "source_format": "gutenberg",
        "original_file": "",
        "text_id": "tales",
    }


def test_normalize_gutenberg_without_markers_keeps_everything(nt):
    body, meta = nt.normalize_gutenberg("Just text.\n\n\n\n\nMore.", "plain")
    assert body == "Just text.\n\n\nMore."
    assert "title" not in meta


def test_parse_gutenberg_metadata_multiline_title(nt):
    meta = nt.parse_gutenberg_metadata("Title: The Long\n       Title Here\n\nAuthor: A. B.\n\n")
    assert meta["title"] == "The Long\n       Title Here"
    assert meta["author"] == "A. B."


# ---------------------------------------------------------------- sacred texts

def test_normalize_sacred_texts(nt):
    content = "\n".join([
        "Source: https://sacred-texts.com/x/index.htm",
        "Downloaded: 2026-01-01",
        "Corpus: test",
        "=====",
        "Sacred-Texts",
        "Next: Chapter 2",
        "[p. 42]",
        "The real line.   ",
        "Contents",
        "Another real line.",
    ])
    body, meta = nt.normalize_sacred_texts(content, "st")
    assert body == "The real line.\nAnother real line."
    assert meta == {
        "source_format": "sacred-texts",
        "text_id": "st",
        "source_url": "https://sacred-texts.com/x/index.htm",
        "download_date": "2026-01-01",
        "corpus": "test",
        "index_only": True,  # under 200 lines and under 500 words
    }


def test_normalize_sacred_texts_long_is_not_index_only(nt):
    content = "=====\n" + "\n".join(["word " * 10] * 60)
    _, meta = nt.normalize_sacred_texts(content, "st")
    assert "index_only" not in meta


# ---------------------------------------------------------------- etcsl

def test_fix_word_joining(nt):
    assert nt.fix_word_joining("from the greatheaven she descendedto the greatbelow") == \
        "from the great heaven she descended to the great below"
    # camelCase transitions get a space
    assert nt.fix_word_joining("SumerianLiterature") == "Sumerian Literature"
    assert nt.fix_word_joining("McDonald") == "Mc Donald"


def test_normalize_etcsl_skips_navigation_before_first_line_range(nt):
    content = "\n".join([
        "Source: https://etcsl.orinst.ox.ac.uk/x",
        "Corpus: ETCSL",
        "=====",
        "Catalogues:",
        "by date",
        "1-5",
        "From the greatheaven she set her mind.",
    ])
    body, meta = nt.normalize_etcsl(content, "inanna")
    assert body == "1-5\nFrom the great heaven she set her mind."
    assert meta["source_url"] == "https://etcsl.orinst.ox.ac.uk/x"
    assert meta["corpus"] == "ETCSL"


def test_normalize_etcsl_filters_navigation_without_line_ranges(nt):
    content = "=====\nCatalogues:\nby date\nA line of text.\nlinks\n"
    body, _ = nt.normalize_etcsl(content, "x")
    assert body == "A line of text."


# ---------------------------------------------------------------- generic

def test_normalize_generic(nt):
    body, meta = nt.normalize_generic("﻿a  \r\nb\r\n\r\n\r\n\r\n\r\nc\n", "g")
    assert body == "a\nb\n\n\nc"
    assert meta == {"source_format": "other", "text_id": "g"}


# ---------------------------------------------------------------- format detection

@pytest.mark.parametrize("name,content,expected", [
    ("pg123_gutenberg.txt", "", "gutenberg"),
    ("x.txt", "Header\nThe Project Gutenberg eBook of X", "gutenberg"),
    ("sacred-texts_index.txt", "", "sacred-texts"),
    ("x.txt", "Source: https://sacred-texts.com/abc", "sacred-texts"),
    ("etcsl_c141.txt", "", "etcsl"),
    ("x.txt", "Electronic Text Corpus of Sumerian Literature", "etcsl"),
    ("archive.txt", "Some scanned book.", "other"),
])
def test_detect_source_format(nt, name, content, expected):
    assert nt.detect_source_format(Path(name), content) == expected
