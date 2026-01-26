# MythOS Validation: ACP + Library Integration

**Purpose**: Connect the Archetypal Context Protocol (ACP) with the mythic library to validate theoretical coordinates against empirical narrative patterns.

## Overview

This integration tests whether the ACP's 8-dimensional coordinate system accurately predicts:
- Which archetypes appear together in narratives (co-occurrence patterns)
- How Thompson motifs cluster in archetypal space
- Where gaps exist between theory and empirical data

The system has three main components:
1. **ACP Loader**: Parse JSON-LD archetypal data into queryable structures
2. **Library Loader**: Query the mythic database (173 entities, 4,000 segments, 149 motifs)
3. **Validation Suite**: Test coordinate accuracy, find outliers, generate metrics

---

## Project Structure

```
mythos-validation/
├── README.md                          # Setup & quickstart
├── INTEGRATION_SETUP.md               # This file
├── requirements.txt                   # Python dependencies
├── package.json                       # Node dependencies (for ACP tools)
├── .env.example                       # Config template
│
├── acp/                              # Git submodule or copy
│   └── [existing ACP structure]
│
├── library/                          # Your mythic library data
│   ├── data/
│   │   ├── mythic_patterns.db       # 137MB database
│   │   └── segments/                # 4,000 narrative segments
│   └── schema/
│       └── library_schema.json
│
├── integration/                      # Bridge layer
│   ├── __init__.py
│   ├── acp_loader.py                # Load ACP JSON-LD into Python
│   ├── library_loader.py            # Load library database
│   ├── entity_mapper.py             # Entity→Archetype alignment
│   └── coordinate_calculator.py     # Distance/similarity metrics
│
├── validation/                       # Test suite
│   ├── __init__.py
│   ├── test_entity_mapping.py       # Does Hermes=Hermes?
│   ├── test_coordinate_accuracy.py  # Co-occurrence vs distance
│   ├── test_motif_clustering.py     # Thompson motif patterns
│   └── test_relationship_prediction.py
│
├── analysis/                         # Jupyter notebooks
│   ├── 01_entity_alignment.ipynb    # Interactive mapping
│   ├── 02_coordinate_validation.ipynb
│   ├── 03_motif_signatures.ipynb
│   └── 04_gap_analysis.ipynb
│
├── scripts/                          # CLI tools
│   ├── setup.py                     # Initial data import
│   ├── run_validation.py            # Run all tests
│   ├── generate_report.py           # Output metrics
│   └── export_alignments.py         # Save mappings back to ACP
│
└── outputs/                          # Generated artifacts
    ├── mappings/
    │   └── entity_to_archetype.json
    ├── metrics/
    │   └── validation_results.json
    └── visualizations/
        └── coordinate_accuracy.html
```

---

## Initial Setup

### 1. Create Project Directory

```bash
# Create project directory
mkdir mythos-validation
cd mythos-validation

# Initialize git
git init

# Add ACP as submodule (or copy)
git submodule add https://github.com/templeoflum/ACP.git acp
# OR: cp -r /path/to/ACP ./acp

# Create directory structure
mkdir -p integration validation analysis scripts outputs/{mappings,metrics,visualizations}
mkdir -p library/data library/schema
```

### 2. Create Configuration Files

**requirements.txt**:
```txt
# Core
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.11.0
scikit-learn>=1.3.0

# Data handling
jsonld>=0.16.0
# sqlite3 is built-in

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.14.0

# Notebooks
jupyter>=1.0.0
ipykernel>=6.23.0

# Optional: NLP for entity extraction
spacy>=3.5.0
sentence-transformers>=2.2.0
```

**package.json**:
```json
{
  "name": "mythos-validation",
  "version": "0.1.0",
  "description": "ACP + Library validation and integration",
  "scripts": {
    "validate-acp": "node acp/tools/validate.js",
    "serve": "python -m http.server 8000"
  },
  "devDependencies": {
    "jsonld": "^8.1.0"
  }
}
```

**.env.example**:
```bash
# Paths
ACP_DATA_PATH=./acp
LIBRARY_DB_PATH=./library/data/mythic_patterns.db
SEGMENTS_PATH=./library/data/segments

# Validation thresholds
MIN_SIMILARITY_THRESHOLD=0.75
COORDINATE_DISTANCE_THRESHOLD=0.3
MIN_MOTIF_CLUSTER_SIZE=3

# Output
RESULTS_PATH=./outputs/metrics
MAPPINGS_PATH=./outputs/mappings
```

### 3. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Node dependencies (for ACP validation)
npm install

# Copy .env template
cp .env.example .env
```

### 4. Copy Library Data

```bash
# Copy your mythic library database
cp /path/to/mythic_patterns.db ./library/data/

# Copy segment data if separate
cp -r /path/to/segments ./library/data/
```

---

## Core Integration Code

### integration/acp_loader.py

```python
"""Load and query ACP archetype data."""
import json
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np

