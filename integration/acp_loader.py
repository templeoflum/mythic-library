"""Load and query ACP archetype data from JSON-LD files."""
import json
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np

AXES = [
    "order-chaos",
    "creation-destruction",
    "light-shadow",
    "active-receptive",
    "individual-collective",
    "ascent-descent",
    "stasis-transformation",
    "voluntary-fated",
]


class ACPLoader:
    def __init__(self, acp_path: str):
        self.acp_path = Path(acp_path)
        self.archetypes: Dict[str, dict] = {}
        self.primordials: Dict[str, dict] = {}
        self.systems: Dict[str, dict] = {}
        self._alias_index: Dict[str, List[str]] = {}  # name -> list of archetype @ids
        self._load_all()

    def _load_all(self):
        """Load all JSON-LD files from ACP."""
        # Load primordials first
        primordials_path = self.acp_path / "schema" / "primordials.jsonld"
        if primordials_path.exists():
            self._load_file(primordials_path)

        # Load all archetype domains
        for domain in ["archetypes", "divination", "psychology", "modern", "calibration"]:
            domain_path = self.acp_path / domain
            if domain_path.exists():
                for jsonld_file in domain_path.rglob("*.jsonld"):
                    self._load_file(jsonld_file)

        # Build alias index
        self._build_alias_index()

    def _load_file(self, path: Path):
        """Parse a single JSON-LD file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return

        entries = data.get("entries", [])
        if not entries:
            # Try @graph format as fallback
            entries = data.get("@graph", [])
        if not entries:
            # Single entry file
            if "@id" in data:
                entries = [data]

        for entry in entries:
            entry_id = entry.get("@id", "")
            entry_type = entry.get("@type", "")

            if entry_type == "System" or entry_type == "skos:ConceptScheme":
                self.systems[entry_id] = entry
            elif entry_id.startswith("primordial:"):
                self.primordials[entry_id] = entry
            elif "spectralCoordinates" in entry:
                self.archetypes[entry_id] = entry

    def _build_alias_index(self):
        """Index all archetype names and aliases for fast lookup."""
        for arch_id, arch in self.archetypes.items():
            name = arch.get("name", "")
            if name:
                key = name.lower().strip()
                self._alias_index.setdefault(key, []).append(arch_id)

            for alias in arch.get("aliases", []):
                if isinstance(alias, dict):
                    alias_name = alias.get("name", "")
                elif isinstance(alias, str):
                    alias_name = alias
                else:
                    continue
                if alias_name:
                    key = alias_name.lower().strip()
                    self._alias_index.setdefault(key, []).append(arch_id)

    def get_coordinates(self, archetype_id: str) -> Optional[np.ndarray]:
        """Get 8D coordinate vector for an archetype."""
        arch = self.archetypes.get(archetype_id)
        if not arch or "spectralCoordinates" not in arch:
            return None

        coords = arch["spectralCoordinates"]
        return np.array([coords.get(axis, 0.5) for axis in AXES])

    def find_by_name(self, name: str) -> List[Dict]:
        """Search for archetypes by exact or alias name."""
        key = name.lower().strip()
        results = []

        # Exact match in index
        if key in self._alias_index:
            for arch_id in self._alias_index[key]:
                results.append({
                    "id": arch_id,
                    "data": self.archetypes[arch_id],
                    "match_type": "exact",
                })

        # Word-boundary substring match if no exact hit
        # Only match if the shorter string is >= 4 chars AND forms a complete
        # word boundary in the longer string (prevents Ra→Ragnarok, Hel→Helen)
        if not results and len(key) >= 4:
            for alias_key, arch_ids in self._alias_index.items():
                if len(alias_key) < 4:
                    continue
                # Check if one is a complete word within the other
                if key == alias_key:
                    continue  # already handled above
                match = False
                if len(key) <= len(alias_key):
                    # key might be a word in alias_key
                    idx = alias_key.find(key)
                    if idx >= 0:
                        before_ok = (idx == 0 or not alias_key[idx - 1].isalpha())
                        after_ok = (idx + len(key) >= len(alias_key) or not alias_key[idx + len(key)].isalpha())
                        match = before_ok and after_ok
                else:
                    # alias_key might be a word in key
                    idx = key.find(alias_key)
                    if idx >= 0:
                        before_ok = (idx == 0 or not key[idx - 1].isalpha())
                        after_ok = (idx + len(alias_key) >= len(key) or not key[idx + len(alias_key)].isalpha())
                        match = before_ok and after_ok
                if match:
                    for arch_id in arch_ids:
                        results.append({
                            "id": arch_id,
                            "data": self.archetypes[arch_id],
                            "match_type": "substring",
                        })

        # Deduplicate
        seen = set()
        unique = []
        for r in results:
            if r["id"] not in seen:
                seen.add(r["id"])
                unique.append(r)
        return unique

    def get_alias_info(self, archetype_id: str) -> List[Dict]:
        """Get alias entries for an archetype (includes fidelity scores)."""
        arch = self.archetypes.get(archetype_id)
        if not arch:
            return []
        return arch.get("aliases", [])

    def get_instantiations(self, archetype_id: str) -> List[Dict]:
        """Get primordial instantiation info for an archetype."""
        arch = self.archetypes.get(archetype_id)
        if not arch:
            return []
        return arch.get("instantiates", [])

    def calculate_distance(self, id1: str, id2: str) -> Optional[float]:
        """Calculate Euclidean distance in 8D spectral space."""
        c1 = self.get_coordinates(id1)
        c2 = self.get_coordinates(id2)
        if c1 is None or c2 is None:
            return None
        return float(np.linalg.norm(c1 - c2))

    def get_nearby(self, archetype_id: str, threshold: float = 0.3) -> List[tuple]:
        """Find archetypes within distance threshold."""
        base = self.get_coordinates(archetype_id)
        if base is None:
            return []

        nearby = []
        for other_id in self.archetypes:
            if other_id == archetype_id:
                continue
            other = self.get_coordinates(other_id)
            if other is not None:
                dist = float(np.linalg.norm(base - other))
                if dist <= threshold:
                    nearby.append((other_id, dist))

        return sorted(nearby, key=lambda x: x[1])

    def get_all_relationships(self, type_filter: Optional[str] = None) -> List[Dict]:
        """Extract all relationships from all archetypes.

        Walks every archetype's 'relationships' array and collects entries
        with the source archetype ID added.

        Args:
            type_filter: If set, only return relationships of this type
                         (e.g. "CULTURAL_ECHO", "POLAR_OPPOSITE").

        Returns:
            List of dicts, each with 'source', 'target', 'type', plus all
            type-specific properties (fidelity, axis, strength, etc.).
        """
        results = []
        for arch_id, arch in self.archetypes.items():
            for rel in arch.get("relationships", []):
                rel_type = rel.get("type", "")
                if type_filter and rel_type != type_filter:
                    continue
                entry = {"source": arch_id}
                entry.update(rel)
                results.append(entry)
        return results

    def get_primordial_ids(self) -> List[str]:
        """Return sorted list of all primordial IDs."""
        return sorted(self.primordials.keys())

    def get_all_names(self) -> Dict[str, str]:
        """Return dict of archetype_id -> name."""
        return {
            aid: a.get("name", aid) for aid, a in self.archetypes.items()
        }

    def summary(self) -> dict:
        """Return summary statistics."""
        return {
            "archetypes": len(self.archetypes),
            "primordials": len(self.primordials),
            "systems": len(self.systems),
            "alias_entries": sum(
                len(a.get("aliases", []))
                for a in self.archetypes.values()
            ),
            "with_coordinates": sum(
                1 for a in self.archetypes.values()
                if "spectralCoordinates" in a
            ),
        }
