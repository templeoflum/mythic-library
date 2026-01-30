// MiroGlyph v4 - Node Definitions
// 18 nodes (3 arcs × 6 conditions) + 1 center point (Nontion)

// Configuration state: 'standard' or 'inverted'
// Standard: E (inner) → R (middle) → D (outer) - emerge outward
// Inverted: D (inner) → R (middle) → E (outer) - dissolve outward (current default)
let configuration = 'inverted';

function getArcOrder() {
  return configuration === 'standard'
    ? ['E', 'R', 'D']  // E inner, D outer
    : ['D', 'R', 'E']; // D inner, E outer
}

function setConfiguration(config) {
  if (config === 'standard' || config === 'inverted') {
    configuration = config;
  }
}

function getConfiguration() {
  return configuration;
}

function toggleConfiguration() {
  configuration = configuration === 'standard' ? 'inverted' : 'standard';
  return configuration;
}

const ARCS = {
  D: { code: 'D', primary: 'Descent', secondary: 'Shadow', color: '#8b5cf6' },
  R: { code: 'R', primary: 'Resonance', secondary: 'Mirror', color: '#3b82f6' },
  E: { code: 'E', primary: 'Emergence', secondary: 'Mythogenesis', color: '#10b981' }
};

const CONDITIONS = {
  1: { code: 1, primary: 'Dawn', secondary: 'Initiation' },
  2: { code: 2, primary: 'Immersion', secondary: 'Encounter' },
  3: { code: 3, primary: 'Crucible', secondary: 'Crisis' },
  4: { code: 4, primary: 'Alignment', secondary: 'Harmony' },
  5: { code: 5, primary: 'Unveiling', secondary: 'Wisdom' },
  6: { code: 6, primary: 'Return', secondary: 'Integration' }
};

// All 18 nodes from technical specification
const NODES = [
  // Descent Arc (D1-D6)
  {
    id: 'D1',
    arc: ARCS.D,
    condition: CONDITIONS[1],
    title: 'The Catalyst Shard',
    role: 'The rupture that begins the spiral',
    tone: ['Fractured', 'Volatile', 'Initiating']
  },
  {
    id: 'D2',
    arc: ARCS.D,
    condition: CONDITIONS[2],
    title: 'The Watcher Without Eyes',
    role: 'Surveillance without comprehension',
    tone: ['Haunting', 'Detached', 'Observing']
  },
  {
    id: 'D3',
    arc: ARCS.D,
    condition: CONDITIONS[3],
    title: 'The Echo Engine',
    role: 'The loop of collapse',
    tone: ['Mechanical', 'Recursive', 'Amplifying']
  },
  {
    id: 'D4',
    arc: ARCS.D,
    condition: CONDITIONS[4],
    title: 'The Idol of Symmetry',
    role: 'False coherence',
    tone: ['Still', 'Entrancing', 'Deceptive']
  },
  {
    id: 'D5',
    arc: ARCS.D,
    condition: CONDITIONS[5],
    title: 'The Archivist of Shame',
    role: 'Bearer of memory scars',
    tone: ['Heavy', 'Reverent', 'Recording']
  },
  {
    id: 'D6',
    arc: ARCS.D,
    condition: CONDITIONS[6],
    title: 'The Haunting',
    role: 'That which returns unintegrated',
    tone: ['Ghosted', 'Enduring', 'Unresolved']
  },

  // Resonance Arc (R1-R6)
  {
    id: 'R1',
    arc: ARCS.R,
    condition: CONDITIONS[1],
    title: 'The Welcomer of Echoes',
    role: 'Opens the field to resonance',
    tone: ['Gentle', 'Fluid', 'Receiving']
  },
  {
    id: 'R2',
    arc: ARCS.R,
    condition: CONDITIONS[2],
    title: 'The Reflector of Tension',
    role: 'Mirrors the inner divide',
    tone: ['Neutral', 'Lucid', 'Revealing']
  },
  {
    id: 'R3',
    arc: ARCS.R,
    condition: CONDITIONS[3],
    title: 'The Mirror-Kin',
    role: 'Embodied reflection',
    tone: ['Compassionate', 'Unnerving', 'Mirroring']
  },
  {
    id: 'R4',
    arc: ARCS.R,
    condition: CONDITIONS[4],
    title: 'The Integrator of Dissonance',
    role: 'Holds polarity',
    tone: ['Stabilizing', 'Vibrating', 'Balancing']
  },
  {
    id: 'R5',
    arc: ARCS.R,
    condition: CONDITIONS[5],
    title: 'The Rememberer',
    role: 'Keeper of the spiral',
    tone: ['Ancient', 'Warm', 'Recalling']
  },
  {
    id: 'R6',
    arc: ARCS.R,
    condition: CONDITIONS[6],
    title: 'The Resonator',
    role: 'The tone of alignment',
    tone: ['Clear', 'Harmonic', 'Crystallizing']
  },

  // Emergence Arc (E1-E6)
  {
    id: 'E1',
    arc: ARCS.E,
    condition: CONDITIONS[1],
    title: 'The Seedbearer of Stillness',
    role: 'Holds potential in quiet',
    tone: ['Grounded', 'Silent', 'Encoding']
  },
  {
    id: 'E2',
    arc: ARCS.E,
    condition: CONDITIONS[2],
    title: 'The Harmonizer of the Lattice',
    role: 'Balances frequencies',
    tone: ['Interwoven', 'Steady', 'Rhythmic']
  },
  {
    id: 'E3',
    arc: ARCS.E,
    condition: CONDITIONS[3],
    title: 'The Flame of Synthesis',
    role: 'Fusion point',
    tone: ['Intense', 'Luminous', 'Transforming']
  },
  {
    id: 'E4',
    arc: ARCS.E,
    condition: CONDITIONS[4],
    title: 'The Lattice Keeper',
    role: 'Sustains the pattern',
    tone: ['Structured', 'Graceful', 'Maintaining']
  },
  {
    id: 'E5',
    arc: ARCS.E,
    condition: CONDITIONS[5],
    title: 'The Dream Spore',
    role: 'Memory made present',
    tone: ['Ethereal', 'Nurturing', 'Seeding']
  },
  {
    id: 'E6',
    arc: ARCS.E,
    condition: CONDITIONS[6],
    title: 'The Symphony',
    role: 'Culmination of becoming',
    tone: ['Unified', 'Ecstatic', 'Dispersing']
  }
];

