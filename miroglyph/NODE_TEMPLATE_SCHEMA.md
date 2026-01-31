# MiroGlyph Node Template Schema

## Overview

This document defines the canonical structure for each of the 19 MiroGlyph nodes. The template encodes all structural information needed for the guided frontend experience to present contextually appropriate choices.

**Key Principle:** Nodes don't own content (archetypes, entities, motifs). Nodes own the **lens and filter logic** that determines how content is presented and interpreted.

---

## Template Structure

```json
{
  "node_id": "D3",

  "identity": {
    "arc": {
      "code": "D",
      "primary": "Descent",
      "secondary": "Shadow",
      "themes": ["fragmentation", "rupture", "shadow work", "dissolution", "katabasis"]
    },
    "condition": {
      "code": 3,
      "primary": "Crucible",
      "secondary": "Crisis",
      "themes": ["transformation pressure", "breaking point", "trial by fire", "make-or-break"]
    },
    "title": "The Echo Engine",
    "role": "The loop of collapse",
    "tone": ["Mechanical", "Recursive", "Amplifying"]
  },

  "evidence_markers": {
    "primary": "B",
    "primary_name": "Being",
    "secondary": "O",
    "secondary_name": "Object",
    "thompson_primary": ["A", "B", "E", "G"],
    "thompson_secondary": ["D", "F"]
  },

  "structural_relationships": {
    "polarity_partner": {
      "node_id": "D4",
      "relationship": "Crucible ↔ Alignment",
      "tension": "Crisis seeks resolution in Harmony"
    },
    "condition_resonance": {
      "nodes": ["R3", "E3"],
      "shared_condition": 3,
      "theme": "Crisis across all lenses",
      "interpretation": "Same pressure, different modes: D3 fragments, R3 mirrors, E3 synthesizes"
    },
    "arc_siblings": ["D1", "D2", "D4", "D5", "D6"],
    "arc_circuit": "D1 → D2 → D3 → D4 → D5 → D6"
  },

  "thematic_lens": {
    "combined": "Shadow Crisis",
    "description": "The moment when descent reaches peak pressure; the loop that threatens to trap",
    "questions": [
      "What is collapsing?",
      "What pattern keeps repeating?",
      "What shadow is being amplified?"
    ],
    "narrative_beats": [
      "The crisis that forces confrontation",
      "The recursive trap",
      "The pressure that demands transformation"
    ]
  },

  "selection_prompts": {
    "archetype": "Which figure embodies this shadow crisis?",
    "entity": "Who is caught in this collapsing loop?",
    "motif": "What pattern marks this moment of peak pressure?"
  }
}
```

---

## Complete Node Templates

### Descent Arc (D)

#### D1 - The Catalyst Shard
```json
{
  "node_id": "D1",
  "identity": {
    "arc": {"code": "D", "primary": "Descent", "secondary": "Shadow"},
    "condition": {"code": 1, "primary": "Dawn", "secondary": "Initiation"},
    "title": "The Catalyst Shard",
    "role": "The rupture that begins the spiral",
    "tone": ["Fractured", "Volatile", "Initiating"]
  },
  "evidence_markers": {
    "primary": "O", "primary_name": "Object",
    "secondary": "Q", "secondary_name": "Quality",
    "thompson_primary": ["D", "F"],
    "thompson_secondary": ["W", "J", "U", "L"]
  },
  "structural_relationships": {
    "polarity_partner": {"node_id": "D4", "relationship": "Dawn ↔ Alignment"},
    "condition_resonance": {"nodes": ["R1", "E1"], "theme": "Initiation across all lenses"}
  },
  "thematic_lens": {
    "combined": "Shadow Initiation",
    "description": "The rupture that begins; the shard that cuts the old pattern",
    "questions": ["What breaks?", "What wound initiates the descent?", "What falls away?"]
  }
}
```

