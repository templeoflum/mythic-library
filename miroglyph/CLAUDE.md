# CLAUDE.md - MiroGlyph v4 Development Guide

## Project Overview

MiroGlyph v4 is a **navigation topology for mythic narrative structures**. It provides a framework for mapping transformation journeys across 19 symbolic positions: 18 nodes organized into 3 arcs and 6 conditions, plus a center point called Nontion.

**Core Principle:** Myth is not discovered. It is navigated.

## System Structure

### 19 Points Total
- **18 Nodes**: 3 arcs × 6 conditions
- **1 Center Point**: Nontion (∅)

### Three Arcs (Thematic Lenses)
| Code | Primary Name | Secondary Name | Theme |
|------|--------------|----------------|-------|
| D | Descent | Shadow | Fragmentation, rupture, shadow work |
| R | Resonance | Mirror | Reflection, witnessing, pattern recognition |
| E | Emergence | Mythogenesis | Integration, synthesis, becoming |

### Six Conditions (Universal Phases)
| Code | Primary Name | Secondary Name | Theme |
|------|--------------|----------------|-------|
| 1 | Dawn | Initiation | Threshold, first light |
| 2 | Immersion | Encounter | Deep engagement |
| 3 | Crucible | Crisis | Transformation pressure |
| 4 | Alignment | Harmony | Balance point |
| 5 | Unveiling | Wisdom | Revelation |
| 6 | Return | Integration | Completion, carrying back |

### Node Naming Convention
Each node has dual naming: `Arc/Secondary – Condition/Secondary`
- Example: **D1** = "Descent/Shadow – Dawn/Initiation" = "The Catalyst Shard"

### Nontion (∅)
- Center point, not a node
- Reset and settling state
- Traversable but different ontological status
- Represents pause, integration through absence

## Visual Layout: Dual Orientation Topology

The 19 points are arranged in concentric circles with **two valid orientations** that can be toggled:

### Inverted (Default)
```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    │      E1  E2  E3  E4  E5  E6        │  ← Outer: Emergence
                    │                                     │
                    │         R1  R2  R3  R4  R5  R6     │  ← Middle: Resonance
                    │                                     │
                    │            D1  D2  D3  D4  D5  D6  │  ← Inner: Descent
                    │                                     │
                    │                  ∅                  │  ← Center: Nontion
                    │                                     │
                    └─────────────────────────────────────┘
```

### Standard
```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    │      D1  D2  D3  D4  D5  D6        │  ← Outer: Descent
                    │                                     │
                    │         R1  R2  R3  R4  R5  R6     │  ← Middle: Resonance
                    │                                     │
                    │            E1  E2  E3  E4  E5  E6  │  ← Inner: Emergence
                    │                                     │
                    │                  ∅                  │  ← Center: Nontion
                    │                                     │
                    └─────────────────────────────────────┘
```

**Why two orientations:**

Both configurations are mythologically valid lenses:

1. **Inverted (E outer, D inner)** - "Dissolve outward"
   - Dissolution happens at the core, near stillness
   - Emergence radiates outward into manifestation
   - Suits: katabasis, shadow work, death-rebirth narratives

2. **Standard (D outer, E inner)** - "Emerge outward"
   - Emergence begins at the core, near potential
   - Dissolution happens at the edge, dispersing outward
   - Suits: creation myths, emanation, becoming narratives

**What stays fixed:**
- Resonance (R) is always the middle ring - the threshold, the mirror
- Nontion (∅) is always the center - the pause, the reset
- Polarity pairs (1↔6, 2↔5, 3↔4) work identically in both
- Condition resonance (D1/R1/E1) works identically in both

**Toggle:** Settings menu (gear icon) → "Orientation: Standard/Inverted"

## Critical Design Principles

### 1. NO NAVIGATION RULES
**The system does not prescribe paths.** Users define their own topology and create their own paths.
- Don't validate paths against geometric rules
- Don't code "allowed" vs "disallowed" paths
- Just store what user creates

