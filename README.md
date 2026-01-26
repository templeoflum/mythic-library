# Archetypal Context Protocol (ACP)

A semantic framework for mapping archetypes across mythology, psychology, divination, and culture using an 8-dimensional coordinate system.

[![JSON-LD](https://img.shields.io/badge/format-JSON--LD-blue)](https://json-ld.org/)
[![Archetypes](https://img.shields.io/badge/archetypes-580-green)]()
[![Version](https://img.shields.io/badge/version-0.1.1-yellow)]()
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

ACP currently includes **580 fully-mapped archetypes** across four domains:

### Divination Systems (218 entries)
| System | Entries |
|--------|---------|
| Tarot Major Arcana | 22 |
| Tarot Minor Arcana | 56 |
| I Ching Trigrams | 8 |
| I Ching Hexagrams | 64 |
| Zodiac Signs | 12 |
| Planets | 10 |
| Sephiroth | 10 |
| Chakras | 7 |
| Elder Futhark Runes | 24 |
| Classical Elements | 5 |

### Psychology Systems (55 entries)
| System | Entries |
|--------|---------|
| Jungian Core Archetypes | 12 |
| Enneagram Types | 9 |
| Hero's Journey Stages | 18 |
| Vogler Character Archetypes | 8 |
| Spiral Dynamics | 8 |

### Modern Systems (43 entries)
| System | Entries |
|--------|---------|
| Brand Archetypes | 12 |
| Digital/Internet Archetypes | 10 |
| Superhero Archetypes | 12 |
| Angelic Hierarchy | 9 |

### Mythological Pantheons (265 entries)
| Pantheon | Entries |
|----------|---------|
| Greek (Olympians) | 22 |
| Norse (Aesir/Vanir) | 12 |
| Egyptian (Netjeru) | 17 |
| Celtic | 13 |
| Hindu | 15 |
| Japanese (Kami) | 17 |
| Chinese | 19 |
| Mesopotamian | 13 |
| African (Orisha) | 16 |
| Mesoamerican | 17 |
| Slavic | 16 |
| Polynesian | 17 |
| Native American | 14 |
| Finnish (Kalevala) | 14 |
| Australian (Dreamtime) | 8 |
| Incan/Andean | 17 |
| Persian/Zoroastrian | 18 |

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
├── archetypes/             # Cultural pantheons (v1.1 COMPLETE)
│   ├── greek/              # Olympians (22)
│   ├── norse/              # Aesir, Vanir (12)
│   ├── egyptian/           # Netjeru (17)
│   ├── hindu/              # Trimurti, Devas (15)
│   ├── celtic/             # Tuatha Dé Danann (13)
│   ├── japanese/           # Kami (17)
│   ├── chinese/            # Chinese pantheon (19)
│   ├── african/            # Orisha (16)
│   ├── mesopotamian/       # Sumerian/Babylonian (13)
│   ├── polynesian/         # Pacific deities (17)
│   ├── mesoamerican/       # Aztec/Maya (17)
│   ├── slavic/             # Slavic pantheon (16)
│   ├── native_american/    # Indigenous traditions (14)
│   ├── finnish/            # Kalevala (14)
│   ├── australian/         # Dreamtime (8)
│   ├── incan/              # Andean deities (17)
│   └── persian/            # Zoroastrian (18)
│
├── divination/             # Symbolic systems (v1.0 COMPLETE)
│   ├── tarot/              # Major & Minor Arcana
│   ├── astrology/          # Zodiac, Planets
│   ├── iching/             # Trigrams, Hexagrams
│   ├── runes/              # Elder Futhark
│   ├── kabbalah/           # Sephiroth
│   └── chakras/            # Energy centers
│
├── psychology/             # Psychological frameworks (v1.0 COMPLETE)
│   ├── jungian/            # Core archetypes
│   ├── enneagram/          # 9 types
│   ├── narrative/          # Hero's Journey, Vogler
│   └── developmental/      # Spiral Dynamics
│
├── modern/                 # Contemporary patterns (v1.0 COMPLETE)
│   ├── cultural/           # Brand archetypes
│   ├── digital/            # Internet archetypes
│   ├── pop_culture/        # Superhero archetypes
│   └── spiritual/          # Angelic hierarchy
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

### 0.1.1 ✅ Cultural Pantheons (580 archetypes) — Current
- [x] 17 pantheons (Greek, Norse, Egyptian, Celtic, Hindu, Japanese, Chinese, Mesopotamian, African, Mesoamerican, Slavic, Polynesian, Native American, Finnish, Australian, Incan, Persian)
- [x] Cross-pantheon relationship mapping

### 0.2.0 — Additional Pantheons (~70 archetypes)
- [ ] Roman (Dii Consentes) — ~20 entries
- [ ] Buddhist (Buddhas, Bodhisattvas, Wrathful Deities) — ~30 entries
- [ ] Vodou (Rada, Petro, Ghede Loa) — ~19 entries

### 0.3.0 — Alternate Zodiacs & Calendars (~115 archetypes)
- [ ] Chinese Zodiac, Vedic Rāśis, Nakṣatras, Celtic Tree Zodiac
- [ ] Mayan Tzolk'in, Aztec Tōnalpōhualli, Native American Totems

### 0.4.0 — Expanded Divination (~40 archetypes)
- [ ] Chinese Wu Xing, Ogham Tree Alphabet, Alchemical Archetypes

### 0.5.0 — Psychology Frameworks (~80 archetypes)
- [ ] MBTI, Socionics, Keirsey, Four Temperaments, DISC, Big Five
- [ ] Holland Codes, Transactional Analysis, Carol Pearson, Psychosynthesis

### 0.6.0 — Narrative & Literary (~25 archetypes)
- [ ] Propp's Roles, Seven Basic Plots, Commedia dell'Arte

### 0.7.0 — Gendered Archetype Systems (~35 archetypes)
- [ ] KWML, Triple Goddess, Bolen's Gods/Goddesses, Caroline Myss

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
