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
- Result: 173 unique entities, 32,897 mentions, 85 texts with entities

Created `data/entity_aliases.json` with ~50 cross-cultural mappings (Ishtar→Inanna→Astarte, Zeus→Jupiter→Jove, etc.)

**Known issue**: Short deity names (Set, Nut, Eve, Mars) produce false positives as common English words. Handled with exclusion lists in queries.

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
| `entity_mentions` | 32,897 | Entity occurrences per segment |
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

## Integration Roadmap

### Phase 4: Mythopoetic OS Integration

The extracted patterns feed into higher OS layers:
- **ACP (Archetypal Compression Protocol)**: Pattern encoding
- **Narrative Engine**: Story generation from patterns
- **Validation Layer**: Cross-cultural pattern verification

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
| Entity Mentions | 32,897 |
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

---

## Lessons Learned

1. **Archive.org is the backbone**: Most reliable source for complete PDFs with good metadata.

2. **Sacred Texts is supplementary**: Good for browsing, but often only provides index pages. Better to find Archive.org versions of the same translations.

3. **Gutenberg excels for text**: Clean, normalized text files perfect for NLP. Limited scholarly apparatus though.

4. **Gap analysis drives curation**: Without systematic gap analysis, collection becomes biased toward well-known Western texts.

5. **Archetype-first thinking**: Organizing by mythic function (not just geography) reveals structural holes in the collection.

---

*Last updated: January 2026*
