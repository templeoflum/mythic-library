# Evidence Marker → Thompson Motif Index Mapping

## Overview

This document defines how MiroGlyph's Evidence Marker system maps to Thompson Motif Index categories, enabling structured filtering of motif choices at each node.

**Evidence Markers** (6 categories): O, A, Q, B, F, M
**Thompson Index** (23 categories): A-Z (excluding I, Y)

Each node has a (Primary, Secondary) evidence marker pair. When selecting motifs at a node, the system filters Thompson categories based on these markers.

---

## Evidence Marker Definitions

| Code | Name | Description |
|------|------|-------------|
| **O** | Object | Concrete things, artifacts, physical items |
| **A** | Action | Verbs, movements, processes, activities |
| **Q** | Quality | Attributes, states, characteristics, traits |
| **B** | Being | Entities, characters, presences, creatures |
| **F** | Force | Energies, pressures, dynamics, cosmic mechanisms |
| **M** | MetaSymbol | Recursive patterns, symbolism, self-reference |

---

## Thompson Index Categories

| Code | Name | Primary Focus |
|------|------|---------------|
| A | Mythological Motifs | Gods, creators, cosmogony, world origins |
| B | Animals | Mythical animals, beast fables, animal traits |
| C | Tabu | Prohibitions, forbidden acts, violations |
| D | Magic | Transformation, magic objects, spells, powers |
| E | The Dead | Resurrection, ghosts, reincarnation, afterlife |
| F | Marvels | Otherworld, fairies, extraordinary phenomena |
| G | Ogres | Giants, monsters, cannibals, witches |
| H | Tests | Identity tests, ordeals, riddles, quests |
| J | Wise and Foolish | Wisdom, cleverness, fools, noodleheads |
| K | Deceptions | Tricks, thefts, disguises, escapes by wit |
| L | Reversal of Fortune | Youngest succeeds, humble rise, pride falls |
| M | Ordaining the Future | Prophecy, oaths, bargains, curses |
| N | Chance and Fate | Luck, gambling, accidents, fortune |
| P | Society | Royalty, customs, law, social order |
| Q | Rewards and Punishments | Justice, karma, divine judgment |
| R | Captives and Fugitives | Capture, rescue, pursuit, refuge |
| S | Unnatural Cruelty | Murder, abandonment, persecution |
| T | Sex | Love, marriage, union, fertility |
| U | Nature of Life | Truth, mortality, existence, paradox |
| V | Religion | Ritual, belief, sacred acts, devotion |
| W | Traits of Character | Virtues, vices, personality |
| X | Humor | Jokes, absurdity, comic situations |
| Z | Miscellaneous | Symbolism, heroes, formulas, chains |

---

## The Mapping

### O (Object) → Thompson Categories

**Primary matches:**
| Thompson | Category | Rationale |
|----------|----------|-----------|
| **D** | Magic | D800-D1699 specifically covers magic objects (rings, swords, cloaks, etc.) |
| **F** | Marvels | F800+ covers extraordinary objects and places |

**Secondary matches:**
| Thompson | Category | Rationale |
|----------|----------|-----------|
| P | Society | Regalia, crowns, symbols of office |
| V | Religion | Sacred objects, relics, ritual items |

---

### A (Action) → Thompson Categories

**Primary matches:**
| Thompson | Category | Rationale |
|----------|----------|-----------|
| **H** | Tests | Testing, proving, competing, questing |
| **K** | Deceptions | Tricking, stealing, escaping, disguising |
| **R** | Captives/Fugitives | Capturing, rescuing, fleeing, pursuing |
| **C** | Tabu | Breaking, violating, transgressing |

**Secondary matches:**
| Thompson | Category | Rationale |
|----------|----------|-----------|
| D | Magic | D0-D699 transformation acts, D1700+ magic acts |
| S | Cruelty | Acts of violence, abandonment |

---

### Q (Quality) → Thompson Categories

**Primary matches:**
| Thompson | Category | Rationale |
|----------|----------|-----------|
| **W** | Traits of Character | Virtues, vices, personality attributes |
| **J** | Wise and Foolish | Wisdom/folly as qualities of mind |
| **U** | Nature of Life | States of being, existential qualities |
| **L** | Reversal of Fortune | States of fortune, status, condition |

**Secondary matches:**
| Thompson | Category | Rationale |
|----------|----------|-----------|
| N | Chance and Fate | Lucky/unlucky as qualities |
| X | Humor | Absurdity as a quality of situation |

---

### B (Being) → Thompson Categories

**Primary matches:**
| Thompson | Category | Rationale |
|----------|----------|-----------|
| **A** | Mythological Motifs | Gods, creators, divine beings |
| **B** | Animals | Animal beings, beast characters |
| **E** | The Dead | Ghosts, spirits, revenants, undead |
| **G** | Ogres | Giants, monsters, witches, demons |

**Secondary matches:**
| Thompson | Category | Rationale |
|----------|----------|-----------|
| F | Marvels | F200-F699 fairies, spirits, otherworld beings |
| P | Society | Kings, heroes, social roles as character types |

---

### F (Force) → Thompson Categories

**Primary matches:**
| Thompson | Category | Rationale |
|----------|----------|-----------|
| **N** | Chance and Fate | Fate as cosmic force, luck as mechanism |
| **M** | Ordaining the Future | Prophecy, curses, oaths as binding forces |
| **Q** | Rewards and Punishments | Cosmic justice, karma as force |
| **S** | Unnatural Cruelty | Destructive force, violence as pressure |

