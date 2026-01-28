// Mythic System Explorer — Entity Tracing Tab
// Entity → Archetype → Node chain visualization

(function() {
  var dataLoader = window.MiroGlyph.dataLoader;
  var tabRouter = window.MiroGlyph.tabRouter;

  var AXES = [
    'order-chaos', 'creation-destruction', 'light-shadow', 'active-receptive',
    'individual-collective', 'ascent-descent', 'stasis-transformation', 'voluntary-fated'
  ];
  var AXIS_SHORT = {
    'order-chaos': 'Ord\u2013Chaos',
    'creation-destruction': 'Cre\u2013Dest',
    'light-shadow': 'Light\u2013Shadow',
    'active-receptive': 'Act\u2013Recep',
    'individual-collective': 'Ind\u2013Coll',
    'ascent-descent': 'Asc\u2013Desc',
    'stasis-transformation': 'Sta\u2013Trans',
    'voluntary-fated': 'Vol\u2013Fated'
  };

  var catalog = null;
  var archetypeCatalog = null;
  var archetypeMap = {};

  function init(container) {
    container.innerHTML =
      '<div class="tab-3col">' +
        '<div class="tab-sidebar">' +
          '<input type="text" id="trace-search" class="search-input" placeholder="Search entities...">' +
          '<div class="trace-filters">' +
            '<select id="trace-filter-type" class="filter-select"><option value="">All Types</option></select>' +
            '<select id="trace-filter-tradition" class="filter-select"><option value="">All Traditions</option></select>' +
            '<select id="trace-filter-mapped" class="filter-select">' +
              '<option value="">All</option>' +
              '<option value="mapped">Mapped Only</option>' +
              '<option value="unmapped">Unmapped Only</option>' +
            '</select>' +
          '</div>' +
          '<div id="trace-count" class="result-count"></div>' +
          '<div id="trace-entity-list" class="scroll-list"></div>' +
        '</div>' +
        '<div class="tab-main trace-main">' +
          '<div id="trace-chain" class="trace-chain"><p class="empty-state">Select an entity to trace its path through all three systems.</p></div>' +
        '</div>' +
        '<div class="tab-sidebar-right">' +
          '<div id="trace-coords" class="detail-panel"><p class="empty-state">Coordinate comparison will appear here.</p></div>' +
        '</div>' +
      '</div>';

    // Load both catalogs
    Promise.all([
      dataLoader.load('entities', 'data/entities_catalog.json'),
      dataLoader.load('archetypes', 'data/archetypes_catalog.json')
    ]).then(function(results) {
      catalog = results[0];
      archetypeCatalog = results[1];

      if (!catalog) { container.querySelector('#trace-entity-list').innerHTML = '<p class="empty-state">Failed to load entity data.</p>'; return; }

      // Build archetype map
      if (archetypeCatalog) {
        for (var i = 0; i < archetypeCatalog.archetypes.length; i++) {
          var a = archetypeCatalog.archetypes[i];
          archetypeMap[a.id] = a;
        }
      }

      populateFilters();
      renderEntityList(catalog.entities);
      setupEvents();
    });
  }

  function populateFilters() {
    var typeSelect = document.getElementById('trace-filter-type');
    var tradSelect = document.getElementById('trace-filter-tradition');

    var types = {};
    var traditions = {};
    for (var i = 0; i < catalog.entities.length; i++) {
      var e = catalog.entities[i];
      if (e.type) types[e.type] = true;
      if (e.primary_tradition) traditions[e.primary_tradition] = true;
    }

    Object.keys(types).sort().forEach(function(t) {
      var opt = document.createElement('option');
      opt.value = t;
      opt.textContent = t;
      typeSelect.appendChild(opt);
    });

    Object.keys(traditions).sort().forEach(function(t) {
      var opt = document.createElement('option');
      opt.value = t;
      opt.textContent = t;
      tradSelect.appendChild(opt);
    });
  }

  function setupEvents() {
    var searchInput = document.getElementById('trace-search');
    var typeSelect = document.getElementById('trace-filter-type');
    var tradSelect = document.getElementById('trace-filter-tradition');
    var mappedSelect = document.getElementById('trace-filter-mapped');

    var debounceTimer = null;
    searchInput.addEventListener('input', function() {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function() { applyFilters(); }, 200);
    });
    typeSelect.addEventListener('change', function() { applyFilters(); });
    tradSelect.addEventListener('change', function() { applyFilters(); });
    mappedSelect.addEventListener('change', function() { applyFilters(); });
  }

  function applyFilters() {
    var query = (document.getElementById('trace-search').value || '').toLowerCase();
    var type = document.getElementById('trace-filter-type').value;
    var tradition = document.getElementById('trace-filter-tradition').value;
    var mapped = document.getElementById('trace-filter-mapped').value;

    var filtered = catalog.entities.filter(function(e) {
      if (type && e.type !== type) return false;
      if (tradition && e.primary_tradition !== tradition) return false;
      if (mapped === 'mapped' && !e.mapping) return false;
      if (mapped === 'unmapped' && e.mapping) return false;
      if (query && e.name.toLowerCase().indexOf(query) === -1) return false;
      return true;
    });

    renderEntityList(filtered);
  }

  function renderEntityList(entities) {
    var container = document.getElementById('trace-entity-list');
    var countEl = document.getElementById('trace-count');
    countEl.textContent = entities.length + ' of ' + catalog.entities.length + ' entities';

    if (entities.length === 0) {
      container.innerHTML = '<p class="empty-state">No entities match filters.</p>';
      return;
    }

    var frag = document.createDocumentFragment();
    for (var i = 0; i < entities.length; i++) {
      var e = entities[i];
      var item = document.createElement('div');
      item.className = 'list-item trace-entity-item';
      item.dataset.name = e.name;

      item.innerHTML =
        '<div class="trace-item-header">' +
          '<span class="trace-item-name">' + escapeHtml(e.name) + '</span>' +
          (e.mapping ? '<span class="badge badge-pass" style="font-size:0.6rem">mapped</span>' : '<span class="badge badge-fail" style="font-size:0.6rem">unmapped</span>') +
        '</div>' +
        '<div class="trace-item-meta">' +
          (e.type ? '<span class="tag">' + escapeHtml(e.type) + '</span>' : '') +
          (e.primary_tradition ? '<span class="tag">' + escapeHtml(e.primary_tradition) + '</span>' : '') +
          '<span class="trace-mentions">' + (e.total_mentions || 0) + ' mentions</span>' +
        '</div>';

      frag.appendChild(item);
    }

    container.innerHTML = '';
    container.appendChild(frag);

    container.onclick = function(ev) {
      var item = ev.target.closest('.trace-entity-item');
      if (item) selectEntity(item.dataset.name);
    };
  }

  function selectEntity(name) {
    var entity = null;
    for (var i = 0; i < catalog.entities.length; i++) {
      if (catalog.entities[i].name === name) { entity = catalog.entities[i]; break; }
    }
    if (!entity) return;

    // Highlight in list
    var items = document.querySelectorAll('.trace-entity-item');
    for (var i = 0; i < items.length; i++) {
      items[i].classList.toggle('selected', items[i].dataset.name === name);
    }

    renderChain(entity);
    renderCoordComparison(entity);
  }

  function renderChain(entity) {
    var container = document.getElementById('trace-chain');
    var html = '<div class="chain">';

    // Card 1: Entity (Library)
    html += '<div class="chain-card chain-entity">';
    html += '<div class="chain-label">Library Entity</div>';
    html += '<h3>' + escapeHtml(entity.name) + '</h3>';
    html += '<div class="chain-details">';
    if (entity.type) html += '<div><span class="chain-key">Type:</span> ' + escapeHtml(entity.type) + '</div>';
    if (entity.primary_tradition) html += '<div><span class="chain-key">Tradition:</span> ' + escapeHtml(entity.primary_tradition) + '</div>';
    html += '<div><span class="chain-key">Mentions:</span> ' + (entity.total_mentions || 0) + '</div>';
    html += '<div><span class="chain-key">Texts:</span> ' + (entity.text_count || 0) + '</div>';
    if (entity.tradition_count) html += '<div><span class="chain-key">Traditions:</span> ' + entity.tradition_count + '</div>';
    html += '</div></div>';

    // Arrow
    html += '<div class="chain-arrow">' + (entity.mapping ? '\u2192' : '\u2717') + '</div>';

    // Card 2: Archetype (ACP)
    if (entity.mapping) {
      var archId = entity.mapping.archetype_id;
      var arch = archetypeMap[archId];
      html += '<div class="chain-card chain-archetype">';
      html += '<div class="chain-label">ACP Archetype</div>';
      html += '<h3>' + escapeHtml(arch ? arch.name : archId) + '</h3>';
      html += '<div class="chain-details">';
      html += '<div><span class="chain-key">ID:</span> <code>' + escapeHtml(archId) + '</code></div>';
      html += '<div><span class="chain-key">Confidence:</span> ' + (entity.mapping.confidence || 0).toFixed(2) + '</div>';
      html += '<div><span class="chain-key">Method:</span> ' + escapeHtml(entity.mapping.method || '') + '</div>';
      if (arch && arch.primordials && arch.primordials.length > 0) {
        var primNames = [];
        for (var i = 0; i < Math.min(3, arch.primordials.length); i++) {
          primNames.push(arch.primordials[i].id.replace('primordial:', ''));
        }
        html += '<div><span class="chain-key">Primordials:</span> ' + escapeHtml(primNames.join(', ')) + '</div>';
      }
      html += '</div></div>';

      // Arrow
      html += '<div class="chain-arrow">' + (entity.nearest_node ? '\u2192' : '\u2717') + '</div>';

      // Card 3: Node (Miroglyph)
      if (entity.nearest_node) {
        var nodeId = entity.nearest_node.node_id;
        var nodeData = window.MiroGlyph.nodes ? window.MiroGlyph.nodes.getNode(nodeId) : null;
        html += '<div class="chain-card chain-node">';
        html += '<div class="chain-label">Miroglyph Node</div>';
        html += '<h3>' + escapeHtml(nodeId) + '</h3>';
        html += '<div class="chain-details">';
        html += '<div><span class="chain-key">Affinity:</span> ' + (entity.nearest_node.affinity || 0).toFixed(3) + '</div>';
        if (nodeData) {
          html += '<div><span class="chain-key">Title:</span> ' + escapeHtml(nodeData.title || '') + '</div>';
          html += '<div><span class="chain-key">Role:</span> ' + escapeHtml(nodeData.role || '') + '</div>';
          if (nodeData.arc) {
            html += '<div><span class="chain-key">Arc:</span> ' + escapeHtml(nodeData.arc.primary + '/' + nodeData.arc.secondary) + '</div>';
          }
          if (nodeData.condition) {
            html += '<div><span class="chain-key">Condition:</span> ' + escapeHtml(nodeData.condition.primary + '/' + nodeData.condition.secondary) + '</div>';
          }
        }
        html += '</div></div>';
      } else {
        html += '<div class="chain-card chain-missing">';
        html += '<div class="chain-label">Miroglyph Node</div>';
        html += '<p class="empty-state">No node assignment — coordinates unavailable.</p>';
        html += '</div>';
      }
    } else {
      html += '<div class="chain-card chain-missing">';
      html += '<div class="chain-label">ACP Archetype</div>';
      html += '<p class="empty-state">No ACP mapping found for this entity.</p>';
      html += '</div>';

      html += '<div class="chain-arrow">\u00b7\u00b7\u00b7</div>';

      html += '<div class="chain-card chain-missing">';
      html += '<div class="chain-label">Miroglyph Node</div>';
      html += '<p class="empty-state">Cannot trace without ACP mapping.</p>';
      html += '</div>';
    }

    html += '</div>';

    // Top nodes list
    if (entity.top_nodes && entity.top_nodes.length > 1) {
      html += '<div class="trace-top-nodes">';
      html += '<h4>All Node Affinities</h4>';
      html += '<div class="top-nodes-grid">';
      for (var i = 0; i < entity.top_nodes.length; i++) {
        var tn = entity.top_nodes[i];
        var affPct = Math.round((tn.affinity || 0) * 100);
        var isNearest = entity.nearest_node && tn.node_id === entity.nearest_node.node_id;
        html += '<div class="top-node-item' + (isNearest ? ' nearest' : '') + '">';
        html += '<span class="node-badge">' + escapeHtml(tn.node_id) + '</span>';
        html += '<div class="coord-track"><div class="coord-fill node-fill" style="width:' + affPct + '%"></div></div>';
        html += '<span class="coord-value">' + (tn.affinity || 0).toFixed(3) + '</span>';
        html += '</div>';
      }
      html += '</div></div>';
    }

    container.innerHTML = html;
  }

  function renderCoordComparison(entity) {
    var container = document.getElementById('trace-coords');

    if (!entity.coordinates || entity.coordinates.length !== 8) {
      container.innerHTML = '<p class="empty-state">No coordinate data available for this entity.</p>';
      return;
    }

    // Get node centroid if available
    var nodeCoords = null;
    if (entity.nearest_node && window.MiroGlyph.enrichment && window.MiroGlyph.enrichment.isLoaded()) {
      var profile = window.MiroGlyph.enrichment.getNodeProfile(entity.nearest_node.node_id);
      if (profile && profile.mean_coordinates) {
        nodeCoords = profile.mean_coordinates;
      }
    }

    var html = '<h3>8D Coordinates</h3>';

    if (nodeCoords) {
      html += '<div class="coord-legend">';
      html += '<span class="coord-legend-item"><span class="coord-swatch entity-swatch"></span>Entity</span>';
      html += '<span class="coord-legend-item"><span class="coord-swatch node-swatch"></span>Node ' + escapeHtml(entity.nearest_node.node_id) + '</span>';
      html += '</div>';
    }

    html += '<div class="coord-comparison">';
    for (var i = 0; i < 8; i++) {
      var entVal = entity.coordinates[i];
      var entPct = Math.round(entVal * 100);
      html += '<div class="comp-row">';
      html += '<span class="comp-label">' + (AXIS_SHORT[AXES[i]] || AXES[i]) + '</span>';
      html += '<div class="comp-tracks">';
      html += '<div class="coord-track"><div class="coord-fill entity-fill" style="width:' + entPct + '%"></div>';
      html += '<div class="coord-marker" style="left:' + entPct + '%"></div></div>';
      if (nodeCoords) {
        var nodeVal = nodeCoords[i] || 0.5;
        var nodePct = Math.round(nodeVal * 100);
        html += '<div class="coord-track"><div class="coord-fill node-comp-fill" style="width:' + nodePct + '%"></div>';
        html += '<div class="coord-marker" style="left:' + nodePct + '%"></div></div>';
      }
      html += '</div>';
      html += '<span class="comp-values">' + entVal.toFixed(2);
      if (nodeCoords) html += '<br>' + (nodeCoords[i] || 0.5).toFixed(2);
      html += '</span>';
      html += '</div>';
    }
    html += '</div>';

    container.innerHTML = html;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function activate() {}
  function deactivate() {}

  tabRouter.register('tracing', { init: init, activate: activate, deactivate: deactivate });
})();