class ACPLoader:
    def __init__(self, acp_path: str):
        self.acp_path = Path(acp_path)
        self.archetypes = {}
        self.primordials = {}
        self._load_data()
    
    def _load_data(self):
        """Load all ACP JSON-LD files."""
        # Load primordials
        primordials_path = self.acp_path / "schema" / "primordials.jsonld"
        if primordials_path.exists():
            with open(primordials_path) as f:
                self.primordials = json.load(f)
        
        # Load archetypes from all domains
        domains = ['archetypes', 'divination', 'psychology', 'modern']
        for domain in domains:
            domain_path = self.acp_path / domain
            if domain_path.exists():
                self._load_domain(domain_path, domain)
    
    def _load_domain(self, path: Path, domain: str):
        """Recursively load archetypes from domain."""
        for json_file in path.rglob("*.jsonld"):
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    if '@graph' in data:
                        for item in data['@graph']:
                            if 'spectral_coordinates' in item:
                                arch_id = f"{domain}/{json_file.stem}/{item.get('name', 'unknown')}"
                                self.archetypes[arch_id] = item
                    elif 'spectral_coordinates' in data:
                        arch_id = f"{domain}/{json_file.stem}"
                        self.archetypes[arch_id] = data
            except json.JSONDecodeError:
                print(f"Warning: Could not parse {json_file}")
    
    def get_coordinates(self, archetype_id: str) -> Optional[np.ndarray]:
        """Get 8D coordinate vector for archetype."""
        arch = self.archetypes.get(archetype_id)
        if not arch or 'spectral_coordinates' not in arch:
            return None
        
        coords = arch['spectral_coordinates']
        return np.array([
            coords.get('order_chaos', 0.5),
            coords.get('creation_destruction', 0.5),
            coords.get('light_shadow', 0.5),
            coords.get('active_receptive', 0.5),
            coords.get('individual_collective', 0.5),
            coords.get('ascent_descent', 0.5),
            coords.get('stasis_transformation', 0.5),
            coords.get('voluntary_fated', 0.5)
        ])
    
    def find_by_name(self, name: str, domain: Optional[str] = None) -> List[Dict]:
        """Search for archetypes by name."""
        results = []
        for arch_id, arch_data in self.archetypes.items():
            if domain and not arch_id.startswith(domain):
                continue
            if name.lower() in arch_data.get('name', '').lower():
                results.append({
                    'id': arch_id,
                    'data': arch_data
                })
        return results
    
    def calculate_distance(self, arch1_id: str, arch2_id: str) -> Optional[float]:
        """Calculate Euclidean distance in 8D space."""
        coords1 = self.get_coordinates(arch1_id)
        coords2 = self.get_coordinates(arch2_id)
        
        if coords1 is None or coords2 is None:
            return None
        
        return np.linalg.norm(coords1 - coords2)
    
    def get_nearby(self, archetype_id: str, threshold: float = 0.3) -> List[tuple]:
        """Find all archetypes within distance threshold."""
        base_coords = self.get_coordinates(archetype_id)
        if base_coords is None:
            return []
        
        nearby = []
        for other_id in self.archetypes:
            if other_id == archetype_id:
                continue
            
            distance = self.calculate_distance(archetype_id, other_id)
            if distance and distance <= threshold:
                nearby.append((other_id, distance))
        
        return sorted(nearby, key=lambda x: x[1])
    
    def get_all_archetypes(self) -> Dict[str, Dict]:
        """Return all loaded archetypes."""
        return self.archetypes
    
    def get_archetype(self, archetype_id: str) -> Optional[Dict]:
        """Get specific archetype data."""
        return self.archetypes.get(archetype_id)
```

### integration/library_loader.py

```python
"""Load and query mythic library database."""
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Entity:
    id: int
    name: str
    entity_type: str
    mentions: int
    traditions: List[str]

@dataclass
class Segment:
    id: int
    text: str
    entities: List[str]
    motifs: List[str]
    tradition: str

