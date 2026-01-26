#!/usr/bin/env python3
"""
Corpus Audit Script for Mythic Library Phase 3.

Walks the texts/ directory tree and produces a per-file audit report:
- File size, line count, word count
- Source format detection (gutenberg / sacred-texts / etcsl / pdf / lcpdf)
- Encoding detection
- Usability assessment (flags index-only stubs, wrong-text downloads)
- Cross-references against master_catalog.csv

Output: sources/corpus_audit.json
"""

import csv
import io
import json
import os
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
MASTER_CATALOG = SOURCES_DIR / "master_catalog.csv"
OUTPUT_FILE = SOURCES_DIR / "corpus_audit.json"

# Reuse TEXT_SIGNATURES from bulk_download for content validation
TEXT_SIGNATURES = {
    "epic-of-gilgamesh": {"key_phrases": ["Enkidu", "Uruk", "Utnapishtim"], "min_size": 50000},
    "enuma-elis": {"key_phrases": ["Marduk", "Tiamat", "Apsu"], "min_size": 20000},
    "book-of-the-dead": {"key_phrases": ["Osiris", "Ra", "Anubis"], "min_size": 50000},
    "the-iliad": {"key_phrases": ["Achilles", "Hector", "Troy", "Agamemnon"], "min_size": 500000},
    "the-odyssey": {"key_phrases": ["Odysseus", "Penelope", "Ithaca", "Cyclops"], "min_size": 400000},
    "theogony": {"key_phrases": ["Zeus", "Titans", "Cronus"], "min_size": 20000},
    "beowulf": {"key_phrases": ["Grendel", "Hrothgar", "Heorot"], "min_size": 100000},
    "poetic-edda": {"key_phrases": ["Odin", "Thor", "Loki"], "min_size": 100000},
    "prose-edda": {"key_phrases": ["Odin", "Asgard", "Yggdrasil"], "min_size": 100000},
    "the-mabinogion": {"key_phrases": ["Pryderi", "Pwyll", "Rhiannon"], "min_size": 100000},
    "rigveda": {"key_phrases": ["Indra", "Agni", "Soma"], "min_size": 100000},
    "popol-vuh": {"key_phrases": ["Hunahpu", "Xbalanque", "Xibalba"], "min_size": 50000},
    "kojiki": {"key_phrases": ["Amaterasu", "Izanagi", "Izanami"], "min_size": 100000},
    "kalevala": {"key_phrases": ["Vainamoinen", "Ilmarinen", "Louhi"], "min_size": 200000},
    "divine-comedy": {"key_phrases": ["Dante", "Virgil", "Beatrice"], "min_size": 200000},
    "paradise-lost": {"key_phrases": ["Satan", "Adam", "Eve", "Eden"], "min_size": 200000},
}


def detect_source_format(filepath: Path, content: str = None) -> str:
    """Detect the source format of a downloaded file."""
    name = filepath.name.lower()
    suffix = filepath.suffix.lower()

    if suffix == ".pdf":
        return "pdf"
    if suffix == ".lcpdf":
        return "lcpdf"
    if suffix in (".gitkeep",):
        return "placeholder"
    if suffix == ".md":
        return "markdown"

    # For text files, check content
    if content is None:
        return "unknown"

    if name.startswith("pg") and "_gutenberg" in name:
        return "gutenberg"
    if "gutenberg" in name.lower():
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

    # Check for generic archive.org or other sources
    if "archive.org" in content[:500]:
        return "archive-text"

    return "other-text"


def detect_encoding(filepath: Path) -> str:
    """Detect file encoding."""
    try:
        with open(filepath, "rb") as f:
            raw = f.read(4)
        if raw[:3] == b'\xef\xbb\xbf':
            return "utf-8-bom"
        if raw[:2] in (b'\xff\xfe', b'\xfe\xff'):
            return "utf-16"
        # Try reading as UTF-8
        with open(filepath, "r", encoding="utf-8") as f:
            f.read(1000)
        return "utf-8"
    except UnicodeDecodeError:
        try:
            with open(filepath, "r", encoding="latin-1") as f:
                f.read(1000)
            return "latin-1"
        except Exception:
            return "unknown"


