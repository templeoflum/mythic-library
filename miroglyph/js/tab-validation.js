// Mythic System Explorer — Validation Tab
// Test verdicts, structural recommendations, audit cases

(function() {
  var dataLoader = window.MiroGlyph.dataLoader;
  var tabRouter = window.MiroGlyph.tabRouter;

  var AXES = [
    'order-chaos', 'creation-destruction', 'light-shadow', 'active-receptive',
    'individual-collective', 'ascent-descent', 'stasis-transformation', 'voluntary-fated'
  ];

  var VERDICT_CLASS = {
    'PASS': 'badge-pass',
    'PARTIAL': 'badge-partial',
    'FAIL': 'badge-fail',
    'MIXED': 'badge-partial',
    'PENDING': 'badge-pending',
    'ALTERNATIVES_FOUND': 'badge-partial'
  };

  var data = null;

  function init(container) {
    container.innerHTML = '<div class="validation-container"><div class="loading">Loading validation data...</div></div>';

    dataLoader.load('validation', 'data/validation_summary.json').then(function(d) {
      if (!d) { container.innerHTML = '<p class="empty-state">Failed to load validation data.</p>'; return; }
      data = d;
      render(container);
    });
  }

  function render(container) {
    var html = '<div class="validation-container">';

    // Summary header
    var s = data.summary || {};
    html += '<div class="val-summary">';
    html += '<div class="val-summary-stats">';
    html += '<div class="val-stat"><span class="val-stat-num">' + (s.archetypes || 0) + '</span><span class="val-stat-label">Archetypes</span></div>';
    html += '<div class="val-stat"><span class="val-stat-num">' + (s.primordials || 0) + '</span><span class="val-stat-label">Primordials</span></div>';
    html += '<div class="val-stat"><span class="val-stat-num">' + (s.entities_mapped || 0) + '/' + (s.library_entities || 0) + '</span><span class="val-stat-label">Entities Mapped</span></div>';
    html += '<div class="val-stat"><span class="val-stat-num">' + (s.mapping_rate || 0).toFixed(1) + '%</span><span class="val-stat-label">Mapping Rate</span></div>';
    html += '<div class="val-stat"><span class="val-stat-num">' + (s.library_segments || 0) + '</span><span class="val-stat-label">Text Segments</span></div>';
    html += '</div>';

    // Overall verdict
    var verdictClass = VERDICT_CLASS[data.overall_verdict] || 'badge-partial';
    html += '<div class="val-overall">';
    html += '<span class="badge ' + verdictClass + ' badge-large">' + escapeHtml(data.overall_verdict || 'UNKNOWN') + '</span>';
    if (data.overall_label) {
      html += '<span class="val-overall-label">' + escapeHtml(data.overall_label) + '</span>';
    }
    html += '</div></div>';

    // Tiers
    var tiers = data.tiers || [];
    for (var t = 0; t < tiers.length; t++) {
      html += renderTier(tiers[t]);
    }

    // Recommendations
    var recs = data.recommendations || [];
    if (recs.length > 0) {
      html += '<div class="val-section">';
      html += '<h2 class="val-section-title">Structural Recommendations</h2>';
      html += '<div class="val-recommendations">';
      for (var i = 0; i < recs.length; i++) {
        html += '<div class="val-rec">';
        html += '<span class="val-rec-num">' + (i + 1) + '</span>';
        html += '<span class="val-rec-text">' + escapeHtml(recs[i]) + '</span>';
        html += '</div>';
      }
      html += '</div></div>';
    }

    // Audit Cases
    var cases = data.audit_cases || [];
    if (cases.length > 0) {
      html += '<div class="val-section">';
      html += '<h2 class="val-section-title">Human Audit Cases <span class="val-count">' + cases.length + '</span></h2>';
      html += '<div id="val-audit-list" class="val-audit-list">';
      for (var i = 0; i < cases.length; i++) {
        html += renderAuditCase(cases[i], i);
      }
      html += '</div></div>';
    }

    html += '</div>';
    container.innerHTML = html;

    // Set up expand/collapse
    container.addEventListener('click', function(e) {
      var toggle = e.target.closest('.val-test-toggle');
      if (toggle) {
        var detail = toggle.nextElementSibling;
        if (detail) {
          detail.hidden = !detail.hidden;
          toggle.classList.toggle('expanded');
        }
      }
      var auditToggle = e.target.closest('.val-audit-header');
      if (auditToggle) {
        var body = auditToggle.nextElementSibling;
        if (body) {
          body.hidden = !body.hidden;
          auditToggle.classList.toggle('expanded');
        }
      }
    });
  }

  function renderTier(tier) {
    var verdictClass = VERDICT_CLASS[tier.verdict] || 'badge-partial';
    var html = '<div class="val-tier">';
    html += '<div class="val-tier-header">';
    html += '<span class="val-tier-id">Tier ' + escapeHtml(tier.id) + '</span>';
    html += '<span class="val-tier-label">' + escapeHtml(tier.label) + '</span>';
    html += '<span class="badge ' + verdictClass + '">' + escapeHtml(tier.verdict) + '</span>';
    html += '</div>';

    var tests = tier.tests || [];
    if (tests.length > 0) {
      html += '<div class="val-tests">';
      for (var i = 0; i < tests.length; i++) {
        html += renderTest(tests[i]);
      }
      html += '</div>';
    } else {
      html += '<div class="val-tier-empty">No automated tests for this tier.</div>';
    }

    html += '</div>';
    return html;
  }

  function renderTest(test) {
    var passClass = test.pass ? 'badge-pass' : 'badge-fail';
    var passText = test.pass ? 'PASS' : 'FAIL';

    var html = '<div class="val-test">';
    html += '<div class="val-test-toggle">';
    html += '<span class="val-test-expand">\u25B6</span>';
    html += '<span class="val-test-name">' + escapeHtml(test.name) + '</span>';
    html += '<span class="badge ' + passClass + '">' + passText + '</span>';
    html += '</div>';

    html += '<div class="val-test-detail" hidden>';
    if (test.question) {
      html += '<div class="val-test-question">' + escapeHtml(test.question) + '</div>';
    }
    if (test.criterion) {
      html += '<div class="val-row"><span class="val-key">Criterion:</span> ' + escapeHtml(test.criterion) + '</div>';
    }
    if (test.result) {
      html += '<div class="val-row"><span class="val-key">Result:</span> ' + escapeHtml(test.result) + '</div>';
    }

    // Key metrics table
    var metrics = test.key_metrics;
    if (metrics && typeof metrics === 'object') {
      html += '<div class="val-metrics">';
      html += '<table class="val-metrics-table"><tbody>';
      var keys = Object.keys(metrics);
      for (var i = 0; i < keys.length; i++) {
        var val = metrics[keys[i]];
        var displayVal = typeof val === 'number' ? val.toFixed(4) : String(val);
        html += '<tr><td class="val-metric-key">' + escapeHtml(keys[i]) + '</td>';
        html += '<td class="val-metric-val">' + escapeHtml(displayVal) + '</td></tr>';
      }
      html += '</tbody></table></div>';
    }

    html += '</div></div>';
    return html;
  }

  function renderAuditCase(ac, idx) {
    var html = '<div class="val-audit">';
    html += '<div class="val-audit-header">';
    html += '<span class="val-audit-num">#' + (idx + 1) + '</span>';
    html += '<span class="val-audit-cat badge">' + escapeHtml(ac.category || '') + '</span>';
    html += '<span class="val-audit-expand">\u25B6</span>';
    html += '</div>';

    html += '<div class="val-audit-body" hidden>';
    if (ac.claim) {
      html += '<div class="val-audit-claim">' + escapeHtml(ac.claim) + '</div>';
    }

    // Source and Target side by side
    if (ac.source || ac.target) {
      html += '<div class="val-audit-pair">';
      if (ac.source) {
        html += renderAuditArchetype(ac.source, 'Source');
      }
      if (ac.target) {
        html += renderAuditArchetype(ac.target, 'Target');
      }
      html += '</div>';
    }

    // Metrics
    html += '<div class="val-audit-metrics">';
    if (ac.distance_8d != null) {
      html += '<div class="val-row"><span class="val-key">8D Distance:</span> ' + ac.distance_8d.toFixed(4) + '</div>';
    }
    if (ac.fidelity != null) {
      html += '<div class="val-row"><span class="val-key">Fidelity:</span> ' + ac.fidelity.toFixed(2) + '</div>';
    }
    if (ac.reviewer_judgment) {
      html += '<div class="val-row"><span class="val-key">Judgment:</span> ' + escapeHtml(ac.reviewer_judgment) + '</div>';
    }
    if (ac.reviewer_notes) {
      html += '<div class="val-audit-notes">' + escapeHtml(ac.reviewer_notes) + '</div>';
    }
    html += '</div></div></div>';

    return html;
  }

  function renderAuditArchetype(a, label) {
    var html = '<div class="val-audit-arch">';
    html += '<div class="val-audit-arch-label">' + escapeHtml(label) + '</div>';
    html += '<h4>' + escapeHtml(a.name || a.id || '') + '</h4>';
    if (a.system) html += '<span class="badge badge-system">' + escapeHtml(a.system) + '</span>';
    if (a.description) html += '<p class="val-audit-desc">' + escapeHtml(a.description) + '</p>';

    // Coordinates
    if (a.coordinates && typeof a.coordinates === 'object') {
      html += '<div class="coord-bars compact">';
      for (var i = 0; i < AXES.length; i++) {
        var val = a.coordinates[AXES[i]];
        if (val == null) continue;
        var pct = Math.round(val * 100);
        html += '<div class="coord-row">';
        html += '<div class="coord-track"><div class="coord-fill" style="width:' + pct + '%"></div></div>';
        html += '</div>';
      }
      html += '</div>';
    }

    html += '</div>';
    return html;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function activate() {}
  function deactivate() {}

  tabRouter.register('validation', { init: init, activate: activate, deactivate: deactivate });
})();
