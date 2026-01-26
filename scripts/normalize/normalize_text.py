#!/usr/bin/env python3
"""
Text Normalization Pipeline for Mythic Library Phase 3.

Normalizes downloaded text files into clean UTF-8 with metadata.
Handles three source formats:
  - Project Gutenberg (strip boilerplate, parse metadata)
  - Sacred Texts (strip headers, navigation artifacts)
  - ETCSL (strip navigation, fix word-joining artifacts)

Usage:
    python scripts/normalize/normalize_text.py                  # Normalize all
    python scripts/normalize/normalize_text.py --text the-iliad # Normalize one
    python scripts/normalize/normalize_text.py --audit-first    # Run audit then normalize

Output per text:
    texts/{tradition}/{text-id}/normalized/
        {text-id}_normalized.txt
        {text-id}_metadata.json
"""

import argparse
import csv
import io
import json
import os
import re
import sys

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
TEXTS_DIR = PROJECT_ROOT / "texts"
SOURCES_DIR = PROJECT_ROOT / "sources"
MASTER_CATALOG = SOURCES_DIR / "master_catalog.csv"
AUDIT_FILE = SOURCES_DIR / "corpus_audit.json"


def load_catalog() -> dict:
    """Load master catalog keyed by text_id."""
    catalog = {}
    try:
        with open(MASTER_CATALOG, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                catalog[row["text_id"]] = row
    except Exception:
        pass
    return catalog


def read_text_file(filepath: Path) -> str:
    """Read a text file, handling BOM and encoding issues."""
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(filepath, "r", encoding="latin-1") as f:
            return f.read()


# ============================================================
# Gutenberg Normalizer
# ============================================================

def parse_gutenberg_metadata(header: str) -> dict:
    """Extract metadata from Gutenberg header block."""
    meta = {}
    patterns = {
        "title": r"Title:\s*(.+?)(?:\n\n|\n[A-Z])",
        "author": r"Author:\s*(.+?)(?:\n\n|\n[A-Z])",
        "translator": r"Translator:\s*(.+?)(?:\n\n|\n[A-Z])",
        "language": r"Language:\s*(.+?)(?:\n\n|\n[A-Z])",
        "release_date": r"Release date:\s*(.+?)(?:\[|\n)",
        "ebook_id": r"\[(?:eBook|EBook) #(\d+)\]",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, header, re.DOTALL)
        if match:
            meta[key] = match.group(1).strip()
    return meta


def normalize_gutenberg(content: str, text_id: str) -> tuple:
    """
    Normalize a Project Gutenberg text file.
    Returns (normalized_text, metadata_dict).
    """
    # Find start marker
    start_patterns = [
        r"\*\*\* START OF THE PROJECT GUTENBERG EBOOK .+?\*\*\*",
        r"\*\*\* START OF THIS PROJECT GUTENBERG EBOOK .+?\*\*\*",
        r"\*\*\*START OF THE PROJECT GUTENBERG EBOOK .+?\*\*\*",
    ]
    start_pos = 0
    header_text = ""
    for pat in start_patterns:
        match = re.search(pat, content, re.IGNORECASE)
        if match:
            header_text = content[:match.start()]
            start_pos = match.end()
            break

    # Find end marker
    end_patterns = [
        r"\*\*\* END OF THE PROJECT GUTENBERG EBOOK .+?\*\*\*",
        r"\*\*\* END OF THIS PROJECT GUTENBERG EBOOK .+?\*\*\*",
        r"\*\*\*END OF THE PROJECT GUTENBERG EBOOK .+?\*\*\*",
        r"End of the Project Gutenberg EBook",
        r"End of Project Gutenberg",
    ]
    end_pos = len(content)
    for pat in end_patterns:
        match = re.search(pat, content, re.IGNORECASE)
        if match:
            end_pos = match.start()
            break

    # Extract body
    body = content[start_pos:end_pos]

    # Clean up
    body = body.strip()
    # Remove [Illustration] markers
    body = re.sub(r'\[Illustration[^\]]*\]', '', body)
    # Normalize line endings
    body = body.replace('\r\n', '\n').replace('\r', '\n')
    # Collapse 3+ consecutive blank lines to 2
    body = re.sub(r'\n{4,}', '\n\n\n', body)
    # Strip trailing whitespace per line
    body = '\n'.join(line.rstrip() for line in body.split('\n'))
    # Strip leading/trailing whitespace
    body = body.strip()

    # Parse metadata from header
    meta = parse_gutenberg_metadata(header_text)
    meta["source_format"] = "gutenberg"
    meta["original_file"] = ""  # filled by caller
    meta["text_id"] = text_id

    return body, meta


# ============================================================
# Sacred Texts Normalizer
# ============================================================

def normalize_sacred_texts(content: str, text_id: str) -> tuple:
    """
    Normalize a Sacred Texts downloaded file.
    Returns (normalized_text, metadata_dict).
    """
    meta = {"source_format": "sacred-texts", "text_id": text_id}

    # Parse custom header
    lines = content.split('\n')
    body_start = 0

    # Look for the separator line
    for i, line in enumerate(lines):
        if line.strip().startswith("====="):
            body_start = i + 1
            # Parse header lines above
            for hline in lines[:i]:
                if hline.startswith("Source:"):
                    meta["source_url"] = hline[7:].strip()
                elif hline.startswith("Downloaded:"):
                    meta["download_date"] = hline[11:].strip()
                elif hline.startswith("Corpus:"):
                    meta["corpus"] = hline[7:].strip()
            break

    body_lines = lines[body_start:]

    # Remove Sacred Texts navigation artifacts
    nav_patterns = [
        r'^Sacred-Texts\s*$',
        r'^Internet Sacred Text Archive\s*$',
        r'^Buy this Book at Amazon\.com\s*$',
        r'^Buy CD-ROM\s*$',
        r'^\[?Sacred Texts?\]?\s*$',
        r'^\[?Index\]?\s*$',
        r'^Next:\s',
        r'^Previous:\s',
        r'^Contents\s*$',
        r'^\[p\.\s*\d+\]',  # Page references like [p. 42]
    ]
    compiled_nav = [re.compile(p, re.IGNORECASE) for p in nav_patterns]

    cleaned_lines = []
    for line in body_lines:
        stripped = line.strip()
        if any(pat.match(stripped) for pat in compiled_nav):
            continue
        cleaned_lines.append(line.rstrip())

    body = '\n'.join(cleaned_lines)

    # Collapse excessive blank lines
    body = re.sub(r'\n{4,}', '\n\n\n', body)
    body = body.strip()

    # Check if this is an index-only stub
    if len(cleaned_lines) < 200:
        word_count = len(body.split())
        if word_count < 500:
            meta["index_only"] = True

    return body, meta


# ============================================================
# ETCSL Normalizer
# ============================================================

def fix_word_joining(text: str) -> str:
    """
    Fix word-joining artifacts from HTML tag stripping.
    E.g. 'greatheaven' -> 'great heaven', 'SumerianLiterature' -> 'Sumerian Literature'
    """
    # Insert space before camelCase transitions
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    # Known compound fixes from ETCSL conversion
    fixes = {
        "greatheaven": "great heaven",
        "greatbelow": "great below",
        "netherworldd": "nether world",
        "theunderworld": "the underworld",
        "theoffice": "the office",
        "abandonedheaven": "abandoned heaven",
        "abandonedheart": "abandoned heart",
        "abandonedearth": "abandoned earth",
        "descendedto": "descended to",
        "sethermindon": "set her mind on",
        "goddessset": "goddess set",
        "SumerianLiterature": "Sumerian Literature",
        "consolidatedbibliography": "consolidated bibliography",
        "displayconventions": "display conventions",
    }
    for wrong, right in fixes.items():
        text = text.replace(wrong, right)

    return text


def normalize_etcsl(content: str, text_id: str) -> tuple:
    """
    Normalize an ETCSL downloaded file.
    Returns (normalized_text, metadata_dict).
    """
    meta = {"source_format": "etcsl", "text_id": text_id}

    lines = content.split('\n')
    body_start = 0

    # Parse header
    for i, line in enumerate(lines):
        if line.strip().startswith("====="):
            body_start = i + 1
            for hline in lines[:i]:
                if hline.startswith("Source:"):
                    meta["source_url"] = hline[7:].strip()
                elif hline.startswith("Corpus:"):
                    meta["corpus"] = hline[7:].strip()
                elif hline.startswith("Downloaded:"):
                    meta["download_date"] = hline[11:].strip()
            break

    body_lines = lines[body_start:]

    # Remove ETCSL navigation blocks
    nav_patterns = [
        r'^Catalogues:\s*$',
        r'^by date\s*$',
        r'^\|\s*$',
        r'^by number\s*$',
        r'^in full\s*$',
        r'^Website info:\s*$',
        r'^navigation help\s*$',
        r'^site description\s*$',
        r'^recent changes\s*$',
        r'^Project info:\s*$',
        r'^about the project\s*$',
        r'^credits and copyright\s*$',
        r'^links\s*$',
        r'^This composition:\s*$',
        r'^composite text\s*$',
        r'^bibliography\s*$',
    ]
    compiled_nav = [re.compile(p, re.IGNORECASE) for p in nav_patterns]

    # Find where the actual text starts (after navigation block)
    # Look for the first line range marker (e.g., "1-5") or the title repeated
    text_start = 0
    for i, line in enumerate(body_lines):
        stripped = line.strip()
        # ETCSL text typically starts with line range like "1-5" or "1."
        if re.match(r'^\d+[-.]', stripped):
            text_start = i
            break

    # If we found a line range marker, skip navigation before it
    if text_start > 0:
        body_lines = body_lines[text_start:]
    else:
        # Filter out nav lines
        body_lines = [
            line for line in body_lines
            if not any(pat.match(line.strip()) for pat in compiled_nav)
        ]

    body = '\n'.join(line.rstrip() for line in body_lines)

    # Fix word-joining artifacts
    body = fix_word_joining(body)

    # Collapse excessive blank lines
    body = re.sub(r'\n{4,}', '\n\n\n', body)
    body = body.strip()

    return body, meta


# ============================================================
# Generic Normalizer (for other-text, archive-text)
# ============================================================

def normalize_generic(content: str, text_id: str) -> tuple:
    """Normalize a generic text file with minimal processing."""
    meta = {"source_format": "other", "text_id": text_id}

    # Strip BOM
    if content.startswith('\ufeff'):
        content = content[1:]

    # Normalize line endings
    content = content.replace('\r\n', '\n').replace('\r', '\n')

    # Collapse excessive blank lines
    content = re.sub(r'\n{4,}', '\n\n\n', content)

    # Strip trailing whitespace
    content = '\n'.join(line.rstrip() for line in content.split('\n'))
    content = content.strip()

    return content, meta


# ============================================================
# Main Pipeline
# ============================================================

def detect_source_format(filepath: Path, content: str) -> str:
    """Detect source format (same logic as audit_corpus.py)."""
    name = filepath.name.lower()

    if name.startswith("pg") and "gutenberg" in name:
        return "gutenberg"
    if content.startswith("\ufeff") and "Project Gutenberg" in content[:2000]:
        return "gutenberg"
    if "Project Gutenberg" in content[:2000]:
        return "gutenberg"

    if name.startswith("sacred-texts_") or "sacred-texts" in name:
        return "sacred-texts"
    if content.startswith("Source: https://sacred-texts.com"):
        return "sacred-texts"
    if "sacred-texts.com" in content[:500]:
        return "sacred-texts"

    if name.startswith("etcsl_") or "etcsl" in name:
        return "etcsl"
    if "etcsl.orinst.ox.ac.uk" in content[:500]:
        return "etcsl"
    if "Electronic Text Corpus of Sumerian" in content[:500]:
        return "etcsl"

    return "other"


def normalize_file(filepath: Path, text_id: str, tradition: str,
                   catalog: dict) -> dict:
    """Normalize a single text file. Returns metadata dict."""
    content = read_text_file(filepath)
    source_format = detect_source_format(filepath, content)

    # Route to appropriate normalizer
    if source_format == "gutenberg":
        normalized, meta = normalize_gutenberg(content, text_id)
    elif source_format == "sacred-texts":
        normalized, meta = normalize_sacred_texts(content, text_id)
    elif source_format == "etcsl":
        normalized, meta = normalize_etcsl(content, text_id)
    else:
        normalized, meta = normalize_generic(content, text_id)

    # Skip index-only stubs
    if meta.get("index_only"):
        return {"status": "skipped", "reason": "index-only stub", **meta}

    # Skip very short results
    if len(normalized.split()) < 100:
        return {"status": "skipped", "reason": "too short after normalization", **meta}

    # Enrich metadata from catalog
    cat_entry = catalog.get(text_id, {})
    meta["title"] = meta.get("title") or cat_entry.get("title", text_id)
    meta["author"] = meta.get("author") or cat_entry.get("author", "Unknown")
    meta["tradition"] = tradition
    meta["date_composed"] = cat_entry.get("date_composed", "")
    meta["material_type"] = cat_entry.get("material_type", "")
    meta["original_file"] = filepath.name
    meta["normalization_date"] = datetime.utcnow().isoformat()
    meta["char_count"] = len(normalized)
    meta["line_count"] = len(normalized.split('\n'))
    meta["word_count"] = len(normalized.split())

    # Write normalized text
    norm_dir = filepath.parent.parent / "normalized"
    norm_dir.mkdir(exist_ok=True)

    # Use source format as suffix to distinguish multiple normalizations
    suffix = source_format.replace("-", "_")
    norm_filename = f"{text_id}_{suffix}.txt"
    meta_filename = f"{text_id}_{suffix}_metadata.json"

    norm_path = norm_dir / norm_filename
    meta_path = norm_dir / meta_filename

    with open(norm_path, "w", encoding="utf-8") as f:
        f.write(normalized)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    meta["status"] = "normalized"
    meta["normalized_path"] = str(norm_path)
    meta["metadata_path"] = str(meta_path)

    return meta


def run_normalization(target_text: str = None):
    """Run normalization on all or a specific text."""
    catalog = load_catalog()
    results = {"normalized": [], "skipped": [], "errors": []}

    total = 0
    success = 0
    skipped = 0
    errors = 0

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

            downloads_dir = text_dir / "downloads"
            if not downloads_dir.exists():
                continue

            for filepath in sorted(downloads_dir.iterdir()):
                if not filepath.is_file():
                    continue
                # Skip non-text files
                if filepath.suffix.lower() in (".pdf", ".lcpdf", ".md", ".gitkeep"):
                    continue

                total += 1
                try:
                    result = normalize_file(filepath, text_id, tradition, catalog)
                    if result.get("status") == "normalized":
                        success += 1
                        results["normalized"].append(result)
                        print(f"  [OK] {tradition}/{text_id}/{filepath.name} "
                              f"-> {result['word_count']} words")
                    elif result.get("status") == "skipped":
                        skipped += 1
                        results["skipped"].append(result)
                        print(f"  [SKIP] {tradition}/{text_id}/{filepath.name}: "
                              f"{result.get('reason', 'unknown')}")
                except Exception as e:
                    errors += 1
                    results["errors"].append({
                        "file": str(filepath),
                        "text_id": text_id,
                        "error": str(e),
                    })
                    print(f"  [ERR] {tradition}/{text_id}/{filepath.name}: {e}")

    # Summary
    print(f"\n{'='*60}")
    print(f"NORMALIZATION COMPLETE")
    print(f"{'='*60}")
    print(f"Total text files processed: {total}")
    print(f"Successfully normalized:    {success}")
    print(f"Skipped (stubs/short):      {skipped}")
    print(f"Errors:                     {errors}")

    # Save results
    results_path = SOURCES_DIR / "normalization_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to: {results_path}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Normalize mythic library texts")
    parser.add_argument("--text", help="Normalize a specific text by text_id")
    args = parser.parse_args()
    run_normalization(target_text=args.text)
