# Mythic Library

A curated collection of public domain mythological and ancient texts serving as the **foundation layer** for the Mythopoetic OS. This library provides the raw mythic substrate from which universal patterns, archetypes, and narrative structures can be extracted and validated across cultures.

## Current Status

| Metric | Count |
|--------|-------|
| **Texts Cataloged** | 132 |
| **Traditions Covered** | 32 |
| **Files Downloaded** | 211 |
| **Total Size** | ~822 MB |

### Tradition Coverage

| Region | Traditions | Texts |
|--------|------------|-------|
| **Near East** | Mesopotamian, Egyptian, Levantine, Hebrew, Zoroastrian | 14 |
| **Mediterranean** | Greek, Roman | 14 |
| **Europe** | Norse, Celtic, Germanic, Slavic, Baltic, European | 22 |
| **South Asia** | Indian (Hindu/Buddhist), Tibetan | 13 |
| **East Asia** | Chinese, Japanese, Korean | 12 |
| **Central Asia** | Turkic, Mongol, Persian | 5 |
| **Africa** | Pan-African, Yoruba, Bantu | 13 |
| **Oceania** | Polynesian, Melanesian, Australian Aboriginal | 12 |
| **Americas** | North American, Mesoamerican, South American | 15 |
| **Other** | Arctic, Siberian, Southeast Asian, Anthologies | 12 |

## Project Purpose

This library exists to:

1. **Validate Universal Patterns**: Test whether mythic structures (hero's journey, descent/return, creation/destruction) truly appear across unrelated cultures
2. **Extract Archetypal Substrate**: Identify the recurring figures, motifs, and transformations that form the basis of human mythmaking
3. **Support Computational Mythology**: Provide clean, structured source texts for NLP analysis, pattern extraction, and cross-cultural comparison
4. **Preserve Public Domain Heritage**: Consolidate scattered public domain translations into a unified, well-documented collection

## Architecture

```
mythic-library/
├── texts/                          # Organized by tradition
│   ├── {tradition}/                # e.g., greek, norse, african
│   │   └── {text-id}/              # e.g., the-iliad, poetic-edda
│   │       ├── downloads/          # Acquired files (PDF, TXT, HTML)
│   │       └── SOURCES.md          # Provenance documentation
├── sources/
│   ├── master_catalog.csv          # All texts with metadata
│   ├── curated_sources.json        # Verified source URLs by text
│   └── download_log.json           # Download history with checksums
├── scripts/
│   ├── bulk_download.py            # Multi-source downloader
│   ├── add_*.py                    # Catalog expansion scripts
│   └── analyze_gaps.py             # Coverage analysis
└── docs/
    ├── gap_analysis_v3.md          # Current gap analysis
    └── DEVELOPMENT.md              # Development log
```

## Source Repositories

Automated acquisition from:

| Source | Specialization | Handler |
|--------|---------------|---------|
| [Internet Archive](https://archive.org) | Scanned books, PDFs | `download_from_archive()` |
| [Project Gutenberg](https://gutenberg.org) | Plain text classics | `download_from_gutenberg()` |
| [Sacred Texts](https://sacred-texts.com) | Religious/mythological | `download_from_sacred_texts()` |
| [ETCSL](https://etcsl.orinst.ox.ac.uk) | Sumerian literature | `download_from_etcsl()` |
| Direct URLs | Academic PDFs | `download_direct_url()` |

## Usage

```bash
# Download all texts for a specific work
python scripts/bulk_download.py --text epic-of-gilgamesh

# Download from a specific source type
python scripts/bulk_download.py --source gutenberg

# Dry run to see what would download
python scripts/bulk_download.py --dry-run

# Skip already downloaded files
python scripts/bulk_download.py --skip-existing
```

## Key Texts by Mythic Function

### Cosmogony (Creation)
- Enuma Elish (Babylonian), Theogony (Greek), Genesis, Popol Vuh (Maya)
- Rig Veda hymns, Kojiki (Japanese), Kalevala (Finnish)
- Huarochiri Manuscript (Andean), Myths of Ife (Yoruba)

### Katabasis (Descent/Return)
- Inanna's Descent (Sumerian), Descent of Ishtar (Akkadian)
- Odyssey Book 11, Aeneid Book 6, Divine Comedy
- Orphic materials, Tibetan Book of the Dead

### Hero Cycle
- Epic of Gilgamesh, Iliad/Odyssey, Mahabharata/Ramayana
- Beowulf, Volsunga Saga, Tale of the Heike
- Shahnameh, Sundiata, Popol Vuh Hero Twins

### Trickster
- Anansi tales, Coyote cycles, Raven (Tlingit)
- Loki materials, Hermes/Prometheus, Eshu (Yoruba)
- Maui cycle (Polynesian)

### Dying God / Resurrection
- Osiris materials (Legends of the Gods, Burden of Isis)
- Bacchae (Dionysus), Balder (Norse)
- Attis, Adonis, Tammuz references

### Great Mother / Divine Feminine
- Inanna/Ishtar materials, Isis hymns
- Demeter/Persephone (Homeric Hymns)
- Devi traditions (Hindu), Amaterasu (Kojiki)

## Validation Approach

Each text includes:
1. **Source citation**: Full URL, translator, publication date
2. **Checksum**: SHA-256 hash for integrity verification
3. **Content validation**: Key phrase detection, minimum size checks
4. **Multiple translations**: Where available, for cross-reference

## Roadmap

### Phase 1: Foundation (Complete)
- [x] Core texts from major traditions
- [x] Automated multi-source downloader
- [x] Content validation system
- [x] Gap analysis framework

### Phase 2: Expansion (Current)
- [x] Regional gap filling (Australian, Korean, Mongol, Baltic, etc.)
- [x] Archetype-focused additions (Dying God, Trickster cycles)
- [x] Chinese/Confucian classics
- [x] Japanese literary expansion
- [ ] Remaining Coffin Texts source fix

### Phase 3: Structured Extraction (Planned)
- [ ] NLP pipeline for motif extraction
- [ ] Cross-cultural pattern database
- [ ] Archetype confidence scoring
- [ ] Integration with Mythopoetic OS layers

## Contributing

To add a text:
1. Verify public domain status
2. Add entry to `sources/curated_sources.json`
3. Add catalog entry to `sources/master_catalog.csv`
4. Run `python scripts/bulk_download.py --text {text-id}`
5. Verify download and content validation

## License

All texts are public domain. Scripts and tooling are MIT licensed.

---

*This library is part of the Mythopoetic OS project, providing the foundational mythic substrate for computational mythology and archetypal pattern analysis.*
