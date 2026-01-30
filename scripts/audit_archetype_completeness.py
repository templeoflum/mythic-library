#!/usr/bin/env python3
"""
Audit archetype completeness against Universal Schema v2.

Outputs:
- Per-entry completeness scores
- Missing fields by entry
- System-level summaries
- Priority enrichment list
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from integration.acp_loader import ACPLoader

# Field definitions by tier
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

ALL_FIELDS = {**REQUIRED_FIELDS, **TIER_1_FIELDS, **TIER_2_FIELDS, **TIER_3_FIELDS, **TIER_4_FIELDS}


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
        for field, desc in field_dict.items():
            if field in archetype and archetype[field]:
                # Check if it's not empty
                val = archetype[field]
                if isinstance(val, (list, dict)) and len(val) == 0:
                    result[tier_key]['missing'].append(field)
                else:
                    result[tier_key]['present'].append(field)
            else:
                result[tier_key]['missing'].append(field)

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

    # Determine tier
    if result['score'] >= 80:
        result['tier'] = 'complete'
    elif result['score'] >= 60:
        result['tier'] = 'rich'
    elif result['score'] >= 40:
        result['tier'] = 'partial'
    else:
        result['tier'] = 'stub'

    return result


def audit_relationships(archetypes: dict) -> dict:
    """Check relationship bidirectionality and coverage."""
    issues = {
        'missing_bidirectional': [],
        'orphan_targets': [],
        'no_relationships': [],
    }

    bidirectional_types = {'POLAR_OPPOSITE', 'COMPLEMENT', 'CULTURAL_ECHO', 'MIRRORS', 'TENSION', 'ANTAGONIST', 'ALLY'}

    for aid, arch in archetypes.items():
        rels = arch.get('relationships', [])
        if not rels:
            issues['no_relationships'].append(aid)
            continue

        for rel in rels:
            target = rel.get('target', '')
            rel_type = rel.get('type', '')

            # Handle target as list (some entries have array targets)
            if isinstance(target, list):
                targets = target
            else:
                targets = [target] if target else []

            for t in targets:
                if not isinstance(t, str):
                    continue

                # Check if target exists
                if t and t not in archetypes:
                    # Might be a primordial or constellation ref
                    if not t.startswith('primordial:') and not t.startswith('constellation:'):
                        issues['orphan_targets'].append({'source': aid, 'target': t})

                # Check bidirectionality
                if rel_type in bidirectional_types and t in archetypes:
                    target_rels = archetypes[t].get('relationships', [])
                    has_reverse = any(
                        (r.get('target') == aid or aid in (r.get('target') if isinstance(r.get('target'), list) else []))
                        and r.get('type') == rel_type
                        for r in target_rels
                    )
                    if not has_reverse:
                        issues['missing_bidirectional'].append({
                            'source': aid,
                            'target': t,
                            'type': rel_type
                        })

    return issues


def main():
    print("=" * 70)
    print("ARCHETYPE COMPLETENESS AUDIT - Universal Schema v2")
    print("=" * 70)

    # Load data
    acp = ACPLoader('ACP')
    archetypes = acp.archetypes

    print(f"\nTotal archetypes: {len(archetypes)}")

    # Calculate completeness for each
    results = {}
    tier_counts = Counter()
    system_scores = defaultdict(list)

    for aid, arch in archetypes.items():
        result = calculate_completeness(arch)
        results[aid] = result
        tier_counts[result['tier']] += 1

        system = aid.split(':')[0]
        system_scores[system].append(result['score'])

    # Summary by tier
    print("\n" + "=" * 40)
    print("COMPLETENESS TIERS")
    print("=" * 40)
    for tier in ['complete', 'rich', 'partial', 'stub']:
        count = tier_counts[tier]
        pct = count / len(archetypes) * 100
        bar = '#' * int(pct / 2)
        print(f"  {tier:10s}: {count:4d} ({pct:5.1f}%) {bar}")

    # System-level scores
    print("\n" + "=" * 40)
    print("AVERAGE COMPLETENESS BY SYSTEM")
    print("=" * 40)
    system_avgs = {
        sys: sum(scores) / len(scores)
        for sys, scores in system_scores.items()
    }
    for sys, avg in sorted(system_avgs.items(), key=lambda x: -x[1])[:20]:
        bar = '#' * int(avg / 5)
        print(f"  {sys:15s}: {avg:5.1f}% {bar}")

    # Most common missing fields
    print("\n" + "=" * 40)
    print("MOST COMMON MISSING FIELDS")
    print("=" * 40)
    field_missing = Counter()
    for result in results.values():
        for tier in ['required', 'tier1', 'tier2', 'tier3', 'tier4']:
            for field in result[tier]['missing']:
                field_missing[field] += 1

    for field, count in field_missing.most_common(15):
        pct = count / len(archetypes) * 100
        print(f"  {field:25s}: {count:4d} ({pct:5.1f}%)")

    # Relationship audit
    print("\n" + "=" * 40)
    print("RELATIONSHIP AUDIT")
    print("=" * 40)
    rel_issues = audit_relationships(archetypes)
    print(f"  Entries with no relationships: {len(rel_issues['no_relationships'])}")
    print(f"  Missing bidirectional links:   {len(rel_issues['missing_bidirectional'])}")
    print(f"  Orphan targets (bad refs):     {len(rel_issues['orphan_targets'])}")

    # Priority enrichment list (low score, high importance)
    print("\n" + "=" * 40)
    print("PRIORITY ENRICHMENT (stubs in major systems)")
    print("=" * 40)

    priority_systems = ['arch', 'tarot', 'jungian', 'enneagram', 'mbti', 'iching']
    priority_stubs = [
        (aid, results[aid]['score'])
        for aid in archetypes
        if results[aid]['tier'] == 'stub' and aid.split(':')[0] in priority_systems
    ]
    priority_stubs.sort(key=lambda x: x[1])

    print(f"\nLowest scoring entries in priority systems:")
    for aid, score in priority_stubs[:20]:
        missing = results[aid]['tier1']['missing'] + results[aid]['tier2']['missing']
        print(f"  {aid:35s} ({score:4.1f}%) missing: {', '.join(missing[:3])}")

    # Output JSON summary
    summary = {
        'total': len(archetypes),
        'tier_counts': dict(tier_counts),
        'system_averages': system_avgs,
        'field_missing_counts': dict(field_missing),
        'relationship_issues': {
            'no_relationships': len(rel_issues['no_relationships']),
            'missing_bidirectional': len(rel_issues['missing_bidirectional']),
        }
    }

    output_path = Path('ACP/tools/completeness_audit.json')
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\n[Saved summary to {output_path}]")


if __name__ == '__main__':
    main()
