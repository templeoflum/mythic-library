"""Map library entities to ACP archetypes.

Mapping strategy: entity-driven with tradition preference.
For each library entity, find all candidate ACP archetypes and prefer
the one whose tradition prefix matches the entity's primary_tradition.
This prevents Norse Odin from collapsing into Greek Hermes, etc.
"""
import json
import unicodedata
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

    @staticmethod
    def _strip_diacritics(s: str) -> str:
        """Remove diacritical marks: Cú -> Cu, Ōmikami -> Omikami, Nüwa -> Nuwa."""
        nfkd = unicodedata.normalize("NFKD", s)
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    @staticmethod
    def _collapse_name(s: str) -> str:
        """Collapse a name to alphanumeric only for fuzzy comparison.

        'Cú Chulainn' -> 'cuchulainn', 'Amaterasu-Ōmikami' -> 'amaterasuomikami'
        """
        nfkd = unicodedata.normalize("NFKD", s.lower())
        return "".join(c for c in nfkd if c.isalnum())

    @staticmethod
    def _is_word_boundary_match(needle: str, haystack: str) -> bool:
        """Check if needle appears as a complete word/prefix in haystack.

        Matches cases like:
        - "Amaterasu" in "Amaterasu-Ōmikami" (hyphen-separated prefix)
        - "Dagda" in "The Dagda" (space-separated word)
        - "Izanagi" in "Izanagi-no-Mikoto"

        Requires needle to be >= 4 chars and match at a word boundary.
        """
        if len(needle) < 4:
            return False
        idx = haystack.find(needle)
        if idx < 0:
            return False
        before_ok = (idx == 0 or not haystack[idx - 1].isalpha())
        end = idx + len(needle)
        after_ok = (end >= len(haystack) or not haystack[end].isalpha())
        return before_ok and after_ok

    def _find_all_candidates(self, name: str) -> List[Dict]:
        """Find all ACP archetypes that match a name.

        Matching strategies (in priority order):
        1. Exact name match (confidence 1.0)
        2. Exact alias match (confidence = alias fidelity)
        3. Qualified alias match: "Ishtar (Akkadian)" matches "Ishtar"
        4. Word-boundary name match: "Amaterasu" matches "Amaterasu-Ōmikami"

        Returns list of dicts with keys: arch_id, arch_name, confidence,
        method, fidelity, notes.
        """
        candidates = []
        name_lower = name.lower().strip()
        name_norm = self._strip_diacritics(name_lower)
        name_collapsed = self._collapse_name(name)

        for arch_id, arch_data in self.acp.archetypes.items():
            arch_name = arch_data.get("name", "")
            arch_name_lower = arch_name.lower().strip()
            arch_name_norm = self._strip_diacritics(arch_name_lower)

            # Direct name match (diacritics-insensitive)
            if arch_name_norm == name_norm:
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
            alias_matched = False
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
                alias_norm = self._strip_diacritics(alias_lower)

                # Exact alias match (diacritics-insensitive)
                if alias_norm == name_norm:
                    candidates.append({
                        "arch_id": arch_id,
                        "arch_name": arch_name,
                        "confidence": fidelity,
                        "method": "acp_alias",
                        "fidelity": fidelity,
                        "notes": f"ACP alias: {alias_name} (fidelity {fidelity})",
                    })
                    alias_matched = True
                    break

                # Qualified alias match: "Ishtar (Akkadian)" matches "Ishtar"
                if "(" in alias_norm:
                    base = alias_norm.split("(")[0].strip()
                    if base == name_norm:
                        candidates.append({
                            "arch_id": arch_id,
                            "arch_name": arch_name,
                            "confidence": fidelity,
                            "method": "acp_alias",
                            "fidelity": fidelity,
                            "notes": f"ACP alias: {alias_name} (fidelity {fidelity})",
                        })
                        alias_matched = True
                        break

            if alias_matched:
                continue

            # Collapsed name match: strip all non-alphanumeric chars + diacritics
            # "Cuchulainn" matches "Cú Chulainn", "Setanta" matches "Sétanta"
            arch_collapsed = self._collapse_name(arch_name)
            if arch_collapsed == name_collapsed and len(name_collapsed) >= 4:
                candidates.append({
                    "arch_id": arch_id,
                    "arch_name": arch_name,
                    "confidence": 0.95,
                    "method": "collapsed_name",
                    "fidelity": 0.95,
                    "notes": f"Collapsed match: {name} ~ {arch_name}",
                })
                continue

            # Also check collapsed aliases
            collapsed_alias_matched = False
            for alias in arch_data.get("aliases", []):
                if isinstance(alias, dict):
                    alias_name = alias.get("name", "")
                    fidelity = alias.get("fidelity", 0.5)
                elif isinstance(alias, str):
                    alias_name = alias
                    fidelity = 0.7
                else:
                    continue
                if self._collapse_name(alias_name) == name_collapsed and len(name_collapsed) >= 4:
                    candidates.append({
                        "arch_id": arch_id,
                        "arch_name": arch_name,
                        "confidence": fidelity,
                        "method": "collapsed_alias",
                        "fidelity": fidelity,
                        "notes": f"Collapsed alias match: {name} ~ {alias_name}",
                    })
                    collapsed_alias_matched = True
                    break

            if collapsed_alias_matched:
                continue

            # Word-boundary name match (lower confidence, diacritics-insensitive)
            # "Amaterasu" matches "Amaterasu-Ōmikami", "Dagda" matches "The Dagda"
            if self._is_word_boundary_match(name_norm, arch_name_norm):
                candidates.append({
                    "arch_id": arch_id,
                    "arch_name": arch_name,
                    "confidence": 0.85,
                    "method": "word_boundary",
                    "fidelity": 0.85,
                    "notes": f"Word-boundary match: {name} in {arch_name}",
                })
                continue

            # Word-boundary alias match: "Amun" matches alias "Amun-Ra"
            for alias in arch_data.get("aliases", []):
                if isinstance(alias, dict):
                    alias_name = alias.get("name", "")
                elif isinstance(alias, str):
                    alias_name = alias
                else:
                    continue
                alias_norm = self._strip_diacritics(alias_name.lower().strip())
                if self._is_word_boundary_match(name_norm, alias_norm):
                    candidates.append({
                        "arch_id": arch_id,
                        "arch_name": arch_name,
                        "confidence": 0.7,
                        "method": "word_boundary",
                        "fidelity": 0.7,
                        "notes": f"Word-boundary alias match: {name} in {alias_name}",
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
        """Phase 2: Use library entity_aliases to find ACP matches for unmapped entities.

        Two strategies:
        1. Forward: for each canonical in alias table, try its aliases against ACP.
        2. Reverse: for each unmapped entity, check if its name appears as an alias
           value — if so, use the canonical name to search ACP.
        """
        db_aliases = self.library.get_entity_aliases()
        entities = self.library.get_all_entities()
        entity_traditions = {e.canonical_name: (e.primary_tradition or "") for e in entities}
        matches = []

        # Forward lookup: canonical -> alias_list
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

        # Reverse lookup: if an unmapped entity's name appears as an alias value,
        # use the canonical name to search ACP.
        # e.g., library entity "Balder" is an alias of canonical "Baldur" -> search "Baldur" in ACP
        reverse_index: Dict[str, str] = {}
        for canonical, alias_list in db_aliases.items():
            for alias_name in alias_list:
                reverse_index[alias_name.lower()] = canonical

        unmapped = [e for e in entities if e.canonical_name not in self._mapped_entities]
        for entity in unmapped:
            name_lower = entity.canonical_name.lower()
            if name_lower in reverse_index:
                canonical_alias = reverse_index[name_lower]
                tradition = entity.primary_tradition or ""
                candidates = self._find_all_candidates(canonical_alias)
                best = self._pick_best_candidate(candidates, tradition)
                if best:
                    m = EntityMapping(
                        library_entity=entity.canonical_name,
                        acp_archetype_id=best["arch_id"],
                        acp_name=best["arch_name"],
                        confidence=0.75,
                        method="reverse_alias",
                        fidelity=best["fidelity"],
                        notes=f"Reverse alias: {entity.canonical_name} -> {canonical_alias}",
                    )
                    matches.append(m)
                    self._mapped_entities.add(entity.canonical_name)

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
