// MiroGlyph v4 - Traversals (Path Creation and Management)

(function() {
  const { canvas, storage } = window.MiroGlyph;

  // Expanded color palette - 40 colors
  const COLOR_PALETTE = [
    // Row 1: Reds & Pinks
    '#ef4444', '#f87171', '#fca5a5', '#fecaca',
    '#ec4899', '#f472b6', '#f9a8d4', '#fbcfe8',
    '#e11d48', '#fb7185',
    // Row 2: Oranges & Yellows
    '#f97316', '#fb923c', '#fdba74', '#fed7aa',
    '#eab308', '#facc15', '#fde047', '#fef08a',
    '#f59e0b', '#fbbf24',
    // Row 3: Greens & Teals
    '#22c55e', '#4ade80', '#86efac', '#bbf7d0',
    '#14b8a6', '#2dd4bf', '#5eead4', '#99f6e4',
    '#10b981', '#34d399',
    // Row 4: Blues & Purples
    '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe',
    '#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe',
    '#6366f1', '#818cf8'
  ];

  // State
  let traversals = [];
  let groups = [];
  let currentSequence = [];
  let visibleTraversals = new Set();
  let collapsedGroups = new Set();
  let editingPathId = null;
  let onChangeCallback = null;

  // Drag state
  let draggedPathId = null;

  // Initialize
  function init(existingData = {}, onChange = null) {
    traversals = existingData.paths || [];
    groups = existingData.groups || [];
    onChangeCallback = onChange;

    // Show all traversals by default
    traversals.forEach(t => visibleTraversals.add(t.path_id));

    renderColorPresets();
    updateGroupSelect();
    renderAll();
  }

  // Render color preset buttons
  function renderColorPresets() {
    const container = document.getElementById('color-presets');
    if (!container) return;

    container.innerHTML = COLOR_PALETTE.map(color =>
      `<button type="button" class="color-preset" data-color="${color}" style="background: ${color}"></button>`
    ).join('');
  }

  // Update group dropdown in modal
  function updateGroupSelect() {
    const select = document.getElementById('path-group');
    if (!select) return;

    select.innerHTML = '<option value="">None (Ungrouped)</option>' +
      groups.map(g => `<option value="${g.group_id}">${escapeHtml(g.name)}</option>`).join('');
  }

  // Handle node click - add to sequence
  function handleNodeClick(nodeId) {
    currentSequence.push(nodeId);
    canvas.markNodeInSequence(nodeId, true);
    updateSequenceDisplay();
    drawPreviewPath();
    updateButtons();
  }

  // Undo last node
  function undo() {
    if (currentSequence.length > 0) {
      const removed = currentSequence.pop();
      canvas.markNodeInSequence(removed, false);
      updateSequenceDisplay();
      drawPreviewPath();
      updateButtons();
    }
  }

  // Clear current sequence
  function clearSequence() {
    currentSequence.forEach(id => canvas.markNodeInSequence(id, false));
    currentSequence = [];
    canvas.clearPreview();
    updateSequenceDisplay();
    updateButtons();
  }

  // Draw preview of current path
  function drawPreviewPath() {
    canvas.clearPreview();
    if (currentSequence.length >= 2) {
      canvas.drawTraversal(currentSequence, '#fbbf24', true);
    }
  }

  // Update sequence display
  function updateSequenceDisplay() {
    const container = document.getElementById('path-sequence');
    if (!container) return;

    if (currentSequence.length === 0) {
      container.innerHTML = '<span class="hint">Click nodes to start...</span>';
      return;
    }

    container.innerHTML = currentSequence.map((nodeId, i) => {
      const arcClass = nodeId === '∅' ? 'arc-nontion' : `arc-${nodeId[0]}`;
      return `
        <span class="node-chip ${arcClass}">${nodeId}</span>
        ${i < currentSequence.length - 1 ? '<span class="arrow">→</span>' : ''}
      `;
    }).join('');
  }

  // Update button states
  function updateButtons() {
    const undoBtn = document.getElementById('btn-undo');
    const clearBtn = document.getElementById('btn-clear-path');
    const saveBtn = document.getElementById('btn-save-path');

    if (undoBtn) undoBtn.disabled = currentSequence.length === 0;
    if (clearBtn) clearBtn.disabled = currentSequence.length === 0;
    if (saveBtn) saveBtn.disabled = currentSequence.length < 2;
  }

  // === MODAL FUNCTIONS ===

  function showSaveModal() {
    editingPathId = null;
    const modal = document.getElementById('modal-save-path');
    const title = document.getElementById('modal-title');
    const editIdInput = document.getElementById('edit-path-id');

    if (title) title.textContent = 'Save Traversal';
    if (editIdInput) editIdInput.value = '';

    if (modal) {
      modal.hidden = false;
      const form = document.getElementById('form-save-path');
      if (form) form.reset();
      const colorInput = document.getElementById('path-color');
      if (colorInput) colorInput.value = '#fbbf24';
      const nameInput = document.getElementById('path-name');
      if (nameInput) nameInput.focus();
    }
  }

  function showEditModal(pathId) {
    const traversal = traversals.find(t => t.path_id === pathId);
    if (!traversal) return;

    editingPathId = pathId;
    const modal = document.getElementById('modal-save-path');
    const title = document.getElementById('modal-title');
    const editIdInput = document.getElementById('edit-path-id');
    const nameInput = document.getElementById('path-name');
    const colorInput = document.getElementById('path-color');
    const groupSelect = document.getElementById('path-group');
    const descInput = document.getElementById('path-description');

    if (title) title.textContent = 'Edit Traversal';
    if (editIdInput) editIdInput.value = pathId;
    if (nameInput) nameInput.value = traversal.name;
    if (colorInput) colorInput.value = traversal.color;
    if (groupSelect) groupSelect.value = traversal.group_id || '';
    if (descInput) descInput.value = traversal.description || '';

    document.querySelectorAll('.color-preset').forEach(btn => {
      btn.classList.toggle('selected', btn.dataset.color === traversal.color);
    });

    if (modal) {
      modal.hidden = false;
      if (nameInput) nameInput.focus();
    }
  }

  function hideSaveModal() {
    const modal = document.getElementById('modal-save-path');
    if (modal) modal.hidden = true;
    editingPathId = null;
  }

  // === GROUP MODAL ===

  function showGroupModal(groupId = null) {
    const modal = document.getElementById('modal-group');
    const title = document.getElementById('modal-group-title');
    const editIdInput = document.getElementById('edit-group-id');
    const nameInput = document.getElementById('group-name');

    if (groupId) {
      const group = groups.find(g => g.group_id === groupId);
      if (!group) return;
      if (title) title.textContent = 'Edit Group';
      if (editIdInput) editIdInput.value = groupId;
      if (nameInput) nameInput.value = group.name;
    } else {
      if (title) title.textContent = 'New Group';
      if (editIdInput) editIdInput.value = '';
      const form = document.getElementById('form-group');
      if (form) form.reset();
    }

    if (modal) {
      modal.hidden = false;
      if (nameInput) nameInput.focus();
    }
  }

  function hideGroupModal() {
    const modal = document.getElementById('modal-group');
    if (modal) modal.hidden = true;
  }

  function saveGroup(name) {
    const editId = document.getElementById('edit-group-id')?.value;

    if (editId) {
      const group = groups.find(g => g.group_id === editId);
      if (group) {
        group.name = name.trim();
      }
    } else {
      groups.push({
        group_id: storage.generateId(),
        name: name.trim()
      });
    }

    updateGroupSelect();
    renderAll();
    notifyChange();
  }

  function deleteGroup(groupId) {
    const index = groups.findIndex(g => g.group_id === groupId);
    if (index !== -1) {
      // Ungroup all traversals in this group
      traversals.forEach(t => {
        if (t.group_id === groupId) {
          t.group_id = null;
        }
      });
      groups.splice(index, 1);
      updateGroupSelect();
      renderAll();
      notifyChange();
    }
  }

  // === TRAVERSAL FUNCTIONS ===

  function saveTraversal(name, color, description, groupId) {
    const editId = document.getElementById('edit-path-id')?.value;

    if (editId) {
      return updateTraversal(editId, name, color, description, groupId);
    }

    const traversal = {
      path_id: storage.generateId(),
      name: name.trim(),
      color: color,
      description: description.trim(),
      group_id: groupId || null,
      sequence: [...currentSequence],
      is_circuit: currentSequence.length > 1 && currentSequence[0] === currentSequence[currentSequence.length - 1],
      created_date: new Date().toISOString()
    };

    traversals.push(traversal);
    visibleTraversals.add(traversal.path_id);

    clearSequence();
    renderAll();
    notifyChange();

    return traversal;
  }

  function updateTraversal(pathId, name, color, description, groupId) {
    const traversal = traversals.find(t => t.path_id === pathId);
    if (!traversal) return null;

    traversal.name = name.trim();
    traversal.color = color;
    traversal.description = description.trim();
    traversal.group_id = groupId || null;
    traversal.modified_date = new Date().toISOString();

    renderAll();
    notifyChange();

    return traversal;
  }

  function deleteTraversal(pathId) {
    const index = traversals.findIndex(t => t.path_id === pathId);
    if (index !== -1) {
      traversals.splice(index, 1);
      visibleTraversals.delete(pathId);
      renderAll();
      notifyChange();
      return true;
    }
    return false;
  }

  function moveTraversal(pathId, newGroupId, newIndex = -1) {
    const traversal = traversals.find(t => t.path_id === pathId);
    if (!traversal) return;

    traversal.group_id = newGroupId || null;

    // Reorder if index specified
    if (newIndex >= 0) {
      const oldIndex = traversals.indexOf(traversal);
      traversals.splice(oldIndex, 1);
      traversals.splice(newIndex, 0, traversal);
    }

    renderAll();
    notifyChange();
  }

  // === VISIBILITY ===

  function toggleVisibility(pathId) {
    if (visibleTraversals.has(pathId)) {
      visibleTraversals.delete(pathId);
    } else {
      visibleTraversals.add(pathId);
    }
    renderAll();
  }

  function toggleGroupVisibility(groupId) {
    const groupPaths = traversals.filter(t => t.group_id === groupId);
    const allVisible = groupPaths.every(t => visibleTraversals.has(t.path_id));

    groupPaths.forEach(t => {
      if (allVisible) {
        visibleTraversals.delete(t.path_id);
      } else {
        visibleTraversals.add(t.path_id);
      }
    });

    renderAll();
  }

  function showOnly(pathId) {
    visibleTraversals.clear();
    visibleTraversals.add(pathId);
    renderAll();
  }

  function showOnlyGroup(groupId) {
    visibleTraversals.clear();
    traversals.filter(t => t.group_id === groupId).forEach(t => {
      visibleTraversals.add(t.path_id);
    });
    renderAll();
  }

  function toggleGroupCollapse(groupId) {
    if (collapsedGroups.has(groupId)) {
      collapsedGroups.delete(groupId);
    } else {
      collapsedGroups.add(groupId);
    }
    renderAll();
  }

  // === RENDERING ===

  function renderAll() {
    renderGroups();
    renderUngrouped();
    redrawAllTraversals();
    updateStats();
  }

  function renderGroups() {
    const container = document.getElementById('groups-list');
    if (!container) return;

    if (groups.length === 0) {
      container.innerHTML = '<p class="hint" style="padding: 0.5rem 0;">No groups yet.</p>';
      return;
    }

    container.innerHTML = groups.map(group => {
      const groupPaths = traversals.filter(t => t.group_id === group.group_id);
      const isCollapsed = collapsedGroups.has(group.group_id);
      const allVisible = groupPaths.length > 0 && groupPaths.every(t => visibleTraversals.has(t.path_id));

      return `
        <div class="group-item ${isCollapsed ? 'collapsed' : ''}" data-group-id="${group.group_id}">
          <div class="group-header">
            <span class="group-toggle">▼</span>
            <span class="group-name">${escapeHtml(group.name)}</span>
            <span class="group-count">${groupPaths.length}</span>
            <div class="group-actions">
              <button class="btn-icon btn-icon-small" data-action="toggle-group-visibility" data-group-id="${group.group_id}" title="${allVisible ? 'Hide All' : 'Show All'}">
                ${allVisible ? '👁' : '👁‍🗨'}
              </button>
              <button class="btn-icon btn-icon-small" data-action="edit-group" data-group-id="${group.group_id}" title="Edit">✎</button>
              <button class="btn-icon btn-icon-small" data-action="delete-group" data-group-id="${group.group_id}" title="Delete">×</button>
            </div>
          </div>
          <div class="group-content">
            <div class="group-paths" data-group-id="${group.group_id}">
              ${groupPaths.length === 0 ? '<p class="hint" style="margin:0;font-size:0.7rem;">Drag traversals here</p>' : ''}
              ${groupPaths.map(t => renderPathItem(t)).join('')}
            </div>
          </div>
        </div>
      `;
    }).join('');

    // Event listeners
    container.querySelectorAll('.group-header').forEach(header => {
      header.addEventListener('click', (e) => {
        if (e.target.closest('.group-actions')) return;
        const groupId = header.closest('.group-item').dataset.groupId;
        toggleGroupCollapse(groupId);
      });
    });

    container.querySelectorAll('[data-action]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const action = btn.dataset.action;
        const groupId = btn.dataset.groupId;

        switch (action) {
          case 'toggle-group-visibility':
            toggleGroupVisibility(groupId);
            break;
          case 'edit-group':
            showGroupModal(groupId);
            break;
          case 'delete-group':
            if (confirm('Delete this group? Traversals will be ungrouped.')) {
              deleteGroup(groupId);
            }
            break;
        }
      });
    });

    // Drag-drop for group paths
    container.querySelectorAll('.group-paths').forEach(zone => {
      setupDropZone(zone, zone.dataset.groupId);
    });

    setupPathDragHandlers(container);
  }

  function renderUngrouped() {
    const container = document.getElementById('paths-list');
    if (!container) return;

    const ungrouped = traversals.filter(t => !t.group_id);

    if (ungrouped.length === 0) {
      container.innerHTML = '<p class="hint">No ungrouped traversals.</p>';
    } else {
      container.innerHTML = ungrouped.map(t => renderPathItem(t)).join('');
    }

    setupDropZone(container, null);
    setupPathDragHandlers(container);
  }

  function renderPathItem(traversal) {
    const isVisible = visibleTraversals.has(traversal.path_id);
    const previewSeq = traversal.sequence.slice(0, 4).join('→') +
      (traversal.sequence.length > 4 ? '...' : '');

    return `
      <div class="path-item ${isVisible ? 'visible' : ''}"
           data-path-id="${traversal.path_id}"
           draggable="true"
           style="color: ${traversal.color}">
        <div class="path-item-header">
          <span class="drag-handle">⋮⋮</span>
          <span class="path-color-dot" style="background: ${traversal.color}"></span>
          <span class="path-name">${escapeHtml(traversal.name)}</span>
          <button class="path-toggle ${isVisible ? 'active' : ''}"
                  data-action="toggle"
                  data-path-id="${traversal.path_id}">
            ${isVisible ? '👁' : '👁‍🗨'}
          </button>
        </div>
        <div class="path-preview">${previewSeq}</div>
        <div class="path-actions">
          <button class="btn-small" data-action="edit" data-path-id="${traversal.path_id}">Edit</button>
          <button class="btn-small" data-action="only" data-path-id="${traversal.path_id}">Only</button>
          <button class="btn-small" data-action="delete" data-path-id="${traversal.path_id}">Del</button>
        </div>
      </div>
    `;
  }

  function setupPathDragHandlers(container) {
    container.querySelectorAll('.path-item').forEach(item => {
      item.addEventListener('dragstart', (e) => {
        draggedPathId = item.dataset.pathId;
        item.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
      });

      item.addEventListener('dragend', () => {
        item.classList.remove('dragging');
        draggedPathId = null;
        document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
      });
    });

    // Action buttons
    container.querySelectorAll('[data-action]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const action = btn.dataset.action;
        const pathId = btn.dataset.pathId;

        switch (action) {
          case 'toggle':
            toggleVisibility(pathId);
            break;
          case 'edit':
            showEditModal(pathId);
            break;
          case 'only':
            showOnly(pathId);
            break;
          case 'delete':
            if (confirm('Delete this traversal?')) {
              deleteTraversal(pathId);
            }
            break;
        }
      });
    });
  }

  function setupDropZone(zone, groupId) {
    zone.addEventListener('dragover', (e) => {
      e.preventDefault();
      zone.classList.add('drag-over');
    });

    zone.addEventListener('dragleave', (e) => {
      if (!zone.contains(e.relatedTarget)) {
        zone.classList.remove('drag-over');
      }
    });

    zone.addEventListener('drop', (e) => {
      e.preventDefault();
      zone.classList.remove('drag-over');

      if (draggedPathId) {
        moveTraversal(draggedPathId, groupId);
      }
    });
  }

  function redrawAllTraversals() {
    canvas.clearTraversals();

    traversals.forEach(traversal => {
      if (visibleTraversals.has(traversal.path_id)) {
        canvas.drawTraversal(traversal.sequence, traversal.color, false);
      }
    });

    if (currentSequence.length >= 2) {
      canvas.drawTraversal(currentSequence, '#fbbf24', true);
    }
  }

  function updateStats() {
    const el = document.getElementById('stat-paths');
    if (el) el.textContent = traversals.filter(t => !t.group_id).length;
  }

  function notifyChange() {
    if (onChangeCallback) {
      onChangeCallback({ paths: traversals, groups: groups });
    }
  }

  function redraw() {
    redrawAllTraversals();
  }

  // === DATA ACCESS ===

  function getTraversals() {
    return [...traversals];
  }

  function getGroups() {
    return [...groups];
  }

  function setData(data) {
    traversals = data.paths || [];
    groups = data.groups || [];
    visibleTraversals.clear();
    traversals.forEach(t => visibleTraversals.add(t.path_id));
    updateGroupSelect();
    renderAll();
  }

  // Helper
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Export
  window.MiroGlyph.paths = {
    init,
    handleNodeClick,
    undo,
    clearSequence,
    showSaveModal,
    showEditModal,
    hideSaveModal,
    showGroupModal,
    hideGroupModal,
    saveGroup,
    deleteGroup,
    saveTraversal,
    updateTraversal,
    deleteTraversal,
    moveTraversal,
    toggleVisibility,
    toggleGroupVisibility,
    showOnly,
    showOnlyGroup,
    getTraversals,
    getGroups,
    setData,
    redraw,
    COLOR_PALETTE
  };
})();
