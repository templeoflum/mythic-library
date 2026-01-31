# Universal Archetype Schema v2

## Problem Statement

Current state:
- 996 archetypes, 95% at "rich" tier or above after v0.3.0 enrichment
- Cross-system links exist in correspondences.jsonld but aren't bidirectional
- `correspondences` fields use strings ("Jupiter") not @id refs ("astrology:jupiter")
- Relationships are sparse - most entries have 0-2 relationships
- Primordials list instantiations as strings, not linked @ids

**Goal**: Every archetype connects to every other through multiple pathways. Not flattening - mapping.

---

## Core Principles

### 1. Everything is a Node
Every entry (archetype, primordial, element, card, planet) is a node with an `@id`.

### 2. All Connections are Edges
All relationships are typed, weighted, bidirectional (where applicable), and use `@id` references.

### 3. Multiple Connection Layers
Archetypes connect through:
- **Spectral proximity** (8D coordinate distance)
- **Primordial instantiation** (shared meta-archetypes)
- **Cross-system correspondence** (CULTURAL_ECHO, MIRRORS)
- **Explicit relationships** (POLAR_OPPOSITE, SHADOW, COMPLEMENT, etc.)
- **Shared domains** (both govern "death", "fertility", etc.)

### 4. Provenance Tracking
Every cross-system link tracks:
- `provenance`: TRAD (traditional), SYNC (syncretic), SCHOL (scholarly), ORIG (original to ACP)
- `confidence`: 0.0-1.0

---

## Universal Entry Structure

```jsonc
{
  // === IDENTITY ===
  "@id": "system:identifier",
  "@type": "Archetype",
  "name": "Human-readable name",
  "systemCode": "SYS",
  "belongsToSystem": "system:parent",

  // === DESCRIPTION ===
  "description": "Core meaning and function",
  "keywords": ["searchable", "terms", "lowercase"],

  // === SPECTRAL POSITION (universal comparison layer) ===
  "spectralCoordinates": {
    "order-chaos": 0.00,
    "creation-destruction": 0.00,
    "light-shadow": 0.00,
    "active-receptive": 0.00,
    "individual-collective": 0.00,
    "ascent-descent": 0.00,
    "stasis-transformation": 0.00,
    "voluntary-fated": 0.00
  },

  // === PRIMORDIAL INSTANTIATION (deepest connection) ===
  "instantiates": [
    {
      "primordial": "primordial:identifier",
      "weight": 0.85,
      "aspects": ["specific", "aspects", "embodied"]
    }
  ],

  // === DOMAINS (controlled vocabulary) ===
  "domains": ["death", "transformation", "underworld"],

  // === CROSS-SYSTEM CORRESPONDENCES (unified format) ===
  "correspondences": {
    // Each key is a system, value is an @id reference
    "tarot": "tarot:death",
    "planet": "astrology:pluto",
    "element": "element:water",
    "chakra": "chakra:muladhara",
    "rune": "rune:hagalaz",
    "hexagram": "iching:23",

    // For non-archetype correspondences
    "day": "Saturday",
    "metal": "lead",
    "colors": ["black", "dark red"],
    "animals": ["serpent", "raven"],
    "plants": ["yew", "cypress"]
  },

  // === CROSS-SYSTEM ECHOES (cultural equivalents) ===
  "culturalEchoes": [
    {
      "target": "arch:EG-OSIRIS",
      "fidelity": 0.75,
      "sharedAspects": ["death-and-rebirth", "underworld-ruler"],
      "provenance": "SCHOL",
      "note": "Both rule underworld; Osiris adds resurrection aspect"
    },
    {
      "target": "arch:NO-HEL",
      "fidelity": 0.65,
      "sharedAspects": ["underworld-ruler"],
      "provenance": "SCHOL"
    }
  ],

  // === RELATIONSHIPS (explicit typed connections) ===
  "relationships": [
    {
      "type": "POLAR_OPPOSITE",
      "target": "arch:GR-ZEUS",
      "axis": "ascent-descent",
      "strength": 0.95,
      "note": "Sky ruler vs Underworld ruler"
    },
    {
      "type": "SHADOW",
      "target": "arch:GR-THANATOS",
      "activationThreshold": 0.6,
      "note": "When Hades becomes pure death rather than transformation"
    },
    {
      "type": "COMPLEMENT",
      "target": "arch:GR-PERSEPHONE",
      "strength": 0.95,
      "note": "King and Queen of underworld"
    },
    {
      "type": "CONSTELLATION",
      "target": "constellation:underworld-triad",
      "members": ["arch:GR-HADES", "arch:GR-PERSEPHONE", "arch:GR-HECATE"]
    }
  ],

  // === PSYCHOLOGICAL MAPPING ===
  "psychologicalMapping": {
    "jungianFunction": "Shadow integration, facing mortality",
    "developmentalTask": "Accepting death as transformation",
    "cognitiveBias": "Avoidance of endings",
    "integrationPath": "Embracing necessary endings"
  },

  // === NARRATIVE FUNCTION ===
  "narrativeRoles": ["threshold-guardian", "judge", "initiator"],
  "storyFunctions": ["guards-the-boundary", "tests-the-hero", "holds-the-treasure"],

  // === SYMBOLIC CORE ===
  "coreFunction": "To guard the boundary between life and death",
  "symbolicCore": "The invisible ruler who holds what is precious",

  // === ELEMENTAL COMPOSITION (optional) ===
  "elementalComposition": {
    "earth": 0.7,
    "water": 0.4,
    "fire": 0.1,
    "air": 0.1,
    "aether": 0.5
  }
}
```

