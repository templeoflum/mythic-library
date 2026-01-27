#!/usr/bin/env python3
"""Add new ACP archetypes for unmapped high-mention deities."""
import json
import sys
import io
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).parent.parent.parent


def add_indian_deities():
    """Add Agni, Soma, Varuna to IN_PANTHEON.jsonld."""
    path = PROJECT_ROOT / "ACP" / "archetypes" / "hindu" / "IN_PANTHEON.jsonld"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    existing_ids = {e["@id"] for e in data["entries"]}

    new_entries = [
        {
            "@id": "arch:IN-AGNI",
            "@type": "Archetype",
            "name": "Agni",
            "aliases": ["Vahni", "Anala", "Hutashana"],
            "epithets": ["Lord of Fire", "Mouth of the Gods", "Messenger", "Purifier"],
            "description": "The Vedic fire god and divine messenger between humans and gods. Every sacrificial offering passes through Agni. One of the most important Rigvedic deities, invoked in more hymns than any other god. Represents the transformative power of fire \u2014 digestion, cremation, sacrifice, and illumination.",
            "gender": "masculine",
            "domain": ["fire", "sacrifice", "purification", "messenger", "transformation"],
            "symbols": ["fire", "seven tongues of flame", "ram", "ghee ladle", "two faces"],
            "spectralCoordinates": {
                "order-chaos": 0.30,
                "creation-destruction": 0.55,
                "light-shadow": 0.15,
                "active-receptive": 0.10,
                "individual-collective": 0.65,
                "ascent-descent": 0.30,
                "stasis-transformation": 0.80,
                "voluntary-fated": 0.35
            },
            "instantiates": [
                {"primordial": "primordial:messenger", "weight": 0.90, "aspects": ["divine-intermediary", "sacrifice-carrier"]},
                {"primordial": "primordial:transformer", "weight": 0.85, "aspects": ["purifier", "alchemist-of-matter"]},
                {"primordial": "primordial:preserver", "weight": 0.50, "aspects": ["hearth-keeper", "domestic-fire"]}
            ],
            "temporalOrientation": "eternal",
            "shadowDynamics": {
                "activationConditions": ["When fire consumes without purpose", "When purification becomes destruction"],
                "shadowManifestations": ["All-consuming conflagration", "Insatiable appetite", "Wrath without discrimination"],
                "integrationPath": "Directed transformation; fire as servant of cosmic order"
            },
            "relationships": [
                {"type": "COMPLEMENT", "target": "arch:IN-INDRA", "dynamic": "Fire and storm \u2014 dual Vedic powers", "strength": 0.70},
                {"type": "COMPLEMENT", "target": "arch:IN-SOMA", "dynamic": "Fire and sacred drink \u2014 ritual pair", "strength": 0.80},
                {"type": "CULTURAL_ECHO", "target": "arch:GR-HEPHAESTUS", "fidelity": 0.50, "sharedAspects": ["fire", "craft", "transformation"]},
                {"type": "CULTURAL_ECHO", "target": "arch:GR-PROMETHEUS", "fidelity": 0.45, "sharedAspects": ["fire-bringer", "civilization-enabler"]}
            ],
            "correspondences": {
                "element": "EL-FIRE",
                "planet": "7P-MARS",
                "tarot": "TAMA-TOWER",
                "chakra": "CH-MANIPURA",
                "color": ["red", "orange", "gold"],
                "direction": "Southeast"
            },
            "metadata": {
                "canonicalSources": ["Rigveda (most hymns of any deity)", "Agni Purana", "Yajurveda"],
                "iconography": "Two-faced red god riding a ram, seven tongues of flame",
                "cultCenters": ["Every household hearth", "Every sacrificial altar"],
                "confidence": 0.9
            }
        },
        {
            "@id": "arch:IN-SOMA",
            "@type": "Archetype",
            "name": "Soma",
            "aliases": ["Chandra", "Indu", "Nishakar"],
            "epithets": ["Lord of Plants", "King Soma", "The Moon", "The Pressed One"],
            "description": "The Vedic deity of the sacred ritual drink and the moon. Soma is simultaneously a plant, a drink, a god, and the moon \u2014 a unique four-fold identity. The entire ninth mandala of the Rigveda is dedicated to Soma. Represents ecstasy, immortality, and the liminal state between mortal and divine.",
            "gender": "masculine",
            "domain": ["moon", "sacred drink", "ecstasy", "immortality", "plants", "healing"],
            "symbols": ["moon", "soma plant", "ritual vessel", "white horse", "nectar"],
            "spectralCoordinates": {
                "order-chaos": 0.40,
                "creation-destruction": 0.30,
                "light-shadow": 0.35,
                "active-receptive": 0.55,
                "individual-collective": 0.60,
                "ascent-descent": 0.25,
                "stasis-transformation": 0.65,
                "voluntary-fated": 0.30
            },
            "instantiates": [
                {"primordial": "primordial:healer", "weight": 0.80, "aspects": ["elixir-of-immortality", "plant-medicine"]},
                {"primordial": "primordial:mystic", "weight": 0.75, "aspects": ["ecstatic-vision", "divine-intoxication"]},
                {"primordial": "primordial:nurturer", "weight": 0.60, "aspects": ["moon-nourisher", "plant-lord"]}
            ],
            "temporalOrientation": "cyclical",
            "shadowDynamics": {
                "activationConditions": ["When ecstasy becomes addiction", "When the moon wanes"],
                "shadowManifestations": ["Intoxication without illumination", "Waning power", "Curse of Daksha"],
                "integrationPath": "Sacred use of altered states; cyclic renewal through waning and waxing"
            },
            "relationships": [
                {"type": "COMPLEMENT", "target": "arch:IN-AGNI", "dynamic": "Sacred drink offered through fire", "strength": 0.80},
                {"type": "COMPLEMENT", "target": "arch:IN-INDRA", "dynamic": "Soma empowers Indra for battle", "strength": 0.75},
                {"type": "CULTURAL_ECHO", "target": "arch:GR-DIONYSUS", "fidelity": 0.60, "sharedAspects": ["sacred-drink", "ecstasy", "divine-intoxication"]}
            ],
            "correspondences": {
                "element": "EL-WATER",
                "planet": "7P-MOON",
                "tarot": "TAMA-MOON",
                "chakra": "CH-AJNA",
                "color": ["white", "silver"],
                "direction": "North"
            },
            "metadata": {
                "canonicalSources": ["Rigveda Mandala IX (entire book)", "Atharvaveda"],
                "iconography": "White figure on chariot drawn by ten white horses, holding lotus",
                "cultCenters": ["Somnath (Gujarat)"],
                "confidence": 0.85
            }
        },
        {
            "@id": "arch:IN-VARUNA",
            "@type": "Archetype",
            "name": "Varuna",
            "aliases": ["Pracetas", "Jalapati"],
            "epithets": ["Lord of Waters", "Guardian of Cosmic Order", "King of the Gods (Vedic)", "The Binder"],
            "description": "The Vedic sovereign god of cosmic order (rta), waters, and the night sky. In the earliest Rigvedic hymns, Varuna is the supreme cosmic ruler who upholds rta (cosmic truth/order) \u2014 a moral, ethical deity who watches all deeds with a thousand eyes. Later diminished to lord of oceans. Cognate with Greek Ouranos and Zoroastrian Ahura Mazda.",
            "gender": "masculine",
            "domain": ["cosmic order (rta)", "waters", "night sky", "moral law", "oaths", "punishment"],
            "symbols": ["noose (pasha)", "water", "makara (sea creature)", "thousand eyes", "night sky"],
            "spectralCoordinates": {
                "order-chaos": 0.10,
                "creation-destruction": 0.40,
                "light-shadow": 0.50,
                "active-receptive": 0.45,
                "individual-collective": 0.75,
                "ascent-descent": 0.35,
                "stasis-transformation": 0.30,
                "voluntary-fated": 0.65
            },
            "instantiates": [
                {"primordial": "primordial:sovereign", "weight": 0.90, "aspects": ["cosmic-king", "law-upholder", "oath-binder"]},
                {"primordial": "primordial:judge", "weight": 0.80, "aspects": ["moral-watcher", "sin-punisher", "thousand-eyed"]},
                {"primordial": "primordial:preserver", "weight": 0.60, "aspects": ["rta-guardian", "cosmic-order-maintainer"]}
            ],
            "temporalOrientation": "eternal",
            "shadowDynamics": {
                "activationConditions": ["When law becomes tyranny", "When surveillance becomes paranoia"],
                "shadowManifestations": ["Merciless judge", "Binding without mercy", "Loss of sovereignty (displaced by Indra)"],
                "integrationPath": "Justice tempered by grace; cosmic order sustained through both law and compassion"
            },
            "relationships": [
                {"type": "CONSTELLATION", "targets": ["arch:IN-VARUNA", "arch:IN-INDRA"], "pattern": "Vedic sovereignty: cosmic law (Varuna) vs warrior power (Indra)"},
                {"type": "COMPLEMENT", "target": "arch:IN-AGNI", "dynamic": "Water and fire \u2014 cosmic balance", "strength": 0.65},
                {"type": "CULTURAL_ECHO", "target": "persian:ahura-mazda", "fidelity": 0.65, "sharedAspects": ["cosmic-order", "moral-law", "Indo-Iranian-cognate"]},
                {"type": "CULTURAL_ECHO", "target": "arch:GR-POSEIDON", "fidelity": 0.45, "sharedAspects": ["lord-of-waters", "later-demotion"]}
            ],
            "correspondences": {
                "element": "EL-WATER",
                "planet": "7P-NEPTUNE",
                "tarot": "TAMA-JUSTICE",
                "chakra": "CH-SVADHISTHANA",
                "color": ["blue", "dark blue"],
                "direction": "West"
            },
            "metadata": {
                "canonicalSources": ["Rigveda (especially Mandala VII)", "Atharvaveda", "Mahabharata"],
                "iconography": "Blue figure riding a makara, holding noose, beneath night sky",
                "cultCenters": ["Coastal temples (as ocean lord)"],
                "confidence": 0.85
            }
        }
    ]

    added = 0
    for entry in new_entries:
        if entry["@id"] not in existing_ids:
            data["entries"].append(entry)
            added += 1
            print(f"  Added {entry['@id']}: {entry['name']}")
        else:
            print(f"  Skipped {entry['@id']}: already exists")

    # Update metadata
    data["metadata"]["coverage"] = f"Major Hindu deities ({len(data['entries'])} figures)"
    candidates = data["metadata"].get("expansion_candidates", [])
    data["metadata"]["expansion_candidates"] = [c for c in candidates if c not in ("Agni", "Varuna")]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  Indian: {added} added, {len(data['entries'])} total")
    return added