#### D2 - The Watcher Without Eyes
```json
{
  "node_id": "D2",
  "identity": {
    "arc": {"code": "D", "primary": "Descent", "secondary": "Shadow"},
    "condition": {"code": 2, "primary": "Immersion", "secondary": "Encounter"},
    "title": "The Watcher Without Eyes",
    "role": "Surveillance without comprehension",
    "tone": ["Haunting", "Detached", "Observing"]
  },
  "evidence_markers": {
    "primary": "A", "primary_name": "Action",
    "secondary": "B", "secondary_name": "Being",
    "thompson_primary": ["H", "K", "R", "C"],
    "thompson_secondary": ["A", "B", "E", "G"]
  },
  "structural_relationships": {
    "polarity_partner": {"node_id": "D5", "relationship": "Immersion ↔ Unveiling"},
    "condition_resonance": {"nodes": ["R2", "E2"], "theme": "Encounter across all lenses"}
  },
  "thematic_lens": {
    "combined": "Shadow Encounter",
    "description": "Meeting the dark without understanding; watching what cannot be seen",
    "questions": ["What watches?", "What is encountered but not understood?", "What haunts?"]
  }
}
```

#### D3 - The Echo Engine
```json
{
  "node_id": "D3",
  "identity": {
    "arc": {"code": "D", "primary": "Descent", "secondary": "Shadow"},
    "condition": {"code": 3, "primary": "Crucible", "secondary": "Crisis"},
    "title": "The Echo Engine",
    "role": "The loop of collapse",
    "tone": ["Mechanical", "Recursive", "Amplifying"]
  },
  "evidence_markers": {
    "primary": "B", "primary_name": "Being",
    "secondary": "O", "secondary_name": "Object",
    "thompson_primary": ["A", "B", "E", "G"],
    "thompson_secondary": ["D", "F"]
  },
  "structural_relationships": {
    "polarity_partner": {"node_id": "D4", "relationship": "Crucible ↔ Alignment"},
    "condition_resonance": {"nodes": ["R3", "E3"], "theme": "Crisis across all lenses"}
  },
  "thematic_lens": {
    "combined": "Shadow Crisis",
    "description": "The collapsing loop; the pattern that traps and amplifies",
    "questions": ["What repeats?", "What machine of suffering?", "What echo grows louder?"]
  }
}
```

#### D4 - The Idol of Symmetry
```json
{
  "node_id": "D4",
  "identity": {
    "arc": {"code": "D", "primary": "Descent", "secondary": "Shadow"},
    "condition": {"code": 4, "primary": "Alignment", "secondary": "Harmony"},
    "title": "The Idol of Symmetry",
    "role": "False coherence",
    "tone": ["Still", "Entrancing", "Deceptive"]
  },
  "evidence_markers": {
    "primary": "B", "primary_name": "Being",
    "secondary": "A", "secondary_name": "Action",
    "thompson_primary": ["A", "B", "E", "G"],
    "thompson_secondary": ["H", "K", "R", "C"]
  },
  "structural_relationships": {
    "polarity_partner": {"node_id": "D3", "relationship": "Alignment ↔ Crucible"},
    "condition_resonance": {"nodes": ["R4", "E4"], "theme": "Harmony across all lenses"}
  },
  "thematic_lens": {
    "combined": "Shadow Harmony",
    "description": "The false balance; the stillness that deceives; the idol that entrances",
    "questions": ["What false peace?", "What symmetry conceals?", "What idol demands worship?"]
  }
}
```

#### D5 - The Archivist of Shame
```json
{
  "node_id": "D5",
  "identity": {
    "arc": {"code": "D", "primary": "Descent", "secondary": "Shadow"},
    "condition": {"code": 5, "primary": "Unveiling", "secondary": "Wisdom"},
    "title": "The Archivist of Shame",
    "role": "Bearer of memory scars",
    "tone": ["Heavy", "Reverent", "Recording"]
  },
  "evidence_markers": {
    "primary": "A", "primary_name": "Action",
    "secondary": "A", "secondary_name": "Action",
    "thompson_primary": ["H", "K", "R", "C"],
    "thompson_secondary": ["H", "K", "R", "C"]
  },
  "structural_relationships": {
    "polarity_partner": {"node_id": "D2", "relationship": "Unveiling ↔ Immersion"},
    "condition_resonance": {"nodes": ["R5", "E5"], "theme": "Wisdom across all lenses"}
  },
  "thematic_lens": {
    "combined": "Shadow Wisdom",
    "description": "The revelation of wounds; the archive of what was buried; the weight of knowing",
    "questions": ["What is remembered?", "What shame is revealed?", "What scar teaches?"]
  }
}
```