---

## Controlled Vocabularies

### Domains (areas of influence)
Must use standardized terms for cross-system comparison:

```
death, rebirth, underworld, sky, sea, earth, fire, water, air
war, peace, love, fertility, harvest, hunt, wisdom, knowledge
crafts, smithing, healing, prophecy, music, poetry, dance
threshold, boundaries, travel, commerce, communication
justice, law, order, chaos, fate, time, memory
home, hearth, family, marriage, motherhood, fatherhood, childhood
transformation, initiation, sacrifice, ecstasy, madness
```

### Narrative Roles
```
hero, mentor, threshold-guardian, herald, shapeshifter
shadow, trickster, ally, lover, sovereign, sage
innocent, orphan, caregiver, seeker, creator, destroyer
ruler, magician, warrior, outcast, rebel
```

### Story Functions
```
calls-to-adventure, provides-guidance, guards-the-boundary
tests-the-hero, provides-the-gift, reveals-truth
transforms-through-ordeal, returns-with-elixir
```

---

## Connection Discovery Rules

### Rule 1: Spectral Neighbors
Any two archetypes with Euclidean distance < 0.3 in 8D space should have a relationship or correspondence noted.

### Rule 2: Shared Primordials
Any two archetypes instantiating the same primordial with weight > 0.5 should have CULTURAL_ECHO or MIRRORS relationship.

### Rule 3: Domain Overlap
Archetypes sharing 2+ domains should be checked for relationships.

### Rule 4: Bidirectionality
If A references B, B must reference A (for bidirectional relationship types).

### Rule 5: Transitivity Check
If A ↔ B (CULTURAL_ECHO, 0.8) and B ↔ C (CULTURAL_ECHO, 0.8), then A ↔ C should exist or be noted as absent.

---

## Migration Path

### Phase 1: Schema Validation
- Define exact required vs optional fields
- Create JSON Schema for validation
- Audit existing entries for compliance

### Phase 2: Correspondence Linking
- Convert all string correspondences to @id refs
- Ensure bidirectional links (if Tarot:Emperor → Zeus, Zeus → Tarot:Emperor)
- Add provenance to all cross-system links

### Phase 3: Relationship Enrichment
- Every archetype gets at least: 1 CULTURAL_ECHO, 1 relationship (any type)
- Mythological figures get: POLAR_OPPOSITE, SHADOW, COMPLEMENT where applicable
- Systems with natural sequences get: PRECEDES/SUCCEEDS

### Phase 4: Domain Standardization
- Map all existing domains to controlled vocabulary
- Add domains to entries that lack them

### Phase 5: Narrative & Psychological
- Add narrativeRoles, storyFunctions to all entries
- Add psychologicalMapping to culturally significant entries

---

## Validation Rules

1. All `@id` references must resolve to existing entries
2. All coordinates must be complete (8 axes) and in [0.0, 1.0]
3. All `instantiates` must reference valid primordials
4. Bidirectional relationships must have matching entries
5. `fidelity` scores must correlate with spectral distance (< 0.3 distance should have > 0.7 fidelity)
6. Every entry must have at least: description, spectralCoordinates, 1 instantiation, 1 keyword

---

## Example: Complete Entry

See `archetypes/greek/GR_OLYMPIANS.jsonld` → Zeus entry for current best example.

Target: All 996 entries match this completeness level.
