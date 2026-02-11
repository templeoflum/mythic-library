# Mythogenetic OS — Architecture Reference

## What This System Is

A mythogenetic operating system: three layers that work together to organize, validate, and eventually synthesize archetypal knowledge from mythic texts across cultures.

**Current priority: make the existing data work correctly end-to-end before any synthesis work.**

---

## Three Layers

```
                Interface Layer
            +-------------------+
            |     MiroGlyph     |  Navigate, interact, build journeys
            +--------+----------+
                     |
                     | consumes archetype/entity/pattern catalogs (JSON)
                     |
              Structure Layer
            +-------------------+
            |       ACP         |  Coordinate system, archetype organization
            +--------+----------+
                     |
                     | consumes entities, patterns, motifs, textual evidence
                     |
                Data Layer
            +-------------------+
            |  Mythic Library   |  Texts, entities, patterns, motifs
            +-------------------+
```

Data flows upward. Each layer has a defined interface. Each layer CAN function independently but the full system requires all three.

---

## Layer 1: Mythic Library (Data)

**Purpose:** Curated corpus of mythic texts with extracted entities, patterns, and motifs. The empirical foundation — everything above this layer must be grounded in textual evidence.

### What It Owns

| Component | Location | Description |
|-----------|----------|-------------|
| Text corpus | `texts/` | Primary source mythology texts |
| Source metadata | `sources/` | Catalogs, provenance, audit trails |
| Database | `data/mythic_patterns.db` | SQLite — entities, segments, motif tags, patterns |
| Entity data | `data/entities.json`, `entity_aliases.json` | Canonical names and aliases |
| Motif index | `data/thompson_motif_index.json` | 579 Thompson Motif Index entries |
| Processing scripts | `scripts/` | Acquisition, enrichment, extraction, segmentation |

### Interface (what it exposes)

Via `integration/library_loader.py`:

- `get_all_entities()` — 173 entities with mention counts, traditions, types
- `get_all_patterns()` — 18 cross-cultural patterns with attestation counts
- `get_all_motif_codes()` — motif tags from Thompson index
- `get_entity_traditions(name)` — which traditions an entity appears in
- `get_entity_cooccurrence(name1, name2)` — shared segment count
- `get_text_segments_ordered(text_id)` — narrative-ordered segments with entities and motifs
- `get_entities_for_motif_codes(codes)` — entities appearing in motif-tagged segments
- `summary()` — corpus stats

### Does NOT own

- Archetype coordinates (ACP)
- Topology/navigation (MiroGlyph)
- Any concept of "nodes" or "arcs"

---

## Layer 2: ACP (Structure)

**Purpose:** An 8-dimensional coordinate system for positioning archetypes across traditions. Provides the structural framework that organizes Library data into a comparable, navigable space.

### What It Owns

| Component | Location | Description |
|-----------|----------|-------------|
| Schema | `ACP/schema/` | 8 axes, 22 primordials, 17 relationship types |
| Archetype data | `ACP/archetypes/` | 20 cultural pantheons as JSONLD |
| Divination systems | `ACP/divination/` | Tarot, I Ching, Runes, Astrology, etc. |
| Psychology frameworks | `ACP/psychology/` | Jungian, Enneagram, Hero's Journey, MBTI, etc. |
| Modern systems | `ACP/modern/` | Brand, digital, pop culture archetypes |
| Calibration | `ACP/calibration/` | 17-point reference frame (origin + 16 poles) |
| Fundamental Laws | `ACP/FUNDAMENTAL_LAWS.md` | Physics-mapped principles |
| Validation | `validation/` | Statistical tests against Library data |

### Core Schema

**8 Spectral Axes** (each 0.0–1.0):

1. Order–Chaos
2. Creation–Destruction
3. Light–Shadow
4. Active–Receptive
5. Individual–Collective
6. Ascent–Descent
7. Stasis–Transformation
8. Voluntary–Fated

**22 Primordial Meta-Archetypes:** Creator, Destroyer, Preserver, Trickster, Hero, Rebel, Shadow, Self, Great Mother, Great Father, Divine Child, Lover, Warrior, Magician, Sovereign, Maiden, Crone, Wise Elder, Psychopomp, Healer, Outcast, Ancestor, Monster, Twin

**17 Relationship Types:** POLAR_OPPOSITE, SHADOW, COMPLEMENT, EVOLUTION, DEVOLUTION, CULTURAL_ECHO, SYNTHESIS, DECOMPOSITION, CONTAINS, CONTAINED_BY, MIRRORS, ANTAGONIST, ALLY, PRECEDES, SUCCEEDS, TRANSCENDS, TENSION, CONSTELLATION, SUBLIMATION, INSTANTIATES

### Interface (what it exposes)

Via `integration/acp_loader.py`:

