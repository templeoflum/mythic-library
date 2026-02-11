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
          patterns: dataLoader.get('patterns')
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
          patterns: dataDeps.patterns
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
      // Random config → straight to network screen
      state.generateRandomConfig(dataDeps);
      state.createNetwork('Random Network');
      ui.showNetworkScreen();
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
