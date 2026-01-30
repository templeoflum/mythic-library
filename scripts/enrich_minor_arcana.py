#!/usr/bin/env python3
"""
Enrich Tarot Minor Arcana with domains, relationships, and Tier 3 fields.

The Minor Arcana has a special nested structure (suits[].cards[]) that
requires specialized handling.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Suit to domain and element mapping
SUIT_DATA = {
    'wands': {
        'element': 'EL-FIRE',
        'domains': ['fire', 'creation', 'will', 'passion', 'enterprise', 'action'],
        'narrative_base': ['hero', 'creator'],
    },
    'cups': {
        'element': 'EL-WATER',
        'domains': ['water', 'love', 'emotion', 'intuition', 'relationships'],
        'narrative_base': ['lover', 'healer'],
    },
    'swords': {
        'element': 'EL-AIR',
        'domains': ['air', 'truth', 'conflict', 'intellect', 'communication'],
        'narrative_base': ['warrior', 'sage'],
    },
    'pentacles': {
        'element': 'EL-EARTH',
        'domains': ['earth', 'wealth', 'crafts', 'material', 'prosperity'],
        'narrative_base': ['sovereign', 'caregiver'],
    }
}

# Number meanings and core functions
NUMBER_DATA = {
    1: {
        'theme': 'pure potential and new beginnings',
        'core_function': 'To embody the pure potential of {element} energy at its inception',
        'symbolic_core': 'The seed of {element} awaiting manifestation',
        'narrative_roles': ['herald', 'creator'],
    },
    2: {
        'theme': 'duality, choice, and balance',
        'core_function': 'To navigate the choice between opposing {element} expressions',
        'symbolic_core': 'The crossroads of {element} where paths diverge',
        'narrative_roles': ['seeker', 'shapeshifter'],
    },
    3: {
        'theme': 'expansion, growth, and collaboration',
        'core_function': 'To expand {element} energy through growth and collaboration',
        'symbolic_core': 'The fruit of {element} beginning to ripen',
        'narrative_roles': ['ally', 'creator'],
    },
    4: {
        'theme': 'stability, foundation, and structure',
        'core_function': 'To establish stable foundation in the realm of {element}',
        'symbolic_core': 'The fortress of {element} offering security',
        'narrative_roles': ['sovereign', 'guardian'],
    },
    5: {
        'theme': 'conflict, challenge, and disruption',
        'core_function': 'To confront the challenges inherent in {element} expression',
        'symbolic_core': 'The storm of {element} that tests and purifies',
        'narrative_roles': ['warrior', 'shadow'],
    },
    6: {
        'theme': 'harmony, healing, and exchange',
        'core_function': 'To restore harmony and facilitate exchange in {element} matters',
        'symbolic_core': 'The balance point where {element} energy flows freely',
        'narrative_roles': ['healer', 'ally'],
    },
    7: {
        'theme': 'assessment, challenge, and perseverance',
        'core_function': 'To assess progress and persevere through {element} challenges',
        'symbolic_core': 'The threshold where {element} mastery is tested',
        'narrative_roles': ['warrior', 'threshold-guardian'],
    },
    8: {
        'theme': 'movement, power, and momentum',
        'core_function': 'To channel the momentum of {element} toward completion',
        'symbolic_core': 'The swift current of {element} gaining force',
        'narrative_roles': ['hero', 'magician'],
    },
    9: {
        'theme': 'culmination, near-completion, and solitude',
        'core_function': 'To approach the culmination of {element} mastery',
        'symbolic_core': 'The peak of {element} journey before final transformation',
        'narrative_roles': ['sage', 'seeker'],
    },
    10: {
        'theme': 'completion, fulfillment, and endings',
        'core_function': 'To embody the full manifestation and completion of {element} energy',
        'symbolic_core': 'The harvest of {element} in its fullest expression',
        'narrative_roles': ['sovereign', 'destroyer'],
    },
}

# Court card data
COURT_DATA = {
    'page': {
        'theme': 'student, messenger, and emerging energy',
        'core_function': 'To embody the youthful, curious exploration of {element}',
        'symbolic_core': 'The apprentice discovering the ways of {element}',
        'narrative_roles': ['innocent', 'herald', 'seeker'],
        'psych': {
            'jungianStructure': 'Puer/Puella, playful engagement with element',
            'developmentalStage': 'Beginning to develop elemental skills',
            'integrationTask': 'Learning without losing enthusiasm'
        }
    },
    'knight': {
        'theme': 'action, pursuit, and extremity',
        'core_function': 'To pursue {element} goals with passionate intensity',
        'symbolic_core': 'The warrior charging forth with {element} energy',
        'narrative_roles': ['hero', 'warrior', 'seeker'],
        'psych': {
            'jungianStructure': 'Active animus, single-minded pursuit',
            'developmentalStage': 'Adolescent intensity and idealism',
            'integrationTask': 'Channeling passion without burning out'
        }
    },
    'queen': {
        'theme': 'receptive mastery and nurturing authority',
        'core_function': 'To nurture and embody mature {element} wisdom receptively',
        'symbolic_core': 'The throne of {element} power held with grace',
        'narrative_roles': ['sovereign', 'caregiver', 'sage'],
        'psych': {
            'jungianStructure': 'Positive anima, receptive mastery',
            'developmentalStage': 'Mature integration of elemental qualities',
            'integrationTask': 'Nurturing without possessing'
        }
    },
    'king': {
        'theme': 'active mastery and commanding authority',
        'core_function': 'To command and direct {element} energy with mature authority',
        'symbolic_core': 'The crown of {element} mastery earned through experience',
        'narrative_roles': ['sovereign', 'mentor', 'ruler'],
        'psych': {
            'jungianStructure': 'Positive senex, wise authority',
            'developmentalStage': 'Full mastery and responsibility',
            'integrationTask': 'Leading without dominating'
        }
    }
}

# Element display names
ELEMENT_NAMES = {
    'wands': 'fire',
    'cups': 'water',
    'swords': 'air',
    'pentacles': 'earth'
}


def enrich_card(card: dict, suit_id: str) -> dict:
    """Enrich a single minor arcana card."""
    enriched = dict(card)
    suit_name = suit_id.split(':')[-1] if ':' in suit_id else suit_id
    element_name = ELEMENT_NAMES.get(suit_name, suit_name)
    suit_info = SUIT_DATA.get(suit_name, {})

    card_name = card.get('name', '')
    card_number = card.get('number', 0)

    # Determine if it's a court card
    is_court = any(court in card_name.lower() for court in ['page', 'knight', 'queen', 'king'])
    court_type = None
    if is_court:
        for ct in ['page', 'knight', 'queen', 'king']:
            if ct in card_name.lower():
                court_type = ct
                break

    # Add domains if missing
    if not enriched.get('domains'):
        base_domains = list(suit_info.get('domains', []))[:4]
        if is_court and court_type:
            # Add court-specific domains
            court_domains = {
                'page': ['learning', 'messages', 'youth'],
                'knight': ['action', 'journey', 'intensity'],
                'queen': ['nurturing', 'mastery', 'wisdom'],
                'king': ['authority', 'mastery', 'leadership']
            }
            base_domains.extend(court_domains.get(court_type, [])[:2])
        elif card_number:
            # Add number-specific domains
            number_domains = {
                1: ['beginnings', 'potential'],
                5: ['conflict', 'challenge'],
                10: ['completion', 'culmination']
            }
            if card_number in number_domains:
                base_domains.extend(number_domains[card_number])
        enriched['domains'] = base_domains[:6]

    # Add correspondences
    if not enriched.get('correspondences'):
        enriched['correspondences'] = {
            'element': suit_info.get('element', ''),
            'suit': f"tarot:{suit_name}"
        }

    # Add relationships
    if not enriched.get('relationships'):
        rels = []
        # Relationship to suit
        rels.append({
            'type': 'CONTAINED_BY',
            'target': f"tarot:{suit_name}",
            'note': 'Part of suit'
        })
        # Relationship to element
        rels.append({
            'type': 'CULTURAL_ECHO',
            'target': f"element:{element_name}",
            'fidelity': 0.8,
            'note': 'Elemental correspondence'
        })
        enriched['relationships'] = rels

    # Add core function
    if not enriched.get('coreFunction'):
        if is_court and court_type:
            cf = COURT_DATA[court_type]['core_function'].format(element=element_name)
        elif card_number and card_number in NUMBER_DATA:
            cf = NUMBER_DATA[card_number]['core_function'].format(element=element_name)
        else:
            cf = f"To express {element_name} energy in the context of {card_name.lower()}"
        enriched['coreFunction'] = cf

    # Add symbolic core
    if not enriched.get('symbolicCore'):
        if is_court and court_type:
            sc = COURT_DATA[court_type]['symbolic_core'].format(element=element_name)
        elif card_number and card_number in NUMBER_DATA:
            sc = NUMBER_DATA[card_number]['symbolic_core'].format(element=element_name)
        else:
            sc = f"The expression of {element_name} through {card_name}"
        enriched['symbolicCore'] = sc

    # Add narrative roles
    if not enriched.get('narrativeRoles'):
        base_roles = list(suit_info.get('narrative_base', []))
        if is_court and court_type:
            base_roles.extend(COURT_DATA[court_type]['narrative_roles'])
        elif card_number and card_number in NUMBER_DATA:
            base_roles.extend(NUMBER_DATA[card_number]['narrative_roles'])
        # Dedupe while preserving order
        seen = set()
        roles = []
        for r in base_roles:
            if r not in seen:
                seen.add(r)
                roles.append(r)
        enriched['narrativeRoles'] = roles[:5]

    # Add psychological mapping
    if not enriched.get('psychologicalMapping'):
        if is_court and court_type:
            psych = dict(COURT_DATA[court_type]['psych'])
            psych['cognitiveBias'] = f'Identification with {element_name} expression'
        else:
            psych = {
                'jungianStructure': f'{element_name.capitalize()} function expression',
                'developmentalStage': NUMBER_DATA.get(card_number, {}).get('theme', 'Energy manifestation'),
                'integrationTask': f'Balancing {element_name} energy appropriately',
                'cognitiveBias': f'Over-identification with {element_name} qualities'
            }
        enriched['psychologicalMapping'] = psych

    return enriched


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Enrich Tarot Minor Arcana')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Show what would be changed without modifying files')
    parser.add_argument('--apply', action='store_true',
                        help='Actually apply the changes')
    args = parser.parse_args()

    dry_run = not args.apply

    print("=" * 70)
    print("TAROT MINOR ARCANA ENRICHMENT")
    print("=" * 70)
    if dry_run:
        print("\n[DRY RUN - No files will be modified. Use --apply to save changes.]\n")

    file_path = Path('ACP/divination/tarot/minor_arcana.jsonld')

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_enriched = 0

    for suit in data.get('suits', []):
        suit_id = suit.get('@id', '')
        suit_name = suit.get('name', '')
        print(f"\nProcessing {suit_name}...")

        new_cards = []
        for card in suit.get('cards', []):
            enriched = enrich_card(card, suit_id)
            card_id = card.get('@id', '')

            # Check what changed
            added = []
            for field in ['domains', 'correspondences', 'relationships', 'coreFunction',
                         'symbolicCore', 'narrativeRoles', 'psychologicalMapping']:
                if field in enriched and field not in card:
                    added.append(field)

            if added:
                total_enriched += 1
                if total_enriched <= 5 or len(added) > 3:
                    print(f"  {card_id}: +{', '.join(added[:3])}{'...' if len(added) > 3 else ''}")

            new_cards.append(enriched)

        suit['cards'] = new_cards

    print(f"\n{'='*40}")
    print(f"Total cards enriched: {total_enriched}")

    if not dry_run:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n[Changes saved to {file_path}]")
    else:
        print("\n[DRY RUN complete. Run with --apply to save changes.]")


if __name__ == '__main__':
    main()