class LibraryLoader:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def get_all_entities(self) -> List[Entity]:
        """Retrieve all 173 entities."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, type, mention_count, traditions
            FROM entities
        """)
        
        entities = []
        for row in cursor:
            entities.append(Entity(
                id=row['id'],
                name=row['name'],
                entity_type=row['type'],
                mentions=row['mention_count'],
                traditions=row['traditions'].split(',') if row['traditions'] else []
            ))
        return entities
    
    def get_segments_with_entity(self, entity_name: str) -> List[Segment]:
        """Get all narrative segments containing entity."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT s.id, s.text, s.entities, s.motifs, s.tradition
            FROM segments s
            WHERE s.entities LIKE ?
        """, (f'%{entity_name}%',))
        
        segments = []
        for row in cursor:
            segments.append(Segment(
                id=row['id'],
                text=row['text'],
                entities=row['entities'].split(',') if row['entities'] else [],
                motifs=row['motifs'].split(',') if row['motifs'] else [],
                tradition=row['tradition']
            ))
        return segments
    
    def get_entity_cooccurrence(self, entity1: str, entity2: str) -> int:
        """Count how many segments contain both entities."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM segments
            WHERE entities LIKE ? AND entities LIKE ?
        """, (f'%{entity1}%', f'%{entity2}%'))
        
        return cursor.fetchone()['count']
    
    def get_motif_entities(self, motif_code: str) -> List[str]:
        """Get all entities associated with a Thompson motif."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT entities
            FROM segments
            WHERE motifs LIKE ?
        """, (f'%{motif_code}%',))
        
        all_entities = set()
        for row in cursor:
            if row['entities']:
                all_entities.update(row['entities'].split(','))
        
        return list(all_entities)
    
    def get_all_motifs(self) -> List[str]:
        """Get all unique Thompson motif codes."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT motifs
            FROM segments
            WHERE motifs IS NOT NULL AND motifs != ''
        """)
        
        all_motifs = set()
        for row in cursor:
            if row['motifs']:
                all_motifs.update(row['motifs'].split(','))
        
        return sorted(list(all_motifs))
    
    def get_segment_count(self) -> int:
        """Get total number of segments."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM segments")
        return cursor.fetchone()['count']
    
    def close(self):
        self.conn.close()
```

### integration/entity_mapper.py

```python
"""Map library entities to ACP archetypes."""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json

@dataclass
class EntityMapping:
    library_entity: str
    acp_archetype: str
    confidence: float
    method: str  # 'exact', 'fuzzy', 'manual', 'inferred'
    notes: str = ""

class EntityMapper:
    def __init__(self, acp_loader, library_loader):
        self.acp = acp_loader
        self.library = library_loader
        self.mappings: List[EntityMapping] = []
    
    def auto_map_exact(self) -> List[EntityMapping]:
        """Find exact name matches between library and ACP."""
        entities = self.library.get_all_entities()
        exact_matches = []
        
        for entity in entities:
            # Search ACP for matching name
            acp_results = self.acp.find_by_name(entity.name)
            
            if len(acp_results) == 1:
                # Unique match
                mapping = EntityMapping(
                    library_entity=entity.name,
                    acp_archetype=acp_results[0]['id'],
                    confidence=1.0,
                    method='exact'
                )
                exact_matches.append(mapping)
            elif len(acp_results) > 1:
                # Multiple matches - need disambiguation
                # Take closest match from same tradition
                for result in acp_results:
                    if any(t in result['id'] for t in entity.traditions):
                        mapping = EntityMapping(
                            library_entity=entity.name,
                            acp_archetype=result['id'],
                            confidence=0.9,
                            method='exact',
                            notes='Multiple matches, chose by tradition'
                        )
                        exact_matches.append(mapping)
                        break
        
        self.mappings.extend(exact_matches)
        return exact_matches
    
    def suggest_fuzzy_matches(self, threshold: float = 0.8) -> List[Tuple[str, List[Dict]]]:
        """Suggest possible matches for unmapped entities."""
        from difflib import SequenceMatcher
        
        mapped_entities = {m.library_entity for m in self.mappings}
        entities = self.library.get_all_entities()
        unmapped = [e for e in entities if e.name not in mapped_entities]
        
        suggestions = []
        for entity in unmapped:
            candidates = []
            
            # Check all ACP archetypes
            for arch_id, arch_data in self.acp.archetypes.items():
                arch_name = arch_data.get('name', '')
                similarity = SequenceMatcher(None, entity.name.lower(), arch_name.lower()).ratio()
                
                if similarity >= threshold:
                    candidates.append({
                        'acp_id': arch_id,
                        'acp_name': arch_name,
                        'similarity': similarity
                    })
            
            if candidates:
                suggestions.append((entity.name, sorted(candidates, key=lambda x: -x['similarity'])))
        
        return suggestions
    
    def add_manual_mapping(self, library_entity: str, acp_archetype: str, 
                          confidence: float = 1.0, notes: str = ""):
        """Add a manually confirmed mapping."""
        mapping = EntityMapping(
            library_entity=library_entity,
            acp_archetype=acp_archetype,
            confidence=confidence,
            method='manual',
            notes=notes
        )
        self.mappings.append(mapping)
    
    def get_mapping(self, library_entity: str) -> Optional[EntityMapping]:
        """Get mapping for a specific entity."""
        for m in self.mappings:
            if m.library_entity == library_entity:
                return m
        return None
    
    def get_unmapped_entities(self) -> List[str]:
        """Return list of entities without mappings."""
        mapped_entities = {m.library_entity for m in self.mappings}
        all_entities = self.library.get_all_entities()
        return [e.name for e in all_entities if e.name not in mapped_entities]
    
    def save_mappings(self, output_path: str):
        """Save mappings to JSON."""
        with open(output_path, 'w') as f:
            json.dump([
                {
                    'library_entity': m.library_entity,
                    'acp_archetype': m.acp_archetype,
                    'confidence': m.confidence,
                    'method': m.method,
                    'notes': m.notes
                }
                for m in self.mappings
            ], f, indent=2)
    
    def load_mappings(self, input_path: str):
        """Load previously saved mappings."""
        with open(input_path) as f:
            data = json.load(f)
            self.mappings = [
                EntityMapping(**item) for item in data
            ]
```

### validation/test_coordinate_accuracy.py

```python
"""Test if ACP coordinate distances predict library co-occurrence."""
import numpy as np
from scipy.stats import pearsonr, spearmanr
from typing import List, Tuple, Dict
import random

class CoordinateValidation:
    def __init__(self, acp_loader, library_loader, entity_mapper):
        self.acp = acp_loader
        self.library = library_loader
        self.mapper = entity_mapper
    
    def test_distance_correlation(self, sample_size: int = 1000) -> Dict:
        """
        Test hypothesis: Smaller ACP distance → Higher narrative co-occurrence
        
        Returns correlation metrics and hypothesis test results.
        """
        # Get all mapped entity pairs
        mapped_entities = [m.library_entity for m in self.mapper.mappings]
        
        if len(mapped_entities) < 2:
            return {
                'error': 'Insufficient mapped entities',
                'mapped_count': len(mapped_entities)
            }
        
        distances = []
        cooccurrences = []
        pairs = []
        
        # Sample pairs (all would be n^2)
        max_pairs = len(mapped_entities) * (len(mapped_entities) - 1) // 2
        actual_sample_size = min(sample_size, max_pairs)
        
        sampled_pairs = set()
        attempts = 0
        max_attempts = actual_sample_size * 10
        
        while len(sampled_pairs) < actual_sample_size and attempts < max_attempts:
            e1, e2 = random.sample(mapped_entities, 2)
            pair_key = tuple(sorted([e1, e2]))
            
            if pair_key in sampled_pairs:
                attempts += 1
                continue
            
            sampled_pairs.add(pair_key)
            
            # Get ACP distance
            m1 = self.mapper.get_mapping(e1)
            m2 = self.mapper.get_mapping(e2)
            
            if not m1 or not m2:
                continue
            
            distance = self.acp.calculate_distance(m1.acp_archetype, m2.acp_archetype)
            if distance is None:
                continue
            
            # Get library co-occurrence
            cooccurrence = self.library.get_entity_cooccurrence(e1, e2)
            
            distances.append(distance)
            cooccurrences.append(cooccurrence)
            pairs.append((e1, e2))
            attempts += 1
        
        if len(distances) < 10:
            return {
                'error': 'Insufficient valid pairs',
                'valid_pairs': len(distances)
            }
        
        # Calculate correlations
        pearson_r, pearson_p = pearsonr(distances, cooccurrences)
        spearman_r, spearman_p = spearmanr(distances, cooccurrences)
        
        # Find outliers (high distance but high co-occurrence, or vice versa)
        outliers = self._find_outliers(distances, cooccurrences, pairs)
        
        return {
            'sample_size': len(distances),
            'pearson_correlation': float(pearson_r),
            'pearson_p_value': float(pearson_p),
            'spearman_correlation': float(spearman_r),
            'spearman_p_value': float(spearman_p),
            'hypothesis': 'SUPPORTED' if pearson_r < -0.3 and pearson_p < 0.05 else 'NOT SUPPORTED',
            'interpretation': self._interpret_results(pearson_r, pearson_p),
            'outliers': outliers[:10],  # Top 10 outliers
            'stats': {
                'mean_distance': float(np.mean(distances)),
                'std_distance': float(np.std(distances)),
                'mean_cooccurrence': float(np.mean(cooccurrences)),
                'std_cooccurrence': float(np.std(cooccurrences))
            }
        }
    
    def _interpret_results(self, r: float, p: float) -> str:
        if p >= 0.05:
            return "No significant correlation found between ACP distance and co-occurrence"
        if r < -0.5:
            return "Strong negative correlation: closer archetypes co-occur more frequently"
        elif r < -0.3:
            return "Moderate negative correlation: ACP has some predictive power"
        elif r > 0.3:
            return "Unexpected positive correlation: distant archetypes co-occur more (investigate)"
        else:
            return "Weak correlation: ACP coordinates may need calibration"
    
    def _find_outliers(self, distances: List[float], cooccurrences: List[int], 
                      pairs: List[Tuple[str, str]], threshold: float = 2.0) -> List[Dict]:
        """Find pairs with unexpected distance/co-occurrence ratios."""
        outliers = []
        
        mean_dist = np.mean(distances)
        std_dist = np.std(distances)
        mean_coocc = np.mean(cooccurrences)
        std_coocc = np.std(cooccurrences)
        
        for i, (dist, coocc, pair) in enumerate(zip(distances, cooccurrences, pairs)):
            z_dist = (dist - mean_dist) / std_dist if std_dist > 0 else 0
            z_coocc = (coocc - mean_coocc) / std_coocc if std_coocc > 0 else 0
            
            # Outlier if: high distance but high co-occurrence (or vice versa)
            if abs(z_dist - (-z_coocc)) > threshold:
                outliers.append({
                    'entities': pair,
                    'distance': float(dist),
                    'cooccurrence': int(coocc),
                    'z_distance': float(z_dist),
                    'z_cooccurrence': float(z_coocc),
                    'anomaly_score': float(abs(z_dist - (-z_coocc)))
                })
        
        return sorted(outliers, key=lambda x: -x['anomaly_score'])
    
    def test_primordial_clustering(self) -> Dict:
        """Test if archetypes with same primordial instantiation cluster together."""
        # Get all archetypes grouped by primordial
        primordial_groups = {}
        
        for mapping in self.mapper.mappings:
            arch_data = self.acp.get_archetype(mapping.acp_archetype)
            if not arch_data or 'instantiates' not in arch_data:
                continue
            
            for inst in arch_data['instantiates']:
                prim = inst.get('primordial', '').split(':')[-1]
                if prim not in primordial_groups:
                    primordial_groups[prim] = []
                primordial_groups[prim].append(mapping.acp_archetype)
        
        # Calculate within-group vs between-group distances
        results = {}
        for prim, archetypes in primordial_groups.items():
            if len(archetypes) < 2:
                continue
            
            within_distances = []
            for i, arch1 in enumerate(archetypes):
                for arch2 in archetypes[i+1:]:
                    dist = self.acp.calculate_distance(arch1, arch2)
                    if dist is not None:
                        within_distances.append(dist)
            
            if within_distances:
                results[prim] = {
                    'count': len(archetypes),
                    'mean_distance': float(np.mean(within_distances)),
                    'std_distance': float(np.std(within_distances))
                }
        
        return results
```

### validation/test_motif_clustering.py

```python
"""Test Thompson motif clustering in ACP space."""
from typing import Dict, List
import numpy as np
from collections import defaultdict

class MotifClustering:
    def __init__(self, acp_loader, library_loader, entity_mapper):
        self.acp = acp_loader
        self.library = library_loader
        self.mapper = entity_mapper
    
    def analyze_motif_signatures(self) -> Dict:
        """
        For each Thompson motif, find:
        1. Which archetypes are involved
        2. Their centroid in 8D space
        3. Variance (how spread out are they?)
        """
        motifs = self.library.get_all_motifs()
        signatures = {}
        
        for motif in motifs:
            entities = self.library.get_motif_entities(motif)
            
            # Map to ACP archetypes
            archetype_coords = []
            mapped_entities = []
            
            for entity in entities:
                mapping = self.mapper.get_mapping(entity)
                if mapping:
                    coords = self.acp.get_coordinates(mapping.acp_archetype)
                    if coords is not None:
                        archetype_coords.append(coords)
                        mapped_entities.append(entity)
            
            if len(archetype_coords) < 2:
                continue
            
            coords_array = np.array(archetype_coords)
            centroid = np.mean(coords_array, axis=0)
            variance = np.var(coords_array, axis=0)
            total_variance = np.sum(variance)
            
            signatures[motif] = {
                'entity_count': len(mapped_entities),
                'entities': mapped_entities,
                'centroid': centroid.tolist(),
                'variance_per_axis': variance.tolist(),
                'total_variance': float(total_variance),
                'is_clustered': total_variance < 0.5  # Threshold for "clustered"
            }
        
        return signatures
    
    def find_motif_correlations(self) -> Dict:
        """Find which axes correlate with which motif types."""
        signatures = self.analyze_motif_signatures()
        
        # Group motifs by first letter (A=cosmogony, etc.)
        motif_categories = defaultdict(list)
        for motif, data in signatures.items():
            if motif and len(motif) > 0:
                category = motif[0]
                motif_categories[category].append(data['centroid'])
        
        # Calculate average position per category
        category_centroids = {}
        for category, centroids in motif_categories.items():
            if len(centroids) > 0:
                avg_centroid = np.mean(centroids, axis=0)
                category_centroids[category] = avg_centroid.tolist()
        
        return {
            'motif_signatures': signatures,
            'category_centroids': category_centroids
        }
```

### scripts/run_validation.py

```python
"""Main validation runner."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from integration.acp_loader import ACPLoader
from integration.library_loader import LibraryLoader
from integration.entity_mapper import EntityMapper
from validation.test_coordinate_accuracy import CoordinateValidation
from validation.test_motif_clustering import MotifClustering
import json
from datetime import datetime

