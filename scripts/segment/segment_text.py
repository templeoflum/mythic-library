#!/usr/bin/env python3
"""
Text Segmentation for Mythic Library Phase 3.

Splits normalized texts into structural units (books, chapters, tablets,
hymns, tales, etc.) using regex-based structure detection.

Usage:
    python scripts/segment/segment_text.py                  # Segment all
    python scripts/segment/segment_text.py --text the-iliad # Segment one

Output per text:
    texts/{tradition}/{text-id}/segments/
        segments.json           # Segment index
        seg_001_{label}.txt     # Individual segment files
"""

import argparse
import io
import json
import re
import sys

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
TEXTS_DIR = PROJECT_ROOT / "texts"
SOURCES_DIR = PROJECT_ROOT / "sources"

# Structural division patterns (ordered by specificity)
DIVISION_PATTERNS = [
    # Epic books: "BOOK I", "Book 1", "BOOK THE FIRST"
    {
        "type": "book",
        "pattern": r'^(?:BOOK|Book)\s+(?:THE\s+)?([IVXLCDM]+|\d+|FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH|ELEVENTH|TWELFTH|THIRTEENTH|FOURTEENTH|FIFTEENTH|SIXTEENTH|SEVENTEENTH|EIGHTEENTH|NINETEENTH|TWENTIETH|TWENTY-\w+)\b',
        "label_extract": r'^(?:BOOK|Book)\s+(?:THE\s+)?(.+?)[\.\s]*$',
    },
    # Tablets: "THE FIRST TABLET", "TABLET I", "First Tablet"
    {
        "type": "tablet",
        "pattern": r'^(?:THE\s+)?(?:FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH|ELEVENTH|TWELFTH)\s+TABLET|^TABLET\s+[IVXLCDM\d]+',
        "label_extract": r'^(.+?)[\.\s]*$',
    },
    # Cantos: "CANTO I", "Canto 1"
    {
        "type": "canto",
        "pattern": r'^(?:CANTO|Canto)\s+([IVXLCDM]+|\d+)',
        "label_extract": r'^(.+?)[\.\s]*$',
    },
    # Runes: "RUNE I", "Rune 1" (Kalevala)
    {
        "type": "rune",
        "pattern": r'^(?:RUNE|Rune)\s+([IVXLCDM]+|\d+)',
        "label_extract": r'^(.+?)[\.\s]*$',
    },
    # Hymns: "HYMN TO...", "Hymn I", "HYMN I."
    {
        "type": "hymn",
        "pattern": r'^(?:HYMN|Hymn)\s+(?:TO\s+)?(?:[IVXLCDM]+|\d+|[A-Z])',
        "label_extract": r'^(.+?)[\.\s]*$',
    },
    # Chapters: "CHAPTER I", "Chapter 1", "CHAPTER THE FIRST"
    {
        "type": "chapter",
        "pattern": r'^(?:CHAPTER|Chapter)\s+(?:THE\s+)?([IVXLCDM]+|\d+|FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH)',
        "label_extract": r'^(.+?)[\.\s]*$',
    },
    # Parts: "PART I", "Part One"
    {
        "type": "part",
        "pattern": r'^(?:PART|Part)\s+(?:THE\s+)?([IVXLCDM]+|\d+|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|FIRST|SECOND|THIRD)',
        "label_extract": r'^(.+?)[\.\s]*$',
    },
    # Story/Tale markers (folktale collections)
    {
        "type": "tale",
        "pattern": r'^(?:THE\s+(?:STORY|TALE|LEGEND|MYTH)\s+OF|STORY\s+(?:OF|No\.?\s*\d+)|THE\s+\w+(?:\s+\w+){0,3}\s+(?:STORY|TALE))',
        "label_extract": r'^(.+?)[\.\s]*$',
    },
    # ETCSL line ranges: "1-5", "6-13"
    {
        "type": "line_range",
        "pattern": r'^\d+-\d+$',
        "label_extract": r'^(.+)$',
    },
    # Numbered sections: "I.", "II.", "III." (standalone on a line)
    {
        "type": "section",
        "pattern": r'^([IVXLCDM]+)\.\s*$',
        "label_extract": r'^(.+?)[\.\s]*$',
    },
]


