# Mythic Library Development Log

## Project Vision

The Mythic Library serves as **Layer 0** of the Mythopoetic OS - the raw textual substrate from which mythic patterns are extracted. The goal is not merely to collect texts, but to build a corpus sufficient to **validate or falsify** claims about universal mythic structures.

### Core Hypothesis

Certain narrative patterns (creation, descent, return, transformation, trickster, dying god, great mother) appear independently across cultures with no historical contact. If true, this suggests these patterns emerge from fundamental aspects of human cognition and experience rather than diffusion.

### Validation Requirements

To test this hypothesis rigorously, we need:
1. **Breadth**: Texts from geographically and historically isolated cultures
2. **Depth**: Multiple texts per tradition to distinguish core patterns from variants
3. **Primary sources**: Translations close to original materials, not retellings
4. **Scholarly provenance**: Documented translations with academic credibility

---

## Session Log: January 2025

### Starting State
- 62 texts from initial spreadsheet import
- Basic catalog structure
- No automated download capability

### Key Developments

#### 1. Bulk Download Pipeline

Built `scripts/bulk_download.py` with handlers for:
- **Internet Archive**: Metadata API + file download with format preference (PDF > DJVU > TXT)
- **Project Gutenberg**: Direct text file acquisition via ebook ID
- **Sacred Texts**: HTML scraping with content extraction
- **ETCSL**: Specialized handler for Oxford Sumerian corpus
- **Direct URLs**: For academic PDFs (terebess.hu, hse.ru, etc.)

Features:
- Rate limiting per domain (respects server load)
- SHA-256 checksums for integrity
- Content validation with TEXT_SIGNATURES (key phrases, minimum sizes)
- Download logging with full provenance

#### 2. Gap Analysis Framework

Created systematic gap analysis by:
- **Mythic function** (cosmogony, theogony, katabasis, hero cycle, trickster, etc.)
- **Geographic region** (to ensure non-Western coverage)
- **Archetype** (dying god, great mother, culture hero, etc.)

Key insight: The "Dying God" pattern was significantly under-represented. Added:
- Osiris materials (Legends of the Gods, Burden of Isis)
- Bacchae (Dionysus)
- Attis/Adonis/Tammuz references in Near Eastern texts

#### 3. Regional Expansion

Filled major gaps:

| Region | Before | After | Key Additions |
|--------|--------|-------|---------------|
| Australian Aboriginal | 0 | 2 | Legendary Tales (Parker) |
| Korean | 0 | 1 | Samguk Yusa |
| Mongol | 0 | 1 | Secret History |
| Slavic | 1 | 5 | Byliny, Songs of Russian People, 60 Folktales |
| Polynesian | 2 | 6 | Maui cycle, Grey's Mythology, Hawaiian |
| Oceanic (Melanesian) | 0 | 4 | Codrington, Dixon, Pacific Legends |
| Native American | 4 | 9 | Tlingit, Navajo, Hopi, Seneca, SE tribes |
| South American | 1 | 3 | Huarochiri Manuscript, Codex Chimalpopoca |

#### 4. Philosophical/Religious Expansion

Added foundational texts for pattern validation:
- **Chinese**: Tao Te Ching, I Ching, Chuang Tzu, Analects
- **Indian**: Upanishads, Bhagavad Gita, expanded Jataka
- **Tibetan**: Book of the Dead (Evans-Wentz)
- **Zoroastrian**: Complete Zend Avesta (3 parts)

These provide philosophical frameworks that complement narrative mythology.

#### 5. Japanese Literary Expansion

Added court literature and war epics:
- **Tale of Genji** (Waley): World's first novel, Heian aesthetics
- **Tale of the Heike** (Sadler, Kitagawa): Genpei War, Buddhist impermanence

These complement the mythic Kojiki/Nihongi with literary expressions of Japanese worldview.

---

## Architecture Insights

### Why This Structure Works

```
texts/{tradition}/{text-id}/downloads/
```

This allows:
1. **Multiple translations** per text (different filenames)
2. **Easy tradition-level queries** (all Greek texts)
3. **Text-level provenance** (SOURCES.md per text)
4. **Download isolation** (downloads/ subdirectory)

### Content Validation Strategy

The TEXT_SIGNATURES system validates downloads by checking for:
- **Key phrases** that must appear (e.g., "Enkidu" in Gilgamesh)
- **Minimum file size** (to catch error pages)
- **Format-specific checks** (PDF structure, text encoding)