**Secondary matches:**
| Thompson | Category | Rationale |
|----------|----------|-----------|
| D | Magic | Magic power as force (D1700+) |
| L | Reversal | Fortune's wheel as force |

---

### M (MetaSymbol) → Thompson Categories

**Primary matches:**
| Thompson | Category | Rationale |
|----------|----------|-----------|
| **Z** | Miscellaneous | Z0-Z99 symbolism, Z200+ heroes as patterns, Z300+ formulas |
| **V** | Religion | Religious symbolism, cosmological patterns |
| **U** | Nature of Life | Paradox, recursive truth, meta-existence |

**Secondary matches:**
| Thompson | Category | Rationale |
|----------|----------|-----------|
| T | Sex | Union/creation as archetypal pattern |
| X | Humor | Irony, meta-commentary, self-reference |
| A | Mythological | A0-A99 creator patterns, cosmogonic recursion |

---

## Quick Reference Matrix

```
Evidence → Thompson Categories (Primary | Secondary)

O (Object)    →  D, F           | P, V
A (Action)    →  H, K, R, C     | D, S
Q (Quality)   →  W, J, U, L     | N, X
B (Being)     →  A, B, E, G     | F, P
F (Force)     →  N, M, Q, S     | D, L
M (MetaSymbol)→  Z, V, U        | T, X, A
```

---

## Node Evidence Marker Assignments

From `miroglyph_v4_technical_spec.json`:

### Primary by Condition
| Condition | Primary | Rationale |
|-----------|---------|-----------|
| 1 (Dawn) | O | Initiation involves threshold objects, first things |
| 2 (Immersion) | A | Encounter is active engagement, doing |
| 3 (Crucible) | B | Crisis centers on beings under pressure |
| 4 (Alignment) | B | Harmony requires beings in relationship |
| 5 (Unveiling) | A | Revelation is an act of seeing/showing |
| 6 (Return) | O | Integration carries objects/gifts back |

### Secondary by Node
| Node | Secondary | (Primary, Secondary) |
|------|-----------|----------------------|
| D1 | Q | (O, Q) |
| D2 | B | (A, B) |
| D3 | O | (B, O) |
| D4 | A | (B, A) |
| D5 | A | (A, A) |
| D6 | O | (O, O) |
| R1 | F | (O, F) |
| R2 | Q | (A, Q) |
| R3 | Q | (B, Q) |
| R4 | B | (B, B) |
| R5 | O | (A, O) |
| R6 | A | (O, A) |
| E1 | M | (O, M) |
| E2 | F | (A, F) |
| E3 | M | (B, M) |
| E4 | F | (B, F) |
| E5 | M | (A, M) |
| E6 | B | (O, B) |

---

## Example: Filtering at D3

**D3 "The Echo Engine"**
- Primary: B (Being)
- Secondary: O (Object)
- Arc: Descent/Shadow
- Condition: Crucible/Crisis

**Motif Filter Logic:**

1. **Primary B motifs** (strongly suggested):
   - Thompson A: Gods, divine beings caught in crisis
   - Thompson B: Animals facing transformation
   - Thompson E: The Dead, ghosts, spirits in liminal states
   - Thompson G: Monsters, ogres as shadow figures

2. **Secondary O motifs** (available options):
   - Thompson D: Magic objects that trap or transform
   - Thompson F: Marvels, otherworld objects

3. **Arc lens (Descent)** adds thematic filter:
   - Prefer motifs with shadow/fragmentation themes
   - E (Dead) especially resonant with Descent

4. **Condition lens (Crucible)** adds pressure context:
   - Prefer motifs involving crisis, transformation pressure
   - G (Ogres) as forces of destruction
   - E (Dead) as death-rebirth threshold

**Result:** At D3, the system would surface motifs from E, G, A, B (primary) and D, F (secondary), with E and G weighted highest given the Descent/Crucible intersection.

---

## Implementation Notes

### For Frontend Experience

1. **At each node**, retrieve the (Primary, Secondary) evidence markers
2. **Map to Thompson categories** using this document
3. **Filter the 149 motifs** in the database by their Thompson code prefix
4. **Weight results** by:
   - Primary marker matches = highest weight
   - Secondary marker matches = medium weight
   - Arc thematic alignment = modifier
   - Condition thematic alignment = modifier

### Motif Code Structure

Thompson codes follow pattern: `[Letter][Numbers]` (e.g., `F81.1`, `D672`, `E501`)

The letter prefix maps directly to the categories above:
- `F81.1` (Descent to lower world) → F (Marvels) → maps to O or B depending on context
- `E501` (The Wild Hunt) → E (The Dead) → maps to B (Being)
- `D672` (Obstacle flight) → D (Magic) → maps to O (Object) or A (Action)

### Edge Cases

Some Thompson categories map to multiple evidence markers depending on sub-range:
- **D (Magic)**: D0-D699 (transformation) = A, D800-D1699 (objects) = O, D1700+ (powers) = F
- **F (Marvels)**: F0-F199 (otherworld) = M, F200-F699 (beings) = B, F700+ (things) = O

Consider sub-range mapping for finer filtering if needed.

---

## Validation

This mapping should satisfy:
1. Every Thompson category maps to at least one evidence marker
2. Every evidence marker has at least 2 primary Thompson categories
3. The mapping reflects the semantic essence of each category
4. The mapping enables meaningful filtering at all 18 nodes

---

*This mapping bridges MiroGlyph's structural topology with the empirical motif data from the Mythic Library, enabling the frontend experience to present contextually appropriate choices at each node.*
