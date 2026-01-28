// Mythic System Explorer — Node Drawer Component
// Side drawer with 4 inner tabs: Profile, Archetypes, Entities, Patterns

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var AXES = [
    'order-chaos', 'creation-destruction', 'light-shadow', 'active-receptive',
    'individual-collective', 'ascent-descent', 'stasis-transformation', 'voluntary-fated'
  ];
  var AXIS_SHORT = [
    'Ord-Chaos', 'Cre-Dest', 'Light-Shadow', 'Act-Recep',
    'Ind-Coll', 'Asc-Desc', 'Sta-Trans', 'Vol-Fated'
  ];
  var ARC_CODES = ['D', 'R', 'E'];

  var currentNodeId = null;
  var currentTab = 'profile';

  // --- Open / Close ---

  function open(nodeId) {
    var nodes = window.MiroGlyph.nodes;
    var node = nodes.getNode(nodeId);
    if (!node) return;

    currentNodeId = nodeId;
    currentTab = 'profile';

    renderHeader(nodeId, node);
    setActiveTab('profile');
    renderTabContent('profile');

    var drawer = document.getElementById('node-drawer');
    if (drawer) {
      drawer.classList.remove('node-drawer-closed');
    }
  }

  function close() {
    var drawer = document.getElementById('node-drawer');
    if (drawer) {
      drawer.classList.add('node-drawer-closed');
    }
    currentNodeId = null;

    var canvas = window.MiroGlyph.canvas;
    if (canvas && canvas.clearSelection) {
      canvas.clearSelection();
    }
  }

  function isOpen() {
    return currentNodeId !== null;
  }

  function getCurrentNodeId() {
    return currentNodeId;
  }

  // --- Header ---

  function renderHeader(nodeId, node) {
    var idEl = document.getElementById('drawer-node-id');
    var titleEl = document.getElementById('drawer-node-title');
    var metaEl = document.getElementById('drawer-node-meta');
    var tonesEl = document.getElementById('drawer-node-tones');

    if (nodeId === '\u2205') {
      if (idEl) {
        idEl.style.color = node.color;
        idEl.textContent = '\u2205 Nontion';
      }
      if (titleEl) titleEl.textContent = 'Center Point';
      if (metaEl) metaEl.textContent = 'Reset and settling state';
      if (tonesEl) tonesEl.innerHTML = '';
      return;
    }

    if (idEl) {
      idEl.style.color = node.arc.color;
      idEl.textContent = nodeId;
    }
    if (titleEl) titleEl.textContent = node.title;
    if (metaEl) {
      metaEl.textContent = node.arc.primary + '/' + node.arc.secondary +
        ' \u2014 ' + node.condition.primary + '/' + node.condition.secondary;
    }
    if (tonesEl) {
      var html = '';
      for (var i = 0; i < node.tone.length; i++) {
        html += '<span class="drawer-tone-tag">' + escapeHtml(node.tone[i]) + '</span>';
      }
      tonesEl.innerHTML = html;
    }
  }

  // --- Tab Switching ---

  function setActiveTab(tabName) {
    currentTab = tabName;
    var tabs = document.querySelectorAll('.drawer-tab');
    for (var i = 0; i < tabs.length; i++) {
      var isActive = tabs[i].getAttribute('data-drawer-tab') === tabName;
      if (isActive) {
        tabs[i].classList.add('drawer-tab-active');
      } else {
        tabs[i].classList.remove('drawer-tab-active');
      }
    }
  }

  function renderTabContent(tabName) {
    if (!currentNodeId) return;

    var body = document.getElementById('drawer-body');
    if (!body) return;

    if (tabName === 'profile') {
      renderProfileTab(body);
    } else if (tabName === 'archetypes') {
      renderArchetypesTab(body);
    } else if (tabName === 'entities') {
      renderEntitiesTab(body);
    } else if (tabName === 'patterns') {
      renderPatternsTab(body);
    }
  }

  // --- Profile Tab ---

  function renderProfileTab(body) {
    var nodeId = currentNodeId;

    if (nodeId === '\u2205') {
      body.innerHTML =
        '<div class="drawer-section">' +
          '<p class="hint">Nontion is the center point of the topology \u2014 ' +
          'a reset and settling state outside the coordinate space. ' +
          'It is traversable but holds a different ontological status than the 18 nodes.</p>' +
        '</div>';
      return;
    }

    var enrichment = window.MiroGlyph.enrichment;
    var dataLoader = window.MiroGlyph.dataLoader;
    var profile = enrichment && enrichment.isLoaded() ? enrichment.getNodeProfile(nodeId) : null;
    var entitiesByNode = dataLoader ? dataLoader.getIndex('entitiesByNode') : {};
    var nodeEntities = entitiesByNode[nodeId] || [];

    var html = '';

    // 8D Coordinate bars
    if (profile && profile.mean_coordinates) {
      html += '<div class="drawer-section">';
      html += '<div class="drawer-section-title">8D Spectral Profile</div>';
      html += '<div class="coord-bars">';
      var coords = profile.mean_coordinates;
      for (var i = 0; i < AXES.length; i++) {
        var val = coords[i] || 0.5;
        var pct = Math.round(val * 100);
        html += '<div class="coord-row">';
        html += '<span class="coord-label">' + AXIS_SHORT[i] + '</span>';
        html += '<div class="coord-track"><div class="coord-fill" style="width:' + pct + '%"></div>';
        html += '<div class="coord-marker" style="left:' + pct + '%"></div></div>';
        html += '<span class="coord-value">' + val.toFixed(2) + '</span>';
        html += '</div>';
      }
      html += '</div></div>';
    }

    // Stats grid
    var entityCount = nodeEntities.length;
    var profileEntities = profile ? (profile.n_entities || 0) : 0;

    html += '<div class="drawer-section">';
    html += '<div class="drawer-section-title">Stats</div>';
    html += '<div class="drawer-stats">';
    html += '<div class="drawer-stat">';
    html += '<div class="drawer-stat-value">' + entityCount + '</div>';
    html += '<div class="drawer-stat-label">Entities</div>';
    html += '</div>';
    html += '<div class="drawer-stat">';
    html += '<div class="drawer-stat-value">' + profileEntities + '</div>';
    html += '<div class="drawer-stat-label">Profile N</div>';
    html += '</div>';
    html += '</div></div>';

    // Dominant primordials
    if (profile && profile.dominant_primordials && profile.dominant_primordials.length > 0) {
      html += '<div class="drawer-section">';
      html += '<div class="drawer-section-title">Dominant Primordials</div>';
      var prims = profile.dominant_primordials;
      for (var i = 0; i < prims.length; i++) {
        var p = prims[i];
        var name = (p.primordial_id || '').replace('primordial:', '');
        var weight = p.mean_weight || 0;
        var wPct = Math.round(weight * 100);
        html += '<div class="coord-row">';
        html += '<span class="coord-label">' + escapeHtml(name) + '</span>';
        html += '<div class="coord-track"><div class="coord-fill primordial-fill" style="width:' + wPct + '%"></div></div>';
        html += '<span class="coord-value">' + weight.toFixed(2) + '</span>';
        html += '</div>';
      }
      html += '</div>';
    }

    // Condition Siblings
    html += renderConditionSiblings(nodeId);

    body.innerHTML = html;
    setupSiblingClickHandlers(body);
  }

  function renderConditionSiblings(nodeId) {
    var nodes = window.MiroGlyph.nodes;
    var node = nodes.getNode(nodeId);
    if (!node || nodeId === '\u2205') return '';

    var condNum = node.condition.code;
    var arcCode = node.arc.code;
    var siblings = [];

    for (var i = 0; i < ARC_CODES.length; i++) {
      var code = ARC_CODES[i];
      if (code === arcCode) continue;
      var sibId = code + condNum;
      var sib = nodes.getNode(sibId);
      if (sib) {
        siblings.push(sib);
      }
    }

    if (siblings.length === 0) return '';

    var html = '<div class="drawer-section">';
    html += '<div class="drawer-section-title">Condition Siblings</div>';
    html += '<div class="drawer-sibling-nodes">';

    for (var i = 0; i < siblings.length; i++) {
      var sib = siblings[i];
      html += '<div class="drawer-sibling-card" data-node-id="' + escapeHtml(sib.id) + '">';
      html += '<div class="drawer-sibling-id" style="color:' + sib.arc.color + '">' + escapeHtml(sib.id) + '</div>';
      html += '<div class="drawer-sibling-title">' + escapeHtml(sib.title) + '</div>';
      html += '</div>';
    }

    html += '</div></div>';
    return html;
  }

  function setupSiblingClickHandlers(body) {
    var siblingCards = body.querySelectorAll('.drawer-sibling-card');
    for (var i = 0; i < siblingCards.length; i++) {
      siblingCards[i].addEventListener('click', function() {
        var targetId = this.getAttribute('data-node-id');
        if (targetId) {
          window.MiroGlyph.nav.toNode(targetId);
        }
      });
    }
  }

  // --- Archetypes Tab ---

  function renderArchetypesTab(body) {
    var nodeId = currentNodeId;
    var enrichment = window.MiroGlyph.enrichment;

    if (!enrichment || !enrichment.isLoaded()) {
      body.innerHTML = '<p class="empty-state">Enrichment data not loaded.</p>';
      return;
    }

    var archetypes = enrichment.getNodeArchetypes(nodeId, 20);

    if (archetypes.length === 0) {
      body.innerHTML = '<p class="empty-state">No archetype affinities found for ' + escapeHtml(nodeId) + '.</p>';
      return;
    }

    var html = '<div class="drawer-section">';
    html += '<div class="drawer-section-title">Top Archetypes (' + archetypes.length + ')</div>';

    for (var i = 0; i < archetypes.length; i++) {
      var arch = archetypes[i];
      var name = arch.name || arch.archetype_id || '';
      var system = arch.system || '';
      var affinity = arch.affinity || 0;
      var desc = arch.description || '';
      if (desc.length > 80) {
        desc = desc.substring(0, 80) + '...';
      }

      html += '<div class="drawer-arch-card" data-archetype-id="' + escapeHtml(arch.archetype_id || arch.id || '') + '">';
      html += '<div class="drawer-arch-card-header">';
      html += '<span class="drawer-arch-card-name">' + escapeHtml(name) + '</span>';
      if (system) {
        html += '<span class="badge badge-system">' + escapeHtml(system) + '</span>';
      }
      html += '</div>';
      html += '<div class="drawer-arch-card-affinity">' + affinity.toFixed(3) + '</div>';

      if (desc) {
        html += '<div class="drawer-arch-card-desc">' + escapeHtml(desc) + '</div>';
      }

      // Primordial tags
      var prims = arch.primordials || [];
      if (prims.length > 0) {
        html += '<div class="drawer-arch-card-prims">';
        for (var j = 0; j < Math.min(3, prims.length); j++) {
          var primName = (prims[j].id || '').replace('primordial:', '');
          html += '<span class="primordial-tag">' + escapeHtml(primName) + '</span>';
        }
        html += '</div>';
      }

      html += '</div>';
    }

    html += '</div>';
    body.innerHTML = html;

    // Click handlers
    var cards = body.querySelectorAll('.drawer-arch-card');
    for (var i = 0; i < cards.length; i++) {
      cards[i].addEventListener('click', function() {
        var archId = this.getAttribute('data-archetype-id');
        if (archId) {
          window.MiroGlyph.nav.toArchetype(archId);
        }
      });
    }
  }

  // --- Entities Tab ---

  function renderEntitiesTab(body) {
    var nodeId = currentNodeId;
    var dataLoader = window.MiroGlyph.dataLoader;

    if (!dataLoader) {
      body.innerHTML = '<p class="empty-state">Data loader not available.</p>';
      return;
    }

    var entitiesByNode = dataLoader.getIndex('entitiesByNode');
    var entities = entitiesByNode[nodeId] || [];

    if (entities.length === 0) {
      body.innerHTML = '<p class="empty-state">No entities mapped to ' + escapeHtml(nodeId) + '.</p>';
      return;
    }

    var html = '<div class="drawer-section">';
    html += '<div class="drawer-section-title">Entities (' + entities.length + ')</div>';

    for (var i = 0; i < entities.length; i++) {
      var e = entities[i];
      var affinity = 0;
      if (e.nearest_node && typeof e.nearest_node === 'object') {
        affinity = e.nearest_node.affinity || 0;
      }

      html += '<div class="drawer-entity-row" data-entity-name="' + escapeHtml(e.name) + '">';
      html += '<span class="drawer-entity-name">' + escapeHtml(e.name) + '</span>';
      if (e.type) {
        html += '<span class="badge badge-system">' + escapeHtml(e.type) + '</span>';
      }
      if (e.primary_tradition) {
        html += '<span class="badge">' + escapeHtml(e.primary_tradition) + '</span>';
      }
      if (affinity > 0) {
        html += '<span class="drawer-entity-meta">' + affinity.toFixed(3) + '</span>';
      }
      html += '</div>';
    }

    html += '</div>';
    body.innerHTML = html;

    // Click handlers
    var rows = body.querySelectorAll('.drawer-entity-row');
    for (var i = 0; i < rows.length; i++) {
      rows[i].addEventListener('click', function() {
        var name = this.getAttribute('data-entity-name');
        if (name) {
          window.MiroGlyph.nav.toEntity(name);
        }
      });
    }
  }

  // --- Patterns Tab ---

  function renderPatternsTab(body) {
    var nodeId = currentNodeId;
    var nodes = window.MiroGlyph.nodes;
    var dataLoader = window.MiroGlyph.dataLoader;

    if (!dataLoader) {
      body.innerHTML = '<p class="empty-state">Data loader not available.</p>';
      return;
    }

    var node = nodes.getNode(nodeId);
    if (!node || nodeId === '\u2205') {
      body.innerHTML = '<p class="empty-state">Nontion has no arc-specific patterns.</p>';
      return;
    }

    var arcCode = node.arc.code;
    var arcColor = node.arc.color;
    var patternsByArc = dataLoader.getIndex('patternsByArc');
    var patterns = patternsByArc[arcCode] || [];

    if (patterns.length === 0) {
      body.innerHTML = '<p class="empty-state">No patterns found for the ' +
        escapeHtml(node.arc.primary) + ' arc.</p>';
      return;
    }

    var html = '<div class="drawer-section">';
    html += '<div class="drawer-section-title">' + escapeHtml(node.arc.primary) +
      ' Arc Patterns (' + patterns.length + ')</div>';

    for (var i = 0; i < patterns.length; i++) {
      var p = patterns[i];
      var attestation = p.attestation_count || p.attestations || 0;
      var confidence = p.confidence || 0;

      html += '<div class="drawer-pattern-card" data-pattern-name="' + escapeHtml(p.name) +
        '" style="border-left-color:' + arcColor + '">';
      html += '<div class="drawer-pattern-name">' + escapeHtml(p.name) + '</div>';
      html += '<div class="drawer-pattern-meta">';
      html += attestation + ' attestations \u00b7 ' + confidence.toFixed(2) + ' confidence';
      html += '</div>';
      html += '</div>';
    }

    html += '</div>';
    body.innerHTML = html;

    // Click handlers
    var cards = body.querySelectorAll('.drawer-pattern-card');
    for (var i = 0; i < cards.length; i++) {
      cards[i].addEventListener('click', function() {
        var name = this.getAttribute('data-pattern-name');
        if (name) {
          window.MiroGlyph.nav.toPattern(name);
        }
      });
    }
  }

  // --- Event Setup ---

  function setupTabEvents() {
    var tabs = document.querySelectorAll('.drawer-tab');
    for (var i = 0; i < tabs.length; i++) {
      tabs[i].addEventListener('click', function() {
        var tabName = this.getAttribute('data-drawer-tab');
        if (tabName && tabName !== currentTab) {
          setActiveTab(tabName);
          renderTabContent(tabName);
        }
      });
    }

    var closeBtn = document.getElementById('drawer-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function() {
        close();
      });
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

  // Initialize tab event handlers once DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupTabEvents);
  } else {
    setupTabEvents();
  }

  window.MiroGlyph.nodeDrawer = {
    open: open,
    close: close,
    isOpen: isOpen,
    getCurrentNodeId: getCurrentNodeId
  };
})();
