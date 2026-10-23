"""
Provenance records for derived data files.

A script that writes derived data (data/motif_tags.json, data/entities.json,
...) can write a small sidecar next to it, <name>.provenance.json, saying
which inputs it was built from: a SHA-256 of each input file or file tree,
plus a few counts that are easy to read (the number of motifs in the index,
the number of segment files). scripts/check_published_numbers.py reads the
sidecars and reports when the current inputs no longer match.

Hashes normalise CRLF to LF, so a Windows and a Unix checkout of the same
commit give the same hash. Records hold no timestamps, so rebuilding from the
same inputs writes the same sidecar.
"""

from __future__ import annotations

import glob
import hashlib
import json
import re
from pathlib import Path

SIDECAR_SUFFIX = ".provenance.json"


def _file_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(_file_bytes(path)).hexdigest()


def file_fingerprint(path: Path) -> dict:
    """SHA-256 of one file."""
    return {"sha256": file_sha256(path)}


def tree_fingerprint(root: Path, pattern: str) -> dict:
    """
    SHA-256 over every file matching a glob pattern under root, in sorted
    order of relative path. Each file contributes its relative path and its
    own hash, so renames and edits both change the result.
    """
    paths = sorted(Path(p) for p in glob.glob(str(root / pattern), recursive=True)
                   if Path(p).is_file())
    digest = hashlib.sha256()
    for path in paths:
        rel = path.relative_to(root).as_posix()
        digest.update(rel.encode("utf-8") + b"\0" + file_sha256(path).encode("ascii") + b"\n")
    return {"sha256": digest.hexdigest(), "files": len(paths)}


# Inputs used by more than one generator, keyed by the name they are recorded under.

SEGMENT_FILES = "texts/*/*/segments/*.txt"
MOTIF_INDEX = "data/thompson_motif_index.json"
ACP_FILES = ["ACP/schema/primordials.jsonld"] + [
    f"ACP/{domain}/**/*.jsonld"
    for domain in ("archetypes", "divination", "psychology", "modern", "calibration")
]


def segments_input(root: Path) -> dict:
    return tree_fingerprint(root, SEGMENT_FILES)


def motif_index_input(root: Path) -> dict:
    path = root / MOTIF_INDEX
    record = file_fingerprint(path)
    with open(path, "r", encoding="utf-8") as f:
        record["motifs"] = len(json.load(f).get("motifs", {}))
    return record


def acp_input(root: Path) -> dict:
    """Combined fingerprint of the ACP files that integration/acp_loader.py reads."""
    digest = hashlib.sha256()
    files = 0
    for pattern in ACP_FILES:
        part = tree_fingerprint(root, pattern)
        digest.update(pattern.encode("utf-8") + b"\0" + part["sha256"].encode("ascii") + b"\n")
        files += part["files"]
    record = {"sha256": digest.hexdigest(), "files": files}
    version = acp_version(root)
    if version:
        record["version"] = version
    return record


def acp_version(root: Path) -> str | None:
    """The version on the ACP README badge, if there is one (a label only; the hash decides)."""
    readme = root / "ACP" / "README.md"
    if not readme.exists():
        return None
    match = re.search(r"badge/version-([0-9][0-9A-Za-z.\-]*?)-[a-z]+\)", readme.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def script_input(root: Path, rel_path: str) -> dict:
    return file_fingerprint(root / rel_path)


# What each tracked derived file is built from: sidecar path, generator,
# the outputs it covers, and how to fingerprint each input today.

DERIVED = {
    "motif tags": {
        "sidecar": "data/motif_tags" + SIDECAR_SUFFIX,
        "generator": "scripts/motif/tag_motifs.py",
        "outputs": ["data/motif_tags.json", "data/motif_distribution.json"],
        "inputs": {
            MOTIF_INDEX: motif_index_input,
            SEGMENT_FILES: segments_input,
            "scripts/motif/tag_motifs.py": lambda root: script_input(root, "scripts/motif/tag_motifs.py"),
        },
    },
    "entities": {
        "sidecar": "data/entities" + SIDECAR_SUFFIX,
        "generator": "scripts/extract/extract_entities.py",
        "outputs": ["data/entities.json", "data/entity_catalog.json"],
        "inputs": {
            SEGMENT_FILES: segments_input,
            "scripts/extract/extract_entities.py": lambda root: script_input(root, "scripts/extract/extract_entities.py"),
        },
    },
}

# The v2 suite records its inputs inside its own results file.
V2_RESULTS = "outputs/metrics/v2_validation_results.json"
V2_INPUTS = {
    "ACP": acp_input,
    MOTIF_INDEX: motif_index_input,
}


def current_inputs(root: Path, inputs: dict) -> dict:
    """Fingerprint each input as it is now. An input that isn't there is recorded as missing."""
    out = {}
    for name, fingerprint in inputs.items():
        try:
            out[name] = fingerprint(root)
        except FileNotFoundError:
            out[name] = {"missing": True}
    return out


def build_record(root: Path, name: str, text_filter: str | None = None) -> dict:
    """The provenance record for one DERIVED entry, from the files as they are now."""
    spec = DERIVED[name]
    return {
        "generator": spec["generator"],
        "text_filter": text_filter,
        "outputs": {out: file_fingerprint(root / out) for out in spec["outputs"]},
        "inputs": current_inputs(root, spec["inputs"]),
    }


def write_record(root: Path, name: str, text_filter: str | None = None) -> Path:
    """Write the sidecar for one DERIVED entry. Call after its outputs are written."""
    path = root / DERIVED[name]["sidecar"]
    record = build_record(root, name, text_filter)
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def read_record(path: Path) -> dict | None:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_inputs(recorded: dict, current: dict) -> list[dict]:
    """
    One row per input: "same", "CHANGED", "not recorded" (an input the record
    does not cover) or "missing now" (recorded, but can't be read today).
    """
    rows = []
    for name in sorted(set(recorded) | set(current)):
        was, now = recorded.get(name), current.get(name)
        if was is None:
            status = "not recorded"
        elif now is None:
            status = "missing now"
        else:
            status = "same" if was.get("sha256") == now.get("sha256") else "CHANGED"
        rows.append({"input": name, "recorded": was, "current": now, "status": status})
    return rows
