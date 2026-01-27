# Mythic Library

A curated collection of public domain mythological and ancient texts serving as the **empirical corpus** for validating the Archetypal Context Protocol (ACP). This library provides the raw mythic substrate from which universal patterns, archetypes, and narrative structures are extracted and tested against ACP's 8-dimensional coordinate system across cultures.

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
│   │       ├── normalized/         # Clean UTF-8 text + metadata
│   │       ├── segments/           # Structural segments
│   │       └── SOURCES.md          # Provenance documentation
├── data/
│   ├── mythic_patterns.db          # SQLite pattern database (137 MB)
│   ├── thompson_motif_index.json   # 149 Thompson motif entries
│   ├── entities.json               # Per-text entity extractions
│   ├── entity_catalog.json         # Aggregated entity catalog
│   ├── entity_aliases.json         # Cross-cultural name mappings
│   ├── motif_tags.json             # Per-text motif tags
│   └── motif_distribution.json     # Cross-text motif frequencies
├── sources/
│   ├── master_catalog.csv          # All texts with metadata
│   ├── curated_sources.json        # Verified source URLs by text
│   ├── download_log.json           # Download history with checksums
│   ├── corpus_audit.json           # Full corpus audit results
│   └── best_versions.json          # Best version per text
├── scripts/
│   ├── bulk_download.py            # Multi-source downloader
│   ├── add_*.py                    # Catalog expansion scripts
│   ├── analyze_gaps.py             # Coverage analysis
│   ├── normalize/                  # Phase 3.1: Audit & normalization
│   ├── segment/                    # Phase 3.2: Text segmentation
│   ├── extract/                    # Phase 3.3: Entity extraction
│   ├── motif/                      # Phase 3.4: Motif tagging
│   ├── database/                   # Phase 3.5: Pattern database
│   ├── explorer/                   # Browser-based data explorer
│   │   ├── server.py               # HTTP server + embedded UI
│   │   └── find_suspects.py        # Entity false positive detector
│   └── integration/                # Validation runners
│       ├── run_validation.py       # ACP validation suite
│       └── setup_integration.py    # Prerequisite checker
├── integration/                    # ACP ↔ Library bridge
│   ├── acp_loader.py               # Load ACP JSON-LD, extract coordinates
│   ├── library_loader.py           # Query mythic_patterns.db (cached co-occurrence)
│   ├── entity_mapper.py            # Map library entities → ACP archetypes
│   └── coordinate_calculator.py    # Axis-weighted & reduced-dimension distances
├── validation/                     # Hypothesis tests
│   ├── run.py                      # Single-command validation entry point
│   ├── test_coordinate_accuracy.py # Co-occurrence vs ACP distance
│   ├── test_motif_clustering.py    # Motif signatures in 8D space
│   ├── calibrate_coordinates.py    # Gradient descent coordinate calibration
│   ├── statistical_tests.py        # Permutation, bootstrap, cross-validation
│   ├── alternative_metrics.py      # Cosine, Mantel, per-axis, motif similarity
│   ├── data_quality.py             # Entity audits, normalization, deduplication
│   └── falsification.py            # Formal null hypothesis & falsification criteria
├── ACP/                            # Archetypal Context Protocol (subtree)
│   ├── schema/                     # Primordials, axes, ontology
│   └── archetypes/                 # 539 archetypes as JSON-LD
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

### Text Acquisition (Phase 1-2)

```bash
# Download all texts for a specific work
python scripts/bulk_download.py --text epic-of-gilgamesh

# Download from a specific source type
python scripts/bulk_download.py --source gutenberg

# Dry run to see what would download
python scripts/bulk_download.py --dry-run
```

### Structured Extraction (Phase 3)

```bash
# Run the full extraction pipeline
python scripts/normalize/audit_corpus.py          # Audit corpus health
python scripts/normalize/normalize_text.py         # Normalize all texts
python scripts/normalize/select_best.py            # Select best versions
python scripts/segment/segment_text.py             # Segment into structural units
python scripts/extract/extract_entities.py         # Extract named entities
python scripts/motif/tag_motifs.py                 # Tag with Thompson motifs
python scripts/database/create_db.py --reset       # Build pattern database
```

### Querying the Pattern Database

```bash
# Run all demonstration queries
python scripts/database/query_patterns.py

# Specific queries
python scripts/database/query_patterns.py --query stats      # Database statistics
python scripts/database/query_patterns.py --query patterns    # Cross-cultural patterns
python scripts/database/query_patterns.py --query flood       # Flood narratives
python scripts/database/query_patterns.py --query descent     # Descent to underworld
python scripts/database/query_patterns.py --query entities    # Cross-tradition entities
python scripts/database/query_patterns.py --query hero        # Hero cycle texts
python scripts/database/query_patterns.py --query creation    # Creation myths
python scripts/database/query_patterns.py --query trickster   # Trickster narratives

# Full-text search
python scripts/database/query_patterns.py --search "serpent AND world"

# Custom SQL
python scripts/database/query_patterns.py --sql "SELECT * FROM patterns ORDER BY tradition_count DESC"
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

## ACP Integration

The [Archetypal Context Protocol](ACP/) provides an 8-dimensional coordinate system for archetypes. The integration tests whether ACP coordinates predict narrative co-occurrence patterns in the library corpus.

### Running the Validation Suite

```bash
# Check prerequisites
python scripts/integration/setup_integration.py

