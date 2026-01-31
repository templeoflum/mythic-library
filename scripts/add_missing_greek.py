#!/usr/bin/env python3
"""
Add missing Greek archetypes to GR_OLYMPIANS.jsonld

These are archetypes that are referenced in relationships but don't exist in the catalog.
"""

import json
from pathlib import Path

# The 36 missing Greek archetypes with their data
MISSING_ARCHETYPES = [
    {
        "@id": "arch:GR-ACHILLES",
        "@type": "Archetype",
        "name": "Achilles",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Greatest of the Greek warriors at Troy. Son of the mortal Peleus and sea-nymph Thetis. His wrath and glory define the Iliad. The paradigm of heroic excellence (aristeia) and tragic mortality.",
        "spectralCoordinates": {
            "order-chaos": 0.6,
            "creation-destruction": 0.75,
            "light-shadow": 0.4,
            "active-receptive": 0.15,
            "individual-collective": 0.25,
            "ascent-descent": 0.35,
            "stasis-transformation": 0.65,
            "voluntary-fated": 0.7
        },
        "instantiates": [
            {"primordial": "primordial:warrior", "weight": 0.95, "aspects": ["supreme fighter", "battle fury"]},
            {"primordial": "primordial:hero", "weight": 0.85, "aspects": ["mortal greatness", "tragic nobility"]}
        ],
        "coreFunction": "To embody martial excellence and the price of glory",
        "symbolicCore": "The heel that remains mortal despite divine protection",
        "domains": ["war", "glory", "mortality", "wrath", "friendship", "honor"],
        "relationships": [
            {"type": "COMPLEMENT", "target": "arch:GR-ODYSSEUS", "dynamic": "force vs cunning", "strength": 0.8}
        ],
        "keywords": ["warrior", "hero", "wrath", "glory", "mortality", "trojan-war"]
    },
    {
        "@id": "arch:GR-ADONIS",
        "@type": "Archetype",
        "name": "Adonis",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Beautiful youth loved by both Aphrodite and Persephone. His annual death and rebirth mirror the vegetation cycle. The archetype of ephemeral beauty and the beloved who must die.",
        "spectralCoordinates": {
            "order-chaos": 0.45,
            "creation-destruction": 0.5,
            "light-shadow": 0.55,
            "active-receptive": 0.65,
            "individual-collective": 0.4,
            "ascent-descent": 0.5,
            "stasis-transformation": 0.8,
            "voluntary-fated": 0.75
        },
        "instantiates": [
            {"primordial": "primordial:lover", "weight": 0.9, "aspects": ["beautiful beloved", "object of desire"]},
            {"primordial": "primordial:divine-child", "weight": 0.6, "aspects": ["eternal youth", "vegetation god"]}
        ],
        "coreFunction": "To embody beauty's transience and the cycle of loss and renewal",
        "symbolicCore": "The anemone that blooms from his blood",
        "domains": ["beauty", "desire", "vegetation", "death-rebirth", "youth"],
        "relationships": [
            {"type": "COMPLEMENT", "target": "arch:GR-APHRODITE", "dynamic": "beloved of love goddess", "strength": 0.9},
            {"type": "TENSION", "target": "arch:GR-PERSEPHONE", "notes": "Shared between goddesses"}
        ],
        "keywords": ["beauty", "youth", "desire", "death", "rebirth", "vegetation"]
    },
    {
        "@id": "arch:GR-AEOLUS",
        "@type": "Archetype",
        "name": "Aeolus",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Keeper of the winds, appointed by Zeus. His bag of winds given to Odysseus represents controlled forces that, when released by folly, bring disaster.",
        "spectralCoordinates": {
            "order-chaos": 0.4,
            "creation-destruction": 0.5,
            "light-shadow": 0.5,
            "active-receptive": 0.35,
            "individual-collective": 0.6,
            "ascent-descent": 0.3,
            "stasis-transformation": 0.55,
            "voluntary-fated": 0.4
        },
        "instantiates": [
            {"primordial": "primordial:sovereign", "weight": 0.7, "aspects": ["wind king", "elemental ruler"]}
        ],
        "coreFunction": "To control the chaotic forces of air and storm",
        "symbolicCore": "The bag of winds - contained chaos",
        "domains": ["winds", "storms", "control", "hospitality"],
        "keywords": ["wind", "storm", "control", "odyssey"]
    },
    {
        "@id": "arch:GR-AMPHITRITE",
        "@type": "Archetype",
        "name": "Amphitrite",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Sea goddess and queen consort of Poseidon. A Nereid who initially fled his advances. Represents the vast, calm depths of the sea as opposed to Poseidon's storms.",
        "spectralCoordinates": {
            "order-chaos": 0.35,
            "creation-destruction": 0.4,
            "light-shadow": 0.45,
            "active-receptive": 0.7,
            "individual-collective": 0.6,
            "ascent-descent": 0.65,
            "stasis-transformation": 0.35,
            "voluntary-fated": 0.5
        },
        "instantiates": [
            {"primordial": "primordial:sovereign", "weight": 0.7, "aspects": ["sea queen"]},
            {"primordial": "primordial:great-mother", "weight": 0.5, "aspects": ["nurturing depths"]}
        ],
        "coreFunction": "To embody the feminine depths of the sea",
        "symbolicCore": "The calm beneath the waves",
        "domains": ["sea", "depths", "sovereignty", "marine-life"],
        "relationships": [
            {"type": "COMPLEMENT", "target": "arch:GR-POSEIDON", "dynamic": "royal pair of the sea", "strength": 0.85}
        ],
        "keywords": ["sea", "queen", "depths", "calm", "nereid"]
    },
    {
        "@id": "arch:GR-ASCLEPIUS",
        "@type": "Archetype",
        "name": "Asclepius",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "God of medicine and healing, son of Apollo. Taught by Chiron, his skill grew so great he could resurrect the dead, for which Zeus struck him down. The snake-entwined staff is medicine's enduring symbol.",
        "spectralCoordinates": {
            "order-chaos": 0.25,
            "creation-destruction": 0.2,
            "light-shadow": 0.35,
            "active-receptive": 0.45,
            "individual-collective": 0.55,
            "ascent-descent": 0.45,
            "stasis-transformation": 0.3,
            "voluntary-fated": 0.35
        },
        "instantiates": [
            {"primordial": "primordial:healer", "weight": 0.95, "aspects": ["physician", "restorer"]},
            {"primordial": "primordial:hero", "weight": 0.5, "aspects": ["deified mortal"]}
        ],
        "coreFunction": "To restore health and transgress the boundary of death",
        "symbolicCore": "The staff with entwined serpent - medicine's symbol",
        "domains": ["healing", "medicine", "resurrection", "snakes"],
        "relationships": [
            {"type": "CHILD_OF", "target": "arch:GR-APOLLO", "notes": "Son of the healing god"},
            {"type": "TAUGHT_BY", "target": "arch:GR-CHIRON", "notes": "Learned medicine from the wise centaur"}
        ],
        "keywords": ["healing", "medicine", "physician", "resurrection", "serpent"]
    },
    {
        "@id": "arch:GR-BAUBO",
        "@type": "Archetype",
        "name": "Baubo",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Goddess of bawdy humor who made grieving Demeter laugh through obscene gestures. Embodies the healing power of earthly humor, the sacred feminine in its most primal, unapologetic form.",
        "spectralCoordinates": {
            "order-chaos": 0.7,
            "creation-destruction": 0.55,
            "light-shadow": 0.65,
            "active-receptive": 0.3,
            "individual-collective": 0.5,
            "ascent-descent": 0.7,
            "stasis-transformation": 0.6,
            "voluntary-fated": 0.25
        },
        "instantiates": [
            {"primordial": "primordial:trickster", "weight": 0.8, "aspects": ["bawdy jester", "taboo-breaker"]},
            {"primordial": "primordial:great-mother", "weight": 0.5, "aspects": ["primal feminine"]}
        ],
        "coreFunction": "To heal through sacred obscenity and taboo-breaking laughter",
        "symbolicCore": "The lifted skirt - shamelessness as medicine",
        "domains": ["humor", "obscenity", "fertility", "grief-relief"],
        "relationships": [
            {"type": "HELPER", "target": "arch:GR-DEMETER", "notes": "Lifted Demeter's grief"}
        ],
        "keywords": ["humor", "bawdy", "healing", "laughter", "feminine"]
    },
    {
        "@id": "arch:GR-CASTOR-POLLUX",
        "@type": "Archetype",
        "name": "Castor and Pollux (Dioscuri)",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "The Divine Twins - Castor mortal, Pollux divine. When Castor died, Pollux shared his immortality, so they alternate between Olympus and Hades. Patrons of sailors, horsemen, and brotherly love.",
        "spectralCoordinates": {
            "order-chaos": 0.4,
            "creation-destruction": 0.45,
            "light-shadow": 0.5,
            "active-receptive": 0.35,
            "individual-collective": 0.7,
            "ascent-descent": 0.5,
            "stasis-transformation": 0.55,
            "voluntary-fated": 0.45
        },
        "instantiates": [
            {"primordial": "primordial:twin", "weight": 0.95, "aspects": ["divine twins", "complementary pair"]},
            {"primordial": "primordial:hero", "weight": 0.7, "aspects": ["protectors", "adventurers"]}
        ],
        "coreFunction": "To embody the bond between mortal and divine, the unity of opposites",
        "symbolicCore": "Stars that rise and set together - eternal companionship",
        "domains": ["brotherhood", "horses", "sailors", "boxing", "duality"],
        "keywords": ["twins", "brotherhood", "sailors", "horses", "loyalty"]
    },
    {
        "@id": "arch:GR-CHARON",
        "@type": "Archetype",
        "name": "Charon",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Ferryman of the dead who carries souls across the rivers Styx and Acheron. Demands payment (the obol placed in the mouth of the dead). Grim but necessary guide between worlds.",
        "spectralCoordinates": {
            "order-chaos": 0.3,
            "creation-destruction": 0.55,
            "light-shadow": 0.75,
            "active-receptive": 0.5,
            "individual-collective": 0.6,
            "ascent-descent": 0.85,
            "stasis-transformation": 0.5,
            "voluntary-fated": 0.8
        },
        "instantiates": [
            {"primordial": "primordial:psychopomp", "weight": 0.95, "aspects": ["soul-guide", "liminal ferryman"]}
        ],
        "coreFunction": "To ferry souls across the threshold of death",
        "symbolicCore": "The coin for passage - death's toll",
        "domains": ["death", "transition", "rivers", "underworld"],
        "relationships": [
            {"type": "SERVES", "target": "arch:GR-HADES", "notes": "Ferryman of his realm"}
        ],
        "keywords": ["ferryman", "death", "underworld", "styx", "souls", "passage"]
    },
    {
        "@id": "arch:GR-CHIRON",
        "@type": "Archetype",
        "name": "Chiron",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "The wisest of the centaurs, unlike his savage kin. Teacher of heroes including Achilles, Asclepius, and Jason. His wound from Heracles' poisoned arrow was incurable, leading him to trade immortality for Prometheus's freedom.",
        "spectralCoordinates": {
            "order-chaos": 0.2,
            "creation-destruction": 0.35,
            "light-shadow": 0.3,
            "active-receptive": 0.55,
            "individual-collective": 0.65,
            "ascent-descent": 0.45,
            "stasis-transformation": 0.45,
            "voluntary-fated": 0.6
        },
        "instantiates": [
            {"primordial": "primordial:wise-elder", "weight": 0.9, "aspects": ["teacher", "mentor"]},
            {"primordial": "primordial:healer", "weight": 0.7, "aspects": ["wounded healer"]}
        ],
        "coreFunction": "To mentor heroes and embody the wounded healer archetype",
        "symbolicCore": "The unchealable wound - wisdom through suffering",
        "domains": ["teaching", "healing", "archery", "music", "wisdom"],
        "relationships": [
            {"type": "TEACHER_OF", "target": "arch:GR-ACHILLES", "notes": "Raised and trained him"},
            {"type": "TEACHER_OF", "target": "arch:GR-ASCLEPIUS", "notes": "Taught him medicine"}
        ],
        "keywords": ["centaur", "teacher", "wisdom", "healing", "mentor", "wounded-healer"]
    },
    {
        "@id": "arch:GR-CHRONOS",
        "@type": "Archetype",
        "name": "Chronos",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Personification of Time itself (distinct from Cronus the Titan). Often depicted as an old man, sometimes winged. Represents the inexorable flow of time that devours all things.",
        "spectralCoordinates": {
            "order-chaos": 0.3,
            "creation-destruction": 0.65,
            "light-shadow": 0.5,
            "active-receptive": 0.4,
            "individual-collective": 0.8,
            "ascent-descent": 0.5,
            "stasis-transformation": 0.7,
            "voluntary-fated": 0.95
        },
        "instantiates": [
            {"primordial": "primordial:destroyer", "weight": 0.7, "aspects": ["time's erosion"]},
            {"primordial": "primordial:wise-elder", "weight": 0.6, "aspects": ["aged wisdom"]}
        ],
        "coreFunction": "To embody the unstoppable flow and devouring nature of time",
        "symbolicCore": "The hourglass and scythe - measured and inexorable",
        "domains": ["time", "aging", "mortality", "seasons"],
        "keywords": ["time", "aging", "inexorable", "seasons", "mortality"]
    },
    {
        "@id": "arch:GR-CIRCE",
        "@type": "Archetype",
        "name": "Circe",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Goddess of sorcery, daughter of Helios. Transforms Odysseus's men into swine but becomes his lover and advisor. Embodies dangerous feminine power that can either destroy or enlighten.",
        "spectralCoordinates": {
            "order-chaos": 0.6,
            "creation-destruction": 0.55,
            "light-shadow": 0.65,
            "active-receptive": 0.35,
            "individual-collective": 0.3,
            "ascent-descent": 0.55,
            "stasis-transformation": 0.75,
            "voluntary-fated": 0.3
        },
        "instantiates": [
            {"primordial": "primordial:magician", "weight": 0.9, "aspects": ["sorceress", "transformer"]},
            {"primordial": "primordial:lover", "weight": 0.6, "aspects": ["divine lover"]}
        ],
        "coreFunction": "To transform through magic, revealing hidden natures",
        "symbolicCore": "The wand that transforms men to beasts - revealing true nature",
        "domains": ["magic", "transformation", "herbs", "prophecy"],
        "relationships": [
            {"type": "LOVER_OF", "target": "arch:GR-ODYSSEUS", "notes": "Kept him for a year"}
        ],
        "keywords": ["witch", "magic", "transformation", "herbs", "odyssey"]
    },
    {
        "@id": "arch:GR-DAIMON",
        "@type": "Archetype",
        "name": "Daimon",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Personal guiding spirit or divine intermediary. Socrates' daimonion warned him against wrong action. Not demon but genius - the divine portion within or attending each soul.",
        "spectralCoordinates": {
            "order-chaos": 0.4,
            "creation-destruction": 0.45,
            "light-shadow": 0.55,
            "active-receptive": 0.5,
            "individual-collective": 0.35,
            "ascent-descent": 0.45,
            "stasis-transformation": 0.4,
            "voluntary-fated": 0.6
        },
        "instantiates": [
            {"primordial": "primordial:self", "weight": 0.8, "aspects": ["higher self", "inner voice"]},
            {"primordial": "primordial:psychopomp", "weight": 0.5, "aspects": ["guide"]}
        ],
        "coreFunction": "To guide the individual soul toward its proper destiny",
        "symbolicCore": "The inner voice that warns and guides",
        "domains": ["guidance", "conscience", "fate", "individual-destiny"],
        "keywords": ["spirit", "guide", "conscience", "genius", "socrates"]
    },
    {
        "@id": "arch:GR-DAPHNE",
        "@type": "Archetype",
        "name": "Daphne",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Nymph pursued by Apollo who prayed for rescue and was transformed into a laurel tree. Embodies the maiden who escapes through transformation, preferring death of self to violation.",
        "spectralCoordinates": {
            "order-chaos": 0.4,
            "creation-destruction": 0.45,
            "light-shadow": 0.45,
            "active-receptive": 0.6,
            "individual-collective": 0.35,
            "ascent-descent": 0.55,
            "stasis-transformation": 0.85,
            "voluntary-fated": 0.7
        },
        "instantiates": [
            {"primordial": "primordial:maiden", "weight": 0.85, "aspects": ["virginal", "pursued"]},
            {"primordial": "primordial:nature-spirit", "weight": 0.7, "aspects": ["nymph", "tree"]}
        ],
        "coreFunction": "To escape violation through transformation into nature",
        "symbolicCore": "The laurel tree - autonomy preserved through metamorphosis",
        "domains": ["virginity", "transformation", "nature", "escape"],
        "relationships": [
            {"type": "PURSUED_BY", "target": "arch:GR-APOLLO", "notes": "His unwanted pursuit caused her transformation"}
        ],
        "keywords": ["nymph", "laurel", "transformation", "apollo", "virginity"]
    },
    {
        "@id": "arch:GR-DIKE",
        "@type": "Archetype",
        "name": "Dike",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Goddess of justice and fair judgment, daughter of Zeus and Themis. Sits beside her father, reporting human wrongdoing. Represents moral order enforced through divine oversight.",
        "spectralCoordinates": {
            "order-chaos": 0.15,
            "creation-destruction": 0.4,
            "light-shadow": 0.25,
            "active-receptive": 0.45,
            "individual-collective": 0.7,
            "ascent-descent": 0.35,
            "stasis-transformation": 0.3,
            "voluntary-fated": 0.6
        },
        "instantiates": [
            {"primordial": "primordial:sovereign", "weight": 0.7, "aspects": ["judge", "law-keeper"]}
        ],
        "coreFunction": "To maintain justice and report wrongdoing to Zeus",
        "symbolicCore": "The scales of justice perfectly balanced",
        "domains": ["justice", "law", "morality", "judgment"],
        "relationships": [
            {"type": "CHILD_OF", "target": "arch:GR-THEMIS", "notes": "Daughter of divine law"}
        ],
        "keywords": ["justice", "law", "judgment", "morality", "hora"]
    },
    {
        "@id": "arch:GR-EOS",
        "@type": "Archetype",
        "name": "Eos",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Titaness of the dawn, sister of Helios and Selene. Rose each morning to open the gates for the sun. Known for taking mortal lovers, including Tithonus whom she made immortal but forgot to ask for eternal youth.",
        "spectralCoordinates": {
            "order-chaos": 0.35,
            "creation-destruction": 0.3,
            "light-shadow": 0.2,
            "active-receptive": 0.35,
            "individual-collective": 0.5,
            "ascent-descent": 0.25,
            "stasis-transformation": 0.4,
            "voluntary-fated": 0.5
        },
        "instantiates": [
            {"primordial": "primordial:great-mother", "weight": 0.5, "aspects": ["dawn-bringer", "renewal"]},
            {"primordial": "primordial:lover", "weight": 0.6, "aspects": ["passionate goddess"]}
        ],
        "coreFunction": "To herald each new day, embodying renewal and new beginnings",
        "symbolicCore": "Rosy fingers opening heaven's gates - eternal return",
        "domains": ["dawn", "morning", "renewal", "hope"],
        "relationships": [
            {"type": "SIBLING_OF", "target": "arch:GR-HELIOS", "notes": "Sister of the sun"},
            {"type": "SIBLING_OF", "target": "arch:GR-SELENE", "notes": "Sister of the moon"}
        ],
        "keywords": ["dawn", "morning", "titaness", "renewal", "rosy-fingered"]
    },
    {
        "@id": "arch:GR-EPIMETHEUS",
        "@type": "Archetype",
        "name": "Epimetheus",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Titan of afterthought, brother of Prometheus. Despite warnings, accepted Pandora as wife, releasing evils into the world. Represents hindsight, regret, and the human tendency to act before thinking.",
        "spectralCoordinates": {
            "order-chaos": 0.55,
            "creation-destruction": 0.5,
            "light-shadow": 0.55,
            "active-receptive": 0.6,
            "individual-collective": 0.45,
            "ascent-descent": 0.5,
            "stasis-transformation": 0.45,
            "voluntary-fated": 0.65
        },
        "instantiates": [
            {"primordial": "primordial:fool", "weight": 0.7, "aspects": ["acting without thinking"]},
            {"primordial": "primordial:creator", "weight": 0.4, "aspects": ["creature-maker"]}
        ],
        "coreFunction": "To embody learning through mistake and the wisdom of hindsight",
        "symbolicCore": "The gift accepted without thought - regret's origin",
        "domains": ["hindsight", "regret", "foolishness", "humanity"],
        "relationships": [
            {"type": "SIBLING_OF", "target": "arch:GR-PROMETHEUS", "notes": "Afterthought to forethought"},
            {"type": "POLAR_OPPOSITE", "target": "arch:GR-PROMETHEUS", "axis": "voluntary-fated", "strength": 0.85}
        ],
        "keywords": ["afterthought", "hindsight", "pandora", "titan", "regret"]
    },
    {
        "@id": "arch:GR-EROS",
        "@type": "Archetype",
        "name": "Eros",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Primordial god of love and desire. In early cosmogony, a primal force enabling creation. Later depicted as Aphrodite's son with golden arrows that inflame love and leaden ones that repel it.",
        "spectralCoordinates": {
            "order-chaos": 0.6,
            "creation-destruction": 0.25,
            "light-shadow": 0.45,
            "active-receptive": 0.3,
            "individual-collective": 0.4,
            "ascent-descent": 0.4,
            "stasis-transformation": 0.6,
            "voluntary-fated": 0.35
        },
        "instantiates": [
            {"primordial": "primordial:lover", "weight": 0.95, "aspects": ["desire", "attraction"]},
            {"primordial": "primordial:divine-child", "weight": 0.6, "aspects": ["playful", "mischievous"]}
        ],
        "coreFunction": "To ignite desire and unite opposites through love",
        "symbolicCore": "The arrow that strikes without warning - love's wound",
        "domains": ["love", "desire", "attraction", "fertility", "creation"],
        "relationships": [
            {"type": "CHILD_OF", "target": "arch:GR-APHRODITE", "notes": "Son of the love goddess"},
            {"type": "CULTURAL_ECHO", "target": "arch:RO-CUPID", "fidelity": 0.95}
        ],
        "keywords": ["love", "desire", "arrows", "cupid", "primordial"]
    },
    {
        "@id": "arch:GR-GAIA",
        "@type": "Archetype",
        "name": "Gaia",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Primordial Earth Mother, first to emerge from Chaos. Mother of Ouranos (Sky), Pontus (Sea), and the Titans. The ground of all being, from whom all terrestrial life springs.",
        "spectralCoordinates": {
            "order-chaos": 0.4,
            "creation-destruction": 0.25,
            "light-shadow": 0.5,
            "active-receptive": 0.75,
            "individual-collective": 0.85,
            "ascent-descent": 0.9,
            "stasis-transformation": 0.35,
            "voluntary-fated": 0.7
        },
        "instantiates": [
            {"primordial": "primordial:great-mother", "weight": 0.98, "aspects": ["earth mother", "source of all"]},
            {"primordial": "primordial:creator", "weight": 0.7, "aspects": ["generator of beings"]}
        ],
        "coreFunction": "To be the primordial ground from which all life emerges",
        "symbolicCore": "The earth itself - foundation of existence",
        "domains": ["earth", "fertility", "motherhood", "prophecy", "nature"],
        "relationships": [
            {"type": "MOTHER_OF", "target": "arch:GR-OURANOS", "notes": "Bore the sky"},
            {"type": "MOTHER_OF", "target": "arch:GR-CRONUS", "notes": "Mother of Titans"},
            {"type": "POLAR_OPPOSITE", "target": "arch:GR-OURANOS", "axis": "ascent-descent", "strength": 0.95}
        ],
        "keywords": ["earth", "mother", "primordial", "fertility", "nature", "titans"]
    },
    {
        "@id": "arch:GR-GRIFFIN",
        "@type": "Archetype",
        "name": "Griffin",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Mythical creature with eagle's head and wings upon a lion's body. Guardian of treasures and divine power. Combines the king of beasts with the king of birds - terrestrial and celestial sovereignty united.",
        "spectralCoordinates": {
            "order-chaos": 0.3,
            "creation-destruction": 0.45,
            "light-shadow": 0.35,
            "active-receptive": 0.25,
            "individual-collective": 0.4,
            "ascent-descent": 0.35,
            "stasis-transformation": 0.3,
            "voluntary-fated": 0.5
        },
        "instantiates": [
            {"primordial": "primordial:guardian", "weight": 0.85, "aspects": ["treasure-keeper", "protector"]},
            {"primordial": "primordial:monster", "weight": 0.5, "aspects": ["hybrid creature"]}
        ],
        "coreFunction": "To guard sacred treasures and embody dual sovereignty",
        "symbolicCore": "Eagle and lion merged - sky and earth dominion",
        "domains": ["guardianship", "treasure", "strength", "vigilance"],
        "keywords": ["hybrid", "guardian", "eagle", "lion", "treasure"]
    },
    {
        "@id": "arch:GR-HECATE",
        "@type": "Archetype",
        "name": "Hecate",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Triple goddess of magic, crossroads, and the liminal. Honored at thresholds and three-way crossings. Guides souls, rules witchcraft, and presides over the dark of the moon. Torch-bearer who sees all paths.",
        "spectralCoordinates": {
            "order-chaos": 0.55,
            "creation-destruction": 0.5,
            "light-shadow": 0.8,
            "active-receptive": 0.45,
            "individual-collective": 0.45,
            "ascent-descent": 0.6,
            "stasis-transformation": 0.65,
            "voluntary-fated": 0.45
        },
        "instantiates": [
            {"primordial": "primordial:magician", "weight": 0.9, "aspects": ["witch goddess", "spell-weaver"]},
            {"primordial": "primordial:crone", "weight": 0.75, "aspects": ["dark wisdom", "keeper of secrets"]},
            {"primordial": "primordial:psychopomp", "weight": 0.65, "aspects": ["crossroads guide"]}
        ],
        "coreFunction": "To preside over thresholds, magic, and the hidden paths",
        "symbolicCore": "The triple form at crossroads - all possibilities visible",
        "domains": ["magic", "crossroads", "witchcraft", "ghosts", "keys", "dogs"],
        "relationships": [
            {"type": "HELPED", "target": "arch:GR-DEMETER", "notes": "Aided in search for Persephone"},
            {"type": "MIRRORS", "target": "arch:GR-PERSEPHONE", "domain": "underworld connection"}
        ],
        "keywords": ["magic", "crossroads", "witchcraft", "triple-goddess", "torches", "liminal"]
    },
    {
        "@id": "arch:GR-HELIOS",
        "@type": "Archetype",
        "name": "Helios",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Titan god of the sun who drives his golden chariot across the sky each day. All-seeing witness invoked in oaths. Father of Circe and Phaethon, whose fatal ride shows the danger of borrowing divine power.",
        "spectralCoordinates": {
            "order-chaos": 0.25,
            "creation-destruction": 0.4,
            "light-shadow": 0.1,
            "active-receptive": 0.2,
            "individual-collective": 0.55,
            "ascent-descent": 0.15,
            "stasis-transformation": 0.35,
            "voluntary-fated": 0.65
        },
        "instantiates": [
            {"primordial": "primordial:great-father", "weight": 0.6, "aspects": ["sky-father aspect"]},
            {"primordial": "primordial:witness", "weight": 0.8, "aspects": ["all-seeing"]}
        ],
        "coreFunction": "To illuminate all things and bear witness to oaths",
        "symbolicCore": "The sun chariot crossing the sky - cosmic regularity",
        "domains": ["sun", "light", "sight", "oaths", "truth"],
        "relationships": [
            {"type": "FATHER_OF", "target": "arch:GR-CIRCE", "notes": "Father of the sorceress"},
            {"type": "SIBLING_OF", "target": "arch:GR-EOS", "notes": "Brother of dawn"},
            {"type": "SIBLING_OF", "target": "arch:GR-SELENE", "notes": "Brother of moon"}
        ],
        "keywords": ["sun", "titan", "chariot", "all-seeing", "light", "oath"]
    },
    {
        "@id": "arch:GR-MOIRAI",
        "@type": "Archetype",
        "name": "Moirai (The Fates)",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "The three Fates who control destiny: Clotho (spinner), Lachesis (allotter), Atropos (unturnable). Even Zeus bows to their decrees. They embody the inescapable thread of mortal life from birth to death.",
        "spectralCoordinates": {
            "order-chaos": 0.15,
            "creation-destruction": 0.5,
            "light-shadow": 0.6,
            "active-receptive": 0.4,
            "individual-collective": 0.9,
            "ascent-descent": 0.5,
            "stasis-transformation": 0.55,
            "voluntary-fated": 0.98
        },
        "instantiates": [
            {"primordial": "primordial:crone", "weight": 0.8, "aspects": ["ancient wisdom", "inevitable"]},
            {"primordial": "primordial:sovereign", "weight": 0.7, "aspects": ["cosmic law"]}
        ],
        "coreFunction": "To spin, measure, and cut the thread of each life",
        "symbolicCore": "The thread of life - spun, measured, cut",
        "domains": ["fate", "destiny", "death", "birth", "necessity"],
        "keywords": ["fate", "destiny", "thread", "clotho", "lachesis", "atropos", "inevitable"]
    },
    {
        "@id": "arch:GR-NYMPHS",
        "@type": "Archetype",
        "name": "Nymphs",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Nature spirits embodying places and features: Naiads (springs), Dryads (trees), Oreads (mountains), Nereids (sea). Divine but not immortal, they animate the living world.",
        "spectralCoordinates": {
            "order-chaos": 0.5,
            "creation-destruction": 0.35,
            "light-shadow": 0.45,
            "active-receptive": 0.6,
            "individual-collective": 0.7,
            "ascent-descent": 0.55,
            "stasis-transformation": 0.4,
            "voluntary-fated": 0.5
        },
        "instantiates": [
            {"primordial": "primordial:nature-spirit", "weight": 0.95, "aspects": ["place-spirits", "elementals"]},
            {"primordial": "primordial:maiden", "weight": 0.7, "aspects": ["youthful", "wild"]}
        ],
        "coreFunction": "To animate and embody the living spirit of places",
        "symbolicCore": "Nature ensouled - every spring, tree, and mountain alive",
        "domains": ["nature", "water", "trees", "mountains", "wilderness"],
        "keywords": ["nature", "spirits", "naiad", "dryad", "nereid", "oread"]
    },
    {
        "@id": "arch:GR-ORPHEUS",
        "@type": "Archetype",
        "name": "Orpheus",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Legendary musician whose song could charm all living things, even stones and trees. Descended to Hades to retrieve Eurydice but lost her by looking back. Founder of the Orphic mysteries.",
        "spectralCoordinates": {
            "order-chaos": 0.35,
            "creation-destruction": 0.4,
            "light-shadow": 0.45,
            "active-receptive": 0.4,
            "individual-collective": 0.4,
            "ascent-descent": 0.5,
            "stasis-transformation": 0.6,
            "voluntary-fated": 0.55
        },
        "instantiates": [
            {"primordial": "primordial:magician", "weight": 0.8, "aspects": ["music-magic", "enchanter"]},
            {"primordial": "primordial:lover", "weight": 0.75, "aspects": ["devoted husband"]},
            {"primordial": "primordial:hero", "weight": 0.6, "aspects": ["underworld journey"]}
        ],
        "coreFunction": "To demonstrate art's power over nature and death's limits",
        "symbolicCore": "The backward glance - love's failure at the threshold",
        "domains": ["music", "poetry", "death", "underworld", "mysteries"],
        "relationships": [
            {"type": "LOVER_OF", "target": "arch:GR-EURYDICE", "notes": "Lost through looking back"}
        ],
        "keywords": ["music", "poetry", "eurydice", "underworld", "lyre", "mysteries"]
    },
    {
        "@id": "arch:GR-OURANOS",
        "@type": "Archetype",
        "name": "Ouranos",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Primordial sky god, first ruler of the cosmos, son and husband of Gaia. Hated his monstrous children and imprisoned them in Gaia's depths until Cronus castrated him with an adamantine sickle.",
        "spectralCoordinates": {
            "order-chaos": 0.3,
            "creation-destruction": 0.45,
            "light-shadow": 0.4,
            "active-receptive": 0.25,
            "individual-collective": 0.75,
            "ascent-descent": 0.1,
            "stasis-transformation": 0.3,
            "voluntary-fated": 0.6
        },
        "instantiates": [
            {"primordial": "primordial:great-father", "weight": 0.85, "aspects": ["sky-father", "progenitor"]},
            {"primordial": "primordial:tyrant", "weight": 0.6, "aspects": ["imprisoning father"]}
        ],
        "coreFunction": "To embody the patriarchal sky that both creates and imprisons",
        "symbolicCore": "The castrating sickle - paternal power overthrown",
        "domains": ["sky", "fatherhood", "cosmos", "stars"],
        "relationships": [
            {"type": "CONSORT_OF", "target": "arch:GR-GAIA", "notes": "Sky covering Earth"},
            {"type": "FATHER_OF", "target": "arch:GR-CRONUS", "notes": "Castrated by his son"},
            {"type": "POLAR_OPPOSITE", "target": "arch:GR-GAIA", "axis": "ascent-descent", "strength": 0.95}
        ],
        "keywords": ["sky", "primordial", "father", "castration", "cosmos", "titans"]
    },
    {
        "@id": "arch:GR-PAN",
        "@type": "Archetype",
        "name": "Pan",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "God of the wild, shepherds, and rustic music. Goat-legged and horned, he haunts mountains and forests. His sudden appearance causes 'panic' - the terror of wild nature. Patron of pastoral life.",
        "spectralCoordinates": {
            "order-chaos": 0.75,
            "creation-destruction": 0.45,
            "light-shadow": 0.55,
            "active-receptive": 0.3,
            "individual-collective": 0.4,
            "ascent-descent": 0.65,
            "stasis-transformation": 0.5,
            "voluntary-fated": 0.35
        },
        "instantiates": [
            {"primordial": "primordial:wild-man", "weight": 0.9, "aspects": ["nature-force", "untamed"]},
            {"primordial": "primordial:trickster", "weight": 0.6, "aspects": ["lustful", "mischievous"]}
        ],
        "coreFunction": "To embody wild nature's power, terror, and fertility",
        "symbolicCore": "The panpipes - nature's music",
        "domains": ["wilderness", "shepherds", "music", "fertility", "panic"],
        "relationships": [
            {"type": "CHILD_OF", "target": "arch:GR-HERMES", "notes": "Son of the messenger god"}
        ],
        "keywords": ["wild", "goat", "panic", "pipes", "shepherds", "nature"]
    },
    {
        "@id": "arch:GR-PLEIADES",
        "@type": "Archetype",
        "name": "Pleiades",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "The Seven Sisters, daughters of Atlas and Pleione. Pursued by Orion, they were placed as stars in the heavens. Their rising and setting marked agricultural seasons.",
        "spectralCoordinates": {
            "order-chaos": 0.35,
            "creation-destruction": 0.4,
            "light-shadow": 0.3,
            "active-receptive": 0.55,
            "individual-collective": 0.8,
            "ascent-descent": 0.2,
            "stasis-transformation": 0.45,
            "voluntary-fated": 0.7
        },
        "instantiates": [
            {"primordial": "primordial:maiden", "weight": 0.8, "aspects": ["sisters", "pursued"]},
            {"primordial": "primordial:nature-spirit", "weight": 0.6, "aspects": ["stellar"]}
        ],
        "coreFunction": "To mark the seasons and embody sisterhood transformed",
        "symbolicCore": "Seven stars rising - time's markers",
        "domains": ["stars", "seasons", "sisterhood", "agriculture", "navigation"],
        "keywords": ["stars", "sisters", "atlas", "orion", "seasons", "constellation"]
    },
    {
        "@id": "arch:GR-RHEA",
        "@type": "Archetype",
        "name": "Rhea",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Titan mother of the Olympian gods. When Cronus devoured their children, she hid infant Zeus and substituted a stone. The protective mother who preserves the future against paternal destruction.",
        "spectralCoordinates": {
            "order-chaos": 0.35,
            "creation-destruction": 0.3,
            "light-shadow": 0.45,
            "active-receptive": 0.65,
            "individual-collective": 0.7,
            "ascent-descent": 0.6,
            "stasis-transformation": 0.4,
            "voluntary-fated": 0.55
        },
        "instantiates": [
            {"primordial": "primordial:great-mother", "weight": 0.9, "aspects": ["protective mother", "preserver"]},
            {"primordial": "primordial:trickster", "weight": 0.4, "aspects": ["deceiver of Cronus"]}
        ],
        "coreFunction": "To protect the divine child against devouring forces",
        "symbolicCore": "The swaddled stone - deception that saves",
        "domains": ["motherhood", "protection", "fertility", "mountains"],
        "relationships": [
            {"type": "CONSORT_OF", "target": "arch:GR-CRONUS", "notes": "Saved children from him"},
            {"type": "MOTHER_OF", "target": "arch:GR-ZEUS", "notes": "Hid him from Cronus"},
            {"type": "MOTHER_OF", "target": "arch:GR-HERA", "notes": "Mother of Olympians"}
        ],
        "keywords": ["titan", "mother", "olympians", "protection", "cronus"]
    },
    {
        "@id": "arch:GR-SELENE",
        "@type": "Archetype",
        "name": "Selene",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Titaness of the moon who drives her silver chariot across the night sky. Fell in love with the shepherd Endymion and asked Zeus to grant him eternal sleep so she could visit him forever.",
        "spectralCoordinates": {
            "order-chaos": 0.35,
            "creation-destruction": 0.4,
            "light-shadow": 0.55,
            "active-receptive": 0.6,
            "individual-collective": 0.5,
            "ascent-descent": 0.3,
            "stasis-transformation": 0.4,
            "voluntary-fated": 0.55
        },
        "instantiates": [
            {"primordial": "primordial:great-mother", "weight": 0.6, "aspects": ["lunar feminine"]},
            {"primordial": "primordial:lover", "weight": 0.7, "aspects": ["divine lover"]}
        ],
        "coreFunction": "To illuminate the night and embody the moon's cycles",
        "symbolicCore": "The silver chariot - night's gentle light",
        "domains": ["moon", "night", "cycles", "dreams"],
        "relationships": [
            {"type": "SIBLING_OF", "target": "arch:GR-HELIOS", "notes": "Sister of the sun"},
            {"type": "SIBLING_OF", "target": "arch:GR-EOS", "notes": "Sister of dawn"}
        ],
        "keywords": ["moon", "night", "titaness", "endymion", "cycles", "silver"]
    },
    {
        "@id": "arch:GR-SIRENS",
        "@type": "Archetype",
        "name": "Sirens",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Part-woman, part-bird creatures whose enchanting song lured sailors to their death on rocky shores. Embody the fatal attraction of forbidden knowledge and beauty that destroys.",
        "spectralCoordinates": {
            "order-chaos": 0.6,
            "creation-destruction": 0.7,
            "light-shadow": 0.7,
            "active-receptive": 0.4,
            "individual-collective": 0.5,
            "ascent-descent": 0.55,
            "stasis-transformation": 0.6,
            "voluntary-fated": 0.6
        },
        "instantiates": [
            {"primordial": "primordial:monster", "weight": 0.75, "aspects": ["deadly lure"]},
            {"primordial": "primordial:temptress", "weight": 0.8, "aspects": ["fatal attraction"]}
        ],
        "coreFunction": "To embody the deadly allure of forbidden beauty and knowledge",
        "symbolicCore": "The song that kills - irresistible destruction",
        "domains": ["song", "death", "sea", "temptation", "knowledge"],
        "relationships": [
            {"type": "RESISTED_BY", "target": "arch:GR-ODYSSEUS", "notes": "Bound himself to hear them"}
        ],
        "keywords": ["song", "temptation", "death", "sea", "odyssey", "dangerous"]
    },
    {
        "@id": "arch:GR-TETHYS",
        "@type": "Archetype",
        "name": "Tethys",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Titan goddess of the primal font of fresh water. Mother of all river gods and the Oceanids. With her husband Oceanus, she represents the primordial waters that nourish all life.",
        "spectralCoordinates": {
            "order-chaos": 0.4,
            "creation-destruction": 0.35,
            "light-shadow": 0.45,
            "active-receptive": 0.7,
            "individual-collective": 0.75,
            "ascent-descent": 0.6,
            "stasis-transformation": 0.35,
            "voluntary-fated": 0.55
        },
        "instantiates": [
            {"primordial": "primordial:great-mother", "weight": 0.85, "aspects": ["water-mother", "nurturer"]}
        ],
        "coreFunction": "To embody the fresh waters that sustain all terrestrial life",
        "symbolicCore": "The spring that never ceases - eternal nurture",
        "domains": ["fresh-water", "rivers", "springs", "nurture"],
        "keywords": ["titan", "water", "rivers", "mother", "springs", "oceanids"]
    },
    {
        "@id": "arch:GR-THANATOS",
        "@type": "Archetype",
        "name": "Thanatos",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Personification of peaceful death, twin brother of Hypnos (Sleep). Comes gently to release the soul from the body. Distinguished from violent death (Keres) - he is the final rest.",
        "spectralCoordinates": {
            "order-chaos": 0.3,
            "creation-destruction": 0.75,
            "light-shadow": 0.7,
            "active-receptive": 0.55,
            "individual-collective": 0.65,
            "ascent-descent": 0.75,
            "stasis-transformation": 0.9,
            "voluntary-fated": 0.95
        },
        "instantiates": [
            {"primordial": "primordial:destroyer", "weight": 0.85, "aspects": ["gentle ending"]},
            {"primordial": "primordial:psychopomp", "weight": 0.6, "aspects": ["death's release"]}
        ],
        "coreFunction": "To bring peaceful release from mortal existence",
        "symbolicCore": "The gentle touch that closes eyes forever",
        "domains": ["death", "peace", "release", "endings"],
        "relationships": [
            {"type": "TWIN_OF", "target": "hypnos", "notes": "Death and Sleep are brothers"},
            {"type": "POLAR_OPPOSITE", "target": "arch:GR-EROS", "axis": "creation-destruction", "strength": 0.9}
        ],
        "keywords": ["death", "peaceful", "ending", "release", "hypnos", "inevitable"]
    },
    {
        "@id": "arch:GR-THEMIS",
        "@type": "Archetype",
        "name": "Themis",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Titan goddess of divine law, order, and custom. Mother of the Horae and Moirai. Advisor to Zeus, she represents the natural and moral order that precedes and underlies human law.",
        "spectralCoordinates": {
            "order-chaos": 0.1,
            "creation-destruction": 0.4,
            "light-shadow": 0.3,
            "active-receptive": 0.5,
            "individual-collective": 0.8,
            "ascent-descent": 0.4,
            "stasis-transformation": 0.25,
            "voluntary-fated": 0.75
        },
        "instantiates": [
            {"primordial": "primordial:sovereign", "weight": 0.85, "aspects": ["divine law", "cosmic order"]},
            {"primordial": "primordial:wise-elder", "weight": 0.7, "aspects": ["prophetic", "counselor"]}
        ],
        "coreFunction": "To embody the divine order underlying all law and custom",
        "symbolicCore": "The scales and sword - justice embodied",
        "domains": ["law", "order", "justice", "prophecy", "custom"],
        "relationships": [
            {"type": "MOTHER_OF", "target": "arch:GR-DIKE", "notes": "Mother of Justice"},
            {"type": "MOTHER_OF", "target": "arch:GR-MOIRAI", "notes": "Mother of Fates"},
            {"type": "ADVISOR_TO", "target": "arch:GR-ZEUS", "notes": "Counsels the king of gods"}
        ],
        "keywords": ["law", "order", "titan", "justice", "prophecy", "custom", "counsel"]
    },
    {
        "@id": "arch:GR-TYPHON",
        "@type": "Archetype",
        "name": "Typhon",
        "systemCode": "GR",
        "belongsToSystem": "system:greek",
        "description": "Monstrous giant, last son of Gaia, father of famous monsters (Cerberus, Hydra, Chimera). The most terrible creature Zeus ever faced - his defeat secured Olympian rule.",
        "spectralCoordinates": {
            "order-chaos": 0.9,
            "creation-destruction": 0.85,
            "light-shadow": 0.75,
            "active-receptive": 0.15,
            "individual-collective": 0.35,
            "ascent-descent": 0.75,
            "stasis-transformation": 0.7,
            "voluntary-fated": 0.55
        },
        "instantiates": [
            {"primordial": "primordial:monster", "weight": 0.95, "aspects": ["chaos incarnate", "ultimate threat"]},
            {"primordial": "primordial:destroyer", "weight": 0.85, "aspects": ["world-ender"]}
        ],
        "coreFunction": "To embody chaos threatening cosmic order",
        "symbolicCore": "The hundred-headed storm - primordial chaos",
        "domains": ["chaos", "storms", "destruction", "monsters"],
        "relationships": [
            {"type": "CHILD_OF", "target": "arch:GR-GAIA", "notes": "Last son of Earth"},
            {"type": "ANTAGONIST", "target": "arch:GR-ZEUS", "strength": 0.95, "notes": "Greatest threat to Olympus"}
        ],
        "keywords": ["monster", "chaos", "giant", "storms", "cerberus", "hydra"]
    }
]

def main():
    base_path = Path(__file__).parent.parent
    source_file = base_path / "ACP" / "archetypes" / "greek" / "GR_OLYMPIANS.jsonld"

    # Load existing file
    with open(source_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    existing_ids = {entry["@id"] for entry in data["entries"] if "@id" in entry}

    # Filter out any that already exist and arch:GR-MARY (not Greek)
    to_add = []
    for arch in MISSING_ARCHETYPES:
        arch_id = arch["@id"]
        if arch_id in existing_ids:
            print(f"  Skipping {arch_id} (already exists)")
        elif arch_id == "arch:GR-MARY":
            print(f"  Skipping {arch_id} (not a Greek archetype)")
        else:
            to_add.append(arch)

    if not to_add:
        print("No archetypes to add!")
        return

    print(f"\nAdding {len(to_add)} new Greek archetypes:")
    for arch in to_add:
        print(f"  + {arch['@id']}: {arch['name']}")
        data["entries"].append(arch)

    # Write updated file
    with open(source_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nUpdated {source_file}")
    print(f"Total entries now: {len(data['entries'])}")

if __name__ == "__main__":
    main()
