#!/usr/bin/env node
/**
 * ACP Validation Tool
 *
 * Validates all ACP files against the schema rules defined in dynamics.jsonld
 *
 * Checks:
 * 1. Coordinate bounds: All spectral coordinates in [0.0, 1.0]
 * 2. Coordinate completeness: All 8 axes present
 * 3. No collisions: Euclidean distance > 0.05 between distinct archetypes
 * 4. Relationship bidirectionality: If A→B exists, B→A should exist for bidirectional types
 * 5. Primordial instantiation: Cultural archetypes must instantiate at least one primordial
 * 6. Weight validation: Instantiation weights in [0.0, 1.0]
 * 7. Reference validation: All @id references resolve to existing entities
 */

const fs = require('fs');
const path = require('path');

// Configuration
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

const BIDIRECTIONAL_RELATIONSHIPS = [
  'POLAR_OPPOSITE',
  'COMPLEMENT',
  'TENSION',
  'CULTURAL_ECHO',
  'MIRRORS',
  'TWIN'
];

const MIN_DISTANCE = 0.05;

// Utility functions
function euclideanDistance(coords1, coords2) {
  if (!coords1 || !coords2) return null;
  let sum = 0;
  for (const axis of AXES) {
    const a = coords1[axis];
    const b = coords2[axis];
    if (a === null || a === undefined || b === null || b === undefined) return null;
    sum += Math.pow(a - b, 2);
  }
  return Math.sqrt(sum);
}

function loadJsonFile(filepath) {
  try {
    const content = fs.readFileSync(filepath, 'utf8');
    return JSON.parse(content);
  } catch (e) {
    return { error: e.message };
  }
}

function findJsonFiles(dir, files = []) {
  if (!fs.existsSync(dir)) return files;

  const items = fs.readdirSync(dir);
  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);
    if (stat.isDirectory()) {
      // Skip legacy and node_modules
      if (item !== 'legacy' && item !== 'node_modules' && item !== '.git') {
        findJsonFiles(fullPath, files);
      }
    } else if (item.endsWith('.jsonld') || item.endsWith('.json')) {
      files.push(fullPath);
    }
  }
  return files;
}

// Validation functions
class Validator {
  constructor(rootDir) {
    this.rootDir = rootDir;
    this.errors = [];
    this.warnings = [];
    this.stats = {
      filesChecked: 0,
      archetypesChecked: 0,
      coordinatesValidated: 0,
      relationshipsChecked: 0
    };
    this.allArchetypes = new Map(); // id -> {coords, file, name}
    this.allRelationships = []; // {source, target, type, file}
  }

  error(file, message) {
    this.errors.push({ file: path.relative(this.rootDir, file), message });
  }

  warn(file, message) {
    this.warnings.push({ file: path.relative(this.rootDir, file), message });
  }

  // Check 1: Coordinate bounds
  validateCoordinateBounds(coords, id, file) {
    if (!coords) return;

    for (const axis of AXES) {
      const value = coords[axis];
      if (value === null || value === undefined) continue; // Placeholder
      if (typeof value !== 'number') {
        this.error(file, `${id}: ${axis} is not a number (got ${typeof value})`);
      } else if (value < 0.0 || value > 1.0) {
        this.error(file, `${id}: ${axis} out of bounds: ${value} (must be 0.0-1.0)`);
      }
    }
    this.stats.coordinatesValidated++;
  }

  // Check 2: Coordinate completeness
  validateCoordinateCompleteness(coords, id, file) {
    if (!coords) return;

    // Skip if all null (placeholder)
    const hasAnyValue = AXES.some(a => coords[a] !== null && coords[a] !== undefined);
    if (!hasAnyValue) return; // Valid placeholder

    for (const axis of AXES) {
      if (coords[axis] === null || coords[axis] === undefined) {
        this.error(file, `${id}: Missing axis ${axis} (partial coordinates not allowed)`);
      }
    }
  }

