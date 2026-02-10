// Mythic System Explorer — Codex View
// Card grid with sub-tabs (archetypes/entities/motifs/validation), filtering, lazy loading, and detail views

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var dataLoader = window.MiroGlyph.dataLoader;
  var cardRenderer = window.MiroGlyph.cardRenderer;
  var detailSheet = window.MiroGlyph.detailSheet;
  var nav = window.MiroGlyph.nav;
  var tabRouter = window.MiroGlyph.tabRouter;

  var BATCH_SIZE = 50;

  // --- State ---

  var container = null;
  var gridEl = null;
  var filterBarEl = null;
  var countEl = null;

  var subTab = 'archetypes';
  var filters = {
    search: '',
    system: '',
    primordial: '',
    nearestNode: '',
    type: '',
    tradition: '',
    mapped: '',
    category: ''
  };
  var detailItem = null;  // null = grid view, otherwise { kind, id }
  var filteredData = [];
  var renderedCount = 0;
  var observer = null;
  var debounceTimer = null;
  var boundDetailClick = null;
  var boundSubTabClick = null;

  // Validation state
  var expandedTiers = {};
  var expandedTests = {};
  var expandedAuditCases = {};

  // --- Verdict Styling ---
  var VERDICT_BORDER = {
    PASS: '#10b981',
    PARTIAL: '#f59e0b',
    FAIL: '#ef4444',
    MIXED: '#6366f1',
    PENDING: '#94a3b8',
    ALTERNATIVES_FOUND: '#f59e0b'
  };

  function verdictClass(verdict) {
    if (!verdict) return 'verdict-pending';
    var v = verdict.toUpperCase();
    if (v === 'PASS') return 'verdict-pass';
    if (v === 'PARTIAL' || v === 'ALTERNATIVES_FOUND') return 'verdict-partial';
    if (v === 'FAIL') return 'verdict-fail';
    if (v === 'MIXED') return 'verdict-mixed';
    return 'verdict-pending';
  }

  // --- Init ---

  function init(el) {
    container = el;

    container.innerHTML =
      '<div class="codex-layout">' +
        '<div class="codex-filter-bar" id="codex-filter-bar"></div>' +
        '<div class="codex-grid" id="codex-grid"></div>' +
      '</div>';

    filterBarEl = container.querySelector('#codex-filter-bar');
    gridEl = container.querySelector('#codex-grid');

    buildFilterBar();
    wireFilterEvents();
    renderGrid();
  }

  // --- Activate / Deactivate ---

  function activate() {}

  function deactivate() {
    if (observer) {
      observer.disconnect();
    }
  }

  // --- Route Handling ---

  function onRoute(params) {
    if (!params || !container) return;

    if (params.subview === 'archetype' && params.id) {
      showArchetypeDetail(decodeURIComponent(params.id));
    } else if (params.subview === 'entity' && params.id) {
      showEntityDetail(decodeURIComponent(params.id));
    } else if (params.subview === 'validation') {
      switchSubTab('validation');
    } else {
      // No sub-route: show grid
      if (detailItem) {
        detailItem = null;
        buildFilterBar();
        wireFilterEvents();
        renderGrid();
      }
    }
  }

  // --- Filter Bar ---

  function buildFilterBar() {
    var isValidation = (subTab === 'validation');

    var html = '<div style="display:flex;align-items:center;gap:var(--spacing-sm);flex-wrap:wrap;padding:var(--spacing-sm) var(--spacing-lg)">';

    // Sub-tab toggles
    html += '<div class="codex-sub-tabs">';
    html += '<button class="codex-sub-tab' + (subTab === 'archetypes' ? ' active' : '') + '" data-sub="archetypes">Archetypes</button>';
    html += '<button class="codex-sub-tab' + (subTab === 'entities' ? ' active' : '') + '" data-sub="entities">Entities</button>';
    html += '<button class="codex-sub-tab' + (subTab === 'motifs' ? ' active' : '') + '" data-sub="motifs">Motifs</button>';
    html += '<button class="codex-sub-tab' + (subTab === 'validation' ? ' active' : '') + '" data-sub="validation">Validation</button>';
    html += '</div>';

    if (!isValidation) {
      // Search
      html += '<input type="text" class="search-input" id="codex-search" placeholder="Search..." value="' +
        escapeAttr(filters.search) + '" style="flex:1;min-width:160px">';

      // Dropdowns depend on sub-tab
      if (subTab === 'archetypes') {
        html += buildArchetypeFilters();
      } else if (subTab === 'entities') {
        html += buildEntityFilters();
      } else if (subTab === 'motifs') {
        html += buildMotifFilters();
      }

      // Surprise Me button
      html += '<button class="btn btn-small btn-surprise" id="codex-surprise" title="Random discovery">';
      html += '\u2728 Surprise Me';
      html += '</button>';

      // Count
      html += '<span id="codex-count" class="result-count" style="margin-left:auto;white-space:nowrap"></span>';
    }

    html += '</div>';
    filterBarEl.innerHTML = html;
    countEl = filterBarEl.querySelector('#codex-count');

    if (!isValidation) {
      // Wire up surprise button
      var surpriseBtn = filterBarEl.querySelector('#codex-surprise');
      if (surpriseBtn) {
        surpriseBtn.addEventListener('click', function() {
          var nav = window.MiroGlyph.nav;
          if (nav && nav.surpriseMe) {
            if (subTab === 'archetypes') nav.surpriseMe('archetype');
            else if (subTab === 'entities') nav.surpriseMe('entity');
            else if (subTab === 'motifs') nav.surpriseMe('motif');
          }
        });
      }
    }
  }

  function buildArchetypeFilters() {
    var archData = dataLoader.get('archetypes');
    var html = '';

    // System dropdown
    html += '<select class="filter-select" id="codex-filter-system">';
    html += '<option value="">All Systems</option>';
    if (archData && archData.systems) {
      for (var i = 0; i < archData.systems.length; i++) {
        var s = archData.systems[i];
        var selected = filters.system === s.code ? ' selected' : '';
        html += '<option value="' + escapeAttr(s.code) + '"' + selected + '>' +
          escapeHtml(s.name) + ' (' + s.count + ')' +
        '</option>';
      }
    }
    html += '</select>';

    // Primordial dropdown
    html += '<select class="filter-select" id="codex-filter-primordial">';
    html += '<option value="">All Primordials</option>';
    if (archData && archData.primordials) {
      for (var p = 0; p < archData.primordials.length; p++) {
        var pr = archData.primordials[p];
        var selected = filters.primordial === pr.id ? ' selected' : '';
        html += '<option value="' + escapeAttr(pr.id) + '"' + selected + '>' +
          escapeHtml(pr.name) +
        '</option>';
      }
    }
    html += '</select>';

    // Nearest-node dropdown
    html += '<select class="filter-select" id="codex-filter-node">';
    html += '<option value="">All Nodes</option>';
    var nodeIds = ['D1','D2','D3','D4','D5','D6','R1','R2','R3','R4','R5','R6','E1','E2','E3','E4','E5','E6'];
    for (var n = 0; n < nodeIds.length; n++) {
      var selected = filters.nearestNode === nodeIds[n] ? ' selected' : '';
      html += '<option value="' + nodeIds[n] + '"' + selected + '>' + nodeIds[n] + '</option>';
    }
    html += '</select>';

    return html;
  }

  function buildEntityFilters() {
    var entData = dataLoader.get('entities');
    var html = '';

    // Collect unique types and traditions
    var types = {};
    var traditions = {};
    if (entData && entData.entities) {
      for (var i = 0; i < entData.entities.length; i++) {
        var ent = entData.entities[i];
        if (ent.type) types[ent.type] = true;
        if (ent.primary_tradition) traditions[ent.primary_tradition] = true;
      }
    }

    // Type dropdown
    html += '<select class="filter-select" id="codex-filter-type">';
    html += '<option value="">All Types</option>';
    var typeKeys = Object.keys(types).sort();
    for (var t = 0; t < typeKeys.length; t++) {
      var selected = filters.type === typeKeys[t] ? ' selected' : '';
      html += '<option value="' + escapeAttr(typeKeys[t]) + '"' + selected + '>' +
        escapeHtml(typeKeys[t]) +
      '</option>';
    }
    html += '</select>';

    // Tradition dropdown
    html += '<select class="filter-select" id="codex-filter-tradition">';
    html += '<option value="">All Traditions</option>';
    var tradKeys = Object.keys(traditions).sort();
    for (var tr = 0; tr < tradKeys.length; tr++) {
      var selected = filters.tradition === tradKeys[tr] ? ' selected' : '';
      html += '<option value="' + escapeAttr(tradKeys[tr]) + '"' + selected + '>' +
        escapeHtml(tradKeys[tr]) +
      '</option>';
    }
    html += '</select>';

    // Mapped toggle
    html += '<select class="filter-select" id="codex-filter-mapped">';
    html += '<option value=""' + (filters.mapped === '' ? ' selected' : '') + '>All</option>';
    html += '<option value="mapped"' + (filters.mapped === 'mapped' ? ' selected' : '') + '>Mapped</option>';
    html += '<option value="unmapped"' + (filters.mapped === 'unmapped' ? ' selected' : '') + '>Unmapped</option>';
    html += '</select>';

    return html;
  }

  function buildMotifFilters() {
    var patData = dataLoader.get('patterns');
    var motifs = patData && patData.motifs ? patData.motifs : {};
    var html = '';

    // Collect unique categories
    var categories = {};
    for (var code in motifs) {
      var cat = motifs[code].category || '?';
      categories[cat] = (categories[cat] || 0) + 1;
    }

    // Thompson Motif Index category names
    var catNames = {
      'A': 'Mythological',
      'B': 'Animals',
      'C': 'Tabu',
      'D': 'Magic',
      'E': 'The Dead',
      'F': 'Marvels',
      'G': 'Ogres',
      'H': 'Tests',
      'J': 'Wisdom',
      'K': 'Deceptions',
      'L': 'Reversal of Fortune',
      'M': 'Ordaining the Future',
      'N': 'Chance',
      'P': 'Society',
      'Q': 'Rewards & Punishments',
      'R': 'Captives & Fugitives',
      'S': 'Cruelty',
      'T': 'Sex',
      'U': 'Nature of Life',
      'V': 'Religion',
      'W': 'Traits of Character',
      'X': 'Humor',
      'Z': 'Miscellaneous'
    };

    // Category dropdown
    html += '<select class="filter-select" id="codex-filter-category">';
    html += '<option value="">All Categories</option>';
    var catKeys = Object.keys(categories).sort();
    for (var c = 0; c < catKeys.length; c++) {
      var cat = catKeys[c];
      var catName = catNames[cat] || cat;
      var selected = filters.category === cat ? ' selected' : '';
      html += '<option value="' + escapeAttr(cat) + '"' + selected + '>' +
        escapeHtml(cat + ': ' + catName) + ' (' + categories[cat] + ')' +
      '</option>';
    }
    html += '</select>';

    return html;
  }

  // --- Filter Events ---

  function wireFilterEvents() {
    // Remove previous sub-tab delegation listener to prevent stacking
    if (boundSubTabClick) {
      filterBarEl.removeEventListener('click', boundSubTabClick);
    }
    boundSubTabClick = function(e) {
      var subBtn = e.target.closest('.codex-sub-tab');
      if (subBtn && subBtn.dataset.sub) {
        switchSubTab(subBtn.dataset.sub);
      }
    };
    filterBarEl.addEventListener('click', boundSubTabClick);

    // Search (debounced)
    var searchInput = filterBarEl.querySelector('#codex-search');
    if (searchInput) {
      searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(function() {
          filters.search = searchInput.value.trim();
          renderGrid();
        }, 200);
      });
    }

    // Dropdown changes
    wireDropdown('codex-filter-system', 'system');
    wireDropdown('codex-filter-primordial', 'primordial');
    wireDropdown('codex-filter-node', 'nearestNode');
    wireDropdown('codex-filter-type', 'type');
    wireDropdown('codex-filter-tradition', 'tradition');
    wireDropdown('codex-filter-mapped', 'mapped');
    wireDropdown('codex-filter-category', 'category');
  }

  function wireDropdown(elementId, filterKey) {
    var el = filterBarEl.querySelector('#' + elementId);
    if (el) {
      el.addEventListener('change', function() {
        filters[filterKey] = el.value;
        renderGrid();
      });
    }
  }

  function switchSubTab(newTab) {
    if (newTab === subTab) return;
    subTab = newTab;

    // Reset filters on tab switch
    filters.search = '';
    filters.system = '';
    filters.primordial = '';
    filters.nearestNode = '';
    filters.type = '';
    filters.tradition = '';
    filters.mapped = '';
    filters.category = '';

    detailItem = null;
    buildFilterBar();
    wireFilterEvents();

    if (subTab === 'validation') {
      renderValidationView();
    } else {
      renderGrid();
    }
  }

  // --- Grid Rendering ---

  function renderGrid() {
    // Clean up detail click listener when switching back to grid
    if (boundDetailClick) {
      gridEl.removeEventListener('click', boundDetailClick);
      boundDetailClick = null;
    }

    detailItem = null;
    filteredData = filterData();
    renderedCount = 0;

    if (countEl) {
      var totalLabel = subTab === 'archetypes' ? 'archetypes' : (subTab === 'entities' ? 'entities' : 'motifs');
      var totalCount = getTotalCount();
      countEl.textContent = filteredData.length + ' of ' + totalCount + ' ' + totalLabel;
    }

    if (filteredData.length === 0) {
      gridEl.innerHTML = '<p class="empty-state" style="padding:var(--spacing-xl)">No results match current filters.</p>';
      return;
    }

    gridEl.innerHTML = '<div class="card-grid" id="codex-card-grid"></div>';

    var cardGrid = gridEl.querySelector('#codex-card-grid');
    renderBatch(cardGrid);
    setupObserver(cardGrid);
    setupCardClicks(cardGrid);
  }

  function filterData() {
    if (subTab === 'archetypes') {
      return filterArchetypes();
    } else if (subTab === 'entities') {
      return filterEntities();
    } else if (subTab === 'motifs') {
      return filterMotifs();
    }
    return [];
  }

  function filterArchetypes() {
    var archData = dataLoader.get('archetypes');
    if (!archData || !archData.archetypes) return [];

    var query = filters.search.toLowerCase();
    var system = filters.system;
    var primordial = filters.primordial;
    var nearestNode = filters.nearestNode;

    return archData.archetypes.filter(function(a) {
      // System filter
      if (system && a.system !== system) return false;

      // Primordial filter
      if (primordial) {
        var hasPrim = false;
        var prims = a.primordials || [];
        for (var i = 0; i < prims.length; i++) {
          if (prims[i].id === primordial) { hasPrim = true; break; }
        }
        if (!hasPrim) return false;
      }

      // Nearest node filter
      if (nearestNode) {
        var hasNode = false;
        var nodes = a.nearest_nodes || [];
        for (var j = 0; j < nodes.length; j++) {
          if (nodes[j].node_id === nearestNode) { hasNode = true; break; }
        }
        if (!hasNode) return false;
      }

      // Search filter
      if (query) {
        var searchable = (a.name + ' ' + a.description + ' ' + a.id).toLowerCase();
        if (searchable.indexOf(query) === -1) return false;
      }

      return true;
    });
  }

  function filterEntities() {
    var entData = dataLoader.get('entities');
    if (!entData || !entData.entities) return [];

    var query = filters.search.toLowerCase();
    var type = filters.type;
    var tradition = filters.tradition;
    var mapped = filters.mapped;

    return entData.entities.filter(function(e) {
      if (type && e.type !== type) return false;
      if (tradition && e.primary_tradition !== tradition) return false;
      if (mapped === 'mapped' && !e.mapping) return false;
      if (mapped === 'unmapped' && e.mapping) return false;
      if (query && e.name.toLowerCase().indexOf(query) === -1) return false;
      return true;
    });
  }

  function filterMotifs() {
    var patData = dataLoader.get('patterns');
    if (!patData || !patData.motifs) return [];

    var motifs = patData.motifs;
    var patterns = patData.patterns || [];
    var query = filters.search.toLowerCase();
    var category = filters.category;

    // Build reverse index: motif code -> pattern names
    var motifToPatterns = {};
    for (var p = 0; p < patterns.length; p++) {
      var pat = patterns[p];
      var codes = pat.motif_codes || [];
      for (var c = 0; c < codes.length; c++) {
        if (!motifToPatterns[codes[c]]) motifToPatterns[codes[c]] = [];
        motifToPatterns[codes[c]].push(pat.name);
      }
    }

    // Convert to array and filter
    var result = [];
    for (var code in motifs) {
      var m = motifs[code];
      var motifObj = {
        code: code,
        label: m.label || '',
        category: m.category || '?',
        patterns: motifToPatterns[code] || []
      };

      // Category filter
      if (category && motifObj.category !== category) continue;

      // Search filter
      if (query) {
        var searchable = (code + ' ' + motifObj.label).toLowerCase();
        if (searchable.indexOf(query) === -1) continue;
      }

      result.push(motifObj);
    }

    // Sort by code
    result.sort(function(a, b) {
      return a.code.localeCompare(b.code, undefined, { numeric: true });
    });

    return result;
  }

  function getTotalCount() {
    if (subTab === 'archetypes') {
      var archData = dataLoader.get('archetypes');
      return archData && archData.archetypes ? archData.archetypes.length : 0;
    } else if (subTab === 'entities') {
      var entData = dataLoader.get('entities');
      return entData && entData.entities ? entData.entities.length : 0;
    } else if (subTab === 'motifs') {
      var patData = dataLoader.get('patterns');
      return patData && patData.motifs ? Object.keys(patData.motifs).length : 0;
    }
    return 0;
  }

  // --- Batch Rendering ---

  function renderBatch(cardGrid) {
    var end = Math.min(renderedCount + BATCH_SIZE, filteredData.length);
    var frag = document.createDocumentFragment();

    for (var i = renderedCount; i < end; i++) {
      var wrapper = document.createElement('div');
      if (subTab === 'archetypes') {
        wrapper.innerHTML = cardRenderer.renderArchetypeCard(filteredData[i]);
      } else if (subTab === 'entities') {
        wrapper.innerHTML = cardRenderer.renderEntityCard(filteredData[i]);
      } else if (subTab === 'motifs') {
        wrapper.innerHTML = renderMotifCard(filteredData[i]);
      }
      // Unwrap the single child element
      if (wrapper.firstElementChild) {
        frag.appendChild(wrapper.firstElementChild);
      }
    }

    renderedCount = end;
    cardGrid.appendChild(frag);

    // Add or update sentinel and re-observe it
    updateSentinel(cardGrid);
    if (observer) {
      var newSentinel = cardGrid.querySelector('.load-more-sentinel');
      if (newSentinel) {
        observer.observe(newSentinel);
      }
    }
  }

  function updateSentinel(cardGrid) {
    // Remove existing sentinel
    var existing = cardGrid.querySelector('.load-more-sentinel');
    if (existing) existing.remove();

    // Add sentinel if more data remains
    if (renderedCount < filteredData.length) {
      var sentinel = document.createElement('div');
      sentinel.className = 'load-more-sentinel';
      sentinel.textContent = 'Loading more...';
      sentinel.style.gridColumn = '1 / -1';
      cardGrid.appendChild(sentinel);
    }
  }

  // --- Motif Card Rendering ---

  var MOTIF_CATEGORIES = {
    'A': 'Mythological',
    'B': 'Animals',
    'C': 'Tabu',
    'D': 'Magic',
    'E': 'The Dead',
    'F': 'Marvels',
    'G': 'Ogres',
    'H': 'Tests',
    'J': 'Wisdom',
    'K': 'Deceptions',
    'L': 'Reversal',
    'M': 'Future',
    'N': 'Chance',
    'P': 'Society',
    'Q': 'Rewards',
    'R': 'Captives',
    'S': 'Cruelty',
    'T': 'Sex',
    'U': 'Life',
    'V': 'Religion',
    'W': 'Character',
    'X': 'Humor',
    'Z': 'Misc'
  };

  function renderMotifCard(motif) {
    var catName = MOTIF_CATEGORIES[motif.category] || motif.category;
    var patternCount = motif.patterns.length;
    // Get entities that have this motif
    var entitiesWithMotif = findEntitiesWithMotif(motif.code);
    var entityCount = entitiesWithMotif.length;

    var html = '<div class="codex-card motif-card" data-motif-code="' + escapeAttr(motif.code) + '" tabindex="0">';

    // Header: code + category badge
    html += '<div class="codex-card-header">';
    html += '<span class="codex-card-title">' + escapeHtml(motif.code) + '</span>';
    html += '<span class="badge" style="background:rgba(245,158,11,0.2);color:#fbbf24;font-size:0.65rem">' +
      escapeHtml(catName) + '</span>';
    html += '</div>';

    // Label/description
    if (motif.label) {
      html += '<div class="codex-card-desc">' + escapeHtml(motif.label) + '</div>';
    }

    // Stats row
    html += '<div class="motif-stats" style="display:flex;gap:12px;font-size:0.7rem;color:var(--color-text-muted);margin-bottom:8px">';
    html += '<span>' + patternCount + ' patterns</span>';
    if (entityCount > 0) {
      html += '<span class="clickable-count motif-entity-count" data-motif-code="' + escapeAttr(motif.code) + '">' + entityCount + ' entities</span>';
    }
    html += '</div>';

    // Patterns that use this motif - show ALL, scrollable
    html += '<div class="motif-patterns">';
    if (patternCount > 0) {
      html += '<div class="motif-patterns-label">Appears in:</div>';
      html += '<div class="motif-pattern-tags" style="max-height:80px;overflow-y:auto">';
      // Show ALL patterns, not truncated
      for (var p = 0; p < motif.patterns.length; p++) {
        var patName = cardRenderer.formatPatternName(motif.patterns[p]);
        html += '<span class="motif-pattern-tag" data-pattern="' + escapeAttr(motif.patterns[p]) + '">' +
          escapeHtml(patName) + '</span>';
      }
      html += '</div>';
    } else {
      html += '<div class="motif-patterns-label" style="opacity:0.5">Not used in any patterns</div>';
    }
    html += '</div>';

    // Entities with this motif preview (first 3)
    if (entityCount > 0) {
      html += '<div class="motif-entities" style="margin-top:8px;padding-top:8px;border-top:1px solid var(--color-border)">';
      html += '<div class="motif-patterns-label">Entities:</div>';
      html += '<div class="motif-entity-tags" style="display:flex;flex-wrap:wrap;gap:4px">';
      var displayCount = Math.min(3, entityCount);
      for (var e = 0; e < displayCount; e++) {
        html += '<span class="motif-entity-tag" data-entity="' + escapeAttr(entitiesWithMotif[e]) + '" style="font-size:0.7rem;padding:2px 6px;background:var(--color-bg);color:var(--color-library);border-radius:4px;cursor:pointer">' +
          escapeHtml(entitiesWithMotif[e]) + '</span>';
      }
      if (entityCount > 3) {
        html += '<span class="motif-entity-tag more" style="font-size:0.7rem;padding:2px 6px;color:var(--color-text-muted)">+' + (entityCount - 3) + ' more</span>';
      }
      html += '</div>';
      html += '</div>';
    }

    html += '</div>';
    return html;
  }

  // Find entities that have a specific motif code
  function findEntitiesWithMotif(motifCode) {
    var entData = dataLoader.get('entities');
    if (!entData || !entData.entities) return [];

    var result = [];
    for (var i = 0; i < entData.entities.length; i++) {
      var ent = entData.entities[i];
      // Check if entity has motifs and if this code is in them
      if (ent.motif_codes && ent.motif_codes.indexOf(motifCode) !== -1) {
        result.push(ent.name);
      }
    }
    return result;
  }

  // --- Intersection Observer ---

  function setupObserver(cardGrid) {
    if (observer) observer.disconnect();

    if (!('IntersectionObserver' in window)) return;

    observer = new IntersectionObserver(function(entries) {
      for (var i = 0; i < entries.length; i++) {
        if (entries[i].isIntersecting && renderedCount < filteredData.length) {
          renderBatch(cardGrid);
        }
      }
    }, {
      root: gridEl,
      rootMargin: '200px'
    });

    var sentinel = cardGrid.querySelector('.load-more-sentinel');
    if (sentinel) {
      observer.observe(sentinel);
    }
  }

  // --- Card Click Handling ---

  function setupCardClicks(cardGrid) {
    cardGrid.addEventListener('click', function(e) {
      // Pattern tag click -> navigate to Chronicle patterns
      var patternTag = e.target.closest('.motif-pattern-tag');
      if (patternTag && patternTag.dataset.pattern && !patternTag.classList.contains('more')) {
        e.stopPropagation();
        nav.toPattern(patternTag.dataset.pattern);
        return;
      }

      // Motif entity tag click -> navigate to entity detail
      var motifEntityTag = e.target.closest('.motif-entity-tag');
      if (motifEntityTag && motifEntityTag.dataset.entity && !motifEntityTag.classList.contains('more')) {
        e.stopPropagation();
        nav.toEntity(motifEntityTag.dataset.entity);
        return;
      }

      // Motif entity count click -> filter entities view by motif
      var entityCount = e.target.closest('.motif-entity-count');
      if (entityCount && entityCount.dataset.motifCode) {
        e.stopPropagation();
        // Switch to entities tab and could filter by motif in future
        // For now, switch to entities sub-tab
        switchSubTab('entities');
        return;
      }

      var archCard = e.target.closest('.arch-card');
      if (archCard && archCard.dataset.id) {
        nav.toArchetype(archCard.dataset.id);
        return;
      }

      var entityCard = e.target.closest('.entity-card');
      if (entityCard && entityCard.dataset.name) {
        nav.toEntity(entityCard.dataset.name);
        return;
      }

      // Motif card click -> could show detail in future
      var motifCard = e.target.closest('.motif-card');
      if (motifCard && motifCard.dataset.motifCode) {
        // For now, just highlight - could expand to full detail view later
        return;
      }
    });
  }

  // --- Detail Views ---

  function showArchetypeDetail(archetypeId) {
    var archById = dataLoader.getIndex('archetypeById');
    var archetype = archById[archetypeId];
    if (!archetype) {
      gridEl.innerHTML = '<p class="empty-state" style="padding:var(--spacing-xl)">Archetype not found: ' +
        escapeHtml(archetypeId) + '</p>';
      return;
    }

    detailItem = { kind: 'archetype', id: archetypeId };
    subTab = 'archetypes';

    // Hide filter bar during detail view
    filterBarEl.innerHTML = '';

    gridEl.innerHTML = detailSheet.renderArchetypeDetail(archetype);
    wireDetailEvents();
  }

  function showEntityDetail(entityName) {
    var entityByName = dataLoader.getIndex('entityByName');
    var entity = entityByName[entityName];
    if (!entity) {
      gridEl.innerHTML = '<p class="empty-state" style="padding:var(--spacing-xl)">Entity not found: ' +
        escapeHtml(entityName) + '</p>';
      return;
    }

    detailItem = { kind: 'entity', id: entityName };
    subTab = 'entities';

    // Hide filter bar during detail view
    filterBarEl.innerHTML = '';

    gridEl.innerHTML = detailSheet.renderEntityDetail(entity);
    wireDetailEvents();
  }

  function wireDetailEvents() {
    // Remove previous detail listener to prevent stacking
    if (boundDetailClick) {
      gridEl.removeEventListener('click', boundDetailClick);
    }
    boundDetailClick = handleDetailClick;
    gridEl.addEventListener('click', boundDetailClick);
  }

  function handleDetailClick(e) {
    var target = e.target.closest('[data-action]');
    if (!target) return;

    var action = target.dataset.action;

    if (action === 'back') {
      nav.back();
      return;
    }

    if (action === 'toArchetype' && target.dataset.id) {
      nav.toArchetype(target.dataset.id);
      return;
    }

    if (action === 'toEntity' && target.dataset.name) {
      nav.toEntity(target.dataset.name);
      return;
    }

    if (action === 'toNode' && target.dataset.nodeId) {
      nav.toNode(target.dataset.nodeId);
      return;
    }

    if (action === 'toPattern' && target.dataset.name) {
      nav.toPattern(target.dataset.name);
      return;
    }
  }

  // =========================================================================
  // Validation Sub-view (migrated from Chronicle)
  // =========================================================================

  function renderValidationView() {
    var data = dataLoader.get('validation');
    if (!data) {
      gridEl.innerHTML = '<p class="empty-state" style="padding:var(--spacing-xl)">Loading validation data...</p>';
      dataLoader.load('validation', 'data/validation_summary.json').then(function(d) {
        if (d) renderValidation(d);
      });
      return;
    }
    renderValidation(data);
  }

  function renderValidation(data) {
    if (!gridEl) return;

    var html = '<div class="validation-layout">';
    var summary = data.summary || {};

    // Summary header
    html += '<div class="validation-summary">';
    html += renderValidationStat(summary.archetypes || 0, 'Archetypes');
    html += renderValidationStat(summary.primordials || 0, 'Primordials');
    html += renderValidationStat(
      (summary.entities_mapped || 0) + '/' + (summary.library_entities || 0),
      'Entities Mapped'
    );
    html += renderValidationStat(
      (summary.mapping_rate || 0).toFixed(1) + '%',
      'Mapping Rate'
    );
    html += renderValidationStat(summary.library_segments || 0, 'Segments');

    // Overall verdict badge
    var vClass = verdictClass(data.overall_verdict);
    html += '<div class="validation-verdict ' + vClass + '">';
    html += escapeHtml(data.overall_label || data.overall_verdict || 'Unknown');
    html += '</div>';
    html += '</div>';

    // Tier cards
    var tiers = data.tiers || [];
    if (tiers.length > 0) {
      html += '<div class="tier-cards" id="codex-tier-cards">';
      for (var t = 0; t < tiers.length; t++) {
        html += renderTierCard(tiers[t]);
      }
      html += '</div>';

      // Expanded tier tests (rendered below the card row)
      html += '<div id="codex-tier-tests"></div>';
    }

    // Recommendations
    var recs = data.recommendations || [];
    if (recs.length > 0) {
      html += '<div class="recommendations">';
      html += '<div class="pattern-detail-section-title" style="margin-bottom:8px">Recommendations</div>';
      for (var r = 0; r < recs.length; r++) {
        html += '<div class="recommendation-item">';
        html += '<strong>' + (r + 1) + '.</strong> ' + escapeHtml(recs[r]);
        html += '</div>';
      }
      html += '</div>';
    }

    // Audit Cases
    var cases = data.audit_cases || [];
    if (cases.length > 0) {
      html += '<div class="audit-cases">';
      html += '<div class="pattern-detail-section-title" style="margin-bottom:8px">Audit Cases (' + cases.length + ')</div>';
      for (var c = 0; c < cases.length; c++) {
        html += renderAuditCase(cases[c], c);
      }
      html += '</div>';
    }

    html += '</div>';
    gridEl.innerHTML = html;

    // Wire validation click events
    wireValidationEvents();

    // Render any initially expanded tiers
    refreshExpandedTierTests(data);
  }

  function wireValidationEvents() {
    gridEl.addEventListener('click', function(e) {
      // Tier card toggle
      var tierCard = e.target.closest('.tier-card');
      if (tierCard) {
        var tierId = tierCard.getAttribute('data-tier-id');
        if (tierId) {
          toggleTier(tierId);
        }
        return;
      }

      // Test toggle
      var testHeader = e.target.closest('.tier-test-header');
      if (testHeader) {
        var testKey = testHeader.getAttribute('data-test-key');
        if (testKey) {
          toggleTest(testKey);
        }
        return;
      }

      // Audit case toggle
      var auditHeader = e.target.closest('.audit-case-header');
      if (auditHeader) {
        var auditIdx = auditHeader.getAttribute('data-audit-idx');
        if (auditIdx !== null) {
          toggleAuditCase(parseInt(auditIdx, 10));
        }
        return;
      }
    });
  }

  function renderValidationStat(value, label) {
    return '<div class="validation-stat">' +
      '<div class="validation-stat-value">' + value + '</div>' +
      '<div class="validation-stat-label">' + escapeHtml(label) + '</div>' +
    '</div>';
  }

  function renderTierCard(tier) {
    var borderColor = VERDICT_BORDER[tier.verdict] || VERDICT_BORDER.PENDING;
    var vClass = verdictClass(tier.verdict);
    var tests = tier.tests || [];
    var passCount = 0;
    for (var i = 0; i < tests.length; i++) {
      if (tests[i].pass) passCount++;
    }

    var isExpanded = expandedTiers[tier.id];

    var html = '<div class="tier-card' + (isExpanded ? ' expanded' : '') + '" data-tier-id="' + escapeAttr(tier.id) + '" style="border-top-color:' + borderColor + '">';
    html += '<div class="tier-card-header">';
    html += '<span class="tier-card-name">' + escapeHtml(tier.label || tier.id) + '</span>';
    html += '<span class="validation-verdict ' + vClass + '" style="font-size:0.65rem;padding:1px 6px">' + escapeHtml(tier.verdict || '') + '</span>';
    html += '</div>';
    if (tests.length > 0) {
      html += '<div class="tier-card-score">' + passCount + '/' + tests.length + ' passed</div>';
    } else if (tier.insights && tier.insights.length > 0) {
      html += '<div class="tier-card-score">' + tier.insights.length + ' insights</div>';
    } else {
      html += '<div class="tier-card-score">' + escapeHtml(tier.description || '') + '</div>';
    }
    html += '</div>';

    return html;
  }

  function toggleTier(tierId) {
    expandedTiers[tierId] = !expandedTiers[tierId];

    // Update card expanded class
    var card = gridEl.querySelector('.tier-card[data-tier-id="' + tierId + '"]');
    if (card) {
      card.classList.toggle('expanded', expandedTiers[tierId]);
    }

    var data = dataLoader.get('validation');
    if (data) {
      refreshExpandedTierTests(data);
    }
  }

  function refreshExpandedTierTests(data) {
    var testsEl = document.getElementById('codex-tier-tests');
    if (!testsEl) return;

    var tiers = data.tiers || [];
    var html = '';

    for (var t = 0; t < tiers.length; t++) {
      var tier = tiers[t];
      if (!expandedTiers[tier.id]) continue;

      html += '<div class="tier-tests">';
      var tests = tier.tests || [];
      var insights = tier.insights || [];

      if (tests.length > 0) {
        html += '<div class="pattern-detail-section-title">' + escapeHtml(tier.label || tier.id) + ' Tests</div>';
        for (var i = 0; i < tests.length; i++) {
          html += renderTierTest(tier.id, tests[i], i);
        }
      }

      if (insights.length > 0) {
        html += '<div class="pattern-detail-section-title" style="margin-top:8px">' + escapeHtml(tier.label || tier.id) + ' Insights</div>';
        for (var j = 0; j < insights.length; j++) {
          var insight = insights[j];
          var isConfirmed = insight.indexOf('CONFIRMED') === 0;
          var badgeStyle = isConfirmed
            ? 'background:rgba(16,185,129,0.2);color:#34d399'
            : 'background:rgba(59,130,246,0.2);color:#60a5fa';
          var badgeText = isConfirmed ? 'CONFIRMED' : 'INSIGHT';
          html += '<div class="tier-test" style="padding:6px 0">';
          html += '<span class="badge" style="' + badgeStyle + ';font-size:0.65rem;margin-right:8px">' + badgeText + '</span>';
          html += '<span style="font-size:0.8rem">' + escapeHtml(insight.replace(/^(CONFIRMED|INSIGHT): ?/, '')) + '</span>';
          html += '</div>';
        }
      }

      if (tests.length === 0 && insights.length === 0) {
        html += '<div class="empty-state" style="font-size:0.8rem">No automated tests for this tier.</div>';
      }

      html += '</div>';
    }

    testsEl.innerHTML = html;
  }

  function renderTierTest(tierId, test, idx) {
    var testKey = tierId + ':' + idx;
    var isExpanded = expandedTests[testKey];
    var passBadge = test.pass
      ? '<span class="badge" style="background:rgba(16,185,129,0.2);color:#34d399;font-size:0.65rem">PASS</span>'
      : '<span class="badge" style="background:rgba(239,68,68,0.2);color:#f87171;font-size:0.65rem">FAIL</span>';

    var html = '<div class="tier-test">';
    html += '<div class="tier-test-header" data-test-key="' + escapeAttr(testKey) + '" style="cursor:pointer">';
    html += '<span class="tier-test-name">' + escapeHtml(test.name || '') + '</span>';
    html += passBadge;
    html += '</div>';

    if (isExpanded) {
      html += '<div class="tier-test-detail">';
      if (test.question) {
        html += '<div style="margin-bottom:4px"><strong>Question:</strong> ' + escapeHtml(test.question) + '</div>';
      }
      if (test.criterion) {
        html += '<div style="margin-bottom:4px"><strong>Criterion:</strong> ' + escapeHtml(test.criterion) + '</div>';
      }
      if (test.result) {
        html += '<div style="margin-bottom:4px"><strong>Result:</strong> ' + escapeHtml(test.result) + '</div>';
      }

      // Key metrics table
      var metrics = test.key_metrics;
      if (metrics && typeof metrics === 'object') {
        var keys = Object.keys(metrics);
        if (keys.length > 0) {
          html += '<div class="tier-test-metrics">';
          for (var k = 0; k < keys.length; k++) {
            var val = metrics[keys[k]];
            var displayVal = typeof val === 'number' ? val.toFixed(4) : String(val);
            html += '<div class="tier-test-metric-row">';
            html += '<span>' + escapeHtml(keys[k]) + '</span>';
            html += '<span>' + escapeHtml(displayVal) + '</span>';
            html += '</div>';
          }
          html += '</div>';
        }
      }
      html += '</div>';
    }

    html += '</div>';
    return html;
  }

  function toggleTest(testKey) {
    expandedTests[testKey] = !expandedTests[testKey];

    var data = dataLoader.get('validation');
    if (data) {
      refreshExpandedTierTests(data);
    }
  }

  function renderAuditCase(ac, idx) {
    var isExpanded = expandedAuditCases[idx];

    var html = '<div class="audit-case' + (isExpanded ? ' expanded' : '') + '">';

    // Header
    html += '<div class="audit-case-header" data-audit-idx="' + idx + '">';
    html += '<span class="audit-case-num">#' + (idx + 1) + '</span>';
    if (ac.category) {
      html += '<span class="badge" style="font-size:0.65rem">' + escapeHtml(ac.category) + '</span>';
    }
    html += '<span class="audit-case-claim">' + escapeHtml(ac.claim || '') + '</span>';
    html += '<span class="audit-case-expand">' + (isExpanded ? '\u25BC' : '\u25B6') + '</span>';
    html += '</div>';

    // Body (visible only when expanded)
    html += '<div class="audit-case-body"' + (isExpanded ? '' : ' style="display:none"') + '>';

    // Source + Target pair
    if (ac.source || ac.target) {
      html += '<div class="audit-case-pair">';
      if (ac.source) {
        html += renderAuditArchetype(ac.source, 'Source');
      }
      if (ac.target) {
        html += renderAuditArchetype(ac.target, 'Target');
      }
      html += '</div>';
    }

    // Metrics
    html += '<div class="audit-case-metrics">';
    if (ac.distance_8d != null) {
      html += renderAuditMetric(ac.distance_8d.toFixed(4), 'Distance');
    }
    if (ac.fidelity != null) {
      html += renderAuditMetric(ac.fidelity.toFixed(2), 'Fidelity');
    }
    if (ac.reviewer_judgment) {
      html += renderAuditMetric(ac.reviewer_judgment, 'Judgment');
    }
    html += '</div>';

    // Reviewer notes
    if (ac.reviewer_notes) {
      html += '<div class="audit-case-notes">' + escapeHtml(ac.reviewer_notes) + '</div>';
    }

    html += '</div>'; // body
    html += '</div>'; // audit-case

    return html;
  }

  function renderAuditArchetype(arch, label) {
    var html = '<div class="audit-case-archetype">';
    html += '<div style="font-size:0.65rem;color:#94a3b8;text-transform:uppercase;margin-bottom:2px">' + escapeHtml(label) + '</div>';
    html += '<div class="audit-case-arch-name">' + escapeHtml(arch.name || arch.id || '') + '</div>';
    if (arch.system) {
      html += '<span class="badge" style="font-size:0.6rem">' + escapeHtml(arch.system) + '</span>';
    }
    html += '</div>';
    return html;
  }

  function renderAuditMetric(value, label) {
    return '<div class="audit-case-metric">' +
      '<div class="audit-case-metric-value">' + escapeHtml(String(value)) + '</div>' +
      '<div class="audit-case-metric-label">' + escapeHtml(label) + '</div>' +
    '</div>';
  }

  function toggleAuditCase(idx) {
    expandedAuditCases[idx] = !expandedAuditCases[idx];

    var data = dataLoader.get('validation');
    if (!data) return;

    var casesEl = gridEl.querySelector('.audit-cases');
    if (!casesEl) return;

    var cases = data.audit_cases || [];
    var html = '<div class="pattern-detail-section-title" style="margin-bottom:8px">Audit Cases (' + cases.length + ')</div>';
    for (var c = 0; c < cases.length; c++) {
      html += renderAuditCase(cases[c], c);
    }
    casesEl.innerHTML = html;
  }

  // --- Utilities ---

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function escapeAttr(str) {
    return (str || '').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  // --- Register View ---

  tabRouter.register('codex', {
    init: init,
    activate: activate,
    deactivate: deactivate,
    onRoute: onRoute
  });

  window.MiroGlyph.viewCodex = {
    switchSubTab: switchSubTab
  };
})();
