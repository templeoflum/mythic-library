// Mythic System Explorer - Main Application Controller

(function() {
  const { storage, paths, tabRouter } = window.MiroGlyph;

  // Set up import/export handlers (global, not tab-specific)
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
      importInput.addEventListener('change', async function(e) {
        var file = e.target.files[0];
        if (!file) return;

        try {
          var imported = await storage.importJSON(file);

          if (confirm('Import ' + imported.paths.length + ' traversals? This will replace current data.')) {
            storage.save(imported);
            paths.setData({ paths: imported.paths, groups: imported.groups || [] });
            alert('Import successful!');
          }
        } catch (err) {
          alert('Import failed: ' + err.message);
        }

        importInput.value = '';
      });
    }
  }

  setupImportExport();
  tabRouter.init();

  console.log('Mythic System Explorer initialized');
})();