#### D6 - The Haunting
```json
{
  "node_id": "D6",
  "identity": {
    "arc": {"code": "D", "primary": "Descent", "secondary": "Shadow"},
    "condition": {"code": 6, "primary": "Return", "secondary": "Integration"},
    "title": "The Haunting",
    "role": "That which returns unintegrated",
    "tone": ["Ghosted", "Enduring", "Unresolved"]
  },
  "evidence_markers": {
    "primary": "O", "primary_name": "Object",
    "secondary": "O", "secondary_name": "Object",
    "thompson_primary": ["D", "F"],
    "thompson_secondary": ["D", "F"]
  },
  "structural_relationships": {
    "polarity_partner": {"node_id": "D1", "relationship": "Return ↔ Dawn"},
    "condition_resonance": {"nodes": ["R6", "E6"], "theme": "Integration across all lenses"}
  },
  "thematic_lens": {
    "combined": "Shadow Integration",
    "description": "What returns but isn't resolved; the ghost that won't rest; the unfinished haunting",
    "questions": ["What won't stay buried?", "What haunts?", "What returns incomplete?"]
  }
}
```

---

### Resonance Arc (R)

#### R1 - The Welcomer of Echoes
```json
{
  "node_id": "R1",
  "identity": {
    "arc": {"code": "R", "primary": "Resonance", "secondary": "Mirror"},
    "condition": {"code": 1, "primary": "Dawn", "secondary": "Initiation"},
    "title": "The Welcomer of Echoes",
    "role": "Opens the field to resonance",
    "tone": ["Gentle", "Fluid", "Receiving"]
  },
  "evidence_markers": {
    "primary": "O", "primary_name": "Object",
    "secondary": "F", "secondary_name": "Force",
    "thompson_primary": ["D", "F"],
    "thompson_secondary": ["N", "M", "Q", "S"]
  },
  "structural_relationships": {
    "polarity_partner": {"node_id": "R4", "relationship": "Dawn ↔ Alignment"},
    "condition_resonance": {"nodes": ["D1", "E1"], "theme": "Initiation across all lenses"}
  },
  "thematic_lens": {
    "combined": "Mirror Initiation",
    "description": "Opening to reflection; welcoming what echoes back; first seeing in the mirror",
    "questions": ["What opens?", "What echo is welcomed?", "What begins to reflect?"]
  }
}
```

#### R2 - The Reflector of Tension
```json
{
  "node_id": "R2",
  "identity": {
    "arc": {"code": "R", "primary": "Resonance", "secondary": "Mirror"},
    "condition": {"code": 2, "primary": "Immersion", "secondary": "Encounter"},
    "title": "The Reflector of Tension",
    "role": "Mirrors the inner divide",
    "tone": ["Neutral", "Lucid", "Revealing"]
  },
  "evidence_markers": {
    "primary": "A", "primary_name": "Action",
    "secondary": "Q", "secondary_name": "Quality",
    "thompson_primary": ["H", "K", "R", "C"],
    "thompson_secondary": ["W", "J", "U", "L"]
  },
  "structural_relationships": {
    "polarity_partner": {"node_id": "R5", "relationship": "Immersion ↔ Unveiling"},
    "condition_resonance": {"nodes": ["D2", "E2"], "theme": "Encounter across all lenses"}
  },
  "thematic_lens": {
    "combined": "Mirror Encounter",
    "description": "Meeting one's reflection; the tension made visible; lucid confrontation",
    "questions": ["What tension is mirrored?", "What divide is revealed?", "What do you see?"]
  }
}
```

#### R3 - The Mirror-Kin
```json
{
  "node_id": "R3",
  "identity": {
    "arc": {"code": "R", "primary": "Resonance", "secondary": "Mirror"},
    "condition": {"code": 3, "primary": "Crucible", "secondary": "Crisis"},
    "title": "The Mirror-Kin",
    "role": "Embodied reflection",
    "tone": ["Compassionate", "Unnerving", "Mirroring"]
  },
  "evidence_markers": {
    "primary": "B", "primary_name": "Being",
    "secondary": "Q", "secondary_name": "Quality",
    "thompson_primary": ["A", "B", "E", "G"],
    "thompson_secondary": ["W", "J", "U", "L"]
  },
  "structural_relationships": {
    "polarity_partner": {"node_id": "R4", "relationship": "Crucible ↔ Alignment"},
    "condition_resonance": {"nodes": ["D3", "E3"], "theme": "Crisis across all lenses"}
  },
  "thematic_lens": {
    "combined": "Mirror Crisis",
    "description": "The other who reflects you; the kin who shows what you cannot see; compassionate confrontation",
    "questions": ["Who mirrors you?", "What does the reflection reveal?", "Who is your mirror-kin?"]
  }
}
```