def main():
    print("=== MythOS Validation Suite ===")
    print(f"Run started: {datetime.now().isoformat()}\n")
    
    # Load data
    print("Loading ACP...")
    acp = ACPLoader('./acp')
    print(f"  ✓ Loaded {len(acp.archetypes)} archetypes")
    
    print("\nLoading Library...")
    library = LibraryLoader('./library/data/mythic_patterns.db')
    entities = library.get_all_entities()
    segment_count = library.get_segment_count()
    motif_count = len(library.get_all_motifs())
    print(f"  ✓ Loaded {len(entities)} entities")
    print(f"  ✓ Loaded {segment_count} narrative segments")
    print(f"  ✓ Loaded {motif_count} Thompson motifs")
    
    # Map entities
    print("\n--- Entity Mapping ---")
    mapper = EntityMapper(acp, library)
    
    print("Finding exact matches...")
    exact_matches = mapper.auto_map_exact()
    print(f"  ✓ Found {len(exact_matches)} exact matches")
    
    print("Finding fuzzy suggestions...")
    fuzzy_suggestions = mapper.suggest_fuzzy_matches(threshold=0.75)
    print(f"  ✓ Found {len(fuzzy_suggestions)} entities needing review")
    
    unmapped = mapper.get_unmapped_entities()
    print(f"  ⚠ {len(unmapped)} entities remain unmapped")
    
    # Save mappings
    mappings_path = './outputs/mappings/entity_to_archetype.json'
    mapper.save_mappings(mappings_path)
    print(f"  ✓ Saved mappings to {mappings_path}")
    
    # Save unmapped entities
    with open('./outputs/mappings/unmapped_entities.json', 'w') as f:
        json.dump(unmapped, f, indent=2)
    
    # Save fuzzy suggestions
    with open('./outputs/mappings/fuzzy_suggestions.json', 'w') as f:
        json.dump([
            {
                'entity': entity,
                'candidates': candidates
            }
            for entity, candidates in fuzzy_suggestions
        ], f, indent=2)
    
    # Run validation tests
    print("\n=== Validation Tests ===\n")
    
    # Test 1: Coordinate accuracy
    print("Test 1: Coordinate Distance vs Co-occurrence")
    validator = CoordinateValidation(acp, library, mapper)
    coord_results = validator.test_distance_correlation(sample_size=1000)
    
    if 'error' not in coord_results:
        print(f"  Sample size: {coord_results['sample_size']}")
        print(f"  Pearson r: {coord_results['pearson_correlation']:.3f} (p={coord_results['pearson_p_value']:.4f})")
        print(f"  Spearman ρ: {coord_results['spearman_correlation']:.3f} (p={coord_results['spearman_p_value']:.4f})")
        print(f"  Hypothesis: {coord_results['hypothesis']}")
        print(f"  → {coord_results['interpretation']}")
        
        if coord_results['outliers']:
            print(f"\n  Top outliers (unexpected pairs):")
            for outlier in coord_results['outliers'][:3]:
                print(f"    • {outlier['entities'][0]} ↔ {outlier['entities'][1]}")
                print(f"      Distance: {outlier['distance']:.3f}, Co-occurrence: {outlier['cooccurrence']}")
    else:
        print(f"  ✗ Error: {coord_results['error']}")
    
    # Test 2: Primordial clustering
    print("\nTest 2: Primordial Instantiation Clustering")
    prim_results = validator.test_primordial_clustering()
    print(f"  Analyzed {len(prim_results)} primordial categories")
    
    # Show top 3 most cohesive
    sorted_prims = sorted(prim_results.items(), key=lambda x: x[1]['mean_distance'])[:3]
    print(f"\n  Most cohesive primordials:")
    for prim, data in sorted_prims:
        print(f"    • {prim}: {data['count']} archetypes, mean distance {data['mean_distance']:.3f}")
    
    # Test 3: Motif clustering
    print("\nTest 3: Thompson Motif Signatures")
    motif_analyzer = MotifClustering(acp, library, mapper)
    motif_results = motif_analyzer.find_motif_correlations()
    
    clustered_count = sum(1 for sig in motif_results['motif_signatures'].values() if sig['is_clustered'])
    total_motifs = len(motif_results['motif_signatures'])
    print(f"  Analyzed {total_motifs} motifs")
    print(f"  {clustered_count} motifs show tight clustering (variance < 0.5)")
    
    # Save all results
    print("\n--- Saving Results ---")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'acp_archetypes': len(acp.archetypes),
            'library_entities': len(entities),
            'library_segments': segment_count,
            'thompson_motifs': motif_count,
            'mapped_entities': len(mapper.mappings),
            'unmapped_entities': len(unmapped)
        },
        'coordinate_validation': coord_results,
        'primordial_clustering': prim_results,
        'motif_analysis': motif_results
    }
    
    results_path = './outputs/metrics/validation_results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  ✓ Saved validation results to {results_path}")
    
    print("\n=== Validation Complete ===")
    print(f"Run finished: {datetime.now().isoformat()}")
    print("\nNext steps:")
    print("  1. Review unmapped entities in outputs/mappings/unmapped_entities.json")
    print("  2. Check fuzzy suggestions in outputs/mappings/fuzzy_suggestions.json")
    print("  3. Analyze outliers in validation results")
    print("  4. Use Jupyter notebooks in analysis/ for deeper exploration")
    
    library.close()

