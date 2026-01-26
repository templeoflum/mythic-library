# ACP Calibration System

**Status**: ✓ COMPLETE (v1.0)

The calibration system establishes the coordinate reference frame for all archetypes. It defines the mathematical scaffolding that all 302 archetypes in the system reference.

## Structure

```
calibration/
├── origin.jsonld          # The center point (0.5 on all 8 axes)
├── poles/                 # 16 theoretical extremes
│   ├── order.jsonld       # (0.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
│   ├── chaos.jsonld       # (1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
│   ├── creation.jsonld
│   ├── destruction.jsonld
│   ├── light.jsonld
│   ├── shadow.jsonld
│   ├── active.jsonld
│   ├── receptive.jsonld
│   ├── individual.jsonld
│   ├── collective.jsonld
│   ├── ascent.jsonld
│   ├── descent.jsonld
│   ├── stasis.jsonld
│   ├── transformation.jsonld
│   ├── voluntary.jsonld
│   └── fated.jsonld
├── validate.js            # Validation script
└── README.md              # This file
```

## The "Tuning Fork" Concept

The calibration points act like a tuning fork for the entire system:

1. **Origin** - The undifferentiated center where all polarities meet
2. **16 Poles** - The theoretical extremes that no real archetype fully occupies
3. **Reference Frame** - Any archetype can be positioned relative to these known points

## Mathematical Properties

- **Origin**: Equidistant (0.5) from all poles
- **Polar Pairs**: Exactly 1.0 apart on their defining axis
- **All Poles**: Have 7 axes at 0.5, one axis at 0.0 or 1.0

## Usage

### Running Validation

```bash
node calibration/validate.js
```

Expected output:
```
=== ACP Calibration Validation ===

Checking origin...
  ✓ Origin valid

Checking poles...
  ✓ Pure Order
  ✓ Pure Chaos
  ... (all 16 poles)

Checking polar pairs...
  ✓ Pure Order ↔ Pure Chaos
  ... (all 8 pairs)

Checking distances from origin...
  ✓ Pure Order: 0.5000
  ... (all 16 poles)

=== Summary ===
✓ All validation checks passed!
```

### Positioning a New Archetype

When adding a new archetype, use the calibration points as reference:

1. **Which pole is it nearest to?** (e.g., Zeus is near Ascent + Order + Active)
2. **How far from that pole?** (0.0-0.5 range from the pole)
3. **Calculate coordinates** based on relative positions

Example thought process for Zeus:
- Near Ascent pole (low ascent-descent) → 0.15
- Moderate order (not extreme) → 0.25
- Active/projective → 0.25
- Other axes near center → 0.4-0.6

## v1.0 Status

All calibration steps complete:

- [x] **Origin validated** - Center point at (0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
- [x] **16 Poles defined** - All axis extremes positioned
- [x] **22 Primordials anchored** - Meta-archetypes on calibrated grid (see `PRIMORDIAL_MAP.md`)
- [x] **302 Archetypes positioned** - All using calibration reference frame
- [x] **Geodesics defined** - Transformation paths between primordials

## Validation

Run validation using the browser-based validator:
```bash
cd ACP
python -m http.server 8000
# Open http://localhost:8000/tools/validator.html
```

Or use Node.js (if available):
```bash
node tools/validate.js
```
