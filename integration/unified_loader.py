"""Unified loader for all three mythic systems: Library, ACP, and Miroglyph."""
import sys
from pathlib import Path
from typing import Dict

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integration.acp_loader import ACPLoader
from integration.library_loader import LibraryLoader
from integration.entity_mapper import EntityMapper
from integration.miroglyph_loader import MiroGlyphLoader


class UnifiedLoader:
    """Single entry point for Library + ACP + Miroglyph + EntityMapper."""

    def __init__(self, project_root: str = None):
        root = Path(project_root) if project_root else PROJECT_ROOT

        self.acp = ACPLoader(str(root / "ACP"))
        self.library = LibraryLoader(str(root / "data" / "mythic_patterns.db"))
        self.miroglyph = MiroGlyphLoader(
            str(root / "miroglyph" / "miroglyph_v4_technical_spec.json")
        )
        self.mapper = EntityMapper(self.acp, self.library)
        self.map_result = self.mapper.auto_map_all()

    def summary(self) -> Dict:
        """Combined statistics from all three systems."""
        acp_s = self.acp.summary()
        lib_s = self.library.summary()
        miro_s = self.miroglyph.summary()

        return {
            "acp": acp_s,
            "library": lib_s,
            "miroglyph": miro_s,
            "mapping": {
                "total_entities": self.map_result.get("total_entities", 0),
                "mapped": self.map_result.get("total_mapped", 0),
                "rate": round(
                    self.map_result.get("total_mapped", 0)
                    / max(self.map_result.get("total_entities", 1), 1) * 100, 1
                ),
            },
        }

    def get_entity_coordinates(self, entity_name: str):
        """Get ACP 8D coordinates for a library entity (via mapping)."""
        mapping = self.mapper.get_mapping(entity_name)
        if not mapping:
            return None
        return self.acp.get_coordinates(mapping.acp_archetype_id)

    def close(self):
        self.library.close()


if __name__ == "__main__":
    import json

    loader = UnifiedLoader()
    s = loader.summary()
    print("=" * 60)
    print("Unified Mythic System — Summary")
    print("=" * 60)
    print(f"\nACP:       {s['acp']['archetypes']} archetypes, "
          f"{s['acp']['primordials']} primordials")
    print(f"Library:   {s['library']['entities']} entities, "
          f"{s['library']['segments']} segments, "
          f"{s['library']['traditions']} traditions")
    print(f"Miroglyph: {s['miroglyph']['nodes']} nodes, "
          f"{s['miroglyph']['arcs']} arcs, "
          f"{s['miroglyph']['conditions']} conditions")
    print(f"Mapping:   {s['mapping']['mapped']}/{s['mapping']['total_entities']} "
          f"entities mapped ({s['mapping']['rate']}%)")
    loader.close()
