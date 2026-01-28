# Mythic System Integration

Connects three systems — the **Mythic Library** (empirical corpus), the **Archetypal Context Protocol** (8D coordinate theory), and **Miroglyph** (19-node narrative topology) — with a Python integration layer, a validation suite, and an interactive frontend explorer.

## Project Structure

```
mythic library/
├── ACP/                           # Archetypal Context Protocol
│   ├── schema/                    # Primordials, axes, relationships
│   ├── archetypes/                # Cultural tradition JSON-LD files
│   ├── divination/                # Tarot, I Ching, Runes
│   ├── psychology/                # Jungian archetypes
│   └── modern/                    # Vogler, Campbell frameworks
│
├── texts/                         # Mythic Library — source texts by tradition
│   ├── greek/, norse/, indian/... # 60+ texts across 20+ traditions
│   └── [tradition]/[text]/SOURCES.md
│
├── data/
│   └── mythic_patterns.db         # SQLite: 173 entities, 4000 segments, 149 motifs
│
├── integration/                   # Python bridge layer
│   ├── acp_loader.py              # Load ACP JSON-LD into queryable structures
│   ├── library_loader.py          # Query SQLite database (entities, patterns, motifs)
│   ├── entity_mapper.py           # Entity→Archetype alignment (name matching)
│   ├── unified_loader.py          # Combines ACP + Library loaders
│   ├── node_profiler.py           # Compute Miroglyph node centroids from ACP data
│   ├── node_affinity.py           # Gaussian affinity scoring (archetype→node)
│   └── miroglyph_loader.py        # Load Miroglyph topology definitions
│
├── validation/                    # v2 validation suite
│   ├── v2_run.py                  # Main runner — 5 tiers, 8 tests
│   ├── v2_tests/                  # Individual test modules
│   │   └── miroglyph_structure.py # Miroglyph structural tests
│   └── unified_report.py          # Report generation
│
├── scripts/
│   ├── export_explorer_data.py    # Export all system data to static JSON for frontend
│   └── serve_miroglyph.py         # HTTP server for the frontend explorer
│
├── miroglyph/                     # Frontend — Mythic System Explorer
│   ├── index.html                 # Tabbed interface (5 tabs)
│   ├── data/                      # Pre-exported JSON (6 files)
│   ├── css/                       # Styles (base + 5 tab-specific)
│   └── js/                        # Modules (13 JS files)
│
└── outputs/
    ├── mappings/                   # Entity→Archetype alignment results
    ├── metrics/                    # Validation results JSON
    ├── miroglyph/                  # Node profiles, archetype affinities
    └── reports/                    # Generated markdown reports
```

## Quick Start

### 1. Run Validation

```bash
python validation/v2_run.py
```

Runs the 5-tier validation suite:
- **Tier A**: ACP Internal Coherence (echo distances, primordial clustering, axis independence)
- **Tier B**: Library-ACP External Validity (entity mapping rate, co-occurrence correlation)
- **Tier C**: Miroglyph Structural Validity (node separation, arc cohesion, condition orthogonality)
- **Tier D**: Cross-System Integration (dimensionality analysis, structural recommendations)
- **Tier E**: Expert Review (human audit cases)

### 2. Generate Explorer Data

```bash
python scripts/export_explorer_data.py
```

Exports 6 JSON files to `miroglyph/data/`:
- `archetypes_catalog.json` — 539 archetypes with 8D coordinates, primordials, relationships, nearest nodes
- `entities_catalog.json` — 173 entities with ACP mappings and node assignments
- `patterns_catalog.json` — 18 named patterns with motif codes, traditions, entities
- `validation_summary.json` — Tier verdicts, test details, recommendations, audit cases
- `node_profiles.json` — 18 Miroglyph node centroids
- `archetype_affinities.json` — 539 archetype-to-node affinity scores

### 3. Launch Explorer

```bash
python scripts/serve_miroglyph.py
# Open http://localhost:8080
```

Five tabs: Topology, Archetypes, Entity Tracing, Validation, Patterns.

## Three-System Architecture

```
MYTHIC LIBRARY              ACP                         MIROGLYPH
(empirical corpus)          (coordinate theory)         (narrative topology)
─────────────────          ─────────────────           ─────────────────
173 entities        ──→    539 archetypes       ──→    19 nodes
4000 text segments         8D spectral coords          3 arcs × 6 conditions
149 Thompson motifs        24 primordials               + Nontion center
18 named patterns          Relationship graph          Traversal paths

        EntityMapper              NodeAffinity
        (name matching)           (Gaussian scoring)
```

### 8 Spectral Axes
1. Order–Chaos
2. Creation–Destruction
3. Light–Shadow
4. Active–Receptive
5. Individual–Collective
6. Ascent–Descent
7. Stasis–Transformation
8. Voluntary–Fated

### 3 Miroglyph Arcs
- **D (Descent)**: Shadow, underworld, dissolution
- **R (Resonance)**: Mirror, transformation, trickster
- **E (Emergence)**: Creation, birth, mythogenesis

### 6 Conditions
Each arc has 6 conditions (Threshold/Apotheosis, Trial/Revelation, Dissolution/Integration), yielding 18 nodes plus Nontion (center reset).

## Key Integration Components

### EntityMapper
Maps library entities to ACP archetypes by name. 148 of 173 entities mapped (85.5% rate). Each mapped entity inherits the archetype's 8D coordinates.

### NodeAffinity
Scores each archetype against each Miroglyph node using Gaussian similarity (sigma=0.174) between the archetype's 8D coordinates and the node's centroid. Assigns each entity to its highest-affinity node.

### NodeProfiler
Computes Miroglyph node centroids by averaging 8D coordinates of all entities assigned to each node via pattern-to-arc mapping. Produces arc and condition profiles.

## Validation Results (Current)

| Tier | Label | Verdict |
|------|-------|---------|
| A | ACP Internal Coherence | PARTIAL |
| B | Library-ACP External Validity | FAIL |
| C | Miroglyph Structural Validity | PARTIAL |
| D | Cross-System Integration | ALTERNATIVES_FOUND |
| E | Expert Review | PENDING |

Overall: **MIXED** — the system has structural validity but the Library-ACP co-occurrence correlation is weak, suggesting ACP coordinates capture symbolic similarity rather than narrative co-occurrence.

## Dependencies

- Python 3.10+
- numpy, scipy (for validation statistics)
- No frontend dependencies — vanilla JS served as static files
