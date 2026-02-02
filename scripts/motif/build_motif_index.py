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
