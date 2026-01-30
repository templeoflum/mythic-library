# Archetypal Context Protocol (ACP)

## Project Overview

The **Archetypal Context Protocol** is a relational symbolic framework for cataloging, generating, and interpreting archetypes across cultures, systems, and media. It uses **JSON-LD** for semantic web compatibility and enables multi-dimensional querying through spectral positioning and typed relationships.

**Version**: 0.2.0 (Major Expansion)
**Total Archetypes**: 938 entries with full spectral coordinates
**Target**: ~1,200 archetypes for v1.0 release

## Architecture (ORAS v2.0)

The project uses the **Optimal Relational Archetype Schema (ORAS)** - a graph-based structure where archetypes are nodes and relationships are first-class citizens.

### Directory Structure

```
ACP/
├── schema/                    # Core schema definitions
│   ├── ACP_CONTEXT.jsonld     # JSON-LD context (namespace definitions)
│   ├── axes.jsonld            # 8 spectral axes definitions
│   ├── relationships.jsonld   # 17 relationship type ontology
│   ├── primordials.jsonld     # ~22 meta-archetypes (with shadow as modifier)
│   ├── correspondences.jsonld # Cross-system mappings
│   └── dynamics.jsonld        # Mathematical/geometric/physics foundations
│
├── calibration/               # Reference frame
│   ├── origin.jsonld          # Center point (0.5 all axes)
│   ├── poles/                 # 16 axis extremes
│   ├── geodesics/             # Transformation paths
│   └── primordial_matrix.jsonld
│
├── divination/                # Domain: Divination Systems (401 entries)
│   ├── tarot/
│   │   ├── major_arcana.jsonld    # 23 entries - COMPLETE
│   │   └── minor_arcana.jsonld    # 61 entries - COMPLETE
│   ├── iching/
│   │   ├── trigrams.jsonld        # 9 entries - COMPLETE
│   │   └── hexagrams.jsonld       # 65 entries - COMPLETE
│   ├── astrology/
│   │   ├── zodiac.jsonld          # 13 entries - COMPLETE
│   │   ├── planets.jsonld         # 11 entries - COMPLETE
│   │   └── houses.jsonld          # 13 entries - COMPLETE
│   ├── runes/
│   │   └── elder_futhark.jsonld   # 25 entries - COMPLETE
│   ├── kabbalah/
│   │   └── sephiroth.jsonld       # 11 entries - COMPLETE
│   ├── chakras/
│   │   └── energy_centers.jsonld  # 8 entries - COMPLETE
│   ├── elements/
│   │   ├── classical_western.jsonld # 6 entries - COMPLETE
│   │   └── wu_xing.jsonld         # 5 entries - NEW
│   ├── zodiac/
│   │   ├── chinese_zodiac.jsonld  # 12 entries - NEW
│   │   ├── vedic_rashi.jsonld     # 12 entries - NEW
│   │   ├── nakshatra.jsonld       # 27 entries - NEW
│   │   └── celtic_tree.jsonld     # 13 entries - NEW
│   ├── calendar/
│   │   ├── mayan_tzolkin.jsonld   # 20 entries - NEW
│   │   └── aztec_tonalpohualli.jsonld # 20 entries - NEW
│   ├── totems/
│   │   └── native_american.jsonld # 12 entries - NEW
│   ├── ogham/
│   │   └── feda.jsonld            # 20 entries - NEW
│   └── alchemy/
│       └── processes.jsonld       # 15 entries - NEW
│
├── psychology/                # Domain: Psychology Systems (194 entries)
│   ├── jungian/
│   │   └── core_archetypes.jsonld # 13 entries - COMPLETE
│   ├── enneagram/
│   │   └── types.jsonld           # 10 entries - COMPLETE
│   ├── narrative/
│   │   ├── heros_journey.jsonld   # 19 entries - COMPLETE
│   │   ├── vogler_archetypes.jsonld # 9 entries - COMPLETE
│   │   ├── propp_roles.jsonld     # 8 entries - NEW
│   │   └── seven_plots.jsonld     # 7 entries - NEW
│   ├── developmental/
│   │   └── spiral_dynamics.jsonld # 9 entries - COMPLETE
│   ├── personality/
│   │   ├── mbti.jsonld            # 16 entries - NEW
│   │   ├── socionics.jsonld       # 16 entries - NEW
│   │   ├── big_five.jsonld        # 5 entries - NEW
│   │   ├── holland.jsonld         # 6 entries - NEW
│   │   ├── disc.jsonld            # 4 entries - NEW
│   │   └── keirsey.jsonld         # 4 entries - NEW
│   ├── archetypes/
│   │   ├── pearson.jsonld         # 12 entries - NEW
│   │   └── myss.jsonld            # 4 entries - NEW
│   └── gendered/
│       ├── kwml.jsonld            # 8 entries - NEW
│       ├── triple_goddess.jsonld  # 9 entries - NEW
│       ├── bolen_goddesses.jsonld # 7 entries - NEW
│       └── bolen_gods.jsonld      # 8 entries - NEW
│
├── modern/                    # Domain: Modern Systems (57 entries)
│   ├── cultural/
│   │   └── brand_archetypes.jsonld    # 13 entries - COMPLETE
│   ├── digital/
│   │   └── internet_archetypes.jsonld # 11 entries - COMPLETE
│   ├── pop_culture/
│   │   └── superhero.jsonld           # 13 entries - COMPLETE
│   ├── spiritual/
│   │   └── angels.jsonld              # 10 entries - COMPLETE
│   └── theatrical/
│       └── commedia.jsonld            # 10 entries - NEW
│
├── archetypes/                # Domain: Mythological (354 entries) - COMPLETE
│   ├── greek/                 # 24 entries
│   ├── norse/                 # 13 entries
│   ├── egyptian/              # 18 entries
│   ├── celtic/                # 14 entries
│   ├── hindu/                 # 19 entries
│   ├── japanese/              # 18 entries
│   ├── chinese/               # 20 entries
│   ├── mesopotamian/          # 15 entries
│   ├── african/               # 18 entries
│   ├── mesoamerican/          # 18 entries
│   ├── slavic/                # 17 entries
│   ├── polynesian/            # 18 entries
│   ├── native_american/       # 15 entries
│   ├── finnish/               # 15 entries
│   ├── australian/            # 9 entries
│   ├── incan/                 # 18 entries
│   ├── persian/               # 19 entries
│   ├── roman/                 # 11 entries
│   ├── buddhist/              # 27 entries - NEW
│   └── vodou/                 # 18 entries - NEW
│
├── tools/                     # Validation & Exploration
│   ├── validate.js            # Node.js validation script
│   ├── derive_coordinates.js  # Coordinate derivation algorithm
│   ├── explorer.html          # Interactive browser explorer
│   └── validator.html         # Browser-based validator
│
└── legacy/                    # Original sketch files (reference only)
    └── Arechtypal Context Protocol_*.md
```

