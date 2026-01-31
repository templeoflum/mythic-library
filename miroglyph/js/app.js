// Mythic System Explorer — Main Application Controller
// Boot sequence: loadAll → globalSearch → tabRouter

(function() {
  var dataLoader = window.MiroGlyph.dataLoader;
  var globalSearch = window.MiroGlyph.globalSearch;
  var tabRouter = window.MiroGlyph.tabRouter;
  var storage = window.MiroGlyph.storage;
  var paths = window.MiroGlyph.paths;
  var nodes = window.MiroGlyph.nodes;
  var canvas = window.MiroGlyph.canvas;

  // Load and apply saved configuration
  function loadConfiguration() {
    var config = storage.loadConfig();
    if (config && config.configuration) {
      nodes.setConfiguration(config.configuration);
    }
    updateOrientationLabel();
  }

  // Update the orientation label in the UI
  function updateOrientationLabel() {
    var label = document.getElementById('orientation-label');
    if (label) {
      var config = nodes.getConfiguration();
      var displayName = config === 'standard' ? 'Standard' : 'Inverted';
      label.textContent = 'Orientation: ' + displayName;
    }
  }

  // Toggle orientation and redraw
  function handleOrientationToggle() {
    var newConfig = nodes.toggleConfiguration();
    storage.saveConfig({ configuration: newConfig });
    updateOrientationLabel();

    // Redraw canvas if it's initialized
    if (canvas && canvas.init) {
      canvas.init();
    }
    if (paths && paths.redraw) {
      paths.redraw();
    }
  }

  // Set up breadcrumb trail
  function setupBreadcrumbs() {
    var nav = window.MiroGlyph.nav;
    var trailEl = document.getElementById('breadcrumb-trail');
    if (!trailEl || !nav) return;

    function renderBreadcrumbs(crumbs) {
      if (!crumbs || crumbs.length === 0) {
        trailEl.innerHTML = '';
        return;
      }

      var html = '<span style="color:var(--color-text-muted);font-size:0.7rem;margin-right:8px">Trail:</span>';
      for (var i = 0; i < crumbs.length; i++) {
        if (i > 0) {
          html += '<span class="breadcrumb-separator">&rarr;</span>';
        }
        var iconMap = {
          node: '\u25CE',      // ◎
          archetype: '\u2606', // ☆
          entity: '\u2302',    // ⌂
          pattern: '\u2261'    // ≡
        };
        var icon = iconMap[crumbs[i].type] || '';
        html += '<span class="breadcrumb-item" data-idx="' + i + '" title="' + crumbs[i].type + '">';
        html += icon + ' ' + escapeHtml(crumbs[i].name);
        html += '</span>';
      }

      trailEl.innerHTML = html;
    }

    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
    }

    // Listen for breadcrumb updates
    window.addEventListener('breadcrumbsUpdated', function(e) {
      renderBreadcrumbs(e.detail.breadcrumbs);
    });

    // Handle breadcrumb clicks
    trailEl.addEventListener('click', function(e) {
      var item = e.target.closest('.breadcrumb-item');
      if (!item) return;

      var idx = parseInt(item.dataset.idx, 10);
      var crumbs = nav.getBreadcrumbs();
      if (crumbs[idx]) {
        nav.toBreadcrumb(crumbs[idx]);
      }
    });
  }

  // Set up import/export handlers (gear menu)
  function setupImportExport() {
    var exportBtn = document.getElementById('btn-export');
    if (exportBtn) {
      exportBtn.addEventListener('click', function() {
        var exportData = {
          paths: paths.getTraversals(),
          groups: paths.getGroups()
        };
        storage.exportJSON(exportData);
      });
    }

    var importInput = document.getElementById('file-import');
    if (importInput) {
      importInput.addEventListener('change', function(e) {
        var file = e.target.files[0];
        if (!file) return;

        storage.importJSON(file).then(function(imported) {
          if (confirm('Import ' + imported.paths.length + ' traversals? This will replace current data.')) {
            storage.save(imported);
            paths.setData({ paths: imported.paths, groups: imported.groups || [] });
            alert('Import successful!');
          }
        }).catch(function(err) {
          alert('Import failed: ' + err.message);
        });

        importInput.value = '';
      });
    }

    // Gear dropdown toggle
    var gearBtn = document.getElementById('btn-gear');
    var gearDropdown = document.getElementById('gear-dropdown');
    if (gearBtn && gearDropdown) {
      gearBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        gearDropdown.hidden = !gearDropdown.hidden;
      });

      document.addEventListener('click', function() {
        gearDropdown.hidden = true;
      });
    }

    // Orientation toggle
    var orientationBtn = document.getElementById('btn-toggle-orientation');
    if (orientationBtn) {
      orientationBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        handleOrientationToggle();
      });
    }
  }

  // Boot sequence
  function boot() {
    console.log('Mythic System Explorer: loading data...');

    // 0. Load configuration (orientation) before anything else
    loadConfiguration();

    // 1. Load all catalogs and build cross-reference indices
    dataLoader.loadAll().then(function() {
      console.log('Mythic System Explorer: data loaded, initializing UI...');

      // 2. Initialize global search (depends on data indices)
      if (globalSearch) {
        globalSearch.init();
      }

      // 3. Set up import/export in gear menu
      setupImportExport();

      // 3.5. Set up breadcrumb trail
      setupBreadcrumbs();

      // 4. Initialize tab router (activates the default view based on URL hash)
      tabRouter.init();

      console.log('Mythic System Explorer initialized');
    }).catch(function(err) {
      console.error('Failed to initialize:', err);

      // Still try to show the UI even if data loading partially fails
      tabRouter.init();
    });
  }

  boot();
})();
