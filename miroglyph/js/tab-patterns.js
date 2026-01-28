// Mythic System Explorer — Patterns Tab
// 18 named patterns with motifs, traditions, arc assignments

(function() {
  var dataLoader = window.MiroGlyph.dataLoader;
  var tabRouter = window.MiroGlyph.tabRouter;

  var ARC_COLORS = {
    'D': '#8b5cf6',
    'R': '#3b82f6',
    'E': '#10b981'
  };

  var ARC_NAMES = {
    'D': 'Descent',
    'R': 'Resonance',
    'E': 'Emergence'
  };

  var catalog = null;
  var selectedPattern = null;

  function init(container) {
    container.innerHTML =
      '<div class="tab-3col">' +
        '<div class="tab-sidebar">' +
          '<div id="pat-list" class="scroll-list"></div>' +
        '</div>' +
        '<div class="tab-main">' +
          '<div id="pat-detail" class="detail-panel"><p class="empty-state">Select a pattern to view details.</p></div>' +
        '</div>' +
        '<div class="tab-sidebar-right">' +
          '<div id="pat-sidebar" class="detail-panel"><p class="empty-state">Tradition and entity data will appear here.</p></div>' +
        '</div>' +
      '</div>';

    dataLoader.load('patterns', 'data/patterns_catalog.json').then(function(data) {
      if (!data) { container.querySelector('#pat-list').innerHTML = '<p class="empty-state">Failed to load pattern data.</p>'; return; }
      catalog = data;
      renderPatternList();
    });
  }

  function renderPatternList() {
    var container = document.getElementById('pat-list');
    var html = '';

    // Group patterns by arc
    var arcAssign = catalog.arc_assignments || {};
    var arcs = ['D', 'R', 'E'];

    for (var a = 0; a < arcs.length; a++) {
      var arcCode = arcs[a];
      var patNames = arcAssign[arcCode] || [];
      if (patNames.length === 0) continue;

      var color = ARC_COLORS[arcCode] || '#94a3b8';
      html += '<div class="pat-arc-group">';
      html += '<div class="pat-arc-header" style="border-left: 3px solid ' + color + '">';
      html += '<span class="pat-arc-name">' + (ARC_NAMES[arcCode] || arcCode) + '</span>';
      html += '<span class="badge badge-arc-' + arcCode + '">' + arcCode + '</span>';
      html += '<span class="pat-arc-count">' + patNames.length + '</span>';
      html += '</div>';

      for (var i = 0; i < patNames.length; i++) {
        var patName = patNames[i];
        var pattern = findPattern(patName);
        if (!pattern) continue;

        html += '<div class="list-item pat-item" data-name="' + escapeHtml(patName) + '">';
        html += '<div class="pat-item-header">';
        html += '<span class="pat-item-name">' + escapeHtml(formatPatternName(patName)) + '</span>';
        html += '</div>';
        html += '<div class="pat-item-meta">';
        html += '<span class="pat-attest">' + (pattern.attestation_count || 0) + ' attestations</span>';
        html += '<span class="pat-trad-count">' + (pattern.tradition_count || 0) + ' traditions</span>';
        html += '</div>';
        html += '</div>';
      }

      html += '</div>';
    }

    container.innerHTML = html;

    container.onclick = function(e) {
      var item = e.target.closest('.pat-item');
      if (item) selectPattern(item.dataset.name);
    };
  }

  function selectPattern(name) {
    selectedPattern = name;
    var pattern = findPattern(name);
    if (!pattern) return;

    // Update list selection
    var items = document.querySelectorAll('.pat-item');
    for (var i = 0; i < items.length; i++) {
      items[i].classList.toggle('selected', items[i].dataset.name === name);
    }

    renderDetail(pattern);
    renderSidebar(pattern);
  }

  function renderDetail(pattern) {
    var container = document.getElementById('pat-detail');
    var html = '';

    var arcColor = ARC_COLORS[pattern.arc] || '#94a3b8';

    html += '<h2 class="detail-title">' + escapeHtml(formatPatternName(pattern.name)) + '</h2>';
    html += '<div class="pat-detail-badges">';
    html += '<span class="badge badge-arc-' + (pattern.arc || 'D') + '">' + (ARC_NAMES[pattern.arc] || pattern.arc || '?') + ' (' + (pattern.arc || '?') + ')</span>';
    if (pattern.confidence) {
      html += '<span class="badge">Confidence: ' + pattern.confidence.toFixed(3) + '</span>';
    }
    html += '</div>';

    if (pattern.description) {
      html += '<p class="detail-desc">' + escapeHtml(pattern.description) + '</p>';
    }

    // Stats
    html += '<div class="pat-stats">';
    html += '<div class="pat-stat"><span class="pat-stat-num">' + (pattern.attestation_count || 0) + '</span><span class="pat-stat-label">Attestations</span></div>';
    html += '<div class="pat-stat"><span class="pat-stat-num">' + (pattern.tradition_count || 0) + '</span><span class="pat-stat-label">Traditions</span></div>';
    html += '<div class="pat-stat"><span class="pat-stat-num">' + (pattern.motif_codes || []).length + '</span><span class="pat-stat-label">Motifs</span></div>';
    html += '<div class="pat-stat"><span class="pat-stat-num">' + (pattern.related_entities || []).length + '</span><span class="pat-stat-label">Entities</span></div>';
    html += '</div>';

    // Motif codes
    if (pattern.motif_codes && pattern.motif_codes.length > 0) {
      html += '<div class="detail-section"><h4>Motif Codes</h4>';
      html += '<div class="tag-list">';
      var motifs = catalog.motifs || {};
      for (var i = 0; i < pattern.motif_codes.length; i++) {
        var code = pattern.motif_codes[i];
        var motif = motifs[code];
        var label = motif ? motif.label : code;
        html += '<span class="tag motif-tag" title="' + escapeHtml(code + ': ' + label) + '">';
        html += '<strong>' + escapeHtml(code) + '</strong> ' + escapeHtml(label);
        html += '</span>';
      }
      html += '</div></div>';
    }

    // Traditions list
    if (pattern.traditions && pattern.traditions.length > 0) {
      html += '<div class="detail-section"><h4>Traditions (' + pattern.traditions.length + ')</h4>';
      html += '<div class="tag-list">';
      for (var i = 0; i < pattern.traditions.length; i++) {
        html += '<span class="tag tradition-tag">' + escapeHtml(pattern.traditions[i]) + '</span>';
      }
      html += '</div></div>';
    }

    container.innerHTML = html;
  }

  function renderSidebar(pattern) {
    var container = document.getElementById('pat-sidebar');
    var html = '';

    // Related Entities
    var entities = pattern.related_entities || [];
    if (entities.length > 0) {
      html += '<h3>Related Entities <span class="val-count">' + entities.length + '</span></h3>';
      html += '<div class="pat-entity-list">';
      for (var i = 0; i < entities.length; i++) {
        html += '<span class="pat-entity">' + escapeHtml(entities[i]) + '</span>';
      }
      html += '</div>';
    }

    // Tradition breakdown (bar chart)
    if (pattern.traditions && pattern.traditions.length > 0) {
      html += '<h3 style="margin-top: 1.5rem;">Tradition Coverage</h3>';
      html += '<div class="pat-tradition-chart">';
      var maxLen = 26; // max possible traditions
      for (var i = 0; i < pattern.traditions.length; i++) {
        var pct = 100; // Each tradition is present/absent, so show filled
        html += '<div class="pat-tradition-bar">';
        html += '<span class="pat-tradition-name">' + escapeHtml(pattern.traditions[i]) + '</span>';
        html += '<div class="coord-track"><div class="coord-fill tradition-fill" style="width:100%"></div></div>';
        html += '</div>';
      }
      html += '</div>';
      html += '<div class="pat-tradition-summary">' + pattern.traditions.length + ' of ~' + maxLen + ' known traditions</div>';
    }

    container.innerHTML = html || '<p class="empty-state">No additional data.</p>';
  }

  function findPattern(name) {
    if (!catalog || !catalog.patterns) return null;
    for (var i = 0; i < catalog.patterns.length; i++) {
      if (catalog.patterns[i].name === name) return catalog.patterns[i];
    }
    return null;
  }

  function formatPatternName(name) {
    if (!name) return '';
    return name.replace(/_/g, ' ').replace(/\b\w/g, function(c) { return c.toUpperCase(); });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function activate() {}
  function deactivate() {}

  tabRouter.register('patterns', { init: init, activate: activate, deactivate: deactivate });
})();