#### R4 - The Integrator of Dissonance
```json
{
  "node_id": "R4",
  "identity": {
    "arc": {"code": "R", "primary": "Resonance", "secondary": "Mirror"},
    "condition": {"code": 4, "primary": "Alignment", "secondary": "Harmony"},
    "title": "The Integrator of Dissonance",
    "role": "Holds polarity",
    "tone": ["Stabilizing", "Vibrating", "Balancing"]
  },
  "evidence_markers": {
    "primary": "B", "primary_name": "Being",
    "secondary": "B", "secondary_name": "Being",
    "thompson_primary": ["A", "B", "E", "G"],
    "thompson_secondary": ["A", "B", "E", "G"]
  },
  "structural_relationships": {
    "polarity_partner": {"node_id": "R3", "relationship": "Alignment ↔ Crucible"},
    "condition_resonance": {"nodes": ["D4", "E4"], "theme": "Harmony across all lenses"}
  },
  "thematic_lens": {
    "combined": "Mirror Harmony",
    "description": "Holding both sides; the balance that includes dissonance; stabilizing through vibration",
    "questions": ["What opposites are held?", "What dissonance is integrated?", "How does balance vibrate?"]
  }
}
```

#### R5 - The Rememberer
```json
{
  "node_id": "R5",
  "identity": {
    "arc": {"code": "R", "primary": "Resonance", "secondary": "Mirror"},
    "condition": {"code": 5, "primary": "Unveiling", "secondary": "Wisdom"},
    "title": "The Rememberer",
    "role": "Keeper of the spiral",
    "tone": ["Ancient", "Warm", "Recalling"]
  },
  "evidence_markers": {
    "primary": "A", "primary_name": "Action",
    "secondary": "O", "secondary_name": "Object",
    "thompson_primary": ["H", "K", "R", "C"],
    "thompson_secondary": ["D", "F"]
  },
  "structural_relationships": {
    "polarity_partner": {"node_id": "R2", "relationship": "Unveiling ↔ Immersion"},
    "condition_resonance": {"nodes": ["D5", "E5"], "theme": "Wisdom across all lenses"}
  },
  "thematic_lens": {
    "combined": "Mirror Wisdom",
    "description": "The one who remembers; the keeper of what has been seen; ancient pattern recognition",
    "questions": ["What is remembered?", "What pattern repeats?", "What does memory reveal?"]
  }
}
```

#### R6 - The Resonator
```json
{
  "node_id": "R6",
  "identity": {
    "arc": {"code": "R", "primary": "Resonance", "secondary": "Mirror"},
    "condition": {"code": 6, "primary": "Return", "secondary": "Integration"},
    "title": "The Resonator",
    "role": "The tone of alignment",
    "tone": ["Clear", "Harmonic", "Crystallizing"]
  },
  "evidence_markers": {
    "primary": "O", "primary_name": "Object",
    "secondary": "A", "secondary_name": "Action",
    "thompson_primary": ["D", "F"],
    "thompson_secondary": ["H", "K", "R", "C"]
  },
  "structural_relationships": {
    "polarity_partner": {"node_id": "R1", "relationship": "Return ↔ Dawn"},
    "condition_resonance": {"nodes": ["D6", "E6"], "theme": "Integration across all lenses"}
  },
  "thematic_lens": {
    "combined": "Mirror Integration",
    "description": "The clear tone; resonance made complete; the reflection crystallized",
    "questions": ["What resonates clearly?", "What tone carries forward?", "What crystallizes?"]
  }
}
```

---

### Emergence Arc (E)

#### E1 - The Seedbearer of Stillness
```json
{
  "node_id": "E1",
  "identity": {
    "arc": {"code": "E", "primary": "Emergence", "secondary": "Mythogenesis"},
    "condition": {"code": 1, "primary": "Dawn", "secondary": "Initiation"},
    "title": "The Seedbearer of Stillness",
    "role": "Holds potential in quiet",
    "tone": ["Grounded", "Silent", "Encoding"]
  },
  "evidence_markers": {
    "primary": "O", "primary_name": "Object",
    "secondary": "M", "secondary_name": "MetaSymbol",
    "thompson_primary": ["D", "F"],
    "thompson_secondary": ["Z", "V", "U"]
  },
  "structural_relationships": {
    "polarity_partner": {"node_id": "E4", "relationship": "Dawn ↔ Alignment"},
    "condition_resonance": {"nodes": ["D1", "R1"], "theme": "Initiation across all lenses"}
  },
  "thematic_lens": {
    "combined": "Mythogenesis Initiation",
    "description": "The seed before growth; potential held in stillness; the encoded beginning",
    "questions": ["What seed is planted?", "What potential waits?", "What is encoded in silence?"]
  }
}
```

