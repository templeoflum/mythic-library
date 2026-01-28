// MiroGlyph — Topology Tab
// Wraps the existing traversal editor into the tab lifecycle

(function() {
  const { nodes, canvas, storage, paths, enrichment, tabRouter } = window.MiroGlyph;

  let data = null;

  function init(container) {
    data = storage.load();
    canvas.init();
    paths.init({ paths: data.paths || [], groups: data.groups || [] }, handlePathsChange);
    setupCanvasEvents();
    setupControlEvents();
    setupModalEvents();
    setupGroupModalEvents();

    if (enrichment) {
      enrichment.load('data/node_profiles.json', 'data/archetype_affinities.json');
    }
  }

  function activate() {
    // Redraw on reactivation in case window was resized while on another tab
    if (data) {
      canvas.init();
      paths.redraw && paths.redraw();
    }
  }

  function deactivate() {}

  function handlePathsChange(pathsData) {
    data.paths = pathsData.paths;
    data.groups = pathsData.groups;
    storage.save(data);
  }

  function setupCanvasEvents() {
    const svgCanvas = document.getElementById('canvas');

    svgCanvas.addEventListener('click', function(e) {
      const nodeId = canvas.getNodeFromEvent(e);
      if (nodeId) paths.handleNodeClick(nodeId);
    });

    svgCanvas.addEventListener('mouseover', function(e) {
      const nodeId = canvas.getNodeFromEvent(e);
      if (nodeId) showNodeInfo(nodeId);
    });

    svgCanvas.addEventListener('mouseout', function(e) {
      const nodeGroup = e.target.closest('.node-group');
      if (nodeGroup) clearNodeInfo();
    });
  }

  function showNodeInfo(nodeId) {
    const node = nodes.getNode(nodeId);
    const container = document.getElementById('node-info');
    if (!node || !container) return;

    if (nodeId === '\u2205') {
      container.innerHTML =
        '<div class="node-id" style="color: ' + node.color + '">' + node.displayName + '</div>' +
        '<div class="node-role">' + node.role + '</div>' +
        '<p style="margin-top: 0.5rem; font-size: 0.8rem; color: #94a3b8;">' + node.description + '</p>';
    } else {
      container.innerHTML =
        '<div class="node-id" style="color: ' + node.arc.color + '">' + node.id + '</div>' +
        '<div class="node-title">' + node.title + '</div>' +
        '<div class="node-role">' + node.role + '</div>' +
        '<div class="node-arc">Arc: ' + node.arc.primary + '/' + node.arc.secondary + '</div>' +
        '<div class="node-condition">Condition: ' + node.condition.primary + '/' + node.condition.secondary + '</div>' +
        '<div style="margin-top: 0.5rem; font-size: 0.8rem; color: #94a3b8;">' +
        node.tone.join(' \u00b7 ') + '</div>';
    }

    if (enrichment && enrichment.isLoaded()) {
      enrichment.renderNodeEnrichment(nodeId);
    }
  }

  function clearNodeInfo() {
    const container = document.getElementById('node-info');
    if (container) {
      container.innerHTML = '<p class="hint">Hover over a node to see details.</p>';
    }
    if (enrichment && enrichment.isLoaded()) {
      enrichment.clearEnrichment();
    }
  }

  function setupControlEvents() {
    var undoBtn = document.getElementById('btn-undo');
    if (undoBtn) undoBtn.addEventListener('click', function() { paths.undo(); });

    var clearBtn = document.getElementById('btn-clear-path');
    if (clearBtn) clearBtn.addEventListener('click', function() { paths.clearSequence(); });

    var saveBtn = document.getElementById('btn-save-path');
    if (saveBtn) saveBtn.addEventListener('click', function() { paths.showSaveModal(); });
  }

  function setupModalEvents() {
    var modal = document.getElementById('modal-save-path');
    var form = document.getElementById('form-save-path');
    var cancelBtn = document.getElementById('btn-cancel-save');
    var colorInput = document.getElementById('path-color');

    document.querySelectorAll('.color-preset').forEach(function(btn) {
      btn.addEventListener('click', function() {
        if (colorInput) colorInput.value = btn.dataset.color;
        document.querySelectorAll('.color-preset').forEach(function(b) { b.classList.remove('selected'); });
        btn.classList.add('selected');
      });
    });

    if (cancelBtn) cancelBtn.addEventListener('click', function() { paths.hideSaveModal(); });
    if (modal) modal.addEventListener('click', function(e) {
      if (e.target === modal) paths.hideSaveModal();
    });

    if (form) {
      form.addEventListener('submit', function(e) {
        e.preventDefault();
        var name = document.getElementById('path-name').value;
        var color = document.getElementById('path-color').value;
        var description = document.getElementById('path-description').value;
        var groupId = document.getElementById('path-group').value;
        if (name.trim()) {
          paths.saveTraversal(name, color, description, groupId || null);
          paths.hideSaveModal();
        }
      });
    }
  }

  function setupGroupModalEvents() {
    var addGroupBtn = document.getElementById('btn-add-group');
    var modal = document.getElementById('modal-group');
    var form = document.getElementById('form-group');
    var cancelBtn = document.getElementById('btn-cancel-group');

    if (addGroupBtn) addGroupBtn.addEventListener('click', function() { paths.showGroupModal(); });
    if (cancelBtn) cancelBtn.addEventListener('click', function() { paths.hideGroupModal(); });
    if (modal) modal.addEventListener('click', function(e) {
      if (e.target === modal) paths.hideGroupModal();
    });

    if (form) {
      form.addEventListener('submit', function(e) {
        e.preventDefault();
        var name = document.getElementById('group-name').value;
        if (name.trim()) {
          paths.saveGroup(name);
          paths.hideGroupModal();
        }
      });
    }
  }

  tabRouter.register('topology', { init: init, activate: activate, deactivate: deactivate });
})();
