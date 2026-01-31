// Journey Mapper - State Management
// Handles journey state, traversal progression, and LocalStorage persistence

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var JOURNEYS_STORAGE_KEY = 'miroglyph_journeys';

  // Predefined traversals for "Surprise Me"
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

  // Selection steps for each node
  var SELECTION_STEPS = ['archetype', 'entity', 'motif', 'note'];

  // Current journey state
  var currentJourney = null;

  /**
   * Create a new journey with the given traversal
   * @param {Array} sequence - Array of node IDs
   * @param {string} name - Optional name for the journey
   * @returns {Object} - New journey state
   */
  function createJourney(sequence, name) {
    var utils = window.MiroGlyph.utils;

    currentJourney = {
      journey_id: utils.uuid(),
      name: name || 'Unnamed Journey',
      traversal: sequence,
      current_index: 0,
      current_step: 0, // 0=archetype, 1=entity, 2=motif, 3=note
      nodes: sequence.map(function(nodeId) {
        return {
          node_id: nodeId,
          archetype: null,
          entity: null,
          motif: null,
          note: ''
        };
      }),
      created_date: new Date().toISOString(),
      completed: false
    };

    return currentJourney;
  }

  /**
   * Get the current journey state
   * @returns {Object|null}
   */
  function getJourney() {
    return currentJourney;
  }

  /**
   * Get the current node being edited
   * @returns {Object|null}
   */
  function getCurrentNode() {
    if (!currentJourney) return null;
    return currentJourney.nodes[currentJourney.current_index] || null;
  }

  /**
   * Get the current node ID
   * @returns {string|null}
   */
  function getCurrentNodeId() {
    if (!currentJourney) return null;
    return currentJourney.traversal[currentJourney.current_index] || null;
  }

  /**
   * Get current step name
   * @returns {string}
   */
  function getCurrentStepName() {
    if (!currentJourney) return SELECTION_STEPS[0];
    return SELECTION_STEPS[currentJourney.current_step] || SELECTION_STEPS[0];
  }

  /**
   * Check if current node is Nontion
   * @returns {boolean}
   */
  function isCurrentNodeNontion() {
    return getCurrentNodeId() === '∅';
  }

  /**
   * Set selection for current step
   * @param {string} stepName - 'archetype', 'entity', 'motif', or 'note'
   * @param {*} value - The selection value
   */
  function setSelection(stepName, value) {
    var node = getCurrentNode();
    if (!node) return;

    if (stepName === 'archetype') {
      node.archetype = value;
    } else if (stepName === 'entity') {
      node.entity = value;
    } else if (stepName === 'motif') {
      node.motif = value;
    } else if (stepName === 'note') {
      node.note = value || '';
    }
  }

  /**
   * Get selection for current step
   * @param {string} stepName
   * @returns {*}
   */
  function getSelection(stepName) {
    var node = getCurrentNode();
    if (!node) return null;
    return node[stepName];
  }

  /**
   * Advance to next step
   * @returns {Object} - { moved: boolean, newStep: string, nodeComplete: boolean, journeyComplete: boolean }
   */
  function nextStep() {
    if (!currentJourney) return { moved: false };

    var nextStepIndex = currentJourney.current_step + 1;

    if (nextStepIndex >= SELECTION_STEPS.length) {
      // Node complete, move to next node
      return nextNode();
    }

    currentJourney.current_step = nextStepIndex;
    return {
      moved: true,
      newStep: SELECTION_STEPS[nextStepIndex],
      nodeComplete: false,
      journeyComplete: false
    };
  }

  /**
   * Go back to previous step
   * @returns {Object}
   */
  function prevStep() {
    if (!currentJourney) return { moved: false };

    if (currentJourney.current_step > 0) {
      currentJourney.current_step--;
      return {
        moved: true,
        newStep: SELECTION_STEPS[currentJourney.current_step],
        nodeComplete: false
      };
    }

    // At first step of current node, go to previous node
    return prevNode();
  }

  /**
   * Advance to next node
   * @returns {Object}
   */
  function nextNode() {
    if (!currentJourney) return { moved: false };

    var nextIndex = currentJourney.current_index + 1;

    if (nextIndex >= currentJourney.traversal.length) {
      // Journey complete
      currentJourney.completed = true;
      return {
        moved: true,
        nodeComplete: true,
        journeyComplete: true
      };
    }

    currentJourney.current_index = nextIndex;
    currentJourney.current_step = 0;

    return {
      moved: true,
      newStep: SELECTION_STEPS[0],
      nodeComplete: true,
      journeyComplete: false
    };
  }

  /**
   * Go back to previous node
   * @returns {Object}
   */
  function prevNode() {
    if (!currentJourney || currentJourney.current_index === 0) {
      return { moved: false };
    }

    currentJourney.current_index--;
    currentJourney.current_step = SELECTION_STEPS.length - 1; // Go to last step of previous node

    return {
      moved: true,
      newStep: SELECTION_STEPS[currentJourney.current_step],
      nodeComplete: false
    };
  }

  /**
   * Complete Nontion node (no selections, just optional note)
   * @param {string} note - Optional note
   * @returns {Object}
   */
  function completeNontion(note) {
    var node = getCurrentNode();
    if (node) {
      node.note = note || '';
    }
    return nextNode();
  }

  /**
   * Get a random traversal from starter set
   * @returns {Object} - { name, sequence }
   */
  function getRandomTraversal() {
    var index = Math.floor(Math.random() * STARTER_TRAVERSALS.length);
    return STARTER_TRAVERSALS[index];
  }

  /**
   * Get all starter traversals
   * @returns {Array}
   */
  function getStarterTraversals() {
    return STARTER_TRAVERSALS.slice();
  }

  // ========== LocalStorage Persistence ==========

  /**
   * Load saved journeys from LocalStorage
   * @returns {Object} - { version, journeys: [] }
   */
  function loadSavedJourneys() {
    try {
      var data = localStorage.getItem(JOURNEYS_STORAGE_KEY);
      if (data) {
        var parsed = JSON.parse(data);
        return {
          version: parsed.version || '1.0.0',
          journeys: parsed.journeys || []
        };
      }
    } catch (e) {
      console.error('Failed to load journeys:', e);
    }
    return { version: '1.0.0', journeys: [] };
  }

  /**
   * Save journeys to LocalStorage
   * @param {Array} journeys - Array of journey objects
   */
  function saveJourneys(journeys) {
    try {
      var data = {
        version: '1.0.0',
        lastModified: new Date().toISOString(),
        journeys: journeys
      };
      localStorage.setItem(JOURNEYS_STORAGE_KEY, JSON.stringify(data));
      return true;
    } catch (e) {
      console.error('Failed to save journeys:', e);
      return false;
    }
  }

  /**
   * Save current journey to LocalStorage
   * @param {string} name - Journey name
   * @param {string} description - Optional description
   * @returns {boolean}
   */
  function saveCurrentJourney(name, description) {
    if (!currentJourney) return false;

    currentJourney.name = name || currentJourney.name;
    currentJourney.description = description || '';
    currentJourney.saved_date = new Date().toISOString();

    var saved = loadSavedJourneys();
    saved.journeys.push(JSON.parse(JSON.stringify(currentJourney)));
    return saveJourneys(saved.journeys);
  }

  /**
   * Delete a saved journey
   * @param {string} journeyId - Journey ID to delete
   * @returns {boolean}
   */
  function deleteSavedJourney(journeyId) {
    var saved = loadSavedJourneys();
    saved.journeys = saved.journeys.filter(function(j) {
      return j.journey_id !== journeyId;
    });
    return saveJourneys(saved.journeys);
  }

  /**
   * Resume a saved journey
   * @param {string} journeyId - Journey ID to resume
   * @returns {Object|null}
   */
  function resumeJourney(journeyId) {
    var saved = loadSavedJourneys();
    var journey = saved.journeys.find(function(j) {
      return j.journey_id === journeyId;
    });

    if (journey) {
      currentJourney = JSON.parse(JSON.stringify(journey));
      return currentJourney;
    }
    return null;
  }

  /**
   * Export current journey as JSON
   */
  function exportJourneyJSON() {
    if (!currentJourney) return;

    var exportData = {
      miroglyph_version: '4.0.0',
      type: 'journey',
      exported_at: new Date().toISOString(),
      journey: currentJourney
    };

    var blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob);

    var a = document.createElement('a');
    a.href = url;
    var safeName = (currentJourney.name || 'journey').replace(/[^a-z0-9]/gi, '_').toLowerCase();
    a.download = 'miroglyph_journey_' + safeName + '.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  /**
   * Clear current journey
   */
  function clearJourney() {
    currentJourney = null;
  }

  /**
   * Get journey progress info
   * @returns {Object} - { currentIndex, total, percentage }
   */
  function getProgress() {
    if (!currentJourney) return { currentIndex: 0, total: 0, percentage: 0 };

    return {
      currentIndex: currentJourney.current_index,
      total: currentJourney.traversal.length,
      percentage: Math.round((currentJourney.current_index / currentJourney.traversal.length) * 100)
    };
  }

  // Export
  window.MiroGlyph.journeyState = {
    createJourney: createJourney,
    getJourney: getJourney,
    getCurrentNode: getCurrentNode,
    getCurrentNodeId: getCurrentNodeId,
    getCurrentStepName: getCurrentStepName,
    isCurrentNodeNontion: isCurrentNodeNontion,
    setSelection: setSelection,
    getSelection: getSelection,
    nextStep: nextStep,
    prevStep: prevStep,
    nextNode: nextNode,
    prevNode: prevNode,
    completeNontion: completeNontion,
    getRandomTraversal: getRandomTraversal,
    getStarterTraversals: getStarterTraversals,
    loadSavedJourneys: loadSavedJourneys,
    saveCurrentJourney: saveCurrentJourney,
    deleteSavedJourney: deleteSavedJourney,
    resumeJourney: resumeJourney,
    exportJourneyJSON: exportJourneyJSON,
    clearJourney: clearJourney,
    getProgress: getProgress,
    SELECTION_STEPS: SELECTION_STEPS
  };
})();
