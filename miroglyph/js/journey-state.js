// Journey Mapper - State Management (Network Configuration Model)
// Handles network configuration, traversal state, and LocalStorage persistence

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var NETWORKS_STORAGE_KEY = 'miroglyph_networks';

  // ========== Mapping Tables ==========

  // Primary motif position: determined by condition number
  var PRIMARY_MAP = { 1: '1P', 2: '2P', 3: '3P', 4: '1P', 5: '2P', 6: '3P' };

  // Secondary motif position: determined by arc + condition
  var SECONDARY_MAP = {
    D: { 1: '1S', 2: '2S', 3: '3S', 4: '2S', 5: '3S', 6: '1S' },
    R: { 1: '2S', 2: '3S', 3: '1S', 4: '3S', 5: '1S', 6: '2S' },
    E: { 1: '3S', 2: '1S', 3: '2S', 4: '1S', 5: '2S', 6: '3S' }
  };

  // Entity assignment: by polarity pair (conditions 1&4, 2&5, 3&6)
  var ENTITY_MAP = { 1: 'pair_14', 2: 'pair_25', 3: 'pair_36',
                     4: 'pair_14', 5: 'pair_25', 6: 'pair_36' };

  // All 18 node IDs
  var ALL_NODE_IDS = [
    'D1', 'D2', 'D3', 'D4', 'D5', 'D6',
    'R1', 'R2', 'R3', 'R4', 'R5', 'R6',
    'E1', 'E2', 'E3', 'E4', 'E5', 'E6'
  ];

  // Predefined traversals
  var STARTER_TRAVERSALS = [
    { name: 'Descent Circuit', sequence: ['D1', 'D2', 'D3', 'D4', 'D5', 'D6'] },
    { name: 'Shadow Spiral', sequence: ['D1', 'D3', '∅', 'R3', 'E3'] },
    { name: 'Mirror Journey', sequence: ['R1', 'R3', 'R5', '∅', 'E5'] },
    { name: 'Crisis Triangle', sequence: ['D3', 'R3', 'E3'] },
    { name: 'Integration Path', sequence: ['D1', 'R2', 'E3', '∅', 'E6'] },
    { name: 'Full Emergence', sequence: ['E1', 'E2', 'E3', 'E4', 'E5', 'E6'] },
    { name: 'The Katabasis', sequence: ['D1', 'D2', 'D3', '∅', 'E4', 'E5', 'E6'] },
    { name: 'Resonance Weave', sequence: ['R1', 'R2', 'R3', 'R4', 'R5', 'R6'] }
  ];

  // Current state
  var currentNetwork = null;
  var currentTraversalIndex = -1;  // index into currentNetwork.traversals
  var currentNodeIndex = 0;        // position within current traversal sequence

  // Config wizard state (temporary, before network is created)
  var configState = {
    step: 1,
    primary_archetype: null,
    secondary_archetype: null,
    motifs: { '1P': null, '2P': null, '3P': null, '1S': null, '2S': null, '3S': null },
    entities: { pair_14: null, pair_25: null, pair_36: null }
  };

  // ========== Node Content Derivation ==========

  /**
   * Compute node contents from network configuration
   * @param {string} nodeId - e.g. 'D1', 'R4', 'E6'
   * @param {Object} config - network configuration object
   * @returns {Object} - { primary_archetype, secondary_archetype, primary_motif, secondary_motif, entity }
   */
  function getNodeContents(nodeId, config) {
    if (!config || nodeId === '∅') return null;

    var arc = nodeId.charAt(0);
    var condition = parseInt(nodeId.charAt(1), 10);

    return {
      primary_archetype: config.primary_archetype,
      secondary_archetype: config.secondary_archetype,
      primary_motif: config.motifs[PRIMARY_MAP[condition]],
      secondary_motif: config.motifs[SECONDARY_MAP[arc][condition]],
      entity: config.entities[ENTITY_MAP[condition]]
    };
  }

  /**
   * Get the motif position labels for a node
   */
  function getNodePositions(nodeId) {
    if (nodeId === '∅') return null;
    var arc = nodeId.charAt(0);
    var condition = parseInt(nodeId.charAt(1), 10);
    return {
      primary: PRIMARY_MAP[condition],
      secondary: SECONDARY_MAP[arc][condition]
    };
  }

  // ========== Config Wizard ==========

  function getConfigState() {
    return configState;
  }

  function setConfigStep(step) {
    configState.step = step;
  }

  function getConfigStep() {
    return configState.step;
  }

  function setConfigArchetype(which, archetype) {
    if (which === 'primary') {
      configState.primary_archetype = archetype;
    } else {
      configState.secondary_archetype = archetype;
    }
  }

  function setConfigMotif(position, motif) {
    configState.motifs[position] = motif;
  }

  function setConfigEntity(pair, entity) {
    configState.entities[pair] = entity;
  }

  function isConfigComplete() {
    if (!configState.primary_archetype || !configState.secondary_archetype) return false;
    var slots = ['1P', '2P', '3P', '1S', '2S', '3S'];
    for (var i = 0; i < slots.length; i++) {
      if (!configState.motifs[slots[i]]) return false;
    }
    if (!configState.entities.pair_14 || !configState.entities.pair_25 || !configState.entities.pair_36) return false;
    return true;
  }

  function isConfigStepComplete(step) {
    if (step === 1) {
      return !!configState.primary_archetype && !!configState.secondary_archetype;
    } else if (step === 2) {
      var slots = ['1P', '2P', '3P', '1S', '2S', '3S'];
      for (var i = 0; i < slots.length; i++) {
        if (!configState.motifs[slots[i]]) return false;
      }
      return true;
    } else if (step === 3) {
      return !!configState.entities.pair_14 && !!configState.entities.pair_25 && !!configState.entities.pair_36;
    } else if (step === 4) {
      return isConfigComplete();
    }
    return false;
  }

  function resetConfigState() {
    configState = {
      step: 1,
      primary_archetype: null,
      secondary_archetype: null,
      motifs: { '1P': null, '2P': null, '3P': null, '1S': null, '2S': null, '3S': null },
      entities: { pair_14: null, pair_25: null, pair_36: null }
    };
  }

  // ========== Network CRUD ==========

  /**
   * Create a network from the current config state
   * @param {string} name - Optional network name
   * @returns {Object} - The new network
   */
  function createNetwork(name) {
    var utils = window.MiroGlyph.utils;

    currentNetwork = {
      network_id: utils.uuid(),
      name: name || 'Mythic Network',
      configuration: {
        primary_archetype: configState.primary_archetype,
        secondary_archetype: configState.secondary_archetype,
        motifs: JSON.parse(JSON.stringify(configState.motifs)),
        entities: JSON.parse(JSON.stringify(configState.entities))
      },
      traversals: [],
      created_date: new Date().toISOString()
    };

    currentTraversalIndex = -1;
    currentNodeIndex = 0;

    return currentNetwork;
  }

  function getNetwork() {
    return currentNetwork;
  }

  function getConfiguration() {
    return currentNetwork ? currentNetwork.configuration : null;
  }

  // ========== Traversal Management ==========

  /**
   * Add a traversal to the current network
   * @param {string} name
   * @param {Array} sequence - Array of node IDs
   * @returns {Object} - The new traversal
   */
  function addTraversal(name, sequence) {
    if (!currentNetwork) return null;
    var utils = window.MiroGlyph.utils;

    var traversal = {
      traversal_id: utils.uuid(),
      name: name || 'Unnamed Traversal',
      sequence: sequence,
      notes: {},
      created_date: new Date().toISOString(),
      completed: false
    };

    currentNetwork.traversals.push(traversal);
    return traversal;
  }

  /**
   * Start a traversal (set it as current)
   * @param {number} traversalIdx - Index in network.traversals array
   */
  function startTraversal(traversalIdx) {
    if (!currentNetwork || traversalIdx < 0 || traversalIdx >= currentNetwork.traversals.length) return false;
    currentTraversalIndex = traversalIdx;
    currentNodeIndex = 0;
    currentNetwork.traversals[traversalIdx].completed = false;
    return true;
  }

  function getCurrentTraversal() {
    if (!currentNetwork || currentTraversalIndex < 0) return null;
    return currentNetwork.traversals[currentTraversalIndex] || null;
  }

  function getCurrentNodeId() {
    var traversal = getCurrentTraversal();
    if (!traversal) return null;
    return traversal.sequence[currentNodeIndex] || null;
  }

  function getCurrentNodeIndex() {
    return currentNodeIndex;
  }

  function isCurrentNodeNontion() {
    return getCurrentNodeId() === '∅';
  }

  /**
   * Navigate to next node in traversal
   * @returns {Object} - { moved, journeyComplete }
   */
  function nextNode() {
    var traversal = getCurrentTraversal();
    if (!traversal) return { moved: false };

    var nextIndex = currentNodeIndex + 1;
    if (nextIndex >= traversal.sequence.length) {
      traversal.completed = true;
      return { moved: true, journeyComplete: true };
    }

    currentNodeIndex = nextIndex;
    return { moved: true, journeyComplete: false };
  }

  /**
   * Navigate to previous node in traversal
   * @returns {Object} - { moved }
   */
  function prevNode() {
    if (currentNodeIndex === 0) return { moved: false };
    currentNodeIndex--;
    return { moved: true };
  }

  /**
   * Jump to a specific node index
   */
  function goToNode(index) {
    var traversal = getCurrentTraversal();
    if (!traversal || index < 0 || index >= traversal.sequence.length) return false;
    currentNodeIndex = index;
    return true;
  }

  /**
   * Set note for current node in current traversal
   */
  function setNote(nodeId, text) {
    var traversal = getCurrentTraversal();
    if (!traversal) return;
    traversal.notes[nodeId] = text || '';
  }

  /**
   * Get note for a node in current traversal
   */
  function getNote(nodeId) {
    var traversal = getCurrentTraversal();
    if (!traversal) return '';
    return traversal.notes[nodeId] || '';
  }

  /**
   * Complete the current traversal
   */
  function completeTraversal() {
    var traversal = getCurrentTraversal();
    if (traversal) {
      traversal.completed = true;
    }
  }

  /**
   * Get traversal progress info
   */
  function getProgress() {
    var traversal = getCurrentTraversal();
    if (!traversal) return { currentIndex: 0, total: 0, percentage: 0 };
    return {
      currentIndex: currentNodeIndex,
      total: traversal.sequence.length,
      percentage: Math.round((currentNodeIndex / traversal.sequence.length) * 100)
    };
  }

  // ========== Starter Traversals ==========

  function getStarterTraversals() {
    return STARTER_TRAVERSALS.slice();
  }

  function getRandomTraversal() {
    var index = Math.floor(Math.random() * STARTER_TRAVERSALS.length);
    return STARTER_TRAVERSALS[index];
  }

  // ========== Persistence ==========

  /**
   * Load saved networks from LocalStorage
   */
  function loadSavedNetworks() {
    try {
      var data = localStorage.getItem(NETWORKS_STORAGE_KEY);
      if (data) {
        var parsed = JSON.parse(data);
        return {
          version: parsed.version || '2.0.0',
          networks: parsed.networks || []
        };
      }
    } catch (e) {
      console.error('Failed to load networks:', e);
    }
    return { version: '2.0.0', networks: [] };
  }

  /**
   * Save networks to LocalStorage
   */
  function saveNetworks(networks) {
    try {
      var data = {
        version: '2.0.0',
        lastModified: new Date().toISOString(),
        networks: networks
      };
      localStorage.setItem(NETWORKS_STORAGE_KEY, JSON.stringify(data));
      return true;
    } catch (e) {
      console.error('Failed to save networks:', e);
      return false;
    }
  }

  /**
   * Save current network to LocalStorage
   */
  function saveCurrentNetwork(name) {
    if (!currentNetwork) return false;
    if (name) currentNetwork.name = name;
    currentNetwork.saved_date = new Date().toISOString();

    var saved = loadSavedNetworks();
    // Update existing or add new
    var existingIndex = -1;
    for (var i = 0; i < saved.networks.length; i++) {
      if (saved.networks[i].network_id === currentNetwork.network_id) {
        existingIndex = i;
        break;
      }
    }

    var copy = JSON.parse(JSON.stringify(currentNetwork));
    if (existingIndex >= 0) {
      saved.networks[existingIndex] = copy;
    } else {
      saved.networks.push(copy);
    }
    return saveNetworks(saved.networks);
  }

  /**
   * Delete a saved network
   */
  function deleteSavedNetwork(networkId) {
    var saved = loadSavedNetworks();
    saved.networks = saved.networks.filter(function(n) {
      return n.network_id !== networkId;
    });
    return saveNetworks(saved.networks);
  }

  /**
   * Load a saved network
   */
  function loadNetwork(networkId) {
    var saved = loadSavedNetworks();
    var network = saved.networks.find(function(n) {
      return n.network_id === networkId;
    });
    if (network) {
      currentNetwork = JSON.parse(JSON.stringify(network));
      currentTraversalIndex = -1;
      currentNodeIndex = 0;
      return currentNetwork;
    }
    return null;
  }

  /**
   * Export current network as JSON file
   */
  function exportNetworkJSON() {
    if (!currentNetwork) return;

    var exportData = {
      miroglyph_version: '4.0.0',
      type: 'network',
      exported_at: new Date().toISOString(),
      network: currentNetwork
    };

    var blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob);

    var a = document.createElement('a');
    a.href = url;
    var safeName = (currentNetwork.name || 'network').replace(/[^a-z0-9]/gi, '_').toLowerCase();
    a.download = 'miroglyph_network_' + safeName + '.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  /**
   * Clear current network
   */
  function clearNetwork() {
    currentNetwork = null;
    currentTraversalIndex = -1;
    currentNodeIndex = 0;
  }

  // ========== Surprise Me (full random config) ==========

  /**
   * Generate a random network configuration
   * @param {Object} deps - { archetypes, entities, patterns }
   * @returns {Object} - config state ready to create network
   */
  function generateRandomConfig(deps) {
    var archetypes = deps.archetypes && deps.archetypes.archetypes ? deps.archetypes.archetypes : [];
    var entities = deps.entities && deps.entities.entities ? deps.entities.entities : [];
    var allMotifs = deps.patterns && deps.patterns.motifs ? deps.patterns.motifs : {};

    var motifArray = Object.keys(allMotifs).map(function(code) {
      var m = allMotifs[code];
      return { code: code, label: m.label, category: m.category || code.charAt(0) };
    });

    function pickRandom(arr) {
      return arr[Math.floor(Math.random() * arr.length)];
    }

    // Pick 2 different archetypes
    var arch1 = pickRandom(archetypes);
    var arch2 = pickRandom(archetypes);
    while (arch2 && arch1 && arch2.id === arch1.id && archetypes.length > 1) {
      arch2 = pickRandom(archetypes);
    }

    // Pick 6 different motifs
    var usedMotifs = {};
    var motifSlots = ['1P', '2P', '3P', '1S', '2S', '3S'];
    var motifConfig = {};
    for (var i = 0; i < motifSlots.length; i++) {
      var m = pickRandom(motifArray);
      var attempts = 0;
      while (usedMotifs[m.code] && attempts < 50) {
        m = pickRandom(motifArray);
        attempts++;
      }
      usedMotifs[m.code] = true;
      motifConfig[motifSlots[i]] = m;
    }

    // Pick 3 different entities
    var usedEntities = {};
    var entityPairs = ['pair_14', 'pair_25', 'pair_36'];
    var entityConfig = {};
    for (var j = 0; j < entityPairs.length; j++) {
      var e = pickRandom(entities);
      var eAttempts = 0;
      while (e && usedEntities[e.name] && eAttempts < 50) {
        e = pickRandom(entities);
        eAttempts++;
      }
      if (e) usedEntities[e.name] = true;
      entityConfig[entityPairs[j]] = e;
    }

    // Set config state
    configState.primary_archetype = arch1;
    configState.secondary_archetype = arch2;
    configState.motifs = motifConfig;
    configState.entities = entityConfig;
    configState.step = 4;

    return configState;
  }

  // ========== Export ==========

  window.MiroGlyph.journeyState = {
    // Mapping tables
    PRIMARY_MAP: PRIMARY_MAP,
    SECONDARY_MAP: SECONDARY_MAP,
    ENTITY_MAP: ENTITY_MAP,
    ALL_NODE_IDS: ALL_NODE_IDS,

    // Node content derivation
    getNodeContents: getNodeContents,
    getNodePositions: getNodePositions,

    // Config wizard
    getConfigState: getConfigState,
    setConfigStep: setConfigStep,
    getConfigStep: getConfigStep,
    setConfigArchetype: setConfigArchetype,
    setConfigMotif: setConfigMotif,
    setConfigEntity: setConfigEntity,
    isConfigComplete: isConfigComplete,
    isConfigStepComplete: isConfigStepComplete,
    resetConfigState: resetConfigState,

    // Network CRUD
    createNetwork: createNetwork,
    getNetwork: getNetwork,
    getConfiguration: getConfiguration,
    clearNetwork: clearNetwork,

    // Traversal management
    addTraversal: addTraversal,
    startTraversal: startTraversal,
    getCurrentTraversal: getCurrentTraversal,
    getCurrentNodeId: getCurrentNodeId,
    getCurrentNodeIndex: getCurrentNodeIndex,
    isCurrentNodeNontion: isCurrentNodeNontion,
    nextNode: nextNode,
    prevNode: prevNode,
    goToNode: goToNode,
    setNote: setNote,
    getNote: getNote,
    completeTraversal: completeTraversal,
    getProgress: getProgress,

    // Starter traversals
    getStarterTraversals: getStarterTraversals,
    getRandomTraversal: getRandomTraversal,

    // Persistence
    loadSavedNetworks: loadSavedNetworks,
    saveCurrentNetwork: saveCurrentNetwork,
    deleteSavedNetwork: deleteSavedNetwork,
    loadNetwork: loadNetwork,
    exportNetworkJSON: exportNetworkJSON,

    // Random config
    generateRandomConfig: generateRandomConfig
  };
})();