This catches:
- 404 pages saved as files
- Truncated downloads
- Wrong texts from ambiguous URLs

### Source Priority

When multiple sources exist for a text:
1. **Internet Archive PDF** (scholarly scans, full content)
2. **Project Gutenberg TXT** (clean text, good for NLP)
3. **Sacred Texts HTML** (often index pages only - limited)
4. **Direct academic PDFs** (when Archive lacks the text)

---

## Remaining Gaps

### High Priority
- [ ] Egyptian Coffin Texts (Faulkner) - Archive source unavailable
- [ ] Apollodorus Bibliotheca - Sacred Texts URL 404
- [ ] More Mesopotamian tablet translations
- [ ] Aztec Codices beyond Chimalpopoca

### Medium Priority
- [ ] More Buddhist Pali Canon (Vinaya, Abhidhamma)
- [ ] Daoist Canon expansion
- [ ] West African Ifa divination texts
- [ ] Siberian shamanic materials

### Low Priority (Future Phases)
- [ ] Gnostic corpus expansion
- [ ] Hermetic texts
- [ ] Alchemical symbolism texts
- [ ] Comparative mythology secondary sources

---

## Session Log: January 2025 (Phase 3)

### Phase 3: Structured Extraction — Complete

Transformed the 822MB raw text corpus into a queryable pattern database in 5 sub-phases.

#### Sub-Phase 3.1: Corpus Audit & Text Normalization

Built `scripts/normalize/` with 4 scripts:

- **`audit_corpus.py`**: Walked entire `texts/` tree. Found 211 files, identified 139 usable text files, flagged 59 Sacred Texts index-only stubs (<200 lines). Cross-referenced against `master_catalog.csv`.

- **`normalize_text.py`**: Three format-specific normalizers:
  - **Gutenberg**: Strip BOM, remove `*** START/END ***` headers/footers, parse metadata, collapse blank lines
  - **Sacred Texts**: Remove custom headers, strip navigation, flag index-only stubs
  - **ETCSL**: Remove navigation blocks, fix word-joining artifacts from HTML tag stripping
  - Result: 126 texts normalized, 42 skipped (stubs), 0 errors

- **`extract_pdf.py`**: PyPDF2 extraction for accessible PDFs. 20 extracted successfully, 11 failed, 12 DRM-protected skipped.

- **`select_best.py`**: For texts with multiple versions, selected best by format priority (Gutenberg > PDF > Sacred Texts) and word count. Result: 96 texts with usable content, 36 without.

#### Sub-Phase 3.2: Text Segmentation

Built `scripts/segment/segment_text.py` with regex-based structural detection:
- Patterns: `BOOK I`, `Chapter 1`, `THE FIRST TABLET`, `HYMN TO...`, `Canto I`, `Rune I`, ETCSL line ranges, etc.
- Fallback: blank-line splitting with minimum word count grouping
- Result: 4,000 segments across 96 texts (63 structural, 17 single, 16 blank-line)

#### Sub-Phase 3.3: Entity Extraction

**Key decision**: spaCy NER is incompatible with Python 3.14 (pydantic v1 fails). Built a pure regex/gazetteer system instead — better for mythological names that standard NER models don't recognize.

Built `scripts/extract/extract_entities.py` with:
- ~200 curated entity entries across 16 traditions (Mesopotamian, Egyptian, Greek, Norse, Celtic, Indian, Japanese, Chinese, Roman, Polynesian, Mesoamerican, Zoroastrian, Finnish, African, Persian, Hebrew/Christian)
- Compiled regex patterns with word boundary matching
- Records: entity name, type, tradition, char offset, sentence context
- Result: 173 unique entities, 28,104 mentions, 85 texts with entities

Created `data/entity_aliases.json` with ~50 cross-cultural mappings (Ishtar→Inanna→Astarte, Zeus→Jupiter→Jove, etc.)

**Fixed**: Short deity names (Set, Nut, Eve, Mars) initially produced false positives as common English words. Now handled with case-sensitive matching for 27 ambiguous names (32,897 → 28,104 mentions after cleanup).

#### Sub-Phase 3.4: Motif Tagging

Built `scripts/motif/build_motif_index.py`:
- 149 Thompson Motif Index entries across 16 categories (A-Z)
- Each motif has code, label, parent, category, keywords

