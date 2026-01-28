// Mythic System Explorer — Archetypes Tab
// Browse and search 539 archetypes with 8D coordinates, primordials, relationships

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
  var archetypeMap = {};
  var selectedId = null;

  function init(container) {
    container.innerHTML =
      '<div class="tab-3col">' +
        '<div class="tab-sidebar">' +
          '<div class="sidebar-controls">' +
            '<input type="text" id="arch-search" class="search-input" placeholder="Search archetypes...">' +
            '<select id="arch-filter-system" class="filter-select"><option value="">All Systems</option></select>' +
            '<select id="arch-filter-primordial" class="filter-select"><option value="">All Primordials</option></select>' +
          '</div>' +
          '<div id="arch-count" class="result-count"></div>' +
          '<div id="arch-list" class="scroll-list"></div>' +
        '</div>' +
        '<div class="tab-main">' +
          '<div id="arch-detail" class="detail-panel"><p class="empty-state">Select an archetype to view details.</p></div>' +
        '</div>' +
        '<div class="tab-sidebar-right">' +
          '<div id="arch-relationships" class="detail-panel"><p class="empty-state">Relationships will appear here.</p></div>' +
        '</div>' +
      '</div>';

    dataLoader.load('archetypes', 'data/archetypes_catalog.json').then(function(data) {
      if (!data) { container.querySelector('#arch-list').innerHTML = '<p class="empty-state">Failed to load archetype data.</p>'; return; }
      catalog = data;
      archetypeMap = {};
      for (var i = 0; i < catalog.archetypes.length; i++) {
        archetypeMap[catalog.archetypes[i].id] = catalog.archetypes[i];
      }
      populateFilters();
      renderList(catalog.archetypes);
      setupEvents();
    });
  }

  function populateFilters() {
    var systemSelect = document.getElementById('arch-filter-system');
    var primSelect = document.getElementById('arch-filter-primordial');

    if (catalog.systems) {
      for (var i = 0; i < catalog.systems.length; i++) {
        var s = catalog.systems[i];
        var opt = document.createElement('option');
        opt.value = s.code;
        opt.textContent = s.name + ' (' + s.count + ')';
        systemSelect.appendChild(opt);
      }
    }

    if (catalog.primordials) {
      for (var i = 0; i < catalog.primordials.length; i++) {
        var p = catalog.primordials[i];
        var opt = document.createElement('option');
        opt.value = p.id;
        opt.textContent = p.name;
        primSelect.appendChild(opt);
      }
    }
  }

  function setupEvents() {
    var searchInput = document.getElementById('arch-search');
    var systemSelect = document.getElementById('arch-filter-system');
    var primSelect = document.getElementById('arch-filter-primordial');

    var debounceTimer = null;
    searchInput.addEventListener('input', function() {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function() { applyFilters(); }, 200);
    });
    systemSelect.addEventListener('change', function() { applyFilters(); });
    primSelect.addEventListener('change', function() { applyFilters(); });
  }

  function applyFilters() {
    var query = (document.getElementById('arch-search').value || '').toLowerCase();
    var system = document.getElementById('arch-filter-system').value;
    var primordial = document.getElementById('arch-filter-primordial').value;

    var filtered = catalog.archetypes.filter(function(a) {
      if (system && a.system !== system) return false;
      if (primordial) {
        var hasPrim = false;
        for (var i = 0; i < (a.primordials || []).length; i++) {
          if (a.primordials[i].id === primordial) { hasPrim = true; break; }
        }
        if (!hasPrim) return false;
      }
      if (query) {
        var searchable = (a.name + ' ' + a.id + ' ' + a.description + ' ' + (a.domains || []).join(' ')).toLowerCase();
        if (searchable.indexOf(query) === -1) return false;
      }
      return true;
    });

    renderList(filtered);
  }

  function renderList(archetypes) {
    var container = document.getElementById('arch-list');
    var countEl = document.getElementById('arch-count');
    countEl.textContent = archetypes.length + ' of ' + catalog.archetypes.length + ' archetypes';

    if (archetypes.length === 0) {
      container.innerHTML = '<p class="empty-state">No archetypes match filters.</p>';
      return;
    }

    var frag = document.createDocumentFragment();
    for (var i = 0; i < archetypes.length; i++) {
      var a = archetypes[i];
      var item = document.createElement('div');
      item.className = 'list-item arch-item' + (a.id === selectedId ? ' selected' : '');
      item.dataset.id = a.id;

      var topPrim = '';
      if (a.primordials && a.primordials.length > 0) {
        var prims = a.primordials.slice(0, 2);
        for (var j = 0; j < prims.length; j++) {
          var name = (prims[j].id || '').replace('primordial:', '');
          topPrim += '<span class="tag">' + escapeHtml(name) + '</span>';
        }
      }

      var sparkline = '';
      if (a.coordinates && a.coordinates.length === 8) {
        sparkline = '<div class="sparkline">';
        for (var j = 0; j < 8; j++) {
          var pct = Math.round(a.coordinates[j] * 100);
          sparkline += '<div class="spark-bar" style="height:' + pct + '%"></div>';
        }
        sparkline += '</div>';
      }

      item.innerHTML =
        '<div class="arch-item-header">' +
          '<span class="arch-item-name">' + escapeHtml(a.name) + '</span>' +
          (a.system ? '<span class="badge badge-system">' + escapeHtml(a.system) + '</span>' : '') +
        '</div>' +
        '<div class="arch-item-meta">' + topPrim + sparkline + '</div>';

      frag.appendChild(item);
    }

    container.innerHTML = '';
    container.appendChild(frag);

    container.onclick = function(e) {
      var item = e.target.closest('.arch-item');
      if (item) selectArchetype(item.dataset.id);
    };
  }

  function selectArchetype(id) {
    selectedId = id;
    var arch = archetypeMap[id];
    if (!arch) return;

    // Update list selection
    var items = document.querySelectorAll('.arch-item');
    for (var i = 0; i < items.length; i++) {
      items[i].classList.toggle('selected', items[i].dataset.id === id);
    }

    renderDetail(arch);
    renderRelationships(arch);
  }

  function renderDetail(arch) {
    var container = document.getElementById('arch-detail');
    var html = '';

    html += '<h2 class="detail-title">' + escapeHtml(arch.name) + '</h2>';
    html += '<div class="detail-id">' + escapeHtml(arch.id) + '</div>';
    if (arch.system) {
      html += '<span class="badge badge-system">' + escapeHtml(arch.system) + '</span>';
    }
    if (arch.description) {
      html += '<p class="detail-desc">' + escapeHtml(arch.description) + '</p>';
    }

    // Domains
    if (arch.domains && arch.domains.length > 0) {
      html += '<div class="detail-section"><h4>Domains</h4><div class="tag-list">';
      for (var i = 0; i < arch.domains.length; i++) {
        html += '<span class="tag">' + escapeHtml(arch.domains[i]) + '</span>';
      }
      html += '</div></div>';
    }

    // 8D Coordinates
    if (arch.coordinates && arch.coordinates.length === 8) {
      html += '<div class="detail-section"><h4>8D Spectral Coordinates</h4>';
      html += '<div class="coord-bars">';
      for (var i = 0; i < 8; i++) {
        var val = arch.coordinates[i];
        var pct = Math.round(val * 100);
        html += '<div class="coord-row">';
        html += '<span class="coord-label">' + (AXIS_SHORT[AXES[i]] || AXES[i]) + '</span>';
        html += '<div class="coord-track"><div class="coord-fill" style="width:' + pct + '%"></div>';
        html += '<div class="coord-marker" style="left:' + pct + '%"></div></div>';
        html += '<span class="coord-value">' + val.toFixed(2) + '</span>';
        html += '</div>';
      }
      html += '</div></div>';
    }

    // Primordials
    if (arch.primordials && arch.primordials.length > 0) {
      html += '<div class="detail-section"><h4>Primordial Instantiations</h4>';
      html += '<div class="primordial-list">';
      for (var i = 0; i < arch.primordials.length; i++) {
        var p = arch.primordials[i];
        var name = (p.id || '').replace('primordial:', '');
        var pct = Math.round((p.weight || 0) * 100);
        html += '<div class="primordial-row">';
        html += '<span class="primordial-name">' + escapeHtml(name) + '</span>';
        html += '<div class="coord-track"><div class="coord-fill primordial-fill" style="width:' + pct + '%"></div></div>';
        html += '<span class="coord-value">' + (p.weight || 0).toFixed(2) + '</span>';
        html += '</div>';
      }
      html += '</div></div>';
    }

    // Nearest Miroglyph Nodes
    if (arch.nearest_nodes && arch.nearest_nodes.length > 0) {
      html += '<div class="detail-section"><h4>Nearest Miroglyph Nodes</h4>';
      html += '<div class="node-list">';
      for (var i = 0; i < Math.min(5, arch.nearest_nodes.length); i++) {
        var n = arch.nearest_nodes[i];
        var affPct = Math.round((n.affinity || 0) * 100);
        html += '<div class="node-row">';
        html += '<span class="node-badge">' + escapeHtml(n.node_id) + '</span>';
        html += '<div class="coord-track"><div class="coord-fill node-fill" style="width:' + affPct + '%"></div></div>';
        html += '<span class="coord-value">' + (n.affinity || 0).toFixed(3) + '</span>';
        html += '</div>';
      }
      html += '</div></div>';
    }

    container.innerHTML = html;
  }

  function renderRelationships(arch) {
    var container = document.getElementById('arch-relationships');
    if (!arch.relationships || arch.relationships.length === 0) {
      container.innerHTML = '<p class="empty-state">No relationships.</p>';
      return;
    }

    var html = '<h3>Relationships</h3>';

    // Group by type
    var byType = {};
    for (var i = 0; i < arch.relationships.length; i++) {
      var r = arch.relationships[i];
      var type = r.type || 'OTHER';
      if (!byType[type]) byType[type] = [];
      byType[type].push(r);
    }

    var types = Object.keys(byType);
    for (var t = 0; t < types.length; t++) {
      var type = types[t];
      var rels = byType[type];
      html += '<div class="rel-group">';
      html += '<h4 class="rel-type">' + escapeHtml(type.replace(/_/g, ' ')) + '</h4>';
      for (var i = 0; i < rels.length; i++) {
        var r = rels[i];
        var targetArch = archetypeMap[r.target];
        var targetName = targetArch ? targetArch.name : r.target;
        html += '<div class="rel-item" data-target="' + escapeHtml(r.target) + '">';
        html += '<span class="rel-target">' + escapeHtml(targetName) + '</span>';
        if (r.fidelity) {
          html += '<span class="rel-fidelity">' + r.fidelity.toFixed(2) + '</span>';
        }
        html += '</div>';
      }
      html += '</div>';
    }

    container.innerHTML = html;

    // Click handler for relationship targets
    container.onclick = function(e) {
      var relItem = e.target.closest('.rel-item');
      if (relItem && relItem.dataset.target) {
        var targetId = relItem.dataset.target;
        if (archetypeMap[targetId]) {
          selectArchetype(targetId);
          // Scroll the list to the target
          var listItem = document.querySelector('.arch-item[data-id="' + targetId + '"]');
          if (listItem) listItem.scrollIntoView({ block: 'center', behavior: 'smooth' });
        }
      }
    };
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function activate() {}
  function deactivate() {}

  tabRouter.register('archetypes', { init: init, activate: activate, deactivate: deactivate });
})();
