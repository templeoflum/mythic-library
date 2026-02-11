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

    var html = '';

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
    body.innerHTML = '<p class="empty-state">Any archetype can be placed in any node. ' +
      'Browse archetypes in the Codex.</p>';
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
