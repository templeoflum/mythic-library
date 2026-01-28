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

## Visual Layout: Centrifugal Topology

The 19 points are arranged in concentric circles following a **centrifugal journey pattern**:

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

**Why this arrangement:**

1. **Descent nearest the void** - Shadow work, fragmentation, rupture happens closest to stillness. You descend *inward* before you can emerge *outward*.

2. **Resonance as threshold** - The Mirror sits between descent and emergence. It's the witnessing layer, the mediator between inner collapse and outer becoming.

3. **Emergence radiates outward** - Mythogenesis, synthesis, "The Symphony" (E6) disperses outward into the world. You emerge *out of* the system.

4. **Nontion touches Shadow first** - The reset state connects most directly to the wound. You cannot integrate what you haven't descended into.

This creates a natural **centrifugal flow**: Center → Descent → Resonance → Emergence. Traversals expand outward rather than contracting inward. You're not spiraling into a point; you're spiraling out into becoming.

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
Miroglyph/
├── index.html       # Main entry point
├── css/styles.css   # Dark theme styling
├── js/
│   ├── nodes.js     # 18 nodes + Nontion definitions
│   ├── storage.js   # LocalStorage + JSON import/export
│   ├── canvas.js    # SVG rendering (centrifugal layout)
│   ├── paths.js     # Traversal creation & management
│   └── app.js       # Main controller
```

### Core Features
1. **Display** - 19 points in centrifugal concentric layout
2. **Traversal Creator** - Click nodes in sequence, save with name + color
3. **Visibility Toggles** - Show/hide individual traversals to compare
4. **Edit** - Modify name, color, description after creation
5. **Persistence** - Auto-save to LocalStorage, JSON export/import

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
