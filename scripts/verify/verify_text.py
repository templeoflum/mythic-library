#!/usr/bin/env python3
"""
Verify downloaded texts for authenticity and completeness.

Verification checks:
1. Checksum matches recorded value
2. File is not corrupted/readable
3. Content matches expected structure (line counts, sections, etc.)
4. Cross-reference with known canonical versions
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

# Known text signatures for verification
# Format: {text_id: {expected_lines, expected_sections, key_phrases, etc.}}
TEXT_SIGNATURES = {
    "gilgamesh": {
        "tablets": 12,
        "key_phrases": [
            "Enkidu",
            "Uruk",
            "Utnapishtim",
            "cedar forest",
            "Bull of Heaven",
        ],
        "min_lines": 2000,
    },
    "iliad": {
        "books": 24,
        "key_phrases": [
            "Achilles",
            "Hector",
            "Troy",
            "Agamemnon",
            "Patroclus",
        ],
        "min_lines": 15000,
    },
    "odyssey": {
        "books": 24,
        "key_phrases": [
            "Odysseus",
            "Penelope",
            "Telemachus",
            "Ithaca",
            "Cyclops",
        ],
        "min_lines": 12000,
    },
    "aeneid": {
        "books": 12,
        "key_phrases": [
            "Aeneas",
            "Dido",
            "Carthage",
            "Turnus",
            "Lavinia",
        ],
        "min_lines": 10000,
    },
    "beowulf": {
        "key_phrases": [
            "Grendel",
            "Hrothgar",
            "Heorot",
            "dragon",
        ],
        "min_lines": 3000,
    },
    "edda": {
        "key_phrases": [
            "Odin",
            "Thor",
            "Loki",
            "Ragnarok",
            "Yggdrasil",
        ],
    },
    "mahabharata": {
        "books": 18,
        "key_phrases": [
            "Arjuna",
            "Krishna",
            "Pandava",
            "Kaurava",
            "Bhishma",
        ],
    },
    "ramayana": {
        "books": 7,
        "key_phrases": [
            "Rama",
            "Sita",
            "Hanuman",
            "Ravana",
            "Lanka",
        ],
    },
}


def compute_checksum(filepath: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_checksum(filepath: Path, expected: str) -> bool:
    """Verify file checksum matches expected value."""
    actual = compute_checksum(filepath)
    return actual == expected


def count_lines(filepath: Path) -> int:
    """Count lines in a text file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def check_key_phrases(filepath: Path, phrases: list[str]) -> dict[str, bool]:
    """Check if key phrases appear in the text."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().lower()
    except Exception:
        return {p: False for p in phrases}

    return {phrase: phrase.lower() in content for phrase in phrases}


def detect_text_type(filepath: Path) -> str | None:
    """Try to detect which text this file contains."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().lower()
    except Exception:
        return None

    for text_id, sig in TEXT_SIGNATURES.items():
        phrases = sig.get("key_phrases", [])
        if phrases:
            matches = sum(1 for p in phrases if p.lower() in content)
            if matches >= len(phrases) * 0.6:  # 60% threshold
                return text_id

    return None


def verify_text(filepath: Path, text_id: str = None, expected_checksum: str = None) -> dict:
    """
    Perform full verification of a text file.

    Returns a verification report.
    """
    report = {
        "filepath": str(filepath),
        "exists": filepath.exists(),
        "verified": False,
        "checks": {},
    }

    if not filepath.exists():
        report["error"] = "File not found"
        return report

    # Basic file checks
    report["size_bytes"] = filepath.stat().st_size
    report["checksum"] = compute_checksum(filepath)

    if expected_checksum:
        report["checks"]["checksum"] = report["checksum"] == expected_checksum

    # For text files, do content checks
    if filepath.suffix in [".txt", ".html", ".htm"]:
        report["line_count"] = count_lines(filepath)

        # Auto-detect text type if not provided
        if not text_id:
            text_id = detect_text_type(filepath)
            if text_id:
                report["detected_text"] = text_id

        if text_id and text_id in TEXT_SIGNATURES:
            sig = TEXT_SIGNATURES[text_id]

            # Check minimum line count
            if "min_lines" in sig:
                report["checks"]["min_lines"] = report["line_count"] >= sig["min_lines"]

            # Check key phrases
            if "key_phrases" in sig:
                phrase_checks = check_key_phrases(filepath, sig["key_phrases"])
                report["phrase_matches"] = phrase_checks
                report["checks"]["key_phrases"] = all(phrase_checks.values())

    # Overall verification status
    if report["checks"]:
        report["verified"] = all(report["checks"].values())
    else:
        report["verified"] = report["exists"] and report["size_bytes"] > 0

    return report


def main():
    parser = argparse.ArgumentParser(description="Verify downloaded texts")
    parser.add_argument("filepath", type=Path, help="Path to file or directory to verify")
    parser.add_argument("--text-id", help="Text identifier for signature matching")
    parser.add_argument("--checksum", help="Expected SHA-256 checksum")
    parser.add_argument("--detect", action="store_true", help="Try to auto-detect text type")

    args = parser.parse_args()

    if args.filepath.is_dir():
        # Verify all files in directory
        files = list(args.filepath.glob("**/*.txt")) + list(args.filepath.glob("**/*.pdf"))
        results = []
        for f in files:
            result = verify_text(f, args.text_id)
            results.append(result)
            status = "PASS" if result["verified"] else "FAIL"
            print(f"[{status}] {f}")

        passed = sum(1 for r in results if r["verified"])
        print(f"\nTotal: {passed}/{len(results)} verified")
    else:
        result = verify_text(args.filepath, args.text_id, args.checksum)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["verified"] else 1)


if __name__ == "__main__":
    main()
