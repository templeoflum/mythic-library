// Mythic System Explorer — Global Search
// Omni-search across nodes, archetypes, entities, and patterns

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var input = null;
  var dropdown = null;
  var debounceTimer = null;
  var isOpen = false;

  function init() {
    input = document.getElementById('global-search');
    dropdown = document.getElementById('search-dropdown');
    if (!input || !dropdown) return;

    input.addEventListener('input', function() {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function() {
        doSearch(input.value.trim());
      }, 200);
    });

    input.addEventListener('focus', function() {
      if (input.value.trim().length >= 2) {
        doSearch(input.value.trim());
      }
    });

    // Close on click outside
    document.addEventListener('click', function(e) {
      if (!e.target.closest('.global-search-wrap')) {
        close();
      }
    });

    // Close on Escape
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        close();
        input.blur();
      }
    });
  }

  function doSearch(query) {
    if (query.length < 2) {
      close();
      return;
    }

    var q = query.toLowerCase();
    var results = { nodes: [], archetypes: [], entities: [], patterns: [] };
    var nodes = window.MiroGlyph.nodes;
    var dl = window.MiroGlyph.dataLoader;

    // Search nodes
    if (nodes && nodes.NODES) {
      nodes.NODES.forEach(function(n) {
        if (n.id.toLowerCase().indexOf(q) >= 0 ||
            n.title.toLowerCase().indexOf(q) >= 0 ||
            n.role.toLowerCase().indexOf(q) >= 0 ||
            (n.tone && n.tone.join(' ').toLowerCase().indexOf(q) >= 0)) {
          results.nodes.push(n);
        }
      });
      // Also check Nontion
      if (nodes.NONTION && ('nontion'.indexOf(q) >= 0 || 'center'.indexOf(q) >= 0)) {
        results.nodes.push({ id: '\u2205', title: 'Nontion', role: nodes.NONTION.role });
      }
    }

    // Search archetypes
    var archData = dl.get('archetypes');
    if (archData && archData.archetypes) {
      var count = 0;
      for (var i = 0; i < archData.archetypes.length && count < 5; i++) {
        var a = archData.archetypes[i];
        if (a.name.toLowerCase().indexOf(q) >= 0 ||
            (a.description && a.description.toLowerCase().indexOf(q) >= 0) ||
            a.id.toLowerCase().indexOf(q) >= 0) {
          results.archetypes.push(a);
          count++;
        }
      }
    }

    // Search entities
    var entData = dl.get('entities');
    if (entData && entData.entities) {
      var eCount = 0;
      for (var j = 0; j < entData.entities.length && eCount < 5; j++) {
        var e = entData.entities[j];
        if (e.name.toLowerCase().indexOf(q) >= 0 ||
            (e.type && e.type.toLowerCase().indexOf(q) >= 0) ||
            (e.primary_tradition && e.primary_tradition.toLowerCase().indexOf(q) >= 0)) {
          results.entities.push(e);
          eCount++;
        }
      }
    }

    // Search patterns
    var patData = dl.get('patterns');
    if (patData && patData.patterns) {
      patData.patterns.forEach(function(p) {
        if (p.name.toLowerCase().indexOf(q) >= 0 ||
            (p.description && p.description.toLowerCase().indexOf(q) >= 0)) {
          results.patterns.push(p);
        }
      });
    }

    render(results, query);
  }

  function render(results, query) {
    var total = results.nodes.length + results.archetypes.length +
                results.entities.length + results.patterns.length;

    if (total === 0) {
      dropdown.innerHTML = '<div class="search-empty">No results for "' + escapeHtml(query) + '"</div>';
      open();
      return;
    }

    var html = '';

    if (results.nodes.length > 0) {
      html += '<div class="search-group">';
      html += '<div class="search-group-label">Nodes</div>';
      results.nodes.slice(0, 5).forEach(function(n) {
        html += '<div class="search-result" data-action="node" data-id="' + escapeAttr(n.id) + '">';
        html += '<span class="search-result-icon" style="color:' + getNodeColor(n) + '">\u25CF</span>';
        html += '<span class="search-result-name">' + escapeHtml(n.id) + ' \u2014 ' + escapeHtml(n.title) + '</span>';
        html += '<span class="search-result-type">node</span>';
        html += '</div>';
      });
      html += '</div>';
    }

    if (results.archetypes.length > 0) {
      html += '<div class="search-group">';
      html += '<div class="search-group-label">Archetypes</div>';
      results.archetypes.forEach(function(a) {
        html += '<div class="search-result" data-action="archetype" data-id="' + escapeAttr(a.id) + '">';
        html += '<span class="search-result-icon" style="color: var(--color-acp)">\u25C6</span>';
        html += '<span class="search-result-name">' + escapeHtml(a.name);
        if (a.system) html += ' <span class="badge badge-system">' + escapeHtml(a.system) + '</span>';
        html += '</span>';
        html += '<span class="search-result-type">archetype</span>';
        html += '</div>';
      });
      html += '</div>';
    }

    if (results.entities.length > 0) {
      html += '<div class="search-group">';
      html += '<div class="search-group-label">Entities</div>';
      results.entities.forEach(function(e) {
        html += '<div class="search-result" data-action="entity" data-id="' + escapeAttr(e.name) + '">';
        html += '<span class="search-result-icon" style="color: var(--color-library)">\u2726</span>';
        html += '<span class="search-result-name">' + escapeHtml(e.name);
        if (e.primary_tradition) html += ' <span class="badge badge-system">' + escapeHtml(e.primary_tradition) + '</span>';
        html += '</span>';
        html += '<span class="search-result-type">' + escapeHtml(e.type || 'entity') + '</span>';
        html += '</div>';
      });
      html += '</div>';
    }

    if (results.patterns.length > 0) {
      html += '<div class="search-group">';
      html += '<div class="search-group-label">Patterns</div>';
      results.patterns.slice(0, 5).forEach(function(p) {
        html += '<div class="search-result" data-action="pattern" data-id="' + escapeAttr(p.name) + '">';
        html += '<span class="search-result-icon">\u223F</span>';
        html += '<span class="search-result-name">' + escapeHtml(formatPatternName(p.name));
        html += ' <span class="badge badge-arc-' + p.arc + '">' + p.arc + '</span>';
        html += '</span>';
        html += '<span class="search-result-type">pattern</span>';
        html += '</div>';
      });
      html += '</div>';
    }

    dropdown.innerHTML = html;
    open();

    // Attach click handlers
    dropdown.querySelectorAll('.search-result').forEach(function(el) {
      el.addEventListener('click', function() {
        var action = el.dataset.action;
        var id = el.dataset.id;
        var nav = window.MiroGlyph.nav;

        if (action === 'node') nav.toNode(id);
        else if (action === 'archetype') nav.toArchetype(id);
        else if (action === 'entity') nav.toEntity(id);
        else if (action === 'pattern') nav.toPattern(id);

        close();
        input.value = '';
        input.blur();
      });
    });
  }

  function open() {
    dropdown.hidden = false;
    isOpen = true;
  }

  function close() {
    if (dropdown) dropdown.hidden = true;
    isOpen = false;
  }

  function getNodeColor(node) {
    if (node.id === '\u2205') return '#f59e0b';
    if (node.arc) return node.arc.color;
    var nodesModule = window.MiroGlyph.nodes;
    var n = nodesModule.getNode(node.id);
    return n ? n.arc.color : '#94a3b8';
  }

  function formatPatternName(name) {
    return name.replace(/_/g, ' ').replace(/\b\w/g, function(c) { return c.toUpperCase(); });
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
  }

  function escapeAttr(str) {
    return (str || '').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  window.MiroGlyph.globalSearch = { init: init };
})();
