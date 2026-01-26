"""Map library entities to ACP archetypes.

Mapping strategy: entity-driven with tradition preference.
For each library entity, find all candidate ACP archetypes and prefer
the one whose tradition prefix matches the entity's primary_tradition.
This prevents Norse Odin from collapsing into Greek Hermes, etc.
"""
import json
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

from integration.acp_loader import ACPLoader
from integration.library_loader import LibraryLoader


# Map library tradition names to ACP archetype ID prefixes.
# An entity with primary_tradition "norse" should prefer "arch:NO-*" archetypes.
TRADITION_TO_PREFIX = {
    "african": "AF",
    "australian": "AU",
    "celtic": "CE",
    "chinese": "CN",
    "egyptian": "EG",
    "finnish": "FI",
    "greek": "GR",
    "roman": "RO",
    "indian": "IN",
    "japanese": "JP",
    "mesoamerican": "MA",
    "mesopotamian": "ME",
    "north_american": "NA",
    "norse": "NO",
    "polynesian": "PL",
    "slavic": "SL",
    "persian": "persian",
    "zoroastrian": "persian",
    "christian": "christian",
}


@dataclass
class EntityMapping:
    library_entity: str
    acp_archetype_id: str
    acp_name: str
    confidence: float
    method: str  # 'acp_alias', 'library_alias', 'exact_name', 'fuzzy'
    fidelity: float = 1.0  # ACP alias fidelity if applicable
    notes: str = ""


def _arch_matches_tradition(arch_id: str, tradition: str) -> bool:
    """Check if an archetype ID belongs to the given tradition."""
    prefix = TRADITION_TO_PREFIX.get(tradition, "")
    if not prefix:
        return False
    # arch:GR-ZEUS -> prefix "GR", persian:ahura-mazda -> prefix "persian"
    id_body = arch_id.split(":", 1)[1] if ":" in arch_id else arch_id
    id_prefix = id_body.split("-", 1)[0] if "-" in id_body else id_body
    return id_prefix.upper() == prefix.upper()


