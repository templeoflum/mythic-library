// Journey Mapper - UI Rendering (Network Configuration Model)
// Handles config wizard, network grid, node detail, and interactions

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
  }

  // ========== Screen Management ==========

  function showScreen(screenId) {
    var screens = document.querySelectorAll('.journey-screen');
    screens.forEach(function(s) { s.hidden = true; });
    var screen = document.getElementById('screen-' + screenId);
    if (screen) screen.hidden = false;
    // Hide all modals
    document.querySelectorAll('.modal').forEach(function(m) { m.hidden = true; });
  }

  function showStartScreen() {
    showScreen('start');
    renderSavedNetworks();
    window.location.hash = 'start';
  }

  function showConfigScreen(step) {
    showScreen('config');
    if (step !== undefined) state.setConfigStep(step);
    renderConfigStep();
    window.location.hash = 'config/' + state.getConfigStep();
  }

  function showNetworkScreen() {
    showScreen('network');
    renderNetworkGrid();
    var network = state.getNetwork();
    if (network) {
      document.getElementById('network-title').textContent = network.name || 'Mythic Network';
    }
    window.location.hash = 'network';
  }

  // ========== Start Screen ==========

  function renderSavedNetworks() {
    var saved = state.loadSavedNetworks();
    var container = document.getElementById('saved-networks');
    var list = document.getElementById('saved-list');

    if (!saved.networks || saved.networks.length === 0) {
      container.hidden = true;
      return;
    }

    container.hidden = false;
    list.innerHTML = saved.networks.map(function(n) {
      var archInfo = '';
      if (n.configuration && n.configuration.primary_archetype) {
        archInfo = (n.configuration.primary_archetype.name || '') + ' / ' +
                   (n.configuration.secondary_archetype ? n.configuration.secondary_archetype.name : '');
      }
      var traversalCount = n.traversals ? n.traversals.length : 0;
      return '<div class="saved-journey-item" data-network-id="' + n.network_id + '">' +
        '<div>' +
          '<div class="saved-journey-name">' + utils.escapeHtml(n.name || 'Unnamed') + '</div>' +
          '<div class="saved-journey-path">' + utils.escapeHtml(archInfo) +
            ' &middot; ' + traversalCount + ' traversal' + (traversalCount !== 1 ? 's' : '') + '</div>' +
        '</div>' +
        '<div class="saved-journey-actions">' +
          '<button class="btn btn-small btn-resume" data-network-id="' + n.network_id + '">Open</button>' +
          '<button class="btn btn-small btn-delete-journey" data-network-id="' + n.network_id + '">&times;</button>' +
        '</div>' +
      '</div>';
    }).join('');

    // Bind events
    list.querySelectorAll('.btn-resume').forEach(function(btn) {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        var id = btn.getAttribute('data-network-id');
        if (state.loadNetwork(id)) {
          showNetworkScreen();
        }
      });
    });

    list.querySelectorAll('.btn-delete-journey').forEach(function(btn) {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        var id = btn.getAttribute('data-network-id');
        if (confirm('Delete this saved network?')) {
          state.deleteSavedNetwork(id);
          renderSavedNetworks();
        }
      });
    });
  }

  // ========== Config Wizard ==========

  function renderConfigStep() {
    var step = state.getConfigStep();
    var content = document.getElementById('config-content');

    // Update stepper indicators
    document.querySelectorAll('.config-step-indicator').forEach(function(ind) {
      var s = parseInt(ind.getAttribute('data-step'), 10);
      ind.classList.toggle('active', s === step);
      ind.classList.toggle('completed', s < step);
    });

    // Update nav buttons
    var backBtn = document.getElementById('btn-config-back');
    var nextBtn = document.getElementById('btn-config-next');
    backBtn.textContent = step === 1 ? 'Cancel' : 'Back';

    if (step === 4) {
      nextBtn.textContent = 'Confirm & Continue';
      nextBtn.disabled = !state.isConfigComplete();
    } else {
      nextBtn.textContent = 'Next';
      nextBtn.disabled = !state.isConfigStepComplete(step);
    }

    // Render step content
    if (step === 1) {
      renderConfigArchetypes(content);
    } else if (step === 2) {
      renderConfigMotifs(content);
    } else if (step === 3) {
      renderConfigEntities(content);
    } else if (step === 4) {
      renderConfigReview(content);
    }
  }

  // ----- Step 1: Archetypes -----

  function renderConfigArchetypes(container) {
    var cfg = state.getConfigState();
    var html = '<div class="config-step-content">' +
      '<h3 class="config-step-title">Choose two archetypes that define this network\'s tension</h3>' +
      '<div class="config-archetype-pair">';

    // Primary archetype
    html += renderArchetypeSlot('primary', 'Primary Archetype', cfg.primary_archetype);
    // Secondary archetype
    html += renderArchetypeSlot('secondary', 'Secondary Archetype', cfg.secondary_archetype);

    html += '</div></div>';
    container.innerHTML = html;
    bindArchetypeSlotEvents();
  }

  function renderArchetypeSlot(which, label, current) {
    var html = '<div class="config-slot" data-which="' + which + '">';
    html += '<div class="config-slot-label">' + label + '</div>';

    if (current) {
      var tradition = current.tradition || (current.id ? current.id.split(':')[0].replace('arch:', '') : '');
      html += '<div class="config-slot-filled">' +
        '<div class="config-slot-name">' + utils.escapeHtml(current.name || current.id) + '</div>' +
        '<div class="config-slot-meta">' + utils.escapeHtml(tradition) + '</div>' +
        '<button class="config-slot-clear" data-which="' + which + '">&times;</button>' +
      '</div>';
    } else {
      html += '<div class="config-slot-empty">' +
        '<div class="selection-search">' +
          '<input type="text" class="selection-search-input" id="arch-search-' + which + '" placeholder="Search archetypes...">' +
        '</div>' +
        '<div class="choice-grid" id="arch-grid-' + which + '"></div>' +
      '</div>';
    }

    html += '</div>';
    return html;
  }

  function bindArchetypeSlotEvents() {
    ['primary', 'secondary'].forEach(function(which) {
      var searchInput = document.getElementById('arch-search-' + which);
      var grid = document.getElementById('arch-grid-' + which);

      if (!grid) return; // Already filled

      // Initial display
      var initial = archetypesData && archetypesData.archetypes ? archetypesData.archetypes.slice(0, DISPLAY_LIMIT - 1) : [];
      renderArchetypeGrid(grid, initial, which);

      if (searchInput) {
        searchInput.addEventListener('input', utils.debounce(function() {
          var all = archetypesData && archetypesData.archetypes ? archetypesData.archetypes : [];
          var filtered = filters.searchArchetypes(all, searchInput.value).slice(0, DISPLAY_LIMIT - 1);
          renderArchetypeGrid(grid, filtered, which);
        }, 200));
      }
    });

    // Clear buttons
    document.querySelectorAll('.config-slot-clear').forEach(function(btn) {
      btn.addEventListener('click', function() {
        state.setConfigArchetype(btn.getAttribute('data-which'), null);
        renderConfigStep();
      });
    });
  }

  function renderArchetypeGrid(grid, archetypes, which) {
    grid.innerHTML = archetypes.map(function(a) {
      var tradition = a.tradition || (a.id ? a.id.split(':')[0].replace('arch:', '') : '');
      return '<div class="choice-card" data-type="archetype" data-which="' + which + '" data-id="' + utils.escapeAttr(a.id) + '">' +
        '<div class="choice-card-name">' + utils.escapeHtml(a.name || a.id) + '</div>' +
        '<div class="choice-card-meta">' + utils.escapeHtml(tradition) + '</div>' +
      '</div>';
    }).join('') +
    '<div class="choice-card choice-card-surprise" data-action="surprise" data-which="' + which + '">' +
      '<div class="choice-card-name">Surprise Me</div>' +
      '<div class="choice-card-meta">Random archetype</div>' +
    '</div>';

    grid.onclick = function(e) {
      var card = e.target.closest('.choice-card');
      if (!card) return;

      var w = card.getAttribute('data-which');
      if (card.getAttribute('data-action') === 'surprise') {
        var pool = archetypesData && archetypesData.archetypes ? archetypesData.archetypes : [];
        var random = filters.getRandomItem(pool);
        if (random) {
          state.setConfigArchetype(w, random);
          renderConfigStep();
        }
        return;
      }

      var id = card.getAttribute('data-id');
      var arch = archetypesData && archetypesData.archetypes ?
        archetypesData.archetypes.find(function(a) { return a.id === id; }) : null;
      if (!arch && id) {
        var nameEl = card.querySelector('.choice-card-name');
        arch = { id: id, name: nameEl ? nameEl.textContent : id };
      }
      if (arch) {
        state.setConfigArchetype(w, arch);
        renderConfigStep();
      }
    };
  }

  // ----- Step 2: Motifs -----

  function renderConfigMotifs(container) {
    var cfg = state.getConfigState();
    var html = '<div class="config-step-content">' +
      '<h3 class="config-step-title">Choose six motifs &mdash; three primary positions, three secondary</h3>' +
      '<div class="config-motif-columns">' +
        '<div class="config-motif-column">' +
          '<h4 class="config-column-title">Primary Positions</h4>' +
          renderMotifSlot('1P', 'Position 1P (conditions 1 & 4)', cfg.motifs['1P']) +
          renderMotifSlot('2P', 'Position 2P (conditions 2 & 5)', cfg.motifs['2P']) +
          renderMotifSlot('3P', 'Position 3P (conditions 3 & 6)', cfg.motifs['3P']) +
        '</div>' +
        '<div class="config-motif-column">' +
          '<h4 class="config-column-title">Secondary Positions</h4>' +
          renderMotifSlot('1S', 'Position 1S', cfg.motifs['1S']) +
          renderMotifSlot('2S', 'Position 2S', cfg.motifs['2S']) +
          renderMotifSlot('3S', 'Position 3S', cfg.motifs['3S']) +
        '</div>' +
      '</div></div>';

    container.innerHTML = html;
    bindMotifSlotEvents();
  }

  function renderMotifSlot(position, label, current) {
    var html = '<div class="config-slot config-slot-motif" data-position="' + position + '">';
    html += '<div class="config-slot-label">' + label + '</div>';

    if (current) {
      html += '<div class="config-slot-filled">' +
        '<div class="config-slot-name">' + utils.escapeHtml(current.code + ' - ' + current.label) + '</div>' +
        '<button class="config-slot-clear" data-position="' + position + '">&times;</button>' +
      '</div>';
    } else {
      html += '<div class="config-slot-empty">' +
        '<div class="selection-search">' +
          '<input type="text" class="selection-search-input motif-slot-search" data-position="' + position + '" placeholder="Search motifs...">' +
        '</div>' +
        '<div class="motif-list motif-slot-list" data-position="' + position + '"></div>' +
      '</div>';
    }

    html += '</div>';
    return html;
  }

  function getSelectedMotifCodes(excludePosition) {
    var cfg = state.getConfigState();
    var codes = {};
    var slots = ['1P', '2P', '3P', '1S', '2S', '3S'];
    for (var i = 0; i < slots.length; i++) {
      if (slots[i] !== excludePosition && cfg.motifs[slots[i]]) {
        codes[cfg.motifs[slots[i]].code] = true;
      }
    }
    return codes;
  }

  function getRandomSample(allMotifs, excludeCodes, count) {
    // Group available motifs by category
    var byCategory = {};
    for (var i = 0; i < allMotifs.length; i++) {
      var m = allMotifs[i];
      if (excludeCodes[m.code]) continue;
      var cat = m.category;
      if (!byCategory[cat]) byCategory[cat] = [];
      byCategory[cat].push(m);
    }
    // Pick 1 random from each category
    var sample = [];
    var cats = Object.keys(byCategory);
    for (var c = 0; c < cats.length; c++) {
      var pool = byCategory[cats[c]];
      sample.push(pool[Math.floor(Math.random() * pool.length)]);
    }
    // Shuffle using Fisher-Yates
    for (var j = sample.length - 1; j > 0; j--) {
      var k = Math.floor(Math.random() * (j + 1));
      var temp = sample[j]; sample[j] = sample[k]; sample[k] = temp;
    }
    return sample.slice(0, count || 15);
  }

  function bindMotifSlotEvents() {
    var allMotifs = getMotifArray();

    document.querySelectorAll('.motif-slot-search').forEach(function(input) {
      var position = input.getAttribute('data-position');
      var list = document.querySelector('.motif-slot-list[data-position="' + position + '"]');

      // Initial display: category-diverse random sample, excluding already-selected
      var selectedCodes = getSelectedMotifCodes(position);
      renderMotifSlotList(list, getRandomSample(allMotifs, selectedCodes, 15), position);

      input.addEventListener('input', utils.debounce(function() {
        var selected = getSelectedMotifCodes(position);
        var filtered = filters.searchMotifs(allMotifs, input.value).filter(function(m) {
          return !selected[m.code];
        });
        renderMotifSlotList(list, filtered.slice(0, 20), position);
      }, 200));
    });

    // Clear buttons
    document.querySelectorAll('.config-slot-clear[data-position]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        state.setConfigMotif(btn.getAttribute('data-position'), null);
        renderConfigStep();
      });
    });
  }

  function renderMotifSlotList(list, motifs, position) {
    var selectedCodes = getSelectedMotifCodes(position);

    list.innerHTML =
    '<div class="motif-item motif-item-surprise" data-position="' + position + '">' +
      '<span class="motif-code">\u2728</span>' +
      '<span class="motif-name">Surprise Me</span>' +
    '</div>' +
    motifs.map(function(m) {
      var disabled = selectedCodes[m.code] ? ' motif-item-disabled' : '';
      return '<div class="motif-item' + disabled + '" data-code="' + m.code + '" data-position="' + position + '">' +
        '<span class="motif-code">' + m.code + '</span>' +
        '<span class="motif-name">' + utils.escapeHtml(m.label) + '</span>' +
      '</div>';
    }).join('');

    list.onclick = function(e) {
      var item = e.target.closest('.motif-item');
      if (!item) return;

      // Handle Surprise Me
      if (item.classList.contains('motif-item-surprise')) {
        var pos = item.getAttribute('data-position');
        var excluded = getSelectedMotifCodes(pos);
        var available = getMotifArray().filter(function(m) { return !excluded[m.code]; });
        if (available.length > 0) {
          var random = available[Math.floor(Math.random() * available.length)];
          state.setConfigMotif(pos, random);
          renderConfigStep();
        }
        return;
      }

      // Ignore disabled items
      if (item.classList.contains('motif-item-disabled')) return;

      var code = item.getAttribute('data-code');
      var pos = item.getAttribute('data-position');
      var motif = getMotifArray().find(function(m) { return m.code === code; });
      if (motif) {
        state.setConfigMotif(pos, motif);
        renderConfigStep();
      }
    };
  }

  function getMotifArray() {
    if (!patternsData || !patternsData.motifs) return [];
    return Object.keys(patternsData.motifs).map(function(code) {
      var m = patternsData.motifs[code];
      return { code: code, label: m.label, category: m.category || code.charAt(0) };
    }).sort(function(a, b) { return a.code.localeCompare(b.code); });
  }

  // ----- Step 3: Entities -----

  function renderConfigEntities(container) {
    var cfg = state.getConfigState();
    var html = '<div class="config-step-content">' +
      '<h3 class="config-step-title">Choose three entities &mdash; one per polarity pair</h3>' +
      '<div class="config-entity-slots">';

    html += renderEntitySlot('pair_14', 'Entity for conditions 1 &amp; 4 (Dawn &harr; Alignment)', cfg.entities.pair_14);
    html += renderEntitySlot('pair_25', 'Entity for conditions 2 &amp; 5 (Immersion &harr; Unveiling)', cfg.entities.pair_25);
    html += renderEntitySlot('pair_36', 'Entity for conditions 3 &amp; 6 (Crucible &harr; Return)', cfg.entities.pair_36);

    html += '</div></div>';
    container.innerHTML = html;
    bindEntitySlotEvents();
  }

  function renderEntitySlot(pair, label, current) {
    var html = '<div class="config-slot" data-pair="' + pair + '">';
    html += '<div class="config-slot-label">' + label + '</div>';

    if (current) {
      html += '<div class="config-slot-filled">' +
        '<div class="config-slot-name">' + utils.escapeHtml(current.name || 'Selected') + '</div>' +
        '<div class="config-slot-meta">' + utils.escapeHtml(current.primary_tradition || current.type || '') + '</div>' +
        '<button class="config-slot-clear" data-pair="' + pair + '">&times;</button>' +
      '</div>';
    } else {
      html += '<div class="config-slot-empty">' +
        '<div class="selection-search">' +
          '<input type="text" class="selection-search-input entity-slot-search" data-pair="' + pair + '" placeholder="Search entities...">' +
        '</div>' +
        '<div class="choice-grid entity-slot-grid" data-pair="' + pair + '"></div>' +
      '</div>';
    }

    html += '</div>';
    return html;
  }

  function bindEntitySlotEvents() {
    document.querySelectorAll('.entity-slot-search').forEach(function(input) {
      var pair = input.getAttribute('data-pair');
      var grid = document.querySelector('.entity-slot-grid[data-pair="' + pair + '"]');

      // Initial display
      var initial = entitiesData && entitiesData.entities ? entitiesData.entities.slice(0, DISPLAY_LIMIT - 1) : [];
      renderEntityGrid(grid, initial, pair);

      input.addEventListener('input', utils.debounce(function() {
        var all = entitiesData && entitiesData.entities ? entitiesData.entities : [];
        var filtered = filters.searchEntities(all, input.value).slice(0, DISPLAY_LIMIT - 1);
        renderEntityGrid(grid, filtered, pair);
      }, 200));
    });

    // Clear buttons
    document.querySelectorAll('.config-slot-clear[data-pair]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        state.setConfigEntity(btn.getAttribute('data-pair'), null);
        renderConfigStep();
      });
    });
  }

  function renderEntityGrid(grid, entities, pair) {
    grid.innerHTML = entities.map(function(e) {
      return '<div class="choice-card" data-type="entity" data-pair="' + pair + '" data-name="' + utils.escapeAttr(e.name) + '">' +
        '<div class="choice-card-name">' + utils.escapeHtml(e.name) + '</div>' +
        '<div class="choice-card-meta">' + utils.escapeHtml(e.primary_tradition || e.type || '') + '</div>' +
      '</div>';
    }).join('') +
    '<div class="choice-card choice-card-surprise" data-action="surprise" data-pair="' + pair + '">' +
      '<div class="choice-card-name">Surprise Me</div>' +
      '<div class="choice-card-meta">Random entity</div>' +
    '</div>';

    grid.onclick = function(e) {
      var card = e.target.closest('.choice-card');
      if (!card) return;

      var p = card.getAttribute('data-pair');
      if (card.getAttribute('data-action') === 'surprise') {
        var pool = entitiesData && entitiesData.entities ? entitiesData.entities : [];
        var random = filters.getRandomItem(pool);
        if (random) {
          state.setConfigEntity(p, random);
          renderConfigStep();
        }
        return;
      }

      var name = card.getAttribute('data-name');
      var entity = entitiesData && entitiesData.entities ?
        entitiesData.entities.find(function(e) { return e.name === name; }) : null;
      if (!entity && name) {
        entity = { name: name };
      }
      if (entity) {
        state.setConfigEntity(p, entity);
        renderConfigStep();
      }
    };
  }

  // ----- Step 4: Review -----

  function renderConfigReview(container) {
    var cfg = state.getConfigState();
    var html = '<div class="config-step-content">' +
      '<h3 class="config-step-title">Review your network configuration</h3>';

    // Archetype summary
    html += '<div class="review-section">' +
      '<h4>Archetypes</h4>' +
      '<div class="review-archetypes">' +
        '<span class="review-tag">' + utils.escapeHtml(cfg.primary_archetype ? cfg.primary_archetype.name : '?') + '</span>' +
        '<span class="review-vs">&amp;</span>' +
        '<span class="review-tag">' + utils.escapeHtml(cfg.secondary_archetype ? cfg.secondary_archetype.name : '?') + '</span>' +
      '</div>' +
    '</div>';

    // Motif summary
    html += '<div class="review-section">' +
      '<h4>Motifs</h4>' +
      '<div class="review-motifs">';
    ['1P', '2P', '3P', '1S', '2S', '3S'].forEach(function(pos) {
      var m = cfg.motifs[pos];
      html += '<div class="review-motif-item">' +
        '<span class="review-motif-pos">' + pos + '</span>' +
        '<span class="review-motif-code">' + (m ? m.code : '?') + '</span>' +
        '<span class="review-motif-label">' + utils.escapeHtml(m ? m.label : 'Not selected') + '</span>' +
      '</div>';
    });
    html += '</div></div>';

    // Entity summary
    html += '<div class="review-section">' +
      '<h4>Entities</h4>' +
      '<div class="review-entities">';
    var pairLabels = { pair_14: '1 &harr; 4', pair_25: '2 &harr; 5', pair_36: '3 &harr; 6' };
    ['pair_14', 'pair_25', 'pair_36'].forEach(function(pair) {
      var e = cfg.entities[pair];
      html += '<div class="review-entity-item">' +
        '<span class="review-entity-pair">' + pairLabels[pair] + '</span>' +
        '<span class="review-entity-name">' + utils.escapeHtml(e ? e.name : 'Not selected') + '</span>' +
      '</div>';
    });
    html += '</div></div>';

    // 18-node preview grid
    html += '<div class="review-section">' +
      '<h4>Network Preview</h4>' +
      renderReviewGrid(cfg) +
    '</div>';

    html += '</div>';
    container.innerHTML = html;
  }

  function renderReviewGrid(cfg) {
    var arcs = [
      { code: 'D', name: 'Descent' },
      { code: 'R', name: 'Resonance' },
      { code: 'E', name: 'Emergence' }
    ];

    var html = '<div class="review-grid">';

    // Header row
    html += '<div class="review-grid-header">';
    html += '<div class="review-grid-cell review-grid-corner"></div>';
    for (var c = 1; c <= 6; c++) {
      html += '<div class="review-grid-cell review-grid-col-header">' + c + '</div>';
    }
    html += '</div>';

    // Arc rows
    arcs.forEach(function(arc) {
      html += '<div class="review-grid-row">';
      html += '<div class="review-grid-cell review-grid-row-header arc-' + arc.code + '">' + arc.code + '</div>';

      for (var c = 1; c <= 6; c++) {
        var nodeId = arc.code + c;
        var contents = state.getNodeContents(nodeId, cfg);
        var pm = contents && contents.primary_motif ? contents.primary_motif.code : '?';
        var sm = contents && contents.secondary_motif ? contents.secondary_motif.code : '?';
        var eName = contents && contents.entity ? contents.entity.name : '?';

        html += '<div class="review-grid-cell review-grid-node arc-' + arc.code + '">' +
          '<div class="review-grid-node-id">' + nodeId + '</div>' +
          '<div class="review-grid-node-motifs">' + pm + ' + ' + sm + '</div>' +
          '<div class="review-grid-node-entity">' + utils.escapeHtml(eName) + '</div>' +
        '</div>';
      }

      html += '</div>';
    });

    html += '</div>';
    return html;
  }

  // ========== Network Screen ==========

  function renderNetworkGrid() {
    var network = state.getNetwork();
    if (!network) return;
    var config = network.configuration;
    var grid = document.getElementById('network-grid');

    var arcs = [
      { code: 'D', name: 'Descent', secondary: 'Shadow' },
      { code: 'R', name: 'Resonance', secondary: 'Mirror' },
      { code: 'E', name: 'Emergence', secondary: 'Mythogenesis' }
    ];

    var html = '';

    arcs.forEach(function(arc) {
      html += '<div class="network-arc-row">' +
        '<div class="network-arc-label arc-' + arc.code + '">' + arc.name + '</div>';

      for (var c = 1; c <= 6; c++) {
        var nodeId = arc.code + c;
        var contents = state.getNodeContents(nodeId, config);
        var template = getNodeTemplate(nodeId);
        var title = template ? template.identity.title : nodeId;

        var pm = contents && contents.primary_motif ? contents.primary_motif.code : '?';
        var sm = contents && contents.secondary_motif ? contents.secondary_motif.code : '?';
        var eName = contents && contents.entity ? contents.entity.name : '?';
        var positions = state.getNodePositions(nodeId);

        html += '<div class="network-node-card arc-' + arc.code + '" data-node-id="' + nodeId + '">' +
          '<div class="network-node-id">' + nodeId + '</div>' +
          '<div class="network-node-title">' + utils.escapeHtml(title) + '</div>' +
          '<div class="network-node-motifs">' +
            '<span class="network-motif-tag">' + (positions ? positions.primary : '') + ': ' + pm + '</span> ' +
            '<span class="network-motif-tag">' + (positions ? positions.secondary : '') + ': ' + sm + '</span>' +
          '</div>' +
          '<div class="network-node-entity">' + utils.escapeHtml(eName) + '</div>' +
        '</div>';
      }

      html += '</div>';
    });

    grid.innerHTML = html;

    // Click handler for node detail
    grid.querySelectorAll('.network-node-card').forEach(function(card) {
      card.addEventListener('click', function() {
        var nodeId = card.getAttribute('data-node-id');
        showNodeDetailModal(nodeId);
      });
    });
  }

  function showNodeDetailModal(nodeId) {
    var network = state.getNetwork();
    if (!network) return;

    var contents = state.getNodeContents(nodeId, network.configuration);
    var template = getNodeTemplate(nodeId);
    var positions = state.getNodePositions(nodeId);

    var container = document.getElementById('node-detail-content');
    var arcClass = 'arc-' + nodeId.charAt(0);

    var html = '<div class="node-detail ' + arcClass + '">';

    if (template) {
      var identity = template.identity;
      html += '<div class="node-info-header">' +
        '<span class="node-info-id">' + nodeId + '</span>' +
      '</div>' +
      '<div class="node-info-title">' + utils.escapeHtml(identity.title) + '</div>' +
      '<div class="node-info-role">' + utils.escapeHtml(identity.role) + '</div>' +
      '<div class="node-info-meta">' +
        identity.arc.primary + '/' + identity.arc.secondary + ' &ndash; ' +
        identity.condition.primary + '/' + identity.condition.secondary +
      '</div>' +
      '<div class="node-info-tone">' +
        (identity.tone || []).map(function(t) {
          return '<span class="tone-tag">' + utils.escapeHtml(t) + '</span>';
        }).join('') +
      '</div>';

      var question = template.thematic_lens.questions ? template.thematic_lens.questions[0] : '';
      if (question) {
        html += '<div class="node-info-question">"' + utils.escapeHtml(question) + '"</div>';
      }
    }

    if (contents) {
      html += '<div class="node-detail-contents">' +
        '<div class="node-detail-row"><strong>Primary Archetype:</strong> ' +
          utils.escapeHtml(contents.primary_archetype ? contents.primary_archetype.name : '?') + '</div>' +
        '<div class="node-detail-row"><strong>Secondary Archetype:</strong> ' +
          utils.escapeHtml(contents.secondary_archetype ? contents.secondary_archetype.name : '?') + '</div>' +
        '<div class="node-detail-row"><strong>Primary Motif (' + (positions ? positions.primary : '') + '):</strong> ' +
          (contents.primary_motif ? contents.primary_motif.code + ' - ' + utils.escapeHtml(contents.primary_motif.label) : '?') + '</div>' +
        '<div class="node-detail-row"><strong>Secondary Motif (' + (positions ? positions.secondary : '') + '):</strong> ' +
          (contents.secondary_motif ? contents.secondary_motif.code + ' - ' + utils.escapeHtml(contents.secondary_motif.label) : '?') + '</div>' +
        '<div class="node-detail-row"><strong>Entity:</strong> ' +
          utils.escapeHtml(contents.entity ? contents.entity.name : '?') + '</div>' +
      '</div>';
    }

    html += '</div>';
    container.innerHTML = html;
    document.getElementById('modal-node-detail').hidden = false;
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
    showConfigScreen: showConfigScreen,
    showNetworkScreen: showNetworkScreen,
    renderConfigStep: renderConfigStep,
    renderSavedNetworks: renderSavedNetworks,
    renderNetworkGrid: renderNetworkGrid,
    showNodeDetailModal: showNodeDetailModal
  };
})();