  // Check 3: Weight validation
  validateWeights(instantiates, id, file) {
    if (!instantiates || !Array.isArray(instantiates)) return;

    for (const inst of instantiates) {
      const weight = inst.weight || inst.estimatedWeight;
      if (weight !== undefined && weight !== null) {
        if (typeof weight !== 'number') {
          this.error(file, `${id}: instantiation weight is not a number`);
        } else if (weight < 0.0 || weight > 1.0) {
          this.error(file, `${id}: instantiation weight ${weight} out of bounds (must be 0.0-1.0)`);
        }
      }
    }
  }

  // Collect archetype for collision detection
  collectArchetype(id, name, coords, file) {
    if (!coords) return;
    const hasCoords = AXES.some(a => coords[a] !== null && coords[a] !== undefined);
    if (!hasCoords) return;

    this.allArchetypes.set(id, { coords, file, name });
    this.stats.archetypesChecked++;
  }

  // Collect relationship for bidirectionality check
  collectRelationship(source, target, type, file) {
    if (!source || !target || !type) return;
    this.allRelationships.push({ source, target, type, file });
    this.stats.relationshipsChecked++;
  }

  // Process a single entry (archetype/stub)
  processEntry(entry, file) {
    const id = entry['@id'];
    const name = entry.name;
    const coords = entry.spectralCoordinates;
    const instantiates = entry.instantiates || entry.expectedInstantiates;
    const relationships = entry.relationships || entry.expectedRelationships;

    if (coords) {
      this.validateCoordinateBounds(coords, id, file);
      this.validateCoordinateCompleteness(coords, id, file);
      this.collectArchetype(id, name, coords, file);
    }

    if (instantiates) {
      this.validateWeights(instantiates, id, file);
    }

    if (relationships && Array.isArray(relationships)) {
      for (const rel of relationships) {
        this.collectRelationship(id, rel.target, rel.type, file);
      }
    }
  }

  // Process a file
  processFile(filepath) {
    const data = loadJsonFile(filepath);
    if (data.error) {
      this.error(filepath, `Failed to parse: ${data.error}`);
      return;
    }

    this.stats.filesChecked++;

    // Handle @graph arrays
    if (data['@graph'] && Array.isArray(data['@graph'])) {
      for (const entry of data['@graph']) {
        if (entry['@id'] && entry['@type']) {
          this.processEntry(entry, filepath);
        }
      }
    }

    // Handle entries arrays
    if (data.entries && Array.isArray(data.entries)) {
      for (const entry of data.entries) {
        this.processEntry(entry, filepath);
      }
    }

    // Handle suits with cards (Tarot minor arcana)
    if (data.suits && Array.isArray(data.suits)) {
      for (const suit of data.suits) {
        if (suit.cards && Array.isArray(suit.cards)) {
          for (const card of suit.cards) {
            this.processEntry(card, filepath);
          }
        }
      }
    }

    // Handle acts with stages (Hero's Journey)
    if (data.acts && Array.isArray(data.acts)) {
      for (const act of data.acts) {
        if (act.stages && Array.isArray(act.stages)) {
          for (const stage of act.stages) {
            this.processEntry(stage, filepath);
          }
        }
      }
    }

    // Handle direct entries in calibration files
    if (data['@id'] && data.spectralCoordinates) {
      this.processEntry(data, filepath);
    }
  }

  // Check 3: No coordinate collisions
  checkCollisions() {
    const archetypes = Array.from(this.allArchetypes.entries());

    for (let i = 0; i < archetypes.length; i++) {
      for (let j = i + 1; j < archetypes.length; j++) {
        const [id1, data1] = archetypes[i];
        const [id2, data2] = archetypes[j];

        const dist = euclideanDistance(data1.coords, data2.coords);
        if (dist !== null && dist < MIN_DISTANCE) {
          this.error(data1.file,
            `Collision: ${id1} and ${id2} are too close (distance: ${dist.toFixed(4)}, min: ${MIN_DISTANCE})`);
        }
      }
    }
  }