def slugify(text: str, max_len: int = 40) -> str:
    """Convert text to a URL-friendly slug."""
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = slug.strip('-')
    return slug[:max_len]


def detect_divisions(text: str) -> list:
    """
    Detect structural divisions in a text.
    Returns list of (line_number, division_type, label).
    """
    lines = text.split('\n')
    divisions = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        # Skip very long lines (not headers)
        if len(stripped) > 100:
            continue

        for pattern_def in DIVISION_PATTERNS:
            if re.match(pattern_def["pattern"], stripped, re.IGNORECASE):
                # Extract label
                label_match = re.match(
                    pattern_def["label_extract"], stripped, re.IGNORECASE
                )
                label = label_match.group(1).strip() if label_match else stripped
                divisions.append((i, pattern_def["type"], label))
                break  # Only match first pattern per line

    return divisions


def segment_by_divisions(text: str, divisions: list) -> list:
    """Split text into segments based on detected divisions."""
    lines = text.split('\n')
    segments = []

    if not divisions:
        # No divisions found - return whole text as one segment
        return [{
            "label": "full_text",
            "segment_type": "full",
            "start_line": 0,
            "end_line": len(lines) - 1,
            "content": text,
        }]

    for idx, (line_num, div_type, label) in enumerate(divisions):
        # Determine end of this segment
        if idx + 1 < len(divisions):
            end_line = divisions[idx + 1][0] - 1
        else:
            end_line = len(lines) - 1

        # Extract content
        segment_lines = lines[line_num:end_line + 1]
        content = '\n'.join(segment_lines).strip()

        if content:  # Skip empty segments
            segments.append({
                "label": label,
                "segment_type": div_type,
                "start_line": line_num,
                "end_line": end_line,
                "content": content,
            })

    # Handle content before first division
    if divisions and divisions[0][0] > 0:
        preamble_lines = lines[:divisions[0][0]]
        preamble = '\n'.join(preamble_lines).strip()
        if preamble and len(preamble.split()) > 50:  # Skip tiny preambles
            segments.insert(0, {
                "label": "preamble",
                "segment_type": "preamble",
                "start_line": 0,
                "end_line": divisions[0][0] - 1,
                "content": preamble,
            })

    return segments


def segment_by_blank_lines(text: str, min_segment_words: int = 200) -> list:
    """
    Fallback segmentation: split by double blank lines.
    Groups small sections together to meet minimum word count.
    """
    # Split on double+ blank lines
    raw_sections = re.split(r'\n\s*\n\s*\n', text)

    segments = []
    current_content = []
    current_words = 0

    for section in raw_sections:
        section = section.strip()
        if not section:
            continue

        word_count = len(section.split())
        current_content.append(section)
        current_words += word_count

        if current_words >= min_segment_words:
            content = '\n\n'.join(current_content)
            segments.append({
                "label": f"section_{len(segments)+1}",
                "segment_type": "section",
                "content": content,
            })
            current_content = []
            current_words = 0

    # Don't forget the last chunk
    if current_content:
        content = '\n\n'.join(current_content)
        if segments:
            # Append to last segment if too short
            segments[-1]["content"] += '\n\n' + content
        else:
            segments.append({
                "label": "section_1",
                "segment_type": "section",
                "content": content,
            })

    return segments


