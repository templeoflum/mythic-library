#!/usr/bin/env python3
"""
Phase 2 Enrichment: Cultural Echoes, Aliases, and Bidirectional Relationships

This script:
1. Generates culturalEchoes from correspondences.jsonld mappings
2. Finds similar archetypes across systems using spectral distance
3. Adds aliases for cross-cultural recognition
4. Fixes missing bidirectional relationships
5. Adds missing instantiates for orphan archetypes
"""

import json
import sys
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Known cross-pantheon equivalents (sky father gods, etc.)
# Format: { archetype_id: [(equivalent_id, fidelity, shared_aspects), ...] }
KNOWN_EQUIVALENTS = {
    # Sky Father / Thunder Gods
    "arch:GR-ZEUS": [
        ("arch:RO-JUPITER", 0.95, ["sky", "thunder", "sovereignty", "king-of-gods"]),
        ("arch:NO-THOR", 0.70, ["thunder", "storm", "strength"]),
        ("arch:IN-INDRA", 0.75, ["thunder", "storm", "king-of-gods", "warrior"]),
        ("arch:SL-PERUN", 0.80, ["thunder", "storm", "sky"]),
        ("arch:CN-LEI-GONG", 0.65, ["thunder", "storm"]),
    ],
    "arch:NO-ODIN": [
        ("arch:GR-ZEUS", 0.60, ["sky-father", "sovereignty"]),
        ("arch:RO-JUPITER", 0.55, ["sky-father", "king-of-gods"]),
        ("arch:CE-DAGDA", 0.70, ["father-god", "wisdom", "magic"]),
    ],
    # Love/Beauty Goddesses
    "arch:GR-APHRODITE": [
        ("arch:RO-VENUS", 0.95, ["love", "beauty", "desire"]),
        ("arch:NO-FREYA", 0.75, ["love", "beauty", "fertility"]),
        ("arch:ME-ISHTAR", 0.80, ["love", "war", "fertility"]),
        ("arch:EG-HATHOR", 0.70, ["love", "beauty", "music"]),
        ("arch:IN-LAKSHMI", 0.65, ["beauty", "fortune", "prosperity"]),
    ],
    # War Gods
    "arch:GR-ARES": [
        ("arch:RO-MARS", 0.95, ["war", "violence", "battle"]),
        ("arch:NO-TYR", 0.70, ["war", "courage", "battle"]),
        ("arch:CE-MORRIGAN", 0.60, ["war", "battle", "death"]),
        ("arch:EG-SEKHMET", 0.65, ["war", "destruction", "fierce"]),
    ],
    # Wisdom/Craft Goddesses
    "arch:GR-ATHENA": [
        ("arch:RO-MINERVA", 0.95, ["wisdom", "crafts", "strategy"]),
        ("arch:EG-NEITH", 0.70, ["war", "weaving", "wisdom"]),
        ("arch:CE-BRIGID", 0.65, ["crafts", "wisdom", "fire"]),
    ],
    # Underworld/Death Gods
    "arch:GR-HADES": [
        ("arch:RO-PLUTO", 0.95, ["underworld", "death", "wealth"]),
        ("arch:EG-OSIRIS", 0.75, ["underworld", "death", "rebirth"]),
        ("arch:NO-HEL", 0.70, ["underworld", "death"]),
        ("arch:ME-ERESHKIGAL", 0.80, ["underworld", "death"]),
    ],
    # Sun Gods
    "arch:GR-APOLLO": [
        ("arch:RO-APOLLO", 0.98, ["sun", "music", "prophecy", "healing"]),
        ("arch:EG-RA", 0.75, ["sun", "light", "kingship"]),
        ("arch:IN-SURYA", 0.80, ["sun", "light"]),
        ("arch:JP-AMATERASU", 0.70, ["sun", "light", "sovereignty"]),
    ],
    # Sea Gods
    "arch:GR-POSEIDON": [
        ("arch:RO-NEPTUNE", 0.95, ["sea", "storms", "horses"]),
        ("arch:NO-AEGIR", 0.70, ["sea", "ocean"]),
        ("arch:JP-RYUJIN", 0.65, ["sea", "dragons", "water"]),
    ],
    # Messenger/Trickster Gods
    "arch:GR-HERMES": [
        ("arch:RO-MERCURY", 0.95, ["messenger", "commerce", "travel", "trickster"]),
        ("arch:NO-LOKI", 0.60, ["trickster", "shapeshifter"]),
        ("arch:EG-THOTH", 0.70, ["messenger", "wisdom", "magic"]),
        ("arch:AF-ESHU", 0.75, ["messenger", "trickster", "crossroads"]),
    ],
    # Fertility/Earth Goddesses
    "arch:GR-DEMETER": [
        ("arch:RO-CERES", 0.95, ["harvest", "fertility", "agriculture"]),
        ("arch:NO-FREYA", 0.65, ["fertility", "abundance"]),
        ("arch:EG-ISIS", 0.70, ["mother", "magic", "fertility"]),
        ("arch:IN-PARVATI", 0.60, ["mother", "fertility"]),
    ],
    # Smith/Craft Gods
    "arch:GR-HEPHAESTUS": [
        ("arch:RO-VULCAN", 0.95, ["forge", "fire", "crafts"]),
        ("arch:NO-BROKKR", 0.70, ["smithing", "crafts"]),
        ("arch:CE-GOIBNIU", 0.80, ["smithing", "crafts"]),
        ("arch:AF-OGUN", 0.75, ["iron", "war", "crafts"]),
    ],
    # Wine/Ecstasy Gods
    "arch:GR-DIONYSUS": [
        ("arch:RO-BACCHUS", 0.95, ["wine", "ecstasy", "theater"]),
        ("arch:IN-SOMA", 0.65, ["intoxication", "ecstasy"]),
    ],
    # Hunt Goddesses
    "arch:GR-ARTEMIS": [
        ("arch:RO-DIANA", 0.95, ["hunt", "moon", "wilderness"]),
        ("arch:CE-FLIDAIS", 0.70, ["hunt", "forests", "wild-animals"]),
    ],
    # Hearth Goddesses
    "arch:GR-HESTIA": [
        ("arch:RO-VESTA", 0.95, ["hearth", "home", "sacred-flame"]),
    ],
    # Trickster figures across cultures
    "arch:AF-ANANSI": [
        ("arch:NA-COYOTE", 0.75, ["trickster", "storyteller", "cunning"]),
        ("arch:NO-LOKI", 0.65, ["trickster", "shapeshifter"]),
    ],
    "arch:NA-COYOTE": [
        ("arch:AF-ANANSI", 0.75, ["trickster", "storyteller"]),
        ("arch:PL-MAUI", 0.70, ["trickster", "culture-hero"]),
    ],
}