def assess_usability(filepath: Path, content: str, line_count: int,
                     word_count: int, source_format: str, text_id: str) -> dict:
    """Assess whether a file contains usable text content."""
    issues = []
    usable = True

    # Check for index-only stubs (Sacred Texts)
    if source_format == "sacred-texts" and line_count < 200:
        issues.append("index-only stub (< 200 lines)")
        usable = False

    # Check for very small files
    if source_format in ("gutenberg", "sacred-texts", "etcsl", "other-text"):
        file_size = filepath.stat().st_size
        if file_size < 1000:
            issues.append(f"very small file ({file_size} bytes)")
            usable = False

    # Check TEXT_SIGNATURES for wrong content
    # Normalize text_id for signature lookup (handle unicode)
    sig_id = text_id.replace("\u0101", "a").replace("\u016b", "u").replace("\u0113", "e")
    sig = TEXT_SIGNATURES.get(sig_id) or TEXT_SIGNATURES.get(text_id)
    if sig:
        phrases_found = sum(1 for p in sig["key_phrases"] if p.lower() in content.lower())
        if phrases_found == 0 and word_count > 100:
            issues.append(f"no key phrases found (expected: {sig['key_phrases']})")
            usable = False

    # Check for non-English content
    # Simple heuristic: if >30% of chars are non-ASCII, flag it
    if content:
        non_ascii = sum(1 for c in content[:5000] if ord(c) > 127)
        total = min(len(content), 5000)
        if total > 0 and non_ascii / total > 0.3:
            issues.append("high non-ASCII ratio (possibly non-English)")

    # DRM files
    if source_format == "lcpdf":
        issues.append("DRM-protected (not extractable)")
        usable = False

    # PDF files need extraction
    if source_format == "pdf":
        issues.append("PDF requires text extraction")

    return {"usable": usable, "issues": issues}