## The 8 Spectral Axes

Every archetype is positioned on these continuous spectrums (0.0 to 1.0):

| Axis | Negative Pole (0.0) | Positive Pole (1.0) |
|------|---------------------|---------------------|
| **Order-Chaos** | Structure, Law, Pattern | Entropy, Freedom, Dissolution |
| **Creation-Destruction** | Genesis, Building, Growth | Ending, Breaking, Transformation |
| **Light-Shadow** | Conscious, Revealed, Known | Unconscious, Hidden, Repressed |
| **Active-Receptive** | Yang, Projective, Initiating | Yin, Absorptive, Responding |
| **Individual-Collective** | Self, Ego, Personal | Group, Unconscious, Transpersonal |
| **Ascent-Descent** | Sky, Spirit, Transcendence | Earth, Matter, Immanence |
| **Stasis-Transformation** | Preservation, Continuity | Change, Metamorphosis, Death-Rebirth |
| **Voluntary-Fated** | Free Choice, Agency, Self-determination | Destiny, Necessity, Cosmic Inevitability |

The 8th axis (Voluntary-Fated) captures whether an archetype CHOOSES or IS CHOSEN - the tension between free will and determinism that runs through all mythology.

## Entry Structure

Every archetype entry follows this structure:

```json
{
  "@id": "system:identifier",
  "@type": "Archetype",
  "name": "Human-readable name",
  "description": "Brief description of the archetype",
  "keywords": ["keyword1", "keyword2", "keyword3"],

  "spectralCoordinates": {
    "order-chaos": 0.45,
    "creation-destruction": 0.30,
    "light-shadow": 0.25,
    "active-receptive": 0.20,
    "individual-collective": 0.35,
    "ascent-descent": 0.40,
    "stasis-transformation": 0.65,
    "voluntary-fated": 0.38
  },

  "instantiates": [
    {"primordial": "primordial:hero", "weight": 0.85, "aspects": ["courage", "sacrifice"]},
    {"primordial": "primordial:trickster", "weight": 0.55, "aspects": ["boundary-crossing"]}
  ],

  "relationships": [
    {"type": "POLAR_OPPOSITE", "target": "system:other", "axis": "light-shadow"},
    {"type": "CULTURAL_ECHO", "target": "other_system:similar", "fidelity": 0.8},
    {"type": "EVOLUTION", "target": "system:next_stage", "note": "Transforms through trials"}
  ]
}
```

## Relationship Types

Key relationship types connecting archetypes:

- **POLAR_OPPOSITE** - Opposite end of a spectral axis (requires `axis` field)
- **SHADOW** - Repressed/distorted form of same energy
- **COMPLEMENT** - Balances and completes
- **EVOLUTION / DEVOLUTION** - Transforms into (with direction)
- **CULTURAL_ECHO** - Same pattern in different system (includes `fidelity` score)
- **SYNTHESIS** - Combines to form new archetype
- **INSTANTIATES** - Cultural figure embodies meta-archetype
- **CONTAINS / CONTAINED_BY** - Hierarchical inclusion
- **MIRRORS** - Same pattern in different domain
- **TENSION** - Productive dialectical pull
- **CONSTELLATION** - Group that appears together with emergent properties