class EntityMapper:
    def __init__(self, acp: ACPLoader, library: LibraryLoader):
        self.acp = acp
        self.library = library
        self.mappings: List[EntityMapping] = []
        self._mapped_entities: set = set()

    def auto_map_all(self) -> dict:
        """Run all mapping phases in order. Returns summary."""
        phase1 = self._map_tradition_aware()
        phase2 = self._map_via_library_aliases()

        return {
            "tradition_aware_matches": len(phase1),
            "library_alias_matches": len(phase2),
            "total_mapped": len(self.mappings),
            "total_entities": len(self.library.get_all_entities()),
        }

    def _find_all_candidates(self, name: str) -> List[Dict]:
        """Find all ACP archetypes that match a name (exact, alias, or qualified alias).

        Handles parenthetical qualifiers in ACP aliases — e.g., searching for
        "Ishtar" will also match an alias "Ishtar (Akkadian)" in the ACP.

        Returns list of dicts with keys: arch_id, arch_name, confidence,
        method, fidelity, notes.
        """
        candidates = []
        name_lower = name.lower().strip()

        for arch_id, arch_data in self.acp.archetypes.items():
            arch_name = arch_data.get("name", "")

            # Direct name match
            if arch_name.lower().strip() == name_lower:
                candidates.append({
                    "arch_id": arch_id,
                    "arch_name": arch_name,
                    "confidence": 1.0,
                    "method": "exact_name",
                    "fidelity": 1.0,
                    "notes": "",
                })
                continue

            # Alias match
            for alias in arch_data.get("aliases", []):
                if isinstance(alias, dict):
                    alias_name = alias.get("name", "")
                    fidelity = alias.get("fidelity", 0.5)
                elif isinstance(alias, str):
                    alias_name = alias
                    fidelity = 0.7
                else:
                    continue

                alias_lower = alias_name.lower().strip()

                # Exact alias match
                if alias_lower == name_lower:
                    candidates.append({
                        "arch_id": arch_id,
                        "arch_name": arch_name,
                        "confidence": fidelity,
                        "method": "acp_alias",
                        "fidelity": fidelity,
                        "notes": f"ACP alias: {alias_name} (fidelity {fidelity})",
                    })
                    break

                # Qualified alias match: "Ishtar (Akkadian)" matches "Ishtar"
                # Strip parenthetical qualifier and re-check
                if "(" in alias_lower:
                    base = alias_lower.split("(")[0].strip()
                    if base == name_lower:
                        candidates.append({
                            "arch_id": arch_id,
                            "arch_name": arch_name,
                            "confidence": fidelity,
                            "method": "acp_alias",
                            "fidelity": fidelity,
                            "notes": f"ACP alias: {alias_name} (fidelity {fidelity})",
                        })
                        break

        return candidates

    def _pick_best_candidate(self, candidates: List[Dict], tradition: str) -> Optional[Dict]:
        """Pick the best archetype candidate, preferring tradition match.

        Priority:
        1. Exact name match in the entity's own tradition
        2. Any match in the entity's own tradition
        3. Exact name match in any tradition
        4. Highest-fidelity alias match
        """
        if not candidates:
            return None

        # Partition into tradition-matched vs other
        native = [c for c in candidates if _arch_matches_tradition(c["arch_id"], tradition)]
        foreign = [c for c in candidates if not _arch_matches_tradition(c["arch_id"], tradition)]

        # Prefer native tradition
        if native:
            # Among native, prefer exact_name over alias
            exact = [c for c in native if c["method"] == "exact_name"]
            if exact:
                return exact[0]
            # Highest fidelity alias in native tradition
            native.sort(key=lambda c: -c["fidelity"])
            return native[0]

        # No native match — use best foreign
        exact = [c for c in foreign if c["method"] == "exact_name"]
        if exact:
            return exact[0]
        foreign.sort(key=lambda c: -c["fidelity"])
        return foreign[0]

    def _map_tradition_aware(self) -> List[EntityMapping]:
        """Map entities to ACP archetypes with tradition preference.

        For each library entity, find all candidate archetypes and prefer
        the one from the entity's own tradition. This prevents cross-cultural
        alias collapsing (e.g., Odin -> arch:GR-HERMES when arch:NO-ODIN exists).
        """
        entities = self.library.get_all_entities()
        matches = []

        for entity in entities:
            name = entity.canonical_name
            tradition = entity.primary_tradition or ""

            candidates = self._find_all_candidates(name)
            best = self._pick_best_candidate(candidates, tradition)

            if best:
                m = EntityMapping(
                    library_entity=name,
                    acp_archetype_id=best["arch_id"],
                    acp_name=best["arch_name"],
                    confidence=best["confidence"],
                    method=best["method"],
                    fidelity=best["fidelity"],
                    notes=best["notes"],
                )
                matches.append(m)
                self._mapped_entities.add(name)

        self.mappings.extend(matches)
        return matches

    def _map_via_library_aliases(self) -> List[EntityMapping]:
        """Phase 2: Use library entity_aliases to find ACP matches for unmapped entities."""
        db_aliases = self.library.get_entity_aliases()
        # Build tradition lookup
        entities = self.library.get_all_entities()
        entity_traditions = {e.canonical_name: (e.primary_tradition or "") for e in entities}
        matches = []

        for canonical, alias_list in db_aliases.items():
            if canonical in self._mapped_entities:
                continue

            tradition = entity_traditions.get(canonical, "")

            for alias_name in alias_list:
                candidates = self._find_all_candidates(alias_name)
                best = self._pick_best_candidate(candidates, tradition)
                if best:
                    m = EntityMapping(
                        library_entity=canonical,
                        acp_archetype_id=best["arch_id"],
                        acp_name=best["arch_name"],
                        confidence=0.8,
                        method="library_alias",
                        fidelity=best["fidelity"],
                        notes=f"Library alias: {alias_name}",
                    )
                    matches.append(m)
                    self._mapped_entities.add(canonical)
                    break

        self.mappings.extend(matches)
        return matches

    def suggest_fuzzy_matches(self, threshold: float = 0.7) -> List[Tuple[str, List[dict]]]:
        """Suggest possible matches for unmapped entities."""
        entities = self.library.get_all_entities()
        unmapped = [e for e in entities if e.canonical_name not in self._mapped_entities]
        suggestions = []

        acp_names = {}
        for arch_id, arch_data in self.acp.archetypes.items():
            name = arch_data.get("name", "")
            if name:
                acp_names[arch_id] = name

        for entity in unmapped:
            candidates = []
            for arch_id, arch_name in acp_names.items():
                ratio = SequenceMatcher(
                    None, entity.canonical_name.lower(), arch_name.lower()
                ).ratio()
                if ratio >= threshold:
                    candidates.append({
                        "acp_id": arch_id,
                        "acp_name": arch_name,
                        "similarity": round(ratio, 3),
                    })

            if candidates:
                candidates.sort(key=lambda x: -x["similarity"])
                suggestions.append((entity.canonical_name, candidates))

        return suggestions

    def get_mapping(self, library_entity: str) -> Optional[EntityMapping]:
        """Get mapping for a specific entity."""
        for m in self.mappings:
            if m.library_entity == library_entity:
                return m
        return None

    def get_unmapped_entities(self) -> List[str]:
        """Return names of entities without mappings."""
        all_names = {e.canonical_name for e in self.library.get_all_entities()}
        return sorted(all_names - self._mapped_entities)

    def get_mapped_pairs(self) -> List[Tuple[str, str]]:
        """Return (library_entity, acp_id) pairs for all mappings."""
        return [(m.library_entity, m.acp_archetype_id) for m in self.mappings]

    def save_mappings(self, output_path: str):
        """Save mappings to JSON."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                [asdict(m) for m in self.mappings],
                f, indent=2, ensure_ascii=False,
            )

    def load_mappings(self, input_path: str):
        """Load previously saved mappings."""
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.mappings = [EntityMapping(**item) for item in data]
            self._mapped_entities = {m.library_entity for m in self.mappings}
