#!/usr/bin/env python3
"""
Entity Extraction for Mythic Library Phase 3.

Extracts named entities (deities, heroes, places, creatures) from segmented
texts using a curated gazetteer + regex pattern matching approach.

This replaces the originally planned spaCy NER pipeline because Python 3.14
is not yet supported by spaCy. The gazetteer approach is actually better for
mythological texts since standard NER models don't recognize deity names.

Usage:
    python scripts/extract/extract_entities.py                  # Extract all
    python scripts/extract/extract_entities.py --text the-iliad # Extract one

Output:
    data/entities.json          # Per-segment entity extractions
    data/entity_catalog.json    # Aggregated cross-text catalog
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

DATA_DIR.mkdir(exist_ok=True)

# ============================================================
# Mythological Entity Gazetteer
# ============================================================
# Format: "Name": {"type": "deity|hero|place|creature|artifact|concept", "tradition": "..."}
# This is the core knowledge base for extraction.

GAZETTEER = {
    # === MESOPOTAMIAN ===
    "Enkidu": {"type": "hero", "tradition": "mesopotamian"},
    "Gilgamesh": {"type": "hero", "tradition": "mesopotamian"},
    "Utnapishtim": {"type": "hero", "tradition": "mesopotamian"},
    "Ishtar": {"type": "deity", "tradition": "mesopotamian"},
    "Inanna": {"type": "deity", "tradition": "mesopotamian"},
    "Tiamat": {"type": "deity", "tradition": "mesopotamian"},
    "Marduk": {"type": "deity", "tradition": "mesopotamian"},
    "Apsu": {"type": "deity", "tradition": "mesopotamian"},
    "Ereshkigal": {"type": "deity", "tradition": "mesopotamian"},
    "Ninhursag": {"type": "deity", "tradition": "mesopotamian"},
    "Enlil": {"type": "deity", "tradition": "mesopotamian"},
    "Enki": {"type": "deity", "tradition": "mesopotamian"},
    "Anu": {"type": "deity", "tradition": "mesopotamian"},
    "Shamash": {"type": "deity", "tradition": "mesopotamian"},
    "Nergal": {"type": "deity", "tradition": "mesopotamian"},
    "Dumuzi": {"type": "deity", "tradition": "mesopotamian"},
    "Tammuz": {"type": "deity", "tradition": "mesopotamian"},
    "Uruk": {"type": "place", "tradition": "mesopotamian"},
    "Kur": {"type": "place", "tradition": "mesopotamian"},
    "Nibiru": {"type": "concept", "tradition": "mesopotamian"},

    # === EGYPTIAN ===
    "Osiris": {"type": "deity", "tradition": "egyptian"},
    "Isis": {"type": "deity", "tradition": "egyptian"},
    "Horus": {"type": "deity", "tradition": "egyptian"},
    "Set": {"type": "deity", "tradition": "egyptian"},
    "Thoth": {"type": "deity", "tradition": "egyptian"},
    "Anubis": {"type": "deity", "tradition": "egyptian"},
    "Hathor": {"type": "deity", "tradition": "egyptian"},
    "Nephthys": {"type": "deity", "tradition": "egyptian"},
    "Ptah": {"type": "deity", "tradition": "egyptian"},
    "Atum": {"type": "deity", "tradition": "egyptian"},
    "Amun": {"type": "deity", "tradition": "egyptian"},
    "Sekhmet": {"type": "deity", "tradition": "egyptian"},
    "Sobek": {"type": "deity", "tradition": "egyptian"},
    "Khepri": {"type": "deity", "tradition": "egyptian"},
    "Nut": {"type": "deity", "tradition": "egyptian"},
    "Geb": {"type": "deity", "tradition": "egyptian"},

    # === GREEK ===
    "Zeus": {"type": "deity", "tradition": "greek"},
    "Athena": {"type": "deity", "tradition": "greek"},
    "Apollo": {"type": "deity", "tradition": "greek"},
    "Aphrodite": {"type": "deity", "tradition": "greek"},
    "Ares": {"type": "deity", "tradition": "greek"},
    "Artemis": {"type": "deity", "tradition": "greek"},
    "Hera": {"type": "deity", "tradition": "greek"},
    "Poseidon": {"type": "deity", "tradition": "greek"},
    "Hades": {"type": "deity", "tradition": "greek"},
    "Hermes": {"type": "deity", "tradition": "greek"},
    "Hephaestus": {"type": "deity", "tradition": "greek"},
    "Demeter": {"type": "deity", "tradition": "greek"},
    "Persephone": {"type": "deity", "tradition": "greek"},
    "Dionysus": {"type": "deity", "tradition": "greek"},
    "Prometheus": {"type": "deity", "tradition": "greek"},
    "Cronus": {"type": "deity", "tradition": "greek"},
    "Achilles": {"type": "hero", "tradition": "greek"},
    "Odysseus": {"type": "hero", "tradition": "greek"},
    "Hector": {"type": "hero", "tradition": "greek"},
    "Agamemnon": {"type": "hero", "tradition": "greek"},
    "Penelope": {"type": "hero", "tradition": "greek"},
    "Telemachus": {"type": "hero", "tradition": "greek"},
    "Ajax": {"type": "hero", "tradition": "greek"},
    "Patroclus": {"type": "hero", "tradition": "greek"},
    "Priam": {"type": "hero", "tradition": "greek"},
    "Helen": {"type": "hero", "tradition": "greek"},
    "Menelaus": {"type": "hero", "tradition": "greek"},
    "Jason": {"type": "hero", "tradition": "greek"},
    "Medea": {"type": "hero", "tradition": "greek"},
    "Theseus": {"type": "hero", "tradition": "greek"},
    "Perseus": {"type": "hero", "tradition": "greek"},
    "Heracles": {"type": "hero", "tradition": "greek"},
    "Hercules": {"type": "hero", "tradition": "greek"},
    "Orpheus": {"type": "hero", "tradition": "greek"},
    "Eurydice": {"type": "hero", "tradition": "greek"},
    "Troy": {"type": "place", "tradition": "greek"},
    "Ithaca": {"type": "place", "tradition": "greek"},
    "Olympus": {"type": "place", "tradition": "greek"},
    "Tartarus": {"type": "place", "tradition": "greek"},
    "Styx": {"type": "place", "tradition": "greek"},
    "Cyclops": {"type": "creature", "tradition": "greek"},
    "Minotaur": {"type": "creature", "tradition": "greek"},
    "Medusa": {"type": "creature", "tradition": "greek"},
    "Titans": {"type": "creature", "tradition": "greek"},
    "Cerberus": {"type": "creature", "tradition": "greek"},
    "Centaur": {"type": "creature", "tradition": "greek"},

    # === NORSE ===
    "Odin": {"type": "deity", "tradition": "norse"},
    "Thor": {"type": "deity", "tradition": "norse"},
    "Loki": {"type": "deity", "tradition": "norse"},
    "Freya": {"type": "deity", "tradition": "norse"},
    "Frigg": {"type": "deity", "tradition": "norse"},
    "Baldur": {"type": "deity", "tradition": "norse"},
    "Balder": {"type": "deity", "tradition": "norse"},
    "Heimdall": {"type": "deity", "tradition": "norse"},
    "Tyr": {"type": "deity", "tradition": "norse"},
    "Fenrir": {"type": "creature", "tradition": "norse"},
    "Jormungandr": {"type": "creature", "tradition": "norse"},
    "Yggdrasil": {"type": "place", "tradition": "norse"},
    "Asgard": {"type": "place", "tradition": "norse"},
    "Midgard": {"type": "place", "tradition": "norse"},
    "Valhalla": {"type": "place", "tradition": "norse"},
    "Ragnarok": {"type": "concept", "tradition": "norse"},
    "Sigurd": {"type": "hero", "tradition": "norse"},
    "Brynhild": {"type": "hero", "tradition": "norse"},
    "Grendel": {"type": "creature", "tradition": "norse"},
    "Beowulf": {"type": "hero", "tradition": "norse"},
    "Hrothgar": {"type": "hero", "tradition": "norse"},

    # === CELTIC ===
    "Cuchulainn": {"type": "hero", "tradition": "celtic"},
    "Cuchulain": {"type": "hero", "tradition": "celtic"},
    "Lugh": {"type": "deity", "tradition": "celtic"},
    "Dagda": {"type": "deity", "tradition": "celtic"},
    "Morrigan": {"type": "deity", "tradition": "celtic"},
    "Brigid": {"type": "deity", "tradition": "celtic"},
    "Danu": {"type": "deity", "tradition": "celtic"},
    "Rhiannon": {"type": "deity", "tradition": "celtic"},
    "Pryderi": {"type": "hero", "tradition": "celtic"},
    "Pwyll": {"type": "hero", "tradition": "celtic"},
    "Finn": {"type": "hero", "tradition": "celtic"},
    "Oisin": {"type": "hero", "tradition": "celtic"},
    "Tuatha": {"type": "concept", "tradition": "celtic"},

    # === INDIAN ===
    "Brahma": {"type": "deity", "tradition": "indian"},
    "Vishnu": {"type": "deity", "tradition": "indian"},
    "Shiva": {"type": "deity", "tradition": "indian"},
    "Krishna": {"type": "deity", "tradition": "indian"},
    "Rama": {"type": "deity", "tradition": "indian"},
    "Indra": {"type": "deity", "tradition": "indian"},
    "Agni": {"type": "deity", "tradition": "indian"},
    "Varuna": {"type": "deity", "tradition": "indian"},
    "Soma": {"type": "deity", "tradition": "indian"},
    "Kali": {"type": "deity", "tradition": "indian"},
    "Lakshmi": {"type": "deity", "tradition": "indian"},
    "Saraswati": {"type": "deity", "tradition": "indian"},
    "Ganesha": {"type": "deity", "tradition": "indian"},
    "Hanuman": {"type": "deity", "tradition": "indian"},
    "Arjuna": {"type": "hero", "tradition": "indian"},
    "Bhishma": {"type": "hero", "tradition": "indian"},
    "Draupadi": {"type": "hero", "tradition": "indian"},
    "Yudhishthira": {"type": "hero", "tradition": "indian"},
    "Sita": {"type": "hero", "tradition": "indian"},
    "Ravana": {"type": "creature", "tradition": "indian"},

    # === JAPANESE ===
    "Amaterasu": {"type": "deity", "tradition": "japanese"},
    "Izanagi": {"type": "deity", "tradition": "japanese"},
    "Izanami": {"type": "deity", "tradition": "japanese"},
    "Susanoo": {"type": "deity", "tradition": "japanese"},
    "Tsukuyomi": {"type": "deity", "tradition": "japanese"},

    # === CHINESE ===
    "Jade Emperor": {"type": "deity", "tradition": "chinese"},
    "Pangu": {"type": "deity", "tradition": "chinese"},
    "Nuwa": {"type": "deity", "tradition": "chinese"},
    "Fuxi": {"type": "deity", "tradition": "chinese"},
    "Confucius": {"type": "hero", "tradition": "chinese"},

    # === ROMAN ===
    "Jupiter": {"type": "deity", "tradition": "roman"},
    "Juno": {"type": "deity", "tradition": "roman"},
    "Mars": {"type": "deity", "tradition": "roman"},
    "Venus": {"type": "deity", "tradition": "roman"},
    "Mercury": {"type": "deity", "tradition": "roman"},
    "Neptune": {"type": "deity", "tradition": "roman"},
    "Minerva": {"type": "deity", "tradition": "roman"},
    "Pluto": {"type": "deity", "tradition": "roman"},
    "Saturn": {"type": "deity", "tradition": "roman"},
    "Jove": {"type": "deity", "tradition": "roman"},
    "Aeneas": {"type": "hero", "tradition": "roman"},
    "Romulus": {"type": "hero", "tradition": "roman"},
    "Remus": {"type": "hero", "tradition": "roman"},
    "Dido": {"type": "hero", "tradition": "roman"},

    # === POLYNESIAN ===
    "Maui": {"type": "hero", "tradition": "polynesian"},
    "Pele": {"type": "deity", "tradition": "polynesian"},
    "Tangaroa": {"type": "deity", "tradition": "polynesian"},
    "Tane": {"type": "deity", "tradition": "polynesian"},

    # === MESOAMERICAN ===
    "Quetzalcoatl": {"type": "deity", "tradition": "mesoamerican"},
    "Hunahpu": {"type": "hero", "tradition": "mesoamerican"},
    "Xbalanque": {"type": "hero", "tradition": "mesoamerican"},
    "Xibalba": {"type": "place", "tradition": "mesoamerican"},
    "Tezcatlipoca": {"type": "deity", "tradition": "mesoamerican"},

    # === ZOROASTRIAN ===
    "Ahura Mazda": {"type": "deity", "tradition": "zoroastrian"},
    "Angra Mainyu": {"type": "deity", "tradition": "zoroastrian"},
    "Zarathustra": {"type": "hero", "tradition": "zoroastrian"},

    # === FINNISH ===
    "Vainamoinen": {"type": "hero", "tradition": "finnish"},
    "Ilmarinen": {"type": "hero", "tradition": "finnish"},
    "Louhi": {"type": "deity", "tradition": "finnish"},
    "Kullervo": {"type": "hero", "tradition": "finnish"},

    # === AFRICAN ===
    "Anansi": {"type": "deity", "tradition": "african"},
    "Eshu": {"type": "deity", "tradition": "african"},
    "Ogun": {"type": "deity", "tradition": "african"},
    "Shango": {"type": "deity", "tradition": "african"},
    "Obatala": {"type": "deity", "tradition": "african"},
    "Olorun": {"type": "deity", "tradition": "african"},
    "Sundiata": {"type": "hero", "tradition": "african"},

    # === PERSIAN ===
    "Rustam": {"type": "hero", "tradition": "persian"},
    "Rostam": {"type": "hero", "tradition": "persian"},
    "Sohrab": {"type": "hero", "tradition": "persian"},

    # === LITERARY/CHRISTIAN ===
    "Satan": {"type": "deity", "tradition": "christian"},
    "Adam": {"type": "hero", "tradition": "hebrew"},
    "Eve": {"type": "hero", "tradition": "hebrew"},
    "Moses": {"type": "hero", "tradition": "hebrew"},
    "Dante": {"type": "hero", "tradition": "roman"},
    "Virgil": {"type": "hero", "tradition": "roman"},
    "Beatrice": {"type": "hero", "tradition": "roman"},
}


def build_regex_patterns() -> list:
    """Build compiled regex patterns from gazetteer for fast matching.

    Ambiguous names (common English words like 'Set', 'Nut', 'Eve') use
    case-sensitive matching to reduce false positives. A capitalized 'Set'
    is likely the Egyptian god; a lowercase 'set' is the English verb.
    """
    # Names that are also common English words — require case-sensitive match
    CASE_SENSITIVE = {
        "Set", "Nut", "Eve", "Adam", "Mars", "Venus", "Mercury",
        "Saturn", "Jupiter", "Juno", "Neptune", "Minerva", "Pluto",
        "Soma", "Finn", "Virgil", "Dante", "Beatrice", "Jason",
        "Helen", "Ajax", "Troy", "Tyr", "Kur", "Anu", "Tane",
    }

    # Sort by length (longest first) to match multi-word names first
    names = sorted(GAZETTEER.keys(), key=len, reverse=True)
    patterns = []
    for name in names:
        # Escape regex special chars and create word-boundary pattern
        escaped = re.escape(name)
        if name in CASE_SENSITIVE:
            # Case-sensitive: only match when capitalized (e.g., "Set" not "set")
            pattern = re.compile(r'\b' + escaped + r'\b')
        else:
            pattern = re.compile(r'\b' + escaped + r'\b', re.IGNORECASE)
        patterns.append((name, pattern))
    return patterns


def extract_entities_from_text(text: str, patterns: list) -> list:
    """
    Extract entity mentions from a text using gazetteer patterns.
    Returns list of mentions with context.
    """
    mentions = []
    # Split into sentences for context
    sentences = re.split(r'(?<=[.!?])\s+', text)

    sentence_offset = 0
    for sentence in sentences:
        for name, pattern in patterns:
            for match in pattern.finditer(sentence):
                mentions.append({
                    "entity_name": name,
                    "matched_text": match.group(0),
                    "entity_type": GAZETTEER[name]["type"],
                    "tradition": GAZETTEER[name]["tradition"],
                    "char_offset": sentence_offset + match.start(),
                    "sentence_context": sentence[:200].strip(),
                })
        sentence_offset += len(sentence) + 1  # +1 for space

    return mentions


def process_text(text_dir: Path, text_id: str, tradition: str,
                 patterns: list) -> dict:
    """Extract entities from all segments of a text."""
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
        "entity_summary": defaultdict(int),
        "total_mentions": 0,
        "unique_entities": set(),
    }

    for seg_info in seg_index["segments"]:
        seg_file = seg_dir / seg_info["file"]
        if not seg_file.exists():
            continue

        with open(seg_file, "r", encoding="utf-8") as f:
            content = f.read()

        mentions = extract_entities_from_text(content, patterns)

        if mentions:
            seg_result = {
                "segment_id": seg_info["id"],
                "segment_label": seg_info["label"],
                "mention_count": len(mentions),
                "mentions": mentions,
            }
            text_result["segments"].append(seg_result)
            text_result["total_mentions"] += len(mentions)

            for m in mentions:
                text_result["entity_summary"][m["entity_name"]] += 1
                text_result["unique_entities"].add(m["entity_name"])

    # Convert sets and defaultdicts for JSON
    text_result["unique_entity_count"] = len(text_result["unique_entities"])
    text_result["unique_entities"] = sorted(text_result["unique_entities"])
    text_result["entity_summary"] = dict(text_result["entity_summary"])
    text_result["status"] = "extracted"

    return text_result


def build_catalog(all_results: list) -> dict:
    """Build aggregated entity catalog from all extraction results."""
    catalog = {}

    for result in all_results:
        if result.get("status") != "extracted":
            continue

        text_id = result["text_id"]
        tradition = result["tradition"]

        for entity_name, count in result.get("entity_summary", {}).items():
            if entity_name not in catalog:
                info = GAZETTEER.get(entity_name, {})
                catalog[entity_name] = {
                    "entity_name": entity_name,
                    "entity_type": info.get("type", "unknown"),
                    "primary_tradition": info.get("tradition", "unknown"),
                    "total_mentions": 0,
                    "text_count": 0,
                    "tradition_count": 0,
                    "texts": [],
                    "traditions": set(),
                }

            entry = catalog[entity_name]
            entry["total_mentions"] += count
            entry["text_count"] += 1
            entry["texts"].append({"text_id": text_id, "tradition": tradition, "count": count})
            entry["traditions"].add(tradition)

    # Finalize
    for entry in catalog.values():
        entry["traditions"] = sorted(entry["traditions"])
        entry["tradition_count"] = len(entry["traditions"])

    # Sort by total mentions
    sorted_catalog = dict(
        sorted(catalog.items(), key=lambda x: -x[1]["total_mentions"])
    )

    return sorted_catalog


def run_extraction(target_text: str = None):
    """Run entity extraction on all or a specific text."""
    patterns = build_regex_patterns()
    all_results = []

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

            seg_dir = text_dir / "segments"
            if not seg_dir.exists():
                continue

            total += 1
            try:
                result = process_text(text_dir, text_id, tradition, patterns)
                all_results.append(result)

                if result["status"] == "extracted" and result["total_mentions"] > 0:
                    success += 1
                    top = sorted(result["entity_summary"].items(),
                                key=lambda x: -x[1])[:5]
                    top_str = ", ".join(f"{n}({c})" for n, c in top)
                    print(f"  [{result['total_mentions']:5d} mentions] "
                          f"{tradition}/{text_id}: {top_str}")
                else:
                    print(f"  [    0 mentions] {tradition}/{text_id}")

            except Exception as e:
                print(f"  [ERR] {tradition}/{text_id}: {e}")

    # Build catalog
    catalog = build_catalog(all_results)

    # Save results
    entities_path = DATA_DIR / "entities.json"
    catalog_path = DATA_DIR / "entity_catalog.json"

    with open(entities_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    # Summary
    print(f"\n{'='*60}")
    print(f"ENTITY EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"Texts processed:       {total}")
    print(f"Texts with entities:   {success}")
    print(f"Unique entities found: {len(catalog)}")
    total_mentions = sum(e["total_mentions"] for e in catalog.values())
    print(f"Total mentions:        {total_mentions}")

    # Top entities
    print(f"\nTop 20 entities by mention count:")
    for name, info in list(catalog.items())[:20]:
        print(f"  {info['total_mentions']:6d} | {name:20s} | "
              f"{info['entity_type']:10s} | {info['tradition_count']} traditions")

    # Cross-tradition entities
    cross_tradition = {k: v for k, v in catalog.items() if v["tradition_count"] >= 3}
    if cross_tradition:
        print(f"\nEntities appearing across 3+ traditions ({len(cross_tradition)}):")
        for name, info in sorted(cross_tradition.items(),
                                 key=lambda x: -x[1]["tradition_count"]):
            traditions = ", ".join(info["traditions"])
            print(f"  {name:20s} | {info['tradition_count']} traditions: {traditions}")

    print(f"\nOutput: {entities_path}")
    print(f"Catalog: {catalog_path}")

    return all_results, catalog


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract entities from mythic texts")
    parser.add_argument("--text", help="Extract from a specific text by text_id")
    args = parser.parse_args()
    run_extraction(target_text=args.text)