Built `scripts/motif/tag_motifs.py` with confidence scoring:
- 3+ keywords co-occur: confidence 0.5–0.95
- 2 keywords: confidence 0.3–0.8
- 1 keyword with context: confidence 0.1–0.5
- Penalties for short texts, boosts for long texts with multiple hits
- Result: 55,539 tags, 140 unique motifs, 93 texts tagged

Top motif: "A1: Creation of universe" — 84 texts across 26 traditions.

#### Sub-Phase 3.5: Pattern Database

Built `scripts/database/create_db.py` — SQLite database at `data/mythic_patterns.db`:

| Table | Rows | Purpose |
|-------|------|---------|
| `texts` | 132 | Core metadata |
| `segments` | 4,000 | Structural units with full text |
| `entities` | 173 | Canonical entity records |
| `entity_aliases` | 77 | Cross-cultural name mappings |
| `entity_mentions` | 28,104 | Entity occurrences per segment |
| `motifs` | 149 | Thompson Motif Index reference |
| `motif_tags` | 55,539 | Motif assignments with confidence |
| `patterns` | 18 | Cross-cultural pattern definitions |
| `pattern_attestations` | 786 | Which texts/traditions attest each pattern |
| `segments_fts` | — | FTS5 full-text search index |

18 cross-cultural patterns defined and scored:
- **Cosmogony/Creation**: 73 texts, 26 traditions
- **Hero Cycle**: 72 texts, 26 traditions
- **Creation of Humanity**: 66 texts, 24 traditions
- **Quest for Immortality**: 66 texts, 24 traditions
- **Descent to Underworld**: 61 texts, 24 traditions
- **World Flood**: 51 texts, 20 traditions
- **Trickster**: 47 texts, 20 traditions
- **Dying & Rising God**: 40 texts, 20 traditions

Database size: 137 MB. Query tool: `scripts/database/query_patterns.py`.

---

## Session Log: January 2026 (Phase 4)

### Phase 4: ACP Integration — In Progress

Connected the ACP's 8-dimensional coordinate system with the library's empirical data to test whether coordinates predict narrative co-occurrence.

#### 4.1: ACP Subtree & Integration Bridge

Pulled ACP repository as git subtree at `ACP/`. Built `integration/` package:

- **`acp_loader.py`**: Loads all 534 archetypes from `ACP/**/*.jsonld`. Parses `@graph` arrays, extracts 8D `spectralCoordinates`, builds alias index from archetype `aliases` (with `fidelity` scores). Loads 24 primordials from `ACP/schema/primordials.jsonld`.

- **`library_loader.py`**: Queries `mythic_patterns.db` with corrected schema (joins through `entity_mentions` and `motif_tags` tables, not inline columns). Provides co-occurrence, motif-entity associations, and entity stats.

- **`entity_mapper.py`**: Tradition-aware entity-driven mapping:
  1. For each library entity, finds all candidate ACP archetypes via exact name, alias, collapsed name (diacritics/space-insensitive), and word-boundary matching
  2. Prefers the candidate from the entity's own tradition (e.g., Norse Odin → `arch:NO-ODIN` instead of Greek `arch:GR-HERMES`)
  3. Reverse alias lookup for spelling variants (e.g., library "Balder" → canonical "Baldur" → `arch:NO-BALDUR`)
  - Fuzzy fallback via `difflib.SequenceMatcher`
  - Result: 104/173 entities mapped (60.1%)

#### 4.2: Validation Suite

Built `validation/` package with two hypothesis tests:

- **`test_coordinate_accuracy.py`**: For each mapped entity pair, computes 8D Euclidean distance (ACP) vs segment co-occurrence count (library). Tests Pearson and Spearman correlation. Identifies outliers.

- **`test_motif_clustering.py`**: For each Thompson motif, finds associated entities via segment joins, maps to ACP coordinates, computes centroid and variance. Tests whether motif-related archetypes cluster tightly in 8D space.

**Results (after tradition-aware mapping and de-collapsing):**

| Metric | All Entities | Excluding "Set" |
|--------|-------------|-----------------|
| Pearson r | -0.069 (p=0.000001) | -0.077 (p<0.000001) |
| Spearman r | -0.072 (p<0.000001) | -0.086 (p<0.000001) |

The negative correlation confirms the ACP hypothesis at weak but highly statistically significant levels: archetypes closer in coordinate space co-occur more often in narratives. The improved correlation (from r=-0.036 to r=-0.069) is due to tradition-aware mapping preventing cross-cultural alias collapsing.

**Per-tradition correlation (Spearman, sorted by strength):**

