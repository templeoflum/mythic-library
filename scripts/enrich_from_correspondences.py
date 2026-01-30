#!/usr/bin/env python3
"""
Enrich archetypes using data from correspondences.jsonld.

This script:
1. Parses correspondences.jsonld for tarot, planet, element, chakra mappings
2. Reverse-populates correspondences into archetype entries
3. Creates bidirectional culturalEchoes from greekEchoes data
4. Extracts domains and keywords from descriptions
5. Applies provenance framework (TRAD/SYNC/SCHOL/ORIG)

Target: Automatically enrich 200+ entries with Tier 1 and Tier 2 fields.
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from integration.acp_loader import ACPLoader

# Controlled domain vocabulary
DOMAIN_VOCABULARY = {
    # Core elemental/spatial
    'death', 'rebirth', 'underworld', 'sky', 'sea', 'earth', 'fire', 'water', 'air',
    'light', 'darkness', 'moon', 'sun', 'stars', 'storms', 'thunder', 'lightning',
    'mountains', 'forests', 'rivers', 'wilderness', 'nature',
    # War and conflict
    'war', 'peace', 'battle', 'victory', 'strategy', 'conquest',
    # Love and relationships
    'love', 'beauty', 'desire', 'pleasure', 'sexuality', 'fertility', 'marriage',
    'family', 'motherhood', 'fatherhood', 'childhood', 'home', 'hearth',
    'women', 'men', 'youth', 'fidelity', 'childbirth',
    # Agriculture and nature
    'harvest', 'agriculture', 'hunt', 'hunting', 'animals', 'horses',
    # Knowledge and arts
    'wisdom', 'knowledge', 'learning', 'prophecy', 'truth', 'dreams', 'vision',
    'crafts', 'smithing', 'forge', 'artisans', 'technology',
    'music', 'poetry', 'dance', 'theatre', 'arts',
    'language', 'writing', 'stories', 'eloquence',
    # Commerce and travel
    'threshold', 'boundaries', 'travel', 'roads', 'journeys',
    'commerce', 'trade', 'merchants', 'wealth', 'prosperity',
    'communication', 'messages',
    # Law and order
    'justice', 'law', 'order', 'chaos', 'fate', 'destiny',
    'sovereignty', 'kingship', 'rulership', 'authority',
    'oaths', 'hospitality', 'contracts',
    # Time and memory
    'time', 'memory', 'ancestors', 'past', 'future', 'eternity', 'cycles',
    # Transformation and liminality
    'transformation', 'initiation', 'sacrifice', 'death-rebirth',
    'ecstasy', 'madness', 'intoxication', 'wine', 'liberation',
    # Protection and guidance
    'protection', 'guardian', 'defense', 'shelter',
    'healing', 'medicine', 'health', 'cure',
    'guidance', 'souls', 'afterlife',
    # Creation and destruction
    'creation', 'destruction', 'preservation', 'maintenance',
    # Other common domains
    'thieves', 'trickery', 'cunning', 'deception',
    'heroes', 'civilization', 'culture', 'community',
    'archery', 'plague', 'navigation',
    'depth', 'shadows', 'hidden',
}

# Domain extraction patterns (description text -> domains)
DOMAIN_PATTERNS = {
    r'\b(death|dying|mortality|underworld|afterlife)\b': 'death',
    r'\b(rebirth|resurrection|renewal|reborn)\b': 'rebirth',
    r'\b(underworld|hades|hell|netherworld|realm of dead)\b': 'underworld',
    r'\b(sky|heaven|celestial|clouds|atmosphere)\b': 'sky',
    r'\b(sea|ocean|water|waves|maritime|naval)\b': 'sea',
    r'\b(earth|ground|soil|terrestrial|land)\b': 'earth',
    r'\b(fire|flame|burning|volcanic|solar)\b': 'fire',
    r'\b(water|rain|river|lake|fluid)\b': 'water',
    r'\b(air|wind|breath|atmosphere|storms)\b': 'air',
    r'\b(war|battle|combat|military|warrior|martial)\b': 'war',
    r'\b(peace|harmony|tranquility|reconciliation)\b': 'peace',
    r'\b(love|romance|passion|desire|erotic|affection)\b': 'love',
    r'\b(fertility|fecundity|abundance|pregnancy|childbirth)\b': 'fertility',
    r'\b(harvest|agriculture|crops|farming|grain)\b': 'harvest',
    r'\b(hunt|hunting|hunter|prey|chase)\b': 'hunt',
    r'\b(wisdom|wise|knowledge|intelligence|insight)\b': 'wisdom',
    r'\b(crafts|artisan|smith|forge|metalwork|craft)\b': 'crafts',
    r'\b(healing|medicine|health|cure|restoration)\b': 'healing',
    r'\b(prophecy|oracle|divination|foresight|seer)\b': 'prophecy',
    r'\b(music|song|melody|harmony|instrument)\b': 'music',
    r'\b(poetry|verse|bard|poetic|hymn)\b': 'poetry',
    r'\b(dance|dancing|movement|rhythm)\b': 'dance',
    r'\b(threshold|doorway|gateway|transition|liminal)\b': 'threshold',
    r'\b(boundaries|borders|limits|demarcation)\b': 'boundaries',
    r'\b(travel|journey|wandering|voyage|road)\b': 'travel',
    r'\b(commerce|trade|merchant|market|exchange)\b': 'commerce',
    r'\b(communication|messenger|message|herald)\b': 'communication',
    r'\b(justice|law|judgment|fairness|tribunal)\b': 'justice',
    r'\b(order|structure|organization|hierarchy)\b': 'order',
    r'\b(chaos|disorder|entropy|confusion)\b': 'chaos',
    r'\b(fate|destiny|fortune|doom|predetermined)\b': 'fate',
    r'\b(time|temporal|chronos|age|season)\b': 'time',
    r'\b(memory|remembrance|recollection|ancestral)\b': 'memory',
    r'\b(home|hearth|domestic|household|dwelling)\b': 'home',
    r'\b(family|kinship|clan|lineage|blood)\b': 'family',
    r'\b(marriage|wedding|union|spouse|matrimony)\b': 'marriage',
    r'\b(mother|maternal|motherhood|nurturing)\b': 'motherhood',
    r'\b(father|paternal|fatherhood|patriarch)\b': 'fatherhood',
    r'\b(child|children|childhood|youth|innocent)\b': 'childhood',
    r'\b(transformation|metamorphosis|change|transmutation)\b': 'transformation',
    r'\b(initiation|rite|passage|ceremony)\b': 'initiation',
    r'\b(sacrifice|offering|immolation|martyr)\b': 'sacrifice',
    r'\b(ecstasy|rapture|frenzy|intoxication)\b': 'ecstasy',
    r'\b(madness|insanity|frenzy|possession)\b': 'madness',
    r'\b(sovereignty|king|queen|ruler|reign|throne)\b': 'sovereignty',
    r'\b(protection|guardian|defender|shield)\b': 'protection',
    r'\b(destruction|ruin|annihilation|devastation)\b': 'destruction',
    r'\b(creation|creator|genesis|origin|birth)\b': 'creation',
    r'\b(preservation|maintain|conserve|protect|keeper)\b': 'preservation',
}

# Narrative role vocabulary
NARRATIVE_ROLES = {
    'hero', 'mentor', 'threshold-guardian', 'herald', 'shapeshifter',
    'shadow', 'trickster', 'ally', 'lover', 'sovereign', 'sage',
    'innocent', 'orphan', 'caregiver', 'seeker', 'creator', 'destroyer',
    'ruler', 'magician', 'warrior', 'outcast', 'rebel'
}

# Primordial to narrative role mapping
PRIMORDIAL_TO_ROLES = {
    'primordial:hero': ['hero', 'warrior', 'seeker'],
    'primordial:mentor': ['mentor', 'sage', 'caregiver'],
    'primordial:trickster': ['trickster', 'shapeshifter', 'herald'],
    'primordial:shadow': ['shadow', 'antagonist'],
    'primordial:lover': ['lover', 'ally'],
    'primordial:sovereign': ['sovereign', 'ruler'],
    'primordial:magician': ['magician', 'shapeshifter'],
    'primordial:warrior': ['warrior', 'hero', 'threshold-guardian'],
    'primordial:wise-elder': ['sage', 'mentor'],
    'primordial:great-mother': ['caregiver', 'creator'],
    'primordial:great-father': ['sovereign', 'ruler'],
    'primordial:divine-child': ['innocent', 'hero'],
    'primordial:maiden': ['innocent', 'seeker'],
    'primordial:crone': ['sage', 'destroyer'],
    'primordial:psychopomp': ['threshold-guardian', 'herald'],
    'primordial:healer': ['healer', 'caregiver'],
    'primordial:rebel': ['rebel', 'outcast'],
    'primordial:outcast': ['outcast', 'orphan'],
    'primordial:creator': ['creator'],
    'primordial:destroyer': ['destroyer'],
    'primordial:preserver': ['caregiver', 'sovereign'],
    'primordial:self': ['seeker'],
}


@dataclass
class CorrespondenceData:
    """Extracted correspondence mappings."""
    tarot_to_greek: Dict[str, List[str]] = field(default_factory=dict)
    greek_to_tarot: Dict[str, List[str]] = field(default_factory=dict)
    planet_to_greek: Dict[str, str] = field(default_factory=dict)
    greek_to_planet: Dict[str, str] = field(default_factory=dict)
    chakra_to_greek: Dict[str, List[str]] = field(default_factory=dict)
    greek_to_chakra: Dict[str, str] = field(default_factory=dict)
    element_to_zodiac: Dict[str, List[str]] = field(default_factory=dict)
    tarot_primordials: Dict[str, List[str]] = field(default_factory=dict)
    tarot_keywords: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class EnrichmentResult:
    """Result of enrichment operation."""
    archetype_id: str
    fields_added: List[str]
    fields_updated: List[str]
    errors: List[str]


def load_correspondences(acp_path: Path) -> CorrespondenceData:
    """Parse correspondences.jsonld and extract mapping data."""
    corr_path = acp_path / "schema" / "correspondences.jsonld"
    with open(corr_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    result = CorrespondenceData()

    for item in data.get('@graph', []):
        item_id = item.get('@id', '')

        # Tarot Major Arcana
        if item_id == 'corr:tarot':
            for member in item.get('members', []):
                tarot_id = member.get('@id', '')
                greek_echoes = member.get('greekEchoes', [])
                primordial_links = member.get('archetypalLinks', [])
                keywords = member.get('keywords', [])

                if tarot_id and greek_echoes:
                    result.tarot_to_greek[tarot_id] = greek_echoes
                    for greek_id in greek_echoes:
                        result.greek_to_tarot.setdefault(greek_id, []).append(tarot_id)

                if tarot_id and primordial_links:
                    result.tarot_primordials[tarot_id] = primordial_links

                if tarot_id and keywords:
                    result.tarot_keywords[tarot_id] = keywords

                # Planet correspondences from tarot
                if 'planet' in member:
                    planet_id = member['planet']
                    # We'll use this later for cross-reference

        # Chakra system
        elif item_id == 'corr:chakras':
            for member in item.get('members', []):
                chakra_id = member.get('@id', '')
                greek_echoes = member.get('greekEchoes', [])

                if chakra_id and greek_echoes:
                    result.chakra_to_greek[chakra_id] = greek_echoes
                    for greek_id in greek_echoes:
                        result.greek_to_chakra[greek_id] = chakra_id

        # Classical planets
        elif item_id == 'corr:planets':
            for member in item.get('members', []):
                planet_id = member.get('@id', '')
                greek_deity = member.get('greekDeity', '')

                if planet_id and greek_deity:
                    result.planet_to_greek[planet_id] = greek_deity
                    result.greek_to_planet[greek_deity] = planet_id

        # Classical elements
        elif item_id == 'corr:elements':
            for member in item.get('members', []):
                element_id = member.get('@id', '')
                zodiac_triplicity = member.get('zodiacTriplicity', [])

                if element_id and zodiac_triplicity:
                    result.element_to_zodiac[element_id] = zodiac_triplicity

    return result


def extract_domains(description: str, existing_domains: List[str] = None) -> List[str]:
    """Extract domains from description text using pattern matching."""
    if not description:
        return existing_domains or []

    domains = set(existing_domains or [])
    text = description.lower()

    for pattern, domain in DOMAIN_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            domains.add(domain)

    # Limit to 8 domains max, prioritizing existing ones
    result = list(domains)
    if len(result) > 8:
        existing = set(existing_domains or [])
        result = sorted(result, key=lambda d: (d not in existing, d))[:8]

    return sorted(result)


def extract_keywords(archetype: dict, domains: List[str]) -> List[str]:
    """Generate keywords from name, description, and domains."""
    keywords = set()

    # From name
    name = archetype.get('name', '')
    if name:
        # Add name as keyword (lowercase)
        keywords.add(name.lower())
        # Add name parts
        for part in re.split(r'[\s\-_]+', name.lower()):
            if len(part) >= 3:
                keywords.add(part)

    # From description
    description = archetype.get('description', '')
    if description:
        # Extract significant words (nouns, adjectives)
        words = re.findall(r'\b[a-z]{4,}\b', description.lower())
        # Filter common words
        stopwords = {'this', 'that', 'with', 'from', 'have', 'been', 'were', 'their',
                     'which', 'when', 'where', 'what', 'being', 'other', 'about',
                     'into', 'over', 'such', 'most', 'some', 'than', 'them', 'also'}
        keywords.update(w for w in words if w not in stopwords)

    # From domains
    keywords.update(domains)

    # From primordials
    for inst in archetype.get('instantiates', []):
        prim = inst.get('primordial', '')
        if prim.startswith('primordial:'):
            keywords.add(prim.split(':')[1].replace('-', ' '))

    # Limit and sort
    result = sorted(keywords)[:10]
    return result


def derive_narrative_roles(archetype: dict) -> List[str]:
    """Derive narrative roles from primordial instantiations."""
    roles = set()

    for inst in archetype.get('instantiates', []):
        prim = inst.get('primordial', '')
        weight = inst.get('weight', 0.5)

        if prim in PRIMORDIAL_TO_ROLES and weight >= 0.4:
            # Add roles proportional to weight
            prim_roles = PRIMORDIAL_TO_ROLES[prim]
            if weight >= 0.7:
                roles.update(prim_roles[:2])
            else:
                roles.add(prim_roles[0])

    return sorted(roles)[:5]


def build_correspondences(archetype_id: str, corr_data: CorrespondenceData,
                          existing: dict = None) -> dict:
    """Build correspondences object for an archetype."""
    result = dict(existing or {})

    # Tarot correspondences
    if archetype_id in corr_data.greek_to_tarot:
        result['tarot'] = corr_data.greek_to_tarot[archetype_id]

    # Planet correspondences
    if archetype_id in corr_data.greek_to_planet:
        result['planet'] = corr_data.greek_to_planet[archetype_id]

    # Chakra correspondences
    if archetype_id in corr_data.greek_to_chakra:
        result['chakra'] = corr_data.greek_to_chakra[archetype_id]

    return result if result else None


def build_cultural_echoes(archetype_id: str, corr_data: CorrespondenceData,
                          existing: List[dict] = None) -> List[dict]:
    """Build culturalEchoes array from correspondence data."""
    echoes = {e.get('target'): e for e in (existing or [])}

    # From tarot correspondences (Greek deity <-> Tarot card)
    if archetype_id in corr_data.greek_to_tarot:
        for tarot_id in corr_data.greek_to_tarot[archetype_id]:
            if tarot_id not in echoes:
                echoes[tarot_id] = {
                    'target': f"tarot:{tarot_id}",
                    'fidelity': 0.65,
                    'sharedAspects': ['archetypal function'],
                    'provenance': {
                        'type': 'SYNC',
                        'confidence': 0.65,
                        'note': 'Golden Dawn / Jungian tarot-archetype mapping'
                    }
                }

    return list(echoes.values()) if echoes else None


def enrich_archetype(archetype: dict, archetype_id: str,
                     corr_data: CorrespondenceData) -> Tuple[dict, EnrichmentResult]:
    """Enrich a single archetype entry."""
    result = EnrichmentResult(
        archetype_id=archetype_id,
        fields_added=[],
        fields_updated=[],
        errors=[]
    )

    enriched = dict(archetype)

    # 1. Extract/enhance domains
    existing_domains = archetype.get('domains', [])
    description = archetype.get('description', '')
    new_domains = extract_domains(description, existing_domains)

    if new_domains and new_domains != existing_domains:
        enriched['domains'] = new_domains
        if existing_domains:
            result.fields_updated.append('domains')
        else:
            result.fields_added.append('domains')

    # 2. Generate keywords
    existing_keywords = archetype.get('keywords', [])
    if not existing_keywords or len(existing_keywords) < 3:
        new_keywords = extract_keywords(enriched, new_domains)
        if new_keywords:
            enriched['keywords'] = new_keywords
            if existing_keywords:
                result.fields_updated.append('keywords')
            else:
                result.fields_added.append('keywords')

    # 3. Build correspondences
    existing_corr = archetype.get('correspondences', {})
    new_corr = build_correspondences(archetype_id, corr_data, existing_corr)
    if new_corr and new_corr != existing_corr:
        enriched['correspondences'] = new_corr
        if existing_corr:
            result.fields_updated.append('correspondences')
        else:
            result.fields_added.append('correspondences')

    # 4. Build cultural echoes
    existing_echoes = archetype.get('culturalEchoes', [])
    new_echoes = build_cultural_echoes(archetype_id, corr_data, existing_echoes)
    if new_echoes and new_echoes != existing_echoes:
        enriched['culturalEchoes'] = new_echoes
        if existing_echoes:
            result.fields_updated.append('culturalEchoes')
        else:
            result.fields_added.append('culturalEchoes')

    # 5. Derive narrative roles if missing
    existing_roles = archetype.get('narrativeRoles', [])
    if not existing_roles:
        new_roles = derive_narrative_roles(archetype)
        if new_roles:
            enriched['narrativeRoles'] = new_roles
            result.fields_added.append('narrativeRoles')

    return enriched, result


def load_archetype_file(file_path: Path) -> Tuple[dict, List[dict]]:
    """Load a JSON-LD file and return (full_data, entries_list)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    entries = data.get('entries', [])
    return data, entries