if __name__ == '__main__':
    main()
```

### scripts/setup.py

```python
"""Initial setup and validation script."""
import sys
from pathlib import Path
import subprocess

def main():
    print("=== MythOS Validation Setup ===\n")
    
    # Check directories
    required_dirs = [
        'acp',
        'library/data',
        'integration',
        'validation',
        'scripts',
        'outputs/mappings',
        'outputs/metrics',
        'outputs/visualizations'
    ]
    
    print("Checking directories...")
    for dir_path in required_dirs:
        path = Path(dir_path)
        if not path.exists():
            print(f"  ✗ Missing: {dir_path}")
            if 'outputs' in dir_path:
                print(f"    Creating {dir_path}...")
                path.mkdir(parents=True, exist_ok=True)
        else:
            print(f"  ✓ Found: {dir_path}")
    
    # Check for library database
    print("\nChecking library database...")
    db_path = Path('library/data/mythic_patterns.db')
    if not db_path.exists():
        print(f"  ✗ Library database not found at {db_path}")
        print("  → Please copy your mythic_patterns.db to library/data/")
        return
    else:
        print(f"  ✓ Database found")
    
    # Check ACP data
    print("\nChecking ACP data...")
    acp_schema = Path('acp/schema/primordials.jsonld')
    if not acp_schema.exists():
        print(f"  ✗ ACP schema not found")
        print("  → Please ensure ACP repository is cloned/copied to ./acp/")
        return
    else:
        print(f"  ✓ ACP schema found")
    
    # Validate ACP data with Node
    print("\nValidating ACP data...")
    try:
        result = subprocess.run(
            ['node', 'acp/tools/validate.js'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("  ✓ ACP validation passed")
        else:
            print("  ⚠ ACP validation had warnings")
            if result.stdout:
                print(result.stdout)
    except FileNotFoundError:
        print("  ⚠ Node.js not found, skipping ACP validation")
    except Exception as e:
        print(f"  ⚠ Could not validate ACP: {e}")
    
    # Create .env if needed
    print("\nChecking configuration...")
    env_path = Path('.env')
    if not env_path.exists():
        env_example = Path('.env.example')
        if env_example.exists():
            print("  Creating .env from .env.example...")
            env_path.write_text(env_example.read_text())
            print("  ✓ Created .env")
        else:
            print("  ⚠ No .env.example found")
    else:
        print("  ✓ .env exists")
    
    # Create __init__.py files
    print("\nCreating Python package files...")
    for module_dir in ['integration', 'validation']:
        init_file = Path(module_dir) / '__init__.py'
        if not init_file.exists():
            init_file.touch()
            print(f"  ✓ Created {init_file}")
    
    print("\n=== Setup Complete ===")
    print("\nNext steps:")
    print("  1. Run: python scripts/run_validation.py")
    print("  2. Explore results in outputs/")
    print("  3. Use Jupyter notebooks for interactive analysis")

if __name__ == '__main__':
    main()
```

---

## Usage

### Quick Start

```bash
# Setup
python scripts/setup.py

# Run validation
python scripts/run_validation.py

# Results will be in outputs/
ls outputs/mappings/
ls outputs/metrics/
```

### Interactive Analysis

```bash
# Start Jupyter
jupyter notebook

# Open notebooks in analysis/
# - 01_entity_alignment.ipynb
# - 02_coordinate_validation.ipynb
# - 03_motif_signatures.ipynb
# - 04_gap_analysis.ipynb
```

### Manual Entity Mapping

```python
from integration.acp_loader import ACPLoader
from integration.library_loader import LibraryLoader
from integration.entity_mapper import EntityMapper

acp = ACPLoader('./acp')
library = LibraryLoader('./library/data/mythic_patterns.db')
mapper = EntityMapper(acp, library)

# Add manual mappings for entities that weren't auto-matched
mapper.add_manual_mapping(
    library_entity="Loki",
    acp_archetype="archetypes/norse/loki",
    confidence=1.0,
    notes="Manually verified"
)

mapper.save_mappings('./outputs/mappings/entity_to_archetype.json')
```

---

## Expected Outputs

### 1. Entity Mappings (`outputs/mappings/`)

**entity_to_archetype.json**:
```json
[
  {
    "library_entity": "Zeus",
    "acp_archetype": "archetypes/greek/zeus",
    "confidence": 1.0,
    "method": "exact",
    "notes": ""
  },
  {
    "library_entity": "Hermes",
    "acp_archetype": "archetypes/greek/hermes",
    "confidence": 1.0,
    "method": "exact",
    "notes": ""
  }
]
```

**unmapped_entities.json**: List of entities that need manual mapping

**fuzzy_suggestions.json**: Suggested matches with similarity scores

### 2. Validation Results (`outputs/metrics/`)

**validation_results.json**:
```json
{
  "timestamp": "2026-01-26T...",
  "summary": {
    "acp_archetypes": 580,
    "library_entities": 173,
    "library_segments": 4000,
    "thompson_motifs": 149,
    "mapped_entities": 156,
    "unmapped_entities": 17
  },
  "coordinate_validation": {
    "sample_size": 1000,
    "pearson_correlation": -0.42,
    "pearson_p_value": 0.001,
    "hypothesis": "SUPPORTED",
    "interpretation": "Moderate negative correlation: ACP has some predictive power",
    "outliers": [...]
  },
  "primordial_clustering": {...},
  "motif_analysis": {...}
}
```

### 3. Key Metrics to Interpret

**Correlation Results:**
- `r < -0.3, p < 0.05`: ACP coordinates predict co-occurrence ✓
- `r ≈ 0, p > 0.05`: No correlation, coordinates need calibration
- `r > 0.3`: Unexpected positive correlation, investigate outliers

**Outliers to Investigate:**
- High distance + high co-occurrence: Narratively connected but symbolically different
- Low distance + low co-occurrence: Symbolically similar but rarely appear together

**Motif Clustering:**
- `total_variance < 0.5`: Motif tightly clustered in ACP space
- `total_variance > 1.0`: Motif spans diverse archetypal territory

---

## Next Steps After Validation

### If Correlation is Strong (r < -0.4)
ACP coordinates are empirically grounded. You can:
1. Use ACP + RAG for myth generation
2. Build structured prompting system
3. Fine-tuning may not be necessary

### If Correlation is Weak (r ≈ 0)
ACP coordinates need calibration:
1. Use co-occurrence data to adjust weights
2. Implement optimization loop (gradient descent on coordinates)
3. Re-run validation to measure improvement

### If Many Outliers Exist
Investigate specific cases:
1. Are outliers due to narrative convention vs symbolic similarity?
2. Do certain mythological systems have unique patterns?
3. Should coordinate system be culture-specific?

### If Motif Signatures are Clear
Thompson motifs provide training data:
1. Fine-tune model on motif→archetype patterns
2. Use motif centroids as "archetypal verbs"
3. Build motif-driven narrative generation

---

## Integration with LLM Strategy

After validation, you'll know:

1. **How accurate is ACP?** (correlation strength)
2. **What needs calibration?** (outliers, unmapped entities)
3. **Can motifs drive generation?** (motif clustering results)

Then choose architecture:

### Option A: ACP is Accurate → RAG + Structured Prompting
```
User query → ACP selects archetypes → RAG finds library examples → LLM renders
```
No fine-tuning needed.

### Option B: ACP Needs Calibration → Hybrid System
```
Optimize ACP coordinates using library data → Then use RAG approach
```
Mathematical optimization, not neural training.

### Option C: Build New Patterns → Fine-tune on Structure
```
Training data: motif signatures + archetypal transitions
Model learns: narrative grammar, not specific myths
```
Fine-tune to understand structure-to-narrative mapping.

---

## Troubleshooting

### "No module named 'integration'"

```bash
# Make sure you're running from project root
cd mythos-validation
python scripts/run_validation.py
```

### "Database file not found"

```bash
# Check database path
ls library/data/mythic_patterns.db

# Update path in .env if different
nano .env
```

### "No archetypes loaded"

```bash
# Verify ACP structure
ls acp/schema/
ls acp/archetypes/

# Check JSON-LD files are valid
node acp/tools/validate.js
```

### "Insufficient mapped entities"

This is expected on first run. Follow these steps:
1. Check `outputs/mappings/fuzzy_suggestions.json`
2. Manually verify suggested matches
3. Add confirmed mappings using `mapper.add_manual_mapping()`
4. Re-run validation

---

## File Checklist

Before running validation, ensure you have:

- [ ] ACP repository in `./acp/`
- [ ] Library database at `./library/data/mythic_patterns.db`
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] Output directories created (`scripts/setup.py` does this)
- [ ] `.env` file configured
- [ ] `__init__.py` in integration/ and validation/

---

## Questions to Answer

After running validation, you should be able to answer:

1. **How many entities mapped automatically?** (Target: >70%)
2. **What's the correlation between distance and co-occurrence?** (Target: r < -0.3)
3. **Which archetypes are outliers?** (Need coordinate adjustment)
4. **Do Thompson motifs cluster in ACP space?** (Target: >50% clustered)
5. **Which primordials have tight clustering?** (Validates theoretical model)

These answers determine whether to:
- Use ACP as-is with RAG
- Calibrate coordinates with optimization
- Fine-tune an LLM on structural patterns

---

**End of Integration Guide**

For questions or issues, check:
- ACP documentation: `acp/README.md`
- System architecture: `acp/SYSTEM_ARCHITECTURE.md`
- Fundamental laws: `acp/FUNDAMENTAL_LAWS.md`
