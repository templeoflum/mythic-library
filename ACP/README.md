# Archetypal Context Protocol (ACP)

A semantic framework for mapping archetypes across mythology, psychology, divination, and culture using an 8-dimensional coordinate system.

[![JSON-LD](https://img.shields.io/badge/format-JSON--LD-blue)](https://json-ld.org/)
[![Archetypes](https://img.shields.io/badge/archetypes-997-green)]()
[![Completeness](https://img.shields.io/badge/completeness-95%25%20rich+-brightgreen)]()
[![Version](https://img.shields.io/badge/version-0.3.0-yellow)]()
[![License](https://img.shields.io/badge/license-MIT-lightgrey)]()

---

## What is ACP?

The Archetypal Context Protocol is a relational ontology that positions archetypes—gods, symbols, psychological patterns, and cultural figures—in a shared coordinate space. This enables:

- **Cross-cultural comparison**: Find the Greek equivalent of a Norse god
- **Pattern discovery**: Which archetypes cluster together across systems?
- **Transformation mapping**: What does The Innocent evolve into?
- **Correspondence validation**: Does Tarot-Astrology mapping hold mathematically?

## The 8 Spectral Axes

Every archetype is positioned on eight continuous spectrums (0.0 to 1.0):

| Axis | 0.0 (Negative Pole) | 1.0 (Positive Pole) |
|------|---------------------|---------------------|
| **Order ↔ Chaos** | Structure, Law | Entropy, Freedom |
| **Creation ↔ Destruction** | Genesis, Building | Ending, Transformation |
| **Light ↔ Shadow** | Conscious, Known | Unconscious, Hidden |
| **Active ↔ Receptive** | Yang, Initiating | Yin, Responding |
| **Individual ↔ Collective** | Self, Ego | Group, Transpersonal |
| **Ascent ↔ Descent** | Sky, Spirit | Earth, Matter |
| **Stasis ↔ Transformation** | Preservation | Metamorphosis |
| **Voluntary ↔ Fated** | Free Choice | Destiny, Necessity |

## 22 Primordial Meta-Archetypes

Culture-transcendent patterns that all specific figures instantiate:

```
Creator    Destroyer    Preserver    Trickster    Hero       Self
Great Mother    Great Father    Divine Child    Lover    Warrior
Magician    Sovereign    Maiden    Crone    Wise Elder
Psychopomp    Healer    Rebel    Outcast    Ancestor    Monster    Twin
```

Cultural figures instantiate these with weights:
```json
{
  "name": "Hermes",
  "instantiates": [
    {"primordial": "trickster", "weight": 0.85},
    {"primordial": "psychopomp", "weight": 0.65},
    {"primordial": "magician", "weight": 0.45}
  ]
}
```

## Current Coverage

ACP currently includes **997 fully-mapped archetypes** across four domains:

**Enrichment Status (v0.3.0):**
- 88% Complete (838 entries at 80%+ completeness)
- 95% at "Rich" tier or above
- Mean completeness score: 84.5%
- 3,574 total relationships
- 1,840 cultural echo cross-links

### Mythological Pantheons (399 entries)
| Pantheon | Entries |
|----------|---------|
| Greek (Olympians) | 66 |
| Chinese | 21 |
| Hindu | 20 |
| Persian/Zoroastrian | 19 |
| African (Orisha) | 18 |
| Egyptian (Netjeru) | 18 |
| Incan/Andean | 18 |
| Japanese (Kami) | 18 |
| Mesoamerican | 18 |
| Polynesian | 18 |
| Slavic | 17 |
| Finnish (Kalevala) | 16 |
| Mesopotamian | 15 |
| Native American | 15 |
| Celtic | 14 |
| Norse (Aesir/Vanir) | 14 |
| Roman | 11 |
| Australian (Dreamtime) | 9 |
| **Buddhist** | 27 |
| **Vodou (Loa)** | 18 |

### Divination Systems (401 entries)
| System | Entries |
|--------|---------|
| I Ching Hexagrams | 65 |
| Tarot Minor Arcana | 61 |
| **Nakshatra (Lunar Mansions)** | 27 |
| Elder Futhark Runes | 25 |
| Tarot Major Arcana | 23 |
| **Ogham Tree Alphabet** | 20 |
| **Mayan Tzolk'in** | 20 |
| **Aztec Tonalpohualli** | 20 |
| **Alchemical Processes** | 15 |
| Astrology Houses | 13 |
| **Celtic Tree Calendar** | 13 |
| Zodiac Signs | 13 |
| **Chinese Zodiac** | 12 |
| **Vedic Rashi** | 12 |
| **Native American Totems** | 12 |
| Planets | 11 |
| Kabbalah Sephiroth | 11 |
| I Ching Trigrams | 9 |
| Chakras | 8 |
| Classical Elements | 6 |
| **Wu Xing (Chinese Elements)** | 5 |

### Psychology Systems (194 entries)
| System | Entries |
|--------|---------|
| Hero's Journey Stages | 19 |
| **MBTI Types** | 16 |
| **Socionics Types** | 16 |
| Jungian Core Archetypes | 13 |
| **Carol Pearson Archetypes** | 12 |
| **Commedia dell'Arte** | 10 |
| Enneagram Types | 10 |
| Spiral Dynamics | 9 |
| Vogler Character Archetypes | 9 |
| **Triple Goddess** | 9 |
| **KWML (Moore/Gillette)** | 8 |
| **Propp's Folktale Roles** | 8 |
| **Bolen's Gods** | 8 |
| **Seven Basic Plots** | 7 |
| **Bolen's Goddesses** | 7 |
| **Holland Codes (RIASEC)** | 6 |
| **Big Five (OCEAN)** | 5 |
| **Keirsey Temperaments** | 4 |
| **DISC Styles** | 4 |
| **Caroline Myss Survival** | 4 |

### Modern Systems (57 entries)
| System | Entries |
|--------|---------|
| Brand Archetypes | 13 |
| Superhero Archetypes | 13 |
| Digital/Internet Archetypes | 11 |
| Angelic Hierarchy | 10 |
| **Commedia dell'Arte** | 10 |

## Project Structure

```
ACP/
├── schema/                 # Core definitions
│   ├── primordials.jsonld  # 22 meta-archetypes
│   ├── axes.jsonld         # 8 spectral dimensions
│   ├── relationships.jsonld # 17 relationship types
│   └── dynamics.jsonld     # Physics-like rules
│
├── calibration/            # Reference frame
│   ├── origin.jsonld       # Center point (0.5 all axes)
│   ├── poles/              # 16 axis extremes
│   └── primordial_matrix.jsonld
│
├── archetypes/             # Cultural pantheons (v2.0 COMPLETE)
│   ├── greek/              # Olympians + heroes, creatures, primordials (66)
│   ├── norse/              # Aesir, Vanir, monsters (14)
│   ├── egyptian/           # Netjeru (18)
│   ├── hindu/              # Trimurti, Devas, asuras (20)
│   ├── celtic/             # Tuatha Dé Danann (14)
│   ├── japanese/           # Kami (18)
│   ├── chinese/            # Chinese pantheon (21)
│   ├── african/            # Orisha (18)
│   ├── mesopotamian/       # Sumerian/Babylonian (15)
│   ├── polynesian/         # Pacific deities (18)
│   ├── mesoamerican/       # Aztec/Maya (18)
│   ├── slavic/             # Slavic pantheon (17)
│   ├── native_american/    # Indigenous traditions (15)
│   ├── finnish/            # Kalevala heroes & spirits (16)
│   ├── australian/         # Dreamtime (9)
│   ├── incan/              # Andean deities (18)
│   ├── persian/            # Zoroastrian (19)
│   ├── roman/              # Roman pantheon (11)
│   ├── buddhist/           # Buddhist figures (27) — NEW
│   └── vodou/              # Vodou Loa (18) — NEW
│
├── divination/             # Symbolic systems (v2.0 COMPLETE)
│   ├── tarot/              # Major & Minor Arcana
│   ├── astrology/          # Zodiac, Planets, Houses
│   ├── iching/             # Trigrams, Hexagrams
│   ├── runes/              # Elder Futhark
│   ├── kabbalah/           # Sephiroth
│   ├── chakras/            # Energy centers
│   ├── elements/           # Western & Wu Xing — NEW
│   ├── zodiac/             # Chinese, Vedic, Nakshatra, Celtic — NEW
│   ├── calendar/           # Mayan, Aztec — NEW
│   ├── totems/             # Native American — NEW
│   ├── ogham/              # Tree alphabet — NEW
│   └── alchemy/            # Alchemical processes — NEW
│
├── psychology/             # Psychological frameworks (v2.0 COMPLETE)
│   ├── jungian/            # Core archetypes
│   ├── enneagram/          # 9 types
│   ├── narrative/          # Hero's Journey, Vogler, Propp, Plots — NEW
│   ├── developmental/      # Spiral Dynamics
│   ├── personality/        # MBTI, Socionics, Big Five, etc. — NEW
│   ├── archetypes/         # Pearson, Myss — NEW
│   └── gendered/           # KWML, Triple Goddess, Bolen — NEW
│
├── modern/                 # Contemporary patterns (v2.0 COMPLETE)
│   ├── cultural/           # Brand archetypes
│   ├── digital/            # Internet archetypes
│   ├── pop_culture/        # Superhero archetypes
│   ├── spiritual/          # Angelic hierarchy
│   └── theatrical/         # Commedia dell'Arte — NEW
│
├── legacy/                 # Archived planning docs
│
└── tools/                  # Validation & exploration
    ├── validate.js         # Schema validator
    ├── explorer.html       # Interactive browser
    └── validator.html      # Browser-based validator
```

## Quick Start

### Explore Archetypes (Browser)
```bash
cd ACP
python -m http.server 8000
# Open http://localhost:8000/tools/explorer.html
```

### Validate Data (Browser)
```bash
# Open http://localhost:8000/tools/validator.html
# Click "Run Validation"
```

### Validate Data (Node.js)
```bash
node tools/validate.js
```

### Run Enrichment Tools
```bash
# Audit completeness
python scripts/audit_archetype_completeness.py

# Generate enrichment queue
python scripts/enrichment_queue.py

# Auto-enrich from correspondences (dry run)
python scripts/enrich_from_correspondences.py --dry-run

# Apply enrichment changes
python scripts/enrich_from_correspondences.py --apply

# Validate enrichment quality
python scripts/validate_enrichment.py
```

## Query Examples

### Find Trickster Figures Across Systems
```
Query: All archetypes where instantiates includes "primordial:trickster" with weight > 0.7

Results:
- The Fool (Tarot) - 0.90
- Vogler Trickster - 1.0
- Jungian Trickster - 0.95
- The Viral Meme (Digital) - 0.80
- The Hacker (Digital) - 0.85
```

### Spectral Distance Query
```
Query: Archetypes within distance 0.3 of The Fool (Tarot)

Results:
- Divine Child (primordial) - 0.18
- The Innocent (Brand) - 0.15
- Jungian Child - 0.20
```

### Transformation Path
```
Query: Hero's Journey progression

Path: Ordinary World → Call to Adventure → ... → Freedom to Live
Axes involved: stasis-transformation, light-shadow, individual-collective
```

## Relationship Types

17 typed connections between archetypes:

| Relationship | Description |
|--------------|-------------|
| `POLAR_OPPOSITE` | Opposite end of a spectral axis |
| `SHADOW` | Repressed/distorted form |
| `COMPLEMENT` | Balances and completes |
| `EVOLUTION` | Transforms into (forward) |
| `DEVOLUTION` | Transforms into (backward) |
| `CULTURAL_ECHO` | Same pattern, different system |
| `INSTANTIATES` | Embodies meta-archetype |
| `TENSION` | Productive dialectical pull |
| `MIRRORS` | Same pattern, different domain |

## Validation Rules

The system enforces coherence:

- All coordinates must be in [0.0, 1.0]
- No two archetypes can occupy identical coordinates (min distance: 0.05)
- Polar opposites must differ by >0.5 on their axis
- Cultural echoes include fidelity scores (0.0-1.0)
- All archetypes must instantiate at least one primordial

## Use Cases

**Writers & Worldbuilders**
- Design characters with archetypal depth
- Map character arcs to transformation paths
- Find archetypal gaps in your narrative

**Researchers**
- Quantitative comparative mythology
- Pattern analysis across cultures
- Validate correspondence claims

**Therapists & Coaches**
- Map client patterns to archetypes
- Identify shadow dynamics
- Track transformation journeys

**AI & Narrative Engines** (via integration)
- Procedural character generation
- Story structure validation
- Dynamic myth generation

## Roadmap

**Target**: ~1,200 archetypes across 60+ systems | **v1.0** = complete data + API

### 0.1.0 ✅ Core Systems (315 archetypes)
- [x] Divination: Tarot, I Ching, Astrology, Runes, Kabbalah, Chakras, Elements
- [x] Psychology: Jungian, Enneagram, Hero's Journey, Vogler, Spiral Dynamics
- [x] Modern: Brand, Digital, Superhero, Angels
- [x] Interactive browser explorer & validation tooling

### 0.1.1 ✅ Cultural Pantheons (661 archetypes)
- [x] 18 pantheons (Greek, Norse, Egyptian, Celtic, Hindu, Japanese, Chinese, Mesopotamian, African, Mesoamerican, Slavic, Polynesian, Native American, Finnish, Australian, Incan, Persian, Roman)
- [x] Cross-pantheon relationship mapping

### 0.2.0 ✅ Major Expansion (938 archetypes)
- [x] **Additional Pantheons**: Buddhist (27), Vodou Loa (18)
- [x] **Alternate Zodiacs**: Chinese (12), Vedic Rashi (12), Nakshatra (27), Celtic Tree (13)
- [x] **Sacred Calendars**: Mayan Tzolk'in (20), Aztec Tonalpohualli (20), Native American Totems (12)
- [x] **Expanded Divination**: Wu Xing (5), Ogham (20), Alchemy (15)
- [x] **Psychology Frameworks**: MBTI (16), Socionics (16), Big Five (5), Holland (6), DISC (4), Keirsey (4), Pearson (12), Myss (4)
- [x] **Narrative Systems**: Propp's Roles (8), Seven Basic Plots (7), Commedia dell'Arte (10)
- [x] **Gendered Systems**: KWML (8), Triple Goddess (9), Bolen's Goddesses (7), Bolen's Gods (8)

### 0.2.1 ✅ Enrichment Phase 1
- [x] **Completeness**: 22% complete (210), 46% rich (429), 30% partial (280), 2% stub (19)
- [x] **Fields Added**: domains, keywords, narrativeRoles, coreFunction, symbolicCore, psychologicalMapping
- [x] **Infrastructure**: Automated enrichment scripts (`scripts/enrich_*.py`)
- [x] **Tarot Minor Arcana**: Fully enriched with Tier 3 fields (56 cards)
- [x] **Mean Score**: 64% (up from 44%)

### 0.2.2 ✅ Enrichment Phase 2
- [x] **culturalEchoes**: 1,840 cross-system links (98% → 5% missing)
- [x] **Bidirectional relationships**: 951 reverse links added
- [x] **Domain vocabulary**: 1,680 domains added
- [x] **Mean Score**: 76% (up from 64%)

### 0.3.0 ✅ Enrichment Phase 3 — Current
- [x] **Aliases**: 586 added (Roman, Germanic, Sanskrit variants)
- [x] **Correspondences**: 558 added (tarot, planet, element mappings)
- [x] **Descriptions**: 325 generated for all missing entries
- [x] **Completeness**: 88% complete (838), 7% rich (65), 3% partial (31)
- [x] **Target exceeded**: 95% entries at "rich" tier or above
- [x] **Mean Score**: 84.5% (up from 76%)

### 0.4.0 — Polish & API
- [ ] Expand domain vocabulary (1,274 unknown domain warnings)
- [ ] Add missing primordials (storyteller, culture-hero, guardian, etc.)
- [ ] Fix remaining orphan relationship targets (109)

### 1.0.0 — Production Release
- [ ] Complete ~1,200 archetype database
- [ ] REST/GraphQL API
- [ ] 3D spectral space visualization
- [ ] Community contribution system

*Note: ACP is a database and visualization tool. Narrative engine integration is planned as a separate project.*

## Contributing

This project uses JSON-LD for semantic web compatibility. To add an archetype:

1. Determine which primordial(s) it instantiates
2. Calculate spectral coordinates (0.0-1.0 on all 8 axes)
3. Define relationships to existing archetypes
4. Run validation: `node tools/validate.js`
5. Submit PR

See [CLAUDE.md](CLAUDE.md) for detailed schema documentation.

## Grounded in Fundamental Laws

The system is modeled on real physics principles:

- **Conservation**: Archetypal energy is conserved during transformation
- **Polar Attraction**: Opposites complete each other
- **Activation Energy**: Transformations require threshold conditions
- **Superposition**: Individuals hold multiple archetypal positions simultaneously

See [FUNDAMENTAL_LAWS.md](FUNDAMENTAL_LAWS.md) for the complete physics layer.

## License

MIT License - Use freely, attribute kindly.

---

*"All the gods, all the heavens, all the hells, are within you."* — Joseph Campbell