def load_master_catalog() -> dict:
    """Load master catalog as dict keyed by text_id."""
    catalog = {}
    try:
        with open(MASTER_CATALOG, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                catalog[row["text_id"]] = row
    except Exception as e:
        print(f"Warning: Could not load master catalog: {e}")
    return catalog


def audit_file(filepath: Path, text_id: str, tradition: str) -> dict:
    """Audit a single file."""
    result = {
        "path": str(filepath),
        "filename": filepath.name,
        "text_id": text_id,
        "tradition": tradition,
        "size_bytes": filepath.stat().st_size,
        "extension": filepath.suffix.lower(),
    }

    # For non-text files, limited audit
    if filepath.suffix.lower() in (".pdf", ".lcpdf"):
        result["source_format"] = "pdf" if filepath.suffix.lower() == ".pdf" else "lcpdf"
        result["encoding"] = "binary"
        result["line_count"] = 0
        result["word_count"] = 0
        usability = assess_usability(filepath, "", 0, 0, result["source_format"], text_id)
        result.update(usability)
        return result

    if filepath.suffix.lower() in (".md", ".gitkeep"):
        result["source_format"] = "markdown" if filepath.suffix.lower() == ".md" else "placeholder"
        result["encoding"] = "utf-8"
        result["line_count"] = 0
        result["word_count"] = 0
        result["usable"] = False
        result["issues"] = ["not a text file"]
        return result

    # Text file audit
    encoding = detect_encoding(filepath)
    result["encoding"] = encoding

    try:
        enc = "utf-8" if encoding in ("utf-8", "utf-8-bom") else encoding
        if enc == "unknown":
            enc = "utf-8"
        with open(filepath, "r", encoding=enc, errors="replace") as f:
            content = f.read()
    except Exception as e:
        result["source_format"] = "error"
        result["line_count"] = 0
        result["word_count"] = 0
        result["usable"] = False
        result["issues"] = [f"read error: {e}"]
        return result

    lines = content.split("\n")
    result["line_count"] = len(lines)
    result["word_count"] = len(content.split())
    result["source_format"] = detect_source_format(filepath, content)

    usability = assess_usability(
        filepath, content, result["line_count"],
        result["word_count"], result["source_format"], text_id
    )
    result.update(usability)

    return result


def run_audit():
    """Run the full corpus audit."""
    catalog = load_master_catalog()
    audit_results = {
        "summary": {},
        "texts": {},
        "files": [],
        "issues": [],
    }

    # Counters
    total_files = 0
    usable_files = 0
    format_counts = {}
    tradition_counts = {}
    total_size = 0

    # Walk the texts directory
    if not TEXTS_DIR.exists():
        print(f"Error: texts directory not found at {TEXTS_DIR}")
        sys.exit(1)

    for tradition_dir in sorted(TEXTS_DIR.iterdir()):
        if not tradition_dir.is_dir():
            continue
        tradition = tradition_dir.name

        for text_dir in sorted(tradition_dir.iterdir()):
            if not text_dir.is_dir():
                continue
            text_id = text_dir.name

            text_entry = {
                "text_id": text_id,
                "tradition": tradition,
                "catalog_entry": text_id in catalog,
                "files": [],
                "has_usable_text": False,
                "best_file": None,
            }

            # Check downloads/ subdirectory
            downloads_dir = text_dir / "downloads"
            if not downloads_dir.exists():
                text_entry["files"] = []
                audit_results["issues"].append(
                    f"{tradition}/{text_id}: no downloads/ directory"
                )
            else:
                for filepath in sorted(downloads_dir.iterdir()):
                    if not filepath.is_file():
                        continue

                    file_result = audit_file(filepath, text_id, tradition)
                    text_entry["files"].append(file_result)
                    audit_results["files"].append(file_result)

                    total_files += 1
                    total_size += file_result["size_bytes"]
                    fmt = file_result.get("source_format", "unknown")
                    format_counts[fmt] = format_counts.get(fmt, 0) + 1

                    if file_result.get("usable", False):
                        usable_files += 1
                        text_entry["has_usable_text"] = True

                    if file_result.get("issues"):
                        for issue in file_result["issues"]:
                            audit_results["issues"].append(
                                f"{tradition}/{text_id}/{filepath.name}: {issue}"
                            )

            # Select best usable text file
            usable_texts = [
                f for f in text_entry["files"]
                if f.get("usable") and f["source_format"] in
                ("gutenberg", "sacred-texts", "etcsl", "other-text", "archive-text")
            ]
            if usable_texts:
                # Prefer gutenberg, then by word count
                def score(f):
                    fmt_priority = {
                        "gutenberg": 4,
                        "archive-text": 3,
                        "other-text": 2,
                        "sacred-texts": 1,
                        "etcsl": 1,
                    }
                    return (fmt_priority.get(f["source_format"], 0), f.get("word_count", 0))
                best = max(usable_texts, key=score)
                text_entry["best_file"] = best["path"]

            tradition_counts[tradition] = tradition_counts.get(tradition, 0) + 1
            audit_results["texts"][f"{tradition}/{text_id}"] = text_entry

    # Check catalog coverage
    cataloged_ids = set(catalog.keys())
    audited_ids = set()
    for key, entry in audit_results["texts"].items():
        audited_ids.add(entry["text_id"])

    missing_from_catalog = audited_ids - cataloged_ids
    missing_from_disk = cataloged_ids - audited_ids

    # Summary
    audit_results["summary"] = {
        "total_files": total_files,
        "usable_text_files": usable_files,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 1),
        "format_counts": format_counts,
        "traditions": len(tradition_counts),
        "tradition_counts": tradition_counts,
        "texts_with_usable_content": sum(
            1 for t in audit_results["texts"].values() if t["has_usable_text"]
        ),
        "texts_without_usable_content": sum(
            1 for t in audit_results["texts"].values() if not t["has_usable_text"]
        ),
        "total_texts_on_disk": len(audit_results["texts"]),
        "total_texts_in_catalog": len(catalog),
        "missing_from_catalog": sorted(missing_from_catalog),
        "missing_from_disk": sorted(missing_from_disk),
        "total_issues": len(audit_results["issues"]),
    }

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2, ensure_ascii=False)

    # Print summary
    s = audit_results["summary"]
    print(f"\n{'='*60}")
    print(f"MYTHIC LIBRARY CORPUS AUDIT")
    print(f"{'='*60}")
    print(f"Total files:              {s['total_files']}")
    print(f"Usable text files:        {s['usable_text_files']}")
    print(f"Total size:               {s['total_size_mb']} MB")
    print(f"Traditions:               {s['traditions']}")
    print(f"Texts with usable content: {s['texts_with_usable_content']}")
    print(f"Texts without usable content: {s['texts_without_usable_content']}")
    print(f"Total issues:             {s['total_issues']}")
    print(f"\nFormat breakdown:")
    for fmt, count in sorted(format_counts.items(), key=lambda x: -x[1]):
        print(f"  {fmt:20s} {count:4d}")
    print(f"\nOutput: {OUTPUT_FILE}")

    if s["missing_from_disk"]:
        print(f"\nTexts in catalog but not on disk ({len(s['missing_from_disk'])}):")
        for tid in s["missing_from_disk"][:10]:
            print(f"  - {tid}")
        if len(s["missing_from_disk"]) > 10:
            print(f"  ... and {len(s['missing_from_disk']) - 10} more")

    # Print top issues
    issue_types = {}
    for issue in audit_results["issues"]:
        # Extract issue type (after last colon)
        parts = issue.split(": ", 2)
        if len(parts) >= 2:
            itype = parts[-1].split("(")[0].strip()
            issue_types[itype] = issue_types.get(itype, 0) + 1

    if issue_types:
        print(f"\nTop issue types:")
        for itype, count in sorted(issue_types.items(), key=lambda x: -x[1])[:10]:
            print(f"  {count:4d} x {itype}")

    return audit_results


if __name__ == "__main__":
    run_audit()
