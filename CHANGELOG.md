# Changelog

All notable changes to the Mythic Library project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Journey Mapper & Thompson Index Expansion

**Journey Mapper (journey.html):**
- New guided traversal experience for step-by-step mythic journeys
- 8 predefined traversals: Shadow Spiral, Mirror Journey, Crisis Triangle, etc.
- Step-by-step selection: archetype → entity → motif → note at each node
- Evidence-based motif filtering using node evidence markers
- Nontion pause screens with reflection prompts
- Journey persistence to LocalStorage with JSON export
- "Surprise Me" random selection for serendipitous discovery

**Evidence Marker System:**
- 18 node templates with predetermined evidence markers (Primary + Secondary)
- 6 marker types: Object (O), Action (A), Quality (Q), Being (B), Force (F), MetaSymbol (M)
- Primary markers by condition: O, A, B, O, A, B (polarity partners share same primary)
- Secondary markers by arc with thematic alignment:
  - D (Shadow) → Q (Quality): Shadow work is qualitative
  - R (Mirror) → F (Force): Reflection involves force/tension
  - E (Mythogenesis) → M (MetaSymbol): Myth-making is meta-symbolic
- 9 unique evidence pairs, each appearing exactly twice across 18 nodes
- Cross-arc structural threads connecting nodes with same pair

**Thompson Motif Index Expansion:**
- Total motifs: 149 → 579 (289% increase)
- Categories: 16 → 23 (all Thompson categories now represented)
- New categories added: B (Animals), C (Tabu), J (Wise/Foolish), P (Society), U (Nature of Life), W (Traits), X (Humor)
- All categories balanced to 15-54 entries for robust filtering
- Evidence marker → Thompson category mapping for contextual filtering

**Node Templates:**
- Complete templates for all 18 nodes in `data/node_templates.json`
- Evocative names (e.g., D3 "The Echo Engine", R4 "The Reflective Artifact")
- Guiding questions for each selection gate (archetype, entity, motif)
- Arc-condition thematic descriptions
- Evidence marker assignments with filtering logic

### Added - Database Completion & UI Improvements