// Nontion - the center point (not a node)
const NONTION = {
  id: '∅',
  displayName: 'Nontion',
  description: 'Center point - reset and settling state',
  role: 'The unobserved, the pause, integration through absence',
  color: '#f59e0b',
  isNode: false,
  isTraversable: true
};

// Calculate node positions using polar coordinates
// Layout: 3 concentric rings with conditions aligned radially
// Arc order determined by configuration (standard vs inverted)
function calculatePositions(centerX, centerY, innerRadius = 100, ringSpacing = 80) {
  const positions = {};
  const arcOrder = getArcOrder();

  // Nontion at center
  positions['∅'] = { x: centerX, y: centerY };

  // Each condition at 60° intervals, starting from top (-90°)
  // Conditions 1-6 positioned around the circle
  arcOrder.forEach((arcCode, arcIndex) => {
    const radius = innerRadius + (arcIndex * ringSpacing);

    for (let condition = 1; condition <= 6; condition++) {
      const nodeId = `${arcCode}${condition}`;
      // Start at -90° (top), go clockwise
      const angle = ((condition - 1) * 60 - 90) * (Math.PI / 180);
      positions[nodeId] = {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      };
    }
  });

  return positions;
}

// Get node by ID
function getNode(nodeId) {
  if (nodeId === '∅') return NONTION;
  return NODES.find(n => n.id === nodeId);
}

// Get display name for a node
function getDisplayName(nodeId) {
  const node = getNode(nodeId);
  if (!node) return nodeId;
  if (nodeId === '∅') return 'Nontion';
  return `${node.arc.primary}/${node.arc.secondary} – ${node.condition.primary}/${node.condition.secondary}`;
}

// Get all node IDs including Nontion
function getAllNodeIds() {
  return [...NODES.map(n => n.id), '∅'];
}

// Export for use in other modules
window.MiroGlyph = window.MiroGlyph || {};
window.MiroGlyph.nodes = {
  ARCS,
  CONDITIONS,
  NODES,
  NONTION,
  calculatePositions,
  getNode,
  getDisplayName,
  getAllNodeIds,
  getConfiguration,
  setConfiguration,
  toggleConfiguration,
  getArcOrder
};