def add_mesopotamian_deity():
    """Add Apsu to ME_PANTHEON.jsonld."""
    path = PROJECT_ROOT / "ACP" / "archetypes" / "mesopotamian" / "ME_PANTHEON.jsonld"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    existing_ids = {e["@id"] for e in data["entries"]}

    new_entry = {
        "@id": "arch:ME-APSU",
        "@type": "Archetype",
        "name": "Apsu",
        "aliases": ["Abzu", "Engur"],
        "epithets": ["The Deep", "Primordial Waters", "Father of the Gods"],
        "description": "The primordial freshwater abyss beneath the earth, personified as a deity. With Tiamat (salt water), Apsu represents the primordial couple whose mingling waters generated the first gods. Slain by Enki/Ea, whose temple was built upon Apsu's body \u2014 making the abzu the foundation of cosmic order.",
        "gender": "masculine",
        "domain": ["freshwater", "primordial depths", "underground waters", "creation"],
        "symbols": ["deep waters", "underground springs", "the abzu (sacred pool)"],
        "spectralCoordinates": {
            "order-chaos": 0.50,
            "creation-destruction": 0.25,
            "light-shadow": 0.70,
            "active-receptive": 0.65,
            "individual-collective": 0.80,
            "ascent-descent": 0.85,
            "stasis-transformation": 0.20,
            "voluntary-fated": 0.70
        },
        "instantiates": [
            {"primordial": "primordial:primeval-waters", "weight": 0.95, "aspects": ["primordial-source", "pre-creation-substance"]},
            {"primordial": "primordial:father", "weight": 0.70, "aspects": ["progenitor-of-gods", "sacrificed-parent"]}
        ],
        "temporalOrientation": "primordial",
        "shadowDynamics": {
            "activationConditions": ["When rest is disturbed by offspring", "When silence is broken"],
            "shadowManifestations": ["Desire to destroy creation (own children)", "Entropy-drive"],
            "integrationPath": "Sacrifice of the primordial for cosmic foundation"
        },
        "relationships": [
            {"type": "COMPLEMENT", "target": "arch:ME-TIAMAT", "dynamic": "Fresh and salt water; primordial couple", "strength": 0.95},
            {"type": "OPPOSITION", "target": "arch:ME-ENKI", "dynamic": "Slain by Ea/Enki; body becomes abzu-temple"},
            {"type": "CULTURAL_ECHO", "target": "arch:GR-OURANOS", "fidelity": 0.55, "sharedAspects": ["primordial-father", "overthrown-by-offspring"]},
            {"type": "CULTURAL_ECHO", "target": "arch:EG-NUN", "fidelity": 0.70, "sharedAspects": ["primordial-waters", "pre-creation-abyss"]}
        ],
        "correspondences": {
            "element": "EL-WATER",
            "color": ["dark blue", "black"],
            "direction": "Below"
        },
        "metadata": {
            "canonicalSources": ["Enuma Elish", "Sumerian cosmology"],
            "iconography": "Rarely depicted; represented by temple pools (abzu)",
            "confidence": 0.85
        }
    }

    if new_entry["@id"] not in existing_ids:
        data["entries"].append(new_entry)
        print(f"  Added {new_entry['@id']}: {new_entry['name']}")
    else:
        print(f"  Skipped {new_entry['@id']}: already exists")

    data["metadata"]["coverage"] = f"Major Mesopotamian deities ({len(data['entries'])} figures)"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  Mesopotamian: {len(data['entries'])} total")