# Common aliases for major deities
KNOWN_ALIASES = {
    # Greek
    "arch:GR-ZEUS": ["Jupiter (Roman)", "Jove", "Zeus Pater", "Dias (Modern Greek)"],
    "arch:GR-HERA": ["Juno (Roman)", "Queen of Heaven"],
    "arch:GR-ATHENA": ["Minerva (Roman)", "Pallas Athena", "Athene"],
    "arch:GR-APHRODITE": ["Venus (Roman)", "Cyprian", "Cytherea"],
    "arch:GR-APOLLO": ["Phoebus", "Phoebus Apollo"],
    "arch:GR-ARTEMIS": ["Diana (Roman)", "Phoebe", "Cynthia"],
    "arch:GR-ARES": ["Mars (Roman)", "Enyalios"],
    "arch:GR-HERMES": ["Mercury (Roman)", "Psychopompos"],
    "arch:GR-POSEIDON": ["Neptune (Roman)", "Earth-Shaker"],
    "arch:GR-HADES": ["Pluto (Roman)", "Plouton", "Aidoneus", "The Unseen One"],
    "arch:GR-DEMETER": ["Ceres (Roman)", "Grain Mother"],
    "arch:GR-HEPHAESTUS": ["Vulcan (Roman)", "The Lame God"],
    "arch:GR-DIONYSUS": ["Bacchus (Roman)", "Bromios", "Twice-Born"],
    "arch:GR-HESTIA": ["Vesta (Roman)"],
    # Norse
    "arch:NO-ODIN": ["Wotan (Germanic)", "Woden (Anglo-Saxon)", "Allfather"],
    "arch:NO-THOR": ["Donar (Germanic)", "Thunor (Anglo-Saxon)", "Thunderer"],
    "arch:NO-FREYA": ["Freyja", "Vanadis", "Lady of the Vanir"],
    "arch:NO-LOKI": ["Lopt", "The Trickster", "Sky-Treader"],
    "arch:NO-TYR": ["Tiw (Anglo-Saxon)", "Ziu (Germanic)"],
    # Egyptian
    "arch:EG-RA": ["Re", "Atum-Ra", "Ra-Horakhty"],
    "arch:EG-ISIS": ["Aset", "Great of Magic"],
    "arch:EG-OSIRIS": ["Usir", "Lord of the Underworld"],
    "arch:EG-HORUS": ["Heru", "The Distant One"],
    "arch:EG-THOTH": ["Djehuty", "Hermes Trismegistus (syncretic)"],
    "arch:EG-ANUBIS": ["Anpu", "Lord of the Sacred Land"],
    "arch:EG-SEKHMET": ["The Powerful One", "Eye of Ra"],
    "arch:EG-HATHOR": ["Het-Heru", "Lady of the West"],
    # Hindu
    "arch:IN-VISHNU": ["The Preserver", "Narayana", "Hari"],
    "arch:IN-SHIVA": ["Mahadeva", "Nataraja", "The Destroyer"],
    "arch:IN-BRAHMA": ["The Creator", "Prajapati"],
    "arch:IN-LAKSHMI": ["Shri", "Goddess of Fortune"],
    "arch:IN-SARASWATI": ["Goddess of Learning", "Vani"],
    "arch:IN-GANESHA": ["Ganapati", "Vinayaka", "Elephant-Headed God"],
    "arch:IN-INDRA": ["King of the Devas", "Lord of Heaven"],
    # Celtic
    "arch:CE-DAGDA": ["The Good God", "Eochaid Ollathair"],
    "arch:CE-BRIGID": ["Brighid", "Bride", "Saint Brigid (Christian sync)"],
    "arch:CE-MORRIGAN": ["Phantom Queen", "The Great Queen"],
    "arch:CE-CERNUNNOS": ["The Horned One", "Lord of Wild Things"],
    # Japanese
    "arch:JP-AMATERASU": ["Amaterasu-Omikami", "Great Divinity Illuminating Heaven"],
    "arch:JP-SUSANOO": ["Susano-o", "The Impetuous Male"],
    "arch:JP-TSUKUYOMI": ["Moon Reader", "Moon God"],
    # African/Yoruba
    "arch:AF-SHANGO": ["Xangô (Candomblé)", "Changó (Santería)", "Saint Barbara (sync)"],
    "arch:AF-ESHU": ["Elegua (Santería)", "Exu (Candomblé)", "Papa Legba (Vodou)"],
    "arch:AF-YEMOJA": ["Yemanjá (Candomblé)", "Yemayá (Santería)", "Our Lady of Regla (sync)"],
    "arch:AF-OSHUN": ["Oxum (Candomblé)", "Ochún (Santería)", "Our Lady of Charity (sync)"],
    "arch:AF-OGUN": ["Ogum (Candomblé)", "Ogún (Santería)", "Saint George (sync)"],
    # Mesopotamian
    "arch:ME-ISHTAR": ["Inanna (Sumerian)", "Astarte (Canaanite)", "Queen of Heaven"],
    "arch:ME-MARDUK": ["Bel", "Lord of Babylon"],
    "arch:ME-ENKI": ["Ea", "Lord of the Abzu"],
    "arch:ME-ERESHKIGAL": ["Queen of the Great Below"],
    # Slavic
    "arch:SL-PERUN": ["Perkūnas (Baltic)", "Thunderer"],
    "arch:SL-VELES": ["Volos", "Lord of the Underworld"],
    # Mesoamerican
    "arch:MA-QUETZALCOATL": ["Kukulkan (Maya)", "Feathered Serpent"],
    "arch:MA-TEZCATLIPOCA": ["Smoking Mirror", "Lord of the Night"],
}

