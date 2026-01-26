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