#### E2 - The Harmonizer of the Lattice
```json
{
  "node_id": "E2",
  "identity": {
    "arc": {"code": "E", "primary": "Emergence", "secondary": "Mythogenesis"},
    "condition": {"code": 2, "primary": "Immersion", "secondary": "Encounter"},
    "title": "The Harmonizer of the Lattice",
    "role": "Balances frequencies",
    "tone": ["Interwoven", "Steady", "Rhythmic"]
  },
  "evidence_markers": {
    "primary": "A", "primary_name": "Action",
    "secondary": "F", "secondary_name": "Force",
    "thompson_primary": ["H", "K", "R", "C"],
    "thompson_secondary": ["N", "M", "Q", "S"]
  },
  "structural_relationships": {
    "polarity_partner": {"node_id": "E5", "relationship": "Immersion ↔ Unveiling"},
    "condition_resonance": {"nodes": ["D2", "R2"], "theme": "Encounter across all lenses"}
  },
  "thematic_lens": {
    "combined": "Mythogenesis Encounter",
    "description": "Meeting the emerging pattern; harmonizing what arises; the lattice taking shape",
    "questions": ["What pattern emerges?", "What frequencies balance?", "What lattice forms?"]
  }
}
```

#### E3 - The Flame of Synthesis
```json
{
  "node_id": "E3",
  "identity": {
    "arc": {"code": "E", "primary": "Emergence", "secondary": "Mythogenesis"},
    "condition": {"code": 3, "primary": "Crucible", "secondary": "Crisis"},
    "title": "The Flame of Synthesis",
    "role": "Fusion point",
    "tone": ["Intense", "Luminous", "Transforming"]
  },
  "evidence_markers": {
    "primary": "B", "primary_name": "Being",
    "secondary": "M", "secondary_name": "MetaSymbol",
    "thompson_primary": ["A", "B", "E", "G"],
    "thompson_secondary": ["Z", "V", "U"]
  },
  "structural_relationships": {
    "polarity_partner": {"node_id": "E4", "relationship": "Crucible ↔ Alignment"},
    "condition_resonance": {"nodes": ["D3", "R3"], "theme": "Crisis across all lenses"}
  },
  "thematic_lens": {
    "combined": "Mythogenesis Crisis",
    "description": "The fusion point; where synthesis burns brightest; the transforming flame",
    "questions": ["What fuses?", "What burns into unity?", "What new thing is forged?"]
  }
}
```

#### E4 - The Lattice Keeper
```json
{
  "node_id": "E4",
  "identity": {
    "arc": {"code": "E", "primary": "Emergence", "secondary": "Mythogenesis"},
    "condition": {"code": 4, "primary": "Alignment", "secondary": "Harmony"},
    "title": "The Lattice Keeper",
    "role": "Sustains the pattern",
    "tone": ["Structured", "Graceful", "Maintaining"]
  },
  "evidence_markers": {
    "primary": "B", "primary_name": "Being",
    "secondary": "F", "secondary_name": "Force",
    "thompson_primary": ["A", "B", "E", "G"],
    "thompson_secondary": ["N", "M", "Q", "S"]
  },
  "structural_relationships": {
    "polarity_partner": {"node_id": "E3", "relationship": "Alignment ↔ Crucible"},
    "condition_resonance": {"nodes": ["D4", "R4"], "theme": "Harmony across all lenses"}
  },
  "thematic_lens": {
    "combined": "Mythogenesis Harmony",
    "description": "The keeper of the emerged pattern; sustaining what was created; graceful maintenance",
    "questions": ["What pattern is sustained?", "What structure holds?", "Who keeps the lattice?"]
  }
}
```

