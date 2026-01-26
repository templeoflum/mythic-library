#!/usr/bin/env python3
"""
PDF Text Extraction for Mythic Library Phase 3.

Extracts text from PDF files using PyPDF2.
Skips .lcpdf (DRM-protected) files.
Flags extraction quality issues.

Usage:
    python scripts/normalize/extract_pdf.py                  # Extract all
    python scripts/normalize/extract_pdf.py --text the-iliad # Extract one

Output per text:
    texts/{tradition}/{text-id}/normalized/
        {text-id}_pdf_extract.txt
        {text-id}_pdf_metadata.json
"""

import argparse
import io
import json
import sys

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from datetime import datetime
from pathlib import Path

try:
    from PyPDF2 import PdfReader
except ImportError:
    print("Error: PyPDF2 required. Install with: pip install PyPDF2")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
TEXTS_DIR = PROJECT_ROOT / "texts"
SOURCES_DIR = PROJECT_ROOT / "sources"


def extract_pdf(filepath: Path) -> tuple:
    """
    Extract text from a PDF file.
    Returns (text, quality_report).
    """
    quality = {
        "total_pages": 0,
        "pages_with_text": 0,
        "total_chars": 0,
        "garbled_ratio": 0.0,
        "extraction_quality": "unknown",
    }

    try:
        reader = PdfReader(str(filepath))
        quality["total_pages"] = len(reader.pages)

        pages_text = []
        for i, page in enumerate(reader.pages):
            try:
                text = page.extract_text() or ""
                if text.strip():
                    quality["pages_with_text"] += 1
                pages_text.append(text)
            except Exception as e:
                pages_text.append(f"[Page {i+1}: extraction error - {e}]")

        full_text = "\n\n".join(pages_text)
        quality["total_chars"] = len(full_text)

        # Assess quality: check for garbled characters
        if full_text:
            # Count replacement chars and non-printable
            garbled = sum(1 for c in full_text
                        if c == '\ufffd' or (ord(c) < 32 and c not in '\n\r\t'))
            quality["garbled_ratio"] = round(garbled / len(full_text), 4) if full_text else 0

        # Quality rating
        if quality["total_pages"] == 0:
            quality["extraction_quality"] = "empty"
        elif quality["pages_with_text"] / quality["total_pages"] > 0.8:
            if quality["garbled_ratio"] < 0.01:
                quality["extraction_quality"] = "good"
            elif quality["garbled_ratio"] < 0.05:
                quality["extraction_quality"] = "fair"
            else:
                quality["extraction_quality"] = "poor"
        elif quality["pages_with_text"] / quality["total_pages"] > 0.3:
            quality["extraction_quality"] = "partial"
        else:
            quality["extraction_quality"] = "failed"

        return full_text, quality

    except Exception as e:
        quality["extraction_quality"] = "error"
        quality["error"] = str(e)
        return "", quality


def process_pdf(filepath: Path, text_id: str, tradition: str) -> dict:
    """Process a single PDF file."""
    text, quality = extract_pdf(filepath)

    meta = {
        "text_id": text_id,
        "tradition": tradition,
        "source_format": "pdf",
        "original_file": filepath.name,
        "extraction_date": datetime.utcnow().isoformat(),
        **quality,
    }

    if not text.strip() or quality["extraction_quality"] in ("empty", "failed", "error"):
        meta["status"] = "failed"
        return meta

    # Write extracted text
    norm_dir = filepath.parent.parent / "normalized"
    norm_dir.mkdir(exist_ok=True)

    # Use the original filename stem for clarity
    stem = filepath.stem
    extract_path = norm_dir / f"{text_id}_pdf_{stem}.txt"
    meta_path = norm_dir / f"{text_id}_pdf_{stem}_metadata.json"

    # Basic cleanup
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Remove excessive whitespace runs
    text = '\n'.join(line.rstrip() for line in text.split('\n'))

    meta["word_count"] = len(text.split())
    meta["line_count"] = len(text.split('\n'))
    meta["char_count"] = len(text)

    with open(extract_path, "w", encoding="utf-8") as f:
        f.write(text)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    meta["status"] = "extracted"
    meta["extract_path"] = str(extract_path)
    return meta


def run_extraction(target_text: str = None):
    """Run PDF extraction on all or a specific text."""
    results = {"extracted": [], "failed": [], "skipped": []}

    total_pdf = 0
    total_lcpdf = 0
    extracted = 0
    failed = 0

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

                if filepath.suffix.lower() == ".lcpdf":
                    total_lcpdf += 1
                    results["skipped"].append({
                        "file": str(filepath),
                        "text_id": text_id,
                        "reason": "DRM-protected (lcpdf)",
                    })
                    print(f"  [SKIP] {tradition}/{text_id}/{filepath.name}: DRM-protected")
                    continue

                if filepath.suffix.lower() != ".pdf":
                    continue

                total_pdf += 1
                try:
                    result = process_pdf(filepath, text_id, tradition)
                    if result.get("status") == "extracted":
                        extracted += 1
                        results["extracted"].append(result)
                        q = result["extraction_quality"]
                        print(f"  [OK] {tradition}/{text_id}/{filepath.name} "
                              f"-> {result['word_count']} words (quality: {q})")
                    else:
                        failed += 1
                        results["failed"].append(result)
                        print(f"  [FAIL] {tradition}/{text_id}/{filepath.name}: "
                              f"{result.get('extraction_quality', 'unknown')}")
                except Exception as e:
                    failed += 1
                    results["failed"].append({
                        "file": str(filepath),
                        "text_id": text_id,
                        "error": str(e),
                    })
                    print(f"  [ERR] {tradition}/{text_id}/{filepath.name}: {e}")

    # Summary
    print(f"\n{'='*60}")
    print(f"PDF EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"PDFs processed:    {total_pdf}")
    print(f"Successfully extracted: {extracted}")
    print(f"Failed:            {failed}")
    print(f"Skipped (lcpdf):   {total_lcpdf}")

    # Quality breakdown
    quality_counts = {}
    for r in results["extracted"]:
        q = r.get("extraction_quality", "unknown")
        quality_counts[q] = quality_counts.get(q, 0) + 1
    if quality_counts:
        print(f"\nExtraction quality:")
        for q, count in sorted(quality_counts.items()):
            print(f"  {q:12s} {count:4d}")

    # Save results
    results_path = SOURCES_DIR / "pdf_extraction_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to: {results_path}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract text from PDF files")
    parser.add_argument("--text", help="Extract from a specific text by text_id")
    args = parser.parse_args()
    run_extraction(target_text=args.text)