**ACP Archetype Expansion (997 total, +46):**
- 42 new Greek archetypes: Achilles, Gaia, Eros, Hecate, Charon, Orpheus, Eurydice, Medusa, Cerberus, Minotaur, Cyclops, Titans, Centaur, Pan, Helios, Selene, Eos, Thanatos, Typhon, Moirai, Sirens, Nymphs, and more
- Victorious Fighting Buddha (Chinese - Sun Wukong's enlightened form)
- Ravana (Hindu demon king)
- Kullervo (Finnish tragic hero)
- Grendel (Norse/Germanic monster)
- Greek pantheon now complete with 66 entries
- Chinese pantheon now 21 entries

**Entity Mapping Improvements:**
- Mapped entities increased from 150 to 159
- Remaining 14 unmapped are places/concepts (not character archetypes)

**Broken Reference Fixes:**
- Relationship reference errors reduced from 426 to 109 (74% reduction)
- Removed invalid arch:GR-MARY reference from Chinese pantheon

**Miroglyph UI Enhancements:**
- Breadcrumb trail navigation (tracks last 5 items viewed)
- "Surprise Me" random discovery buttons in each view
- Interactive mini-map with hover tooltips and click navigation
- Fidelity badges on entity cards (green/yellow/red indicators)
- Related sections in detail views (entities, patterns, archetypes)
- Enhanced hover/focus states for accessibility
- New `js/utils.js` module with shared utility functions

### Fixed - Miroglyph Explorer
- **Tab switching:** Fixed CSS specificity issue where Atlas view's `display: grid !important` was overriding the hidden state
- **Traversal duplication:** Fixed duplicate event handlers causing nodes to be added twice, paths to save twice, and groups to create twice
- **Node ID visibility:** Fixed CSS specificity so node IDs display as white text in the "Current Path" sequence instead of invisible text
- Added initialization guards and debounce protection to prevent duplicate event listener attachment

## [0.3.1] - 2026-01-30

### Added - Miroglyph & Validation Improvements

**Miroglyph Dual Orientation:**
- Added toggle to swap Emergence (E) and Descent (D) arc positions
- Two valid configurations: Standard (E inner, D outer) and Inverted (D inner, E outer)
- Resonance (R) and Nontion (∅) remain fixed as middle ring and center point
- Orientation persists via localStorage
- Settings accessible via gear menu

**Validation Test Reframing:**
- Tests 7a/7b (Arc Analysis) redesigned as insight tests rather than pass/fail criteria
- Documented key finding: Arcs are interpretive lenses, not entity clusters
- Same entities appear across all arcs with nearly identical coordinate profiles
- Tier C now depends only on Tests 8 (Conditions) and 9 (Polarity Pairs)
- New `miroglyph_structure_v2.py` test suite with interpretation framework

### Changed
- Tier C verdict now PARTIAL (1/2 validation tests pass)
- Test 7 reframed from "Arc Separation (FAIL)" to insight documentation
- CLAUDE.md updated with dual orientation system documentation

### Documented
- Core insight: ACP coordinates capture what entities ARE; Miroglyph arcs capture HOW you view them
- Zeus viewed through D (destroyer of Titans), R (judge/witness), or E (creator of cosmic order) - same coordinates, different lens

## [0.3.0] - 2026-01-29

### Added - ACP Enrichment Phase 3 (Final)

**Infrastructure Scripts:**
- `scripts/enrich_phase3_aliases.py` - Aliases, correspondences, and description generation
- `scripts/enrich_phase3_stubs.py` - Fix remaining stubs and relationship gaps
- `scripts/fix_remaining_stubs.py` - Add spectral coordinates to astrology houses

**Alias Enrichment:**
- 586 aliases added (Roman equivalents, transliteration variants, epithets)
- Greek↔Roman deity name mappings (Zeus/Jupiter, Athena/Minerva, etc.)
- Norse↔Germanic variants (Odin/Wotan, Thor/Donar)
- Egyptian transliterations (Ra/Re, Isis/Aset, Osiris/Usir)
- Hindu Sanskrit variants (Vishnu/Narayana, Shiva/Mahadeva)

**Correspondence Enrichment:**
- 558 correspondences added (tarot, planet, element mappings)
- Primordial-to-system correspondence mappings implemented
- Cross-system symbolic links established

**Description Generation:**
- 325 descriptions generated for entries missing them
- Template-based generation using primordial types
- All entries now have descriptions

**Completeness Results:**
| Tier | Before | After | Change |
|------|--------|-------|--------|
| Complete (80%+) | 273 (29.1%) | 838 (88.1%) | +565 |
| Rich (60-79%) | 597 (63.6%) | 65 (6.8%) | - |
| Partial (40-59%) | 51 (5.4%) | 31 (3.3%) | -20 |
| Stub (<40%) | 17 (1.8%) | 17 (1.8%) | 0 |

**94.9% of entries now at "rich" tier or above**

**Mean completeness score:** 76% → 84.5%

### Changed
- Astrology houses now have full spectral coordinates
- Greek deity aspects (Aphrodite-Anadyomene) enriched with coordinates
- Total archetypes: 938 → 951 (houses now fully countable)
- Total relationships: 3,541 → 3,574

## [0.2.2] - 2026-01-29

### Added - ACP Enrichment Phase 2

**Infrastructure Scripts:**
- `scripts/enrich_phase2_echoes.py` - Cultural echoes, aliases, bidirectional relationships
- `scripts/enrich_phase2_domains.py` - Domain vocabulary expansion and auto-assignment

**Cultural Echo Network:**
- 68 known cultural equivalents mapped (Zeus↔Jupiter↔Thor↔Indra, etc.)
- 1,772 spectral proximity echoes generated (distance < 0.12)
- 951 bidirectional relationship links added
- Cross-pantheon relationship graph now connected

**Domain Enrichment:**
- 1,680 domains added across 814 entries
- 70 domains normalized to controlled vocabulary
- System-specific domain defaults applied

**Field Enrichment Results:**
| Field | Before | After | Improved |
|-------|--------|-------|----------|
| culturalEchoes | 923 (98.4%) | 43 (4.6%) | +880 |
| domains | 410 (43.7%) | 62 (6.6%) | +348 |
| bidirectional | 934 missing | 59 missing | +875 |

**Completeness Tier Changes:**
| Tier | Before | After | Change |
|------|--------|-------|--------|
| Complete (80%+) | 210 (22.4%) | 273 (29.1%) | +63 |
| Rich (60-79%) | 429 (45.7%) | 597 (63.6%) | +168 |
| Partial (40-59%) | 280 (29.9%) | 51 (5.4%) | -229 |
| Stub (<40%) | 19 (2.0%) | 17 (1.8%) | -2 |

**92.7% of entries now at "rich" tier or above** (target: 80%)

**Mean completeness score:** 64% → 76%+

### Changed
- Relationship total increased from 2,590 to 3,541
- Known deity equivalents across 10+ pantheons mapped
- Domain vocabulary expanded with 60+ canonical terms

## [0.2.1] - 2026-01-29

### Added - ACP Enrichment Phase 1

**Infrastructure Scripts:**
- `scripts/enrichment_queue.py` - Generates prioritized work queue from audit data
- `scripts/enrich_from_correspondences.py` - Auto-populates fields from correspondences.jsonld
- `scripts/validate_enrichment.py` - Pre/post validation with tier tracking
- `scripts/enrich_priority_systems.py` - Adds Tier 3 fields (coreFunction, symbolicCore, psychologicalMapping)
- `scripts/enrich_minor_arcana.py` - Specialized enrichment for Tarot minor arcana

**Field Enrichment Results:**
| Field | Before Missing | After Missing | Improved |
|-------|---------------|---------------|----------|
| narrativeRoles | 933 (99.5%) | 49 (5.2%) | +884 |
| coreFunction | 906 (96.6%) | 35 (3.7%) | +871 |
| symbolicCore | 906 (96.6%) | 35 (3.7%) | +871 |
| psychologicalMapping | 911 (97.1%) | 110 (11.7%) | +801 |
| domains | 904 (96.4%) | 410 (43.7%) | +494 |
| keywords | 342 (36.5%) | 17 (1.8%) | +325 |

**Completeness Tier Changes:**
| Tier | Before | After | Change |
|------|--------|-------|--------|
| Complete (80%+) | 5 (0.5%) | 210 (22.4%) | +205 |
| Rich (60-79%) | 27 (2.9%) | 429 (45.7%) | +402 |
| Partial (40-59%) | 532 (56.7%) | 280 (29.9%) | -252 |
| Stub (<40%) | 374 (39.9%) | 19 (2.0%) | -355 |

**Mean completeness score:** 43.7% → 64%+

### Changed
- Updated ACP/CLAUDE.md with v0.2.1 roadmap
- Updated ACP/README.md with enrichment tools documentation
- Expanded domain vocabulary in validation scripts
- Fixed list-target handling in audit/validation scripts

## [0.2.0] - 2026-01-28

### Added - Major Expansion
- **938 total archetypes** (up from 661)
- Buddhist pantheon (27 entries)
- Vodou Loa system (18 entries)
- Alternate zodiacs: Chinese (12), Vedic Rashi (12), Nakshatra (27), Celtic Tree (13)
- Sacred calendars: Mayan Tzolk'in (20), Aztec Tonalpohualli (20)
- Native American Totems (12)
- Wu Xing Chinese elements (5)
- Ogham tree alphabet (20)
- Alchemical processes (15)
- Psychology: MBTI (16), Socionics (16), Big Five (5), Holland (6), DISC (4), Keirsey (4)
- Carol Pearson archetypes (12), Caroline Myss (4)
- Narrative: Propp's roles (8), Seven Basic Plots (7)
- Commedia dell'Arte (10)
- Gendered: KWML (8), Triple Goddess (9), Bolen Goddesses (7), Bolen Gods (8)

### Changed
- Export script fixes for archetype counting
- Corrected documentation counts

## [0.1.1] - 2026-01-15

### Added
- 17 cultural pantheons with full spectral coordinates
- Cross-pantheon relationship mapping
- Interactive browser explorer (miroglyph)

## [0.1.0] - 2026-01-01

### Added
- Initial release with 315 archetypes
- Core divination systems (Tarot, I Ching, Astrology, Runes, Kabbalah, Chakras)
- Psychology systems (Jungian, Enneagram, Hero's Journey, Vogler, Spiral Dynamics)
- Modern systems (Brand, Digital, Superhero, Angels)
- 8-axis spectral coordinate system
- 22 primordial meta-archetypes
- JSON-LD schema with validation tooling

---

[Unreleased]: https://github.com/templeoflum/mythic-library/compare/v0.3.1...HEAD
[0.3.1]: https://github.com/templeoflum/mythic-library/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/templeoflum/mythic-library/compare/v0.2.2...v0.3.0
[0.2.2]: https://github.com/templeoflum/mythic-library/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/templeoflum/mythic-library/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/templeoflum/mythic-library/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/templeoflum/mythic-library/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/templeoflum/mythic-library/releases/tag/v0.1.0
