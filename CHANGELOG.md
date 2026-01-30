# Changelog

All notable changes to the Mythic Library project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/templeoflum/mythic-library/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/templeoflum/mythic-library/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/templeoflum/mythic-library/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/templeoflum/mythic-library/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/templeoflum/mythic-library/releases/tag/v0.1.0
