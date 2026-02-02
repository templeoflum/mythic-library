#!/usr/bin/env python3
"""
Thompson Motif Index Builder for Mythic Library Phase 3.

Compiles a local reference of Thompson Motif Index entries relevant to
the mythic library corpus. Each entry has a code, label, parent, category,
and keywords for matching.

The Thompson Motif-Index of Folk-Literature (1955-58) is the standard
classification system for recurring elements in folk narratives.

Output: data/thompson_motif_index.json
"""

import io
import json
import sys

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# ============================================================
# Thompson Motif Index Reference
# ============================================================
# Categories:
# A - Mythological Motifs (creator, creation, cosmogony)
# B - Animals
# C - Tabu
# D - Magic / Transformation
# E - The Dead / Resurrection
# F - Marvels (otherworld, fairies, extraordinary)
# G - Ogres / Monsters
# H - Tests / Recognition
# J - The Wise and the Foolish
# K - Deceptions / Trickster
# L - Reversal of Fortune
# M - Ordaining the Future
# N - Chance and Fate
# P - Society
# Q - Rewards and Punishments
# R - Captives and Fugitives
# S - Unnatural Cruelty
# T - Sex / Marriage / Birth
# V - Religion
# Z - Miscellaneous

MOTIF_INDEX = {
    # === A: MYTHOLOGICAL MOTIFS ===
    "A0": {
        "label": "Creator",
        "parent": None,
        "category": "A",
        "keywords": ["creator", "god", "supreme being", "first god", "primordial"]
    },
    "A1": {
        "label": "Creation of the universe",
        "parent": "A0",
        "category": "A",
        "keywords": ["creation", "cosmos", "world", "beginning", "origin", "created"]
    },
    "A10": {
        "label": "Creation by thought",
        "parent": "A1",
        "category": "A",
        "keywords": ["thought", "spoke", "word", "will", "conceived", "imagined"]
    },
    "A18": {
        "label": "Creation from cosmic egg",
        "parent": "A1",
        "category": "A",
        "keywords": ["egg", "cosmic egg", "hatched", "emerged from egg"]
    },
    "A21": {
        "label": "Creator from above",
        "parent": "A0",
        "category": "A",
        "keywords": ["sky god", "above", "heaven", "descended", "came down"]
    },
    "A30": {
        "label": "Creator's companions",
        "parent": "A0",
        "category": "A",
        "keywords": ["companion", "helper", "assistant", "aided"]
    },
    "A100": {
        "label": "Deity",
        "parent": "A0",
        "category": "A",
        "keywords": ["god", "goddess", "deity", "divine", "immortal"]
    },
    "A110": {
        "label": "Origin of gods",
        "parent": "A100",
        "category": "A",
        "keywords": ["birth of god", "born", "emerged", "first gods", "theogony"]
    },
    "A120": {
        "label": "Nature and appearance of gods",
        "parent": "A100",
        "category": "A",
        "keywords": ["shape", "form", "appearance", "radiant", "terrible"]
    },
    "A150": {
        "label": "Conflict of the gods",
        "parent": "A100",
        "category": "A",
        "keywords": ["war of gods", "battle", "rebellion", "overthrow", "divine war"]
    },
    "A151": {
        "label": "Battle of gods and giants",
        "parent": "A150",
        "category": "A",
        "keywords": ["giant", "titan", "gigantomachy", "titanomachy"]
    },
    "A160": {
        "label": "Mutual relations of gods",
        "parent": "A100",
        "category": "A",
        "keywords": ["marriage of gods", "jealousy", "rival", "alliance", "divine family"]
    },
    "A162": {
        "label": "Conflicts of divine beings",
        "parent": "A150",
        "category": "A",
        "keywords": ["good vs evil", "light vs dark", "chaos vs order"]
    },
    "A170": {
        "label": "Deeds of the gods",
        "parent": "A100",
        "category": "A",
        "keywords": ["decree", "judgment", "punishment", "blessing", "intervention"]
    },
    "A200": {
        "label": "God of the upper world",
        "parent": "A100",
        "category": "A",
        "keywords": ["sky god", "heaven god", "sun god", "thunder god", "rain"]
    },
    "A210": {
        "label": "Sky-god",
        "parent": "A200",
        "category": "A",
        "keywords": ["sky", "heavens", "celestial", "firmament"]
    },
    "A220": {
        "label": "Sun-god",
        "parent": "A200",
        "category": "A",
        "keywords": ["sun", "solar", "dawn", "chariot of sun", "sun rises"]
    },
    "A240": {
        "label": "Moon-god",
        "parent": "A200",
        "category": "A",
        "keywords": ["moon", "lunar", "crescent", "waxing", "waning"]
    },
    "A250": {
        "label": "Storm-god",
        "parent": "A200",
        "category": "A",
        "keywords": ["storm", "thunder", "lightning", "tempest", "hurricane"]
    },
    "A300": {
        "label": "God of the underworld",
        "parent": "A100",
        "category": "A",
        "keywords": ["underworld", "death god", "netherworld", "land of dead", "lord of dead"]
    },
    "A310": {
        "label": "Ruler of the dead",
        "parent": "A300",
        "category": "A",
        "keywords": ["judge of dead", "ruler of dead", "king of underworld"]
    },
    "A400": {
        "label": "Gods of earth",
        "parent": "A100",
        "category": "A",
        "keywords": ["earth god", "fertility", "harvest", "mother earth", "earth goddess"]
    },
    "A410": {
        "label": "Earth-mother",
        "parent": "A400",
        "category": "A",
        "keywords": ["earth mother", "mother goddess", "great mother", "gaia", "prithvi"]
    },
    "A430": {
        "label": "God of vegetation",
        "parent": "A400",
        "category": "A",
        "keywords": ["vegetation", "grain", "corn", "harvest", "fertility", "growth"]
    },
    "A431": {
        "label": "Goddess of fertility",
        "parent": "A400",
        "category": "A",
        "keywords": ["fertility goddess", "abundance", "fruitfulness", "motherhood"]
    },
    "A500": {
        "label": "Demigods and culture heroes",
        "parent": None,
        "category": "A",
        "keywords": ["demigod", "culture hero", "half-god", "hero", "civilizer"]
    },
    "A510": {
        "label": "Culture hero as demiurge",
        "parent": "A500",
        "category": "A",
        "keywords": ["demiurge", "maker", "shaper", "world-maker"]
    },
    "A520": {
        "label": "Culture hero as transformer",
        "parent": "A500",
        "category": "A",
        "keywords": ["transformer", "shaped the world", "moved mountains", "created rivers"]
    },
    "A530": {
        "label": "Culture hero overcomes monsters",
        "parent": "A500",
        "category": "A",
        "keywords": ["slays monster", "defeats dragon", "kills beast", "overcomes serpent"]
    },
    "A540": {
        "label": "Culture hero teaches arts and crafts",
        "parent": "A500",
        "category": "A",
        "keywords": ["taught", "fire", "agriculture", "writing", "craft", "arts"]
    },
    "A541": {
        "label": "Culture hero teaches agriculture",
        "parent": "A540",
        "category": "A",
        "keywords": ["agriculture", "planting", "sowing", "corn", "grain"]
    },
    "A560": {
        "label": "Culture hero's death",
        "parent": "A500",
        "category": "A",
        "keywords": ["hero dies", "sacrifice", "departed", "ascended"]
    },
    "A600": {
        "label": "Creation of the universe",
        "parent": None,
        "category": "A",
        "keywords": ["creation", "cosmogony", "in the beginning", "chaos", "void"]
    },
    "A610": {
        "label": "Creation from primordial chaos",
        "parent": "A600",
        "category": "A",
        "keywords": ["chaos", "void", "abyss", "darkness", "formless", "waters"]
    },
    "A620": {
        "label": "Creation from body of primordial being",
        "parent": "A600",
        "category": "A",
        "keywords": ["body of giant", "dismembered", "sacrifice", "cosmic body"]
    },
    "A625": {
        "label": "World from parts of giant's body",
        "parent": "A620",
        "category": "A",
        "keywords": ["skull became sky", "blood became sea", "bones became mountains"]
    },
    "A700": {
        "label": "Creation of the earth",
        "parent": "A600",
        "category": "A",
        "keywords": ["earth formed", "land rose", "earth created"]
    },
    "A720": {
        "label": "Earth-diver",
        "parent": "A700",
        "category": "A",
        "keywords": ["dived", "dove", "brought up mud", "earth diver", "beneath waters"]
    },
    "A800": {
        "label": "Creation of the heavens",
        "parent": "A600",
        "category": "A",
        "keywords": ["sky created", "stars placed", "sun set", "moon hung"]
    },
    "A900": {
        "label": "Topographical features",
        "parent": None,
        "category": "A",
        "keywords": ["mountain formed", "river created", "lake made", "island raised"]
    },
    "A1000": {
        "label": "World catastrophe",
        "parent": None,
        "category": "A",
        "keywords": ["catastrophe", "destruction", "end of world", "apocalypse"]
    },
    "A1010": {
        "label": "Deluge / World flood",
        "parent": "A1000",
        "category": "A",
        "keywords": ["flood", "deluge", "waters", "ark", "drowned", "inundation", "submerged"]
    },
    "A1020": {
        "label": "World fire",
        "parent": "A1000",
        "category": "A",
        "keywords": ["world fire", "conflagration", "ragnarok", "burning"]
    },
    "A1030": {
        "label": "World-winter",
        "parent": "A1000",
        "category": "A",
        "keywords": ["world winter", "fimbulwinter", "ice age", "great cold"]
    },
    "A1050": {
        "label": "Destruction and renewal of world",
        "parent": "A1000",
        "category": "A",
        "keywords": ["renewal", "rebirth", "new world", "cycle", "ages of world"]
    },
    "A1200": {
        "label": "Creation of man",
        "parent": None,
        "category": "A",
        "keywords": ["created man", "first man", "formed from clay", "breathed life"]
    },
    "A1210": {
        "label": "Man made from clay",
        "parent": "A1200",
        "category": "A",
        "keywords": ["clay", "earth", "mud", "dust", "molded"]
    },
    "A1240": {
        "label": "Man made from wood",
        "parent": "A1200",
        "category": "A",
        "keywords": ["wood", "tree", "log", "carved from wood"]
    },
    "A1270": {
        "label": "Primeval human pair",
        "parent": "A1200",
        "category": "A",
        "keywords": ["first man and woman", "primeval pair", "Adam and Eve"]
    },
    "A1300": {
        "label": "Ordering of human life",
        "parent": None,
        "category": "A",
        "keywords": ["death came", "mortality", "aging", "suffering", "original sin"]
    },
    "A1310": {
        "label": "Origin of death",
        "parent": "A1300",
        "category": "A",
        "keywords": ["death entered", "mortality", "why we die", "banishment"]
    },
    "A1330": {
        "label": "Emergence of mankind from underground",
        "parent": "A1200",
        "category": "A",
        "keywords": ["emerged", "underground", "cave", "sipapuni", "lower world"]
    },
    "A1400": {
        "label": "Acquisition of culture",
        "parent": None,
        "category": "A",
        "keywords": ["fire stolen", "arts", "crafts", "agriculture", "civilization"]
    },
    "A1415": {
        "label": "Theft of fire",
        "parent": "A1400",
        "category": "A",
        "keywords": ["stole fire", "fire theft", "brought fire", "prometheus"]
    },

    # === D: MAGIC AND TRANSFORMATION ===
    "D0": {
        "label": "Transformation",
        "parent": None,
        "category": "D",
        "keywords": ["transformed", "changed into", "shape-shifted", "metamorphosis"]
    },
    "D10": {
        "label": "Transformation to animal",
        "parent": "D0",
        "category": "D",
        "keywords": ["turned into animal", "became beast", "animal form"]
    },
    "D100": {
        "label": "Transformation: man to animal",
        "parent": "D10",
        "category": "D",
        "keywords": ["man to animal", "cursed", "enchanted"]
    },
    "D150": {
        "label": "Transformation: man to bird",
        "parent": "D100",
        "category": "D",
        "keywords": ["became bird", "flew away", "wings"]
    },
    "D200": {
        "label": "Transformation: man to object",
        "parent": "D0",
        "category": "D",
        "keywords": ["turned to stone", "became tree", "became star"]
    },
    "D610": {
        "label": "Repeated transformations",
        "parent": "D0",
        "category": "D",
        "keywords": ["many shapes", "changing form", "proteus", "shape-changer"]
    },
    "D700": {
        "label": "Disenchantment",
        "parent": None,
        "category": "D",
        "keywords": ["disenchanted", "spell broken", "curse lifted", "restored"]
    },
    "D800": {
        "label": "Magic object",
        "parent": None,
        "category": "D",
        "keywords": ["magic object", "enchanted", "talisman", "amulet", "wand"]
    },
    "D810": {
        "label": "Magic object as gift",
        "parent": "D800",
        "category": "D",
        "keywords": ["gift", "given", "bestowed", "received"]
    },
    "D900": {
        "label": "Magic weapon",
        "parent": "D800",
        "category": "D",
        "keywords": ["magic sword", "magic spear", "magic bow", "thunderbolt"]
    },
    "D1000": {
        "label": "Magic body parts",
        "parent": "D800",
        "category": "D",
        "keywords": ["magic eye", "magic hand", "magic hair", "magic blood"]
    },
    "D1300": {
        "label": "Magic object gives power",
        "parent": "D800",
        "category": "D",
        "keywords": ["power", "strength", "invincible", "invisible", "flight"]
    },
    "D1400": {
        "label": "Magic object overcomes",
        "parent": "D800",
        "category": "D",
        "keywords": ["overcomes", "defeats", "destroys", "banishes"]
    },
    "D1500": {
        "label": "Magic object heals",
        "parent": "D800",
        "category": "D",
        "keywords": ["heals", "restores", "cures", "revives"]
    },
    "D1600": {
        "label": "Automatic magic object",
        "parent": "D800",
        "category": "D",
        "keywords": ["self-moving", "automatic", "self-acting", "mill", "table"]
    },
    "D1700": {
        "label": "Magic powers",
        "parent": None,
        "category": "D",
        "keywords": ["magic power", "sorcery", "witchcraft", "enchantment"]
    },
    "D1800": {
        "label": "Magic knowledge",
        "parent": "D1700",
        "category": "D",
        "keywords": ["prophecy", "divination", "wisdom", "oracle", "foresight"]
    },
    "D1900": {
        "label": "Love induced magically",
        "parent": "D1700",
        "category": "D",
        "keywords": ["love potion", "enchanted", "spell", "bewitched"]
    },
    "D2000": {
        "label": "Magic forgetfulness",
        "parent": "D1700",
        "category": "D",
        "keywords": ["forgot", "memory lost", "amnesia", "enchanted sleep"]
    },

    # === E: THE DEAD / RESURRECTION ===
    "E0": {
        "label": "Resurrection",
        "parent": None,
        "category": "E",
        "keywords": ["resurrection", "raised from dead", "revived", "brought back to life"]
    },
    "E10": {
        "label": "Resuscitation by magic",
        "parent": "E0",
        "category": "E",
        "keywords": ["magic revival", "spell", "elixir", "water of life"]
    },
    "E30": {
        "label": "Resuscitation by arrangement of members",
        "parent": "E0",
        "category": "E",
        "keywords": ["reassembled", "put together", "gathered bones"]
    },
    "E50": {
        "label": "Resuscitation by magic plant",
        "parent": "E0",
        "category": "E",
        "keywords": ["herb", "plant", "fruit", "soma", "ambrosia"]
    },
    "E100": {
        "label": "Resurrection by divine power",
        "parent": "E0",
        "category": "E",
        "keywords": ["god raised", "divine power", "miracle"]
    },
    "E200": {
        "label": "Ghost and other revenants",
        "parent": None,
        "category": "E",
        "keywords": ["ghost", "spirit", "revenant", "shade", "apparition"]
    },
    "E230": {
        "label": "Return from the dead",
        "parent": "E200",
        "category": "E",
        "keywords": ["returned from dead", "came back", "visited living"]
    },
    "E300": {
        "label": "Friendly return from dead",
        "parent": "E200",
        "category": "E",
        "keywords": ["helpful ghost", "guardian spirit", "ancestor"]
    },
    "E400": {
        "label": "Ghosts and revenants - miscellaneous",
        "parent": "E200",
        "category": "E",
        "keywords": ["haunting", "restless dead", "unquiet grave"]
    },
    "E700": {
        "label": "The soul",
        "parent": None,
        "category": "E",
        "keywords": ["soul", "ba", "ka", "atman", "spirit leaves body"]
    },
    "E20": {
        "label": "Resuscitation by prayer",
        "parent": "E0",
        "category": "E",
        "keywords": ["prayed back", "invoked", "called back", "petition"]
    },
    "E40": {
        "label": "Resuscitation by tears",
        "parent": "E0",
        "category": "E",
        "keywords": ["wept back", "tears revive", "mourning restores"]
    },
    "E60": {
        "label": "Resuscitation by kiss",
        "parent": "E0",
        "category": "E",
        "keywords": ["kiss of life", "true love's kiss", "awakened by kiss"]
    },
    "E210": {
        "label": "Dead spouse's return",
        "parent": "E200",
        "category": "E",
        "keywords": ["dead wife returns", "dead husband returns", "spouse ghost"]
    },
    "E220": {
        "label": "Dead relative's return",
        "parent": "E200",
        "category": "E",
        "keywords": ["dead parent returns", "dead child returns", "ancestor visits"]
    },
    "E240": {
        "label": "Ghost asks for proper burial",
        "parent": "E200",
        "category": "E",
        "keywords": ["unburied ghost", "needs funeral rites", "proper burial"]
    },
    "E310": {
        "label": "Dead mother returns to care for children",
        "parent": "E300",
        "category": "E",
        "keywords": ["mother ghost", "cares for children", "protective spirit"]
    },
    "E320": {
        "label": "Dead father returns to advise son",
        "parent": "E300",
        "category": "E",
        "keywords": ["father ghost", "gives advice", "warns son"]
    },
    "E410": {
        "label": "Ghosts that haunt",
        "parent": "E400",
        "category": "E",
        "keywords": ["haunted", "poltergeist", "restless spirit", "vengeful ghost"]
    },
    "E420": {
        "label": "Appearance of ghosts",
        "parent": "E400",
        "category": "E",
        "keywords": ["white shroud", "pale", "translucent", "skeletal"]
    },
    "E500": {
        "label": "The Wild Hunt",
        "parent": "E400",
        "category": "E",
        "keywords": ["wild hunt", "host of dead", "ghostly riders", "odin's hunt"]
    },
    "E600": {
        "label": "Reincarnation",
        "parent": None,
        "category": "E",
        "keywords": ["reincarnation", "rebirth", "transmigration", "metempsychosis"]
    },
    "E610": {
        "label": "Reincarnation as animal",
        "parent": "E600",
        "category": "E",
        "keywords": ["born as animal", "became animal", "animal rebirth"]
    },
    "E620": {
        "label": "Reincarnation as human",
        "parent": "E600",
        "category": "E",
        "keywords": ["born again", "new life", "human rebirth"]
    },
    "E710": {
        "label": "External soul",
        "parent": "E700",
        "category": "E",
        "keywords": ["soul outside body", "heart hidden", "life force stored"]
    },
    "E720": {
        "label": "Soul journeys",
        "parent": "E700",
        "category": "E",
        "keywords": ["soul travels", "astral travel", "spirit journey"]
    },
    "E730": {
        "label": "Soul weighed",
        "parent": "E700",
        "category": "E",
        "keywords": ["judgment", "scales", "heart weighed", "afterlife trial"]
    },

    # === F: MARVELS ===
    "F0": {
        "label": "Journey to otherworld",
        "parent": None,
        "category": "F",
        "keywords": ["otherworld", "fairy realm", "spirit world"]
    },
    "F10": {
        "label": "Journey to upper world",
        "parent": "F0",
        "category": "F",
        "keywords": ["ascended", "climbed", "sky world", "heaven"]
    },
    "F80": {
        "label": "Journey to the underworld / katabasis",
        "parent": "F0",
        "category": "F",
        "keywords": ["underworld", "descent", "netherworld", "land of dead", "katabasis", "descended"]
    },
    "F81": {
        "label": "Descent to lower world of dead",
        "parent": "F80",
        "category": "F",
        "keywords": ["descended", "went down", "entered underworld", "gate of dead"]
    },
    "F90": {
        "label": "Entrance to lower world",
        "parent": "F80",
        "category": "F",
        "keywords": ["gate", "entrance", "cave", "portal", "river crossing"]
    },
    "F100": {
        "label": "Return from underworld",
        "parent": "F80",
        "category": "F",
        "keywords": ["returned", "escaped", "came back", "ascended"]
    },
    "F110": {
        "label": "Conditions for return from underworld",
        "parent": "F100",
        "category": "F",
        "keywords": ["condition", "must not look back", "must not eat", "forbidden"]
    },
    "F200": {
        "label": "Fairy and fairy realm",
        "parent": "F0",
        "category": "F",
        "keywords": ["fairy", "sidhe", "elves", "fay", "enchanted"]
    },
    "F300": {
        "label": "Marriage to fairy",
        "parent": "F200",
        "category": "F",
        "keywords": ["fairy bride", "supernatural wife", "fairy husband"]
    },
    "F500": {
        "label": "Extraordinary persons",
        "parent": None,
        "category": "F",
        "keywords": ["giant", "dwarf", "extraordinary strength", "superhuman"]
    },
    "F600": {
        "label": "Extraordinary persons - feats",
        "parent": "F500",
        "category": "F",
        "keywords": ["feat", "labor", "trial", "impossible task"]
    },
    "F700": {
        "label": "Extraordinary places",
        "parent": None,
        "category": "F",
        "keywords": ["enchanted", "paradise", "garden", "island", "mountain"]
    },
    "F900": {
        "label": "Extraordinary occurrences",
        "parent": None,
        "category": "F",
        "keywords": ["marvel", "wonder", "miracle", "portent", "omen"]
    },
    "F20": {
        "label": "Journey to earthly paradise",
        "parent": "F0",
        "category": "F",
        "keywords": ["eden", "paradise", "blessed isles", "avalon"]
    },
    "F30": {
        "label": "Journey to underwater world",
        "parent": "F0",
        "category": "F",
        "keywords": ["underwater", "sea kingdom", "lake palace", "beneath waves"]
    },
    "F50": {
        "label": "Time passes differently in otherworld",
        "parent": "F0",
        "category": "F",
        "keywords": ["time stands still", "years pass", "rip van winkle"]
    },
    "F210": {
        "label": "Fairyland under earth",
        "parent": "F200",
        "category": "F",
        "keywords": ["hollow hill", "under mound", "sidhe dwelling"]
    },
    "F220": {
        "label": "Fairyland under water",
        "parent": "F200",
        "category": "F",
        "keywords": ["lake fairy", "water sprite", "underwater palace"]
    },
    "F250": {
        "label": "Fairy abducts human",
        "parent": "F200",
        "category": "F",
        "keywords": ["changeling", "stolen away", "taken by fairies"]
    },
    "F310": {
        "label": "Fairy lover",
        "parent": "F300",
        "category": "F",
        "keywords": ["fairy mistress", "supernatural beloved", "immortal lover"]
    },
    "F320": {
        "label": "Fairy taboo broken",
        "parent": "F300",
        "category": "F",
        "keywords": ["broke promise", "violated condition", "fairy leaves"]
    },
    "F400": {
        "label": "Spirits and demons",
        "parent": None,
        "category": "F",
        "keywords": ["spirit", "demon", "djinn", "elemental"]
    },
    "F510": {
        "label": "Giant",
        "parent": "F500",
        "category": "F",
        "keywords": ["giant", "titan", "colossus", "huge person"]
    },
    "F520": {
        "label": "Dwarf",
        "parent": "F500",
        "category": "F",
        "keywords": ["dwarf", "little person", "gnome", "earth-dweller"]
    },
    "F710": {
        "label": "Extraordinary building",
        "parent": "F700",
        "category": "F",
        "keywords": ["palace", "castle", "tower", "enchanted building"]
    },
    "F720": {
        "label": "Submarine world",
        "parent": "F700",
        "category": "F",
        "keywords": ["underwater kingdom", "sea realm", "atlantis"]
    },
    "F800": {
        "label": "Extraordinary rocks and mountains",
        "parent": "F700",
        "category": "F",
        "keywords": ["glass mountain", "magic rock", "singing stones"]
    },

    # === G: OGRES / MONSTERS ===
    "G100": {
        "label": "Giant ogre",
        "parent": None,
        "category": "G",
        "keywords": ["giant", "ogre", "troll", "monster"]
    },
    "G200": {
        "label": "Witch",
        "parent": None,
        "category": "G",
        "keywords": ["witch", "sorceress", "enchantress", "hag"]
    },
    "G300": {
        "label": "Dragon",
        "parent": None,
        "category": "G",
        "keywords": ["dragon", "serpent", "worm", "wyrm"]
    },
    "G500": {
        "label": "Ogre defeated",
        "parent": None,
        "category": "G",
        "keywords": ["slain", "defeated", "overcome", "tricked"]
    },
    "G10": {
        "label": "Cannibalism",
        "parent": None,
        "category": "G",
        "keywords": ["cannibal", "eats humans", "man-eater", "devours"]
    },
    "G11": {
        "label": "Cannibal demon",
        "parent": "G10",
        "category": "G",
        "keywords": ["demon eater", "flesh eating spirit", "rakshasa"]
    },
    "G20": {
        "label": "Ghouls and grave dwellers",
        "parent": None,
        "category": "G",
        "keywords": ["ghoul", "grave", "corpse eater", "cemetery dweller"]
    },
    "G110": {
        "label": "Giant as ogre",
        "parent": "G100",
        "category": "G",
        "keywords": ["man-eating giant", "cyclops", "one-eyed giant"]
    },
    "G120": {
        "label": "Giant ogre's strength",
        "parent": "G100",
        "category": "G",
        "keywords": ["enormous strength", "hurls boulders", "uproots trees"]
    },
    "G210": {
        "label": "Witch in animal form",
        "parent": "G200",
        "category": "G",
        "keywords": ["witch as cat", "witch as bird", "shape-shifting witch"]
    },
    "G220": {
        "label": "Witch's familiar",
        "parent": "G200",
        "category": "G",
        "keywords": ["familiar", "witch's servant", "black cat", "imp"]
    },
    "G230": {
        "label": "Witch's powers",
        "parent": "G200",
        "category": "G",
        "keywords": ["evil eye", "curse", "blight", "hex"]
    },
    "G250": {
        "label": "Witch defeated",
        "parent": "G200",
        "category": "G",
        "keywords": ["burned", "drowned", "destroyed", "witch killed"]
    },
    "G302": {
        "label": "Fire-breathing dragon",
        "parent": "G300",
        "category": "G",
        "keywords": ["fire breath", "burns", "flame", "scorches"]
    },
    "G303": {
        "label": "Many-headed dragon",
        "parent": "G300",
        "category": "G",
        "keywords": ["hydra", "multiple heads", "grows back", "regenerates"]
    },
    "G304": {
        "label": "Dragon guards treasure",
        "parent": "G300",
        "category": "G",
        "keywords": ["guards gold", "treasure hoard", "sleeps on gold"]
    },
    "G310": {
        "label": "Sea monster",
        "parent": None,
        "category": "G",
        "keywords": ["leviathan", "kraken", "sea serpent", "water monster"]
    },
    "G350": {
        "label": "Demon",
        "parent": None,
        "category": "G",
        "keywords": ["demon", "devil", "evil spirit", "fiend"]
    },
    "G400": {
        "label": "Person falls into ogre's power",
        "parent": None,
        "category": "G",
        "keywords": ["captured by ogre", "prisoner", "in monster's lair"]
    },
    "G510": {
        "label": "Ogre killed through own stupidity",
        "parent": "G500",
        "category": "G",
        "keywords": ["tricked", "fooled", "outsmarted", "ogre's stupidity"]
    },
    "G520": {
        "label": "Ogre deceived into self-injury",
        "parent": "G500",
        "category": "G",
        "keywords": ["blinds self", "hurts self", "tricked into harm"]
    },
    "G530": {
        "label": "Help from ogre's wife/daughter",
        "parent": "G500",
        "category": "G",
        "keywords": ["ogre's daughter helps", "secret ally", "betrays father"]
    },

    # === H: TESTS ===
    "H0": {
        "label": "Tests and recognition",
        "parent": None,
        "category": "H",
        "keywords": ["test", "trial", "prove", "recognition"]
    },
    "H300": {
        "label": "Tests of valor",
        "parent": "H0",
        "category": "H",
        "keywords": ["valor", "courage", "brave", "quest"]
    },
    "H900": {
        "label": "Tasks assigned",
        "parent": "H0",
        "category": "H",
        "keywords": ["task", "labor", "assigned", "impossible task"]
    },
    "H1200": {
        "label": "Quest",
        "parent": "H0",
        "category": "H",
        "keywords": ["quest", "search", "journey", "seek", "find"]
    },
    "H1210": {
        "label": "Quest assigned by king",
        "parent": "H1200",
        "category": "H",
        "keywords": ["king commands", "sent forth", "royal command"]
    },
    "H1220": {
        "label": "Quest voluntarily undertaken",
        "parent": "H1200",
        "category": "H",
        "keywords": ["volunteered", "chose", "set out", "determined"]
    },
    "H1250": {
        "label": "Quest for golden fleece",
        "parent": "H1200",
        "category": "H",
        "keywords": ["golden fleece", "argonauts", "treasure", "sacred object"]
    },
    "H1260": {
        "label": "Quest for holy grail",
        "parent": "H1200",
        "category": "H",
        "keywords": ["grail", "holy vessel", "sacred cup"]
    },
    "H1300": {
        "label": "Quest for bride",
        "parent": "H1200",
        "category": "H",
        "keywords": ["win bride", "wooing", "marriage quest"]
    },
    "H10": {
        "label": "Recognition through common knowledge",
        "parent": "H0",
        "category": "H",
        "keywords": ["recognized", "identified", "knew them by"]
    },
    "H30": {
        "label": "Recognition by token",
        "parent": "H0",
        "category": "H",
        "keywords": ["ring recognized", "birthmark", "token", "proof"]
    },
    "H50": {
        "label": "Recognition by physical sign",
        "parent": "H0",
        "category": "H",
        "keywords": ["scar", "mark", "wound", "physical proof"]
    },
    "H100": {
        "label": "Riddles",
        "parent": "H0",
        "category": "H",
        "keywords": ["riddle", "puzzle", "sphinx", "answer or die"]
    },
    "H110": {
        "label": "Riddle solved",
        "parent": "H100",
        "category": "H",
        "keywords": ["answered riddle", "solved puzzle", "defeated sphinx"]
    },
    "H200": {
        "label": "Identity tests",
        "parent": "H0",
        "category": "H",
        "keywords": ["prove identity", "slipper fits", "true heir"]
    },
    "H310": {
        "label": "Suitor tests",
        "parent": "H300",
        "category": "H",
        "keywords": ["win bride test", "prove worthiness", "compete for hand"]
    },
    "H400": {
        "label": "Chastity tests",
        "parent": "H0",
        "category": "H",
        "keywords": ["chastity test", "fidelity test", "purity proven"]
    },
    "H500": {
        "label": "Test of cleverness",
        "parent": "H0",
        "category": "H",
        "keywords": ["clever test", "wit test", "outsmart"]
    },
    "H600": {
        "label": "Symbolic interpretation tests",
        "parent": "H0",
        "category": "H",
        "keywords": ["interpret dream", "explain sign", "read omen"]
    },
    "H1000": {
        "label": "Ordeals",
        "parent": "H0",
        "category": "H",
        "keywords": ["ordeal", "trial by fire", "trial by combat"]
    },
    "H1100": {
        "label": "Tasks requiring great labor",
        "parent": "H900",
        "category": "H",
        "keywords": ["herculean labor", "impossible task", "great feat"]
    },
    "H1110": {
        "label": "Cleaning Augean stables",
        "parent": "H1100",
        "category": "H",
        "keywords": ["clean stables", "enormous mess", "impossible cleaning"]
    },
    "H1400": {
        "label": "Quest for dangerous object",
        "parent": "H1200",
        "category": "H",
        "keywords": ["fetch dangerous thing", "retrieve from monster"]
    },

    # === K: DECEPTIONS / TRICKSTER ===
    "K0": {
        "label": "Deceptions",
        "parent": None,
        "category": "K",
        "keywords": ["deception", "trick", "trickster", "cunning", "ruse"]
    },
    "K100": {
        "label": "Deceptive bargains",
        "parent": "K0",
        "category": "K",
        "keywords": ["bargain", "deal", "trade", "exchange", "wager"]
    },
    "K200": {
        "label": "Deceptions through disguise",
        "parent": "K0",
        "category": "K",
        "keywords": ["disguise", "pretend", "impersonate", "costume"]
    },
    "K300": {
        "label": "Thefts and cheats",
        "parent": "K0",
        "category": "K",
        "keywords": ["theft", "stole", "cheat", "swindled"]
    },
    "K500": {
        "label": "Escape by deception",
        "parent": "K0",
        "category": "K",
        "keywords": ["escaped", "fled", "deceived captor", "trick escape"]
    },
    "K700": {
        "label": "Capture by deception",
        "parent": "K0",
        "category": "K",
        "keywords": ["trapped", "lured", "captured", "snared"]
    },
    "K800": {
        "label": "Killing by deception",
        "parent": "K0",
        "category": "K",
        "keywords": ["killed by trick", "poisoned", "treachery", "betrayed"]
    },
    "K1000": {
        "label": "Deception into self-injury",
        "parent": "K0",
        "category": "K",
        "keywords": ["tricked into", "fooled", "self-harm", "outwitted"]
    },
    "K110": {
        "label": "Bargain to sell soul",
        "parent": "K100",
        "category": "K",
        "keywords": ["sold soul", "devil's deal", "faustian bargain"]
    },
    "K130": {
        "label": "Bargain with supernatural being cheated",
        "parent": "K100",
        "category": "K",
        "keywords": ["cheated devil", "outwitted demon", "tricked god"]
    },
    "K210": {
        "label": "Devil (god, etc.) deceived by disguise",
        "parent": "K200",
        "category": "K",
        "keywords": ["fooled devil", "god deceived", "disguised from supernatural"]
    },
    "K230": {
        "label": "Woman disguised as man",
        "parent": "K200",
        "category": "K",
        "keywords": ["cross-dressing", "woman in armor", "hidden gender"]
    },
    "K240": {
        "label": "Man disguised as woman",
        "parent": "K200",
        "category": "K",
        "keywords": ["disguised as female", "achilles type", "hidden gender"]
    },
    "K310": {
        "label": "Theft of fire",
        "parent": "K300",
        "category": "K",
        "keywords": ["stole fire", "prometheus", "fire theft"]
    },
    "K330": {
        "label": "Theft of treasure",
        "parent": "K300",
        "category": "K",
        "keywords": ["stole gold", "treasure theft", "took hoard"]
    },
    "K400": {
        "label": "Murder by deception",
        "parent": "K0",
        "category": "K",
        "keywords": ["lured to death", "treacherous murder", "deceived and killed"]
    },
    "K510": {
        "label": "Escape by substitution",
        "parent": "K500",
        "category": "K",
        "keywords": ["substitute victim", "another dies", "switched places"]
    },
    "K520": {
        "label": "Death feigned to escape",
        "parent": "K500",
        "category": "K",
        "keywords": ["played dead", "feigned death", "fake death escape"]
    },
    "K600": {
        "label": "Deception by testing",
        "parent": "K0",
        "category": "K",
        "keywords": ["false test", "rigged test", "tricked in trial"]
    },
    "K810": {
        "label": "Killed while asleep",
        "parent": "K800",
        "category": "K",
        "keywords": ["killed sleeping", "murder in bed", "treacherous attack"]
    },
    "K910": {
        "label": "Murder by drowning",
        "parent": "K800",
        "category": "K",
        "keywords": ["drowned", "pushed in water", "lured to water"]
    },

    # === L: REVERSAL OF FORTUNE ===
    "L0": {
        "label": "Reversal of fortune",
        "parent": None,
        "category": "L",
        "keywords": ["humble", "lowly", "youngest", "despised", "unpromising"]
    },
    "L100": {
        "label": "Unpromising hero",
        "parent": "L0",
        "category": "L",
        "keywords": ["youngest son", "youngest daughter", "despised", "ugly duckling"]
    },
    "L101": {
        "label": "Youngest son succeeds",
        "parent": "L100",
        "category": "L",
        "keywords": ["third son", "brothers failed", "youngest triumphs"]
    },
    "L102": {
        "label": "Youngest daughter succeeds",
        "parent": "L100",
        "category": "L",
        "keywords": ["third daughter", "sisters failed", "cinderella type"]
    },
    "L110": {
        "label": "Stupid hero succeeds",
        "parent": "L100",
        "category": "L",
        "keywords": ["simpleton", "fool succeeds", "clever fool", "lucky fool"]
    },
    "L111": {
        "label": "Small hero succeeds",
        "parent": "L100",
        "category": "L",
        "keywords": ["small", "weak", "underestimated", "david and goliath"]
    },
    "L112": {
        "label": "Poor hero succeeds",
        "parent": "L100",
        "category": "L",
        "keywords": ["poor", "beggar", "rags to riches", "peasant"]
    },
    "L113": {
        "label": "Orphan hero succeeds",
        "parent": "L100",
        "category": "L",
        "keywords": ["orphan", "abandoned child", "foundling", "no family"]
    },
    "L140": {
        "label": "Unpromising heroine",
        "parent": "L0",
        "category": "L",
        "keywords": ["ash girl", "ugly girl", "mistreated daughter", "scullery maid"]
    },
    "L160": {
        "label": "Success of the lowly",
        "parent": "L0",
        "category": "L",
        "keywords": ["slave becomes king", "servant rises", "low becomes high"]
    },
    "L200": {
        "label": "Modesty rewarded",
        "parent": "L0",
        "category": "L",
        "keywords": ["humble", "modest", "meek", "unassuming"]
    },
    "L210": {
        "label": "Modest request best",
        "parent": "L200",
        "category": "L",
        "keywords": ["asks for little", "simple wish", "modest choice"]
    },
    "L220": {
        "label": "Modest choice best",
        "parent": "L200",
        "category": "L",
        "keywords": ["chooses least", "plain gift", "simple object"]
    },
    "L300": {
        "label": "Triumph of the weak",
        "parent": "L0",
        "category": "L",
        "keywords": ["weak overcomes strong", "small beats large", "underdog wins"]
    },
    "L310": {
        "label": "Weak overcomes strong through cleverness",
        "parent": "L300",
        "category": "L",
        "keywords": ["outwits", "tricks strong opponent", "brain over brawn"]
    },
    "L400": {
        "label": "Pride brought low",
        "parent": "L0",
        "category": "L",
        "keywords": ["pride falls", "arrogant humbled", "mighty fallen"]
    },
    "L410": {
        "label": "Proud king humbled",
        "parent": "L400",
        "category": "L",
        "keywords": ["king overthrown", "tyrant falls", "mighty humbled"]
    },
    "L420": {
        "label": "Overweening pride punished",
        "parent": "L400",
        "category": "L",
        "keywords": ["hubris punished", "nemesis", "pride precedes fall"]
    },
    "L500": {
        "label": "Fortune changed by fortune's wheel",
        "parent": "L0",
        "category": "L",
        "keywords": ["wheel of fortune", "fate turns", "fortune changes"]
    },

    # === M: ORDAINING THE FUTURE ===
    "M300": {
        "label": "Prophecies",
        "parent": None,
        "category": "M",
        "keywords": ["prophecy", "foretold", "oracle", "prediction", "fate"]
    },
    "M340": {
        "label": "Unfavorable prophecies",
        "parent": "M300",
        "category": "M",
        "keywords": ["doom", "cursed", "fated to die", "destined"]
    },
    "M370": {
        "label": "Vain attempt to escape fulfillment of prophecy",
        "parent": "M300",
        "category": "M",
        "keywords": ["tried to escape fate", "despite efforts", "prophecy fulfilled"]
    },
    "M0": {
        "label": "Ordaining the future",
        "parent": None,
        "category": "M",
        "keywords": ["fate", "destiny", "future", "predetermined"]
    },
    "M100": {
        "label": "Vows and oaths",
        "parent": "M0",
        "category": "M",
        "keywords": ["vow", "oath", "swear", "promise", "pledge"]
    },
    "M101": {
        "label": "Irrevocable oath",
        "parent": "M100",
        "category": "M",
        "keywords": ["cannot break", "bound by oath", "sacred oath"]
    },
    "M110": {
        "label": "Oath broken",
        "parent": "M100",
        "category": "M",
        "keywords": ["forsworn", "broke promise", "violated oath"]
    },
    "M200": {
        "label": "Bargains and promises",
        "parent": "M0",
        "category": "M",
        "keywords": ["bargain", "promise", "deal", "agreement", "compact"]
    },
    "M201": {
        "label": "Bargain with devil",
        "parent": "M200",
        "category": "M",
        "keywords": ["devil's bargain", "sold soul", "faustian"]
    },
    "M210": {
        "label": "Bargain with god or supernatural being",
        "parent": "M200",
        "category": "M",
        "keywords": ["divine bargain", "god's promise", "covenant"]
    },
    "M211": {
        "label": "Person promises child to supernatural being",
        "parent": "M200",
        "category": "M",
        "keywords": ["promised child", "rumpelstiltskin", "first born"]
    },
    "M220": {
        "label": "Rash promise",
        "parent": "M200",
        "category": "M",
        "keywords": ["hasty promise", "regretted oath", "thoughtless vow"]
    },
    "M301": {
        "label": "Prophet foretells future",
        "parent": "M300",
        "category": "M",
        "keywords": ["seer", "prophet", "reveals future", "vision"]
    },
    "M310": {
        "label": "Prophecy of death",
        "parent": "M300",
        "category": "M",
        "keywords": ["death foretold", "will die", "fatal prophecy"]
    },
    "M311": {
        "label": "Prophecy: death at certain time",
        "parent": "M310",
        "category": "M",
        "keywords": ["death at age", "die on day", "time of death"]
    },
    "M312": {
        "label": "Prophecy: death by certain person",
        "parent": "M310",
        "category": "M",
        "keywords": ["killed by son", "slain by heir", "parricide"]
    },
    "M341": {
        "label": "Prophecy: hero's future",
        "parent": "M300",
        "category": "M",
        "keywords": ["destined for greatness", "future glory", "will become"]
    },
    "M350": {
        "label": "Prophecy: downfall of kingdom",
        "parent": "M300",
        "category": "M",
        "keywords": ["kingdom fall", "city destroyed", "empire ends"]
    },
    "M400": {
        "label": "Curses",
        "parent": "M0",
        "category": "M",
        "keywords": ["curse", "malediction", "doom", "blight"]
    },
    "M410": {
        "label": "Dying curse",
        "parent": "M400",
        "category": "M",
        "keywords": ["curses with last breath", "death curse", "dying words"]
    },
    "M411": {
        "label": "Curse by parent",
        "parent": "M400",
        "category": "M",
        "keywords": ["father's curse", "mother's curse", "parental curse"]
    },

    # === N: CHANCE AND FATE ===
    "N0": {
        "label": "Wagers and gambling",
        "parent": None,
        "category": "N",
        "keywords": ["wager", "gamble", "bet", "dice", "game of chance"]
    },
    "N100": {
        "label": "Nature of luck",
        "parent": "N0",
        "category": "N",
        "keywords": ["luck", "fortune", "chance", "fate"]
    },
    "N110": {
        "label": "Luck personified",
        "parent": "N100",
        "category": "N",
        "keywords": ["fortune goddess", "tyche", "fortuna", "luck spirit"]
    },
    "N111": {
        "label": "Good luck gained",
        "parent": "N100",
        "category": "N",
        "keywords": ["lucky", "blessed", "fortunate", "good fortune"]
    },
    "N120": {
        "label": "Determination of luck or fate",
        "parent": "N100",
        "category": "N",
        "keywords": ["lots cast", "divination", "sortilege", "drawing lots"]
    },
    "N130": {
        "label": "Changing of luck",
        "parent": "N100",
        "category": "N",
        "keywords": ["luck changes", "fortune turns", "reversal"]
    },
    "N200": {
        "label": "Lucky accidents",
        "parent": "N0",
        "category": "N",
        "keywords": ["accident", "coincidence", "by chance", "fortunate event"]
    },
    "N210": {
        "label": "Lucky accident leads to fortune",
        "parent": "N200",
        "category": "N",
        "keywords": ["stumbles on treasure", "finds by chance", "accidental discovery"]
    },
    "N250": {
        "label": "Persistent bad luck",
        "parent": "N0",
        "category": "N",
        "keywords": ["cursed", "unlucky", "bad fortune", "ill-fated"]
    },
    "N300": {
        "label": "Unlucky accidents",
        "parent": "N0",
        "category": "N",
        "keywords": ["misfortune", "accident", "mishap", "disaster"]
    },
    "N340": {
        "label": "Hasty killing through misunderstanding",
        "parent": "N300",
        "category": "N",
        "keywords": ["killed by mistake", "tragic misunderstanding", "wrong person killed"]
    },
    "N350": {
        "label": "Accidental death",
        "parent": "N300",
        "category": "N",
        "keywords": ["died by accident", "killed accidentally", "fate"]
    },
    "N400": {
        "label": "Lucky numbers",
        "parent": "N0",
        "category": "N",
        "keywords": ["three", "seven", "lucky number", "sacred number"]
    },
    "N500": {
        "label": "Treasure trove",
        "parent": "N0",
        "category": "N",
        "keywords": ["treasure found", "hidden gold", "buried treasure"]
    },
    "N510": {
        "label": "Where treasure is found",
        "parent": "N500",
        "category": "N",
        "keywords": ["cave", "buried", "underwater", "secret place"]
    },
    "N530": {
        "label": "Discovery of treasure",
        "parent": "N500",
        "category": "N",
        "keywords": ["found treasure", "stumbles on", "discovers hoard"]
    },
    "N600": {
        "label": "Lucky escapes",
        "parent": "N0",
        "category": "N",
        "keywords": ["narrow escape", "miraculous survival", "cheated death"]
    },
    "N700": {
        "label": "Fateful meeting",
        "parent": "N0",
        "category": "N",
        "keywords": ["fated to meet", "chance encounter", "destined meeting"]
    },
    "N800": {
        "label": "Helpful chance events",
        "parent": "N0",
        "category": "N",
        "keywords": ["help arrives", "timely aid", "saved by chance"]
    },

    # === Q: REWARDS AND PUNISHMENTS ===
    "Q200": {
        "label": "Deeds punished",
        "parent": None,
        "category": "Q",
        "keywords": ["punished", "cursed", "banished", "struck down"]
    },
    "Q220": {
        "label": "Punishment for hubris",
        "parent": "Q200",
        "category": "Q",
        "keywords": ["hubris", "pride", "arrogance", "presumption", "overreach"]
    },
    "Q240": {
        "label": "Punishment for disobedience",
        "parent": "Q200",
        "category": "Q",
        "keywords": ["disobedient", "defied", "broke taboo", "transgressed"]
    },
    "Q260": {
        "label": "Punishment for breaking taboo",
        "parent": "Q200",
        "category": "Q",
        "keywords": ["taboo", "forbidden", "ate forbidden fruit", "looked back"]
    },
    "Q0": {
        "label": "Rewards and punishments",
        "parent": None,
        "category": "Q",
        "keywords": ["justice", "karma", "reward", "punishment", "judgment"]
    },
    "Q10": {
        "label": "Deeds rewarded",
        "parent": "Q0",
        "category": "Q",
        "keywords": ["rewarded", "blessed", "granted wish", "given"]
    },
    "Q20": {
        "label": "Piety rewarded",
        "parent": "Q10",
        "category": "Q",
        "keywords": ["faithful", "devoted", "pious", "religious devotion"]
    },
    "Q40": {
        "label": "Kindness rewarded",
        "parent": "Q10",
        "category": "Q",
        "keywords": ["kind", "gentle", "compassionate", "helped"]
    },
    "Q41": {
        "label": "Politeness rewarded",
        "parent": "Q40",
        "category": "Q",
        "keywords": ["polite", "courteous", "respectful", "mannered"]
    },
    "Q45": {
        "label": "Hospitality rewarded",
        "parent": "Q40",
        "category": "Q",
        "keywords": ["welcomed stranger", "gave food", "sheltered", "hosted"]
    },
    "Q50": {
        "label": "Honesty rewarded",
        "parent": "Q10",
        "category": "Q",
        "keywords": ["honest", "truthful", "returned", "did not steal"]
    },
    "Q60": {
        "label": "Modesty rewarded",
        "parent": "Q10",
        "category": "Q",
        "keywords": ["modest", "humble", "unassuming", "simple"]
    },
    "Q100": {
        "label": "Nature of rewards",
        "parent": "Q0",
        "category": "Q",
        "keywords": ["reward type", "gift", "blessing", "boon"]
    },
    "Q110": {
        "label": "Material rewards",
        "parent": "Q100",
        "category": "Q",
        "keywords": ["gold", "treasure", "wealth", "riches"]
    },
    "Q111": {
        "label": "Riches as reward",
        "parent": "Q110",
        "category": "Q",
        "keywords": ["became wealthy", "given gold", "rich"]
    },
    "Q112": {
        "label": "Kingdom as reward",
        "parent": "Q110",
        "category": "Q",
        "keywords": ["became king", "given kingdom", "rules"]
    },
    "Q150": {
        "label": "Immortality as reward",
        "parent": "Q100",
        "category": "Q",
        "keywords": ["immortal", "eternal life", "deified", "apotheosis"]
    },
    "Q210": {
        "label": "Murder punished",
        "parent": "Q200",
        "category": "Q",
        "keywords": ["murderer punished", "killer cursed", "blood guilt"]
    },
    "Q250": {
        "label": "Disrespect punished",
        "parent": "Q200",
        "category": "Q",
        "keywords": ["insult gods", "blasphemy", "sacrilege"]
    },
    "Q270": {
        "label": "Cruelty punished",
        "parent": "Q200",
        "category": "Q",
        "keywords": ["cruel punished", "tyrant falls", "oppressor"]
    },
    "Q280": {
        "label": "Unkindness punished",
        "parent": "Q200",
        "category": "Q",
        "keywords": ["refused help", "denied stranger", "inhospitable"]
    },
    "Q300": {
        "label": "Nature of punishments",
        "parent": "Q0",
        "category": "Q",
        "keywords": ["punishment type", "penalty", "consequence"]
    },
    "Q400": {
        "label": "Death as punishment",
        "parent": "Q300",
        "category": "Q",
        "keywords": ["killed", "executed", "slain", "death penalty"]
    },
    "Q500": {
        "label": "Tedious punishments",
        "parent": "Q300",
        "category": "Q",
        "keywords": ["eternal labor", "endless task", "sisyphean"]
    },
    "Q550": {
        "label": "Miraculous punishments",
        "parent": "Q300",
        "category": "Q",
        "keywords": ["turned to stone", "struck by lightning", "divine punishment"]
    },

    # === R: CAPTIVES AND FUGITIVES ===
    "R0": {
        "label": "Captivity",
        "parent": None,
        "category": "R",
        "keywords": ["captive", "prisoner", "enslaved", "imprisoned"]
    },
    "R100": {
        "label": "Rescue",
        "parent": "R0",
        "category": "R",
        "keywords": ["rescued", "freed", "saved", "delivered", "liberated"]
    },
    "R200": {
        "label": "Escape and pursuit",
        "parent": "R0",
        "category": "R",
        "keywords": ["escaped", "fled", "pursuit", "chase"]
    },
    "R10": {
        "label": "Abduction",
        "parent": "R0",
        "category": "R",
        "keywords": ["abducted", "carried off", "stolen", "kidnapped"]
    },
    "R11": {
        "label": "Abduction by monster",
        "parent": "R10",
        "category": "R",
        "keywords": ["dragon takes", "monster carries", "seized by beast"]
    },
    "R12": {
        "label": "Abduction by supernatural being",
        "parent": "R10",
        "category": "R",
        "keywords": ["taken by fairy", "god abducts", "spirit steals"]
    },
    "R13": {
        "label": "Abduction to underworld",
        "parent": "R10",
        "category": "R",
        "keywords": ["taken to hell", "underworld captive", "persephone type"]
    },
    "R50": {
        "label": "Prisoner put in pit or well",
        "parent": "R0",
        "category": "R",
        "keywords": ["thrown in pit", "dungeon", "oubliette", "well"]
    },
    "R110": {
        "label": "Rescue of captive",
        "parent": "R100",
        "category": "R",
        "keywords": ["freed prisoner", "rescued captive", "delivered"]
    },
    "R111": {
        "label": "Princess rescued from dragon",
        "parent": "R110",
        "category": "R",
        "keywords": ["maiden freed", "dragon slain", "princess saved"]
    },
    "R130": {
        "label": "Rescue by animal",
        "parent": "R100",
        "category": "R",
        "keywords": ["animal helper", "beast rescues", "grateful animal"]
    },
    "R150": {
        "label": "Rescue from prison or dungeon",
        "parent": "R100",
        "category": "R",
        "keywords": ["prison break", "freed from cell", "escaped dungeon"]
    },
    "R160": {
        "label": "Rescue from underworld",
        "parent": "R100",
        "category": "R",
        "keywords": ["brought back from dead", "orpheus type", "harrowing"]
    },
    "R210": {
        "label": "Flight from home",
        "parent": "R200",
        "category": "R",
        "keywords": ["fled home", "ran away", "left family"]
    },
    "R220": {
        "label": "Obstacles to flight",
        "parent": "R200",
        "category": "R",
        "keywords": ["barrier", "blocked", "can't escape", "trapped"]
    },
    "R230": {
        "label": "Obstacles magically overcome",
        "parent": "R220",
        "category": "R",
        "keywords": ["magic escape", "obstacle flight", "threw objects"]
    },
    "R260": {
        "label": "Pursuit",
        "parent": "R200",
        "category": "R",
        "keywords": ["chased", "hunted", "pursued", "followed"]
    },
    "R270": {
        "label": "Pursuit by transformed witch",
        "parent": "R260",
        "category": "R",
        "keywords": ["witch chases", "shape-shifting pursuer", "transformed hunter"]
    },
    "R300": {
        "label": "Refuge",
        "parent": "R0",
        "category": "R",
        "keywords": ["sanctuary", "safe place", "shelter", "haven"]
    },
    "R310": {
        "label": "Refuge in church",
        "parent": "R300",
        "category": "R",
        "keywords": ["sanctuary", "temple", "sacred refuge", "altar"]
    },
    "R320": {
        "label": "Refuge in tree",
        "parent": "R300",
        "category": "R",
        "keywords": ["climbed tree", "hid in branches", "world tree"]
    },

    # === S: UNNATURAL CRUELTY ===
    "S0": {
        "label": "Cruel relative",
        "parent": None,
        "category": "S",
        "keywords": ["cruel", "jealous", "stepmother", "envious"]
    },
    "S100": {
        "label": "Persecuted wife/husband",
        "parent": "S0",
        "category": "S",
        "keywords": ["persecuted", "falsely accused", "banished", "cast out"]
    },
    "S300": {
        "label": "Abandoned children",
        "parent": "S0",
        "category": "S",
        "keywords": ["abandoned", "exposed", "left to die", "cast out"]
    },
    "S310": {
        "label": "Exposed or abandoned child rescued",
        "parent": "S300",
        "category": "S",
        "keywords": ["found", "rescued", "nursed by animal", "raised by"]
    },
    "S10": {
        "label": "Cruel parent",
        "parent": "S0",
        "category": "S",
        "keywords": ["cruel father", "cruel mother", "abusive parent"]
    },
    "S11": {
        "label": "Cruel father",
        "parent": "S10",
        "category": "S",
        "keywords": ["harsh father", "father torments", "paternal cruelty"]
    },
    "S12": {
        "label": "Cruel mother",
        "parent": "S10",
        "category": "S",
        "keywords": ["harsh mother", "mother torments", "maternal cruelty"]
    },
    "S20": {
        "label": "Cruel stepparent",
        "parent": "S0",
        "category": "S",
        "keywords": ["stepmother", "stepfather", "step-parent cruelty"]
    },
    "S31": {
        "label": "Cruel stepmother",
        "parent": "S20",
        "category": "S",
        "keywords": ["wicked stepmother", "evil stepmother", "cinderella type"]
    },
    "S50": {
        "label": "Cruel stepsisters",
        "parent": "S0",
        "category": "S",
        "keywords": ["jealous sisters", "cruel siblings", "stepsisters torment"]
    },
    "S110": {
        "label": "Murder of spouse",
        "parent": "S100",
        "category": "S",
        "keywords": ["killed wife", "killed husband", "spouse murder"]
    },
    "S111": {
        "label": "Murder of wife",
        "parent": "S110",
        "category": "S",
        "keywords": ["wife killed", "uxoricide", "murdered bride"]
    },
    "S130": {
        "label": "Casting out of wife",
        "parent": "S100",
        "category": "S",
        "keywords": ["wife banished", "cast out", "repudiated"]
    },
    "S140": {
        "label": "Cruel abandonment",
        "parent": "S100",
        "category": "S",
        "keywords": ["left to die", "deserted", "stranded"]
    },
    "S200": {
        "label": "Children cruel to parent",
        "parent": "S0",
        "category": "S",
        "keywords": ["ungrateful child", "cruel son", "cruel daughter"]
    },
    "S301": {
        "label": "Children abandoned in forest",
        "parent": "S300",
        "category": "S",
        "keywords": ["lost in woods", "hansel and gretel", "forest exposure"]
    },
    "S302": {
        "label": "Child cast adrift",
        "parent": "S300",
        "category": "S",
        "keywords": ["set adrift", "basket on river", "moses type"]
    },
    "S320": {
        "label": "Child exposed in mountain",
        "parent": "S300",
        "category": "S",
        "keywords": ["mountain exposure", "oedipus type", "left on hillside"]
    },
    "S400": {
        "label": "Cruel persecutions",
        "parent": "S0",
        "category": "S",
        "keywords": ["tormented", "persecution", "hounded", "oppressed"]
    },
    "S410": {
        "label": "Persecuted innocent",
        "parent": "S400",
        "category": "S",
        "keywords": ["wrongly accused", "innocent suffers", "false charges"]
    },
    "S450": {
        "label": "Cruel oppression",
        "parent": "S400",
        "category": "S",
        "keywords": ["slavery", "bondage", "tyrant", "oppressor"]
    },

    # === T: SEX / MARRIAGE / BIRTH ===
    "T0": {
        "label": "Love and marriage",
        "parent": None,
        "category": "T",
        "keywords": ["love", "marriage", "wedding", "bride", "woo"]
    },
    "T100": {
        "label": "Marriage",
        "parent": "T0",
        "category": "T",
        "keywords": ["married", "wedding", "wife", "husband", "bride"]
    },
    "T500": {
        "label": "Miraculous conception",
        "parent": None,
        "category": "T",
        "keywords": ["virgin birth", "miraculous", "conceived", "immaculate"]
    },
    "T510": {
        "label": "Conception from supernatural being",
        "parent": "T500",
        "category": "T",
        "keywords": ["god fathered", "divine parent", "demigod born"]
    },
    "T540": {
        "label": "Miraculous birth",
        "parent": "T500",
        "category": "T",
        "keywords": ["born from head", "born from thigh", "born from egg", "born from earth"]
    },
    "T550": {
        "label": "Monstrous birth",
        "parent": "T500",
        "category": "T",
        "keywords": ["monster born", "deformed", "half-human", "chimera"]
    },
    "T10": {
        "label": "Falling in love",
        "parent": "T0",
        "category": "T",
        "keywords": ["fell in love", "smitten", "love at first sight"]
    },
    "T11": {
        "label": "Love through sight of picture",
        "parent": "T10",
        "category": "T",
        "keywords": ["saw picture", "portrait love", "fell for image"]
    },
    "T15": {
        "label": "Love at first sight",
        "parent": "T10",
        "category": "T",
        "keywords": ["first glance", "instant love", "eyes met"]
    },
    "T20": {
        "label": "Magic love",
        "parent": "T0",
        "category": "T",
        "keywords": ["love potion", "enchanted love", "spelled to love"]
    },
    "T30": {
        "label": "Lovesickness",
        "parent": "T0",
        "category": "T",
        "keywords": ["pining", "heartbreak", "wasting away", "lovesick"]
    },
    "T50": {
        "label": "Wooing",
        "parent": "T0",
        "category": "T",
        "keywords": ["courtship", "pursuit", "winning love", "suitor"]
    },
    "T60": {
        "label": "Supernatural or unusual suitor",
        "parent": "T50",
        "category": "T",
        "keywords": ["god suitor", "beast suitor", "supernatural lover"]
    },
    "T110": {
        "label": "Extraordinary marriage",
        "parent": "T100",
        "category": "T",
        "keywords": ["marriage to animal", "fairy marriage", "divine union"]
    },
    "T120": {
        "label": "Unequal marriage",
        "parent": "T100",
        "category": "T",
        "keywords": ["mortal and god", "rich and poor", "high and low"]
    },
    "T200": {
        "label": "Married life",
        "parent": "T0",
        "category": "T",
        "keywords": ["married life", "husband and wife", "domestic"]
    },
    "T210": {
        "label": "Faithful wife",
        "parent": "T200",
        "category": "T",
        "keywords": ["faithful", "loyal wife", "penelope type", "waited"]
    },
    "T230": {
        "label": "Faithless wife",
        "parent": "T200",
        "category": "T",
        "keywords": ["adultery", "unfaithful", "betraying spouse"]
    },
    "T300": {
        "label": "Chastity and celibacy",
        "parent": "T0",
        "category": "T",
        "keywords": ["virgin", "chaste", "celibate", "pure"]
    },
    "T520": {
        "label": "Conception from eating",
        "parent": "T500",
        "category": "T",
        "keywords": ["ate fruit", "swallowed seed", "food conception"]
    },
    "T560": {
        "label": "Unusual manner of birth",
        "parent": "T500",
        "category": "T",
        "keywords": ["born differently", "emerged from", "unusual birth"]
    },
    "T580": {
        "label": "Child with remarkable birth growth",
        "parent": "T500",
        "category": "T",
        "keywords": ["rapid growth", "born adult", "quick maturity"]
    },
    "T600": {
        "label": "Care of children",
        "parent": None,
        "category": "T",
        "keywords": ["child care", "nurturing", "raising child", "foster"]
    },
    "T610": {
        "label": "Child raised by animals",
        "parent": "T600",
        "category": "T",
        "keywords": ["wolf raised", "animal foster", "feral child"]
    },

    # === V: RELIGION ===
    "V200": {
        "label": "Sacred places",
        "parent": None,
        "category": "V",
        "keywords": ["temple", "shrine", "sacred grove", "holy mountain"]
    },
    "V300": {
        "label": "Ritual and ceremony",
        "parent": None,
        "category": "V",
        "keywords": ["ritual", "ceremony", "sacrifice", "offering", "worship"]
    },
    "V310": {
        "label": "Human sacrifice",
        "parent": "V300",
        "category": "V",
        "keywords": ["human sacrifice", "offered", "altar", "blood offering"]
    },
    "V320": {
        "label": "Animal sacrifice",
        "parent": "V300",
        "category": "V",
        "keywords": ["animal sacrifice", "hecatomb", "bull", "lamb"]
    },
    "V0": {
        "label": "Religion and religious services",
        "parent": None,
        "category": "V",
        "keywords": ["religion", "worship", "faith", "devotion"]
    },
    "V10": {
        "label": "Religious sacrifices",
        "parent": "V0",
        "category": "V",
        "keywords": ["sacrifice", "offering", "oblation", "libation"]
    },
    "V50": {
        "label": "Prayer",
        "parent": "V0",
        "category": "V",
        "keywords": ["prayer", "invocation", "supplication", "entreaty"]
    },
    "V51": {
        "label": "Prayer answered",
        "parent": "V50",
        "category": "V",
        "keywords": ["prayer granted", "god responds", "wish fulfilled"]
    },
    "V60": {
        "label": "Fasting and abstinence",
        "parent": "V0",
        "category": "V",
        "keywords": ["fasting", "abstain", "renounce", "ascetic"]
    },
    "V70": {
        "label": "Pilgrimage",
        "parent": "V0",
        "category": "V",
        "keywords": ["pilgrimage", "holy journey", "sacred travel", "pilgrim"]
    },
    "V100": {
        "label": "Sacred persons",
        "parent": "V0",
        "category": "V",
        "keywords": ["priest", "shaman", "prophet", "holy person"]
    },
    "V110": {
        "label": "Priests",
        "parent": "V100",
        "category": "V",
        "keywords": ["priest", "priestess", "oracle", "druid"]
    },
    "V120": {
        "label": "Saints",
        "parent": "V100",
        "category": "V",
        "keywords": ["saint", "holy one", "blessed", "sanctified"]
    },
    "V210": {
        "label": "Sacred trees",
        "parent": "V200",
        "category": "V",
        "keywords": ["sacred tree", "world tree", "yggdrasil", "holy grove"]
    },
    "V220": {
        "label": "Sacred waters",
        "parent": "V200",
        "category": "V",
        "keywords": ["sacred well", "holy spring", "magic water", "river god"]
    },
    "V230": {
        "label": "Sacred mountains",
        "parent": "V200",
        "category": "V",
        "keywords": ["holy mountain", "mount olympus", "sacred peak", "world mountain"]
    },
    "V250": {
        "label": "Temples",
        "parent": "V200",
        "category": "V",
        "keywords": ["temple", "sanctuary", "shrine", "altar"]
    },
    "V330": {
        "label": "Conversion",
        "parent": "V0",
        "category": "V",
        "keywords": ["converted", "baptized", "changed faith", "born again"]
    },
    "V400": {
        "label": "Charity",
        "parent": "V0",
        "category": "V",
        "keywords": ["charity", "alms", "generosity", "giving"]
    },
    "V500": {
        "label": "Saints' lives and miracles",
        "parent": "V0",
        "category": "V",
        "keywords": ["miracle", "wonder", "saintly deed", "holy power"]
    },
    "V510": {
        "label": "Visions",
        "parent": "V500",
        "category": "V",
        "keywords": ["vision", "revelation", "divine sight", "apparition"]
    },

    # === B: ANIMALS ===
    "B0": {
        "label": "Mythical animals",
        "parent": None,
        "category": "B",
        "keywords": ["mythical", "legendary", "fantastic", "creature"]
    },
    "B11": {
        "label": "Dragon",
        "parent": "B0",
        "category": "B",
        "keywords": ["dragon", "serpent", "wyrm", "fire-breathing", "winged serpent"]
    },
    "B11.2": {
        "label": "Multi-headed dragon",
        "parent": "B11",
        "category": "B",
        "keywords": ["hydra", "many heads", "seven-headed", "nine-headed"]
    },
    "B12": {
        "label": "Basilisk",
        "parent": "B0",
        "category": "B",
        "keywords": ["basilisk", "cockatrice", "deadly gaze", "petrify"]
    },
    "B15": {
        "label": "Unicorn",
        "parent": "B0",
        "category": "B",
        "keywords": ["unicorn", "single horn", "pure", "virgin"]
    },
    "B20": {
        "label": "Beast-men",
        "parent": "B0",
        "category": "B",
        "keywords": ["centaur", "minotaur", "satyr", "half-human", "hybrid"]
    },
    "B30": {
        "label": "Mythical birds",
        "parent": "B0",
        "category": "B",
        "keywords": ["mythical bird", "thunderbird", "roc", "simurgh"]
    },
    "B32": {
        "label": "Phoenix",
        "parent": "B30",
        "category": "B",
        "keywords": ["phoenix", "firebird", "rebirth", "ashes", "immortal bird"]
    },
    "B40": {
        "label": "Bird-beasts",
        "parent": "B0",
        "category": "B",
        "keywords": ["griffin", "hippogriff", "winged lion", "eagle-lion"]
    },
    "B50": {
        "label": "Bird-men",
        "parent": "B0",
        "category": "B",
        "keywords": ["harpy", "siren", "winged human", "feathered"]
    },
    "B60": {
        "label": "Mythical fish and sea creatures",
        "parent": "B0",
        "category": "B",
        "keywords": ["leviathan", "sea serpent", "kraken", "sea monster"]
    },
    "B80": {
        "label": "Fish-men and merfolk",
        "parent": "B0",
        "category": "B",
        "keywords": ["mermaid", "merman", "selkie", "sea-folk", "fish-tail"]
    },
    "B100": {
        "label": "Treasure animals",
        "parent": None,
        "category": "B",
        "keywords": ["treasure", "gold-producing", "wealth", "precious"]
    },
    "B120": {
        "label": "Wise animals",
        "parent": None,
        "category": "B",
        "keywords": ["wise", "knowing", "counselor", "adviser"]
    },
    "B122": {
        "label": "Bird as adviser",
        "parent": "B120",
        "category": "B",
        "keywords": ["bird adviser", "raven", "owl", "wise bird"]
    },
    "B130": {
        "label": "Truth-telling animals",
        "parent": "B120",
        "category": "B",
        "keywords": ["truth-telling", "reveals secret", "exposes lie"]
    },
    "B140": {
        "label": "Prophetic animals",
        "parent": "B120",
        "category": "B",
        "keywords": ["prophetic", "foretells", "omen", "portent"]
    },
    "B150": {
        "label": "Oracular animals",
        "parent": "B120",
        "category": "B",
        "keywords": ["oracle", "speaks wisdom", "divine message"]
    },
    "B180": {
        "label": "Magic quadrupeds",
        "parent": None,
        "category": "B",
        "keywords": ["magic horse", "magic wolf", "magic steed", "enchanted beast"]
    },
    "B184": {
        "label": "Magic horse",
        "parent": "B180",
        "category": "B",
        "keywords": ["magic horse", "flying horse", "Pegasus", "eight-legged"]
    },
    "B210": {
        "label": "Speaking animals",
        "parent": None,
        "category": "B",
        "keywords": ["speaking", "talks", "human speech", "animal speaks"]
    },
    "B300": {
        "label": "Helpful animals",
        "parent": None,
        "category": "B",
        "keywords": ["helpful", "aids hero", "loyal", "serves"]
    },
    "B310": {
        "label": "Acquisition of helpful animal",
        "parent": "B300",
        "category": "B",
        "keywords": ["acquired", "won", "given", "befriended"]
    },
    "B350": {
        "label": "Grateful animals",
        "parent": "B300",
        "category": "B",
        "keywords": ["grateful", "repays kindness", "returns favor"]
    },
    "B400": {
        "label": "Helpful wild beasts",
        "parent": "B300",
        "category": "B",
        "keywords": ["wild beast", "lion", "bear", "wolf"]
    },
    "B450": {
        "label": "Helpful birds",
        "parent": "B300",
        "category": "B",
        "keywords": ["helpful bird", "eagle", "dove", "carries hero"]
    },
    "B500": {
        "label": "Services of helpful animals",
        "parent": "B300",
        "category": "B",
        "keywords": ["service", "task", "labor", "work"]
    },
    "B520": {
        "label": "Animals save person's life",
        "parent": "B500",
        "category": "B",
        "keywords": ["saves life", "rescues", "protects", "defends"]
    },
    "B540": {
        "label": "Animal as carrier",
        "parent": "B500",
        "category": "B",
        "keywords": ["carries", "transports", "bears rider", "flight"]
    },
    "B600": {
        "label": "Animal husband or wife",
        "parent": None,
        "category": "B",
        "keywords": ["animal spouse", "beast marriage", "shape-shifted mate"]
    },
    "B620": {
        "label": "Animal suitor",
        "parent": "B600",
        "category": "B",
        "keywords": ["animal suitor", "beast woos", "seeks bride"]
    },
    "B640": {
        "label": "Marriage to beast by day and man by night",
        "parent": "B600",
        "category": "B",
        "keywords": ["beast by day", "man by night", "enchanted husband"]
    },

    # === C: TABU ===
    "C0": {
        "label": "Tabu: contact with supernatural",
        "parent": None,
        "category": "C",
        "keywords": ["tabu", "forbidden", "supernatural", "sacred"]
    },
    "C10": {
        "label": "Tabu: profanely calling up spirit",
        "parent": "C0",
        "category": "C",
        "keywords": ["summon", "call spirit", "invoke", "profane"]
    },
    "C30": {
        "label": "Tabu: offending supernatural relative",
        "parent": "C0",
        "category": "C",
        "keywords": ["offend", "anger", "divine relative", "supernatural kin"]
    },
    "C50": {
        "label": "Tabu: offending the gods",
        "parent": "C0",
        "category": "C",
        "keywords": ["offend gods", "blasphemy", "sacrilege", "impiety"]
    },
    "C100": {
        "label": "Sex tabu",
        "parent": None,
        "category": "C",
        "keywords": ["sex", "forbidden union", "incest", "adultery"]
    },
    "C110": {
        "label": "Tabu: forbidden sexual intercourse",
        "parent": "C100",
        "category": "C",
        "keywords": ["forbidden", "illicit", "transgression"]
    },
    "C120": {
        "label": "Tabu: kissing",
        "parent": "C100",
        "category": "C",
        "keywords": ["kiss", "forbidden kiss", "enchanted"]
    },
    "C200": {
        "label": "Eating tabu",
        "parent": None,
        "category": "C",
        "keywords": ["eating", "forbidden food", "taboo food"]
    },
    "C211": {
        "label": "Tabu: eating in otherworld",
        "parent": "C200",
        "category": "C",
        "keywords": ["otherworld food", "underworld feast", "fairy food"]
    },
    "C220": {
        "label": "Tabu: eating certain things",
        "parent": "C200",
        "category": "C",
        "keywords": ["forbidden fruit", "sacred animal", "taboo meat"]
    },
    "C300": {
        "label": "Looking tabu",
        "parent": None,
        "category": "C",
        "keywords": ["looking", "forbidden sight", "must not see"]
    },
    "C310": {
        "label": "Tabu: looking at certain person or thing",
        "parent": "C300",
        "category": "C",
        "keywords": ["gaze", "forbidden look", "blinded"]
    },
    "C312": {
        "label": "Tabu: looking back",
        "parent": "C300",
        "category": "C",
        "keywords": ["look back", "Orpheus", "Lot's wife", "turned to stone"]
    },
    "C320": {
        "label": "Tabu: looking into certain receptacle",
        "parent": "C300",
        "category": "C",
        "keywords": ["forbidden box", "chest", "Pandora", "curiosity"]
    },
    "C400": {
        "label": "Speaking tabu",
        "parent": None,
        "category": "C",
        "keywords": ["speaking", "silence", "forbidden words"]
    },
    "C410": {
        "label": "Tabu: asking questions",
        "parent": "C400",
        "category": "C",
        "keywords": ["question", "inquiry", "must not ask"]
    },
    "C420": {
        "label": "Tabu: uttering secrets",
        "parent": "C400",
        "category": "C",
        "keywords": ["secret", "reveal", "betray", "tell"]
    },
    "C430": {
        "label": "Name tabu",
        "parent": "C400",
        "category": "C",
        "keywords": ["name", "true name", "forbidden name", "power of name"]
    },
    "C450": {
        "label": "Tabu: boasting",
        "parent": "C400",
        "category": "C",
        "keywords": ["boast", "brag", "pride", "hubris"]
    },
    "C500": {
        "label": "Tabu: touching",
        "parent": None,
        "category": "C",
        "keywords": ["touch", "forbidden contact", "sacred object"]
    },
    "C600": {
        "label": "Unique prohibition",
        "parent": None,
        "category": "C",
        "keywords": ["one forbidden thing", "single prohibition", "unique rule"]
    },
    "C610": {
        "label": "The one forbidden place",
        "parent": "C600",
        "category": "C",
        "keywords": ["forbidden chamber", "locked room", "secret place"]
    },
    "C611": {
        "label": "Forbidden chamber",
        "parent": "C610",
        "category": "C",
        "keywords": ["bluebeard", "locked door", "forbidden room"]
    },
    "C620": {
        "label": "Tabu: partaking of the one forbidden object",
        "parent": "C600",
        "category": "C",
        "keywords": ["forbidden fruit", "apple", "one tree"]
    },
    "C630": {
        "label": "Tabu: the one forbidden time",
        "parent": "C600",
        "category": "C",
        "keywords": ["forbidden time", "midnight", "seventh day"]
    },
    "C650": {
        "label": "The one compulsory thing",
        "parent": None,
        "category": "C",
        "keywords": ["must do", "compulsion", "required", "obligation"]
    },
    "C710": {
        "label": "Tabus connected with otherworld journeys",
        "parent": None,
        "category": "C",
        "keywords": ["otherworld", "underworld", "fairy realm", "rules"]
    },
    "C900": {
        "label": "Punishment for breaking tabu",
        "parent": None,
        "category": "C",
        "keywords": ["punishment", "consequence", "curse", "doom"]
    },
    "C920": {
        "label": "Death for breaking tabu",
        "parent": "C900",
        "category": "C",
        "keywords": ["death", "killed", "struck down", "perish"]
    },
    "C960": {
        "label": "Transformation for breaking tabu",
        "parent": "C900",
        "category": "C",
        "keywords": ["transformed", "turned to stone", "became animal"]
    },

    # === J: THE WISE AND THE FOOLISH ===
    "J0": {
        "label": "Acquisition of wisdom",
        "parent": None,
        "category": "J",
        "keywords": ["wisdom", "knowledge", "learning", "understanding"]
    },
    "J10": {
        "label": "Wisdom acquired from experience",
        "parent": "J0",
        "category": "J",
        "keywords": ["experience", "learned", "trial", "hardship"]
    },
    "J21": {
        "label": "Do not believe all you hear",
        "parent": "J10",
        "category": "J",
        "keywords": ["skepticism", "doubt", "credulity"]
    },
    "J30": {
        "label": "Wisdom acquired from inference",
        "parent": "J0",
        "category": "J",
        "keywords": ["inference", "deduction", "reasoning"]
    },
    "J50": {
        "label": "Wisdom acquired from observation",
        "parent": "J0",
        "category": "J",
        "keywords": ["observation", "watching", "seeing"]
    },
    "J80": {
        "label": "Wisdom taught by parable",
        "parent": "J0",
        "category": "J",
        "keywords": ["parable", "fable", "lesson", "moral"]
    },
    "J130": {
        "label": "Wisdom learned from animals",
        "parent": "J0",
        "category": "J",
        "keywords": ["animal teacher", "beast wisdom", "nature's lesson"]
    },
    "J150": {
        "label": "Other means of acquiring wisdom",
        "parent": "J0",
        "category": "J",
        "keywords": ["wisdom", "enlightenment", "revelation"]
    },
    "J200": {
        "label": "Choices",
        "parent": None,
        "category": "J",
        "keywords": ["choice", "decision", "selection", "preference"]
    },
    "J210": {
        "label": "Choice between real and apparent values",
        "parent": "J200",
        "category": "J",
        "keywords": ["true value", "false value", "appearance", "reality"]
    },
    "J225": {
        "label": "Better a small gain than a large promise",
        "parent": "J200",
        "category": "J",
        "keywords": ["bird in hand", "certain gain", "promise"]
    },
    "J400": {
        "label": "Choice of associates",
        "parent": "J200",
        "category": "J",
        "keywords": ["friend", "ally", "companion", "associate"]
    },
    "J500": {
        "label": "Prudence and discretion",
        "parent": None,
        "category": "J",
        "keywords": ["prudence", "caution", "discretion", "careful"]
    },
    "J510": {
        "label": "Prudence in ambition",
        "parent": "J500",
        "category": "J",
        "keywords": ["ambition", "overreach", "know limits"]
    },
    "J600": {
        "label": "Forethought",
        "parent": None,
        "category": "J",
        "keywords": ["forethought", "planning", "preparation", "foresight"]
    },
    "J610": {
        "label": "Forethought in provision for food",
        "parent": "J600",
        "category": "J",
        "keywords": ["ant and grasshopper", "stored food", "winter"]
    },
    "J700": {
        "label": "Forethought in defences",
        "parent": "J600",
        "category": "J",
        "keywords": ["defense", "protection", "fortification"]
    },
    "J800": {
        "label": "Adaptability",
        "parent": None,
        "category": "J",
        "keywords": ["adapt", "flexible", "adjust", "accommodate"]
    },
    "J860": {
        "label": "Consolation in misfortune",
        "parent": "J800",
        "category": "J",
        "keywords": ["consolation", "comfort", "acceptance", "stoic"]
    },
    "J900": {
        "label": "Humility",
        "parent": None,
        "category": "J",
        "keywords": ["humble", "modest", "meek", "lowly"]
    },
    "J950": {
        "label": "Presumption punished",
        "parent": "J900",
        "category": "J",
        "keywords": ["presumption", "arrogance", "pride", "fall"]
    },
    "J1000": {
        "label": "Other aspects of wisdom",
        "parent": None,
        "category": "J",
        "keywords": ["wisdom", "sagacity", "insight"]
    },
    "J1100": {
        "label": "Cleverness",
        "parent": None,
        "category": "J",
        "keywords": ["clever", "cunning", "witty", "shrewd"]
    },
    "J1110": {
        "label": "Clever persons",
        "parent": "J1100",
        "category": "J",
        "keywords": ["clever person", "wise man", "sage"]
    },
    "J1140": {
        "label": "Cleverness in detection of truth",
        "parent": "J1100",
        "category": "J",
        "keywords": ["detection", "truth", "Solomon", "judgment"]
    },
    "J1170": {
        "label": "Clever judicial decisions",
        "parent": "J1100",
        "category": "J",
        "keywords": ["judgment", "verdict", "Solomon", "wise ruling"]
    },
    "J1250": {
        "label": "Clever verbal retorts",
        "parent": "J1100",
        "category": "J",
        "keywords": ["retort", "repartee", "wit", "comeback"]
    },
    "J1700": {
        "label": "Fools",
        "parent": None,
        "category": "J",
        "keywords": ["fool", "stupid", "simpleton", "noodlehead"]
    },
    "J1730": {
        "label": "Absurd ignorance",
        "parent": "J1700",
        "category": "J",
        "keywords": ["ignorance", "does not know", "naive"]
    },
    "J1800": {
        "label": "Absurd misunderstanding",
        "parent": "J1700",
        "category": "J",
        "keywords": ["misunderstanding", "literal", "confused"]
    },
    "J1900": {
        "label": "Absurd disregard of facts",
        "parent": "J1700",
        "category": "J",
        "keywords": ["disregard", "ignores facts", "denial"]
    },
    "J2000": {
        "label": "Absurd absent-mindedness",
        "parent": "J1700",
        "category": "J",
        "keywords": ["absent-minded", "forgets", "distracted"]
    },
    "J2100": {
        "label": "Absurd short-sightedness",
        "parent": "J1700",
        "category": "J",
        "keywords": ["short-sighted", "cannot see", "blind to"]
    },
    "J2200": {
        "label": "Absurd lack of logic",
        "parent": "J1700",
        "category": "J",
        "keywords": ["illogical", "nonsense", "absurd reasoning"]
    },
    "J2300": {
        "label": "Gullible fools",
        "parent": "J1700",
        "category": "J",
        "keywords": ["gullible", "credulous", "easily fooled"]
    },
    "J2400": {
        "label": "Foolish imitation",
        "parent": "J1700",
        "category": "J",
        "keywords": ["imitation", "copy", "mimic", "ape"]
    },
    "J2500": {
        "label": "Foolish extremes",
        "parent": "J1700",
        "category": "J",
        "keywords": ["extreme", "excessive", "too much"]
    },
    "J2600": {
        "label": "Cowardly fools",
        "parent": "J1700",
        "category": "J",
        "keywords": ["coward", "fearful", "timid"]
    },

    # === P: SOCIETY ===
    "P0": {
        "label": "Royalty and nobility",
        "parent": None,
        "category": "P",
        "keywords": ["royalty", "nobility", "aristocracy", "court"]
    },
    "P10": {
        "label": "Kings",
        "parent": "P0",
        "category": "P",
        "keywords": ["king", "monarch", "ruler", "sovereign"]
    },
    "P12": {
        "label": "Character of kings",
        "parent": "P10",
        "category": "P",
        "keywords": ["just king", "cruel king", "wise ruler"]
    },
    "P14": {
        "label": "King and subject",
        "parent": "P10",
        "category": "P",
        "keywords": ["subject", "loyalty", "fealty", "service"]
    },
    "P17": {
        "label": "Succession to the throne",
        "parent": "P10",
        "category": "P",
        "keywords": ["succession", "heir", "crown", "inherit"]
    },
    "P20": {
        "label": "Queens",
        "parent": "P0",
        "category": "P",
        "keywords": ["queen", "consort", "empress"]
    },
    "P30": {
        "label": "Princes",
        "parent": "P0",
        "category": "P",
        "keywords": ["prince", "heir", "royal son"]
    },
    "P40": {
        "label": "Princesses",
        "parent": "P0",
        "category": "P",
        "keywords": ["princess", "royal daughter", "maiden"]
    },
    "P50": {
        "label": "Noblemen and knights",
        "parent": "P0",
        "category": "P",
        "keywords": ["knight", "lord", "nobleman", "baron"]
    },
    "P100": {
        "label": "Other social orders",
        "parent": None,
        "category": "P",
        "keywords": ["social class", "caste", "rank", "station"]
    },
    "P150": {
        "label": "Rich and poor",
        "parent": "P100",
        "category": "P",
        "keywords": ["rich", "poor", "wealth", "poverty"]
    },
    "P160": {
        "label": "Beggars",
        "parent": "P100",
        "category": "P",
        "keywords": ["beggar", "pauper", "mendicant"]
    },
    "P170": {
        "label": "Slaves",
        "parent": "P100",
        "category": "P",
        "keywords": ["slave", "bondage", "servant", "thrall"]
    },
    "P200": {
        "label": "The family",
        "parent": None,
        "category": "P",
        "keywords": ["family", "kin", "relatives", "household"]
    },
    "P210": {
        "label": "Husband and wife",
        "parent": "P200",
        "category": "P",
        "keywords": ["husband", "wife", "spouse", "marriage"]
    },
    "P230": {
        "label": "Parents and children",
        "parent": "P200",
        "category": "P",
        "keywords": ["parent", "child", "father", "mother", "son", "daughter"]
    },
    "P250": {
        "label": "Brothers and sisters",
        "parent": "P200",
        "category": "P",
        "keywords": ["brother", "sister", "sibling", "twin"]
    },
    "P260": {
        "label": "Relations by marriage",
        "parent": "P200",
        "category": "P",
        "keywords": ["in-law", "stepmother", "stepfather"]
    },
    "P300": {
        "label": "Other social relationships",
        "parent": None,
        "category": "P",
        "keywords": ["relationship", "bond", "tie"]
    },
    "P310": {
        "label": "Friendship",
        "parent": "P300",
        "category": "P",
        "keywords": ["friend", "companion", "comrade", "loyal"]
    },
    "P320": {
        "label": "Hospitality",
        "parent": "P300",
        "category": "P",
        "keywords": ["hospitality", "guest", "host", "welcome"]
    },
    "P360": {
        "label": "Master and servant",
        "parent": "P300",
        "category": "P",
        "keywords": ["master", "servant", "service", "duty"]
    },
    "P400": {
        "label": "Trades and professions",
        "parent": None,
        "category": "P",
        "keywords": ["trade", "profession", "craft", "work"]
    },
    "P410": {
        "label": "Laborers",
        "parent": "P400",
        "category": "P",
        "keywords": ["laborer", "worker", "peasant", "farmer"]
    },
    "P420": {
        "label": "Learned professions",
        "parent": "P400",
        "category": "P",
        "keywords": ["scholar", "priest", "doctor", "lawyer"]
    },
    "P430": {
        "label": "Artisans and tradesmen",
        "parent": "P400",
        "category": "P",
        "keywords": ["smith", "carpenter", "weaver", "potter"]
    },
    "P500": {
        "label": "Government",
        "parent": None,
        "category": "P",
        "keywords": ["government", "law", "rule", "order"]
    },
    "P510": {
        "label": "Law courts",
        "parent": "P500",
        "category": "P",
        "keywords": ["court", "judge", "trial", "justice"]
    },
    "P550": {
        "label": "Military affairs",
        "parent": "P500",
        "category": "P",
        "keywords": ["army", "soldier", "war", "battle"]
    },
    "P600": {
        "label": "Customs",
        "parent": None,
        "category": "P",
        "keywords": ["custom", "tradition", "ritual", "practice"]
    },
    "P610": {
        "label": "Wedding customs",
        "parent": "P600",
        "category": "P",
        "keywords": ["wedding", "marriage", "bridal", "ceremony"]
    },
    "P630": {
        "label": "Customs of inheritance",
        "parent": "P600",
        "category": "P",
        "keywords": ["inheritance", "heir", "birthright", "legacy"]
    },

    # === U: THE NATURE OF LIFE ===
    "U0": {
        "label": "Life's inequalities",
        "parent": None,
        "category": "U",
        "keywords": ["inequality", "unfair", "disparity", "imbalance"]
    },
    "U10": {
        "label": "Justice and injustice",
        "parent": "U0",
        "category": "U",
        "keywords": ["justice", "injustice", "fair", "unfair"]
    },
    "U30": {
        "label": "Rights of the strong",
        "parent": "U0",
        "category": "U",
        "keywords": ["might makes right", "power", "strong", "weak"]
    },
    "U60": {
        "label": "Wealth and poverty",
        "parent": "U0",
        "category": "U",
        "keywords": ["wealth", "poverty", "rich", "poor"]
    },
    "U100": {
        "label": "Nature of life - miscellaneous",
        "parent": None,
        "category": "U",
        "keywords": ["life", "existence", "being", "nature"]
    },
    "U110": {
        "label": "Appearances deceive",
        "parent": "U100",
        "category": "U",
        "keywords": ["appearance", "deceptive", "illusion", "false"]
    },
    "U120": {
        "label": "Nature will show itself",
        "parent": "U100",
        "category": "U",
        "keywords": ["true nature", "reveal", "cannot hide"]
    },
    "U130": {
        "label": "The power of habit",
        "parent": "U100",
        "category": "U",
        "keywords": ["habit", "custom", "ingrained", "routine"]
    },
    "U140": {
        "label": "One man's food is another man's poison",
        "parent": "U100",
        "category": "U",
        "keywords": ["relative", "perspective", "different", "subjective"]
    },
    "U210": {
        "label": "Bad ruler, bad subject",
        "parent": "U100",
        "category": "U",
        "keywords": ["ruler", "subject", "reflection", "like begets like"]
    },
    "U230": {
        "label": "The nature of sin",
        "parent": "U100",
        "category": "U",
        "keywords": ["sin", "transgression", "wrong", "evil"]
    },
    "U240": {
        "label": "Power of mind over body",
        "parent": "U100",
        "category": "U",
        "keywords": ["mind", "body", "will", "mental power"]
    },
    "U250": {
        "label": "Shortness of life",
        "parent": "U100",
        "category": "U",
        "keywords": ["mortality", "brief", "fleeting", "death"]
    },
    "U260": {
        "label": "Passage of time",
        "parent": "U100",
        "category": "U",
        "keywords": ["time", "passing", "change", "impermanence"]
    },
    "U270": {
        "label": "Security breeds indifference",
        "parent": "U100",
        "category": "U",
        "keywords": ["security", "complacency", "indifference"]
    },

    # === W: TRAITS OF CHARACTER ===
    "W0": {
        "label": "Favorable traits of character",
        "parent": None,
        "category": "W",
        "keywords": ["virtue", "good", "favorable", "positive"]
    },
    "W10": {
        "label": "Kindness",
        "parent": "W0",
        "category": "W",
        "keywords": ["kind", "gentle", "compassion", "mercy"]
    },
    "W11": {
        "label": "Generosity",
        "parent": "W0",
        "category": "W",
        "keywords": ["generous", "giving", "liberal", "bountiful"]
    },
    "W13": {
        "label": "Charity",
        "parent": "W0",
        "category": "W",
        "keywords": ["charity", "alms", "helping poor"]
    },
    "W15": {
        "label": "Pity",
        "parent": "W0",
        "category": "W",
        "keywords": ["pity", "sympathy", "compassion"]
    },
    "W20": {
        "label": "Honesty",
        "parent": "W0",
        "category": "W",
        "keywords": ["honest", "truthful", "sincere"]
    },
    "W25": {
        "label": "Patience",
        "parent": "W0",
        "category": "W",
        "keywords": ["patient", "enduring", "forbearing"]
    },
    "W28": {
        "label": "Courage",
        "parent": "W0",
        "category": "W",
        "keywords": ["courage", "brave", "valor", "fearless"]
    },
    "W31": {
        "label": "Obedience",
        "parent": "W0",
        "category": "W",
        "keywords": ["obedient", "dutiful", "compliant"]
    },
    "W34": {
        "label": "Loyalty",
        "parent": "W0",
        "category": "W",
        "keywords": ["loyal", "faithful", "devoted", "true"]
    },
    "W37": {
        "label": "Gratitude",
        "parent": "W0",
        "category": "W",
        "keywords": ["grateful", "thankful", "appreciation"]
    },
    "W100": {
        "label": "Unfavorable traits of character",
        "parent": None,
        "category": "W",
        "keywords": ["vice", "bad", "unfavorable", "negative"]
    },
    "W111": {
        "label": "Laziness",
        "parent": "W100",
        "category": "W",
        "keywords": ["lazy", "idle", "slothful", "indolent"]
    },
    "W116": {
        "label": "Vanity",
        "parent": "W100",
        "category": "W",
        "keywords": ["vain", "proud", "conceited", "narcissist"]
    },
    "W117": {
        "label": "Boastfulness",
        "parent": "W100",
        "category": "W",
        "keywords": ["boast", "brag", "arrogant"]
    },
    "W121": {
        "label": "Cowardice",
        "parent": "W100",
        "category": "W",
        "keywords": ["coward", "fearful", "timid", "craven"]
    },
    "W125": {
        "label": "Gluttony",
        "parent": "W100",
        "category": "W",
        "keywords": ["glutton", "greedy", "eating", "excess"]
    },
    "W137": {
        "label": "Curiosity",
        "parent": "W100",
        "category": "W",
        "keywords": ["curious", "nosy", "prying", "inquisitive"]
    },
    "W151": {
        "label": "Greed",
        "parent": "W100",
        "category": "W",
        "keywords": ["greedy", "avaricious", "grasping", "covetous"]
    },
    "W152": {
        "label": "Stinginess",
        "parent": "W100",
        "category": "W",
        "keywords": ["stingy", "miserly", "tight-fisted"]
    },
    "W154": {
        "label": "Ingratitude",
        "parent": "W100",
        "category": "W",
        "keywords": ["ungrateful", "thankless", "ingratitude"]
    },
    "W155": {
        "label": "Hardness of heart",
        "parent": "W100",
        "category": "W",
        "keywords": ["hard-hearted", "cruel", "merciless"]
    },
    "W165": {
        "label": "Pride and arrogance",
        "parent": "W100",
        "category": "W",
        "keywords": ["pride", "arrogance", "haughty", "hubris"]
    },
    "W167": {
        "label": "Stubbornness",
        "parent": "W100",
        "category": "W",
        "keywords": ["stubborn", "obstinate", "willful"]
    },
    "W181": {
        "label": "Jealousy",
        "parent": "W100",
        "category": "W",
        "keywords": ["jealous", "envious", "possessive"]
    },
    "W185": {
        "label": "Violence of temper",
        "parent": "W100",
        "category": "W",
        "keywords": ["temper", "rage", "anger", "wrath"]
    },
    "W195": {
        "label": "Envy",
        "parent": "W100",
        "category": "W",
        "keywords": ["envy", "covet", "resentment"]
    },

    # === X: HUMOR ===
    "X0": {
        "label": "Humor of discomfiture",
        "parent": None,
        "category": "X",
        "keywords": ["discomfiture", "embarrassment", "comeuppance"]
    },
    "X100": {
        "label": "Humor of disability",
        "parent": None,
        "category": "X",
        "keywords": ["disability", "infirmity", "mishap"]
    },
    "X110": {
        "label": "Humor of deafness",
        "parent": "X100",
        "category": "X",
        "keywords": ["deaf", "mishearing", "misunderstanding"]
    },
    "X120": {
        "label": "Humor of bad eyesight",
        "parent": "X100",
        "category": "X",
        "keywords": ["blind", "poor sight", "cannot see"]
    },
    "X200": {
        "label": "Humor dealing with tradesmen",
        "parent": None,
        "category": "X",
        "keywords": ["tradesman", "merchant", "shopkeeper"]
    },
    "X300": {
        "label": "Humor dealing with professions",
        "parent": None,
        "category": "X",
        "keywords": ["profession", "doctor", "lawyer", "priest"]
    },
    "X350": {
        "label": "Humor of doctors",
        "parent": "X300",
        "category": "X",
        "keywords": ["doctor", "physician", "medicine"]
    },
    "X410": {
        "label": "Humor of parsons",
        "parent": "X300",
        "category": "X",
        "keywords": ["parson", "priest", "clergy", "sermon"]
    },
    "X500": {
        "label": "Humor concerning other social classes",
        "parent": None,
        "category": "X",
        "keywords": ["social class", "peasant", "nobleman"]
    },
    "X600": {
        "label": "Humor concerning races or nations",
        "parent": None,
        "category": "X",
        "keywords": ["nation", "ethnic", "foreigner"]
    },
    "X700": {
        "label": "Humor concerning sex",
        "parent": None,
        "category": "X",
        "keywords": ["sex", "marriage", "husband", "wife"]
    },
    "X800": {
        "label": "Humor based on drunkenness",
        "parent": None,
        "category": "X",
        "keywords": ["drunk", "intoxicated", "wine", "ale"]
    },
    "X900": {
        "label": "Humor of lies and exaggeration",
        "parent": None,
        "category": "X",
        "keywords": ["lie", "exaggeration", "tall tale", "impossible"]
    },
    "X1000": {
        "label": "Lie: the remarkable man",
        "parent": "X900",
        "category": "X",
        "keywords": ["remarkable", "incredible", "superhuman"]
    },
    "X1100": {
        "label": "Lie: great hunters and fishermen",
        "parent": "X900",
        "category": "X",
        "keywords": ["hunter", "fisherman", "big catch", "impossible shot"]
    },
    "X1200": {
        "label": "Lies about animals",
        "parent": "X900",
        "category": "X",
        "keywords": ["animal", "beast", "incredible creature"]
    },
    "X1300": {
        "label": "Lies about plants",
        "parent": "X900",
        "category": "X",
        "keywords": ["plant", "vegetable", "giant crop"]
    },
    "X1500": {
        "label": "Lies about geography",
        "parent": "X900",
        "category": "X",
        "keywords": ["geography", "land", "impossible place"]
    },
    "X1700": {
        "label": "Lies: logical absurdities",
        "parent": "X900",
        "category": "X",
        "keywords": ["absurd", "impossible", "paradox", "contradiction"]
    },

    # === Z: MISCELLANEOUS ===
    "Z200": {
        "label": "Heroes",
        "parent": None,
        "category": "Z",
        "keywords": ["hero", "warrior", "champion", "mighty"]
    },
    "Z210": {
        "label": "Hero cycle",
        "parent": "Z200",
        "category": "Z",
        "keywords": ["hero journey", "departure", "initiation", "return", "call to adventure"]
    },
    "Z300": {
        "label": "Dying god",
        "parent": None,
        "category": "Z",
        "keywords": ["dying god", "death and resurrection", "seasonal death", "slain god", "reborn"]
    },
    "Z310": {
        "label": "Trickster figure",
        "parent": None,
        "category": "Z",
        "keywords": ["trickster", "clever", "cunning", "mischief", "shape-shifter", "boundary crosser"]
    },
    "Z0": {
        "label": "Formulas",
        "parent": None,
        "category": "Z",
        "keywords": ["formula", "pattern", "structure", "form"]
    },
    "Z10": {
        "label": "Beginning formulas",
        "parent": "Z0",
        "category": "Z",
        "keywords": ["once upon a time", "long ago", "in the beginning"]
    },
    "Z11": {
        "label": "Ending formulas",
        "parent": "Z0",
        "category": "Z",
        "keywords": ["they lived happily", "the end", "and so it was"]
    },
    "Z30": {
        "label": "Chains",
        "parent": "Z0",
        "category": "Z",
        "keywords": ["chain tale", "cumulative", "repeated pattern"]
    },
    "Z31": {
        "label": "Cumulative tales",
        "parent": "Z30",
        "category": "Z",
        "keywords": ["adds on", "builds up", "house that jack built"]
    },
    "Z40": {
        "label": "Symbolic numbers",
        "parent": "Z0",
        "category": "Z",
        "keywords": ["sacred number", "three", "seven", "twelve", "symbolic"]
    },
    "Z71": {
        "label": "Formulistic number: three",
        "parent": "Z40",
        "category": "Z",
        "keywords": ["three", "triad", "third time", "three wishes"]
    },
    "Z72": {
        "label": "Formulistic number: seven",
        "parent": "Z40",
        "category": "Z",
        "keywords": ["seven", "heptad", "seven days", "seven years"]
    },
    "Z100": {
        "label": "Symbolism",
        "parent": None,
        "category": "Z",
        "keywords": ["symbol", "metaphor", "allegory", "represents"]
    },
    "Z110": {
        "label": "Personification",
        "parent": "Z100",
        "category": "Z",
        "keywords": ["personified", "death as person", "time as figure"]
    },
    "Z111": {
        "label": "Death personified",
        "parent": "Z110",
        "category": "Z",
        "keywords": ["death figure", "grim reaper", "death comes"]
    },
    "Z120": {
        "label": "Colors as symbols",
        "parent": "Z100",
        "category": "Z",
        "keywords": ["red", "white", "black", "color symbolism"]
    },
    "Z130": {
        "label": "Animals as symbols",
        "parent": "Z100",
        "category": "Z",
        "keywords": ["symbolic animal", "lion courage", "fox cunning"]
    },
    "Z140": {
        "label": "Natural phenomena as symbols",
        "parent": "Z100",
        "category": "Z",
        "keywords": ["storm anger", "sun glory", "moon mystery"]
    },
    "Z150": {
        "label": "Time symbols",
        "parent": "Z100",
        "category": "Z",
        "keywords": ["dawn new beginning", "night death", "seasons cycle"]
    },
    "Z220": {
        "label": "Hero recognition signs",
        "parent": "Z200",
        "category": "Z",
        "keywords": ["birthmark", "token", "proof of identity", "recognized"]
    },
    "Z250": {
        "label": "Hero patterns",
        "parent": "Z200",
        "category": "Z",
        "keywords": ["hero birth", "hero childhood", "hero death", "pattern"]
    },
    "Z320": {
        "label": "Culture hero",
        "parent": None,
        "category": "Z",
        "keywords": ["culture hero", "brings fire", "teaches", "civilization bringer"]
    },
}


def build_index():
    """Build and save the motif index."""
    output_path = DATA_DIR / "thompson_motif_index.json"

    # Add metadata
    output = {
        "_metadata": {
            "description": "Thompson Motif-Index of Folk-Literature (selected entries)",
            "source": "Compiled from Stith Thompson (1955-58), public domain classification",
            "total_entries": len(MOTIF_INDEX),
            "categories": sorted(set(m["category"] for m in MOTIF_INDEX.values())),
        },
        "motifs": MOTIF_INDEX,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Summary
    cat_counts = {}
    for m in MOTIF_INDEX.values():
        cat = m["category"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    print(f"Thompson Motif Index built: {len(MOTIF_INDEX)} entries")
    print(f"Categories:")
    for cat, count in sorted(cat_counts.items()):
        print(f"  {cat}: {count} entries")
    print(f"\nOutput: {output_path}")


if __name__ == "__main__":
    build_index()