def save_archetype_file(file_path: Path, data: dict, entries: List[dict]):
    """Save updated entries back to JSON-LD file."""
    data['entries'] = entries
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def process_file(file_path: Path, corr_data: CorrespondenceData,
                 dry_run: bool = True) -> List[EnrichmentResult]:
    """Process a single archetype file."""
    results = []

    try:
        data, entries = load_archetype_file(file_path)
    except (json.JSONDecodeError, IOError) as e:
        print(f"  Error loading {file_path}: {e}")
        return results

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

        enriched, result = enrich_archetype(entry, entry_id, corr_data)

        if result.fields_added or result.fields_updated:
            results.append(result)
            modified = True
            new_entries.append(enriched)
        else:
            new_entries.append(entry)

    if modified and not dry_run:
        save_archetype_file(file_path, data, new_entries)

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Enrich archetypes from correspondences')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Show what would be changed without modifying files')
    parser.add_argument('--apply', action='store_true',
                        help='Actually apply the changes')
    parser.add_argument('--system', type=str, default=None,
                        help='Only process specific system (e.g., "greek", "tarot")')
    args = parser.parse_args()

    dry_run = not args.apply

    print("=" * 70)
    print("ARCHETYPE ENRICHMENT FROM CORRESPONDENCES")
    print("=" * 70)
    if dry_run:
        print("\n[DRY RUN - No files will be modified. Use --apply to save changes.]\n")

    acp_path = Path('ACP')

    # Load correspondence data
    print("Loading correspondences.jsonld...")
    corr_data = load_correspondences(acp_path)

    print(f"  Tarot->Greek mappings: {len(corr_data.tarot_to_greek)}")
    print(f"  Greek->Tarot mappings: {len(corr_data.greek_to_tarot)}")
    print(f"  Planet->Greek mappings: {len(corr_data.planet_to_greek)}")
    print(f"  Chakra->Greek mappings: {len(corr_data.chakra_to_greek)}")

    # Find all archetype files
    all_results: List[EnrichmentResult] = []
    domains_to_process = ['archetypes', 'divination', 'psychology', 'modern']

    for domain in domains_to_process:
        domain_path = acp_path / domain
        if not domain_path.exists():
            continue

        for jsonld_file in sorted(domain_path.rglob('*.jsonld')):
            # Filter by system if specified
            if args.system and args.system.lower() not in str(jsonld_file).lower():
                continue

            rel_path = jsonld_file.relative_to(acp_path)
            print(f"\nProcessing {rel_path}...")

            results = process_file(jsonld_file, corr_data, dry_run=dry_run)
            all_results.extend(results)

            if results:
                for r in results[:3]:  # Show first 3 per file
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

    # Summary
    print("\n" + "=" * 70)
    print("ENRICHMENT SUMMARY")
    print("=" * 70)

    total_modified = len(all_results)
    fields_added_count = defaultdict(int)
    fields_updated_count = defaultdict(int)

    for r in all_results:
        for f in r.fields_added:
            fields_added_count[f] += 1
        for f in r.fields_updated:
            fields_updated_count[f] += 1

    print(f"\nTotal archetypes enriched: {total_modified}")
    print("\nFields added:")
    for field_name, count in sorted(fields_added_count.items(), key=lambda x: -x[1]):
        print(f"  {field_name:25s}: {count:4d}")

    print("\nFields updated:")
    for field_name, count in sorted(fields_updated_count.items(), key=lambda x: -x[1]):
        print(f"  {field_name:25s}: {count:4d}")

    if dry_run:
        print("\n[DRY RUN complete. Run with --apply to save changes.]")
    else:
        print(f"\n[Changes saved to {total_modified} entries.]")


if __name__ == '__main__':
    main()
