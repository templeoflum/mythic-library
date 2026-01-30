#!/usr/bin/env python3
"""
Validate archetype enrichment quality and completeness.

This script provides:
1. Pre/post validation for enrichment batches
2. Schema compliance checking
3. Coordinate validity verification
4. Relationship bidirectionality audit
5. Completeness tier change reporting

Use before and after enrichment to track improvements.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
import math

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from integration.acp_loader import ACPLoader

# Schema definitions
REQUIRED_AXES = [
    "order-chaos", "creation-destruction", "light-shadow", "active-receptive",
    "individual-collective", "ascent-descent", "stasis-transformation", "voluntary-fated"
]

TIER_FIELDS = {
    'required': ['description', 'spectralCoordinates', 'instantiates'],
    'tier1': ['keywords', 'domains', 'relationships'],
    'tier2': ['correspondences', 'culturalEchoes', 'aliases'],
    'tier3': ['narrativeRoles', 'psychologicalMapping', 'coreFunction', 'symbolicCore'],
    'tier4': ['storyFunctions', 'elementalComposition'],
}

BIDIRECTIONAL_RELATIONSHIP_TYPES = {
    'POLAR_OPPOSITE', 'COMPLEMENT', 'CULTURAL_ECHO', 'MIRRORS', 'TENSION', 'ANTAGONIST', 'ALLY'
}

VALID_DOMAINS = {
    # Core elemental/spatial
    'death', 'rebirth', 'underworld', 'sky', 'sea', 'earth', 'fire', 'water', 'air',
    'light', 'darkness', 'moon', 'sun', 'stars', 'storms', 'thunder', 'lightning',
    'mountains', 'forests', 'rivers', 'wilderness', 'nature',
    # War and conflict
    'war', 'peace', 'battle', 'victory', 'strategy', 'conquest',
    # Love and relationships
    'love', 'beauty', 'desire', 'pleasure', 'sexuality', 'fertility', 'marriage',
    'family', 'motherhood', 'fatherhood', 'childhood', 'home', 'hearth',
    'women', 'men', 'young women', 'youth', 'fidelity', 'childbirth',
    # Agriculture and nature
    'harvest', 'agriculture', 'hunt', 'hunting', 'animals', 'horses',
    # Knowledge and arts
    'wisdom', 'knowledge', 'learning', 'prophecy', 'truth', 'dreams', 'vision',
    'crafts', 'smithing', 'forge', 'artisans', 'technology',
    'music', 'poetry', 'dance', 'theatre', 'arts',
    'language', 'writing', 'stories', 'eloquence',
    # Commerce and travel
    'threshold', 'boundaries', 'travel', 'travelers', 'roads', 'journeys',
    'commerce', 'trade', 'merchants', 'wealth', 'hidden wealth', 'prosperity',
    'communication', 'messages', 'messengers',
    # Law and order
    'justice', 'law', 'order', 'chaos', 'fate', 'destiny',
    'sovereignty', 'kingship', 'rulership', 'authority',
    'oaths', 'hospitality', 'contracts', 'agreements',
    # Time and memory
    'time', 'memory', 'ancestors', 'past', 'future', 'eternity', 'cycles',
    # Transformation and liminality
    'transformation', 'initiation', 'sacrifice', 'death-rebirth',
    'ecstasy', 'madness', 'intoxication', 'wine', 'liberation',
    # Protection and guidance
    'protection', 'guardian', 'defense', 'shelter',
    'healing', 'medicine', 'health', 'cure',
    'guidance', 'souls', 'psychopomp', 'afterlife',
    # Creation and destruction
    'creation', 'destruction', 'preservation', 'maintenance',
    # Other common domains
    'thieves', 'trickery', 'cunning', 'deception',
    'heroes', 'civilization', 'culture', 'community',
    'archery', 'plague', 'earthquakes', 'navigation',
    'sacred fire', 'center', 'stability', 'virginity',
    'depth', 'the unconscious', 'shadows', 'hidden',
    'just warfare', 'defense',
}

VALID_NARRATIVE_ROLES = {
    'hero', 'mentor', 'threshold-guardian', 'herald', 'shapeshifter',
    'shadow', 'trickster', 'ally', 'lover', 'sovereign', 'sage',
    'innocent', 'orphan', 'caregiver', 'seeker', 'creator', 'destroyer',
    'ruler', 'magician', 'warrior', 'outcast', 'rebel', 'antagonist',
    'father', 'mother', 'child', 'judge', 'protector', 'healer',
    'philanderer', 'messenger', 'guide'
}


@dataclass
class ValidationIssue:
    """A single validation issue."""
    archetype_id: str
    severity: str  # error, warning, info
    category: str  # coordinates, relationships, schema, domain, etc.
    message: str
    field: str = ''


@dataclass
class ValidationReport:
    """Complete validation report."""
    timestamp: str
    total_archetypes: int
    issues: List[ValidationIssue]
    tier_distribution: Dict[str, int]
    completeness_stats: Dict[str, float]
    relationship_stats: Dict[str, int]


def calculate_completeness_score(archetype: dict) -> Tuple[float, str, Dict[str, List[str]]]:
    """Calculate completeness score, tier, and missing fields."""
    missing = defaultdict(list)

    def check_field(field_name, tier_key):
        if field_name not in archetype or not archetype[field_name]:
            missing[tier_key].append(field_name)
            return False
        val = archetype[field_name]
        if isinstance(val, (list, dict)) and len(val) == 0:
            missing[tier_key].append(field_name)
            return False
        return True

    # Count present fields
    required_present = sum(1 for f in TIER_FIELDS['required'] if check_field(f, 'required'))
    tier1_present = sum(1 for f in TIER_FIELDS['tier1'] if check_field(f, 'tier1'))
    tier2_present = sum(1 for f in TIER_FIELDS['tier2'] if check_field(f, 'tier2'))
    tier3_present = sum(1 for f in TIER_FIELDS['tier3'] if check_field(f, 'tier3'))
    tier4_present = sum(1 for f in TIER_FIELDS['tier4'] if check_field(f, 'tier4'))

    # Weighted score calculation
    score = (
        required_present / len(TIER_FIELDS['required']) * 30 +
        tier1_present / len(TIER_FIELDS['tier1']) * 25 +
        tier2_present / len(TIER_FIELDS['tier2']) * 20 +
        tier3_present / len(TIER_FIELDS['tier3']) * 15 +
        tier4_present / len(TIER_FIELDS['tier4']) * 10
    )

    # Determine tier
    if score >= 80:
        tier = 'complete'
    elif score >= 60:
        tier = 'rich'
    elif score >= 40:
        tier = 'partial'
    else:
        tier = 'stub'

    return score, tier, dict(missing)


def validate_coordinates(archetype: dict, archetype_id: str) -> List[ValidationIssue]:
    """Validate spectral coordinates."""
    issues = []
    coords = archetype.get('spectralCoordinates', {})

    if not coords:
        issues.append(ValidationIssue(
            archetype_id=archetype_id,
            severity='error',
            category='coordinates',
            message='Missing spectralCoordinates',
            field='spectralCoordinates'
        ))
        return issues

    # Check all 8 axes present
    for axis in REQUIRED_AXES:
        if axis not in coords:
            issues.append(ValidationIssue(
                archetype_id=archetype_id,
                severity='error',
                category='coordinates',
                message=f'Missing axis: {axis}',
                field='spectralCoordinates'
            ))
        else:
            val = coords[axis]
            if not isinstance(val, (int, float)):
                issues.append(ValidationIssue(
                    archetype_id=archetype_id,
                    severity='error',
                    category='coordinates',
                    message=f'Invalid coordinate type for {axis}: {type(val).__name__}',
                    field='spectralCoordinates'
                ))
            elif val < 0.0 or val > 1.0:
                issues.append(ValidationIssue(
                    archetype_id=archetype_id,
                    severity='error',
                    category='coordinates',
                    message=f'Coordinate out of range for {axis}: {val}',
                    field='spectralCoordinates'
                ))

    return issues


def validate_instantiates(archetype: dict, archetype_id: str,
                          valid_primordials: Set[str]) -> List[ValidationIssue]:
    """Validate primordial instantiations."""
    issues = []
    instantiates = archetype.get('instantiates', [])

    if not instantiates:
        issues.append(ValidationIssue(
            archetype_id=archetype_id,
            severity='error',
            category='schema',
            message='Missing instantiates array (must have at least 1 primordial)',
            field='instantiates'
        ))
        return issues

    for i, inst in enumerate(instantiates):
        prim = inst.get('primordial', '')
        weight = inst.get('weight', None)

        if not prim:
            issues.append(ValidationIssue(
                archetype_id=archetype_id,
                severity='error',
                category='schema',
                message=f'instantiates[{i}] missing primordial reference',
                field='instantiates'
            ))
        elif prim not in valid_primordials:
            issues.append(ValidationIssue(
                archetype_id=archetype_id,
                severity='warning',
                category='schema',
                message=f'Unknown primordial: {prim}',
                field='instantiates'
            ))

        if weight is None:
            issues.append(ValidationIssue(
                archetype_id=archetype_id,
                severity='warning',
                category='schema',
                message=f'instantiates[{i}] missing weight',
                field='instantiates'
            ))
        elif not isinstance(weight, (int, float)) or weight < 0.0 or weight > 1.0:
            issues.append(ValidationIssue(
                archetype_id=archetype_id,
                severity='error',
                category='schema',
                message=f'Invalid weight for {prim}: {weight}',
                field='instantiates'
            ))

    return issues


def validate_domains(archetype: dict, archetype_id: str) -> List[ValidationIssue]:
    """Validate domain vocabulary."""
    issues = []
    domains = archetype.get('domains', [])

    if not domains:
        return issues  # Not required, just validate if present

    for domain in domains:
        if domain.lower() not in VALID_DOMAINS:
            issues.append(ValidationIssue(
                archetype_id=archetype_id,
                severity='warning',
                category='domain',
                message=f'Unknown domain: {domain}',
                field='domains'
            ))

    if len(domains) > 10:
        issues.append(ValidationIssue(
            archetype_id=archetype_id,
            severity='warning',
            category='domain',
            message=f'Too many domains ({len(domains)}), recommend 3-8',
            field='domains'
        ))

    return issues


def validate_narrative_roles(archetype: dict, archetype_id: str) -> List[ValidationIssue]:
    """Validate narrative role vocabulary."""
    issues = []
    roles = archetype.get('narrativeRoles', [])

    if not roles:
        return issues  # Not required

    for role in roles:
        if role.lower() not in VALID_NARRATIVE_ROLES:
            issues.append(ValidationIssue(
                archetype_id=archetype_id,
                severity='info',
                category='narrative',
                message=f'Non-standard narrative role: {role}',
                field='narrativeRoles'
            ))

    return issues


def validate_relationships(archetypes: Dict[str, dict]) -> Tuple[List[ValidationIssue], Dict[str, int]]:
    """Validate relationship integrity and bidirectionality."""
    issues = []
    stats = {
        'total_relationships': 0,
        'missing_bidirectional': 0,
        'orphan_targets': 0,
        'no_relationships': 0,
    }

    for arch_id, arch in archetypes.items():
        rels = arch.get('relationships', [])

        if not rels:
            stats['no_relationships'] += 1
            continue

        stats['total_relationships'] += len(rels)

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
                # Check target exists
                if t and not t.startswith('primordial:') and not t.startswith('constellation:'):
                    if t not in archetypes:
                        stats['orphan_targets'] += 1
                        issues.append(ValidationIssue(
                            archetype_id=arch_id,
                            severity='warning',
                            category='relationship',
                            message=f'Orphan target: {t}',
                            field='relationships'
                        ))

                    # Check bidirectionality for symmetric types
                    if rel_type in BIDIRECTIONAL_RELATIONSHIP_TYPES and t in archetypes:
                        target_rels = archetypes[t].get('relationships', [])
                        has_reverse = any(
                            (r.get('target') == arch_id or arch_id in (r.get('target') if isinstance(r.get('target'), list) else [r.get('target')]))
                            and r.get('type') == rel_type
                            for r in target_rels
                        )
                        if not has_reverse:
                            stats['missing_bidirectional'] += 1
                            issues.append(ValidationIssue(
                                archetype_id=arch_id,
                                severity='warning',
                                category='relationship',
                                message=f'Missing reverse {rel_type} from {t}',
                                field='relationships'
                            ))

            # Validate POLAR_OPPOSITE has axis
            if rel_type == 'POLAR_OPPOSITE' and 'axis' not in rel:
                issues.append(ValidationIssue(
                    archetype_id=arch_id,
                    severity='warning',
                    category='relationship',
                    message=f'POLAR_OPPOSITE missing axis field',
                    field='relationships'
                ))

            # Validate CULTURAL_ECHO has fidelity
            if rel_type == 'CULTURAL_ECHO' and 'fidelity' not in rel:
                issues.append(ValidationIssue(
                    archetype_id=arch_id,
                    severity='info',
                    category='relationship',
                    message=f'CULTURAL_ECHO missing fidelity score',
                    field='relationships'
                ))

    return issues, stats


def check_coordinate_collisions(archetypes: Dict[str, dict],
                                threshold: float = 0.05) -> List[ValidationIssue]:
    """Check for coordinate collisions (archetypes too close together)."""
    issues = []
    coords_list = []

    for arch_id, arch in archetypes.items():
        coords = arch.get('spectralCoordinates', {})
        if len(coords) == 8:
            vec = tuple(coords.get(axis, 0.5) for axis in REQUIRED_AXES)
            coords_list.append((arch_id, vec))

    # Check pairwise distances (this is O(n^2) but n is manageable)
    for i, (id1, vec1) in enumerate(coords_list):
        for id2, vec2 in coords_list[i+1:]:
            dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))
            if dist < threshold:
                issues.append(ValidationIssue(
                    archetype_id=id1,
                    severity='warning',
                    category='collision',
                    message=f'Coordinate collision with {id2} (distance: {dist:.4f})',
                    field='spectralCoordinates'
                ))

    return issues


def run_validation(acp: ACPLoader, check_collisions: bool = False) -> ValidationReport:
    """Run full validation suite."""
    from datetime import datetime

    issues: List[ValidationIssue] = []
    tier_counts = Counter()
    scores = []

    # Get valid primordial IDs
    valid_primordials = set(acp.primordials.keys())

    # Validate each archetype
    for arch_id, arch in acp.archetypes.items():
        # Calculate completeness
        score, tier, missing = calculate_completeness_score(arch)
        tier_counts[tier] += 1
        scores.append(score)

        # Coordinate validation
        issues.extend(validate_coordinates(arch, arch_id))

        # Instantiates validation
        issues.extend(validate_instantiates(arch, arch_id, valid_primordials))

        # Domain validation
        issues.extend(validate_domains(arch, arch_id))

        # Narrative roles validation
        issues.extend(validate_narrative_roles(arch, arch_id))

    # Relationship validation (needs full archetype dict)
    rel_issues, rel_stats = validate_relationships(acp.archetypes)
    issues.extend(rel_issues)

    # Coordinate collision check (expensive)
    if check_collisions:
        issues.extend(check_coordinate_collisions(acp.archetypes))

    # Calculate stats
    completeness_stats = {
        'mean_score': sum(scores) / len(scores) if scores else 0,
        'min_score': min(scores) if scores else 0,
        'max_score': max(scores) if scores else 0,
        'median_score': sorted(scores)[len(scores) // 2] if scores else 0,
    }

    return ValidationReport(
        timestamp=datetime.now().isoformat(),
        total_archetypes=len(acp.archetypes),
        issues=issues,
        tier_distribution=dict(tier_counts),
        completeness_stats=completeness_stats,
        relationship_stats=rel_stats
    )


def compare_reports(before: ValidationReport, after: ValidationReport) -> dict:
    """Compare two validation reports to show improvements."""
    comparison = {
        'archetypes_changed': after.total_archetypes - before.total_archetypes,
        'tier_changes': {},
        'completeness_improvement': {
            'mean': after.completeness_stats['mean_score'] - before.completeness_stats['mean_score'],
            'min': after.completeness_stats['min_score'] - before.completeness_stats['min_score'],
            'max': after.completeness_stats['max_score'] - before.completeness_stats['max_score'],
        },
        'issues_resolved': len(before.issues) - len(after.issues),
    }

    # Tier changes
    for tier in ['complete', 'rich', 'partial', 'stub']:
        before_count = before.tier_distribution.get(tier, 0)
        after_count = after.tier_distribution.get(tier, 0)
        comparison['tier_changes'][tier] = after_count - before_count

    return comparison


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Validate archetype enrichment')
    parser.add_argument('--collisions', action='store_true',
                        help='Check for coordinate collisions (slow)')
    parser.add_argument('--save', type=str, default=None,
                        help='Save report to JSON file')
    parser.add_argument('--compare', type=str, default=None,
                        help='Compare with previous report JSON')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show all issues (default: errors and warnings only)')
    args = parser.parse_args()

    print("=" * 70)
    print("ARCHETYPE ENRICHMENT VALIDATION")
    print("=" * 70)

    # Load ACP data
    acp = ACPLoader('ACP')
    print(f"\nLoaded {len(acp.archetypes)} archetypes, {len(acp.primordials)} primordials")

    # Run validation
    print("\nRunning validation...")
    report = run_validation(acp, check_collisions=args.collisions)

    # Print summary
    print(f"\n{'='*40}")
    print("COMPLETENESS DISTRIBUTION")
    print("="*40)
    for tier in ['complete', 'rich', 'partial', 'stub']:
        count = report.tier_distribution.get(tier, 0)
        pct = count / report.total_archetypes * 100
        bar = '#' * int(pct / 2)
        print(f"  {tier:10s}: {count:4d} ({pct:5.1f}%) {bar}")

    print(f"\n{'='*40}")
    print("COMPLETENESS SCORES")
    print("="*40)
    print(f"  Mean:   {report.completeness_stats['mean_score']:5.1f}%")
    print(f"  Median: {report.completeness_stats['median_score']:5.1f}%")
    print(f"  Min:    {report.completeness_stats['min_score']:5.1f}%")
    print(f"  Max:    {report.completeness_stats['max_score']:5.1f}%")

    print(f"\n{'='*40}")
    print("RELATIONSHIP STATS")
    print("="*40)
    print(f"  Total relationships:     {report.relationship_stats['total_relationships']}")
    print(f"  Entries with none:       {report.relationship_stats['no_relationships']}")
    print(f"  Missing bidirectional:   {report.relationship_stats['missing_bidirectional']}")
    print(f"  Orphan targets:          {report.relationship_stats['orphan_targets']}")

    # Issue summary
    print(f"\n{'='*40}")
    print("VALIDATION ISSUES")
    print("="*40)
    by_severity = Counter(i.severity for i in report.issues)
    by_category = Counter(i.category for i in report.issues)

    print("\nBy severity:")
    for sev in ['error', 'warning', 'info']:
        count = by_severity.get(sev, 0)
        print(f"  {sev:10s}: {count:4d}")

    print("\nBy category:")
    for cat, count in by_category.most_common():
        print(f"  {cat:15s}: {count:4d}")

    # Show issues
    if args.verbose:
        severities = ['error', 'warning', 'info']
    else:
        severities = ['error', 'warning']

    filtered_issues = [i for i in report.issues if i.severity in severities]
    if filtered_issues:
        print(f"\n{'='*40}")
        print(f"ISSUES ({len(filtered_issues)} shown)")
        print("="*40)
        for issue in filtered_issues[:50]:  # Limit output
            icon = {'error': 'ERR', 'warning': 'WRN', 'info': 'INF'}[issue.severity]
            print(f"  [{icon}] {issue.archetype_id}: {issue.message}")
        if len(filtered_issues) > 50:
            print(f"  ... and {len(filtered_issues) - 50} more")

    # Compare with previous report
    if args.compare:
        compare_path = Path(args.compare)
        if compare_path.exists():
            with open(compare_path) as f:
                before_data = json.load(f)
            before = ValidationReport(**before_data)
            comparison = compare_reports(before, report)

            print(f"\n{'='*40}")
            print("COMPARISON WITH PREVIOUS REPORT")
            print("="*40)
            print(f"  Mean score change: {comparison['completeness_improvement']['mean']:+.1f}%")
            print(f"  Issues resolved:   {comparison['issues_resolved']}")
            print("\n  Tier changes:")
            for tier, change in comparison['tier_changes'].items():
                if change != 0:
                    print(f"    {tier:10s}: {change:+4d}")

    # Save report
    if args.save:
        output_path = Path(args.save)
        report_dict = {
            'timestamp': report.timestamp,
            'total_archetypes': report.total_archetypes,
            'tier_distribution': report.tier_distribution,
            'completeness_stats': report.completeness_stats,
            'relationship_stats': report.relationship_stats,
            'issue_count': len(report.issues),
            'issues_by_severity': dict(by_severity),
            'issues_by_category': dict(by_category),
        }
        with open(output_path, 'w') as f:
            json.dump(report_dict, f, indent=2)
        print(f"\n[Saved report to {output_path}]")


if __name__ == '__main__':
    main()
