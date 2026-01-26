#!/usr/bin/env python3
"""
Best Version Selector for Mythic Library Phase 3.

For texts with multiple normalized versions, selects the best one based on:
1. Source format priority (gutenberg > archive > sacred-texts > etcsl)
2. Word count (longer is generally better)
3. Extraction quality (for PDFs)

Creates a symlink/copy at {text-id}_best.txt and outputs best_versions.json.

Usage:
    python scripts/normalize/select_best.py
"""

import io
import json
import shutil
import sys

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
TEXTS_DIR = PROJECT_ROOT / "texts"
SOURCES_DIR = PROJECT_ROOT / "sources"
OUTPUT_FILE = SOURCES_DIR / "best_versions.json"

# Source format priority (higher = better)
FORMAT_PRIORITY = {
    "gutenberg": 5,
    "pdf": 3,         # good PDF extracts
    "other": 2,
    "sacred-texts": 2,
    "etcsl": 2,
    "sacred_texts": 2,
    "archive-text": 2,
}


def score_version(meta: dict) -> tuple:
    """Score a normalized version for selection. Higher is better."""
    fmt = meta.get("source_format", "other")
    fmt_score = FORMAT_PRIORITY.get(fmt, 1)

    # Penalize poor PDF extractions
    if fmt == "pdf":
        quality = meta.get("extraction_quality", "unknown")
        quality_mult = {
            "good": 1.0,
            "fair": 0.7,
            "partial": 0.3,
            "poor": 0.1,
            "failed": 0.0,
            "error": 0.0,
        }
        fmt_score *= quality_mult.get(quality, 0.5)

    word_count = meta.get("word_count", 0)
    return (fmt_score, word_count)


def find_normalized_versions(text_dir: Path) -> list:
    """Find all normalized versions for a text."""
    norm_dir = text_dir / "normalized"
    if not norm_dir.exists():
        return []

    versions = []
    for meta_file in sorted(norm_dir.glob("*_metadata.json")):
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)

            # Find corresponding text file
            text_stem = meta_file.stem.replace("_metadata", "")
            text_file = norm_dir / f"{text_stem}.txt"
            if text_file.exists():
                meta["_norm_path"] = str(text_file)
                meta["_meta_path"] = str(meta_file)
                versions.append(meta)
        except Exception:
            continue

    return versions


def run_selection():
    """Select best version for each text."""
    best_versions = {}
    stats = {"texts_processed": 0, "texts_with_content": 0, "texts_without_content": 0}

    for tradition_dir in sorted(TEXTS_DIR.iterdir()):
        if not tradition_dir.is_dir():
            continue
        tradition = tradition_dir.name

        for text_dir in sorted(tradition_dir.iterdir()):
            if not text_dir.is_dir():
                continue
            text_id = text_dir.name
            stats["texts_processed"] += 1

            versions = find_normalized_versions(text_dir)

            if not versions:
                stats["texts_without_content"] += 1
                best_versions[text_id] = {
                    "text_id": text_id,
                    "tradition": tradition,
                    "status": "no_normalized_content",
                    "versions_found": 0,
                }
                continue

            stats["texts_with_content"] += 1

            # Score and select best
            scored = [(score_version(v), v) for v in versions]
            scored.sort(key=lambda x: x[0], reverse=True)
            best_score, best = scored[0]

            # Copy/link as _best.txt
            norm_dir = text_dir / "normalized"
            best_path = norm_dir / f"{text_id}_best.txt"
            src_path = Path(best["_norm_path"])

            try:
                shutil.copy2(str(src_path), str(best_path))
            except Exception as e:
                print(f"  [WARN] Could not copy best for {text_id}: {e}")

            best_versions[text_id] = {
                "text_id": text_id,
                "tradition": tradition,
                "status": "selected",
                "best_file": str(best_path),
                "source_file": best.get("original_file", ""),
                "source_format": best.get("source_format", ""),
                "word_count": best.get("word_count", 0),
                "versions_found": len(versions),
                "selection_reason": f"format={best.get('source_format')}, "
                                   f"words={best.get('word_count', 0)}",
            }

            fmt = best.get("source_format", "?")
            wc = best.get("word_count", 0)
            nv = len(versions)
            print(f"  {tradition}/{text_id}: {fmt} ({wc} words) "
                  f"[{nv} version{'s' if nv != 1 else ''}]")

    # Write output
    output = {
        "summary": stats,
        "best_versions": best_versions,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"BEST VERSION SELECTION COMPLETE")
    print(f"{'='*60}")
    print(f"Texts processed:      {stats['texts_processed']}")
    print(f"With content:         {stats['texts_with_content']}")
    print(f"Without content:      {stats['texts_without_content']}")
    print(f"\nOutput: {OUTPUT_FILE}")

    return output


if __name__ == "__main__":
    run_selection()