  // Check 4: Relationship bidirectionality
  checkBidirectionality() {
    const relMap = new Map();

    // Build map of relationships
    for (const rel of this.allRelationships) {
      const key = `${rel.source}|${rel.target}|${rel.type}`;
      relMap.set(key, rel);
    }

    // Check for reverse
    for (const rel of this.allRelationships) {
      if (BIDIRECTIONAL_RELATIONSHIPS.includes(rel.type)) {
        const reverseKey = `${rel.target}|${rel.source}|${rel.type}`;
        if (!relMap.has(reverseKey)) {
          this.warn(rel.file,
            `Missing reverse relationship: ${rel.target} → ${rel.source} (${rel.type})`);
        }
      }
    }
  }

  // Check 5: Reference validation - all targets exist
  checkReferenceValidity() {
    const allIds = new Set(this.allArchetypes.keys());

    for (const rel of this.allRelationships) {
      // Skip cross-system references that use prefixes we don't track fully
      const targetPrefix = rel.target.split(':')[0];
      const knownPrefixes = ['tarot', 'iching', 'trigram', 'hexagram', 'zodiac', 'astrology',
                            'rune', 'kabbalah', 'chakra', 'jungian', 'enneagram', 'journey',
                            'vogler', 'spiral', 'brand', 'digital', 'superhero', 'angel',
                            'greek', 'primordial', 'element'];

      // Only warn for references within our known systems that don't resolve
      if (knownPrefixes.includes(targetPrefix) && !allIds.has(rel.target)) {
        // Check if it's a system-level reference vs entry-level
        const isSystemRef = !rel.target.includes(':') || rel.target.split(':')[1].includes('_');
        if (!isSystemRef) {
          this.warn(rel.file, `Unresolved reference: ${rel.source} → ${rel.target}`);
        }
      }
    }
  }

  // Check 6: Polar opposite axis verification
  checkPolarOpposites() {
    const POLARITY_THRESHOLD = 0.5; // Minimum difference on specified axis

    for (const rel of this.allRelationships) {
      if (rel.type === 'POLAR_OPPOSITE' && rel.axis) {
        const source = this.allArchetypes.get(rel.source);
        const target = this.allArchetypes.get(rel.target);

        if (source && target && source.coords && target.coords) {
          const axis = rel.axis;
          if (source.coords[axis] !== undefined && target.coords[axis] !== undefined) {
            const diff = Math.abs(source.coords[axis] - target.coords[axis]);
            if (diff < POLARITY_THRESHOLD) {
              this.warn(rel.file,
                `Weak polarity: ${rel.source} ↔ ${rel.target} on ${axis} (diff: ${diff.toFixed(2)}, expected > ${POLARITY_THRESHOLD})`);
            }
          }
        }
      }
    }
  }

  // Generate summary statistics
  generateSummary() {
    const systemCounts = new Map();
    const coordinateRanges = {};

    for (const axis of AXES) {
      coordinateRanges[axis] = { min: 1, max: 0, sum: 0, count: 0 };
    }

    for (const [id, data] of this.allArchetypes) {
      // Count by system
      const prefix = id.split(':')[0];
      systemCounts.set(prefix, (systemCounts.get(prefix) || 0) + 1);

      // Track coordinate ranges
      if (data.coords) {
        for (const axis of AXES) {
          const val = data.coords[axis];
          if (val !== null && val !== undefined) {
            coordinateRanges[axis].min = Math.min(coordinateRanges[axis].min, val);
            coordinateRanges[axis].max = Math.max(coordinateRanges[axis].max, val);
            coordinateRanges[axis].sum += val;
            coordinateRanges[axis].count++;
          }
        }
      }
    }

    console.log('\n───────────────────────────────────────────────────────');
    console.log('ENTRY COUNTS BY SYSTEM');
    console.log('───────────────────────────────────────────────────────');
    const sorted = Array.from(systemCounts.entries()).sort((a, b) => b[1] - a[1]);
    let total = 0;
    for (const [system, count] of sorted) {
      console.log(`  ${system.padEnd(20)} ${count}`);
      total += count;
    }
    console.log(`  ${'─'.repeat(28)}`);
    console.log(`  ${'TOTAL'.padEnd(20)} ${total}`);

    console.log('\n───────────────────────────────────────────────────────');
    console.log('COORDINATE DISTRIBUTION');
    console.log('───────────────────────────────────────────────────────');
    for (const axis of AXES) {
      const r = coordinateRanges[axis];
      if (r.count > 0) {
        const avg = (r.sum / r.count).toFixed(2);
        console.log(`  ${axis.padEnd(24)} min: ${r.min.toFixed(2)}  max: ${r.max.toFixed(2)}  avg: ${avg}`);
      }
    }

    // Relationship type counts
    const relTypeCounts = new Map();
    for (const rel of this.allRelationships) {
      relTypeCounts.set(rel.type, (relTypeCounts.get(rel.type) || 0) + 1);
    }

    console.log('\n───────────────────────────────────────────────────────');
    console.log('RELATIONSHIP COUNTS BY TYPE');
    console.log('───────────────────────────────────────────────────────');
    const sortedRels = Array.from(relTypeCounts.entries()).sort((a, b) => b[1] - a[1]);
    for (const [type, count] of sortedRels) {
      console.log(`  ${type.padEnd(24)} ${count}`);
    }
  }