#### E5 - The Dream Spore
```json
{
  "node_id": "E5",
  "identity": {
    "arc": {"code": "E", "primary": "Emergence", "secondary": "Mythogenesis"},
    "condition": {"code": 5, "primary": "Unveiling", "secondary": "Wisdom"},
    "title": "The Dream Spore",
    "role": "Memory made present",
    "tone": ["Ethereal", "Nurturing", "Seeding"]
  },
  "evidence_markers": {
    "primary": "A", "primary_name": "Action",
    "secondary": "M", "secondary_name": "MetaSymbol",
    "thompson_primary": ["H", "K", "R", "C"],
    "thompson_secondary": ["Z", "V", "U"]
  },
  "structural_relationships": {
    "polarity_partner": {"node_id": "E2", "relationship": "Unveiling ↔ Immersion"},
    "condition_resonance": {"nodes": ["D5", "R5"], "theme": "Wisdom across all lenses"}
  },
  "thematic_lens": {
    "combined": "Mythogenesis Wisdom",
    "description": "The dream that seeds new growth; wisdom that nurtures; memory made generative",
    "questions": ["What dream seeds the future?", "What wisdom nurtures?", "What memory becomes present?"]
  }
}
```

#### E6 - The Symphony
```json
{
  "node_id": "E6",
  "identity": {
    "arc": {"code": "E", "primary": "Emergence", "secondary": "Mythogenesis"},
    "condition": {"code": 6, "primary": "Return", "secondary": "Integration"},
    "title": "The Symphony",
    "role": "Culmination of becoming",
    "tone": ["Unified", "Ecstatic", "Dispersing"]
  },
  "evidence_markers": {
    "primary": "O", "primary_name": "Object",
    "secondary": "B", "secondary_name": "Being",
    "thompson_primary": ["D", "F"],
    "thompson_secondary": ["A", "B", "E", "G"]
  },
  "structural_relationships": {
    "polarity_partner": {"node_id": "E1", "relationship": "Return ↔ Dawn"},
    "condition_resonance": {"nodes": ["D6", "R6"], "theme": "Integration across all lenses"}
  },
  "thematic_lens": {
    "combined": "Mythogenesis Integration",
    "description": "The symphony of completion; all voices unified; ecstatic dispersal into new beginnings",
    "questions": ["What symphony completes?", "What unifies?", "What disperses into new potential?"]
  }
}
```

---

### Nontion (∅)

```json
{
  "node_id": "∅",
  "identity": {
    "display_name": "Nontion",
    "role": "The unobserved, the pause, integration through absence",
    "tone": ["Still", "Void", "Generative"],
    "is_node": false,
    "is_traversable": true
  },
  "evidence_markers": {
    "note": "Nontion has no evidence markers - it is the space between all categories"
  },
  "structural_relationships": {
    "note": "Nontion connects to all nodes as the center point",
    "function": "Reset, pause, integration through stillness"
  },
  "thematic_lens": {
    "combined": "The Pause",
    "description": "Neither descent nor emergence nor reflection - the space where integration happens through not-doing",
    "questions": ["What needs to rest?", "What integrates in silence?", "What resets?"]
  },
  "selection_prompts": {
    "note": "At Nontion, no selection is required - it is a moment of pause before the next node"
  }
}
```

---

## Frontend Usage

### At Each Node, Present:

1. **Node Context**
   - Display: title, role, tone, thematic lens
   - Show: polarity partner and condition resonance for navigation hints

2. **Archetype Selection**
   - Prompt: `selection_prompts.archetype`
   - Filter: None (any archetype can be viewed through any lens)
   - Context: Arc + Condition determine how the archetype is interpreted

3. **Entity Selection**
   - Prompt: `selection_prompts.entity`
   - Filter: None (any entity can be viewed through any lens)
   - Context: Arc + Condition determine how the entity is interpreted

4. **Motif Selection**
   - Prompt: `selection_prompts.motif`
   - Filter: `evidence_markers.thompson_primary` (primary) + `thompson_secondary` (secondary)
   - Weight: Primary matches weighted higher than secondary

5. **Proceed**
   - Save selections to traversal record
   - Move to next node in sequence
   - At Nontion: pause, no selection required

---

## Data Files

This schema should be implemented as:
- `miroglyph/data/node_templates.json` - Complete node templates
- Referenced by frontend for filtering and prompts
- Integrated with existing `node_profiles.json` for semantic coordinates

---

*The node template encodes the structural logic. The content (archetypes, entities, motifs) flows through that logic. The user's choices create meaning by passing content through structural lenses.*