# Run full validation (all 10 phases)
python -m validation.run

# Quick mode (fewer permutations, faster)
python -m validation.run --quick

# Generate standalone markdown report
python -m validation.run --report

# Save versioned baseline metrics
python -m validation.run --baseline

# Run pytest suite
pytest tests/ -v
```

### Browsing the Data

```bash
# Start the explorer UI at http://127.0.0.1:8421
python scripts/explorer/server.py
```

The explorer provides views for entity details, ACP coordinate projections, co-occurrence networks, Thompson motif distributions, validation results, and an interactive audit view with live falsification tests.

### Current Results

| Metric | Pre-Calibration | Post-Calibration |
|--------|----------------|------------------|
| ACP Archetypes | 539 | — |
| Entities Mapped | 148 / 173 (85.5%) | — |
| Pearson r | -0.064 (p<0.000001) | -0.156 (p<0.000001) |
| Spearman r | -0.074 (p<0.000001) | -0.203 (p<0.000001) |
| Axis-weighted r | -0.125 | — |
| Optimized 6D weighted r | -0.140 | — |
| Best 3D subset r | -0.147 | — |

The negative correlation is consistent with the ACP hypothesis: archetypes closer in coordinate space co-occur more often in narratives. Falsification testing (Phase 9) shows the signal **partially survives** (2/4 criteria pass): the Mantel test is significant (p=0.039), coordinates are robust to noise perturbation, but a simpler 1D tradition-similarity model outperforms full 8D ACP (|r|=0.420 vs |r|=0.074). Phase 10 optimization zeroes 2 harmful axes (ascent-descent, stasis-transformation) and applies per-axis weighting, nearly doubling the correlation (r=-0.074 to r=-0.140), though tradition identity remains the stronger predictor. The best 3D subset (order-chaos, creation-destruction, individual-collective) at r=-0.147 outperforms the full 8D system.

## Validation Approach

Each text includes:
1. **Source citation**: Full URL, translator, publication date
2. **Checksum**: SHA-256 hash for integrity verification
3. **Content validation**: Key phrase detection, minimum size checks
4. **Multiple translations**: Where available, for cross-reference

## Pattern Database

The SQLite database at `data/mythic_patterns.db` contains:

| Table | Rows | Description |
|-------|------|-------------|
| `texts` | 132 | Core metadata (96 usable with content) |
| `segments` | 4,000 | Structural units with full text |
| `entities` | 173 | Canonical entity records |
| `entity_mentions` | 28,104 | Entity occurrences in segments |
| `motifs` | 149 | Thompson Motif Index reference |
| `motif_tags` | 55,539 | Motif assignments with confidence |
| `patterns` | 18 | Cross-cultural pattern definitions |
| `pattern_attestations` | 786 | Pattern evidence across texts |
| `segments_fts` | — | FTS5 full-text search index |

### Cross-Cultural Patterns Identified

| Pattern | Traditions | Texts |
|---------|-----------|-------|
| Cosmogony/Creation | 26 | 73 |
| Hero Cycle | 26 | 72 |
| Creation of Humanity | 24 | 66 |
| Quest for Immortality | 24 | 66 |
| Theft of Fire | 24 | 64 |
| Descent to Underworld | 24 | 61 |
| World Flood | 20 | 51 |
| Dragon Slaying | 22 | 49 |
| Trickster | 20 | 47 |
| Dying & Rising God | 20 | 40 |

## Roadmap

### v1 Validation (Co-occurrence Based) — Archived

> Phases 4-10 used textual co-occurrence (entities appearing in the same text
> segments) as the validation target. This measures textual proximity, not the
> relational archetypal meaning the ACP claims to encode. The key finding:
> simple 1D "same tradition?" outperforms the full 8D system, indicating
> co-occurrence primarily reflects cultural origin rather than archetypal
> structure. This approach is archived; v2 will test cross-cultural functional
> equivalence, axis interpretability, and relational prediction directly.

### Phase 1: Foundation — Complete
- [x] Core texts from major traditions
- [x] Automated multi-source downloader
- [x] Content validation system
- [x] Gap analysis framework

### Phase 2: Expansion — Complete
- [x] Regional gap filling (Australian, Korean, Mongol, Baltic, etc.)
- [x] Archetype-focused additions (Dying God, Trickster cycles)
- [x] Chinese/Confucian classics
- [x] Japanese literary expansion

### Phase 3: Structured Extraction — Complete
- [x] Corpus audit & text normalization (126 texts normalized)
- [x] Structural segmentation (4,000 segments)
- [x] Entity extraction (173 entities, 28,104 mentions)
- [x] Thompson Motif Index tagging (149 motifs, 55,539 tags)
- [x] SQLite pattern database with FTS5 search (137 MB)
- [x] 18 cross-cultural patterns identified across 20-26 traditions
- [x] Case-sensitive disambiguation for 27 ambiguous entity names

### Phase 4: ACP Integration Bridge — Complete
- [x] ACP pulled as git subtree (539 archetypes, 24 primordials, 8D coordinates)
- [x] Integration bridge: ACP loader, library loader, entity mapper
- [x] Tradition-aware entity mapping: 148/173 (85.5%) including fuzzy hero matching
- [x] Coordinate validation: distance vs co-occurrence correlation
- [x] Thompson motif clustering analysis in 8D coordinate space
- [x] Browser-based data explorer (entities, coordinates, co-occurrence, motifs)
- [x] Per-tradition correlation analysis (Norse r=-0.354, p=0.008)
- [x] Coordinate calibration via gradient descent (Spearman r: -0.074 → -0.203)

### Phase 5: Statistical Rigor — Complete
- [x] Permutation test: empirical p=0.053 (borderline — random can nearly match)
- [x] Cross-validation: 5-fold CV r=-0.225 ± 0.041 (calibration generalizes)
- [x] Bootstrap 95% CIs: Spearman [-0.121, -0.070], excludes zero
- [x] Multiple comparison correction: 0/12 traditions survive Bonferroni/BH
- [x] Holdout tradition test: Norse r=-0.354 robust when excluded from training

### Phase 6: Alternative Metrics & Hypothesis Tests — Complete
- [x] Cosine similarity (Euclidean wins r=-0.095 vs r=-0.036), per-axis (creation-destruction strongest r=-0.140)
- [x] Axis-weighted distance: 50% improvement (r=-0.142 vs r=-0.095)
- [x] Mantel test: empirical p=0.029 (significant at α=0.05)
- [x] Motif-mediated similarity: Jaccard r=0.749 (ceiling), ACP dist vs Jaccard r=-0.110

### Phase 7: Data Quality & Coverage — Complete
- [x] Entity mention audit: 100-sample random check — 0 flags, extraction is clean
- [x] Co-occurrence normalization: raw, log, TF-IDF, tradition-normalized — raw is best
- [x] Cross-tradition deduplication: 1 cross-tradition share (Prometheus/Satan), not inflating results
- [x] Unmapped analysis: 64 entities (44% mentions) unmapped, 42 heroes — ACP scope is deities, documented

### Phase 8: Reproducibility & Reporting — Complete
- [x] Single-command validation: `python -m validation.run --full` (all 10 phases)
- [x] Automated pytest suite: 32 tests across 9 classes, all passing
- [x] Standalone markdown report generator (`--report` flag)
- [x] Versioned metric baselines per git commit (`--baseline` flag)

### Phase 9: Falsification Criteria — Complete
- [x] Formal null hypothesis: H0 = "ACP 8D coordinates no better than random at predicting co-occurrence"
- [x] Pre-registered threshold: Mantel p < 0.05 required
- [x] Alternative model: 1D tradition beats 8D ACP (|r|=0.361 vs |r|=0.095) — but ACP shows intra-tradition signal
- [x] Axis ablation: 2 harmful axes (active-receptive, ascent-descent), 5-6D system may be better
- [x] Coordinate sensitivity: 100% robust to ±0.05 noise, new archetypes don't drive signal
- [x] Verdict: PARTIALLY SURVIVES — real but modest signal, tradition is a stronger predictor

### Phase 10: Optimized Model — Complete
- [x] Per-axis weight computation from |Spearman r| correlations
- [x] Harmful axis identification and zeroing (ascent-descent, stasis-transformation)
- [x] 6D weighted model: r=-0.140 (90% improvement over 8D r=-0.074)
- [x] Exhaustive dimensionality search: 218 axis subsets from 3D to 7D
- [x] Best subset: 3D (order-chaos, creation-destruction, individual-collective) r=-0.147
- [x] Weighted calibration with axis-frozen gradient descent (loss reduction 39.1%)
- [x] Weighted falsification: tradition still outperforms (|r|=0.420 vs |r|=0.301)
- [x] Interactive "Optimized" audit tab in browser explorer
- [x] Performance: bulk co-occurrence caching (150K queries → 1 query), vectorized calibration (10x speedup)
- [x] Verdict: PARTIALLY SURVIVES (2/4) — optimization improves signal but doesn't close the tradition gap

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

*This library is part of the Mythogenetic OS project, providing the empirical corpus for validating the Archetypal Context Protocol against cross-cultural narrative data.*