def process_text(text_dir: Path, text_id: str, tradition: str) -> dict:
    """Segment a single text. Returns summary dict."""
    # Find best normalized text
    norm_dir = text_dir / "normalized"
    best_file = norm_dir / f"{text_id}_best.txt"

    if not best_file.exists():
        # Try any normalized file
        norm_files = list(norm_dir.glob(f"{text_id}_*.txt"))
        norm_files = [f for f in norm_files if "_metadata" not in f.name]
        if not norm_files:
            return {"status": "no_normalized_text", "text_id": text_id}
        best_file = max(norm_files, key=lambda f: f.stat().st_size)

    with open(best_file, "r", encoding="utf-8") as f:
        text = f.read()

    if len(text.split()) < 100:
        return {"status": "too_short", "text_id": text_id}

    # Detect structural divisions
    divisions = detect_divisions(text)

    # Choose segmentation strategy
    if divisions and len(divisions) >= 2:
        segments = segment_by_divisions(text, divisions)
        strategy = "structural"
    else:
        # Fallback to blank-line splitting for texts without clear structure
        word_count = len(text.split())
        if word_count > 5000:
            segments = segment_by_blank_lines(text, min_segment_words=500)
            strategy = "blank_line"
        else:
            # Short text - keep as one segment
            segments = [{
                "label": "full_text",
                "segment_type": "full",
                "start_line": 0,
                "end_line": len(text.split('\n')) - 1,
                "content": text,
            }]
            strategy = "single"

    # Write segments
    seg_dir = text_dir / "segments"
    seg_dir.mkdir(exist_ok=True)

    segment_index = {
        "text_id": text_id,
        "tradition": tradition,
        "source_file": str(best_file),
        "strategy": strategy,
        "segment_count": len(segments),
        "segments": [],
    }

    for i, seg in enumerate(segments):
        seg_id = f"seg_{i+1:03d}"
        slug = slugify(seg["label"])
        filename = f"{seg_id}_{slug}.txt"
        filepath = seg_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(seg["content"])

        word_count = len(seg["content"].split())

        segment_index["segments"].append({
            "id": seg_id,
            "label": seg["label"],
            "segment_type": seg.get("segment_type", "unknown"),
            "file": filename,
            "word_count": word_count,
            "start_line": seg.get("start_line"),
            "end_line": seg.get("end_line"),
        })

    # Write segment index
    index_path = seg_dir / "segments.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(segment_index, f, indent=2, ensure_ascii=False)

    return {
        "status": "segmented",
        "text_id": text_id,
        "tradition": tradition,
        "strategy": strategy,
        "segment_count": len(segments),
        "total_words": sum(len(s["content"].split()) for s in segments),
    }


def run_segmentation(target_text: str = None):
    """Run segmentation on all or a specific text."""
    results = {"segmented": [], "skipped": [], "errors": []}
    total = 0
    success = 0

    for tradition_dir in sorted(TEXTS_DIR.iterdir()):
        if not tradition_dir.is_dir():
            continue
        tradition = tradition_dir.name

        for text_dir in sorted(tradition_dir.iterdir()):
            if not text_dir.is_dir():
                continue
            text_id = text_dir.name

            if target_text and target_text != text_id:
                continue

            norm_dir = text_dir / "normalized"
            if not norm_dir.exists():
                continue

            total += 1
            try:
                result = process_text(text_dir, text_id, tradition)
                if result["status"] == "segmented":
                    success += 1
                    results["segmented"].append(result)
                    print(f"  [{result['strategy']:10s}] {tradition}/{text_id}: "
                          f"{result['segment_count']} segments, "
                          f"{result['total_words']} words")
                else:
                    results["skipped"].append(result)
                    print(f"  [SKIP] {tradition}/{text_id}: {result['status']}")
            except Exception as e:
                results["errors"].append({
                    "text_id": text_id,
                    "tradition": tradition,
                    "error": str(e),
                })
                print(f"  [ERR] {tradition}/{text_id}: {e}")

    # Summary
    print(f"\n{'='*60}")
    print(f"SEGMENTATION COMPLETE")
    print(f"{'='*60}")
    print(f"Texts processed:    {total}")
    print(f"Successfully segmented: {success}")
    print(f"Skipped:            {len(results['skipped'])}")
    print(f"Errors:             {len(results['errors'])}")

    # Strategy breakdown
    strategy_counts = {}
    total_segments = 0
    for r in results["segmented"]:
        s = r["strategy"]
        strategy_counts[s] = strategy_counts.get(s, 0) + 1
        total_segments += r["segment_count"]

    print(f"\nTotal segments created: {total_segments}")
    print(f"Strategy breakdown:")
    for s, count in sorted(strategy_counts.items(), key=lambda x: -x[1]):
        print(f"  {s:15s} {count:4d} texts")

    # Save results
    results_path = SOURCES_DIR / "segmentation_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to: {results_path}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Segment mythic library texts")
    parser.add_argument("--text", help="Segment a specific text by text_id")
    args = parser.parse_args()
    run_segmentation(target_text=args.text)
