#!/usr/bin/env python3
"""
Bulk download script for Mythic Library.

Downloads texts from Internet Archive, Project Gutenberg, and Sacred Texts.
Respects rate limits and logs all activity.

Usage:
    python scripts/bulk_download.py                    # Download all
    python scripts/bulk_download.py --text gilgamesh   # Download one text
    python scripts/bulk_download.py --source gutenberg # Download from one source
    python scripts/bulk_download.py --dry-run          # Show what would download
"""

import argparse
import io
import sys

# Fix Windows console encoding for Unicode characters
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, quote_plus

import requests
from bs4 import BeautifulSoup

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SOURCES_DIR = PROJECT_ROOT / "sources"
TEXTS_DIR = PROJECT_ROOT / "texts"
CURATED_SOURCES = SOURCES_DIR / "curated_sources.json"
MASTER_CATALOG = SOURCES_DIR / "master_catalog.csv"
DOWNLOAD_LOG = SOURCES_DIR / "download_log.json"

# Rate limiting (be respectful to servers)
RATE_LIMITS = {
    "archive.org": 2.0,      # 2 seconds between requests
    "gutenberg.org": 1.0,    # 1 second
    "sacred-texts.com": 1.5, # 1.5 seconds
    "perseus.tufts.edu": 2.0,
    "default": 1.5
}

# User agent
USER_AGENT = "MythicLibrary/1.0 (Educational; Public Domain Text Collection)"

# Session for connection reuse
session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})


def get_rate_limit(url: str) -> float:
    """Get rate limit for a domain."""
    domain = urlparse(url).netloc
    for key, limit in RATE_LIMITS.items():
        if key in domain:
            return limit
    return RATE_LIMITS["default"]


def load_curated_sources() -> dict:
    """Load the curated sources catalog."""
    with open(CURATED_SOURCES, "r", encoding="utf-8") as f:
        return json.load(f)