def add_anansi():
    """Add Anansi to AF_ORISHA.jsonld (as a West African non-Yoruba entry)."""
    path = PROJECT_ROOT / "ACP" / "archetypes" / "african" / "AF_ORISHA.jsonld"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    existing_ids = {e["@id"] for e in data["entries"]}

    new_entry = {
        "@id": "arch:AF-ANANSI",
        "@type": "Archetype",
        "name": "Anansi",
        "aliases": ["Ananse", "Kwaku Ananse", "Mr. Spider", "Aunt Nancy (Caribbean)"],
        "epithets": ["The Spider", "Keeper of Stories", "The Trickster"],
        "description": "The Akan trickster spider-god who owns all stories. Anansi won the world's stories from Nyame (the sky god) by capturing the most dangerous creatures. Represents wit triumphing over strength, the power of storytelling, and subversive intelligence. Survived the Middle Passage to become central to Caribbean and African-American folklore.",
        "gender": "masculine",
        "domain": ["stories", "wisdom", "trickery", "cunning", "weaving"],
        "symbols": ["spider", "web", "story-pot", "drum"],
        "spectralCoordinates": {
            "order-chaos": 0.70,
            "creation-destruction": 0.45,
            "light-shadow": 0.50,
            "active-receptive": 0.15,
            "individual-collective": 0.30,
            "ascent-descent": 0.45,
            "stasis-transformation": 0.65,
            "voluntary-fated": 0.20
        },
        "instantiates": [
            {"primordial": "primordial:trickster", "weight": 0.95, "aspects": ["wit-over-strength", "rule-breaker", "culture-hero"]},
            {"primordial": "primordial:storyteller", "weight": 0.90, "aspects": ["keeper-of-all-stories", "narrative-weaver"]},
            {"primordial": "primordial:culture-hero", "weight": 0.60, "aspects": ["bringer-of-stories", "civilizer-through-cunning"]}
        ],
        "temporalOrientation": "eternal",
        "shadowDynamics": {
            "activationConditions": ["When cleverness becomes cruelty", "When trickery harms the innocent"],
            "shadowManifestations": ["Greed", "Selfishness", "Deceit without purpose"],
            "integrationPath": "Cunning in service of community; stories that teach through laughter"
        },
        "relationships": [
            {"type": "CULTURAL_ECHO", "target": "arch:AF-ESHU", "fidelity": 0.55, "sharedAspects": ["trickster", "crossroads-figure", "message-carrier"]},
            {"type": "CULTURAL_ECHO", "target": "arch:NO-LOKI", "fidelity": 0.50, "sharedAspects": ["trickster", "shape-shifter", "web-spinner"]},
            {"type": "CULTURAL_ECHO", "target": "arch:GR-HERMES", "fidelity": 0.45, "sharedAspects": ["trickster", "messenger", "cunning"]}
        ],
        "correspondences": {
            "element": "EL-AIR",
            "color": ["black", "red"],
            "direction": "Center (the web)"
        },
        "metadata": {
            "canonicalSources": ["Akan oral tradition", "Caribbean Anansi stories", "African-American folklore"],
            "iconography": "Spider or man-spider hybrid, sometimes with a hat",
            "culturalNote": "Akan tradition (Ghana/Ivory Coast), not Yoruba \u2014 included in African file for convenience",
            "confidence": 0.85
        }
    }

    if new_entry["@id"] not in existing_ids:
        data["entries"].append(new_entry)
        print(f"  Added {new_entry['@id']}: {new_entry['name']}")
    else:
        print(f"  Skipped {new_entry['@id']}: already exists")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  African: {len(data['entries'])} total")


if __name__ == "__main__":
    print("Adding new ACP archetypes...")
    print("\n--- Indian Deities ---")
    add_indian_deities()
    print("\n--- Mesopotamian Deity ---")
    add_mesopotamian_deity()
    print("\n--- African Deity ---")
    add_anansi()
    print("\nDone.")
