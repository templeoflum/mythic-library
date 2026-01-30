// Mythic System Explorer — Traversal Workshop
// Slide-over panel for building and managing traversals from any view

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var paths = window.MiroGlyph.paths;
  var storage = window.MiroGlyph.storage;
  var tabRouter = window.MiroGlyph.tabRouter;
  var nodes = window.MiroGlyph.nodes;

  var panelEl = null;
  var overlayEl = null;
  var pickerEl = null;
  var isOpen = false;

  function init() {
    panelEl = document.getElementById('workshop-panel');
    overlayEl = document.getElementById('workshop-overlay');
    pickerEl = document.getElementById('workshop-node-picker');

    if (!panelEl) return;

    // Open/close button
    var openBtn = document.getElementById('btn-workshop');
    if (openBtn) {
      openBtn.addEventListener('click', toggle);
    }

    var closeBtn = document.getElementById('workshop-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', close);
    }

    // Overlay click to close
    if (overlayEl) {
      overlayEl.addEventListener('click', close);
    }

    // Undo / Clear / Save buttons
    var undoBtn = document.getElementById('ws-btn-undo');
    if (undoBtn) {
      undoBtn.addEventListener('click', function() {
        if (paths) paths.undo();
      });
    }

    var clearBtn = document.getElementById('ws-btn-clear');
    if (clearBtn) {
      clearBtn.addEventListener('click', function() {
        if (paths) paths.clearSequence();
      });
    }

    var saveBtn = document.getElementById('ws-btn-save');
    if (saveBtn) {
      saveBtn.addEventListener('click', function() {
        if (paths) paths.showSaveModal();
      });
    }

    // Add group button
    var addGroupBtn = document.getElementById('ws-btn-add-group');
    if (addGroupBtn) {
      addGroupBtn.addEventListener('click', function() {
        if (paths) paths.showGroupModal();
      });
    }

    // Save path form
    var saveForm = document.getElementById('form-save-path');
    if (saveForm) {
      saveForm.addEventListener('submit', function(e) {
        e.preventDefault();
        var name = document.getElementById('path-name').value;
        var color = document.getElementById('path-color').value;
        var desc = document.getElementById('path-description').value;
        var group = document.getElementById('path-group').value;

        if (paths) {
          paths.saveTraversal(name, color, desc, group);
          paths.hideSaveModal();
          // Auto-save to storage
          saveToStorage();
        }
      });
    }

    var cancelSaveBtn = document.getElementById('btn-cancel-save');
    if (cancelSaveBtn) {
      cancelSaveBtn.addEventListener('click', function() {
        if (paths) paths.hideSaveModal();
      });
    }

    // Group form
    var groupForm = document.getElementById('form-group');
    if (groupForm) {
      groupForm.addEventListener('submit', function(e) {
        e.preventDefault();
        var name = document.getElementById('group-name').value;
        if (paths) {
          paths.saveGroup(name);
          paths.hideGroupModal();
          saveToStorage();
        }
      });
    }

    var cancelGroupBtn = document.getElementById('btn-cancel-group');
    if (cancelGroupBtn) {
      cancelGroupBtn.addEventListener('click', function() {
        if (paths) paths.hideGroupModal();
      });
    }

    // Color preset clicks
    var colorPresets = document.getElementById('color-presets');
    if (colorPresets) {
      colorPresets.addEventListener('click', function(e) {
        var btn = e.target.closest('.color-preset');
        if (btn && btn.dataset.color) {
          var colorInput = document.getElementById('path-color');
          if (colorInput) colorInput.value = btn.dataset.color;

          // Update selected state
          colorPresets.querySelectorAll('.color-preset').forEach(function(b) {
            b.classList.toggle('selected', b === btn);
          });
        }
      });
    }

    // Initialize paths module with stored data
    var storedData = storage.load();
    paths.init(storedData, function(data) {
      saveToStorage();
    });

    // Build node picker grid
    buildNodePicker();

    // Listen for view changes to update picker visibility
    window.addEventListener('hashchange', function() {
      if (isOpen) {
        updateNodePicker();
      }
    });
  }

  function toggle() {
    if (isOpen) {
      close();
    } else {
      open();
    }
  }

  function open() {
    if (!panelEl) return;
    isOpen = true;
    panelEl.classList.remove('workshop-closed');
    if (overlayEl) overlayEl.hidden = false;

    // Show/hide node picker based on current view
    updateNodePicker();
  }

  function close() {
    if (!panelEl) return;
    isOpen = false;
    panelEl.classList.add('workshop-closed');
    if (overlayEl) overlayEl.hidden = true;
  }

  function getIsOpen() {
    return isOpen;
  }

  // Show node picker when NOT on atlas view (since atlas uses the map directly)
  function updateNodePicker() {
    if (!pickerEl) return;
    var currentView = tabRouter.getActiveView();
    pickerEl.hidden = (currentView === 'atlas');
  }

  // Build a compact grid of clickable node buttons for non-atlas views
  function buildNodePicker() {
    if (!pickerEl) return;
    var grid = document.getElementById('workshop-picker-grid');
    if (!grid) return;

    var ARCS = [
      { code: 'D', name: 'Descent', color: 'var(--color-descent)' },
      { code: 'R', name: 'Resonance', color: 'var(--color-resonance)' },
      { code: 'E', name: 'Emergence', color: 'var(--color-emergence)' }
    ];

    var html = '';

    // Arc nodes (6 each) - one row per arc
    for (var a = 0; a < ARCS.length; a++) {
      var arc = ARCS[a];
      for (var c = 1; c <= 6; c++) {
        var nodeId = arc.code + c;
        html += '<button class="picker-node picker-node-' + arc.code + '" data-node-id="' + nodeId +
          '" style="border-color:' + arc.color + ';color:' + arc.color + ';background:' + arc.color + '22">' +
          nodeId + '</button>';
      }
    }

    // Nontion (spans full width)
    html += '<button class="picker-node picker-node-nontion" data-node-id="\u2205"' +
      ' style="border-color:var(--color-nontion);color:var(--color-nontion);background:rgba(245,158,11,0.1)">' +
      '\u2205 Nontion</button>';

    grid.innerHTML = html;

    // Click handler for picker nodes
    grid.addEventListener('click', function(e) {
      var btn = e.target.closest('.picker-node');
      if (btn && btn.dataset.nodeId) {
        if (paths) paths.handleNodeClick(btn.dataset.nodeId);
      }
    });
  }

  function saveToStorage() {
    if (!paths) return;
    storage.save({
      paths: paths.getTraversals(),
      groups: paths.getGroups()
    });
  }

  window.MiroGlyph.workshop = {
    init: init,
    open: open,
    close: close,
    toggle: toggle,
    isOpen: getIsOpen,
    updateNodePicker: updateNodePicker
  };
})();
