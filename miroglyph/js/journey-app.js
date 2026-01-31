// Journey Mapper - Application Controller
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

        // Initialize UI with dependencies
        ui.init({
          state: state,
          filters: filters,
          nodes: nodes,
          utils: utils,
          templates: templates,
          archetypes: dataLoader.get('archetypes'),
          entities: dataLoader.get('entities'),
          patterns: dataLoader.get('patterns'),
          affinities: dataLoader.get('affinities')
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
    // Start screen buttons
    document.getElementById('btn-surprise').addEventListener('click', function() {
      var traversal = state.getRandomTraversal();
      state.createJourney(traversal.sequence, traversal.name);
      ui.navigateToCurrentNode();
    });

    document.getElementById('btn-choose').addEventListener('click', function() {
      ui.renderChoosePathModal();
    });

    // Choose path modal
    document.getElementById('btn-cancel-choose').addEventListener('click', function() {
      document.getElementById('modal-choose').hidden = true;
    });

    // Node navigation
    document.getElementById('btn-prev-node').addEventListener('click', function() {
      var result = state.prevStep();
      if (result.moved) {
        ui.navigateToCurrentNode();
      }
    });

    document.getElementById('btn-skip-step').addEventListener('click', function() {
      advanceStep();
    });

    document.getElementById('btn-next-step').addEventListener('click', function() {
      advanceStep();
    });

    // Nontion screen
    document.getElementById('btn-continue-nontion').addEventListener('click', function() {
      var note = document.getElementById('nontion-note-input').value;
      var result = state.completeNontion(note);

      if (result.journeyComplete) {
        ui.showCompleteScreen();
      } else {
        ui.navigateToCurrentNode();
      }
    });

    // Complete screen buttons
    document.getElementById('btn-save-journey').addEventListener('click', function() {
      document.getElementById('modal-save').hidden = false;
      var journey = state.getJourney();
      if (journey) {
        document.getElementById('journey-name').value = journey.name || '';
      }
    });

    document.getElementById('btn-export-journey').addEventListener('click', function() {
      state.exportJourneyJSON();
    });

    document.getElementById('btn-new-journey').addEventListener('click', function() {
      state.clearJourney();
      ui.showStartScreen();
    });

    // Save modal
    document.getElementById('btn-cancel-save').addEventListener('click', function() {
      document.getElementById('modal-save').hidden = true;
    });

    document.getElementById('form-save-journey').addEventListener('submit', function(e) {
      e.preventDefault();
      var name = document.getElementById('journey-name').value.trim();
      var description = document.getElementById('journey-description').value.trim();

      if (name && state.saveCurrentJourney(name, description)) {
        document.getElementById('modal-save').hidden = true;
        alert('Journey saved successfully!');
      }
    });

    // Hash change
    window.addEventListener('hashchange', handleRoute);

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
      // Escape to close modals
      if (e.key === 'Escape') {
        document.getElementById('modal-choose').hidden = true;
        document.getElementById('modal-save').hidden = true;
      }
    });
  }

  /**
   * Advance to next step or node
   */
  function advanceStep() {
    var result = state.nextStep();

    if (result.journeyComplete) {
      ui.showCompleteScreen();
      window.location.hash = 'complete';
    } else if (result.nodeComplete) {
      ui.navigateToCurrentNode();
      updateHash();
    } else if (result.moved) {
      ui.renderSelectionStep();
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

    if (hash === 'complete') {
      var journey = state.getJourney();
      if (journey && journey.completed) {
        ui.showCompleteScreen();
      } else {
        ui.showStartScreen();
      }
      return;
    }

    if (hash.startsWith('node/')) {
      var index = parseInt(hash.split('/')[1], 10);
      var journey = state.getJourney();
      if (journey && !isNaN(index) && index >= 0 && index < journey.traversal.length) {
        journey.current_index = index;
        journey.current_step = 0;
        ui.navigateToCurrentNode();
      } else {
        ui.showStartScreen();
      }
      return;
    }

    // Default
    ui.showStartScreen();
  }

  /**
   * Update hash based on current state
   */
  function updateHash() {
    var journey = state.getJourney();
    if (!journey) {
      window.location.hash = 'start';
      return;
    }

    if (journey.completed) {
      window.location.hash = 'complete';
    } else {
      window.location.hash = 'node/' + journey.current_index;
    }
  }

  // Boot on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