### 2. Topology Over Rules
- Provide positions and let users find connections
- Honor the uniqueness of each story
- Honor the agency of the creator

### 3. Dual Naming System
- Functional names give clarity
- Evocative names give resonance
- Display both, let users choose emphasis

### 4. Medium Agnosticism
Same system works for: writing, ritual, divination, games, performance

### 5. Scale Flexibility (Fractal)
Same topology applies at any zoom level: beat, scene, chapter, book

## Data Structures

### Traversal Schema
```json
{
  "path_id": "uuid",
  "name": "Hero's Descent",
  "color": "#fbbf24",
  "description": "Optional description",
  "sequence": ["D1", "D2", "D3", "∅", "E3"],  // min 2 items
  "is_circuit": false,
  "created_date": "2026-01-24T00:00:00Z"
}
```

### Export Schema
```json
{
  "miroglyph_version": "4.0.0",
  "exported_at": "2026-01-24T00:00:00Z",
  "paths": [...]  // Array of traversals
}
```

**Note:** The topology is inherent - all 19 nodes exist and any node can connect to any other. Users define traversal *routes* through this pre-existing field, not the connections themselves.

## Structural Relationships

### Polarity Pairs (within same arc)
- 1 ↔ 6: Dawn ↔ Return
- 2 ↔ 5: Immersion ↔ Unveiling
- 3 ↔ 4: Crucible ↔ Alignment

### Condition Resonance (same condition across arcs)
- D1, R1, E1 = Initiation across all lenses
- D3, R3, E3 = Crisis across all lenses

## Implementation

### Current Implementation
The tool is built with vanilla JavaScript + SVG rendering:

```
miroglyph/
├── index.html              # Main HTML with three-view layout
├── css/
│   ├── styles.css          # Base styles, CSS variables, semantic colors
│   ├── tabs.css            # Tab navigation and shared components
│   ├── view-atlas.css      # Atlas view (three-pane layout)
│   ├── view-codex.css      # Codex view (card grid + details)
│   └── view-chronicle.css  # Chronicle view (patterns + validation)
├── js/
│   ├── utils.js            # Shared utility functions (NEW)
│   ├── nodes.js            # 19-node definitions (arcs, conditions)
│   ├── storage.js          # LocalStorage + JSON import/export
│   ├── data-loader.js      # JSON fetching with cache + indices
│   ├── nav.js              # Cross-navigation + breadcrumbs + discovery
│   ├── tab-router.js       # View switching
│   ├── global-search.js    # Omni-search
│   ├── canvas.js           # SVG rendering (centrifugal layout)
│   ├── paths.js            # Traversal creation & management
│   ├── card-renderer.js    # Shared card rendering with fidelity badges
│   ├── detail-sheet.js     # Detail views with Related sections
│   ├── mini-map.js         # Interactive mini-map with tooltips
│   ├── view-atlas.js       # Atlas view controller
│   ├── view-codex.js       # Codex view controller (archetypes/entities/motifs)
│   ├── view-chronicle.js   # Chronicle view controller
│   └── app.js              # Main controller (boot sequence + breadcrumbs)
└── data/                   # Pre-exported JSON data files
```

### Three Views
- **Atlas**: Three-pane layout (Node Info | Canvas | Traversals) for path building
- **Codex**: Catalog browsing with sub-tabs: Archetypes (951) | Entities (173) | Motifs (149)
- **Chronicle**: Analysis with sub-tabs: Patterns (18 with mini-map) | Validation (tiers + insights)

### Core Features
1. **Display** - 19 points in centrifugal concentric layout
2. **Traversal Creator** - Click nodes in sequence, save with name + color
3. **Visibility Toggles** - Show/hide individual traversals to compare
4. **Edit** - Modify name, color, description after creation
5. **Persistence** - Auto-save to LocalStorage, JSON export/import