- `get_coordinates(archetype_id)` — 8D numpy array
- `calculate_distance(id1, id2)` — Euclidean distance in spectral space
- `get_nearby(archetype_id, threshold)` — nearby archetypes
- `find_by_name(name)` — search archetypes
- `get_instantiations(archetype_id)` — primordial weights
- `get_all_relationships(type_filter)` — relationship graph
- `summary()` — archetype/system counts

### Current Content

- 997 archetypes across 60+ traditions/systems
- ~539 with full 8D coordinates
- 4 domains: Mythological, Divination, Psychology, Modern

### Does NOT own

- Text corpus or entity extraction (Library)
- Navigation topology or traversals (MiroGlyph)
- The concept of "nodes," "arcs," or "conditions"

---

## Layer 3: MiroGlyph (Interface)

**Purpose:** A 19-node navigation topology for mythic narrative structure. The interaction layer — how you explore, build journeys, and work with the system.

### What It Owns

| Component | Location | Description |
|-----------|----------|-------------|
| Topology | `miroglyph/js/nodes.js` | 19 points: 3 arcs x 6 conditions + Nontion |
| Explorer app | `miroglyph/index.html` | Atlas, Codex, Chronicle views |
| Journey Mapper | `miroglyph/journey.html` | Network config + guided traversals |
| Node templates | `miroglyph/data/node_templates.json` | Evidence markers, positional slots |
| Canvas rendering | `miroglyph/js/canvas.js` | SVG centrifugal layout |
| Traversal system | `miroglyph/js/paths.js` | Path creation, storage, visualization |
| All CSS/JS/HTML | `miroglyph/css/`, `miroglyph/js/` | Vanilla JS, no framework |

### Core Structure

**3 Arcs** (thematic lenses):
- D (Descent/Shadow) — fragmentation, rupture
- R (Resonance/Mirror) — reflection, pattern recognition
- E (Emergence/Mythogenesis) — integration, becoming

**6 Conditions** (universal phases):
- 1 Dawn, 2 Immersion, 3 Crucible, 4 Alignment, 5 Unveiling, 6 Return

**Key principle:** Nodes are structural frames. Any archetype can be placed in any node. The node's structure interprets the archetype, not the other way around.

### Interface (what it consumes)

MiroGlyph loads pre-exported JSON catalogs from `miroglyph/data/`:

| File | Source | Used By |
|------|--------|---------|
| `archetypes_catalog.json` | ACP via export pipeline | Codex (archetype browsing) |
| `entities_catalog.json` | Library + ACP via export pipeline | Codex (entity browsing) |
| `patterns_catalog.json` | Library via export pipeline | Chronicle (pattern grid) |
| `validation_summary.json` | ACP validation via export pipeline | Codex (validation tab) |
| `node_templates.json` | MiroGlyph-native | Journey Mapper (node structure) |

**MiroGlyph works with zero external data.** The topology, Journey Mapper, and traversal system are fully functional without any catalog files. Codex and Chronicle are optional views that display ACP/Library data when available.

### Does NOT own

- Archetype coordinates or relationships (ACP)
- Text corpus or entity extraction (Library)
- The export pipeline that produces its data files

---

## The Connector: Integration Layer

**Location:** `integration/` + `scripts/export_explorer_data.py`

This is the only code that knows about all three layers. It wires them together.

| Component | Purpose |
|-----------|---------|
| `acp_loader.py` | Reads ACP JSONLD files into Python objects |
| `library_loader.py` | Reads Library SQLite database |
| `entity_mapper.py` | Maps Library entities → ACP archetypes (3-phase pipeline) |
| `node_profiler.py` | Defines arc-to-pattern mapping (ARC_PATTERN_MAPPING) |
| `export_explorer_data.py` | Exports combined data as JSON for MiroGlyph frontend |

### Entity Mapping Pipeline

```
Library entities (173)
    ↓ Phase 1: Tradition-aware exact/alias match
    ↓ Phase 2: Library alias bridge
    ↓ Phase 3: Fuzzy match (mythology domain only, threshold 0.80)
    ↓
Mapped to ACP archetypes (126 mapped, 47 unmapped)
```

### Export Pipeline

```
python -X utf8 scripts/export_explorer_data.py

    → archetypes_catalog.json  (997 archetypes)
    → entities_catalog.json    (173 entities, 126 mapped)
    → patterns_catalog.json    (18 patterns)
    → validation_summary.json  (tier verdicts)
```

---

## Known Issues (Current State)

### ACP Data Hygiene

| Issue | Count | Severity |
|-------|-------|----------|
| Dangling relationship references | 294 | High — references to archetypes that don't exist |
| Asymmetric CULTURAL_ECHOs | 194 | Medium — A echoes B but B doesn't echo A |
| High-fidelity echo distance violations | 286 | Medium — high fidelity but far apart in 8D space |
| Undefined ghost primordials | 29 | Medium — referenced but not in primordials.jsonld |
| Underscore/hyphen ID format split | 108 | Low — inconsistent naming convention |

