#!/usr/bin/env python3
"""
Motif Tagging for Mythic Library Phase 3.

Tags text segments with Thompson Motif Index codes using keyword-based
matching with confidence scoring.

Usage:
    python scripts/motif/tag_motifs.py                  # Tag all
    python scripts/motif/tag_motifs.py --text the-iliad # Tag one

Output: data/motif_tags.json
"""

import argparse
import io
import json
import re
import sys

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
TEXTS_DIR = PROJECT_ROOT / "texts"
DATA_DIR = PROJECT_ROOT / "data"
SOURCES_DIR = PROJECT_ROOT / "sources"

MOTIF_INDEX_PATH = DATA_DIR / "thompson_motif_index.json"


def load_motif_index() -> dict:
    """Load the Thompson Motif Index."""
    with open(MOTIF_INDEX_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["motifs"]


def prepare_keyword_patterns(motifs: dict) -> list:
    """Compile keyword patterns for efficient matching."""
    prepared = []
    for code, motif in motifs.items():
        keywords = motif.get("keywords", [])
        if not keywords:
            continue

        # Compile patterns for each keyword
        patterns = []
        for kw in keywords:
            # Use word boundary matching
            pattern = re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
            patterns.append((kw, pattern))

        prepared.append({
            "code": code,
            "label": motif["label"],
            "category": motif["category"],
            "patterns": patterns,
            "keyword_count": len(keywords),
        })

    return prepared


def score_segment(text: str, prepared_motifs: list) -> list:
    """
    Score a text segment against all motifs.
    Returns list of (code, label, confidence, evidence) for matches above threshold.
    """
    text_lower = text.lower()
    word_count = len(text.split())
    matches = []

    for motif in prepared_motifs:
        evidence = []
        for kw, pattern in motif["patterns"]:
            found = pattern.findall(text)
            if found:
                evidence.append(kw)

        if not evidence:
            continue

        # Calculate confidence
        # Base: ratio of matched keywords to total keywords
        match_ratio = len(evidence) / motif["keyword_count"]

        # Bonus for multiple distinct keywords
        if len(evidence) >= 3:
            confidence = min(0.95, 0.5 + match_ratio * 0.5)
        elif len(evidence) >= 2:
            confidence = min(0.8, 0.3 + match_ratio * 0.5)
        else:
            confidence = min(0.5, 0.1 + match_ratio * 0.4)

        # Penalty for very short texts (less reliable)
        if word_count < 100:
            confidence *= 0.7

        # Boost for very long texts with many keyword hits
        if word_count > 1000 and len(evidence) >= 2:
            confidence = min(0.95, confidence * 1.1)

        # Minimum threshold
        if confidence >= 0.15:
            matches.append({
                "code": motif["code"],
                "label": motif["label"],
                "category": motif["category"],
                "confidence": round(confidence, 3),
                "evidence": evidence,
                "method": "keyword_match",
            })

    # Sort by confidence descending
    matches.sort(key=lambda x: -x["confidence"])
    return matches


def process_text(text_dir: Path, text_id: str, tradition: str,
                 prepared_motifs: list) -> dict:
    """Tag motifs for all segments of a text."""
    seg_dir = text_dir / "segments"
    seg_index_path = seg_dir / "segments.json"

    if not seg_index_path.exists():
        return {"status": "no_segments", "text_id": text_id}

    with open(seg_index_path, "r", encoding="utf-8") as f:
        seg_index = json.load(f)

    text_result = {
        "text_id": text_id,
        "tradition": tradition,
        "segments": [],
        "motif_summary": defaultdict(lambda: {"count": 0, "max_confidence": 0}),
        "total_tags": 0,
        "unique_motifs": set(),
    }

    for seg_info in seg_index["segments"]:
        seg_file = seg_dir / seg_info["file"]
        if not seg_file.exists():
            continue

        with open(seg_file, "r", encoding="utf-8") as f:
            content = f.read()

        matches = score_segment(content, prepared_motifs)

        if matches:
            seg_result = {
                "segment_id": seg_info["id"],
                "segment_label": seg_info["label"],
                "tag_count": len(matches),
                "tags": matches,
            }
            text_result["segments"].append(seg_result)
            text_result["total_tags"] += len(matches)

            for m in matches:
                code = m["code"]
                text_result["unique_motifs"].add(code)
                summary = text_result["motif_summary"][code]
                summary["count"] += 1
                summary["max_confidence"] = max(
                    summary["max_confidence"], m["confidence"]
                )
                summary["label"] = m["label"]

    # Convert for JSON
    text_result["unique_motif_count"] = len(text_result["unique_motifs"])
    text_result["unique_motifs"] = sorted(text_result["unique_motifs"])
    text_result["motif_summary"] = {
        k: dict(v) for k, v in text_result["motif_summary"].items()
    }
    text_result["status"] = "tagged"

    return text_result


def run_tagging(target_text: str = None):
    """Run motif tagging on all or a specific text."""
    motifs = load_motif_index()
    prepared = prepare_keyword_patterns(motifs)
    print(f"Loaded {len(prepared)} motif patterns")

    all_results = []
    total = 0
    success = 0

    # Global motif frequency
    global_motifs = defaultdict(lambda: {
        "texts": 0, "traditions": set(), "total_tags": 0, "max_confidence": 0
    })

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

            seg_dir = text_dir / "segments"
            if not seg_dir.exists():
                continue

            total += 1
            try:
                result = process_text(text_dir, text_id, tradition, prepared)
                all_results.append(result)

                if result["status"] == "tagged" and result["total_tags"] > 0:
                    success += 1
                    # Track global motif distribution
                    for code, info in result.get("motif_summary", {}).items():
                        gm = global_motifs[code]
                        gm["texts"] += 1
                        gm["traditions"].add(tradition)
                        gm["total_tags"] += info["count"]
                        gm["max_confidence"] = max(gm["max_confidence"], info["max_confidence"])
                        gm["label"] = info.get("label", "")

                    top = sorted(result["motif_summary"].items(),
                                key=lambda x: -x[1]["max_confidence"])[:3]
                    top_str = ", ".join(f"{c}:{v['label'][:20]}" for c, v in top)
                    print(f"  [{result['total_tags']:4d} tags, "
                          f"{result['unique_motif_count']:3d} motifs] "
                          f"{tradition}/{text_id}: {top_str}")
                else:
                    print(f"  [   0 tags] {tradition}/{text_id}")

            except Exception as e:
                print(f"  [ERR] {tradition}/{text_id}: {e}")

    # Save results
    tags_path = DATA_DIR / "motif_tags.json"
    with open(tags_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    # Build cross-text motif distribution
    motif_distribution = {}
    for code, info in sorted(global_motifs.items(),
                             key=lambda x: -x[1]["texts"]):
        motif_distribution[code] = {
            "code": code,
            "label": info["label"],
            "text_count": info["texts"],
            "tradition_count": len(info["traditions"]),
            "traditions": sorted(info["traditions"]),
            "total_segment_tags": info["total_tags"],
            "max_confidence": round(info["max_confidence"], 3),
        }

    dist_path = DATA_DIR / "motif_distribution.json"
    with open(dist_path, "w", encoding="utf-8") as f:
        json.dump(motif_distribution, f, indent=2, ensure_ascii=False)

    # Summary
    print(f"\n{'='*60}")
    print(f"MOTIF TAGGING COMPLETE")
    print(f"{'='*60}")
    print(f"Texts processed:     {total}")
    print(f"Texts with motifs:   {success}")
    print(f"Unique motifs found: {len(global_motifs)}")
    total_tags = sum(r.get("total_tags", 0) for r in all_results)
    print(f"Total tags assigned: {total_tags}")

    # Top motifs by cross-tradition presence
    print(f"\nTop 20 motifs by tradition count:")
    for code, info in list(motif_distribution.items())[:20]:
        traditions = ", ".join(info["traditions"][:5])
        if info["tradition_count"] > 5:
            traditions += f" +{info['tradition_count']-5} more"
        print(f"  {code:8s} | {info['label']:35s} | "
              f"{info['text_count']:3d} texts, "
              f"{info['tradition_count']:2d} traditions: {traditions}")

    print(f"\nOutput: {tags_path}")
    print(f"Distribution: {dist_path}")

    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tag mythic texts with Thompson motifs")
    parser.add_argument("--text", help="Tag a specific text by text_id")
    args = parser.parse_args()
    run_tagging(target_text=args.text)
