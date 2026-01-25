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

## Integration Roadmap

### Phase 3: Structured Extraction

Once the text corpus is stable, the next phase involves:

1. **Text Normalization**
   - Convert all formats to clean UTF-8 text
   - Remove headers, footers, page numbers
   - Standardize chapter/section markers

2. **Entity Extraction**
   - Named entity recognition for deities, heroes, places
   - Relationship mapping (parent-child, enemy, ally)
   - Cross-text entity resolution (Ishtar = Inanna = Astarte)

3. **Motif Tagging**
   - Thompson Motif Index alignment
   - Aarne-Thompson-Uther tale type classification
   - Custom archetypal tagging system

4. **Pattern Database**
   - Structured storage of extracted patterns
   - Confidence scoring based on attestation count
   - Geographic/temporal distribution tracking

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

### Final Session State

| Metric | Value |
|--------|-------|
| Texts Cataloged | 132 |
| Traditions | 32 |
| Files Downloaded | 211 |
| Total Size | 822 MB |
| Source URLs Curated | 250+ |
| Download Success Rate | ~95% |

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

*Last updated: January 2025*