# Default primordial mappings for archetypes missing instantiates
DEFAULT_PRIMORDIALS = {
    # By system prefix patterns
    "GR-": [("primordial:hero", 0.5)],  # Default Greek to hero
    "NO-": [("primordial:warrior", 0.5)],  # Default Norse to warrior
    "EG-": [("primordial:preserver", 0.5)],
    # Specific fixes
    "arch:GR-APHRODITE-URANIA": [("primordial:lover", 0.85), ("primordial:great-mother", 0.4)],
    "arch:GR-APHRODITE-PANDEMOS": [("primordial:lover", 0.90), ("primordial:great-mother", 0.5)],
}


@dataclass
class Archetype:
    """Represents a loaded archetype."""
    id: str
    name: str
    system: str
    file_path: Path
    data: dict
    spectral: Dict[str, float] = field(default_factory=dict)
    instantiates: List[dict] = field(default_factory=list)
    relationships: List[dict] = field(default_factory=list)
    cultural_echoes: List[dict] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)


class Phase2Enricher:
    """Phase 2 enrichment engine."""

    def __init__(self, acp_path: Path):
        self.acp_path = acp_path
        self.archetypes: Dict[str, Archetype] = {}
        self.correspondences: dict = {}
        self.changes: Dict[str, List[str]] = defaultdict(list)

    def load_all(self):
        """Load all archetypes and correspondences."""
        print("Loading archetypes...")
        self._load_archetypes()
        print(f"  Loaded {len(self.archetypes)} archetypes")

        print("Loading correspondences...")
        self._load_correspondences()

    def _load_archetypes(self):
        """Load all archetype files."""
        patterns = [
            "archetypes/**/*.jsonld",
            "divination/**/*.jsonld",
            "psychology/**/*.jsonld",
            "modern/**/*.jsonld",
        ]

        for pattern in patterns:
            for file_path in self.acp_path.glob(pattern):
                self._load_file(file_path)

    def _load_file(self, file_path: Path):
        """Load archetypes from a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"  Error loading {file_path}: {e}")
            return

        # Handle different structures
        entries = []
        if "entries" in data:
            entries = data["entries"]
        elif "@graph" in data:
            entries = data["@graph"]
        elif "archetypes" in data:
            entries = data["archetypes"]
        elif "suits" in data:  # Tarot minor arcana
            for suit in data.get("suits", []):
                entries.extend(suit.get("cards", []))
        elif "members" in data:
            entries = data["members"]
        elif "hexagrams" in data:
            entries = data["hexagrams"]
        elif "@id" in data and "name" in data:
            entries = [data]

        for entry in entries:
            if not isinstance(entry, dict):
                continue
            arch_id = entry.get("@id", "")
            if not arch_id or arch_id.startswith("acp:") or arch_id.startswith("skos:"):
                continue
            # Skip system metadata entries
            if arch_id.startswith("system:"):
                continue

            # Determine system from ID or file path
            system = self._extract_system(arch_id, file_path)

            arch = Archetype(
                id=arch_id,
                name=entry.get("name", ""),
                system=system,
                file_path=file_path,
                data=entry,
                spectral=entry.get("spectralCoordinates", {}),
                instantiates=entry.get("instantiates", []),
                relationships=entry.get("relationships", []),
                cultural_echoes=entry.get("culturalEchoes", []),
                aliases=entry.get("aliases", []),
            )
            self.archetypes[arch_id] = arch

    def _extract_system(self, arch_id: str, file_path: Path) -> str:
        """Extract system identifier from archetype ID or file path."""
        # Try from ID prefix
        if ":" in arch_id:
            prefix = arch_id.split(":")[0]
            if prefix in ["arch", "tarot", "iching", "rune", "chakra", "element",
                         "planet", "zodiac", "house", "sephirah", "hex", "trigram"]:
                # Extract from ID after prefix
                parts = arch_id.split(":")[-1].split("-")
                if len(parts) > 1:
                    return parts[0].lower()

        # From file path
        parts = file_path.parts
        for i, part in enumerate(parts):
            if part in ["archetypes", "divination", "psychology", "modern"]:
                if i + 1 < len(parts):
                    return parts[i + 1].lower()
        return "unknown"

    def _load_correspondences(self):
        """Load correspondences.jsonld."""
        corr_path = self.acp_path / "schema" / "correspondences.jsonld"
        if corr_path.exists():
            with open(corr_path, 'r', encoding='utf-8') as f:
                self.correspondences = json.load(f)
            print(f"  Loaded correspondences")

    def spectral_distance(self, a: Archetype, b: Archetype) -> float:
        """Calculate Euclidean distance between two archetypes' spectral coordinates."""
        if not a.spectral or not b.spectral:
            return 1.0

        axes = ["order-chaos", "creation-destruction", "light-shadow",
                "active-receptive", "individual-collective", "ascent-descent",
                "stasis-transformation", "voluntary-fated"]

        sum_sq = 0.0
        count = 0
        for axis in axes:
            if axis in a.spectral and axis in b.spectral:
                diff = a.spectral[axis] - b.spectral[axis]
                sum_sq += diff * diff
                count += 1

        if count == 0:
            return 1.0
        return math.sqrt(sum_sq / count)

    def enrich_cultural_echoes(self):
        """Add culturalEchoes from known equivalents and correspondences."""
        print("\nEnriching cultural echoes...")

        added = 0

        # First, add from KNOWN_EQUIVALENTS
        for arch_id, equivalents in KNOWN_EQUIVALENTS.items():
            if arch_id not in self.archetypes:
                continue
            arch = self.archetypes[arch_id]

            existing_targets = {e.get("target") for e in arch.cultural_echoes}

            for equiv_id, fidelity, shared in equivalents:
                if equiv_id in existing_targets:
                    continue
                if equiv_id not in self.archetypes:
                    continue

                # Add to this archetype
                arch.cultural_echoes.append({
                    "target": equiv_id,
                    "fidelity": fidelity,
                    "sharedAspects": shared,
                    "provenance": "SCHOL"
                })
                added += 1
                self.changes[arch_id].append(f"Added culturalEcho to {equiv_id}")

                # Add reverse link
                other = self.archetypes[equiv_id]
                other_existing = {e.get("target") for e in other.cultural_echoes}
                if arch_id not in other_existing:
                    other.cultural_echoes.append({
                        "target": arch_id,
                        "fidelity": fidelity,
                        "sharedAspects": shared,
                        "provenance": "SCHOL"
                    })
                    added += 1
                    self.changes[equiv_id].append(f"Added culturalEcho to {arch_id}")

        # Second, add from correspondences.jsonld greekEchoes
        if "@graph" in self.correspondences:
            for collection in self.correspondences["@graph"]:
                if "members" not in collection:
                    continue
                for member in collection["members"]:
                    greek_echoes = member.get("greekEchoes", [])
                    tarot_id = member.get("@id", "")
                    if not tarot_id or not greek_echoes:
                        continue

                    # Build full tarot ID
                    full_tarot_id = f"tarot:{tarot_id}"
                    if full_tarot_id not in self.archetypes:
                        continue

                    tarot_arch = self.archetypes[full_tarot_id]
                    existing = {e.get("target") for e in tarot_arch.cultural_echoes}

                    for greek_id in greek_echoes:
                        if greek_id in existing:
                            continue
                        if greek_id not in self.archetypes:
                            continue

                        # Add tarot -> greek link
                        tarot_arch.cultural_echoes.append({
                            "target": greek_id,
                            "fidelity": 0.65,
                            "sharedAspects": ["archetypal function"],
                            "provenance": "TRAD"
                        })
                        added += 1
                        self.changes[full_tarot_id].append(f"Added culturalEcho to {greek_id}")

                        # Add greek -> tarot reverse link
                        greek_arch = self.archetypes[greek_id]
                        greek_existing = {e.get("target") for e in greek_arch.cultural_echoes}
                        if full_tarot_id not in greek_existing:
                            greek_arch.cultural_echoes.append({
                                "target": full_tarot_id,
                                "fidelity": 0.65,
                                "sharedAspects": ["archetypal function"],
                                "provenance": "TRAD"
                            })
                            added += 1
                            self.changes[greek_id].append(f"Added culturalEcho to {full_tarot_id}")

        print(f"  Added {added} cultural echoes")
        return added

    def enrich_spectral_echoes(self, max_distance: float = 0.12, max_per_arch: int = 2):
        """Find similar archetypes across different systems using spectral distance."""
        print(f"\nFinding spectral echoes (distance < {max_distance})...")

        added = 0
        arch_list = list(self.archetypes.values())

        for i, arch in enumerate(arch_list):
            if not arch.spectral:
                continue

            existing_targets = {e.get("target") for e in arch.cultural_echoes}
            candidates = []

            for other in arch_list:
                if other.id == arch.id:
                    continue
                if other.id in existing_targets:
                    continue
                # Only cross-system echoes
                if other.system == arch.system:
                    continue
                if not other.spectral:
                    continue

                dist = self.spectral_distance(arch, other)
                if dist < max_distance:
                    candidates.append((other, dist))

            # Sort by distance and take top N
            candidates.sort(key=lambda x: x[1])

            for other, dist in candidates[:max_per_arch]:
                fidelity = round(1.0 - dist, 2)
                arch.cultural_echoes.append({
                    "target": other.id,
                    "fidelity": fidelity,
                    "sharedAspects": ["spectral proximity"],
                    "provenance": "ORIG"
                })
                added += 1
                self.changes[arch.id].append(f"Added spectral echo to {other.id} (dist={dist:.3f})")

        print(f"  Added {added} spectral echoes")
        return added

    def enrich_aliases(self):
        """Add aliases from known alias mappings."""
        print("\nEnriching aliases...")

        added = 0

        for arch_id, aliases in KNOWN_ALIASES.items():
            if arch_id not in self.archetypes:
                continue
            arch = self.archetypes[arch_id]

            # Handle aliases that might be dicts or other types
            existing_aliases = []
            for a in arch.aliases:
                if isinstance(a, str):
                    existing_aliases.append(a)
                elif isinstance(a, dict):
                    existing_aliases.append(a.get("name", str(a)))
                else:
                    existing_aliases.append(str(a))

            existing = set(existing_aliases)
            new_count = 0
            for alias in aliases:
                if alias not in existing:
                    arch.aliases.append(alias)
                    new_count += 1
                    added += 1

            if new_count > 0:
                self.changes[arch_id].append(f"Added {new_count} aliases")

        print(f"  Added {added} aliases")
        return added

    def fix_bidirectional_relationships(self):
        """Ensure all relationships have reverse links."""
        print("\nFixing bidirectional relationships...")

        # Relationship types that should be bidirectional
        BIDIRECTIONAL = {
            "POLAR_OPPOSITE": "POLAR_OPPOSITE",
            "COMPLEMENT": "COMPLEMENT",
            "CULTURAL_ECHO": "CULTURAL_ECHO",
            "MIRRORS": "MIRRORS",
            "TENSION": "TENSION",
            "SHADOW": "SHADOW",
        }

        # One-directional pairs
        DIRECTED = {
            "EVOLUTION": "DEVOLUTION",
            "DEVOLUTION": "EVOLUTION",
            "CONTAINS": "CONTAINED_BY",
            "CONTAINED_BY": "CONTAINS",
        }

        added = 0

        for arch_id, arch in self.archetypes.items():
            for rel in arch.relationships:
                rel_type = rel.get("type", "")
                target = rel.get("target", "")

                # Handle list targets
                if isinstance(target, list):
                    targets = [t for t in target if isinstance(t, str)]
                elif isinstance(target, str):
                    targets = [target] if target else []
                else:
                    continue

                for target in targets:
                    if not target or target not in self.archetypes:
                        continue

                    target_arch = self.archetypes[target]
                    target_rels = target_arch.relationships

                    # Determine reverse type
                    if rel_type in BIDIRECTIONAL:
                        reverse_type = BIDIRECTIONAL[rel_type]
                    elif rel_type in DIRECTED:
                        reverse_type = DIRECTED[rel_type]
                    else:
                        continue

                    # Check if reverse exists
                    has_reverse = any(
                        r.get("type") == reverse_type and (
                            r.get("target") == arch_id or
                            (isinstance(r.get("target"), list) and arch_id in r.get("target"))
                        )
                        for r in target_rels
                    )

                    if not has_reverse:
                        # Create reverse relationship
                        reverse_rel = {
                            "type": reverse_type,
                            "target": arch_id,
                        }

                        # Copy relevant fields
                        if "axis" in rel:
                            reverse_rel["axis"] = rel["axis"]
                        if "fidelity" in rel:
                            reverse_rel["fidelity"] = rel["fidelity"]
                        if "note" in rel:
                            reverse_rel["note"] = f"Reverse of: {rel.get('note', rel_type)}"

                        target_arch.relationships.append(reverse_rel)
                        added += 1
                        self.changes[target].append(f"Added reverse {reverse_type} from {arch_id}")

        print(f"  Added {added} reverse relationships")
        return added

    def fix_missing_instantiates(self):
        """Add instantiates for archetypes missing them."""
        print("\nFixing missing instantiates...")

        fixed = 0

        for arch_id, arch in self.archetypes.items():
            if arch.instantiates:
                continue

            # Check specific fixes first
            if arch_id in DEFAULT_PRIMORDIALS:
                primordials = DEFAULT_PRIMORDIALS[arch_id]
            else:
                # Try to infer from ID prefix
                primordials = None
                for prefix, default in DEFAULT_PRIMORDIALS.items():
                    if prefix in arch_id:
                        primordials = default
                        break

            if primordials:
                arch.instantiates = [
                    {"primordial": p, "weight": w} for p, w in primordials
                ]
                fixed += 1
                self.changes[arch_id].append(f"Added default instantiates")

        print(f"  Fixed {fixed} missing instantiates")
        return fixed

    def save_changes(self, dry_run: bool = True):
        """Save all changes back to files."""
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Saving changes...")

        # Group changes by file
        files_to_save: Dict[Path, List[str]] = defaultdict(list)
        for arch_id in self.changes:
            if arch_id in self.archetypes:
                files_to_save[self.archetypes[arch_id].file_path].append(arch_id)

        saved = 0
        for file_path, arch_ids in files_to_save.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Update entries in the file
                self._update_file_entries(data, arch_ids)

                if not dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                saved += 1

            except Exception as e:
                print(f"  Error saving {file_path}: {e}")

        print(f"  {'Would save' if dry_run else 'Saved'} {saved} files")
        return saved

    def _update_file_entries(self, data: dict, arch_ids: List[str]):
        """Update archetype entries in a data structure."""
        # Handle different file structures
        if "entries" in data:
            entries = data["entries"]
        elif "@graph" in data:
            entries = data["@graph"]
        elif "archetypes" in data:
            entries = data["archetypes"]
        elif "suits" in data:
            # Tarot minor arcana - update nested cards
            for suit in data.get("suits", []):
                for card in suit.get("cards", []):
                    card_id = card.get("@id", "")
                    if card_id in arch_ids:
                        self._apply_changes_to_entry(card, card_id)
            return
        elif "members" in data:
            entries = data["members"]
        elif "hexagrams" in data:
            entries = data["hexagrams"]
        elif "@id" in data:
            entries = [data]
        else:
            return

        for entry in entries:
            entry_id = entry.get("@id", "")
            if entry_id in arch_ids:
                self._apply_changes_to_entry(entry, entry_id)

    def _apply_changes_to_entry(self, entry: dict, arch_id: str):
        """Apply accumulated changes to an entry."""
        if arch_id not in self.archetypes:
            return

        arch = self.archetypes[arch_id]

        # Update fields
        if arch.cultural_echoes:
            entry["culturalEchoes"] = arch.cultural_echoes
        if arch.aliases:
            entry["aliases"] = arch.aliases
        if arch.relationships:
            entry["relationships"] = arch.relationships
        if arch.instantiates:
            entry["instantiates"] = arch.instantiates


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Phase 2 Enrichment: Cultural Echoes & Aliases')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Show what would be changed without modifying files')
    parser.add_argument('--apply', action='store_true',
                        help='Actually apply the changes')
    parser.add_argument('--spectral-distance', type=float, default=0.15,
                        help='Max spectral distance for auto-echoes (default: 0.15)')
    args = parser.parse_args()

    dry_run = not args.apply

    print("=" * 70)
    print("PHASE 2 ENRICHMENT: CULTURAL ECHOES, ALIASES & RELATIONSHIPS")
    print("=" * 70)
    if dry_run:
        print("\n[DRY RUN - No files will be modified. Use --apply to save changes.]\n")

    acp_path = Path("ACP")
    enricher = Phase2Enricher(acp_path)

    # Load everything
    enricher.load_all()

    # Run enrichment
    echoes_added = enricher.enrich_cultural_echoes()
    spectral_added = enricher.enrich_spectral_echoes(max_distance=args.spectral_distance)
    aliases_added = enricher.enrich_aliases()
    bidir_added = enricher.fix_bidirectional_relationships()
    inst_fixed = enricher.fix_missing_instantiates()

    # Summary
    print("\n" + "=" * 40)
    print("SUMMARY")
    print("=" * 40)
    print(f"Cultural echoes added:    {echoes_added}")
    print(f"Spectral echoes added:    {spectral_added}")
    print(f"Aliases added:            {aliases_added}")
    print(f"Bidirectional links:      {bidir_added}")
    print(f"Instantiates fixed:       {inst_fixed}")
    print(f"Total archetypes changed: {len(enricher.changes)}")

    # Save
    enricher.save_changes(dry_run=dry_run)

    if dry_run:
        print("\n[DRY RUN complete. Run with --apply to save changes.]")
    else:
        print("\n[Changes saved successfully.]")


if __name__ == '__main__':
    main()
