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

### Design Principles

1. **Primary markers reflect polarity**: Conditions 1-6 use pattern O, A, B, O, A, B. Polarity partners (1↔4, 2↔5, 3↔6) share the same primary.

2. **Secondary markers create unique pairs**: Each arc shifts its secondary pattern so that:
   - No pair repeats at the same condition
   - Each arc has 6 unique pairs
   - 9 total unique pairs, each appearing exactly twice across all 18 nodes

3. **Arc-secondary thematic alignment**: Each arc starts with its aligned secondary:
   - **D (Shadow) → Q (Quality)**: Shadow work is qualitative - examining traits and states
   - **R (Mirror) → F (Force)**: Reflection involves force - vibrational pressure and dynamic tension
   - **E (Mythogenesis) → M (MetaSymbol)**: Myth-making is meta-symbolic - recursive patterns

### Primary by Condition
| Condition | Primary | Rationale |
|-----------|---------|-----------|
| 1 (Dawn) | O | Initiation involves threshold objects, first things |
| 2 (Immersion) | A | Encounter is active engagement, doing |
| 3 (Crucible) | B | Crisis centers on beings under pressure |
| 4 (Alignment) | O | Balance involves objects/anchors (polarity with 1) |
| 5 (Unveiling) | A | Revelation is an act of seeing/showing (polarity with 2) |
| 6 (Return) | B | Integration involves beings transformed (polarity with 3) |

### Secondary by Arc (shifted pattern)
| Arc | Cond 1 | Cond 2 | Cond 3 | Cond 4 | Cond 5 | Cond 6 |
|-----|--------|--------|--------|--------|--------|--------|
| D | Q | F | M | F | M | Q |
| R | F | M | Q | M | Q | F |
| E | M | Q | F | Q | F | M |

### Complete Node Pairs
| Node | Primary | Secondary | Pair | Thread Partner |
|------|---------|-----------|------|----------------|
| D1 | O | Q | O+Q | E4 |
| D2 | A | F | A+F | E5 |
| D3 | B | M | B+M | E6 |
| D4 | O | F | O+F | R1 |
| D5 | A | M | A+M | R2 |
| D6 | B | Q | B+Q | R3 |
| R1 | O | F | O+F | D4 |
| R2 | A | M | A+M | D5 |
| R3 | B | Q | B+Q | D6 |
| R4 | O | M | O+M | E1 |
| R5 | A | Q | A+Q | E2 |
| R6 | B | F | B+F | E3 |
| E1 | O | M | O+M | R4 |
| E2 | A | Q | A+Q | R5 |
| E3 | B | F | B+F | R6 |
| E4 | O | Q | O+Q | D1 |
| E5 | A | F | A+F | D2 |
| E6 | B | M | B+M | D3 |

### Pair Threads (cross-arc connections)
| Pair | Nodes | Conditions |
|------|-------|------------|
| O+Q | D1 ↔ E4 | 1 ↔ 4 |
| A+F | D2 ↔ E5 | 2 ↔ 5 |
| B+M | D3 ↔ E6 | 3 ↔ 6 |
| O+F | D4 ↔ R1 | 4 ↔ 1 |
| A+M | D5 ↔ R2 | 5 ↔ 2 |
| B+Q | D6 ↔ R3 | 6 ↔ 3 |
| O+M | R4 ↔ E1 | 4 ↔ 1 |
| A+Q | R5 ↔ E2 | 5 ↔ 2 |
| B+F | R6 ↔ E3 | 6 ↔ 3 |

---

## Example: Filtering at D3

**D3 "The Echo Engine"**
- Primary: B (Being)
- Secondary: M (MetaSymbol)
- Arc: Descent/Shadow
- Condition: Crucible/Crisis
- Thread Partner: E6 (shares B+M pair)

**Motif Filter Logic:**

1. **Primary B motifs** (strongly suggested):
   - Thompson A: Gods, divine beings caught in crisis
   - Thompson B: Animals facing transformation
   - Thompson E: The Dead, ghosts, spirits in liminal states
   - Thompson G: Monsters, ogres as shadow figures

2. **Secondary M motifs** (available options):
   - Thompson Z: Symbolism, recursive patterns, formulas
   - Thompson V: Religious symbolism, cosmological patterns
   - Thompson U: Paradox, meta-existence, nature of life

3. **Arc lens (Descent)** adds thematic filter:
   - Prefer motifs with shadow/fragmentation themes
   - E (Dead) especially resonant with Descent

4. **Condition lens (Crucible)** adds pressure context:
   - Prefer motifs involving crisis, transformation pressure
   - G (Ogres) as forces of destruction
   - Z (Formulas/chains) as recursive collapse patterns

**Result:** At D3, the system would surface motifs from E, G, A, B (primary) and Z, V, U (secondary), with E and G weighted highest given the Descent/Crucible intersection, and Z emphasized for the recursive "Echo Engine" quality.

---

## Implementation Notes

### For Frontend Experience

1. **At each node**, retrieve the (Primary, Secondary) evidence markers
2. **Map to Thompson categories** using this document
3. **Filter the 579 motifs** in the database by their Thompson code prefix
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

## Thompson Index Coverage

The Mythic Library contains 579 curated Thompson motifs across all 23 categories:

| Category | Count | Primary Evidence Marker |
|----------|-------|------------------------|
| A (Mythological) | 54 | B (Being) |
| B (Animals) | 32 | B (Being) |
| C (Tabu) | 30 | A (Action) |
| D (Magic) | 19 | O (Object) / A (Action) |
| E (The Dead) | 27 | B (Being) |
| F (Marvels) | 27 | O (Object) / B (Being) |
| G (Ogres) | 22 | B (Being) |
| H (Tests) | 23 | A (Action) |
| J (Wise/Foolish) | 38 | Q (Quality) |
| K (Deceptions) | 21 | A (Action) |
| L (Reversal) | 19 | Q (Quality) |
| M (Ordaining Future) | 21 | F (Force) |
| N (Chance/Fate) | 19 | F (Force) |
| P (Society) | 32 | O (Object) / B (Being) |
| Q (Rewards) | 25 | F (Force) |
| R (Captives) | 21 | A (Action) |
| S (Cruelty) | 21 | F (Force) |
| T (Sex/Marriage) | 24 | M (MetaSymbol) |
| U (Nature of Life) | 15 | Q (Quality) / M (MetaSymbol) |
| V (Religion) | 21 | M (MetaSymbol) / O (Object) |
| W (Traits) | 27 | Q (Quality) |
| X (Humor) | 19 | Q (Quality) / M (MetaSymbol) |
| Z (Miscellaneous) | 22 | M (MetaSymbol) |

All categories have 15+ entries for robust filtering at every node.

---

*This mapping bridges MiroGlyph's structural topology with the empirical motif data from the Mythic Library, enabling the frontend experience to present contextually appropriate choices at each node.*
