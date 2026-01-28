// Mythic System Explorer — Codex View
// Card grid with sub-tabs (archetypes/entities), filtering, lazy loading, and detail views

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
    mapped: ''
  };
  var detailItem = null;  // null = grid view, otherwise { kind, id }
  var filteredData = [];
  var renderedCount = 0;
  var observer = null;
  var debounceTimer = null;
  var boundDetailClick = null;
  var boundSubTabClick = null;

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
    var html = '<div style="display:flex;align-items:center;gap:var(--spacing-sm);flex-wrap:wrap;padding:var(--spacing-sm) var(--spacing-lg)">';

    // Sub-tab toggles
    html += '<div class="codex-sub-tabs">';
    html += '<button class="codex-sub-tab' + (subTab === 'archetypes' ? ' active' : '') + '" data-sub="archetypes">Archetypes</button>';
    html += '<button class="codex-sub-tab' + (subTab === 'entities' ? ' active' : '') + '" data-sub="entities">Entities</button>';
    html += '</div>';

    // Search
    html += '<input type="text" class="search-input" id="codex-search" placeholder="Search..." value="' +
      escapeAttr(filters.search) + '" style="flex:1;min-width:160px">';

    // Dropdowns depend on sub-tab
    if (subTab === 'archetypes') {
      html += buildArchetypeFilters();
    } else {
      html += buildEntityFilters();
    }

    // Count
    html += '<span id="codex-count" class="result-count" style="margin-left:auto;white-space:nowrap"></span>';

    html += '</div>';
    filterBarEl.innerHTML = html;
    countEl = filterBarEl.querySelector('#codex-count');
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

    detailItem = null;
    buildFilterBar();
    wireFilterEvents();
    renderGrid();
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
      var totalLabel = subTab === 'archetypes' ? 'archetypes' : 'entities';
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
    }
    return filterEntities();
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

  function getTotalCount() {
    if (subTab === 'archetypes') {
      var archData = dataLoader.get('archetypes');
      return archData && archData.archetypes ? archData.archetypes.length : 0;
    }
    var entData = dataLoader.get('entities');
    return entData && entData.entities ? entData.entities.length : 0;
  }

  // --- Batch Rendering ---

  function renderBatch(cardGrid) {
    var end = Math.min(renderedCount + BATCH_SIZE, filteredData.length);
    var frag = document.createDocumentFragment();

    for (var i = renderedCount; i < end; i++) {
      var wrapper = document.createElement('div');
      if (subTab === 'archetypes') {
        wrapper.innerHTML = cardRenderer.renderArchetypeCard(filteredData[i]);
      } else {
        wrapper.innerHTML = cardRenderer.renderEntityCard(filteredData[i]);
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