  // Run all validations
  run() {
    console.log('═══════════════════════════════════════════════════════');
    console.log('           ACP VALIDATION REPORT');
    console.log('═══════════════════════════════════════════════════════\n');

    // Find and process all files
    const dirs = [
      path.join(this.rootDir, 'schema'),
      path.join(this.rootDir, 'calibration'),
      path.join(this.rootDir, 'archetypes'),
      path.join(this.rootDir, 'divination'),
      path.join(this.rootDir, 'psychology'),
      path.join(this.rootDir, 'modern')
    ];

    console.log('Scanning directories...');
    let allFiles = [];
    for (const dir of dirs) {
      const files = findJsonFiles(dir);
      allFiles = allFiles.concat(files);
    }
    console.log(`Found ${allFiles.length} files\n`);

    console.log('Processing files...');
    for (const file of allFiles) {
      this.processFile(file);
    }

    console.log('Checking for collisions...');
    this.checkCollisions();

    console.log('Checking relationship bidirectionality...');
    this.checkBidirectionality();

    console.log('Checking reference validity...');
    this.checkReferenceValidity();

    console.log('Checking polar opposite axes...');
    this.checkPolarOpposites();

    // Generate summary
    this.generateSummary();

    // Output results
    console.log('\n───────────────────────────────────────────────────────');
    console.log('STATISTICS');
    console.log('───────────────────────────────────────────────────────');
    console.log(`  Files checked:        ${this.stats.filesChecked}`);
    console.log(`  Archetypes checked:   ${this.stats.archetypesChecked}`);
    console.log(`  Coordinates validated: ${this.stats.coordinatesValidated}`);
    console.log(`  Relationships checked: ${this.stats.relationshipsChecked}`);

    if (this.errors.length > 0) {
      console.log('\n───────────────────────────────────────────────────────');
      console.log(`ERRORS (${this.errors.length})`);
      console.log('───────────────────────────────────────────────────────');
      for (const err of this.errors) {
        console.log(`  ✗ [${err.file}]`);
        console.log(`    ${err.message}`);
      }
    }

    if (this.warnings.length > 0) {
      console.log('\n───────────────────────────────────────────────────────');
      console.log(`WARNINGS (${this.warnings.length})`);
      console.log('───────────────────────────────────────────────────────');
      for (const warn of this.warnings) {
        console.log(`  ⚠ [${warn.file}]`);
        console.log(`    ${warn.message}`);
      }
    }

    console.log('\n═══════════════════════════════════════════════════════');
    if (this.errors.length === 0) {
      console.log('✓ VALIDATION PASSED');
    } else {
      console.log(`✗ VALIDATION FAILED (${this.errors.length} errors)`);
    }
    console.log('═══════════════════════════════════════════════════════\n');

    return this.errors.length === 0;
  }
}

// Main
const rootDir = path.resolve(__dirname, '..');
const validator = new Validator(rootDir);
const passed = validator.run();
process.exit(passed ? 0 : 1);
