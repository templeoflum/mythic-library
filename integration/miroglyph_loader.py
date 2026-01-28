"""Load and query Miroglyph v4 node definitions from the technical spec."""
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class MiroNode:
    node_id: str          # "D1", "R3", "E6", etc.
    arc_code: str         # "D", "R", "E"
    arc_primary: str      # "Descent", "Resonance", "Emergence"
    arc_secondary: str    # "Shadow", "Mirror", "Mythogenesis"
    condition_code: int   # 1-6
    condition_primary: str   # "Dawn", "Immersion", etc.
    condition_secondary: str # "Initiation", "Encounter", etc.
    title: str            # "The Catalyst Shard"
    role: str             # "The rupture that begins the spiral"
    tone: List[str] = field(default_factory=list)


class MiroGlyphLoader:
    """Parse miroglyph_v4_technical_spec.json into queryable structures."""

    def __init__(self, spec_path: str):
        self.spec_path = Path(spec_path)
        if not self.spec_path.exists():
            raise FileNotFoundError(f"Spec not found: {self.spec_path}")

        self.nodes: Dict[str, MiroNode] = {}
        self.nontion: dict = {}
        self.polarity_pairs: List[Tuple[int, int]] = []
        self.condition_resonance: Dict[int, List[str]] = {}
        self._load()

    def _load(self):
        """Parse the technical spec JSON."""
        with open(self.spec_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        spec = data.get("miroglyph_v4_technical_specification", data)

        # Load nodes
        for node_data in spec.get("nodes", []):
            arc = node_data.get("arc", {})
            condition = node_data.get("condition", {})
            node = MiroNode(
                node_id=node_data["node_id"],
                arc_code=arc.get("code", ""),
                arc_primary=arc.get("name_primary", ""),
                arc_secondary=arc.get("name_secondary", ""),
                condition_code=condition.get("code", 0),
                condition_primary=condition.get("name_primary", ""),
                condition_secondary=condition.get("name_secondary", ""),
                title=node_data.get("title", ""),
                role=node_data.get("role", ""),
                tone=node_data.get("tone", []),
            )
            self.nodes[node.node_id] = node

        # Load Nontion
        self.nontion = spec.get("nontion", {})

        # Load structural relationships
        relationships = spec.get("structural_relationships", {})

        # Polarity pairs
        for pair in relationships.get("polarity_pairs", {}).get("pairs", []):
            codes = pair.get("condition_pair", [])
            if len(codes) == 2:
                self.polarity_pairs.append((codes[0], codes[1]))

        # Condition resonance groups
        for group in relationships.get("condition_resonance", {}).get("groups", []):
            cond = group.get("condition", 0)
            nodes = group.get("nodes", [])
            self.condition_resonance[cond] = nodes

    def get_node(self, node_id: str) -> Optional[MiroNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def get_arc_nodes(self, arc_code: str) -> List[MiroNode]:
        """Get all nodes for an arc (D, R, or E)."""
        return [n for n in self.nodes.values() if n.arc_code == arc_code]

    def get_condition_nodes(self, condition: int) -> List[MiroNode]:
        """Get all nodes at a condition (1-6)."""
        return [n for n in self.nodes.values() if n.condition_code == condition]

    def get_polarity_partner(self, node_id: str) -> Optional[str]:
        """Get the polarity partner of a node (e.g., D1 -> D6)."""
        node = self.nodes.get(node_id)
        if not node:
            return None
        for c1, c2 in self.polarity_pairs:
            if node.condition_code == c1:
                return f"{node.arc_code}{c2}"
            if node.condition_code == c2:
                return f"{node.arc_code}{c1}"
        return None

    def get_resonance_group(self, node_id: str) -> List[str]:
        """Get same-condition nodes across arcs (e.g., D3 -> [D3, R3, E3])."""
        node = self.nodes.get(node_id)
        if not node:
            return []
        return self.condition_resonance.get(node.condition_code, [])

    def get_all_node_ids(self) -> List[str]:
        """Get all 18 node IDs (no Nontion)."""
        return sorted(self.nodes.keys(), key=lambda x: (x[0], int(x[1:])))

    def get_arc_codes(self) -> List[str]:
        """Return the 3 arc codes."""
        return ["D", "R", "E"]

    def get_condition_codes(self) -> List[int]:
        """Return the 6 condition codes."""
        return [1, 2, 3, 4, 5, 6]

    def summary(self) -> dict:
        """Return summary statistics."""
        return {
            "nodes": len(self.nodes),
            "arcs": len(set(n.arc_code for n in self.nodes.values())),
            "conditions": len(set(n.condition_code for n in self.nodes.values())),
            "polarity_pairs": len(self.polarity_pairs),
            "resonance_groups": len(self.condition_resonance),
            "has_nontion": bool(self.nontion),
        }
