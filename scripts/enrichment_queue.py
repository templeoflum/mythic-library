#!/usr/bin/env python3
"""
Generate prioritized enrichment queue from audit results.

This script analyzes archetype completeness and generates a prioritized
work queue for systematic enrichment, grouped by system, tier, and field type.

Output: JSON manifest showing what needs enrichment and in what order.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Set

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from integration.acp_loader import ACPLoader

# Field definitions by tier (same as audit script)
REQUIRED_FIELDS = {
    'description': 'Core description',
    'spectralCoordinates': '8D coordinates',
    'instantiates': 'Primordial links',
}

TIER_1_FIELDS = {
    'keywords': 'Searchable terms',
    'domains': 'Areas of influence',
    'relationships': 'Explicit connections',
}

TIER_2_FIELDS = {
    'correspondences': 'Cross-system refs',
    'culturalEchoes': 'Cultural equivalents',
    'aliases': 'Alternative names',
}

TIER_3_FIELDS = {
    'narrativeRoles': 'Story functions',
    'psychologicalMapping': 'Jungian/developmental',
    'coreFunction': 'Essential purpose',
    'symbolicCore': 'Central symbol',
}

TIER_4_FIELDS = {
    'storyFunctions': 'Narrative actions',
    'elementalComposition': 'Elemental makeup',
}

# Priority systems for enrichment (order matters)
PRIORITY_SYSTEMS = [
    ('arch', 'GR', 'Greek Olympians'),        # Template system
    ('jungian', None, 'Jungian Core'),        # Psychological foundation
    ('tarot', 'TAMA', 'Tarot Major Arcana'),  # High correspondence density
    ('arch', 'BU', 'Buddhist Pantheon'),      # New, needs enrichment
    ('mbti', None, 'MBTI Types'),             # High user interest
    ('hj', None, "Hero's Journey"),           # Narrative foundation
    ('enneagram', None, 'Enneagram'),         # Psychology
    ('vogler', None, 'Vogler Archetypes'),    # Narrative
    ('arch', 'NO', 'Norse Pantheon'),         # Major pantheon
    ('arch', 'EG', 'Egyptian Pantheon'),      # Major pantheon
]

# Controlled domain vocabulary for validation
VALID_DOMAINS = {
    'death', 'rebirth', 'underworld', 'sky', 'sea', 'earth', 'fire', 'water', 'air',
    'war', 'peace', 'love', 'fertility', 'harvest', 'hunt', 'wisdom', 'knowledge',
    'crafts', 'smithing', 'healing', 'prophecy', 'music', 'poetry', 'dance',
    'threshold', 'boundaries', 'travel', 'commerce', 'communication',
    'justice', 'law', 'order', 'chaos', 'fate', 'time', 'memory',
    'home', 'hearth', 'family', 'marriage', 'motherhood', 'fatherhood', 'childhood',
    'transformation', 'initiation', 'sacrifice', 'ecstasy', 'madness',
    'sovereignty', 'protection', 'destruction', 'creation', 'preservation',
}


@dataclass
class EnrichmentTask:
    """A single archetype needing enrichment."""
    archetype_id: str
    name: str
    system_prefix: str
    system_code: str
    current_score: float
    current_tier: str
    missing_fields: Dict[str, List[str]]  # tier -> [fields]
    priority_rank: int = 999  # Lower = higher priority
    enrichment_effort: str = "low"  # low/medium/high


@dataclass
class EnrichmentQueue:
    """Prioritized queue of enrichment tasks."""
    generated_at: str
    total_archetypes: int
    total_needing_enrichment: int
    by_priority: List[Dict]  # Ordered by priority
    by_system: Dict[str, List[str]]  # system -> [archetype_ids]
    by_missing_field: Dict[str, List[str]]  # field -> [archetype_ids]
    summary: Dict


def calculate_completeness(archetype: dict) -> dict:
    """Calculate completeness score and missing fields."""
    result = {
        'required': {'present': [], 'missing': []},
        'tier1': {'present': [], 'missing': []},
        'tier2': {'present': [], 'missing': []},
        'tier3': {'present': [], 'missing': []},
        'tier4': {'present': [], 'missing': []},
        'score': 0.0,
        'tier': 'stub'
    }

    def check_fields(field_dict, tier_key):
        for field_name in field_dict:
            if field_name in archetype and archetype[field_name]:
                val = archetype[field_name]
                if isinstance(val, (list, dict)) and len(val) == 0:
                    result[tier_key]['missing'].append(field_name)
                else:
                    result[tier_key]['present'].append(field_name)
            else:
                result[tier_key]['missing'].append(field_name)

    check_fields(REQUIRED_FIELDS, 'required')
    check_fields(TIER_1_FIELDS, 'tier1')
    check_fields(TIER_2_FIELDS, 'tier2')
    check_fields(TIER_3_FIELDS, 'tier3')
    check_fields(TIER_4_FIELDS, 'tier4')

    # Calculate weighted score
    required_score = len(result['required']['present']) / len(REQUIRED_FIELDS) * 30
    tier1_score = len(result['tier1']['present']) / len(TIER_1_FIELDS) * 25
    tier2_score = len(result['tier2']['present']) / len(TIER_2_FIELDS) * 20
    tier3_score = len(result['tier3']['present']) / len(TIER_3_FIELDS) * 15
    tier4_score = len(result['tier4']['present']) / len(TIER_4_FIELDS) * 10

    result['score'] = required_score + tier1_score + tier2_score + tier3_score + tier4_score

    if result['score'] >= 80:
        result['tier'] = 'complete'
    elif result['score'] >= 60:
        result['tier'] = 'rich'
    elif result['score'] >= 40:
        result['tier'] = 'partial'
    else:
        result['tier'] = 'stub'

    return result


def get_priority_rank(archetype_id: str, system_code: str) -> int:
    """Determine priority rank based on system membership."""
    prefix = archetype_id.split(':')[0] if ':' in archetype_id else archetype_id.split('-')[0]

    for rank, (sys_prefix, sys_code, _) in enumerate(PRIORITY_SYSTEMS):
        if prefix == sys_prefix:
            if sys_code is None or sys_code == system_code:
                return rank

    # Non-priority systems get rank 100+
    return 100


def estimate_effort(missing_fields: Dict[str, List[str]]) -> str:
    """Estimate enrichment effort based on missing fields."""
    total_missing = sum(len(fields) for fields in missing_fields.values())

    # Tier 1 and 2 fields are often automatable
    automatable = len(missing_fields.get('tier1', [])) + len(missing_fields.get('tier2', []))
    manual = len(missing_fields.get('tier3', [])) + len(missing_fields.get('tier4', []))

    if total_missing <= 3 or (automatable >= manual and total_missing <= 6):
        return "low"
    elif total_missing <= 8 or manual <= 2:
        return "medium"
    else:
        return "high"


def generate_queue(acp: ACPLoader) -> EnrichmentQueue:
    """Generate prioritized enrichment queue."""
    from datetime import datetime

    tasks: List[EnrichmentTask] = []
    by_system: Dict[str, List[str]] = defaultdict(list)
    by_field: Dict[str, List[str]] = defaultdict(list)
    tier_counts = defaultdict(int)

    for arch_id, arch in acp.archetypes.items():
        completeness = calculate_completeness(arch)
        tier_counts[completeness['tier']] += 1

        # Skip complete entries
        if completeness['tier'] == 'complete':
            continue

        # Extract system info
        system_code = arch.get('systemCode', '')
        prefix = arch_id.split(':')[0] if ':' in arch_id else ''

        # Build missing fields dict
        missing = {}
        for tier_key in ['required', 'tier1', 'tier2', 'tier3', 'tier4']:
            if completeness[tier_key]['missing']:
                missing[tier_key] = completeness[tier_key]['missing']

        task = EnrichmentTask(
            archetype_id=arch_id,
            name=arch.get('name', arch_id),
            system_prefix=prefix,
            system_code=system_code,
            current_score=completeness['score'],
            current_tier=completeness['tier'],
            missing_fields=missing,
            priority_rank=get_priority_rank(arch_id, system_code),
            enrichment_effort=estimate_effort(missing)
        )
        tasks.append(task)

        # Index by system
        system_key = f"{prefix}:{system_code}" if system_code else prefix
        by_system[system_key].append(arch_id)

        # Index by missing field
        for tier_fields in missing.values():
            for field_name in tier_fields:
                by_field[field_name].append(arch_id)

    # Sort tasks by priority rank, then by score (lowest first)
    tasks.sort(key=lambda t: (t.priority_rank, t.current_score))

    # Convert to serializable format
    by_priority = [asdict(t) for t in tasks]

    # Generate summary
    summary = {
        'tier_counts': dict(tier_counts),
        'needing_enrichment': len(tasks),
        'by_effort': {
            'low': sum(1 for t in tasks if t.enrichment_effort == 'low'),
            'medium': sum(1 for t in tasks if t.enrichment_effort == 'medium'),
            'high': sum(1 for t in tasks if t.enrichment_effort == 'high'),
        },
        'top_missing_fields': sorted(
            [(f, len(ids)) for f, ids in by_field.items()],
            key=lambda x: -x[1]
        )[:10],
        'priority_systems': [
            {
                'name': name,
                'prefix': prefix,
                'code': code,
                'count': len([t for t in tasks if t.system_prefix == prefix and (code is None or t.system_code == code)])
            }
            for prefix, code, name in PRIORITY_SYSTEMS
        ]
    }

    return EnrichmentQueue(
        generated_at=datetime.now().isoformat(),
        total_archetypes=len(acp.archetypes),
        total_needing_enrichment=len(tasks),
        by_priority=by_priority,
        by_system=dict(by_system),
        by_missing_field=dict(by_field),
        summary=summary
    )


def main():
    print("=" * 70)
    print("ENRICHMENT QUEUE GENERATOR")
    print("=" * 70)

    # Load ACP data
    acp = ACPLoader('ACP')
    print(f"\nLoaded {len(acp.archetypes)} archetypes")

    # Generate queue
    queue = generate_queue(acp)

    # Print summary
    print(f"\n{'='*40}")
    print("SUMMARY")
    print("="*40)
    print(f"Total archetypes:        {queue.total_archetypes}")
    print(f"Needing enrichment:      {queue.total_needing_enrichment}")
    print(f"Already complete:        {queue.total_archetypes - queue.total_needing_enrichment}")

    print(f"\n{'='*40}")
    print("BY TIER")
    print("="*40)
    for tier, count in queue.summary['tier_counts'].items():
        pct = count / queue.total_archetypes * 100
        bar = '#' * int(pct / 2)
        print(f"  {tier:10s}: {count:4d} ({pct:5.1f}%) {bar}")

    print(f"\n{'='*40}")
    print("BY EFFORT LEVEL")
    print("="*40)
    for effort, count in queue.summary['by_effort'].items():
        print(f"  {effort:10s}: {count:4d}")

    print(f"\n{'='*40}")
    print("TOP MISSING FIELDS")
    print("="*40)
    for field_name, count in queue.summary['top_missing_fields']:
        pct = count / queue.total_archetypes * 100
        print(f"  {field_name:25s}: {count:4d} ({pct:5.1f}%)")

    print(f"\n{'='*40}")
    print("PRIORITY SYSTEMS")
    print("="*40)
    for sys in queue.summary['priority_systems']:
        if sys['count'] > 0:
            print(f"  {sys['name']:25s}: {sys['count']:3d} entries need enrichment")

    print(f"\n{'='*40}")
    print("TOP 20 PRIORITY ENRICHMENT TARGETS")
    print("="*40)
    for i, task in enumerate(queue.by_priority[:20]):
        missing_summary = []
        for tier, fields in task['missing_fields'].items():
            missing_summary.extend(fields[:2])  # Show first 2 per tier
        missing_str = ', '.join(missing_summary[:4])
        if len(missing_summary) > 4:
            missing_str += '...'
        print(f"  {i+1:2d}. {task['archetype_id']:35s} ({task['current_score']:4.1f}%) [{task['enrichment_effort']}]")
        print(f"      Missing: {missing_str}")

    # Save to file
    output_path = Path('ACP/tools/enrichment_queue.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(asdict(queue), f, indent=2, default=str)

    print(f"\n[Saved queue to {output_path}]")

    # Also save a compact version for quick reference
    compact_path = Path('ACP/tools/enrichment_priority.json')
    compact = {
        'generated_at': queue.generated_at,
        'priority_order': [
            {
                'id': t['archetype_id'],
                'name': t['name'],
                'score': t['current_score'],
                'tier': t['current_tier'],
                'effort': t['enrichment_effort'],
                'missing': sum(len(f) for f in t['missing_fields'].values())
            }
            for t in queue.by_priority[:100]  # Top 100
        ],
        'by_field_count': dict(queue.summary['top_missing_fields'])
    }
    with open(compact_path, 'w', encoding='utf-8') as f:
        json.dump(compact, f, indent=2)

    print(f"[Saved compact priority list to {compact_path}]")


if __name__ == '__main__':
    main()
