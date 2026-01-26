#!/usr/bin/env node
/**
 * ACP Calibration Validation Script
 *
 * Validates that the calibration system is mathematically coherent:
 * - Origin is at (0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
 * - All poles are at correct positions
 * - Polar opposites have distance = 1.0 on their axis
 * - All poles are equidistant from origin (0.5)
 */

const fs = require('fs');
const path = require('path');

const AXES = [
  'order-chaos',
  'creation-destruction',
  'light-shadow',
  'active-receptive',
  'individual-collective',
  'ascent-descent',
  'stasis-transformation',
  'voluntary-fated'
];

function loadJsonld(filepath) {
  const content = fs.readFileSync(filepath, 'utf8');
  return JSON.parse(content);
}

function euclideanDistance(coords1, coords2) {
  let sum = 0;
  for (const axis of AXES) {
    const diff = coords1[axis] - coords2[axis];
    sum += diff * diff;
  }
  return Math.sqrt(sum);
}

function distanceOnAxis(coords1, coords2, axis) {
  return Math.abs(coords1[axis] - coords2[axis]);
}

function validateOrigin(origin) {
  const errors = [];
  const coords = origin.spectralCoordinates;

  for (const axis of AXES) {
    if (coords[axis] !== 0.5) {
      errors.push(`Origin ${axis} should be 0.5, got ${coords[axis]}`);
    }
  }

  return errors;
}

function validatePole(pole, expectedAxis, expectedValue) {
  const errors = [];
  const coords = pole.spectralCoordinates;

  // Check the defining axis
  if (coords[expectedAxis] !== expectedValue) {
    errors.push(`${pole.name}: ${expectedAxis} should be ${expectedValue}, got ${coords[expectedAxis]}`);
  }

  // Check all other axes are 0.5
  for (const axis of AXES) {
    if (axis !== expectedAxis && coords[axis] !== 0.5) {
      errors.push(`${pole.name}: ${axis} should be 0.5, got ${coords[axis]}`);
    }
  }

  return errors;
}

function validatePolarPair(pole1, pole2, axis) {
  const errors = [];
  const dist = distanceOnAxis(pole1.spectralCoordinates, pole2.spectralCoordinates, axis);

  if (dist !== 1.0) {
    errors.push(`Polar pair ${pole1.name}/${pole2.name}: distance on ${axis} should be 1.0, got ${dist}`);
  }

  return errors;
}

function main() {
  const calibrationDir = __dirname;
  const polesDir = path.join(calibrationDir, 'poles');

  console.log('=== ACP Calibration Validation ===\n');

  let allErrors = [];

  // Validate origin
  console.log('Checking origin...');
  const origin = loadJsonld(path.join(calibrationDir, 'origin.jsonld'));
  const originErrors = validateOrigin(origin);
  allErrors = allErrors.concat(originErrors);
  console.log(originErrors.length === 0 ? '  ✓ Origin valid' : `  ✗ ${originErrors.length} errors`);

  // Define expected poles
  const poleDefinitions = [
    { file: 'order.jsonld', axis: 'order-chaos', value: 0.0, opposite: 'chaos.jsonld' },
    { file: 'chaos.jsonld', axis: 'order-chaos', value: 1.0, opposite: 'order.jsonld' },
    { file: 'creation.jsonld', axis: 'creation-destruction', value: 0.0, opposite: 'destruction.jsonld' },
    { file: 'destruction.jsonld', axis: 'creation-destruction', value: 1.0, opposite: 'creation.jsonld' },
    { file: 'light.jsonld', axis: 'light-shadow', value: 0.0, opposite: 'shadow.jsonld' },
    { file: 'shadow.jsonld', axis: 'light-shadow', value: 1.0, opposite: 'light.jsonld' },
    { file: 'active.jsonld', axis: 'active-receptive', value: 0.0, opposite: 'receptive.jsonld' },
    { file: 'receptive.jsonld', axis: 'active-receptive', value: 1.0, opposite: 'active.jsonld' },
    { file: 'individual.jsonld', axis: 'individual-collective', value: 0.0, opposite: 'collective.jsonld' },
    { file: 'collective.jsonld', axis: 'individual-collective', value: 1.0, opposite: 'individual.jsonld' },
    { file: 'ascent.jsonld', axis: 'ascent-descent', value: 0.0, opposite: 'descent.jsonld' },
    { file: 'descent.jsonld', axis: 'ascent-descent', value: 1.0, opposite: 'ascent.jsonld' },
    { file: 'stasis.jsonld', axis: 'stasis-transformation', value: 0.0, opposite: 'transformation.jsonld' },
    { file: 'transformation.jsonld', axis: 'stasis-transformation', value: 1.0, opposite: 'stasis.jsonld' },
    { file: 'voluntary.jsonld', axis: 'voluntary-fated', value: 0.0, opposite: 'fated.jsonld' },
    { file: 'fated.jsonld', axis: 'voluntary-fated', value: 1.0, opposite: 'voluntary.jsonld' },
  ];

  // Load all poles
  const poles = {};
  console.log('\nChecking poles...');
  for (const def of poleDefinitions) {
    const pole = loadJsonld(path.join(polesDir, def.file));
    poles[def.file] = pole;

    const errors = validatePole(pole, def.axis, def.value);
    allErrors = allErrors.concat(errors);
    console.log(errors.length === 0 ? `  ✓ ${pole.name}` : `  ✗ ${pole.name}: ${errors.length} errors`);
  }

  // Validate polar pairs
  console.log('\nChecking polar pairs...');
  const checkedPairs = new Set();
  for (const def of poleDefinitions) {
    const pairKey = [def.file, def.opposite].sort().join('|');
    if (!checkedPairs.has(pairKey)) {
      checkedPairs.add(pairKey);
      const errors = validatePolarPair(poles[def.file], poles[def.opposite], def.axis);
      allErrors = allErrors.concat(errors);
      console.log(errors.length === 0
        ? `  ✓ ${poles[def.file].name} ↔ ${poles[def.opposite].name}`
        : `  ✗ ${poles[def.file].name} ↔ ${poles[def.opposite].name}`);
    }
  }

  // Validate distances from origin
  console.log('\nChecking distances from origin...');
  for (const def of poleDefinitions) {
    const pole = poles[def.file];
    const dist = euclideanDistance(origin.spectralCoordinates, pole.spectralCoordinates);
    const expected = 0.5; // Single axis deviation of 0.5 from center
    if (Math.abs(dist - expected) > 0.001) {
      allErrors.push(`${pole.name}: distance from origin should be ${expected}, got ${dist.toFixed(4)}`);
      console.log(`  ✗ ${pole.name}: ${dist.toFixed(4)}`);
    } else {
      console.log(`  ✓ ${pole.name}: ${dist.toFixed(4)}`);
    }
  }

  // Summary
  console.log('\n=== Summary ===');
  if (allErrors.length === 0) {
    console.log('✓ All validation checks passed!');
    console.log(`  - 1 origin point`);
    console.log(`  - 16 poles (8 axes × 2)`);
    console.log(`  - 8 polar pairs validated`);
    process.exit(0);
  } else {
    console.log(`✗ ${allErrors.length} errors found:`);
    for (const err of allErrors) {
      console.log(`  - ${err}`);
    }
    process.exit(1);
  }
}

main();
