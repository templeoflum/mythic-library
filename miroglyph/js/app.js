// Mythic System Explorer — Main Application Controller
// Boot sequence: loadAll → globalSearch → workshop → tabRouter

(function() {
  var dataLoader = window.MiroGlyph.dataLoader;
  var globalSearch = window.MiroGlyph.globalSearch;
  var workshop = window.MiroGlyph.workshop;
  var tabRouter = window.MiroGlyph.tabRouter;
  var storage = window.MiroGlyph.storage;
  var paths = window.MiroGlyph.paths;

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
  }

  // Boot sequence
  function boot() {
    console.log('Mythic System Explorer: loading data...');

    // 1. Load all catalogs and build cross-reference indices
    dataLoader.loadAll().then(function() {
      console.log('Mythic System Explorer: data loaded, initializing UI...');

      // 2. Initialize global search (depends on data indices)
      if (globalSearch) {
        globalSearch.init();
      }

      // 3. Initialize workshop (depends on paths + storage)
      if (workshop) {
        workshop.init();
      }

      // 4. Set up import/export in gear menu
      setupImportExport();

      // 5. Initialize tab router (activates the default view based on URL hash)
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