### Navigation & Discovery Features
- **Breadcrumb Trail** - Tracks last 5 items viewed; clickable to revisit
- **"Surprise Me" Buttons** - Random discovery in each view
- **Cross-Referencing** - Every detail view links to related items:
  - Pattern → Entities, Motifs
  - Motif → Patterns, Entities
  - Entity → Archetype, Patterns, Related Entities
  - Archetype → Source Entities, Related Archetypes
- **Mini-Map Interactivity** - Click nodes to navigate, hover for tooltips

### Data Visualization
- **Fidelity Badges** - Green/Yellow/Red indicators for mapping quality
- **Distance Badges** - ACP distance shown on entity cards
- **Semantic Colors** - Success (#22c55e), Warning (#eab308), Error (#ef4444), Info (#3b82f6)

### Accessibility
- **Keyboard Navigation** - All cards have tabindex, focus indicators
- **Focus Visible** - 2px primary outline on all interactive elements
- **Enhanced Hover States** - 3px lift with shadow on hover

### Usage Flow
1. Click nodes to build a traversal sequence
2. Click "Save Traversal" → name it, pick a color
3. Toggle visibility (eye icon) to compare different routes
4. Edit button to change properties after creation

## Common Pitfalls to Avoid

1. **Don't Over-Validate** - Resist enforcing "correct" paths
2. **Don't Hide Structure** - Make connections visually clear
3. **Don't Assume Linear** - Support circuits, spirals, complex patterns
4. **Don't Treat Nodes As Fixed** - They're positions, not rigid definitions
5. **Don't Forget Nontion** - Give the center point proper treatment

## Technical Stack Suggestions

**Frontend:**
- Canvas: HTML5 Canvas, SVG, or D3.js
- UI: React, Vue, or vanilla JS
- Layout: Polar coordinates (concentric circles + radial)

**Storage:**
- JSON files (simple)
- LocalStorage (web app)
- Database (larger system)

**Visualization:**
- D3.js or Cytoscape.js for network topology
- Custom canvas/SVG rendering

## File Structure

| File | Purpose |
|------|---------|
| `miroglyph_v4_technical_spec.json` | Complete data structures and schemas |
| `miroglyph_v4_context.md` | Usage guide and conceptual overview |
| `miroglyph_v4_philosophy.md` | Principles, vision, and values |
| `README.md` | Quick start and overview |

## Evidence Marker System (Optional)

An optional extension for symbolic depth. Each node gets a (Primary, Secondary) marker pair.

**Categories:**
- O: Object (concrete things)
- A: Action (verbs, movements)
- Q: Quality (attributes, states)
- B: Being (entities, characters)
- F: Force (energies, pressures)
- M: MetaSymbol (recursive patterns)

Primary is locked by condition; secondary varies by arc. This makes polarity and resonance visually evident.

## Success Criteria

**Minimum Viable:**
- Display 19 points clearly
- Draw connections between points
- Create paths by clicking sequences
- Save/load system as JSON

**Well Done:**
- Intuitive UX
- Clear visual distinction (arcs, conditions, paths)
- Reliable persistence
- Good documentation

**Excellent:**
- Multiple path visualization
- Pattern suggestions
- Export to other formats
- Integration hooks

## Key Values

- **Emergence Over Prescription** - Let patterns arise
- **Complexity Over Simplicity** - Honor nuance
- **Navigation Over Destination** - Journey matters
- **Both/And Over Either/Or** - Dual naming exists for a reason
- **User Agency Over System Authority** - User decides what matters
- **Visible Structure Over Hidden Magic** - Transparency over mystery

## Testing Considerations

- Can user create traversal by clicking node sequence?
- Does export/import work without data loss?
- Can traversals pass through Nontion?
- What if traversal is just 2 nodes?
- What if user creates a circuit (returns to start)?
- Do visibility toggles work correctly for multiple traversals?
- Does edit preserve the original sequence while changing name/color?

---

*Build the tool that lets users navigate their own myths.*