### Axis Correlation

The 8 axes are not fully independent. Effective dimensionality is ~5–6:

| Pair | Correlation | Shared Variance |
|------|------------|-----------------|
| Light-Shadow ↔ Ascent-Descent | r = 0.72 | 52% |
| Creation-Destruction ↔ Light-Shadow | r = 0.67 | 45% |
| Order-Chaos ↔ Stasis-Transformation | r = 0.63 | 40% |

Individual-Collective is the most independent axis (avg |r| = 0.175). These correlations reflect real mythological patterns, not measurement error, but should be documented.

### Primordial Representation

- 2.1:1 Western-to-non-Western archetype ratio
- Multi-weighting system works well (non-Western deities map authentically)
- Missing patterns: Culture Hero, Divine Animal, Sacred Fool
- "Monster" primordial has 0 non-Western archetypes mapped

### Validation Suite

- Tests 1–3 may be partially circular (ACP validating against itself)
- Test 5 (axis interpretability): 0/92 motif-axis tests pass
- No inter-rater reliability for human audit
- "STRONG" overall verdict is overclaimed given these gaps

### Frontend

- `node-drawer.js` is dead code (never called)
- `entitiesByNode` index is always empty (entities lack `nearest_node` field)
- Archetype detail "Nearest Nodes" section renders nothing (field not in data)
- Entity detail "Related Entities by node" section renders nothing

---

## What Needs to Happen (Priority Order)

### 1. ACP Data Hygiene
Fix the 294 dangling references, 194 asymmetric echoes, format inconsistencies. This is foundational — everything downstream depends on clean ACP data.

### 2. Clean Layer Interfaces
- Library loader should be the ONLY way to access Library data
- ACP loader should be the ONLY way to access ACP data
- MiroGlyph should ONLY consume pre-exported JSON, never reach into ACP or Library directly
- Remove dead frontend code (node-drawer.js, empty sections in detail-sheet.js)

### 3. Honest Validation
- Fix or remove circular tests
- Recalibrate thresholds for axis interpretability test
- Add inter-rater reliability to human audit
- Downgrade overall verdict to match actual evidence

### 4. Entity Mapping Completeness
47 entities remain unmapped. Some are genuinely unmappable (generic types), but others may need new ACP entries or better alias coverage.

### 5. Frontend Data Completeness
Entity entries lack `nearest_node` and archetype entries lack `nearest_nodes` — several Codex sections render empty. Either populate these fields in the export pipeline or remove the UI that expects them.

---

## File Map

```
mythic library/
+-- ACP/                        # Layer 2: Structure
|   +-- archetypes/             #   20 cultural pantheons (JSONLD)
|   +-- calibration/            #   Reference frame (17 points)
|   +-- divination/             #   Esoteric systems
|   +-- modern/                 #   Contemporary archetypes
|   +-- psychology/             #   Psychological frameworks
|   +-- schema/                 #   Axes, primordials, relationships
|   +-- FUNDAMENTAL_LAWS.md
|   +-- SYSTEM_ARCHITECTURE.md
|
+-- data/                       # Layer 1: Shared data
|   +-- mythic_patterns.db      #   SQLite database
|   +-- entities.json
|   +-- thompson_motif_index.json
|
+-- integration/                # Connector layer
|   +-- acp_loader.py
|   +-- library_loader.py
|   +-- entity_mapper.py
|   +-- node_profiler.py        #   (ARC_PATTERN_MAPPING only)
|
+-- miroglyph/                  # Layer 3: Interface
|   +-- index.html              #   Explorer app
|   +-- journey.html            #   Journey Mapper app
|   +-- css/                    #   6 stylesheets
|   +-- js/                     #   18 JS modules (vanilla IIFE)
|   +-- data/                   #   5 pre-exported JSON catalogs
|
+-- scripts/                    # Layer 1: Processing pipeline
|   +-- export_explorer_data.py #   Main export (connector)
|   +-- (50+ enrichment/processing scripts)
|
+-- sources/                    # Layer 1: Source metadata
+-- texts/                      # Layer 1: Text corpus
+-- validation/                 # Layer 2: ACP validation tests
+-- outputs/                    # Generated artifacts
+-- docs/                       # Documentation
```

---

## Open-Source Potential

Each layer is independently useful:

- **Mythic Library** — Researchers get a curated mythology corpus with entity extraction and motif tagging. No one else has this.
- **ACP** — System builders get a framework for organizing any archetypal knowledge into a navigable coordinate space. The schema is the product; the 997 archetypes are a reference implementation.
- **MiroGlyph** — Creators get a 19-node narrative topology tool. Works standalone for writers, game designers, ritual practitioners.

The full stack is a mythogenetic OS. Each piece alone is a useful tool.
