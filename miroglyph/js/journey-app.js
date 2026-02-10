// Journey Mapper - Application Controller (Network Configuration Model)
// Boot sequence, routing, and global event coordination

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var state = window.MiroGlyph.journeyState;
  var ui = window.MiroGlyph.journeyUI;
  var filters = window.MiroGlyph.journeyFilters;
  var dataLoader = window.MiroGlyph.dataLoader;
  var nodes = window.MiroGlyph.nodes;
  var utils = window.MiroGlyph.utils;

  var templates = null;
  var dataDeps = null;

  /**
   * Boot sequence - load data and initialize UI
   */
  function boot() {
    console.log('Journey Mapper: Initializing...');

    // Load node templates
    fetch('data/node_templates.json')
      .then(function(res) { return res.json(); })
      .then(function(data) {
        templates = data;
        console.log('Journey Mapper: Templates loaded');

        // Load catalogs
        return dataLoader.loadAll();
      })
      .then(function() {
        console.log('Journey Mapper: Catalogs loaded');

        dataDeps = {
          archetypes: dataLoader.get('archetypes'),
          entities: dataLoader.get('entities'),
          patterns: dataLoader.get('patterns'),
          affinities: dataLoader.get('affinities')
        };

        // Initialize UI with dependencies
        ui.init({
          state: state,
          filters: filters,
          nodes: nodes,
          utils: utils,
          templates: templates,
          archetypes: dataDeps.archetypes,
          entities: dataDeps.entities,
          patterns: dataDeps.patterns,
          affinities: dataDeps.affinities
        });

        // Bind global events
        bindGlobalEvents();

        // Check for hash routing
        handleRoute();

        console.log('Journey Mapper: Ready');
      })
      .catch(function(err) {
        console.error('Journey Mapper: Failed to initialize', err);
        document.getElementById('journey-main').innerHTML =
          '<div class="loading-state">Failed to load data. Please refresh the page.</div>';
      });
  }

  /**
   * Bind global UI events
   */
  function bindGlobalEvents() {
    // ===== Start Screen =====
    document.getElementById('btn-new-network').addEventListener('click', function() {
      state.resetConfigState();
      ui.showConfigScreen(1);
    });

    document.getElementById('btn-load-network').addEventListener('click', function() {
      // Toggle saved networks visibility
      var container = document.getElementById('saved-networks');
      container.hidden = !container.hidden;
      if (!container.hidden) {
        ui.renderSavedNetworks();
      }
    });

    document.getElementById('btn-surprise').addEventListener('click', function() {
      // Random config + random traversal
      state.generateRandomConfig(dataDeps);
      state.createNetwork('Random Network');
      var traversal = state.getRandomTraversal();
      state.addTraversal(traversal.name, traversal.sequence);
      state.startTraversal(0);
      ui.showTraversalScreen();
    });

    // ===== Config Screen =====
    document.getElementById('btn-config-back').addEventListener('click', function() {
      var step = state.getConfigStep();
      if (step <= 1) {
        ui.showStartScreen();
      } else {
        ui.showConfigScreen(step - 1);
      }
    });

    document.getElementById('btn-config-next').addEventListener('click', function() {
      var step = state.getConfigStep();
      if (step >= 4) {
        // Confirm & Create network
        state.createNetwork();
        ui.showNetworkScreen();
      } else {
        ui.showConfigScreen(step + 1);
      }
    });

    // ===== Network Screen =====
    document.getElementById('btn-choose-traversal').addEventListener('click', function() {
      ui.renderChooseTraversalModal();
    });

    document.getElementById('btn-surprise-traversal').addEventListener('click', function() {
      var traversal = state.getRandomTraversal();
      state.addTraversal(traversal.name, traversal.sequence);
      var network = state.getNetwork();
      var idx = network.traversals.length - 1;
      state.startTraversal(idx);
      ui.showTraversalScreen();
    });

    document.getElementById('btn-save-network').addEventListener('click', function() {
      var modal = document.getElementById('modal-save');
      var network = state.getNetwork();
      if (network) {
        document.getElementById('network-name-input').value = network.name || '';
      }
      modal.hidden = false;
    });

    document.getElementById('btn-new-network-from-network').addEventListener('click', function() {
      state.clearNetwork();
      state.resetConfigState();
      ui.showStartScreen();
    });

    // ===== Traversal Screen =====
    document.getElementById('btn-traversal-prev').addEventListener('click', function() {
      // Save note before navigating
      saveCurrentNote();
      var result = state.prevNode();
      if (result.moved) {
        ui.navigateToCurrentNode();
      }
    });

    document.getElementById('btn-traversal-next').addEventListener('click', function() {
      // Save note before navigating
      saveCurrentNote();
      var result = state.nextNode();
      if (result.journeyComplete) {
        state.completeTraversal();
        ui.showCompleteScreen();
      } else if (result.moved) {
        ui.navigateToCurrentNode();
      }
    });

    // ===== Nontion Screen =====
    document.getElementById('btn-continue-nontion').addEventListener('click', function() {
      var note = document.getElementById('nontion-note-input').value;
      state.setNote('∅', note);
      var result = state.nextNode();
      if (result.journeyComplete) {
        state.completeTraversal();
        ui.showCompleteScreen();
      } else if (result.moved) {
        ui.navigateToCurrentNode();
      }
    });

    // ===== Complete Screen =====
    document.getElementById('btn-save-complete').addEventListener('click', function() {
      var modal = document.getElementById('modal-save');
      var network = state.getNetwork();
      if (network) {
        document.getElementById('network-name-input').value = network.name || '';
      }
      modal.hidden = false;
    });

    document.getElementById('btn-export-complete').addEventListener('click', function() {
      state.exportNetworkJSON();
    });

    document.getElementById('btn-new-traversal').addEventListener('click', function() {
      ui.showNetworkScreen();
    });

    document.getElementById('btn-new-network-complete').addEventListener('click', function() {
      state.clearNetwork();
      state.resetConfigState();
      ui.showStartScreen();
    });

    // ===== Choose Traversal Modal =====
    document.getElementById('btn-cancel-traversal').addEventListener('click', function() {
      document.getElementById('modal-traversal').hidden = true;
    });

    // ===== Save Modal =====
    document.getElementById('btn-cancel-save').addEventListener('click', function() {
      document.getElementById('modal-save').hidden = true;
    });

    document.getElementById('form-save-network').addEventListener('submit', function(e) {
      e.preventDefault();
      var name = document.getElementById('network-name-input').value.trim();
      if (name && state.saveCurrentNetwork(name)) {
        document.getElementById('modal-save').hidden = true;
        alert('Network saved successfully!');
      }
    });

    // ===== Node Detail Modal =====
    document.getElementById('btn-close-node-detail').addEventListener('click', function() {
      document.getElementById('modal-node-detail').hidden = true;
    });

    // ===== Hash Change =====
    window.addEventListener('hashchange', handleRoute);

    // ===== Keyboard =====
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        document.querySelectorAll('.modal').forEach(function(m) { m.hidden = true; });
      }
    });
  }

  /**
   * Save current note from traversal textarea
   */
  function saveCurrentNote() {
    var nodeId = state.getCurrentNodeId();
    var textarea = document.getElementById('traversal-note-input');
    if (textarea && nodeId) {
      state.setNote(nodeId, textarea.value);
    }
  }

  /**
   * Handle URL hash routing
   */
  function handleRoute() {
    var hash = window.location.hash.slice(1);

    if (!hash || hash === 'start') {
      ui.showStartScreen();
      return;
    }

    if (hash.startsWith('config/')) {
      var step = parseInt(hash.split('/')[1], 10);
      if (!isNaN(step) && step >= 1 && step <= 4) {
        ui.showConfigScreen(step);
      } else {
        ui.showConfigScreen(1);
      }
      return;
    }

    if (hash === 'network') {
      var network = state.getNetwork();
      if (network) {
        ui.showNetworkScreen();
      } else {
        ui.showStartScreen();
      }
      return;
    }

    if (hash.startsWith('traversal/')) {
      var index = parseInt(hash.split('/')[1], 10);
      var traversal = state.getCurrentTraversal();
      if (traversal && !isNaN(index) && index >= 0 && index < traversal.sequence.length) {
        state.goToNode(index);
        ui.navigateToCurrentNode();
      } else {
        ui.showStartScreen();
      }
      return;
    }

    if (hash === 'complete') {
      var traversal = state.getCurrentTraversal();
      if (traversal && traversal.completed) {
        ui.showCompleteScreen();
      } else {
        ui.showStartScreen();
      }
      return;
    }

    // Default
    ui.showStartScreen();
  }

  // Boot on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
