// Journey Mapper - UI Rendering
// Handles screen rendering, choice cards, progress indicators, and interactions

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var state = null;
  var filters = null;
  var nodes = null;
  var utils = null;

  // Data references
  var templates = null;
  var archetypesData = null;
  var entitiesData = null;
  var patternsData = null;
  var affinitiesData = null;

  // Current filtered/displayed items
  var displayedArchetypes = [];
  var displayedEntities = [];
  var displayedMotifs = [];

  // Display limits
  var DISPLAY_LIMIT = 12;

  /**
   * Initialize UI module with dependencies
   */
  function init(deps) {
    state = deps.state;
    filters = deps.filters;
    nodes = deps.nodes;
    utils = deps.utils;
    templates = deps.templates;
    archetypesData = deps.archetypes;
    entitiesData = deps.entities;
    patternsData = deps.patterns;
    affinitiesData = deps.affinities;

    console.log('Journey UI initialized with data:', {
      hasTemplates: !!templates,
      hasArchetypes: !!archetypesData,
      archetypeCount: archetypesData && archetypesData.archetypes ? archetypesData.archetypes.length : 0,
      hasEntities: !!entitiesData,
      hasPatterns: !!patternsData,
      hasAffinities: !!affinitiesData
    });
  }

  // ========== Screen Management ==========

  function showScreen(screenId) {
    var screens = document.querySelectorAll('.journey-screen');
    screens.forEach(function(s) { s.hidden = true; });
    var screen = document.getElementById('screen-' + screenId);
    if (screen) screen.hidden = false;
  }

  function showStartScreen() {
    showScreen('start');
    renderSavedJourneys();
  }

  function showNodeScreen() {
    showScreen('node');
    renderProgress();
    renderNodeInfo();
    renderSelectionStep();
  }

  function showNontionScreen() {
    showScreen('nontion');
    renderProgress();
  }

  function showCompleteScreen() {
    showScreen('complete');
    renderCompleteSummary();
  }

  // ========== Start Screen ==========

  function renderSavedJourneys() {
    var saved = state.loadSavedJourneys();
    var container = document.getElementById('saved-journeys');
    var list = document.getElementById('saved-list');

    if (!saved.journeys || saved.journeys.length === 0) {
      container.hidden = true;
      return;
    }

    container.hidden = false;
    list.innerHTML = saved.journeys.map(function(j) {
      var pathStr = j.traversal.join(' → ');
      return '<div class="saved-journey-item" data-journey-id="' + j.journey_id + '">' +
        '<div>' +
          '<div class="saved-journey-name">' + utils.escapeHtml(j.name) + '</div>' +
          '<div class="saved-journey-path">' + utils.escapeHtml(pathStr) + '</div>' +
        '</div>' +
        '<div class="saved-journey-actions">' +
          '<button class="btn btn-small btn-resume" data-journey-id="' + j.journey_id + '">Resume</button>' +
          '<button class="btn btn-small btn-delete-journey" data-journey-id="' + j.journey_id + '">×</button>' +
        '</div>' +
      '</div>';
    }).join('');

    // Bind events
    list.querySelectorAll('.btn-resume').forEach(function(btn) {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        var id = btn.getAttribute('data-journey-id');
        if (state.resumeJourney(id)) {
          navigateToCurrentNode();
        }
      });
    });

    list.querySelectorAll('.btn-delete-journey').forEach(function(btn) {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        var id = btn.getAttribute('data-journey-id');
        if (confirm('Delete this saved journey?')) {
          state.deleteSavedJourney(id);
          renderSavedJourneys();
        }
      });
    });
  }

  function renderChoosePathModal() {
    var modal = document.getElementById('modal-choose');
    var options = document.getElementById('traversal-options');

    var traversals = state.getStarterTraversals();
    options.innerHTML = traversals.map(function(t) {
      return '<div class="traversal-option" data-sequence="' + t.sequence.join(',') + '" data-name="' + utils.escapeAttr(t.name) + '">' +
        '<div class="traversal-option-name">' + utils.escapeHtml(t.name) + '</div>' +
        '<div class="traversal-option-sequence">' + t.sequence.join(' → ') + '</div>' +
      '</div>';
    }).join('');

    options.querySelectorAll('.traversal-option').forEach(function(opt) {
      opt.addEventListener('click', function() {
        var seq = opt.getAttribute('data-sequence').split(',');
        var name = opt.getAttribute('data-name');
        state.createJourney(seq, name);
        modal.hidden = true;
        navigateToCurrentNode();
      });
    });

    modal.hidden = false;
  }

  // ========== Progress Rendering ==========

  function renderProgress() {
    var journey = state.getJourney();
    if (!journey) return;

    var container = document.getElementById('progress-nodes');
    var html = journey.traversal.map(function(nodeId, index) {
      var arcClass = nodeId === '∅' ? 'arc-nontion' : 'arc-' + nodeId.charAt(0);
      var statusClass = '';
      if (index < journey.current_index) statusClass = 'completed';
      else if (index === journey.current_index) statusClass = 'current';

      return '<span class="progress-node ' + arcClass + ' ' + statusClass + '">' + nodeId + '</span>';
    });

    // Insert arrows between nodes
    container.innerHTML = html.join('<span class="progress-arrow">→</span>');
  }

  // ========== Node Info Rendering ==========

  function renderNodeInfo() {
    var nodeId = state.getCurrentNodeId();
    var container = document.getElementById('node-info');

    if (nodeId === '∅') {
      // Nontion - handled by separate screen
      return;
    }

    var template = getNodeTemplate(nodeId);
    var nodeData = nodes.getNode(nodeId);

    if (!template || !nodeData) {
      container.innerHTML = '<div class="loading-state">Node data not found</div>';
      return;
    }

    var arcClass = 'arc-' + nodeId.charAt(0);
    container.className = 'node-info-card ' + arcClass;

    var identity = template.identity;
    var lens = template.thematic_lens;
    var question = lens.questions ? lens.questions[0] : '';

    container.innerHTML =
      '<div class="node-info-header">' +
        '<span class="node-info-id">' + nodeId + '</span>' +
      '</div>' +
      '<div class="node-info-title">' + utils.escapeHtml(identity.title) + '</div>' +
      '<div class="node-info-role">' + utils.escapeHtml(identity.role) + '</div>' +
      '<div class="node-info-meta">' +
        identity.arc.primary + '/' + identity.arc.secondary + ' – ' +
        identity.condition.primary + '/' + identity.condition.secondary +
      '</div>' +
      '<div class="node-info-tone">' +
        (identity.tone || []).map(function(t) {
          return '<span class="tone-tag">' + utils.escapeHtml(t) + '</span>';
        }).join('') +
      '</div>' +
      (question ? '<div class="node-info-question">"' + utils.escapeHtml(question) + '"</div>' : '');
  }

  // ========== Selection Step Rendering ==========

  function renderSelectionStep() {
    var stepName = state.getCurrentStepName();
    var container = document.getElementById('selection-area');
    var nodeId = state.getCurrentNodeId();
    var template = getNodeTemplate(nodeId);

    console.log('Rendering step:', stepName, 'for node:', nodeId, 'template found:', !!template);

    if (!template) {
      console.warn('No template found for node:', nodeId);
      container.innerHTML = '<div class="loading-state">Loading...</div>';
      return;
    }

    var prompts = template.selection_prompts || {};
    var currentSelection = state.getSelection(stepName);

    var stepNumber = state.SELECTION_STEPS.indexOf(stepName) + 1;
    var stepLabel = stepName.charAt(0).toUpperCase() + stepName.slice(1);

    var html = '<div class="selection-step">' +
      '<div class="step-header">' +
        '<div class="step-number">Step ' + stepNumber + ': Choose ' + (stepName === 'note' ? 'to Add a Note' : 'an ' + stepLabel) + '</div>' +
        '<div class="step-prompt">' + utils.escapeHtml(prompts[stepName] || 'Make your selection') + '</div>' +
      '</div>';

    // Current selection display
    if (currentSelection && stepName !== 'note') {
      html += renderCurrentSelection(stepName, currentSelection);
    }

    // Step-specific content
    if (stepName === 'archetype') {
      html += renderArchetypeStep(nodeId, template);
    } else if (stepName === 'entity') {
      html += renderEntityStep(nodeId, template);
    } else if (stepName === 'motif') {
      html += renderMotifStep(nodeId, template);
    } else if (stepName === 'note') {
      html += renderNoteStep();
    }

    html += '</div>';
    container.innerHTML = html;

    // Bind events
    bindStepEvents(stepName);
    updateContinueButton();
  }

  function renderCurrentSelection(stepName, selection) {
    var label = '';
    var value = '';

    if (stepName === 'archetype' && selection) {
      label = 'Archetype';
      value = selection.name || selection.archetype_name || 'Selected';
    } else if (stepName === 'entity' && selection) {
      label = 'Entity';
      value = selection.name || 'Selected';
    } else if (stepName === 'motif' && selection) {
      label = 'Motif';
      value = selection.code + ' - ' + selection.label;
    }

    if (!value) return '';

    return '<div class="current-selection">' +
      '<span class="current-selection-label">' + label + ':</span>' +
      '<span class="current-selection-value">' + utils.escapeHtml(value) + '</span>' +
      '<button class="current-selection-clear" data-step="' + stepName + '">×</button>' +
    '</div>';
  }

  function renderArchetypeStep(nodeId, template) {
    var html = '<div class="selection-search">' +
      '<input type="text" class="selection-search-input" id="archetype-search" placeholder="Search archetypes...">' +
    '</div>';

    // Get suggested archetypes for this node
    var suggested = filters.getSuggestedArchetypes(nodeId, affinitiesData, DISPLAY_LIMIT - 1);

    // Map to full archetype objects - affinity data has 'name' not 'archetype_name'
    displayedArchetypes = suggested.map(function(s) {
      var arch = archetypesData && archetypesData.archetypes ?
        archetypesData.archetypes.find(function(a) { return a.id === s.archetype_id; }) : null;
      return arch || { id: s.archetype_id, name: s.name || s.archetype_id };
    });

    // If no suggested archetypes, show some popular ones
    if (displayedArchetypes.length === 0 && archetypesData && archetypesData.archetypes) {
      displayedArchetypes = archetypesData.archetypes.slice(0, DISPLAY_LIMIT - 1);
    }

    console.log('Displaying', displayedArchetypes.length, 'archetypes for node', nodeId);

    html += '<div class="choice-grid" id="archetype-grid">';
    html += renderArchetypeCards(displayedArchetypes);
    html += '<div class="choice-card choice-card-surprise" data-action="surprise">' +
      '<div class="choice-card-name">Surprise Me</div>' +
      '<div class="choice-card-meta">Random archetype</div>' +
    '</div>';
    html += '</div>';

    return html;
  }

  function renderArchetypeCards(archetypes) {
    return archetypes.map(function(a) {
      var tradition = a.tradition || (a.id ? a.id.split(':')[0].replace('arch:', '') : '');
      return '<div class="choice-card" data-type="archetype" data-id="' + utils.escapeAttr(a.id) + '">' +
        '<div class="choice-card-name">' + utils.escapeHtml(a.name || a.id) + '</div>' +
        '<div class="choice-card-meta">' + utils.escapeHtml(tradition) + '</div>' +
      '</div>';
    }).join('');
  }

  function renderEntityStep(nodeId, template) {
    var html = '<div class="selection-search">' +
      '<input type="text" class="selection-search-input" id="entity-search" placeholder="Search entities...">' +
    '</div>';

    // Get suggested entities for this node
    displayedEntities = filters.getSuggestedEntities(nodeId, entitiesData, DISPLAY_LIMIT - 1);

    // If not enough, add some popular entities
    if (displayedEntities.length < 4 && entitiesData && entitiesData.entities) {
      var existing = displayedEntities.map(function(e) { return e.name; });
      var popular = entitiesData.entities
        .filter(function(e) { return existing.indexOf(e.name) === -1; })
        .sort(function(a, b) { return (b.total_mentions || 0) - (a.total_mentions || 0); })
        .slice(0, DISPLAY_LIMIT - 1 - displayedEntities.length);
      displayedEntities = displayedEntities.concat(popular);
    }

    html += '<div class="choice-grid" id="entity-grid">';
    html += renderEntityCards(displayedEntities);
    html += '<div class="choice-card choice-card-surprise" data-action="surprise">' +
      '<div class="choice-card-name">Surprise Me</div>' +
      '<div class="choice-card-meta">Random entity</div>' +
    '</div>';
    html += '</div>';

    return html;
  }

  function renderEntityCards(entities) {
    return entities.map(function(e) {
      return '<div class="choice-card" data-type="entity" data-name="' + utils.escapeAttr(e.name) + '">' +
        '<div class="choice-card-name">' + utils.escapeHtml(e.name) + '</div>' +
        '<div class="choice-card-meta">' + utils.escapeHtml(e.primary_tradition || e.type || '') + '</div>' +
      '</div>';
    }).join('');
  }

  function renderMotifStep(nodeId, template) {
    var html = '';

    // Evidence markers info - display as context, not as filter options
    var markers = template.evidence_markers;
    if (markers) {
      html += '<div class="evidence-markers-info">' +
        '<div class="evidence-markers-label">Evidence Markers for this node:</div>' +
        '<div class="evidence-markers-tags">' +
          '<span class="evidence-marker-tag primary">' + markers.primary_name + '</span>' +
          '<span class="evidence-marker-plus">+</span>' +
          '<span class="evidence-marker-tag secondary">' + markers.secondary_name + '</span>' +
        '</div>' +
        '<div class="evidence-markers-hint">Motifs are filtered to Thompson categories that align with these markers</div>' +
      '</div>';
    }

    html += '<div class="selection-search">' +
      '<input type="text" class="selection-search-input" id="motif-search" placeholder="Search motifs by code or name...">' +
    '</div>';

    // Get filtered motifs
    var filtered = filters.getFilteredMotifs(template, patternsData);
    displayedMotifs = filtered.all;

    // Group by marker type for clearer presentation
    var primaryCount = filtered.primary.length;
    var secondaryCount = filtered.secondary.length;

    html += '<div class="motif-list" id="motif-list">';

    // Show primary marker motifs first with section header
    if (primaryCount > 0) {
      html += '<div class="motif-section-header">' + markers.primary_name + ' Motifs (' + primaryCount + ')</div>';
      html += renderMotifItems(filtered.primary.slice(0, 10));
    }

    // Then secondary marker motifs
    if (secondaryCount > 0) {
      html += '<div class="motif-section-header">' + markers.secondary_name + ' Motifs (' + secondaryCount + ')</div>';
      html += renderMotifItems(filtered.secondary.slice(0, 10));
    }

    var totalShown = Math.min(primaryCount, 10) + Math.min(secondaryCount, 10);
    var totalAvailable = primaryCount + secondaryCount;
    if (totalAvailable > totalShown) {
      html += '<div class="show-more"><button class="show-more-btn" id="show-more-motifs">Show all (' + totalAvailable + ' total)</button></div>';
    }
    html += '</div>';

    return html;
  }

  function renderMotifItems(motifs) {
    return motifs.map(function(m) {
      var markerClass = m.markerType === 'primary' ? 'primary' : '';
      return '<div class="motif-item" data-code="' + m.code + '">' +
        '<span class="motif-code">' + m.code + '</span>' +
        '<span class="motif-name">' + utils.escapeHtml(m.label) + '</span>' +
        '<span class="motif-marker ' + markerClass + '">' + utils.escapeHtml(m.markerName || m.categoryName) + '</span>' +
      '</div>';
    }).join('');
  }

  function renderNoteStep() {
    var currentNote = state.getSelection('note') || '';
    return '<div class="note-input">' +
      '<label for="node-note">Add a note about this node (optional)</label>' +
      '<textarea id="node-note" rows="4" placeholder="What does this node mean in your journey?">' +
        utils.escapeHtml(currentNote) +
      '</textarea>' +
    '</div>';
  }

  // ========== Step Event Binding ==========

  function bindStepEvents(stepName) {
    // Clear selection button
    var clearBtns = document.querySelectorAll('.current-selection-clear');
    clearBtns.forEach(function(btn) {
      btn.addEventListener('click', function() {
        var step = btn.getAttribute('data-step');
        state.setSelection(step, null);
        renderSelectionStep();
      });
    });

    if (stepName === 'archetype') {
      bindArchetypeEvents();
    } else if (stepName === 'entity') {
      bindEntityEvents();
    } else if (stepName === 'motif') {
      bindMotifEvents();
    } else if (stepName === 'note') {
      bindNoteEvents();
    }
  }

  function bindArchetypeEvents() {
    var searchInput = document.getElementById('archetype-search');
    var grid = document.getElementById('archetype-grid');

    console.log('Binding archetype events, grid found:', !!grid);

    if (searchInput) {
      searchInput.addEventListener('input', utils.debounce(function() {
        var query = searchInput.value;
        var all = archetypesData && archetypesData.archetypes ? archetypesData.archetypes : [];
        var filtered = filters.searchArchetypes(all, query).slice(0, DISPLAY_LIMIT - 1);

        grid.innerHTML = renderArchetypeCards(filtered) +
          '<div class="choice-card choice-card-surprise" data-action="surprise">' +
            '<div class="choice-card-name">Surprise Me</div>' +
            '<div class="choice-card-meta">Random archetype</div>' +
          '</div>';

        displayedArchetypes = filtered;
        bindCardClicks(grid, 'archetype');
      }, 200));
    }

    bindCardClicks(grid, 'archetype');
  }

  function bindEntityEvents() {
    var searchInput = document.getElementById('entity-search');
    var grid = document.getElementById('entity-grid');

    if (searchInput) {
      searchInput.addEventListener('input', utils.debounce(function() {
        var query = searchInput.value;
        var all = entitiesData && entitiesData.entities ? entitiesData.entities : [];
        var filtered = filters.searchEntities(all, query).slice(0, DISPLAY_LIMIT - 1);

        grid.innerHTML = renderEntityCards(filtered) +
          '<div class="choice-card choice-card-surprise" data-action="surprise">' +
            '<div class="choice-card-name">Surprise Me</div>' +
            '<div class="choice-card-meta">Random entity</div>' +
          '</div>';

        displayedEntities = filtered;
        bindCardClicks(grid, 'entity');
      }, 200));
    }

    bindCardClicks(grid, 'entity');
  }

  function bindMotifEvents() {
    var searchInput = document.getElementById('motif-search');
    var list = document.getElementById('motif-list');

    // Search
    if (searchInput) {
      searchInput.addEventListener('input', utils.debounce(function() {
        var query = searchInput.value;
        var filtered = filters.searchMotifs(displayedMotifs, query);

        list.innerHTML = renderMotifItems(filtered.slice(0, 30));
        bindMotifClicks();
      }, 200));
    }

    // Show more button
    var showMore = document.getElementById('show-more-motifs');
    if (showMore) {
      showMore.addEventListener('click', function() {
        var nodeId = state.getCurrentNodeId();
        var template = getNodeTemplate(nodeId);
        var markers = template.evidence_markers;
        var filtered = filters.getFilteredMotifs(template, patternsData);

        // Show all motifs grouped by marker type
        var html = '';
        if (filtered.primary.length > 0) {
          html += '<div class="motif-section-header">' + markers.primary_name + ' Motifs (' + filtered.primary.length + ')</div>';
          html += renderMotifItems(filtered.primary);
        }
        if (filtered.secondary.length > 0) {
          html += '<div class="motif-section-header">' + markers.secondary_name + ' Motifs (' + filtered.secondary.length + ')</div>';
          html += renderMotifItems(filtered.secondary);
        }

        list.innerHTML = html;
        bindMotifClicks();
      });
    }

    bindMotifClicks();
  }

  function bindMotifClicks() {
    var list = document.getElementById('motif-list');
    if (!list) return;

    // Use event delegation
    list.onclick = function(e) {
      var item = e.target.closest('.motif-item');
      if (!item) return;

      var code = item.getAttribute('data-code');
      var motif = displayedMotifs.find(function(m) { return m.code === code; });

      // If not found in displayed, try to find in patterns data
      if (!motif && patternsData && patternsData.motifs && patternsData.motifs[code]) {
        var m = patternsData.motifs[code];
        motif = { code: code, label: m.label, category: m.category };
      }

      if (motif) {
        state.setSelection('motif', motif);
        list.querySelectorAll('.motif-item').forEach(function(i) {
          i.classList.remove('selected');
        });
        item.classList.add('selected');
        updateContinueButton();
      }
    };
  }

  function bindNoteEvents() {
    var textarea = document.getElementById('node-note');
    if (textarea) {
      textarea.addEventListener('input', function() {
        state.setSelection('note', textarea.value);
      });
    }
  }

  function bindCardClicks(container, type) {
    if (!container) {
      console.warn('bindCardClicks: container is null for type', type);
      return;
    }

    // Use event delegation on the container instead of individual card listeners
    container.onclick = function(e) {
      var card = e.target.closest('.choice-card');
      if (!card) {
        console.log('Click not on card, target:', e.target);
        return;
      }

      console.log('Card clicked:', type, card.getAttribute('data-id') || card.getAttribute('data-name') || 'surprise');
      e.preventDefault();
      var action = card.getAttribute('data-action');

      if (action === 'surprise') {
        // Random selection
        var pool = type === 'archetype' ?
          (archetypesData && archetypesData.archetypes ? archetypesData.archetypes : []) :
          (entitiesData && entitiesData.entities ? entitiesData.entities : []);
        var random = filters.getRandomItem(pool);
        if (random) {
          state.setSelection(type, random);
          renderSelectionStep();
        }
        return;
      }

      // Regular selection
      var selection = null;
      if (type === 'archetype') {
        var id = card.getAttribute('data-id');
        // First check displayedArchetypes
        selection = displayedArchetypes.find(function(a) { return a.id === id; });
        // Fallback to full catalog
        if (!selection && archetypesData && archetypesData.archetypes) {
          selection = archetypesData.archetypes.find(function(a) { return a.id === id; });
        }
        // If still not found, create a minimal selection object
        if (!selection && id) {
          var nameFromCard = card.querySelector('.choice-card-name');
          selection = { id: id, name: nameFromCard ? nameFromCard.textContent : id };
        }
      } else if (type === 'entity') {
        var name = card.getAttribute('data-name');
        selection = displayedEntities.find(function(e) { return e.name === name; });
        if (!selection && entitiesData && entitiesData.entities) {
          selection = entitiesData.entities.find(function(e) { return e.name === name; });
        }
        // If still not found, create minimal object
        if (!selection && name) {
          selection = { name: name };
        }
      }

      if (selection) {
        console.log('Selection made:', type, selection.name || selection.id);
        state.setSelection(type, selection);
        // Update visual state
        container.querySelectorAll('.choice-card').forEach(function(c) {
          c.classList.remove('selected');
        });
        card.classList.add('selected');
        updateContinueButton();
      } else {
        console.warn('No selection found for', type);
      }
    };
  }

  // ========== Navigation ==========

  function updateContinueButton() {
    var btn = document.getElementById('btn-next-step');
    var stepName = state.getCurrentStepName();

    console.log('Updating continue button for step:', stepName);

    // Note step can always continue (it's optional)
    if (stepName === 'note') {
      btn.disabled = false;
      btn.textContent = 'Complete Node';
      return;
    }

    // Other steps require selection OR allow skip
    var selection = state.getSelection(stepName);
    btn.disabled = false; // Always allow continue (skip is an option)
    btn.textContent = selection ? 'Continue' : 'Skip & Continue';
    console.log('Button updated, has selection:', !!selection);
  }

  function navigateToCurrentNode() {
    if (state.isCurrentNodeNontion()) {
      showNontionScreen();
    } else {
      showNodeScreen();
    }
  }

  // ========== Complete Screen ==========

  function renderCompleteSummary() {
    var journey = state.getJourney();
    if (!journey) return;

    // Traversal visualization
    var traversalContainer = document.getElementById('complete-traversal');
    traversalContainer.innerHTML = journey.traversal.map(function(nodeId) {
      var arcClass = nodeId === '∅' ? 'arc-nontion' : 'arc-' + nodeId.charAt(0);
      return '<span class="progress-node completed ' + arcClass + '">' + nodeId + '</span>';
    }).join('<span class="progress-arrow">→</span>');

    // Node summaries
    var summaryContainer = document.getElementById('complete-summary');
    summaryContainer.innerHTML = journey.nodes.map(function(node) {
      var arcClass = node.node_id === '∅' ? 'arc-nontion' : 'arc-' + node.node_id.charAt(0);
      var template = getNodeTemplate(node.node_id);
      var title = template ? template.identity.title : (node.node_id === '∅' ? 'Nontion' : '');

      var selectionsHtml = '';
      if (node.archetype) {
        selectionsHtml += '<div class="summary-selection"><strong>Archetype:</strong> ' +
          utils.escapeHtml(node.archetype.name || node.archetype.archetype_name || 'Selected') + '</div>';
      }
      if (node.entity) {
        selectionsHtml += '<div class="summary-selection"><strong>Entity:</strong> ' +
          utils.escapeHtml(node.entity.name) + '</div>';
      }
      if (node.motif) {
        selectionsHtml += '<div class="summary-selection"><strong>Motif:</strong> ' +
          node.motif.code + ' - ' + utils.escapeHtml(node.motif.label) + '</div>';
      }

      var noteHtml = node.note ?
        '<div class="summary-note">' + utils.escapeHtml(node.note) + '</div>' : '';

      return '<div class="complete-node-summary ' + arcClass + '">' +
        '<div class="summary-header">' +
          '<span class="summary-node-id">' + node.node_id + '</span>' +
          '<span class="summary-node-title">' + utils.escapeHtml(title) + '</span>' +
        '</div>' +
        '<div class="summary-selections">' + (selectionsHtml || '<em>No selections</em>') + '</div>' +
        noteHtml +
      '</div>';
    }).join('');
  }

  // ========== Helpers ==========

  function getNodeTemplate(nodeId) {
    if (!templates || !templates.nodes) return null;
    if (nodeId === '∅') return templates.nontion;
    return templates.nodes.find(function(n) { return n.node_id === nodeId; });
  }

  // ========== Export ==========

  window.MiroGlyph.journeyUI = {
    init: init,
    showStartScreen: showStartScreen,
    showNodeScreen: showNodeScreen,
    showNontionScreen: showNontionScreen,
    showCompleteScreen: showCompleteScreen,
    renderProgress: renderProgress,
    renderNodeInfo: renderNodeInfo,
    renderSelectionStep: renderSelectionStep,
    renderSavedJourneys: renderSavedJourneys,
    renderChoosePathModal: renderChoosePathModal,
    renderCompleteSummary: renderCompleteSummary,
    navigateToCurrentNode: navigateToCurrentNode,
    updateContinueButton: updateContinueButton
  };
})();
