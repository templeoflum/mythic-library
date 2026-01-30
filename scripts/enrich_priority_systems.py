#!/usr/bin/env python3
"""
Enrich priority system archetypes with Tier 3 fields.

This script adds:
- coreFunction: one-line essential purpose derived from description/primordials
- symbolicCore: central metaphor/symbol
- psychologicalMapping: Jungian structure based on primordial instantiation

Priority systems (in order):
1. Greek Olympians - Template system
2. Jungian Core - Psychological foundation
3. Tarot Major Arcana - High correspondence density
4. Tarot Minor Arcana - Currently lowest-scoring
5. Buddhist Pantheon - New, needs enrichment
6. MBTI Types - High user interest
7. Hero's Journey - Narrative foundation
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from integration.acp_loader import ACPLoader

# Primordial to psychological mapping
PRIMORDIAL_PSYCHOLOGY = {
    'primordial:hero': {
        'jungianStructure': 'Ego ideal, active self-assertion',
        'developmentalStage': 'Adolescent individuation, proving oneself',
        'integrationTask': 'Balancing courage with humility and wisdom'
    },
    'primordial:shadow': {
        'jungianStructure': 'Repressed unconscious, rejected aspects of self',
        'developmentalStage': 'Mid-life confrontation with denied potential',
        'integrationTask': 'Acknowledging and integrating rejected qualities'
    },
    'primordial:trickster': {
        'jungianStructure': 'Shadow aspect that disrupts ego rigidity',
        'developmentalStage': 'Any transition point requiring flexibility',
        'integrationTask': 'Accepting uncertainty and embracing creative chaos'
    },
    'primordial:great-mother': {
        'jungianStructure': 'Mother complex, nurturing instinct',
        'developmentalStage': 'Early childhood attachment and security',
        'integrationTask': 'Balancing nurturing with allowing autonomy'
    },
    'primordial:great-father': {
        'jungianStructure': 'Father complex, authority and order',
        'developmentalStage': 'Adolescent relationship with rules and structure',
        'integrationTask': 'Balancing authority with compassion and flexibility'
    },
    'primordial:divine-child': {
        'jungianStructure': 'Self as potential, original wholeness',
        'developmentalStage': 'Beginning of individuation journey',
        'integrationTask': 'Nurturing inner potential while facing reality'
    },
    'primordial:wise-elder': {
        'jungianStructure': 'Senex, accumulated wisdom and meaning',
        'developmentalStage': 'Late life integration and legacy',
        'integrationTask': 'Transmitting wisdom while releasing attachment'
    },
    'primordial:maiden': {
        'jungianStructure': 'Anima in puella form, innocence and potential',
        'developmentalStage': 'Pre-adult openness to experience',
        'integrationTask': 'Maintaining wonder while gaining experience'
    },
    'primordial:crone': {
        'jungianStructure': 'Anima in senex form, wisdom through experience',
        'developmentalStage': 'Post-generative acceptance and insight',
        'integrationTask': 'Sharing hard-won wisdom without bitterness'
    },
    'primordial:lover': {
        'jungianStructure': 'Anima/Animus integration through relationship',
        'developmentalStage': 'Young adult intimacy and connection',
        'integrationTask': 'Balancing desire with genuine connection'
    },
    'primordial:warrior': {
        'jungianStructure': 'Active masculine, disciplined will',
        'developmentalStage': 'Establishing boundaries and competence',
        'integrationTask': 'Channeling aggression into service'
    },
    'primordial:magician': {
        'jungianStructure': 'Transformative function, conscious will',
        'developmentalStage': 'Mastery and skill development',
        'integrationTask': 'Using power responsibly and transparently'
    },
    'primordial:sovereign': {
        'jungianStructure': 'Self as central organizing principle',
        'developmentalStage': 'Mature leadership and responsibility',
        'integrationTask': 'Ruling with justice while remaining humble'
    },
    'primordial:psychopomp': {
        'jungianStructure': 'Guide function between conscious and unconscious',
        'developmentalStage': 'Major life transitions and transformations',
        'integrationTask': 'Facilitating passage while honoring process'
    },
    'primordial:healer': {
        'jungianStructure': 'Compensatory function, restoration of balance',
        'developmentalStage': 'Recovery from crisis or wounding',
        'integrationTask': 'Transforming wounds into sources of healing'
    },
    'primordial:rebel': {
        'jungianStructure': 'Shadow projection onto established order',
        'developmentalStage': 'Adolescent differentiation from parents/culture',
        'integrationTask': 'Channeling rebellion into creative transformation'
    },
    'primordial:creator': {
        'jungianStructure': 'Transcendent function, synthesis of opposites',
        'developmentalStage': 'Generative adult creativity',
        'integrationTask': 'Creating sustainably without exhaustion'
    },
    'primordial:destroyer': {
        'jungianStructure': 'Thanatos, necessary endings for renewal',
        'developmentalStage': 'Letting go of outworn forms',
        'integrationTask': 'Accepting loss as precondition for growth'
    },
    'primordial:preserver': {
        'jungianStructure': 'Ego maintenance, stability function',
        'developmentalStage': 'Middle adult consolidation',
        'integrationTask': 'Preserving what matters while allowing change'
    },
    'primordial:self': {
        'jungianStructure': 'Central archetype of wholeness and integration',
        'developmentalStage': 'Individuation goal, second half of life',
        'integrationTask': 'Achieving conscious relationship with unconscious'
    },
    'primordial:outcast': {
        'jungianStructure': 'Shadow projection, scapegoat dynamic',
        'developmentalStage': 'Alienation from collective, finding unique path',
        'integrationTask': 'Finding belonging while honoring difference'
    },
    'primordial:ancestor': {
        'jungianStructure': 'Collective unconscious inheritance',
        'developmentalStage': 'Late life connection to lineage and legacy',
        'integrationTask': 'Honoring past while living present'
    },
}

# Primordial to symbolic core mapping
PRIMORDIAL_SYMBOLS = {
    'primordial:hero': 'The sword of self-determination',
    'primordial:shadow': 'The mirror that reveals what we hide',
    'primordial:trickster': 'The mask that liberates through deception',
    'primordial:great-mother': 'The nurturing vessel of life',
    'primordial:great-father': 'The staff of authority and judgment',
    'primordial:divine-child': 'The dawn of possibility',
    'primordial:wise-elder': 'The lamp of accumulated wisdom',
    'primordial:maiden': 'The unopened flower of potential',
    'primordial:crone': 'The cauldron of transformation',
    'primordial:lover': 'The rose of passionate connection',
    'primordial:warrior': 'The disciplined blade of focused will',
    'primordial:magician': 'The wand of conscious transformation',
    'primordial:sovereign': 'The crown of rightful authority',
    'primordial:psychopomp': 'The key to threshold passages',
    'primordial:healer': 'The caduceus of restoration',
    'primordial:rebel': 'The fire that burns down the old',
    'primordial:creator': 'The seed of infinite possibility',
    'primordial:destroyer': 'The scythe of necessary endings',
    'primordial:preserver': 'The shield of continuity',
    'primordial:self': 'The mandala of wholeness',
    'primordial:outcast': 'The wanderer without home',
    'primordial:ancestor': 'The root that connects to source',
}


def derive_core_function(archetype: dict) -> str:
    """Derive coreFunction from description and primordials."""
    description = archetype.get('description', '')
    instantiates = archetype.get('instantiates', [])
    name = archetype.get('name', '')

    # If already has coreFunction, keep it
    if archetype.get('coreFunction'):
        return archetype['coreFunction']

    # Build function from highest-weighted primordial
    if instantiates:
        primary = max(instantiates, key=lambda x: x.get('weight', 0))
        prim_name = primary.get('primordial', '').split(':')[-1].replace('-', ' ')
        aspects = primary.get('aspects', [])

        if aspects:
            aspect_str = ' and '.join(aspects[:2])
            return f"To embody {prim_name} energy through {aspect_str}"
        else:
            return f"To manifest the archetypal pattern of the {prim_name}"

    # Fall back to description
    if description:
        # Extract first sentence or key phrase
        first_sentence = description.split('.')[0]
        if len(first_sentence) < 100:
            return f"To embody the essence of {name}: {first_sentence.lower()}"

    return f"To manifest the archetypal pattern of {name}"


def derive_symbolic_core(archetype: dict) -> str:
    """Derive symbolicCore from primordials and domains."""
    instantiates = archetype.get('instantiates', [])
    domains = archetype.get('domains', [])
    name = archetype.get('name', '')

    # If already has symbolicCore, keep it
    if archetype.get('symbolicCore'):
        return archetype['symbolicCore']

    # Use primary primordial's symbol
    if instantiates:
        primary = max(instantiates, key=lambda x: x.get('weight', 0))
        prim = primary.get('primordial', '')
        if prim in PRIMORDIAL_SYMBOLS:
            return PRIMORDIAL_SYMBOLS[prim]

    # Build from domains
    if domains:
        primary_domain = domains[0]
        return f"The {primary_domain} that transforms through {name}'s essence"

    return f"The essential pattern of {name}"


def derive_psychological_mapping(archetype: dict) -> Optional[dict]:
    """Derive psychologicalMapping from primordial instantiation."""
    instantiates = archetype.get('instantiates', [])

    # If already has psychologicalMapping, keep it
    if archetype.get('psychologicalMapping'):
        return archetype['psychologicalMapping']

    if not instantiates:
        return None

    # Use primary primordial's mapping as base
    primary = max(instantiates, key=lambda x: x.get('weight', 0))
    prim = primary.get('primordial', '')

    if prim in PRIMORDIAL_PSYCHOLOGY:
        base = dict(PRIMORDIAL_PSYCHOLOGY[prim])

        # Add cognitive bias based on archetypal pattern
        name = archetype.get('name', '')
        if 'order' in str(archetype.get('domains', [])) or primary.get('weight', 0) > 0.8:
            base['cognitiveBias'] = 'Confirmation bias toward archetypal pattern'
        else:
            base['cognitiveBias'] = 'Projection of shadow elements'

        return base

    return None


@dataclass
class EnrichmentResult:
    archetype_id: str
    fields_added: List[str]
    fields_updated: List[str]


def enrich_archetype(archetype: dict, archetype_id: str) -> Tuple[dict, EnrichmentResult]:
    """Enrich a single archetype with Tier 3 fields."""
    result = EnrichmentResult(
        archetype_id=archetype_id,
        fields_added=[],
        fields_updated=[]
    )

    enriched = dict(archetype)

    # Core function
    existing_cf = archetype.get('coreFunction')
    new_cf = derive_core_function(archetype)
    if new_cf and new_cf != existing_cf:
        enriched['coreFunction'] = new_cf
        if existing_cf:
            result.fields_updated.append('coreFunction')
        else:
            result.fields_added.append('coreFunction')

    # Symbolic core
    existing_sc = archetype.get('symbolicCore')
    new_sc = derive_symbolic_core(archetype)
    if new_sc and new_sc != existing_sc:
        enriched['symbolicCore'] = new_sc
        if existing_sc:
            result.fields_updated.append('symbolicCore')
        else:
            result.fields_added.append('symbolicCore')

    # Psychological mapping
    existing_pm = archetype.get('psychologicalMapping')
    new_pm = derive_psychological_mapping(archetype)
    if new_pm and new_pm != existing_pm:
        enriched['psychologicalMapping'] = new_pm
        if existing_pm:
            result.fields_updated.append('psychologicalMapping')
        else:
            result.fields_added.append('psychologicalMapping')

    return enriched, result


def process_file(file_path: Path, dry_run: bool = True) -> List[EnrichmentResult]:
    """Process a single archetype file."""
    results = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"  Error loading {file_path}: {e}")
        return results

    entries = data.get('entries', [])
    modified = False
    new_entries = []

    for entry in entries:
        entry_id = entry.get('@id', '')
        entry_type = entry.get('@type', '')

        # Skip system definitions
        if entry_type == 'System':
            new_entries.append(entry)
            continue

        # Only process archetypes with spectral coordinates
        if 'spectralCoordinates' not in entry:
            new_entries.append(entry)
            continue

        enriched, result = enrich_archetype(entry, entry_id)

        if result.fields_added or result.fields_updated:
            results.append(result)
            modified = True
            new_entries.append(enriched)
        else:
            new_entries.append(entry)

    if modified and not dry_run:
        data['entries'] = new_entries
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return results


# Priority files to process
PRIORITY_FILES = [
    'ACP/archetypes/greek/GR_OLYMPIANS.jsonld',
    'ACP/psychology/jungian/core_archetypes.jsonld',
    'ACP/divination/tarot/major_arcana.jsonld',
    'ACP/divination/tarot/minor_arcana.jsonld',
    'ACP/archetypes/buddhist/BU_PANTHEON.jsonld',
    'ACP/psychology/personality/mbti.jsonld',
    'ACP/psychology/narrative/heros_journey.jsonld',
    'ACP/psychology/enneagram/types.jsonld',
    'ACP/psychology/narrative/vogler_archetypes.jsonld',
    'ACP/archetypes/norse/NO_AESIR_VANIR.jsonld',
    'ACP/archetypes/egyptian/EG_NETJERU.jsonld',
]


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Enrich priority systems with Tier 3 fields')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Show what would be changed without modifying files')
    parser.add_argument('--apply', action='store_true',
                        help='Actually apply the changes')
    parser.add_argument('--all', action='store_true',
                        help='Process all archetype files, not just priority')
    args = parser.parse_args()

    dry_run = not args.apply

    print("=" * 70)
    print("PRIORITY SYSTEM TIER 3 ENRICHMENT")
    print("=" * 70)
    if dry_run:
        print("\n[DRY RUN - No files will be modified. Use --apply to save changes.]\n")

    all_results: List[EnrichmentResult] = []

    if args.all:
        # Process all archetype files
        acp_path = Path('ACP')
        domains_to_process = ['archetypes', 'divination', 'psychology', 'modern']

        for domain in domains_to_process:
            domain_path = acp_path / domain
            if not domain_path.exists():
                continue

            for jsonld_file in sorted(domain_path.rglob('*.jsonld')):
                rel_path = jsonld_file.relative_to(acp_path)
                print(f"Processing {rel_path}...")
                results = process_file(jsonld_file, dry_run=dry_run)
                all_results.extend(results)

                if results:
                    for r in results[:3]:
                        added = ', '.join(r.fields_added) if r.fields_added else ''
                        updated = ', '.join(r.fields_updated) if r.fields_updated else ''
                        changes = []
                        if added:
                            changes.append(f"+{added}")
                        if updated:
                            changes.append(f"~{updated}")
                        print(f"  {r.archetype_id}: {' '.join(changes)}")
                    if len(results) > 3:
                        print(f"  ... and {len(results) - 3} more")
    else:
        # Process only priority files
        for file_rel_path in PRIORITY_FILES:
            file_path = Path(file_rel_path)
            if not file_path.exists():
                print(f"Warning: {file_rel_path} not found")
                continue

            print(f"\nProcessing {file_rel_path}...")
            results = process_file(file_path, dry_run=dry_run)
            all_results.extend(results)

            for r in results[:5]:
                added = ', '.join(r.fields_added) if r.fields_added else ''
                updated = ', '.join(r.fields_updated) if r.fields_updated else ''
                changes = []
                if added:
                    changes.append(f"+{added}")
                if updated:
                    changes.append(f"~{updated}")
                print(f"  {r.archetype_id}: {' '.join(changes)}")
            if len(results) > 5:
                print(f"  ... and {len(results) - 5} more")

    # Summary
    print("\n" + "=" * 70)
    print("ENRICHMENT SUMMARY")
    print("=" * 70)

    total_modified = len(all_results)
    fields_added = {}
    fields_updated = {}

    for r in all_results:
        for f in r.fields_added:
            fields_added[f] = fields_added.get(f, 0) + 1
        for f in r.fields_updated:
            fields_updated[f] = fields_updated.get(f, 0) + 1

    print(f"\nTotal archetypes enriched: {total_modified}")
    print("\nFields added:")
    for field_name, count in sorted(fields_added.items(), key=lambda x: -x[1]):
        print(f"  {field_name:25s}: {count:4d}")

    if fields_updated:
        print("\nFields updated:")
        for field_name, count in sorted(fields_updated.items(), key=lambda x: -x[1]):
            print(f"  {field_name:25s}: {count:4d}")

    if dry_run:
        print("\n[DRY RUN complete. Run with --apply to save changes.]")
    else:
        print(f"\n[Changes saved to {total_modified} entries.]")


if __name__ == '__main__':
    main()