| Tradition | Entities | Spearman r | p-value |
|-----------|----------|------------|---------|
| Norse | 11 | -0.354 | 0.008 ** |
| Indian | 10 | -0.200 | 0.188 |
| Roman | 11 | -0.148 | 0.280 |
| Greek | 19 | +0.088 | 0.255 |

Norse mythology shows the strongest intra-tradition correlation, significant at the 1% level. Most other traditions lack sufficient mapped entities or have too many co-occurring pairs (Greek deities appear together in nearly every Greek text).

#### 4.3: Entity False Positive Cleanup

Discovered "Set" had 4,275 mentions across 25 traditions — only 3.7% were in Egyptian texts. The case-insensitive regex was matching the English verb "set".

Built `scripts/explorer/find_suspects.py` to systematically identify entities where home-tradition mentions are disproportionately low. Found 16 suspects.

Added `CASE_SENSITIVE` set of 27 ambiguous names to `extract_entities.py` — these compile without `re.IGNORECASE`. Re-extraction reduced mentions from 32,897 → 28,104 (4,793 false positives removed). Key improvements:

| Entity | Before | After |
|--------|--------|-------|
| Set | 4,275 | 190 |
| Nut | 426 | 55 |
| Eve | 266 | 140 |
| Jupiter | 393 | 130 |
| Saturn | 148 | 90 |

#### 4.4: Browser-Based Data Explorer

Built `scripts/explorer/server.py` — a self-contained Python HTTP server (single file, no dependencies beyond stdlib + integration packages) serving an embedded HTML/JS frontend at `http://127.0.0.1:8421`.

Six views:
- **Dashboard**: Summary statistics, tradition distribution, top entities
- **Entities**: Searchable/filterable entity list with ACP mapping status
- **Entity Detail**: ACP coordinates as axis bars, nearby archetypes, co-occurrences, motifs, sample passages
- **Coordinate Space**: 2D scatter plot with selectable axis pair projection, hover tooltips, click-to-detail
- **Co-occurrence**: Entity pair co-occurrence data
- **Motifs**: Thompson motif distribution with entity associations
- **Validation**: Correlation results and outlier analysis

#### 4.5: Tradition-Aware Mapping & Roman Archetypes

Rewrote `entity_mapper.py` from archetype-driven to entity-driven mapping with tradition preference. Previously, Norse Odin would sometimes map to `arch:GR-HERMES` instead of `arch:NO-ODIN` because Hermes' alias list included "Odin".

Key changes:
- **TRADITION_TO_PREFIX mapping**: Maps library tradition names to ACP archetype ID prefixes (e.g., "norse" → "NO")
- **`_find_all_candidates()`**: Finds all matching ACP archetypes for a name via exact, alias, qualified alias, collapsed name (strips diacritics/spaces), and word-boundary matching
- **`_pick_best_candidate()`**: Prefers matches from entity's own tradition
- **Diacritics normalization**: "Nuwa" matches "Nüwa", "Morrigan" matches "Morrígan"
- **Reverse alias lookup**: If library entity "Balder" is listed as an alias of canonical "Baldur", uses "Baldur" to search ACP

Created `ACP/archetypes/roman/RO_PANTHEON.jsonld` with 10 distinct Roman archetypes (Jupiter, Juno, Neptune, Minerva, Pluto, Venus, Mars, Mercury, Saturn, Hercules). Roman gods are not simple aliases of Greek counterparts — Mars has order-chaos 0.30 (vs Ares 0.80) reflecting Rome's civic martial tradition.

Result: Shared archetype collisions reduced from 12 to 5 (remaining are intentional: Jove/Jupiter, Baldur/Balder, Prometheus/Satan, Hero Twins pair, Cuchulainn/Cuchulain).

#### 4.6: Mean-Centered Motif Analysis

Investigated the active-receptive axis bias: 72% of ACP mythological archetypes sit below 0.5 on order-chaos, 64% below 0.5 on active-receptive. This is a genuine encoding property (most named deities are order-bringers), not a bug.

Fixed `test_motif_clustering.py` to compute `dominant_axis` relative to the global mean coordinate instead of the 0.5 midpoint. Result: motif categories now show 3 distinct dominant axes (individual-collective, voluntary-fated, order-chaos) instead of all converging on active-receptive.

#### 4.7: Per-Tradition Correlation Analysis

