#!/usr/bin/env python3
"""
add_shadow_evolution.py

Adds SHADOW and EVOLUTION relationships to ACP archetype .jsonld files
to expand thin relationship types for validation robustness.

Phase 12.4b: Targets 12-15 new SHADOW + 25-30 new EVOLUTION relationships.
"""

import json
from pathlib import Path
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# New relationships to add
# ---------------------------------------------------------------------------

# Format: (file_relative_path, archetype_id, relationship_dict)
NEW_RELATIONSHIPS = [
    # =====================================================================
    # SHADOW RELATIONSHIPS (15 new)
    # =====================================================================

    # --- Egyptian ---
    ("ACP/archetypes/egyptian/EG_NETJERU.jsonld", "arch:EG-RA", {
        "type": "SHADOW",
        "target": "primordial:tyrant",
        "activation": "When solar authority becomes scorching judgment; when aging sun-god fears usurpation",
        "strength": 0.6
    }),
    ("ACP/archetypes/egyptian/EG_NETJERU.jsonld", "arch:EG-SET", {
        "type": "SHADOW",
        "target": "primordial:destroyer",
        "activation": "When protective storm power becomes fratricidal chaos",
        "strength": 0.85
    }),
    ("ACP/archetypes/egyptian/EG_NETJERU.jsonld", "arch:EG-ISIS", {
        "type": "SHADOW",
        "target": "primordial:sorceress",
        "activation": "When magical cunning becomes manipulation; when maternal devotion becomes possessive control",
        "strength": 0.55
    }),

    # --- Norse ---
    ("ACP/archetypes/norse/NO_AESIR_VANIR.jsonld", "arch:NO-LOKI", {
        "type": "SHADOW",
        "target": "primordial:destroyer",
        "activation": "When trickster's playfulness curdles into malice; after Baldur's death",
        "strength": 0.9
    }),
    ("ACP/archetypes/norse/NO_AESIR_VANIR.jsonld", "arch:NO-THOR", {
        "type": "SHADOW",
        "target": "primordial:berserker",
        "activation": "When protective rage becomes indiscriminate violence; when strength substitutes for wisdom",
        "strength": 0.65
    }),

    # --- Hindu ---
    ("ACP/archetypes/hindu/IN_PANTHEON.jsonld", "arch:IN-SHIVA", {
        "type": "SHADOW",
        "target": "primordial:destroyer",
        "activation": "When ascetic detachment becomes world-annihilation; Tandava dance of dissolution",
        "strength": 0.8
    }),
    ("ACP/archetypes/hindu/IN_PANTHEON.jsonld", "arch:IN-INDRA", {
        "type": "SHADOW",
        "target": "primordial:tyrant",
        "activation": "When divine kingship becomes arrogant excess; fear of displacement by mortals",
        "strength": 0.75
    }),

    # --- Mesoamerican ---
    ("ACP/archetypes/mesoamerican/MA_PANTHEON.jsonld", "arch:MA-TEZCATLIPOCA", {
        "type": "SHADOW",
        "target": "primordial:deceiver",
        "activation": "When the Smoking Mirror reflects only destruction; when testing becomes torment",
        "strength": 0.85
    }),

    # --- Celtic ---
    ("ACP/archetypes/celtic/CE_PANTHEON.jsonld", "arch:CE-MORRIGAN", {
        "type": "SHADOW",
        "target": "primordial:devouring-mother",
        "activation": "When battle prophecy becomes war-lust; when sovereignty testing destroys the tested",
        "strength": 0.75
    }),
    ("ACP/archetypes/celtic/CE_PANTHEON.jsonld", "arch:CE-BALOR", {
        "type": "SHADOW",
        "target": "primordial:tyrant",
        "activation": "When the evil eye opens — consumptive authority that devours even its own people",
        "strength": 0.9
    }),

    # --- Slavic ---
    ("ACP/archetypes/slavic/SL_PANTHEON.jsonld", "arch:SL-VELES", {
        "type": "SHADOW",
        "target": "primordial:deceiver",
        "activation": "When underworld cunning becomes cattle-theft and oath-breaking; when chthonic wisdom becomes malice",
        "strength": 0.7
    }),

    # --- African ---
    ("ACP/archetypes/african/AF_ORISHA.jsonld", "arch:AF-ESHU", {
        "type": "SHADOW",
        "target": "primordial:deceiver",
        "activation": "When crossroads trickery becomes cosmic sabotage; when message-bearing becomes message-distortion",
        "strength": 0.65
    }),
    ("ACP/archetypes/african/AF_ORISHA.jsonld", "arch:AF-SHANGO", {
        "type": "SHADOW",
        "target": "primordial:tyrant",
        "activation": "When thunder justice becomes tyrannical wrath; when kingly power cannot accept challenge",
        "strength": 0.7
    }),

    # --- Native American ---
    ("ACP/archetypes/native_american/NA_PANTHEON.jsonld", "arch:NA-COYOTE", {
        "type": "SHADOW",
        "target": "primordial:deceiver",
        "activation": "When sacred foolishness becomes selfish cunning; when boundary-testing destroys taboos without renewal",
        "strength": 0.7
    }),

    # --- Polynesian ---
    ("ACP/archetypes/polynesian/PL_PANTHEON.jsonld", "arch:PL-TU", {
        "type": "SHADOW",
        "target": "primordial:berserker",
        "activation": "When war-god's protective function becomes bloodlust; when mana-seeking becomes cannibalistic rage",
        "strength": 0.8
    }),

    # =====================================================================
    # EVOLUTION RELATIONSHIPS (28 new)
    # =====================================================================

    # --- Egyptian ---
    ("ACP/archetypes/egyptian/EG_NETJERU.jsonld", "arch:EG-OSIRIS", {
        "type": "EVOLUTION",
        "source": "Living king of Egypt",
        "target": "Lord of the Duat (afterlife)",
        "trigger": "Death by Set's betrayal; dismemberment and resurrection by Isis",
        "direction": "forward"
    }),
    ("ACP/archetypes/egyptian/EG_NETJERU.jsonld", "arch:EG-HORUS", {
        "type": "EVOLUTION",
        "source": "Horus the Child (Harpocrates)",
        "target": "Horus the Elder (Haroeris) — avenger and king",
        "trigger": "Maturation through contendings with Set; proving worthiness to rule",
        "direction": "forward"
    }),
    ("ACP/archetypes/egyptian/EG_NETJERU.jsonld", "arch:EG-HATHOR", {
        "type": "EVOLUTION",
        "target": "arch:EG-SEKHMET",
        "trigger": "Ra's command to punish humanity; joy transforms to wrath",
        "direction": "forward"
    }),

    # --- Norse ---
    ("ACP/archetypes/norse/NO_AESIR_VANIR.jsonld", "arch:NO-ODIN", {
        "type": "EVOLUTION",
        "source": "Young war-god",
        "target": "All-Father and wisdom-seeker",
        "trigger": "Self-sacrifice on Yggdrasil; eye-sacrifice at Mímir's well",
        "direction": "forward"
    }),
    ("ACP/archetypes/norse/NO_AESIR_VANIR.jsonld", "arch:NO-LOKI", {
        "type": "EVOLUTION",
        "source": "Mischievous blood-brother of Odin",
        "target": "Bound world-ender leading Naglfar at Ragnarök",
        "trigger": "Causing Baldur's death; binding and punishment by the Aesir",
        "direction": "devolution"
    }),
    ("ACP/archetypes/norse/NO_AESIR_VANIR.jsonld", "arch:NO-BALDUR", {
        "type": "EVOLUTION",
        "source": "Shining god of beauty and peace",
        "target": "Returned ruler of the post-Ragnarök world",
        "trigger": "Death by mistletoe; passage through Hel; rebirth after world-renewal",
        "direction": "forward"
    }),

    # --- Hindu ---
    ("ACP/archetypes/hindu/IN_PANTHEON.jsonld", "arch:IN-VISHNU", {
        "type": "EVOLUTION",
        "source": "Cosmic preserver in celestial ocean",
        "target": "Sequential avatar incarnations (Matsya through Kalki)",
        "trigger": "Each avatar descends when dharma is threatened; progressive revelation of divine purpose",
        "direction": "forward"
    }),
    ("ACP/archetypes/hindu/IN_PANTHEON.jsonld", "arch:IN-PARVATI", {
        "type": "EVOLUTION",
        "source": "Sati (self-immolating devotee)",
        "target": "Parvati (patient ascetic who wins Shiva through tapas)",
        "trigger": "Reincarnation after Sati's death; transformation from passionate devotion to disciplined power",
        "direction": "forward"
    }),
    ("ACP/archetypes/hindu/IN_PANTHEON.jsonld", "arch:IN-RAMA", {
        "type": "EVOLUTION",
        "source": "Prince of Ayodhya",
        "target": "Maryada Purushottam (ideal man who embodies dharma)",
        "trigger": "Exile, Sita's abduction, war with Ravana; trials that forge ideal kingship",
        "direction": "forward"
    }),

    # --- Japanese ---
    ("ACP/archetypes/japanese/JP_KAMI.jsonld", "arch:JP-SUSANOO", {
        "type": "EVOLUTION",
        "source": "Weeping storm-god expelled from heaven",
        "target": "Culture-hero who slays Yamata-no-Orochi",
        "trigger": "Descent to Izumo; confrontation with the eight-headed serpent",
        "direction": "forward"
    }),
    ("ACP/archetypes/japanese/JP_KAMI.jsonld", "arch:JP-IZANAMI", {
        "type": "EVOLUTION",
        "source": "Creator goddess who shaped the islands",
        "target": "Queen of Yomi (land of the dead)",
        "trigger": "Death giving birth to fire-god Kagutsuchi; decay in the underworld",
        "direction": "devolution"
    }),
    ("ACP/archetypes/japanese/JP_KAMI.jsonld", "arch:JP-AMATERASU", {
        "type": "EVOLUTION",
        "source": "Hidden sun-goddess in the rock cave",
        "target": "Imperial ancestress restored to cosmic sovereignty",
        "trigger": "Lured from Ama-no-Iwato by the mirror and dance of Ame-no-Uzume",
        "direction": "forward"
    }),

    # --- Chinese ---
    ("ACP/archetypes/chinese/CN_PANTHEON.jsonld", "arch:CN-SUN-WUKONG", {
        "type": "EVOLUTION",
        "source": "Stone-born Monkey King (rebel against heaven)",
        "target": "Victorious Fighting Buddha",
        "trigger": "Journey to the West pilgrimage; 81 trials transform rebellion into discipline",
        "direction": "forward"
    }),
    ("ACP/archetypes/chinese/CN_PANTHEON.jsonld", "arch:CN-NEZHA", {
        "type": "EVOLUTION",
        "source": "Reckless child-warrior (kills Dragon King's son)",
        "target": "Lotus-reborn protector deity",
        "trigger": "Self-sacrifice to save parents; rebirth from lotus by Taiyi Zhenren",
        "direction": "forward"
    }),
    ("ACP/archetypes/chinese/CN_PANTHEON.jsonld", "arch:CN-NUWA", {
        "type": "EVOLUTION",
        "source": "Creator who shaped humans from yellow clay",
        "target": "World-repairer who mends the broken sky",
        "trigger": "Gonggong shatters the pillar of heaven; Nüwa smelts five-colored stones",
        "direction": "forward"
    }),

    # --- Mesoamerican ---
    ("ACP/archetypes/mesoamerican/MA_PANTHEON.jsonld", "arch:MA-QUETZALCOATL", {
        "type": "EVOLUTION",
        "source": "Creator deity and feathered serpent",
        "target": "Morning Star (Venus) after self-immolation",
        "trigger": "Tricked by Tezcatlipoca into drunkenness and shame; self-exile and self-sacrifice on funeral pyre",
        "direction": "forward"
    }),
    ("ACP/archetypes/mesoamerican/MA_PANTHEON.jsonld", "arch:MA-NANAHUATZIN", {
        "type": "EVOLUTION",
        "source": "Humble, pox-covered god",
        "target": "Tonatiuh — the Fifth Sun",
        "trigger": "Self-sacrifice by leaping into the divine bonfire at Teotihuacan",
        "direction": "forward"
    }),

    # --- Celtic ---
    ("ACP/archetypes/celtic/CE_PANTHEON.jsonld", "arch:CE-LUGH", {
        "type": "EVOLUTION",
        "source": "Young warrior seeking entry to Tara",
        "target": "Samildánach (master of all arts) and king",
        "trigger": "Proving mastery of every craft to gain admission; leading the Tuatha Dé Danann against the Fomorians",
        "direction": "forward"
    }),
    ("ACP/archetypes/celtic/CE_PANTHEON.jsonld", "arch:CE-BRIGID", {
        "type": "EVOLUTION",
        "source": "Triple goddess of poetry, smithcraft, and healing",
        "target": "Saint Brigid (Christian syncretism)",
        "trigger": "Cultural transformation from pagan goddess to Christian saint; Imbolc continuity",
        "direction": "forward"
    }),

    # --- Polynesian ---
    ("ACP/archetypes/polynesian/PL_PANTHEON.jsonld", "arch:PL-MAUI", {
        "type": "EVOLUTION",
        "source": "Abandoned child cast into sea-foam",
        "target": "Culture-hero who fishes up islands, snares the sun, steals fire",
        "trigger": "Successive trickster-hero feats; each quest expands from personal survival to collective benefit",
        "direction": "forward"
    }),
    ("ACP/archetypes/polynesian/PL_PANTHEON.jsonld", "arch:PL-HINE-NUI-TE-PO", {
        "type": "EVOLUTION",
        "source": "Hine-tītama (Dawn Maiden, daughter-wife of Tāne)",
        "target": "Hine-nui-te-pō (Great Woman of Night, guardian of the dead)",
        "trigger": "Discovery of incest with father Tāne; flight to the underworld in shame and rage",
        "direction": "forward"
    }),

    # --- African ---
    ("ACP/archetypes/african/AF_ORISHA.jsonld", "arch:AF-OBATALA", {
        "type": "EVOLUTION",
        "source": "Olodumare's delegate creating the earth",
        "target": "Patient king who accepts wrongful imprisonment without complaint",
        "trigger": "Falsely imprisoned in Ile-Ife; demonstrates divine patience that becomes his defining quality",
        "direction": "forward"
    }),
    ("ACP/archetypes/african/AF_ORISHA.jsonld", "arch:AF-SHANGO", {
        "type": "EVOLUTION",
        "source": "Fourth Alafin of Oyo (mortal king)",
        "target": "Orisha of thunder and lightning",
        "trigger": "Death (or ascension) — rope-hanging transforms mortal king into divine force",
        "direction": "forward"
    }),

    # --- Native American ---
    ("ACP/archetypes/native_american/NA_PANTHEON.jsonld", "arch:NA-RAVEN", {
        "type": "EVOLUTION",
        "source": "Primordial darkness-dweller",
        "target": "Light-bringer and culture-hero",
        "trigger": "Stealing the sun/moon/stars from the old chief's box; trickery becomes world-gift",
        "direction": "forward"
    }),
    ("ACP/archetypes/native_american/NA_PANTHEON.jsonld", "arch:NA-COYOTE", {
        "type": "EVOLUTION",
        "source": "Chaotic trickster and boundary-breaker",
        "target": "Culture-hero who brings fire and names the stars",
        "trigger": "Progression from selfish mischief to gifts that shape the world for humans",
        "direction": "forward"
    }),

    # --- Slavic ---
    ("ACP/archetypes/slavic/SL_PANTHEON.jsonld", "arch:SL-MARZANNA", {
        "type": "EVOLUTION",
        "source": "Winter-death goddess",
        "target": "Spring renewal (through ritual drowning/burning of effigy)",
        "trigger": "Annual cycle: death of the straw figure releases winter's grip, enabling Vesna's return",
        "direction": "forward"
    }),

    # --- Finnish ---
    ("ACP/archetypes/finnish/FI_PANTHEON.jsonld", "arch:FI-VÄINÄMÖINEN", {
        "type": "EVOLUTION",
        "source": "Ancient sage-singer born from Ilmatar",
        "target": "Eternal wanderer who departs Finland, leaving the kantele",
        "trigger": "Birth of Marjatta's son displaces the old order; Väinämöinen sails away in a copper boat",
        "direction": "forward"
    }),

    # --- Mesopotamian ---
    ("ACP/archetypes/mesopotamian/ME_PANTHEON.jsonld", "arch:ME-INANNA", {
        "type": "EVOLUTION",
        "source": "Queen of Heaven seeking underworld power",
        "target": "Returned goddess carrying death-knowledge",
        "trigger": "Descent through seven gates; death on the hook; resurrection by Enki's creatures",
        "direction": "forward"
    }),
    ("ACP/archetypes/mesopotamian/ME_PANTHEON.jsonld", "arch:ME-GILGAMESH", {
        "type": "EVOLUTION",
        "source": "Tyrannical king of Uruk (two-thirds divine)",
        "target": "Wisdom-bearing mortal who accepts death",
        "trigger": "Enkidu's death; failed quest for immortality; return to Uruk's walls as legacy",
        "direction": "forward"
    }),
]