def load_master_catalog() -> dict:
    """Load master catalog as dict keyed by text_id."""
    import csv
    catalog = {}
    with open(MASTER_CATALOG, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            catalog[row["text_id"]] = row
    return catalog


def load_download_log() -> dict:
    """Load download log."""
    if DOWNLOAD_LOG.exists():
        with open(DOWNLOAD_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"downloads": {}, "errors": [], "last_run": None}


def save_download_log(log: dict):
    """Save download log."""
    log["last_run"] = datetime.now().isoformat()
    with open(DOWNLOAD_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def get_text_dir(text_id: str, tradition: str) -> Path:
    """Get directory for a text's downloads."""
    return TEXTS_DIR / tradition / text_id / "downloads"


def sanitize_filename(name: str) -> str:
    """Make a string safe for use as filename."""
    # Remove or replace problematic characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', '-', name)
    name = name.strip('-.')
    return name[:100]  # Limit length


def compute_checksum(filepath: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


# =============================================================================
# Content Validation
# =============================================================================

# Key phrases that MUST appear in each text to verify authenticity
TEXT_SIGNATURES = {
    "epic-of-gilgamesh": {
        "key_phrases": ["Enkidu", "Uruk", "Utnapishtim"],
        "min_size": 50000,
    },
    "enuma-elis": {
        "key_phrases": ["Marduk", "Tiamat", "Apsu"],
        "min_size": 20000,
    },
    "book-of-the-dead": {
        "key_phrases": ["Osiris", "Ra", "Anubis"],
        "min_size": 50000,
    },
    "the-iliad": {
        "key_phrases": ["Achilles", "Hector", "Troy", "Agamemnon"],
        "min_size": 500000,
    },
    "the-odyssey": {
        "key_phrases": ["Odysseus", "Penelope", "Ithaca", "Cyclops"],
        "min_size": 400000,
    },
    "theogony": {
        "key_phrases": ["Zeus", "Titans", "Cronus"],
        "min_size": 20000,
    },
    "aesops-fables": {
        "key_phrases": ["fox", "lion", "moral"],
        "min_size": 50000,
    },
    "beowulf": {
        "key_phrases": ["Grendel", "Hrothgar", "Heorot"],
        "min_size": 100000,
    },
    "poetic-edda": {
        "key_phrases": ["Odin", "Thor", "Loki"],
        "min_size": 100000,
    },
    "prose-edda": {
        "key_phrases": ["Odin", "Asgard", "Yggdrasil"],
        "min_size": 100000,
    },
    "the-mabinogion": {
        "key_phrases": ["Pryderi", "Pwyll", "Rhiannon"],
        "min_size": 100000,
    },
    "rigveda": {
        "key_phrases": ["Indra", "Agni", "Soma"],
        "min_size": 100000,
    },
    "mahabharata": {
        "key_phrases": ["Arjuna", "Krishna", "Pandava"],
        "min_size": 100000,
    },
    "ramayana": {
        "key_phrases": ["Rama", "Sita", "Hanuman", "Ravana"],
        "min_size": 100000,
    },
    "one-thousand-and-one-nights": {
        "key_phrases": ["Scheherazade", "Shahryar"],
        "min_size": 100000,
    },
    "divine-comedy": {
        "key_phrases": ["Dante", "Virgil", "Beatrice", "Inferno"],
        "min_size": 200000,
    },
    "paradise-lost": {
        "key_phrases": ["Satan", "Adam", "Eve", "Eden"],
        "min_size": 200000,
    },
    "kalevala": {
        "key_phrases": ["Vainamoinen", "Ilmarinen", "Louhi"],
        "min_size": 200000,
    },
    "popol-vuh": {
        "key_phrases": ["Hunahpu", "Xbalanque"],
        "min_size": 30000,
    },
    "kojiki": {
        "key_phrases": ["Amaterasu", "Izanagi", "Izanami"],
        "min_size": 100000,
    },
    "journey-to-the-west": {
        "key_phrases": ["Monkey", "Tripitaka", "Pigsy"],
        "min_size": 100000,
    },
    "grimms-fairy-tales": {
        "key_phrases": ["once upon a time", "happily ever after"],
        "min_size": 100000,
    },
    "le-morte-darthur": {
        "key_phrases": ["Arthur", "Lancelot", "Guinevere", "Excalibur"],
        "min_size": 500000,
    },
    "the-golden-bough": {
        "key_phrases": ["ritual", "magic", "primitive"],
        "min_size": 500000,
    },
}


def validate_download(filepath: Path, text_id: str) -> dict:
    """
    Validate a downloaded file for authenticity.

    Returns validation result with pass/fail and details.
    """
    result = {
        "valid": False,
        "checks": {},
        "warnings": [],
    }

    if not filepath.exists():
        result["error"] = "File does not exist"
        return result

    size = filepath.stat().st_size
    result["size"] = size

    # Basic size check (reject tiny files that are likely errors)
    if size < 500:
        result["error"] = f"File too small ({size} bytes) - likely an error page"
        return result

    result["checks"]["min_size_500"] = True

    # For text files, check content
    if filepath.suffix.lower() in [".txt", ".html", ".htm"]:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            result["error"] = f"Could not read file: {e}"
            return result

        content_lower = content.lower()

        # Check for error pages (only in first 500 chars, more specific patterns)
        error_indicators = [
            "404 not found",
            "page not found",
            "access denied",
            "403 forbidden",
            "error occurred",
            "server error",
            "<!doctype html",  # HTML error pages when expecting text
        ]
        first_500 = content_lower[:500]
        for indicator in error_indicators:
            # Skip HTML check if it's from sacred-texts (which is HTML converted to text)
            if indicator == "<!doctype html" and "sacred-texts" in str(filepath):
                continue
            if indicator in first_500:
                result["error"] = f"File appears to be an error page (contains '{indicator}')"
                return result

        result["checks"]["not_error_page"] = True

        # Check text-specific signatures
        if text_id in TEXT_SIGNATURES:
            sig = TEXT_SIGNATURES[text_id]

            # Check minimum size
            min_size = sig.get("min_size", 10000)
            if size < min_size:
                result["warnings"].append(f"File smaller than expected ({size} < {min_size} bytes)")
            result["checks"]["expected_size"] = size >= min_size

            # Check key phrases
            key_phrases = sig.get("key_phrases", [])
            if key_phrases:
                found = []
                missing = []
                for phrase in key_phrases:
                    if phrase.lower() in content_lower:
                        found.append(phrase)
                    else:
                        missing.append(phrase)

                result["phrases_found"] = found
                result["phrases_missing"] = missing

                # Require at least 50% of phrases
                match_ratio = len(found) / len(key_phrases)
                result["checks"]["key_phrases"] = match_ratio >= 0.5

                if missing:
                    result["warnings"].append(f"Missing phrases: {missing}")

    # For PDFs, just check size (can't easily read content)
    elif filepath.suffix.lower() == ".pdf":
        if text_id in TEXT_SIGNATURES:
            min_size = TEXT_SIGNATURES[text_id].get("min_size", 50000)
            result["checks"]["expected_size"] = size >= min_size
            if size < min_size:
                result["warnings"].append(f"PDF smaller than expected ({size} < {min_size} bytes)")
        result["checks"]["is_pdf"] = True

    # Overall validation
    if result["checks"]:
        # Valid if all checks pass (or if we only have warnings)
        result["valid"] = all(result["checks"].values())
    else:
        # No specific checks, just verify file exists and isn't tiny
        result["valid"] = size >= 500

    return result


# =============================================================================
# Internet Archive Downloads
# =============================================================================

def extract_ia_identifier(url: str) -> str | None:
    """Extract Internet Archive identifier from URL."""
    # https://archive.org/details/IDENTIFIER
    # https://archive.org/download/IDENTIFIER/file.pdf
    match = re.search(r'archive\.org/(?:details|download)/([^/\s?]+)', url)
    return match.group(1) if match else None


def get_ia_download_url(identifier: str, prefer_pdf: bool = True) -> tuple[str, str] | None:
    """Get direct download URL for an Internet Archive item."""
    metadata_url = f"https://archive.org/metadata/{identifier}"

    try:
        response = session.get(metadata_url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"    Error fetching IA metadata: {e}")
        return None

    files = data.get("files", [])

    if not files:
        print(f"    No files in metadata for: {identifier}")
        return None

    # Priority: PDF > Text > DJVU > EPUB
    # Note: IA format field can be "PDF", "Text PDF", "DjVu", etc.
    format_priority = ["pdf", "text", "djvu", "epub"] if prefer_pdf else ["text", "pdf", "djvu", "epub"]

    for fmt in format_priority:
        for f in files:
            file_format = f.get("format", "").lower()
            filename = f.get("name", "").lower()

            # Match by format field containing the type, or by file extension
            if fmt in file_format or filename.endswith(f".{fmt}"):
                # Skip derivative files, compressed files, and metadata
                if any(x in filename for x in ["_chocr", "_djvu.txt", "_hocr", "_meta", "_files", ".torrent", "_thumb", "_scandata"]):
                    continue
                # Skip compressed versions
                if filename.endswith(".gz") or filename.endswith(".zip"):
                    continue

                actual_filename = f["name"]
                download_url = f"https://archive.org/download/{identifier}/{quote_plus(actual_filename)}"
                return download_url, actual_filename

    # Fallback: any file that looks like primary content
    for f in files:
        name = f.get("name", "").lower()
        if any(name.endswith(ext) for ext in [".pdf", ".txt", ".djvu", ".epub"]):
            # Skip derivative files
            if any(x in name for x in ["_chocr", "_djvu.txt", "_hocr", "_meta", "_files"]):
                continue
            filename = f["name"]
            download_url = f"https://archive.org/download/{identifier}/{quote_plus(filename)}"
            return download_url, filename

    print(f"    No suitable download file found in {len(files)} files")
    return None


def download_from_ia(url: str, output_dir: Path, source_info: dict) -> dict | None:
    """Download a file from Internet Archive."""
    identifier = extract_ia_identifier(url)
    if not identifier:
        print(f"    Could not extract IA identifier from: {url}")
        return None

    result = get_ia_download_url(identifier)
    if not result:
        print(f"    No downloadable file found for: {identifier}")
        return None

    download_url, filename = result

    # Create filename with translator info
    translator = source_info.get("translator") or "unknown"
    translator_slug = sanitize_filename(translator)[:30]
    ext = Path(filename).suffix
    output_filename = f"{identifier}_{translator_slug}{ext}"
    output_path = output_dir / output_filename

    if output_path.exists():
        print(f"    Already exists: {output_filename}")
        return {
            "status": "exists",
            "path": str(output_path),
            "filename": output_filename
        }

    print(f"    Downloading: {filename}")

    try:
        response = session.get(download_url, stream=True, timeout=120)
        response.raise_for_status()

        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        checksum = compute_checksum(output_path)
        size = output_path.stat().st_size

        print(f"    Saved: {output_filename} ({size:,} bytes)")

        return {
            "status": "downloaded",
            "path": str(output_path),
            "filename": output_filename,
            "checksum": checksum,
            "size": size,
            "source_url": url,
            "download_url": download_url
        }

    except Exception as e:
        print(f"    Download failed: {e}")
        return {"status": "error", "error": str(e)}


# =============================================================================
# Project Gutenberg Downloads
# =============================================================================

def extract_gutenberg_id(url: str) -> int | None:
    """Extract Gutenberg book ID from URL."""
    # https://www.gutenberg.org/ebooks/12345
    match = re.search(r'gutenberg\.org/ebooks/(\d+)', url)
    return int(match.group(1)) if match else None


def get_gutenberg_download_url(book_id: int) -> tuple[str, str] | None:
    """Get direct download URL for a Gutenberg book."""
    # Try the Gutendex API first
    api_url = f"https://gutendex.com/books/{book_id}"

    try:
        response = session.get(api_url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"    Error fetching Gutenberg metadata: {e}")
        return None

    formats = data.get("formats", {})

    # Priority: plain text UTF-8 > plain text > HTML > PDF
    format_priority = [
        ("text/plain; charset=utf-8", ".txt"),
        ("text/plain; charset=us-ascii", ".txt"),
        ("text/plain", ".txt"),
        ("text/html; charset=utf-8", ".html"),
        ("text/html", ".html"),
        ("application/pdf", ".pdf"),
    ]

    for mime_type, ext in format_priority:
        if mime_type in formats:
            url = formats[mime_type]
            # Skip zip files
            if not url.endswith(".zip"):
                return url, ext

    return None


def download_from_gutenberg(url: str, output_dir: Path, source_info: dict) -> dict | None:
    """Download a file from Project Gutenberg."""
    book_id = extract_gutenberg_id(url)
    if not book_id:
        print(f"    Could not extract Gutenberg ID from: {url}")
        return None

    result = get_gutenberg_download_url(book_id)
    if not result:
        print(f"    No downloadable file found for: pg{book_id}")
        return None

    download_url, ext = result

    # Create filename
    translator = source_info.get("translator") or ""
    translator_slug = sanitize_filename(translator)[:30] if translator else "gutenberg"
    output_filename = f"pg{book_id}_{translator_slug}{ext}"
    output_path = output_dir / output_filename

    if output_path.exists():
        print(f"    Already exists: {output_filename}")
        return {
            "status": "exists",
            "path": str(output_path),
            "filename": output_filename
        }

    print(f"    Downloading: pg{book_id}{ext}")

    try:
        response = session.get(download_url, timeout=60)
        response.raise_for_status()

        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(response.content)

        checksum = compute_checksum(output_path)
        size = output_path.stat().st_size

        print(f"    Saved: {output_filename} ({size:,} bytes)")

        return {
            "status": "downloaded",
            "path": str(output_path),
            "filename": output_filename,
            "checksum": checksum,
            "size": size,
            "source_url": url,
            "download_url": download_url
        }

    except Exception as e:
        print(f"    Download failed: {e}")
        return {"status": "error", "error": str(e)}


# =============================================================================
# ETCSL (Electronic Text Corpus of Sumerian Literature) Downloads
# =============================================================================

def download_from_etcsl(url: str, output_dir: Path, source_info: dict) -> dict | None:
    """Download from ETCSL (Oxford Sumerian corpus)."""

    print(f"    Fetching ETCSL: {url}")

    try:
        response = session.get(url, timeout=60)
        response.raise_for_status()
    except Exception as e:
        print(f"    Fetch failed: {e}")
        return {"status": "error", "error": str(e)}

    # Parse and clean HTML
    soup = BeautifulSoup(response.content, "lxml")

    # Remove navigation elements
    for element in soup(["script", "style", "nav", "header", "footer"]):
        element.decompose()

    # Get text content
    text = soup.get_text(separator="\n", strip=True)

    # Create filename from URL
    path_parts = urlparse(url).path.strip("/").replace("/", "_")
    if not path_parts:
        path_parts = "index"
    translator = source_info.get("translator") or "ETCSL"
    translator_slug = sanitize_filename(translator)[:20]
    output_filename = f"etcsl_{path_parts}_{translator_slug}.txt"
    output_path = output_dir / output_filename

    if output_path.exists():
        print(f"    Already exists: {output_filename}")
        return {
            "status": "exists",
            "path": str(output_path),
            "filename": output_filename
        }

    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Source: {url}\n")
        f.write(f"Corpus: Electronic Text Corpus of Sumerian Literature (Oxford)\n")
        f.write(f"Downloaded: {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        f.write(text)

    checksum = compute_checksum(output_path)
    size = output_path.stat().st_size

    print(f"    Saved: {output_filename} ({size:,} bytes)")

    return {
        "status": "downloaded",
        "path": str(output_path),
        "filename": output_filename,
        "checksum": checksum,
        "size": size,
        "source_url": url,
        "format": "txt (from ETCSL html)"
    }


# =============================================================================
# Sacred Texts Downloads (HTML scraping)
# =============================================================================

def download_from_sacred_texts(url: str, output_dir: Path, source_info: dict) -> dict | None:
    """Download content from Sacred Texts (HTML pages)."""

    # Sacred texts has directory pages and single pages
    # For now, just download the main page content

    print(f"    Fetching: {url}")

    try:
        response = session.get(url, timeout=60)
        response.raise_for_status()
    except Exception as e:
        print(f"    Fetch failed: {e}")
        return {"status": "error", "error": str(e)}

    # Parse and clean HTML
    soup = BeautifulSoup(response.content, "lxml")

    # Remove script and style elements
    for element in soup(["script", "style", "nav", "header", "footer"]):
        element.decompose()

    # Get text content
    text = soup.get_text(separator="\n", strip=True)

    # Create filename from URL
    path_parts = urlparse(url).path.strip("/").replace("/", "_")
    if not path_parts:
        path_parts = "index"
    translator = source_info.get("translator") or ""
    translator_slug = sanitize_filename(translator)[:20] if translator else "sacred-texts"
    output_filename = f"sacred-texts_{path_parts}_{translator_slug}.txt"
    output_path = output_dir / output_filename

    if output_path.exists():
        print(f"    Already exists: {output_filename}")
        return {
            "status": "exists",
            "path": str(output_path),
            "filename": output_filename
        }

    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Source: {url}\n")
        f.write(f"Downloaded: {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        f.write(text)

    checksum = compute_checksum(output_path)
    size = output_path.stat().st_size

    print(f"    Saved: {output_filename} ({size:,} bytes)")

    return {
        "status": "downloaded",
        "path": str(output_path),
        "filename": output_filename,
        "checksum": checksum,
        "size": size,
        "source_url": url,
        "format": "txt (from html)"
    }


# =============================================================================
# Perseus Digital Library
# =============================================================================

def download_from_perseus(url: str, output_dir: Path, source_info: dict) -> dict | None:
    """Download from Perseus Digital Library."""
    # Perseus requires more complex handling - for now treat like sacred texts
    return download_from_sacred_texts(url, output_dir, source_info)


# =============================================================================
# Direct URL Downloads (for PDFs and other direct links)
# =============================================================================

def download_direct_url(url: str, output_dir: Path, source_info: dict) -> dict | None:
    """Download a file directly from a URL (for PDFs, text files, etc.)."""

    # Extract filename from URL
    parsed = urlparse(url)
    url_filename = Path(parsed.path).name

    # Determine extension
    ext = Path(url_filename).suffix.lower() if url_filename else ""
    if not ext:
        # Try to detect from format hint
        fmt = source_info.get("format", "").lower()
        if "pdf" in fmt:
            ext = ".pdf"
        elif "txt" in fmt or "text" in fmt:
            ext = ".txt"
        else:
            ext = ".pdf"  # Default assumption

    # Create output filename
    source_name = source_info.get("source_name", "direct")
    source_slug = sanitize_filename(source_name)[:30]
    translator = source_info.get("translator", "")
    translator_slug = sanitize_filename(translator)[:20] if translator else ""

    if translator_slug:
        output_filename = f"{source_slug}_{translator_slug}{ext}"
    else:
        output_filename = f"{source_slug}_{url_filename}" if url_filename else f"{source_slug}{ext}"

    output_path = output_dir / output_filename

    if output_path.exists():
        print(f"    Already exists: {output_filename}")
        return {
            "status": "exists",
            "path": str(output_path),
            "filename": output_filename
        }

    print(f"    Downloading directly: {url_filename or url[:50]}")

    try:
        response = session.get(url, timeout=120, allow_redirects=True)
        response.raise_for_status()

        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(response.content)

        checksum = compute_checksum(output_path)
        size = output_path.stat().st_size

        print(f"    Saved: {output_filename} ({size:,} bytes)")

        return {
            "status": "downloaded",
            "path": str(output_path),
            "filename": output_filename,
            "checksum": checksum,
            "size": size,
            "source_url": url,
            "download_method": "direct"
        }

    except Exception as e:
        print(f"    Direct download failed: {e}")
        return {"status": "error", "error": str(e)}


# =============================================================================
# Main Download Router
# =============================================================================

def download_source(source: dict, output_dir: Path) -> dict | None:
    """Download from any supported source."""
    url = source.get("source_url", "")
    source_name = source.get("source_name", "")

    if "archive.org" in url:
        return download_from_ia(url, output_dir, source)
    elif "gutenberg.org" in url:
        return download_from_gutenberg(url, output_dir, source)
    elif "sacred-texts.com" in url:
        return download_from_sacred_texts(url, output_dir, source)
    elif "perseus.tufts.edu" in url:
        return download_from_perseus(url, output_dir, source)
    elif "etcsl.orinst.ox.ac.uk" in url:
        return download_from_etcsl(url, output_dir, source)
    # Direct file URLs (PDFs, text files, etc.)
    elif url.lower().endswith(('.pdf', '.txt', '.epub', '.djvu')):
        return download_direct_url(url, output_dir, source)
    # Known academic/scholarly sources that serve direct files
    elif any(domain in url for domain in ['terebess.hu', 'hse.ru', 'latinamericanstudies.org', 'mesoweb.com']):
        return download_direct_url(url, output_dir, source)
    else:
        print(f"    Unsupported source: {source_name} ({url})")
        return {"status": "unsupported", "source": source_name}


def download_text(text_id: str, text_data: dict, catalog: dict, log: dict,
                  dry_run: bool = False, source_filter: str = None,
                  validate: bool = True) -> list[dict]:
    """Download all sources for a single text."""

    title = text_data.get("title", text_id)
    sources = text_data.get("sources", [])

    # Get tradition from catalog
    tradition = catalog.get(text_id, {}).get("tradition", "other")
    output_dir = get_text_dir(text_id, tradition)

    print(f"\n{'='*60}")
    print(f"{title} ({text_id})")
    print(f"{'='*60}")
    print(f"  Tradition: {tradition}")
    print(f"  Sources: {len(sources)}")
    print(f"  Output: {output_dir}")

    results = []

    for i, source in enumerate(sources, 1):
        source_name = source.get("source_name", "Unknown")
        source_url = source.get("source_url", "")

        # Apply source filter
        if source_filter:
            if source_filter.lower() not in source_name.lower() and \
               source_filter.lower() not in source_url.lower():
                continue

        print(f"\n  [{i}/{len(sources)}] {source_name}")
        print(f"  URL: {source_url}")

        if dry_run:
            print("    [DRY RUN] Would download")
            results.append({"status": "dry_run", "source": source_name})
            continue

        # Check if already downloaded
        log_key = f"{text_id}:{source_url}"
        if log_key in log.get("downloads", {}):
            existing = log["downloads"][log_key]
            if existing.get("status") == "downloaded":
                print(f"    Already logged as downloaded")
                results.append(existing)
                continue

        # Rate limiting
        rate_limit = get_rate_limit(source_url)
        time.sleep(rate_limit)

        # Download
        result = download_source(source, output_dir)

        if result:
            result["text_id"] = text_id
            result["source_name"] = source_name
            result["timestamp"] = datetime.now().isoformat()

            # Validate the download
            if validate and result.get("status") == "downloaded" and result.get("path"):
                filepath = Path(result["path"])
                validation = validate_download(filepath, text_id)
                result["validation"] = validation

                if validation.get("valid"):
                    print(f"    VALIDATED: Content verified")
                    if validation.get("warnings"):
                        for w in validation["warnings"]:
                            print(f"    WARNING: {w}")
                else:
                    print(f"    VALIDATION FAILED: {validation.get('error', 'Unknown reason')}")
                    if validation.get("checks"):
                        for check, passed in validation["checks"].items():
                            status = "PASS" if passed else "FAIL"
                            print(f"      [{status}] {check}")
                    result["status"] = "validation_failed"

            results.append(result)

            # Log the download
            if "downloads" not in log:
                log["downloads"] = {}
            log["downloads"][log_key] = result
            save_download_log(log)

    return results


def main():
    parser = argparse.ArgumentParser(description="Bulk download mythic texts")
    parser.add_argument("--text", "-t", help="Download specific text by ID")
    parser.add_argument("--source", "-s", help="Filter by source (gutenberg, archive, sacred-texts)")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show what would download")
    parser.add_argument("--limit", "-l", type=int, help="Limit number of texts to process")
    parser.add_argument("--skip-existing", action="store_true", default=True,
                        help="Skip already downloaded files (default: True)")

    args = parser.parse_args()

    print("=" * 60)
    print("MYTHIC LIBRARY BULK DOWNLOADER")
    print("=" * 60)

    # Load data
    curated = load_curated_sources()
    catalog = load_master_catalog()
    log = load_download_log()

    texts = curated.get("texts", {})
    print(f"Loaded {len(texts)} texts from curated sources")
    print(f"Loaded {len(catalog)} texts from master catalog")

    if args.dry_run:
        print("\n*** DRY RUN MODE - No files will be downloaded ***")

    # Filter texts
    if args.text:
        if args.text in texts:
            texts = {args.text: texts[args.text]}
        else:
            print(f"Text '{args.text}' not found in curated sources")
            sys.exit(1)

    # Process texts
    all_results = []
    processed = 0

    for text_id, text_data in texts.items():
        if args.limit and processed >= args.limit:
            print(f"\nReached limit of {args.limit} texts")
            break

        results = download_text(
            text_id, text_data, catalog, log,
            dry_run=args.dry_run,
            source_filter=args.source
        )
        all_results.extend(results)
        processed += 1

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    downloaded = sum(1 for r in all_results if r.get("status") == "downloaded")
    existing = sum(1 for r in all_results if r.get("status") == "exists")
    errors = sum(1 for r in all_results if r.get("status") == "error")
    unsupported = sum(1 for r in all_results if r.get("status") == "unsupported")
    validation_failed = sum(1 for r in all_results if r.get("status") == "validation_failed")
    validated = sum(1 for r in all_results
                    if r.get("validation", {}).get("valid") == True)

    print(f"Texts processed: {processed}")
    print(f"Files downloaded: {downloaded}")
    print(f"  - Validated OK: {validated}")
    print(f"  - Validation failed: {validation_failed}")
    print(f"Already existed: {existing}")
    print(f"Errors: {errors}")
    print(f"Unsupported: {unsupported}")

    if validation_failed > 0:
        print("\nValidation failures:")
        for r in all_results:
            if r.get("status") == "validation_failed":
                val = r.get("validation", {})
                print(f"  - {r.get('text_id', 'unknown')}: {val.get('error', 'check failures')}")

    if errors > 0:
        print("\nDownload errors:")
        for r in all_results:
            if r.get("status") == "error":
                print(f"  - {r.get('text_id', 'unknown')}: {r.get('error', 'unknown error')}")


if __name__ == "__main__":
    main()
