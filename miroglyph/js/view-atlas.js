// Mythic System Explorer — Atlas View
// SVG map with node selection, hover tooltips, drawer integration, and workshop support

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var canvas = window.MiroGlyph.canvas;
  var enrichment = window.MiroGlyph.enrichment;
  var nodeDrawer = window.MiroGlyph.nodeDrawer;
  var nodes = window.MiroGlyph.nodes;
  var nav = window.MiroGlyph.nav;
  var paths = window.MiroGlyph.paths;
  var tabRouter = window.MiroGlyph.tabRouter;

  var tooltip = null;
  var initialized = false;

  function init() {
    canvas.init();
    enrichment.load();
    setupCanvasEvents();
    createTooltip();
    initialized = true;
  }

  function activate() {
    canvas.init();
    if (paths && paths.redraw) {
      paths.redraw();
    }
    showPickerIfWorkshopOpen();
  }

  function deactivate() {
    hideTooltip();
  }

  function onRoute(params) {
    if (!params) return;

    var subview = params.subview;
    if (!subview) {
      // No sub-route: close drawer if open
      if (nodeDrawer && nodeDrawer.isOpen()) {
        nodeDrawer.close();
      }
      return;
    }

    // Check if the subview is a node ID (like D3, R1, E6, or the Nontion symbol)
    var nodeData = nodes.getNode(subview);
    if (nodeData) {
      openNodeDrawer(subview);
    }
  }

  // --- Canvas Events ---

  function setupCanvasEvents() {
    var svgCanvas = document.getElementById('canvas');
    if (!svgCanvas) return;

    svgCanvas.addEventListener('click', function(e) {
      var nodeId = canvas.getNodeFromEvent(e);
      if (!nodeId) return;

      // If workshop is open, add node to workshop sequence
      if (isWorkshopOpen()) {
        if (paths) {
          paths.handleNodeClick(nodeId);
        }
        return;
      }

      // Otherwise open the node drawer
      openNodeDrawer(nodeId);
      nav.toNode(nodeId);
    });

    svgCanvas.addEventListener('mouseover', function(e) {
      var nodeId = canvas.getNodeFromEvent(e);
      if (nodeId) {
        showTooltip(e, nodeId);
      }
    });

    svgCanvas.addEventListener('mousemove', function(e) {
      var nodeId = canvas.getNodeFromEvent(e);
      if (nodeId) {
        positionTooltip(e);
      } else {
        hideTooltip();
      }
    });

    svgCanvas.addEventListener('mouseout', function(e) {
      var nodeGroup = e.target.closest('.node-group');
      if (nodeGroup) {
        hideTooltip();
      }
    });
  }

  // --- Node Drawer Integration ---

  function openNodeDrawer(nodeId) {
    if (canvas.selectNode) {
      canvas.selectNode(nodeId);
    }
    if (nodeDrawer) {
      nodeDrawer.open(nodeId);
    }
  }

  // --- Tooltip ---

  function createTooltip() {
    if (tooltip) return;
    tooltip = document.createElement('div');
    tooltip.className = 'atlas-tooltip';
    tooltip.style.cssText = 'position:fixed;pointer-events:none;z-index:100;' +
      'background:rgba(15,23,42,0.95);color:#f1f5f9;padding:6px 10px;' +
      'border-radius:6px;font-size:0.75rem;border:1px solid #475569;' +
      'opacity:0;transition:opacity 0.15s ease;max-width:220px;';
    document.body.appendChild(tooltip);
  }

  function showTooltip(e, nodeId) {
    if (!tooltip) return;

    var node = nodes.getNode(nodeId);
    if (!node) return;

    var title = '';
    var role = '';

    if (nodeId === '\u2205') {
      title = 'Nontion';
      role = node.role || '';
    } else {
      title = nodeId + ' \u2014 ' + (node.title || '');
      role = node.role || '';
    }

    tooltip.innerHTML =
      '<div style="font-weight:600;margin-bottom:2px;">' + escapeHtml(title) + '</div>' +
      '<div style="color:#94a3b8;font-style:italic;">' + escapeHtml(role) + '</div>';
    tooltip.style.opacity = '1';
    positionTooltip(e);
  }

  function positionTooltip(e) {
    if (!tooltip) return;
    var x = e.clientX + 14;
    var y = e.clientY + 14;

    // Keep tooltip within viewport
    var rect = tooltip.getBoundingClientRect();
    if (x + rect.width > window.innerWidth - 10) {
      x = e.clientX - rect.width - 14;
    }
    if (y + rect.height > window.innerHeight - 10) {
      y = e.clientY - rect.height - 14;
    }

    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';
  }

  function hideTooltip() {
    if (tooltip) {
      tooltip.style.opacity = '0';
    }
  }

  // --- Workshop Integration ---

  function isWorkshopOpen() {
    var panel = document.getElementById('workshop-panel');
    return panel && !panel.classList.contains('workshop-closed');
  }

  function showPickerIfWorkshopOpen() {
    // When atlas is active, the canvas serves as the picker, so hide the node picker grid
    var picker = document.getElementById('workshop-node-picker');
    if (picker && isWorkshopOpen()) {
      picker.hidden = true;
    }
  }

  // --- Utility ---

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  tabRouter.register('atlas', {
    init: init,
    activate: activate,
    deactivate: deactivate,
    onRoute: onRoute
  });
})();
