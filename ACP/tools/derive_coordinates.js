#!/usr/bin/env node
/**
 * ACP Coordinate Derivation Tool
 *
 * Algorithmically derives spectral coordinates for stub entries based on:
 * 1. Weighted average of instantiated primordials
 * 2. Keyword-based adjustments
 * 3. Collision detection and resolution
 */

const fs = require('fs');
const path = require('path');

// 8 spectral axes
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

// Load primordial positions as coordinate lookup
const PRIMORDIAL_COORDS = {
  'primordial:self':         [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
  'primordial:twin':         [0.5, 0.5, 0.5, 0.5, 0.35, 0.5, 0.5, 0.6],
  'primordial:lover':        [0.5, 0.3, 0.4, 0.5, 0.4, 0.5, 0.5, 0.35],
  'primordial:psychopomp':   [0.5, 0.5, 0.5, 0.4, 0.5, 0.5, 0.65, 0.6],
  'primordial:magician':     [0.5, 0.4, 0.5, 0.3, 0.4, 0.5, 0.7, 0.25],
  'primordial:healer':       [0.35, 0.3, 0.4, 0.55, 0.5, 0.5, 0.55, 0.5],
  'primordial:creator':      [0.3, 0.0, 0.3, 0.2, 0.6, 0.3, 0.6, 0.3],
  'primordial:divine_child': [0.5, 0.15, 0.2, 0.5, 0.4, 0.5, 0.6, 0.7],
  'primordial:maiden':       [0.45, 0.25, 0.25, 0.5, 0.3, 0.45, 0.5, 0.35],
  'primordial:great_mother': [0.35, 0.2, 0.4, 0.7, 0.7, 0.7, 0.4, 0.6],
  'primordial:crone':        [0.5, 0.65, 0.65, 0.6, 0.6, 0.7, 0.6, 0.7],
  'primordial:ancestor':     [0.25, 0.45, 0.5, 0.7, 0.8, 0.65, 0.3, 0.8],
  'primordial:great_father': [0.15, 0.4, 0.3, 0.2, 0.6, 0.2, 0.3, 0.4],
  'primordial:sovereign':    [0.15, 0.35, 0.25, 0.3, 0.6, 0.3, 0.25, 0.5],
  'primordial:wise_elder':   [0.3, 0.4, 0.3, 0.6, 0.6, 0.4, 0.3, 0.6],
  'primordial:preserver':    [0.2, 0.5, 0.3, 0.5, 0.6, 0.5, 0.1, 0.5],
  'primordial:hero':         [0.4, 0.4, 0.25, 0.15, 0.2, 0.4, 0.6, 0.4],
  'primordial:warrior':      [0.4, 0.6, 0.35, 0.1, 0.35, 0.45, 0.5, 0.3],
  'primordial:rebel':        [0.7, 0.55, 0.45, 0.2, 0.35, 0.5, 0.75, 0.1],
  'primordial:trickster':    [0.75, 0.5, 0.5, 0.3, 0.4, 0.5, 0.8, 0.15],
  'primordial:destroyer':    [0.7, 1.0, 0.6, 0.2, 0.7, 0.6, 0.9, 0.6],
  'primordial:monster':      [0.85, 0.7, 0.75, 0.25, 0.2, 0.75, 0.55, 0.65],
  'primordial:shadow':       [0.6, 0.6, 0.9, 0.5, 0.5, 0.7, 0.5, 0.7],
  'primordial:outcast':      [0.6, 0.5, 0.65, 0.45, 0.15, 0.6, 0.6, 0.7]
};

// Keyword adjustments - small nudges based on semantic meaning
// Format: keyword -> [axis_index, adjustment]
const KEYWORD_ADJUSTMENTS = {
  // Order-Chaos (0)
  'structure': [0, -0.05], 'law': [0, -0.08], 'stability': [0, -0.06],
  'chaos': [0, 0.08], 'spontaneity': [0, 0.06], 'upheaval': [0, 0.1],
  'freedom': [0, 0.05], 'control': [0, -0.05], 'wild': [0, 0.07],

  // Creation-Destruction (1)
  'creation': [1, -0.08], 'birth': [1, -0.06], 'fertility': [1, -0.07],
  'destruction': [1, 0.1], 'death': [1, 0.08], 'ending': [1, 0.06],
  'transformation': [1, 0.03], 'renewal': [1, -0.02], 'growth': [1, -0.05],

  // Light-Shadow (2)
  'light': [2, -0.08], 'clarity': [2, -0.06], 'revelation': [2, -0.05],
  'shadow': [2, 0.1], 'darkness': [2, 0.08], 'hidden': [2, 0.06],
  'subconscious': [2, 0.07], 'mystery': [2, 0.05], 'illusion': [2, 0.06],
  'conscious': [2, -0.04], 'truth': [2, -0.04],

  // Active-Receptive (3)
  'action': [3, -0.06], 'will': [3, -0.07], 'determination': [3, -0.05],
  'receptive': [3, 0.06], 'intuition': [3, 0.05], 'passive': [3, 0.07],
  'surrender': [3, 0.08], 'patience': [3, 0.04], 'manifestation': [3, -0.04],

  // Individual-Collective (4)
  'individual': [4, -0.06], 'self': [4, -0.05], 'ego': [4, -0.04],
  'collective': [4, 0.06], 'community': [4, 0.05], 'group': [4, 0.05],
  'tradition': [4, 0.04], 'solitude': [4, -0.05], 'union': [4, 0.03],

  // Ascent-Descent (5)
  'spirit': [5, -0.06], 'transcendence': [5, -0.08], 'sky': [5, -0.07],
  'earth': [5, 0.06], 'matter': [5, 0.05], 'immanence': [5, 0.05],
  'underworld': [5, 0.08], 'heaven': [5, -0.07], 'chthonic': [5, 0.08],

  // Stasis-Transformation (6)
  'preservation': [6, -0.07], 'continuity': [6, -0.06], 'stability': [6, -0.05],
  'change': [6, 0.06], 'metamorphosis': [6, 0.08], 'transition': [6, 0.05],
  'cycles': [6, 0.04], 'rebirth': [6, 0.06], 'journey': [6, 0.04],

  // Voluntary-Fated (7)
  'choice': [7, -0.06], 'free will': [7, -0.07], 'agency': [7, -0.05],
  'fate': [7, 0.08], 'destiny': [7, 0.07], 'karma': [7, 0.06],
  'calling': [7, 0.05], 'luck': [7, 0.04], 'necessity': [7, 0.06]
};

/**
 * Derive coordinates from instantiation weights
 */
function deriveFromPrimordials(instantiates) {
  if (!instantiates || instantiates.length === 0) {
    return [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]; // Default to center
  }

  const coords = [0, 0, 0, 0, 0, 0, 0, 0];
  let totalWeight = 0;

  for (const inst of instantiates) {
    // Normalize primordial ID format
    let primId = inst.primordial;
    if (primId.includes('-')) {
      primId = primId.replace(/-/g, '_'); // divine-child -> divine_child
    }

    const primCoords = PRIMORDIAL_COORDS[primId];
    if (!primCoords) {
      console.warn(`Unknown primordial: ${primId}`);
      continue;
    }

    const weight = inst.estimatedWeight || inst.weight || 0.5;
    totalWeight += weight;

    for (let i = 0; i < 8; i++) {
      coords[i] += primCoords[i] * weight;
    }
  }

  // Normalize by total weight
  if (totalWeight > 0) {
    for (let i = 0; i < 8; i++) {
      coords[i] /= totalWeight;
    }
  }

  return coords;
}

/**
 * Apply keyword-based adjustments
 */
function applyKeywordAdjustments(coords, keywords) {
  if (!keywords || keywords.length === 0) return coords;

  const adjusted = [...coords];

  for (const keyword of keywords) {
    const kw = keyword.toLowerCase();

    // Check direct match
    if (KEYWORD_ADJUSTMENTS[kw]) {
      const [axis, adj] = KEYWORD_ADJUSTMENTS[kw];
      adjusted[axis] += adj;
    }

    // Check partial matches
    for (const [pattern, [axis, adj]] of Object.entries(KEYWORD_ADJUSTMENTS)) {
      if (kw.includes(pattern) || pattern.includes(kw)) {
        adjusted[axis] += adj * 0.5; // Half strength for partial matches
      }
    }
  }

  // Clamp to [0.0, 1.0]
  for (let i = 0; i < 8; i++) {
    adjusted[i] = Math.max(0.0, Math.min(1.0, adjusted[i]));
  }

  return adjusted;
}

/**
 * Calculate Euclidean distance between two coordinate arrays
 */
function euclideanDistance(c1, c2) {
  let sum = 0;
  for (let i = 0; i < 8; i++) {
    const diff = c1[i] - c2[i];
    sum += diff * diff;
  }
  return Math.sqrt(sum);
}

/**
 * Round coordinates to 2 decimal places
 */
function roundCoords(coords) {
  return coords.map(c => Math.round(c * 100) / 100);
}

/**
 * Convert coordinate array to object with axis names
 */
function coordsToObject(coords) {
  const obj = {};
  for (let i = 0; i < 8; i++) {
    obj[AXES[i]] = coords[i];
  }
  return obj;
}

/**
 * Process a single entry stub
 */
function processEntry(entry) {
  // Get instantiation info
  const instantiates = entry.expectedInstantiates || entry.instantiates || [];

  // Derive base coordinates from primordials
  let coords = deriveFromPrimordials(instantiates);

  // Apply keyword adjustments
  const keywords = entry.keywords || [];
  coords = applyKeywordAdjustments(coords, keywords);

  // Round to 2 decimal places
  coords = roundCoords(coords);

  return coordsToObject(coords);
}

/**
 * Process an entire file of stubs
 */
function processFile(inputPath, outputPath) {
  console.log(`\nProcessing: ${inputPath}`);

  const content = fs.readFileSync(inputPath, 'utf8');
  const data = JSON.parse(content);

  const existingCoords = []; // Track for collision detection
  let processed = 0;
  let skipped = 0;

  // Process entries
  if (data.entries) {
    for (const entry of data.entries) {
      if (entry.status === 'placeholder' ||
          (entry.spectralCoordinates && entry.spectralCoordinates['order-chaos'] === null)) {

        const newCoords = processEntry(entry);
        const coordArray = AXES.map(a => newCoords[a]);

        // Check for collisions
        for (const existing of existingCoords) {
          const dist = euclideanDistance(coordArray, existing.coords);
          if (dist < 0.05) {
            console.log(`  Collision detected: ${entry.name} too close to ${existing.name} (dist=${dist.toFixed(3)})`);
            // Nudge slightly on transformation axis
            coordArray[6] += 0.03;
            for (let i = 0; i < 8; i++) {
              newCoords[AXES[i]] = Math.round(coordArray[i] * 100) / 100;
            }
          }
        }

        entry.spectralCoordinates = newCoords;
        entry.status = 'derived';
        entry['@type'] = 'Archetype'; // Upgrade from stub

        existingCoords.push({ name: entry.name, coords: coordArray });
        processed++;
      } else {
        skipped++;
      }
    }
  }

  // Update validation status
  if (data.validationStatus) {
    data.validationStatus.coordinatesAssigned = true;
    data.validationStatus.derivationMethod = 'algorithmic-v1';
    data.validationStatus.derivedAt = new Date().toISOString();
  }

  // Write output
  const outputContent = JSON.stringify(data, null, 2);
  fs.writeFileSync(outputPath, outputContent);

  console.log(`  Processed: ${processed}, Skipped: ${skipped}`);
  return { processed, skipped };
}

/**
 * Main execution
 */
function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('Usage: node derive_coordinates.js <input.jsonld> [output.jsonld]');
    console.log('       node derive_coordinates.js --all (process all stub files)');
    process.exit(1);
  }

  if (args[0] === '--all') {
    // Process all stub files
    const stubFiles = [
      'divination/tarot/major_arcana.jsonld',
      'divination/tarot/minor_arcana.jsonld',
      'divination/astrology/zodiac.jsonld',
      'divination/astrology/planets.jsonld',
      'divination/astrology/houses.jsonld',
      'divination/iching/trigrams.jsonld',
      'divination/iching/hexagrams.jsonld',
      'divination/runes/elder_futhark.jsonld',
      'divination/kabbalah/sephiroth.jsonld',
      'divination/elements/classical_western.jsonld',
      'divination/chakras/energy_centers.jsonld',
      'psychology/jungian/core_archetypes.jsonld',
      'psychology/enneagram/types.jsonld',
      'psychology/narrative/heros_journey.jsonld',
      'psychology/narrative/vogler_archetypes.jsonld',
      'psychology/developmental/spiral_dynamics.jsonld',
      'modern/pop_culture/superhero.jsonld',
      'modern/spiritual/angels.jsonld',
      'modern/digital/internet_archetypes.jsonld',
      'modern/cultural/brand_archetypes.jsonld'
    ];

    const baseDir = path.join(__dirname, '..');
    let totalProcessed = 0;
    let totalSkipped = 0;

    for (const file of stubFiles) {
      const inputPath = path.join(baseDir, file);
      if (fs.existsSync(inputPath)) {
        const result = processFile(inputPath, inputPath); // Overwrite in place
        totalProcessed += result.processed;
        totalSkipped += result.skipped;
      } else {
        console.log(`File not found: ${file}`);
      }
    }

    console.log(`\n=== Summary ===`);
    console.log(`Total processed: ${totalProcessed}`);
    console.log(`Total skipped: ${totalSkipped}`);

  } else {
    const inputPath = args[0];
    const outputPath = args[1] || inputPath;
    processFile(inputPath, outputPath);
  }
}

main();