def find_project_root():
    script_dir = Path(__file__).resolve().parent
    candidate = script_dir.parent
    if (candidate / "ACP").is_dir():
        return candidate
    cwd = Path.cwd()
    if (cwd / "ACP").is_dir():
        return cwd
    raise FileNotFoundError("Cannot find project root")


def main():
    root = find_project_root()
    print("=" * 70)
    print("  SHADOW / EVOLUTION RELATIONSHIP EXPANSION")
    print("=" * 70)
    print(f"\nProject root: {root}")

    # Group by file
    by_file = {}
    for rel_path, arch_id, rel_obj in NEW_RELATIONSHIPS:
        key = root / rel_path
        if key not in by_file:
            by_file[key] = []
        by_file[key].append((arch_id, rel_obj))

    shadow_count = sum(1 for _, _, r in NEW_RELATIONSHIPS if r["type"] == "SHADOW")
    evo_count = sum(1 for _, _, r in NEW_RELATIONSHIPS if r["type"] == "EVOLUTION")
    print(f"\nRelationships to add: {shadow_count} SHADOW + {evo_count} EVOLUTION = {len(NEW_RELATIONSHIPS)} total")
    print(f"Files to modify: {len(by_file)}")

    added = 0
    skipped_missing_entry = 0
    skipped_duplicate = 0
    modified_files = set()

    for fpath, entries in sorted(by_file.items()):
        print(f"\n--- {fpath.relative_to(root)} ---")

        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Build lookup of entries by @id
        entry_list = data.get("entries", [])
        entry_map = {e.get("@id"): e for e in entry_list}

        for arch_id, rel_obj in entries:
            if arch_id not in entry_map:
                print(f"  [SKIP] {arch_id} not found in file")
                skipped_missing_entry += 1
                continue

            entry = entry_map[arch_id]
            rels = entry.setdefault("relationships", [])

            # Check for duplicate (same type + target)
            rel_target = rel_obj.get("target", "")
            rel_type = rel_obj["type"]
            is_dup = any(
                r.get("type") == rel_type and r.get("target") == rel_target
                for r in rels
            )
            if is_dup:
                print(f"  [DUP]  {arch_id} already has {rel_type} -> {rel_target}")
                skipped_duplicate += 1
                continue

            rels.append(rel_obj)
            added += 1
            modified_files.add(fpath)
            name = entry.get("name", arch_id)
            print(f"  [ADD]  {name}: {rel_type} -> {rel_target}")

        # Write back
        if fpath in modified_files:
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")

    print(f"\n{'=' * 70}")
    print("  SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Total relationships specified : {len(NEW_RELATIONSHIPS)}")
    print(f"  Added                         : {added}")
    print(f"  Skipped (entry not found)     : {skipped_missing_entry}")
    print(f"  Skipped (duplicate)           : {skipped_duplicate}")
    print(f"  Files modified                : {len(modified_files)}")
    print()


if __name__ == "__main__":
    main()
