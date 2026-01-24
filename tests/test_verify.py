#!/usr/bin/env python3
"""Tests for text verification."""

import sys
import tempfile
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "verify"))

from verify_text import (
    compute_checksum,
    count_lines,
    check_key_phrases,
    detect_text_type,
    verify_text,
)


def test_compute_checksum():
    """Test checksum computation."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Hello, World!")
        f.flush()
        path = Path(f.name)

    checksum = compute_checksum(path)
    # SHA-256 of "Hello, World!"
    expected = "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
    assert checksum == expected, f"Expected {expected}, got {checksum}"
    path.unlink()
    print("test_compute_checksum: PASS")


def test_count_lines():
    """Test line counting."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Line 1\nLine 2\nLine 3\n")
        f.flush()
        path = Path(f.name)

    count = count_lines(path)
    assert count == 3, f"Expected 3 lines, got {count}"
    path.unlink()
    print("test_count_lines: PASS")


def test_check_key_phrases():
    """Test key phrase detection."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Enkidu was the friend of Gilgamesh in Uruk.")
        f.flush()
        path = Path(f.name)

    phrases = ["Enkidu", "Uruk", "Utnapishtim"]
    results = check_key_phrases(path, phrases)

    assert results["Enkidu"] is True
    assert results["Uruk"] is True
    assert results["Utnapishtim"] is False
    path.unlink()
    print("test_check_key_phrases: PASS")


def test_detect_text_type():
    """Test automatic text type detection."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        # Write content that should be detected as Iliad
        f.write("""
        The wrath of Achilles, sing, O goddess!
        Hector, breaker of horses, defender of Troy.
        Agamemnon, king of men, marshalled his forces.
        Patroclus donned the armor of his friend.
        """)
        f.flush()
        path = Path(f.name)

    detected = detect_text_type(path)
    assert detected == "iliad", f"Expected 'iliad', got '{detected}'"
    path.unlink()
    print("test_detect_text_type: PASS")


def test_verify_text():
    """Test full verification."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Test content for verification\n" * 100)
        f.flush()
        path = Path(f.name)

    result = verify_text(path)

    assert result["exists"] is True
    assert result["verified"] is True
    assert "checksum" in result
    assert result["line_count"] == 100
    path.unlink()
    print("test_verify_text: PASS")


def test_verify_nonexistent():
    """Test verification of nonexistent file."""
    path = Path("/nonexistent/file.txt")
    result = verify_text(path)

    assert result["exists"] is False
    assert result["verified"] is False
    print("test_verify_nonexistent: PASS")


if __name__ == "__main__":
    test_compute_checksum()
    test_count_lines()
    test_check_key_phrases()
    test_detect_text_type()
    test_verify_text()
    test_verify_nonexistent()
    print("\nAll tests passed!")