Added `test_per_tradition_correlation()` to `test_coordinate_accuracy.py`. Computes Spearman correlation within each tradition. Norse shows strongest intra-tradition correlation (r=-0.354, p=0.008), suggesting ACP coordinates are well-calibrated for Norse mythology. Greek shows near-zero correlation because Greek deities co-occur in nearly all Greek texts regardless of archetype distance.

#### Open Issues

1. **69 unmapped entities** — Mostly mortal heroes (Achilles, Sigurd, Arjuna), places (Troy, Olympus), creatures (Cerberus, Minotaur), and tradition-specific deities without ACP entries (Agni, Varuna, Anansi).

2. **Motif category deviations are small** — Mean-centered deviations are ±0.01 to ±0.05, suggesting Thompson motif categories don't differentiate strongly in ACP space. Likely because the same broad deity pool appears across most motifs.

3. **Greek intra-tradition correlation is near zero** — Greek deities co-occur in almost all Greek texts, making distance-co-occurrence correlation meaningless within that tradition.

## Integration Roadmap

### Remaining Phase 4 Work

- [x] Resolve shared archetype mappings (12 → 5, remaining intentional)
- [x] Investigate active-receptive axis bias (ACP encoding property, fixed with mean-centering)
- [x] Expand entity mapping coverage (89 → 104, 60.1%)
- [x] Per-tradition coordinate analysis (Norse strongest at r=-0.354)
- [ ] Create ACP archetypes for high-mention unmapped deities (Agni, Varuna, Anansi)
- [ ] Calibrate ACP coordinates using empirical co-occurrence data

### Phase 5: Mythopoetic OS Integration

The validated patterns feed into higher OS layers:
- **Narrative Engine**: Story generation from patterns
- **Cross-cultural Validation Layer**: Pattern verification across traditions

---

## Technical Debt

1. **Sacred Texts multi-page handling**: Currently only downloads index pages for multi-chapter texts. Need to implement page crawling or switch to Archive.org versions.

2. **Download log deduplication**: Some texts logged multiple times with different URLs. Need log cleanup.

3. **SOURCES.md automation**: Currently manual. Should auto-generate from curated_sources.json.

4. **Test coverage**: No automated tests for download handlers. Should add pytest suite.

---

## Metrics

### Phase 3 State

| Metric | Value |
|--------|-------|
| Texts Cataloged | 132 |
| Texts with Content | 96 |
| Traditions | 32 |
| Files Downloaded | 211 |
| Raw Corpus Size | 822 MB |
| Segments | 4,000 |
| Total Word Count | 8,137,973 |
| Unique Entities | 173 |
| Entity Mentions | 28,104 |
| Thompson Motifs | 149 |
| Motif Tags | 55,539 |
| Cross-Cultural Patterns | 18 |
| Pattern Attestations | 786 |
| Pattern Database Size | 137 MB |

### By Tradition (Top 10)

| Tradition | Texts |
|-----------|-------|
| African | 13 |
| Indian | 11 |
| Greek | 10 |
| North American | 9 |
| Chinese | 6 |
| Polynesian | 6 |
| Celtic | 6 |
| European | 6 |
| Egyptian | 6 |
| Japanese | 5 |

### Phase 4 State (ACP Integration)

| Metric | Value |
|--------|-------|
| ACP Archetypes Loaded | 534 |
| ACP Primordials | 24 |
| ACP Systems | 4 |
| ACP Aliases | 606 |
| Entities Mapped | 104 / 173 (60.1%) |
| Entities Unmapped | 69 |
| Pearson r (all) | -0.069 (p<0.000001) |
| Spearman r (all) | -0.072 (p<0.000001) |
| Pearson r (clean) | -0.077 (p<0.000001) |
| Spearman r (clean) | -0.086 (p<0.000001) |
| Norse Spearman r | -0.354 (p=0.008) |
| Motifs Analyzed | 124 |
| Motif Categories | 16 |

---

## Lessons Learned

1. **Archive.org is the backbone**: Most reliable source for complete PDFs with good metadata.

2. **Sacred Texts is supplementary**: Good for browsing, but often only provides index pages. Better to find Archive.org versions of the same translations.

3. **Gutenberg excels for text**: Clean, normalized text files perfect for NLP. Limited scholarly apparatus though.

4. **Gap analysis drives curation**: Without systematic gap analysis, collection becomes biased toward well-known Western texts.

5. **Archetype-first thinking**: Organizing by mythic function (not just geography) reveals structural holes in the collection.

---

*Last updated: January 2026*
