#!/usr/bin/env python3
"""Build a lossless section index for the verified reading copies.

Run from any directory: python3 scripts/build_sections.py
Use --check to verify the committed manifest without writing it.

Source files are read as bytes and decoded without newline translation. Manifest
offsets are UTF-16 code units, exactly the indices used by JavaScript String.slice.
Only the manifest is written: Gutenberg notices, whitespace, variant stories,
footnotes, and every original source character remain in their original files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUTPUT = DIST / "sections.json"

# Edition specs stay outside the hosted book content. Each source is independently
# hash-pinned; whole-line anchors are rechecked on every build, never cached offsets.
SPECS = json.loads((ROOT / "scripts" / "edition_specs.json").read_text(encoding="utf-8"))["editions"]


def require(condition: bool, message: str) -> None:
    """Do not disable safety checks when Python is invoked with -O."""
    if not condition:
        raise ValueError(message)


def utf16_length(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


@dataclass(frozen=True)
class Boundary:
    start: int  # Python code-point offset, converted only when serializing.
    id: str
    label: str
    kind: str
    group: str | None = None


class Source:
    def __init__(self, book: dict):
        self.book = book
        self.spec = SPECS[book["id"]]
        self.path = DIST / book["path"]
        self.raw = self.path.read_bytes()
        self.sha256 = hashlib.sha256(self.raw).hexdigest()
        require(self.sha256 == self.spec["sha256"],
                f"{self.path.name}: source differs from the audited edition")
        require(self.sha256 == book["sha256"],
                f"{self.path.name}: source hash disagrees with catalog.json")
        require(len(self.raw) == book["bytes"],
                f"{self.path.name}: source byte count disagrees with catalog.json")
        self.text = self.raw.decode("utf-8")
        require(self.text.encode("utf-8") == self.raw,
                f"{self.path.name}: UTF-8 round trip changed source bytes")

    def line(self, value: str, *, count: int = 1, occurrence: int = 0,
             after: int = 0, before: int | None = None) -> int:
        r"""Match a whole source line, preserving its leading spaces and CRLF.

        \s is deliberately avoided: it can consume adjacent blank lines.
        Expected match counts distinguish repeated contents/notes headings.
        """
        stop = len(self.text) if before is None else before
        pattern = re.compile(r"^" + re.escape(value) + r"\r?$", re.MULTILINE)
        matches = [m for m in pattern.finditer(self.text)
                   if after <= m.start() < stop]
        require(len(matches) == count,
                f"{self.path.name}: expected {count} anchors {value!r}, got {len(matches)}")
        return matches[occurrence].start()

    def manifest(self, boundaries: list[Boundary], default: str) -> dict:
        require(boundaries[0].start == 0, "First section must start at source offset 0")
        require(len({b.id for b in boundaries}) == len(boundaries), "Duplicate section IDs")
        require(all(b.kind in {"front", "primary", "back"} for b in boundaries),
                "Unknown section kind")
        require(all(left.start < right.start for left, right in zip(boundaries, boundaries[1:])),
                f"{self.path.name}: section boundaries must be strictly increasing")
        require(boundaries[-1].start < len(self.text), "Last section cannot be empty")
        require(any(b.id == default and b.kind == "primary" for b in boundaries),
                "Default section must name a primary section")

        sections, pieces = [], []
        cursor = 0
        utf16_source = self.text.encode("utf-16-le")
        for index, boundary in enumerate(boundaries):
            end = boundaries[index + 1].start if index + 1 < len(boundaries) else len(self.text)
            piece = self.text[boundary.start:end]
            stop = cursor + utf16_length(piece)
            entry = {"id": boundary.id, "label": boundary.label, "kind": boundary.kind,
                     "start": cursor, "end": stop}
            if boundary.group:
                entry["group"] = boundary.group
            require(utf16_source[cursor * 2:stop * 2].decode("utf-16-le") == piece,
                    "UTF-16 boundaries changed a section")
            sections.append(entry)
            pieces.append(piece)
            cursor = stop

        require("".join(pieces).encode("utf-8") == self.raw,
                f"{self.path.name}: section reconstruction changed source bytes")
        require(cursor == utf16_length(self.text), "Sections do not reach source EOF")
        require(all(left["end"] == right["start"]
                    for left, right in zip(sections, sections[1:])), "Non-contiguous sections")
        require(self.path.read_bytes() == self.raw, "Source changed during manifest generation")
        return {
            "source": self.book["path"],
            "path": self.book["path"],
            "sha256": self.sha256,
            "sourceBytes": len(self.raw),
            "length": cursor,
            "defaultSectionId": default,
            "sections": sections,
        }


def republic(source: Source) -> dict:
    title = source.line("THE REPUBLIC")
    introduction = source.line(" INTRODUCTION AND ANALYSIS.", count=2, occurrence=1)
    cast = source.line(" THE REPUBLIC.", count=2, occurrence=1)
    source.line(" PERSONS OF THE DIALOGUE.", after=cast)
    boundaries = [
        Boundary(0, "republic-source-notices", "Source notices", "front"),
        Boundary(title, "republic-title", "Title and contents", "front"),
        Boundary(introduction, "republic-introduction", "Introduction and analysis", "front"),
        Boundary(cast, "republic-persons", "Persons of the dialogue", "front"),
    ]
    roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
    actual_book_headings = re.findall(r"^ BOOK ([IVX]+)\.\r?$", source.text[cast:], re.MULTILINE)
    require(actual_book_headings == roman, "Republic must have exactly Books I–X in order")
    for number, numeral in enumerate(roman, 1):
        start = source.line(f" BOOK {numeral}.", after=cast)
        boundaries.append(Boundary(start, f"republic-book-{number}", f"Book {numeral}", "primary"))
    end = source.line("*** END OF THE PROJECT GUTENBERG EBOOK THE REPUBLIC ***")
    boundaries.append(Boundary(end, "republic-license", "Project Gutenberg license and notices", "back"))
    return source.manifest(boundaries, "republic-book-1")


def symposium(source: Source) -> dict:
    title = source.line("SYMPOSIUM", count=2)
    introduction = source.line("INTRODUCTION.")
    cast = source.line("SYMPOSIUM", count=2, occurrence=1)
    source.line("PERSONS OF THE DIALOGUE: Apollodorus, who repeats to his companion", after=cast)
    source.line("SCENE: The House of Agathon.", after=cast)
    dialogue = source.line("Concerning the things about which you ask to be informed I believe that", after=cast)
    end = source.line("*** END OF THE PROJECT GUTENBERG EBOOK SYMPOSIUM ***")
    return source.manifest([
        Boundary(0, "symposium-source-notices", "Source notices", "front"),
        Boundary(title, "symposium-title", "Title and credits", "front"),
        Boundary(introduction, "symposium-introduction", "Introduction", "front"),
        Boundary(cast, "symposium-persons", "Persons and scene of the dialogue", "front"),
        Boundary(dialogue, "symposium-dialogue", "Symposium", "primary"),
        Boundary(end, "symposium-license", "Project Gutenberg license and notices", "back"),
    ], "symposium-dialogue")


def apology(source: Source) -> dict:
    title = source.line("Apology")
    introduction = source.line("INTRODUCTION.")
    dialogue = source.line("APOLOGY")  # Contents has one leading space.
    source.line("How you, O Athenians, have been affected by my accusers, I cannot tell;", after=dialogue)
    end = source.line("*** END OF THE PROJECT GUTENBERG EBOOK APOLOGY ***")
    return source.manifest([
        Boundary(0, "apology-source-notices", "Source notices", "front"),
        Boundary(title, "apology-title", "Title and contents", "front"),
        Boundary(introduction, "apology-introduction", "Introduction", "front"),
        Boundary(dialogue, "apology-dialogue", "Apology", "primary"),
        Boundary(end, "apology-license", "Project Gutenberg license and notices", "back"),
    ], "apology-dialogue")


def story_label(number: int, heading: str) -> str:
    """Readable navigation metadata; original headings are never modified."""
    heading = re.sub(r"\s*\[\d+\]\s*$", "", heading).rstrip(".")
    minor = {"a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on", "the", "to", "with"}
    words = heading.lower().split()
    title = " ".join(word if i and word in minor else word[:1].upper() + word[1:]
                     for i, word in enumerate(words))
    return f"{number}. {title}"


def anansi(source: Source) -> dict:
    contents = source.line("CONTENTS.")
    preface = source.line("PREFACE.")
    first_group = source.line("ANIMAL STORIES.")  # Contents version is indented.
    witticisms = source.line("WITTICISMS.", count=2)
    riddles = source.line("RIDDLES.")
    index_riddles = source.line("INDEX TO RIDDLES.")
    abbreviations = source.line("ABBREVIATIONS OF TITLES.")
    notes = source.line("NOTES.")
    supplementary = source.line("SUPPLEMENTARY NOTES.")
    informants = source.line("INDEX TO INFORMANTS.")
    footnotes = source.line("NOTES")
    boundaries = [
        Boundary(0, "anansi-title", "Title and credits", "front"),
        Boundary(contents, "anansi-contents", "Original contents", "front"),
        Boundary(preface, "anansi-preface", "Preface", "front"),
    ]
    # Restrict detection to the main story corpus. Its numbered uppercase
    # headings recur in Notes, while riddles and informants restart numbering.
    # Story 145 carries a trailing [70], so a final-period-only pattern fails.
    pattern = re.compile(r"^(\d{1,3})\. ([^\r\n]+)\r?$", re.MULTILINE)
    stories = [match for match in pattern.finditer(source.text)
               if first_group <= match.start() < witticisms]
    require([int(match[1]) for match in stories] == list(range(1, 150)),
            "Anansi must have exactly stories 1–149, once each and in order")
    require(all(match[2] == match[2].upper() for match in stories),
            "Anansi story titles must be uppercase whole-line headings")
    require(all(source.text[match.end():].startswith("\n\n") for match in stories),
            "Anansi story headings must be followed by a blank line")
    groups = [
        (1, first_group, "Animal stories"),
        (63, source.line("OLD STORIES, CHIEFLY OF SORCERY."), "Old stories, chiefly of sorcery"),
        (100, source.line("MODERN EUROPEAN STORIES."), "Modern European stories"),
        (139, source.line("DANCE AND SONG."), "Dance and song"),
    ]
    group_starts = {number: (start, label) for number, start, label in groups}
    group = None
    for match in stories:
        number, heading = int(match[1]), match[2]
        start = match.start()
        if number in group_starts:
            # Carry category headings with the following story, so they cannot
            # become a misleading final page of the preceding story.
            start, group = group_starts[number]
            require(start <= match.start(), "Anansi group must precede its first story")
        boundaries.append(Boundary(start, f"anansi-story-{number}",
                                   story_label(number, heading), "primary", group))
    boundaries.extend([
        Boundary(witticisms, "anansi-witticisms", "Witticisms", "primary", "Witticisms and riddles"),
        Boundary(riddles, "anansi-riddles", "Riddles", "primary", "Witticisms and riddles"),
        Boundary(index_riddles, "anansi-index-riddles", "Index to riddles", "back"),
        Boundary(abbreviations, "anansi-abbreviations", "Abbreviations of titles", "back"),
        Boundary(notes, "anansi-story-notes", "Notes to the stories", "back"),
        Boundary(supplementary, "anansi-supplementary-notes", "Supplementary notes", "back"),
        Boundary(informants, "anansi-index-informants", "Index to informants", "back"),
        Boundary(footnotes, "anansi-footnotes", "Footnotes", "back"),
    ])
    result = source.manifest(boundaries, "anansi-story-1")
    original_path = DIST / source.book["notices"]
    original = original_path.read_bytes()
    original_hash = source.spec["originalSourceSha256"]
    require(hashlib.sha256(original).hexdigest() == original_hash,
            "Anansi's intact Gutenberg source/notices differ from the audited file")
    result["originalSource"] = {
        "path": source.book["notices"], "sha256": original_hash,
        "sourceBytes": len(original),
    }
    return result


def anchored(source: Source) -> dict:
    """A verified edition expressed as ordered, exact source-heading anchors.

    A boundary has no magic character offsets. Its source line and occurrence
    count must still agree with the independently pinned original file.
    """
    boundaries = []
    for index, item in enumerate(source.spec["sections"]):
        if index == 0:
            require(item.get("line") is None, "First section must start at source offset 0")
            start = 0
        else:
            require(isinstance(item.get("line"), str), "Every later section needs an exact source line")
            start = source.line(item["line"], count=item.get("count", 1), occurrence=item.get("occurrence", 0))
        boundaries.append(Boundary(start, item["id"], item["label"], item["kind"], item.get("group")))
    result = source.manifest(boundaries, source.spec["defaultSectionId"])
    for section, item in zip(result["sections"], source.spec["sections"]):
        pagination = item.get("pagination", source.spec.get("pagination", "legacy"))
        require(source.spec.get("pagination", "legacy") in ("legacy", "bounded"),
                "Unknown edition pagination policy")
        require(pagination in ("legacy", "bounded"), "Unknown section pagination policy")
        if pagination != "legacy":
            section["pagination"] = pagination
        # Rendering metadata is opt-in and source-anchored, never source rewriting.
        # Resolve an edition default into each section so the existing core API stays intact.
        formats = {"auto", "verse", "prose"}
        require(isinstance(source.spec.get("textFormat", "auto"), str) and
                source.spec.get("textFormat", "auto") in formats, "Unknown edition text format")
        text_format = item.get("textFormat", source.spec.get("textFormat", "auto"))
        require(isinstance(text_format, str) and text_format in formats, "Unknown section text format")
        if text_format != "auto":
            section["textFormat"] = text_format
        format_ranges = []
        spans = item.get("textFormatRanges", [])
        require(isinstance(spans, list), "Text format ranges must be a list")
        for span in spans:
            require(isinstance(span, dict) and isinstance(span.get("format"), str) and
                    span.get("format") in formats, "Unknown range text format")
            require(isinstance(span.get("start"), dict), "Text format range needs a source start anchor")
            offsets = {}
            for key in ("start", "end"):
                anchor = span.get(key)
                if key == "end" and anchor is None:
                    offsets[key] = section["end"]
                    continue
                require(isinstance(anchor, dict) and isinstance(anchor.get("line"), str),
                        "Text format range needs exact whole-line anchors")
                count, occurrence = anchor.get("count", 1), anchor.get("occurrence", 0)
                require(type(count) is int and count > 0 and type(occurrence) is int and
                        0 <= occurrence < count, "Text format anchor has an invalid occurrence/count")
                start = source.line(anchor["line"], count=count, occurrence=occurrence)
                offsets[key] = utf16_length(source.text[:start])
            require(section["start"] <= offsets["start"] < offsets["end"] <= section["end"],
                    "Text format range lies outside its section or is empty")
            require(not format_ranges or format_ranges[-1]["end"] <= offsets["start"],
                    "Text format ranges must be ordered and non-overlapping")
            format_ranges.append({**offsets, "format": span["format"]})
        if format_ranges:
            section["textFormatRanges"] = format_ranges
        headings = []
        for anchor in item.get("headingAnchors", []):
            start = source.line(anchor["line"], count=anchor.get("count", 1), occurrence=anchor.get("occurrence", 0))
            offset = utf16_length(source.text[:start])
            require(section["start"] <= offset < section["end"], "Heading lies outside its source section")
            headings.append(offset)
        if headings:
            section["headingStarts"] = sorted(set(headings))
        break_anchors = item.get("passageBreakAnchors", [])
        require(isinstance(break_anchors, list), "Passage break anchors must be a list")
        require(not break_anchors or pagination == "bounded",
                "Passage breaks require explicit bounded pagination")
        breaks = []
        for anchor in break_anchors:
            require(isinstance(anchor, dict) and isinstance(anchor.get("line"), str),
                    "Passage break needs an exact whole-line anchor")
            count, occurrence = anchor.get("count", 1), anchor.get("occurrence", 0)
            require(type(count) is int and count > 0 and type(occurrence) is int and
                    0 <= occurrence < count, "Passage break has an invalid occurrence/count")
            start = source.line(anchor["line"], count=count, occurrence=occurrence)
            offset = utf16_length(source.text[:start])
            require(section["start"] < offset < section["end"],
                    "Passage break must lie strictly inside its section")
            require(offset in headings, "Passage break must name an audited heading anchor")
            require(not breaks or breaks[-1] < offset,
                    "Passage breaks must be unique and in source order")
            breaks.append(offset)
        if breaks:
            section["passageBreakStarts"] = breaks
        attribution = item.get("readerAttribution")
        if attribution:
            evidence = attribution.get("sourceEvidence", "")
            source_piece = source.text.encode("utf-16-le")[section["start"] * 2:section["end"] * 2].decode("utf-16-le")
            require(bool(evidence) and evidence in source_piece,
                    "Individual source attribution must have exact evidence in its own section")
            section["sourceAttribution"] = attribution
    return result


def build() -> dict:
    catalog = json.loads((DIST / "catalog.json").read_text(encoding="utf-8"))
    by_id = {book["id"]: book for book in catalog}
    builders = {"republic": republic, "symposium": symposium,
                "apology": apology, "anansi": anansi, "anchored": anchored}
    require(len(by_id) == len(catalog), "Catalog contains duplicate book IDs")
    require(set(SPECS) == set(by_id), "Every catalog book must have exactly one audited edition spec")
    books = {}
    for book_id, book in by_id.items():
        source = Source(book)
        archive = source.spec.get("preservationArchive")
        if archive:
            require(book.get("preservation_archive") == archive,
                    f"{book_id}: preservation archive disagrees with audited edition spec")
            preserved = (DIST / archive["path"]).read_bytes()
            require(len(preserved) == archive["bytes"] and
                    hashlib.sha256(preserved).hexdigest() == archive["sha256"],
                    f"{book_id}: illustrated preservation archive differs from audited original")
            with zipfile.ZipFile(DIST / archive["path"]) as bundle:
                require(bundle.testzip() is None, f"{book_id}: damaged preservation archive")
                html = bundle.read(archive["html_entry"])
                require(hashlib.sha256(html).hexdigest() == archive["html_sha256"],
                        f"{book_id}: archived HTML differs from audited original")
        result = builders[source.spec["builder"]](source)
        primary = [section for section in result["sections"] if section["kind"] == "primary"]
        require(len(primary) == source.spec["primarySectionCount"],
                f"{book_id}: natural primary section count changed")
        first = next(section for section in primary if section["id"] == result["defaultSectionId"])
        opening = source.text.encode("utf-16-le")[first["start"] * 2:first["end"] * 2].decode("utf-16-le")
        require(source.spec["primaryOpening"] in opening[:5000], f"{book_id}: primary opening was not found")
        books[book_id] = result
    all_ids = [section["id"] for book in books.values() for section in book["sections"]]
    require(len(all_ids) == len(set(all_ids)), "Section IDs must be globally unique")
    return {"version": 1, "offsetEncoding": "utf-16", "endExclusive": True, "books": books}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify sections.json without changing it")
    args = parser.parse_args()
    manifest = build()
    encoded = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if args.check:
        require(OUTPUT.exists() and OUTPUT.read_bytes() == encoded,
                "dist/sections.json is stale; run scripts/build_sections.py")
    else:
        OUTPUT.write_bytes(encoded)
    for book_id, book in manifest["books"].items():
        primary = sum(section["kind"] == "primary" for section in book["sections"])
        print(f"{book_id}: {len(book['sections'])} sections, {primary} primary, "
              f"{book['length']:,} UTF-16 units; complete coverage and original bytes verified")
    print("sections.json verified" if args.check else "sections.json generated")


if __name__ == "__main__":
    main()