## Primordial Meta-Archetypes

~22 culture-transcendent patterns that all specific archetypes instantiate:

- Creator, Destroyer, Preserver
- Trickster, Hero, Self
- Great Mother, Great Father, Divine Child
- Lover, Warrior, Magician, Sovereign
- Maiden, Crone, Wise Elder
- Psychopomp, Healer, Rebel
- Outcast, Ancestor, Monster, Twin

### Weighted Multi-Instantiation

Archetypes can instantiate multiple primordials with different weights:

```json
"instantiates": [
  {"primordial": "primordial:trickster", "weight": 0.85, "aspects": ["cunning", "boundary-crossing"]},
  {"primordial": "primordial:psychopomp", "weight": 0.65, "aspects": ["soul-guide", "threshold-crossing"]},
  {"primordial": "primordial:magician", "weight": 0.45, "aspects": ["hidden-knowledge"]}
]
```

## Validation Rules

The system enforces coherence:

- All coordinates must be in [0.0, 1.0] and complete (8 axes)
- No two distinct archetypes can have identical coordinates (distance > 0.05)
- Polar opposites must have difference > 0.5 on the specified axis
- Cultural echoes should have euclidean distance < 0.5 for high fidelity
- All entries must instantiate at least one Primordial with valid weights (0.0-1.0)

## Using the Tools

### Interactive Explorer
```bash
cd ACP
python -m http.server 8000
# Open http://localhost:8000/tools/explorer.html
```

Features:
- Search by name or keyword
- Filter by system
- View spectral coordinates as visual bars
- Navigate relationships by clicking

### Browser Validator
```bash
# Open http://localhost:8000/tools/validator.html
# Click "Run Validation"
```

Features:
- Entry counts by system
- Coordinate distribution statistics
- Error and warning display
- No Node.js required

### Node.js Validator
```bash
node tools/validate.js
```

Features:
- Coordinate bounds checking
- Collision detection
- Bidirectional relationship checking
- Reference validity checking
- Summary statistics

## Working with the Schema

### Adding a new archetype:

1. Determine which primordial(s) it instantiates (with weights and aspects)
2. Calculate spectral coordinates (0.0-1.0 on all **8** axes)
3. Define relationships to existing archetypes
4. Add keywords for searchability
5. Add to appropriate system file
6. Run validation: `node tools/validate.js` or use browser validator

### Best practices:

- Use JSON-LD `@id` references for all links (format: `system:identifier`)
- Include `fidelity` scores (0.0-1.0) for cultural echoes
- Add `axis` field for POLAR_OPPOSITE relationships
- Use `note` fields to explain relationship reasoning
- Keywords should be lowercase, single words or hyphenated
- Preserve cultural nuance in descriptions

### Correspondence Mapping Checklist:

When adding cross-system correspondences:
1. Verify structural isomorphism (relationships mirror each other)
2. Check spectral alignment (distance < 0.3 for strong correspondence)
3. Confirm functional equivalence (same narrative role)
4. Note provenance (TRAD/SYNC/SCHOL/ORIG) and confidence level
5. Validate transitivity (if A↔B and B↔C, then A should relate to C)

## Target Audiences

- Writers & worldbuilders (character design, world mythology)
- Ritual designers & spiritual practitioners
- AI developers & narrative engine architects
- Therapists, coaches, and symbolic analysts
- Researchers in comparative mythology

## Roadmap

**Target**: ~1,200 archetypes | **v1.0** = complete data + API

### 0.1.0 ✅ Core Systems (315 archetypes)
- Divination, Psychology, Modern systems + browser tools

### 0.1.1 ✅ Cultural Pantheons (580 archetypes) — Current
- 17 pantheons with cross-system relationship mapping

### 0.2.0 — Additional Pantheons (+70)
Roman, Buddhist, Vodou Loa

### 0.3.0 — Alternate Zodiacs (+115)
Chinese, Vedic, Nakṣatras, Celtic, Mayan, Aztec, Native American

### 0.4.0 — Expanded Divination (+40)
Wu Xing, Ogham, Alchemical

### 0.5.0 — Psychology Frameworks (+80)
MBTI, Socionics, Big Five, Carol Pearson, etc.

### 0.6.0 — Narrative & Literary (+25)
Propp, Seven Plots, Commedia dell'Arte

### 0.7.0 — Gendered Systems (+35)
KWML, Triple Goddess, Bolen, Caroline Myss

### 1.0.0 — Production Release
Complete database, REST/GraphQL API, 3D visualization

*ACP is a database/visualization tool; narrative engine is a separate project.*

## Legacy Files

The `legacy/Arechtypal Context Protocol_*.md` files contain the original research and full system specifications (~1,200 archetypes documented). They serve as the source material for ongoing implementation.
