// Mythic System Explorer — Atlas View
// Three-pane layout: Node Info | Canvas | Traversals

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var canvas = window.MiroGlyph.canvas;
  var enrichment = window.MiroGlyph.enrichment;
  var nodes = window.MiroGlyph.nodes;
  var paths = window.MiroGlyph.paths;
  var storage = window.MiroGlyph.storage;
  var tabRouter = window.MiroGlyph.tabRouter;

  var tooltip = null;
  var currentNodeId = null;
  var initialized = false;

  // =========================================================================
  // Initialization
  // =========================================================================

  function init() {
    canvas.init();
    enrichment.load();
    setupCanvasEvents();
    setupTraversalControls();
    createTooltip();

    // Initialize paths with stored data
    var storedData = storage.load();
    paths.init(storedData, function() {
      saveToStorage();
    });

    initialized = true;
  }

  function activate() {
    canvas.init();
    if (paths && paths.redraw) {
      paths.redraw();
    }
  }

  function deactivate() {
    hideTooltip();
  }

  function onRoute(params) {
    if (!params) return;

    var subview = params.subview;
    if (subview) {
      // Check if the subview is a node ID
      var nodeData = nodes.getNode(subview);
      if (nodeData) {
        updateNodePanel(subview);
      }
    }
  }

  // =========================================================================
  // Canvas Events
  // =========================================================================

  function setupCanvasEvents() {
    var svgCanvas = document.getElementById('canvas');
    if (!svgCanvas) return;

    svgCanvas.addEventListener('click', function(e) {
      var nodeId = canvas.getNodeFromEvent(e);
      if (!nodeId) return;

      // Always: add to sequence AND show in node panel
      if (paths) {
        paths.handleNodeClick(nodeId);
      }
      updateNodePanel(nodeId);
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

  // =========================================================================
  // Traversal Controls (Right Panel)
  // =========================================================================

  function setupTraversalControls() {
    // Undo button
    var undoBtn = document.getElementById('btn-undo');
    if (undoBtn) {
      undoBtn.addEventListener('click', function() {
        if (paths) paths.undo();
      });
    }

    // Clear button
    var clearBtn = document.getElementById('btn-clear');
    if (clearBtn) {
      clearBtn.addEventListener('click', function() {
        if (paths) paths.clearSequence();
      });
    }

    // Save button
    var saveBtn = document.getElementById('btn-save');
    if (saveBtn) {
      saveBtn.addEventListener('click', function() {
        if (paths) paths.showSaveModal();
      });
    }

    // Add group button
    var addGroupBtn = document.getElementById('btn-add-group');
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
  }

  function saveToStorage() {
    if (!paths) return;
    storage.save({
      paths: paths.getTraversals(),
      groups: paths.getGroups()
    });
  }

  // =========================================================================
  // Node Panel (Left Panel)
  // =========================================================================

  function updateNodePanel(nodeId) {
    currentNodeId = nodeId;
    var panelBody = document.getElementById('node-panel-body');
    if (!panelBody) return;

    var node = nodes.getNode(nodeId);
    if (!node) {
      panelBody.innerHTML = '<div class="node-panel-empty"><p>Node not found</p></div>';
      return;
    }

    var isNontion = nodeId === '\u2205';
    var arcColor = isNontion ? 'var(--color-nontion)' :
      (node.arc ? 'var(--color-' + node.arc.primary.toLowerCase() + ')' : 'var(--color-text)');

    var html = '<div class="node-info">';

    // Header
    html += '<div class="node-info-header">';
    html += '<div class="node-info-id" style="color:' + arcColor + '">' + escapeHtml(nodeId) + '</div>';

    if (isNontion) {
      html += '<div class="node-info-title">' + escapeHtml(node.displayName || 'Nontion') + '</div>';
      html += '<div class="node-info-role">' + escapeHtml(node.role || '') + '</div>';
    } else {
      html += '<div class="node-info-title">' + escapeHtml(node.title || '') + '</div>';
      html += '<div class="node-info-role">' + escapeHtml(node.role || '') + '</div>';

      // Tones
      if (node.tone && node.tone.length > 0) {
        html += '<div class="node-info-tones">';
        for (var i = 0; i < node.tone.length; i++) {
          html += '<span class="node-tone-tag">' + escapeHtml(node.tone[i]) + '</span>';
        }
        html += '</div>';
      }
    }
    html += '</div>';

    // Arc & Condition Info
    if (!isNontion && node.arc && node.condition) {
      html += '<div class="node-info-section">';
      html += '<div class="node-info-section-title">Arc</div>';
      html += '<div style="color:' + arcColor + ';font-weight:600">';
      html += escapeHtml(node.arc.primary) + ' <span style="color:var(--color-text-muted);font-weight:400">(' + escapeHtml(node.arc.secondary) + ')</span>';
      html += '</div>';
      html += '</div>';

      html += '<div class="node-info-section">';
      html += '<div class="node-info-section-title">Condition</div>';
      html += '<div>' + escapeHtml(node.condition.primary) + ' <span style="color:var(--color-text-muted)">(' + escapeHtml(node.condition.secondary) + ')</span></div>';
      html += '</div>';
    }

    // Polarity (opposite condition in same arc)
    if (!isNontion && node.condition) {
      var polarityMap = { 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1 };
      var polarCondition = polarityMap[node.condition.code];
      if (polarCondition) {
        var polarNodeId = node.arc.code + polarCondition;
        var polarNode = nodes.getNode(polarNodeId);
        if (polarNode) {
          html += '<div class="node-info-section">';
          html += '<div class="node-info-section-title">Polarity</div>';
          html += '<div class="node-polarity">';
          html += '<div class="node-polarity-card" data-node-id="' + polarNodeId + '">';
          html += '<div class="node-polarity-id" style="color:' + arcColor + '">' + polarNodeId + '</div>';
          html += '<div class="node-polarity-title">' + escapeHtml(polarNode.title || '') + '</div>';
          html += '</div>';
          html += '</div>';
          html += '</div>';
        }
      }
    }

    // Condition Siblings (same condition, different arcs)
    if (!isNontion && node.condition) {
      var arcs = ['D', 'R', 'E'];
      var condition = node.condition.code;

      html += '<div class="node-info-section">';
      html += '<div class="node-info-section-title">Condition ' + condition + ' Across Arcs</div>';
      html += '<div class="node-siblings">';
      for (var a = 0; a < arcs.length; a++) {
        var sibId = arcs[a] + condition;
        var sibColor = 'var(--color-' + (arcs[a] === 'D' ? 'descent' : arcs[a] === 'R' ? 'resonance' : 'emergence') + ')';
        var isCurrent = sibId === nodeId;
        html += '<div class="node-sibling-chip' + (isCurrent ? ' current' : '') + '" ';
        html += 'style="' + (isCurrent ? '' : 'border:1px solid ' + sibColor + ';color:' + sibColor) + '" ';
        html += 'data-node-id="' + sibId + '">' + sibId + '</div>';
      }
      html += '</div>';
      html += '</div>';
    }

    html += '</div>';
    panelBody.innerHTML = html;

    // Wire click events for navigation
    panelBody.querySelectorAll('[data-node-id]').forEach(function(el) {
      el.addEventListener('click', function() {
        var targetId = el.getAttribute('data-node-id');
        if (targetId && targetId !== currentNodeId) {
          // Add to sequence and update panel
          if (paths) paths.handleNodeClick(targetId);
          updateNodePanel(targetId);
        }
      });
    });
  }

  // =========================================================================
  // Tooltip
  // =========================================================================

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

  // =========================================================================
  // Utility
  // =========================================================================

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // =========================================================================
  // Register View
  // =========================================================================

  tabRouter.register('atlas', {
    init: init,
    activate: activate,
    deactivate: deactivate,
    onRoute: onRoute
  });
})();
