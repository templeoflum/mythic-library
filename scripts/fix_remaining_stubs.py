#!/usr/bin/env python3
"""
Fix remaining stubs by adding spectral coordinates.
"""

import json
from pathlib import Path

# Spectral coordinates for astrology houses
HOUSE_COORDINATES = {
    "astrology:house_1": {  # Self, identity, appearance
        "order-chaos": 0.35,
        "creation-destruction": 0.30,
        "light-shadow": 0.25,
        "active-receptive": 0.20,
        "individual-collective": 0.15,
        "ascent-descent": 0.40,
        "stasis-transformation": 0.45,
        "voluntary-fated": 0.35
    },
    "astrology:house_2": {  # Resources, values, possessions
        "order-chaos": 0.25,
        "creation-destruction": 0.25,
        "light-shadow": 0.30,
        "active-receptive": 0.55,
        "individual-collective": 0.25,
        "ascent-descent": 0.65,
        "stasis-transformation": 0.25,
        "voluntary-fated": 0.40
    },
    "astrology:house_3": {  # Communication, siblings, local travel
        "order-chaos": 0.45,
        "creation-destruction": 0.35,
        "light-shadow": 0.30,
        "active-receptive": 0.35,
        "individual-collective": 0.45,
        "ascent-descent": 0.45,
        "stasis-transformation": 0.50,
        "voluntary-fated": 0.40
    },
    "astrology:house_4": {  # Home, family, roots
        "order-chaos": 0.25,
        "creation-destruction": 0.30,
        "light-shadow": 0.45,
        "active-receptive": 0.70,
        "individual-collective": 0.55,
        "ascent-descent": 0.70,
        "stasis-transformation": 0.25,
        "voluntary-fated": 0.55
    },
    "astrology:house_5": {  # Creativity, romance, children
        "order-chaos": 0.55,
        "creation-destruction": 0.20,
        "light-shadow": 0.25,
        "active-receptive": 0.25,
        "individual-collective": 0.30,
        "ascent-descent": 0.40,
        "stasis-transformation": 0.55,
        "voluntary-fated": 0.30
    },
    "astrology:house_6": {  # Health, work, service
        "order-chaos": 0.20,
        "creation-destruction": 0.35,
        "light-shadow": 0.35,
        "active-receptive": 0.55,
        "individual-collective": 0.50,
        "ascent-descent": 0.60,
        "stasis-transformation": 0.35,
        "voluntary-fated": 0.50
    },
    "astrology:house_7": {  # Partnerships, relationships
        "order-chaos": 0.35,
        "creation-destruction": 0.35,
        "light-shadow": 0.30,
        "active-receptive": 0.55,
        "individual-collective": 0.65,
        "ascent-descent": 0.50,
        "stasis-transformation": 0.45,
        "voluntary-fated": 0.55
    },
    "astrology:house_8": {  # Transformation, shared resources, death
        "order-chaos": 0.50,
        "creation-destruction": 0.70,
        "light-shadow": 0.75,
        "active-receptive": 0.60,
        "individual-collective": 0.60,
        "ascent-descent": 0.70,
        "stasis-transformation": 0.80,
        "voluntary-fated": 0.70
    },
    "astrology:house_9": {  # Philosophy, higher learning, travel
        "order-chaos": 0.45,
        "creation-destruction": 0.30,
        "light-shadow": 0.25,
        "active-receptive": 0.35,
        "individual-collective": 0.55,
        "ascent-descent": 0.25,
        "stasis-transformation": 0.50,
        "voluntary-fated": 0.40
    },
    "astrology:house_10": {  # Career, public image, authority
        "order-chaos": 0.15,
        "creation-destruction": 0.30,
        "light-shadow": 0.20,
        "active-receptive": 0.25,
        "individual-collective": 0.70,
        "ascent-descent": 0.20,
        "stasis-transformation": 0.35,
        "voluntary-fated": 0.55
    },
    "astrology:house_11": {  # Friends, groups, hopes
        "order-chaos": 0.55,
        "creation-destruction": 0.30,
        "light-shadow": 0.30,
        "active-receptive": 0.45,
        "individual-collective": 0.80,
        "ascent-descent": 0.35,
        "stasis-transformation": 0.50,
        "voluntary-fated": 0.40
    },
    "astrology:house_12": {  # Unconscious, spirituality, isolation
        "order-chaos": 0.60,
        "creation-destruction": 0.50,
        "light-shadow": 0.85,
        "active-receptive": 0.80,
        "individual-collective": 0.75,
        "ascent-descent": 0.55,
        "stasis-transformation": 0.65,
        "voluntary-fated": 0.80
    },
}

# Greek aspect coordinates
GREEK_ASPECTS = {
    "arch:GR-APHRODITE-ANADYOMENE": {  # Rising from the sea aspect
        "order-chaos": 0.45,
        "creation-destruction": 0.20,
        "light-shadow": 0.25,
        "active-receptive": 0.55,
        "individual-collective": 0.45,
        "ascent-descent": 0.55,
        "stasis-transformation": 0.60,
        "voluntary-fated": 0.50
    },
}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()

    dry_run = not args.apply

    print("=" * 70)
    print("FIXING REMAINING STUBS - Adding Spectral Coordinates")
    print("=" * 70)
    if dry_run:
        print("\n[DRY RUN]\n")

    # Fix astrology houses
    houses_path = Path("ACP/divination/astrology/houses.jsonld")
    with open(houses_path, 'r', encoding='utf-8') as f:
        houses_data = json.load(f)

    houses_fixed = 0
    for entry in houses_data.get("entries", []):
        arch_id = entry.get("@id", "")
        if arch_id in HOUSE_COORDINATES:
            if "spectralCoordinates" not in entry:
                entry["spectralCoordinates"] = HOUSE_COORDINATES[arch_id]
                houses_fixed += 1
                print(f"  Added coordinates to {arch_id}")

    if not dry_run and houses_fixed > 0:
        with open(houses_path, 'w', encoding='utf-8') as f:
            json.dump(houses_data, f, indent=2, ensure_ascii=False)

    # Fix Greek aspects
    greek_path = Path("ACP/archetypes/greek/GR_OLYMPIANS.jsonld")
    with open(greek_path, 'r', encoding='utf-8') as f:
        greek_data = json.load(f)

    greek_fixed = 0
    for entry in greek_data.get("entries", []):
        arch_id = entry.get("@id", "")
        if arch_id in GREEK_ASPECTS:
            if "spectralCoordinates" not in entry:
                entry["spectralCoordinates"] = GREEK_ASPECTS[arch_id]
                greek_fixed += 1
                print(f"  Added coordinates to {arch_id}")

    if not dry_run and greek_fixed > 0:
        with open(greek_path, 'w', encoding='utf-8') as f:
            json.dump(greek_data, f, indent=2, ensure_ascii=False)

    print(f"\nHouses fixed: {houses_fixed}")
    print(f"Greek aspects fixed: {greek_fixed}")

    if dry_run:
        print("\n[DRY RUN - Use --apply to save]")
    else:
        print("\n[Changes saved]")


if __name__ == "__main__":
    main()
