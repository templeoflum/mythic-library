"""Map library entities to ACP archetypes."""
import json
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

from integration.acp_loader import ACPLoader
from integration.library_loader import LibraryLoader


@dataclass
class EntityMapping:
    library_entity: str
    acp_archetype_id: str
    acp_name: str
    confidence: float
    method: str  # 'acp_alias', 'library_alias', 'exact_name', 'fuzzy'
    fidelity: float = 1.0  # ACP alias fidelity if applicable
    notes: str = ""


class EntityMapper:
    def __init__(self, acp: ACPLoader, library: LibraryLoader):
        self.acp = acp
        self.library = library
        self.mappings: List[EntityMapping] = []
        self._mapped_entities: set = set()

    def auto_map_all(self) -> dict:
        """Run all mapping phases in order. Returns summary."""
        phase1 = self._map_via_acp_aliases()
        phase2 = self._map_via_exact_name()
        phase3 = self._map_via_library_aliases()

        return {
            "acp_alias_matches": len(phase1),
            "exact_name_matches": len(phase2),
            "library_alias_matches": len(phase3),
            "total_mapped": len(self.mappings),
            "total_entities": len(self.library.get_all_entities()),
        }

    def _map_via_acp_aliases(self) -> List[EntityMapping]:
        """Phase 1: Match library entities against ACP alias lists."""
        entities = self.library.get_all_entities()
        entity_names = {e.canonical_name.lower(): e.canonical_name for e in entities}
        matches = []

        for arch_id, arch_data in self.acp.archetypes.items():
            arch_name = arch_data.get("name", "")

            # Check archetype's own name
            if arch_name.lower() in entity_names:
                lib_name = entity_names[arch_name.lower()]
                if lib_name not in self._mapped_entities:
                    m = EntityMapping(
                        library_entity=lib_name,
                        acp_archetype_id=arch_id,
                        acp_name=arch_name,
                        confidence=1.0,
                        method="exact_name",
                        fidelity=1.0,
                    )
                    matches.append(m)
                    self._mapped_entities.add(lib_name)

            # Check aliases
            for alias in arch_data.get("aliases", []):
                if isinstance(alias, dict):
                    alias_name = alias.get("name", "")
                    fidelity = alias.get("fidelity", 0.5)
                elif isinstance(alias, str):
                    alias_name = alias
                    fidelity = 0.7
                else:
                    continue

                if alias_name.lower() in entity_names:
                    lib_name = entity_names[alias_name.lower()]
                    if lib_name not in self._mapped_entities:
                        m = EntityMapping(
                            library_entity=lib_name,
                            acp_archetype_id=arch_id,
                            acp_name=arch_name,
                            confidence=fidelity,
                            method="acp_alias",
                            fidelity=fidelity,
                            notes=f"ACP alias: {alias_name} (fidelity {fidelity})",
                        )
                        matches.append(m)
                        self._mapped_entities.add(lib_name)

        self.mappings.extend(matches)
        return matches

    def _map_via_exact_name(self) -> List[EntityMapping]:
        """Phase 2: Direct name match for anything not caught by aliases."""
        entities = self.library.get_all_entities()
        matches = []

        for entity in entities:
            if entity.canonical_name in self._mapped_entities:
                continue

            results = self.acp.find_by_name(entity.canonical_name)
            if results:
                best = results[0]
                m = EntityMapping(
                    library_entity=entity.canonical_name,
                    acp_archetype_id=best["id"],
                    acp_name=best["data"].get("name", ""),
                    confidence=1.0 if best["match_type"] == "exact" else 0.7,
                    method="exact_name",
                )
                matches.append(m)
                self._mapped_entities.add(entity.canonical_name)

        self.mappings.extend(matches)
        return matches

    def _map_via_library_aliases(self) -> List[EntityMapping]:
        """Phase 3: Use library entity_aliases to find ACP matches."""
        db_aliases = self.library.get_entity_aliases()
        matches = []

        for canonical, alias_list in db_aliases.items():
            if canonical in self._mapped_entities:
                continue

            for alias_name in alias_list:
                results = self.acp.find_by_name(alias_name)
                if results:
                    best = results[0]
                    m = EntityMapping(
                        library_entity=canonical,
                        acp_archetype_id=best["id"],
                        acp_name=best["data"].get("name", ""),
                        confidence=0.8,
                        method="library_alias",
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
