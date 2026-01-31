// Mythic System Explorer — Chronicle View
// Dual sub-view: Patterns (mini-map + pattern grid) and Validation (tiers + audit)

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var dataLoader = window.MiroGlyph.dataLoader;
  var nav = window.MiroGlyph.nav;
  var tabRouter = window.MiroGlyph.tabRouter;
  var miniMap = window.MiroGlyph.miniMap;
  var cardRenderer = window.MiroGlyph.cardRenderer;

  // --- State ---
  var currentSubView = 'patterns'; // 'patterns' or 'validation'
  var selectedPatternName = null;
  var arcFilter = null;              // null, 'D', 'R', or 'E'
  var container = null;
  var expandedTiers = {};            // tier id -> boolean
  var expandedTests = {};            // "tierId:testIdx" -> boolean
  var expandedAuditCases = {};       // index -> boolean

  // --- Arc Metadata ---
  var ARC_COLORS = { D: '#8b5cf6', R: '#3b82f6', E: '#10b981' };
  var ARC_NAMES = { D: 'Descent', R: 'Resonance', E: 'Emergence' };

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

  // =========================================================================
  // Init
  // =========================================================================

  function init(el) {
    container = el;
    buildLayout();
    wireEvents();
  }

  function buildLayout() {
    var html = '';

    // Filter bar
    html += '<div class="chronicle-layout">';
    html += '<div class="chronicle-filter-bar">';

    // Sub-tab toggles
    html += '<div class="chronicle-sub-tabs">';
    html += '<button class="chronicle-sub-tab active" data-subtab="patterns">Patterns</button>';
    html += '<button class="chronicle-sub-tab" data-subtab="validation">Validation</button>';
    html += '</div>';

    // Arc filter buttons (patterns sub-view only)
    html += '<div class="patterns-arc-filters" id="chronicle-arc-filters">';
    html += '<button class="btn btn-small arc-filter-btn" data-arc="D" style="border-color:' + ARC_COLORS.D + ';color:' + ARC_COLORS.D + '">D</button>';
    html += '<button class="btn btn-small arc-filter-btn" data-arc="R" style="border-color:' + ARC_COLORS.R + ';color:' + ARC_COLORS.R + '">R</button>';
    html += '<button class="btn btn-small arc-filter-btn" data-arc="E" style="border-color:' + ARC_COLORS.E + ';color:' + ARC_COLORS.E + '">E</button>';
    html += '</div>';

    html += '</div>'; // filter-bar

    // Patterns sub-view
    html += '<div class="patterns-layout" id="chronicle-patterns">';
    html += '<div class="patterns-map-sidebar">';
    html += '<div class="patterns-map-container" id="chronicle-minimap"></div>';
    html += '</div>';
    html += '<div class="patterns-content" id="chronicle-patterns-content">';
    html += '<div id="chronicle-pattern-detail"></div>';
    html += '<div class="pattern-grid" id="chronicle-pattern-grid"></div>';
    html += '</div>';
    html += '</div>';

    // Validation sub-view
    html += '<div class="validation-layout" id="chronicle-validation" style="display:none">';
    html += '</div>';

    html += '</div>'; // chronicle-layout

    container.innerHTML = html;

    // Render mini-map
    var mapContainer = document.getElementById('chronicle-minimap');
    if (mapContainer && miniMap) {
      miniMap.render(mapContainer);
    }

    // Load and render data
    renderPatternsSubView();
    renderValidationSubView();
  }

  // =========================================================================
  // Event Wiring (delegation)
  // =========================================================================

  function wireEvents() {
    if (!container) return;

    container.addEventListener('click', function(e) {
      // Sub-tab toggle
      var subTab = e.target.closest('.chronicle-sub-tab');
      if (subTab) {
        switchSubView(subTab.getAttribute('data-subtab'));
        return;
      }

      // Arc filter
      var arcBtn = e.target.closest('.arc-filter-btn');
      if (arcBtn) {
        handleArcFilter(arcBtn.getAttribute('data-arc'));
        return;
      }

      // Pattern card click
      var patternCard = e.target.closest('.pattern-card');
      if (patternCard) {
        var patName = patternCard.getAttribute('data-name');
        if (patName) {
          selectPattern(patName);
        }
        return;
      }

      // Pattern detail close button
      var closeBtn = e.target.closest('.pattern-detail-close');
      if (closeBtn) {
        closePatternDetail();
        return;
      }

      // Entity tag click
      var entityTag = e.target.closest('.pattern-entity-tag');
      if (entityTag) {
        var entityName = entityTag.getAttribute('data-entity');
        if (entityName && nav) {
          nav.toEntity(entityName);
        }
        return;
      }

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

  // =========================================================================
  // Sub-view Switching
  // =========================================================================

  function switchSubView(name) {
    currentSubView = name;

    // Update sub-tab buttons
    var tabs = container.querySelectorAll('.chronicle-sub-tab');
    for (var i = 0; i < tabs.length; i++) {
      if (tabs[i].getAttribute('data-subtab') === name) {
        tabs[i].classList.add('active');
      } else {
        tabs[i].classList.remove('active');
      }
    }

    // Toggle visibility
    var patternsEl = document.getElementById('chronicle-patterns');
    var validationEl = document.getElementById('chronicle-validation');
    var arcFilters = document.getElementById('chronicle-arc-filters');

    if (name === 'patterns') {
      if (patternsEl) patternsEl.style.display = '';
      if (validationEl) validationEl.style.display = 'none';
      if (arcFilters) arcFilters.style.display = '';
    } else {
      if (patternsEl) patternsEl.style.display = 'none';
      if (validationEl) validationEl.style.display = '';
      if (arcFilters) arcFilters.style.display = 'none';
    }
  }

  // =========================================================================
  // Route Handling
  // =========================================================================

  function onRoute(params) {
    if (!params) return;

    if (params.subview === 'pattern' && params.id) {
      switchSubView('patterns');
      var patternName = decodeURIComponent(params.id);
      selectPattern(patternName);
    } else if (params.subview === 'validation') {
      switchSubView('validation');
    } else {
      switchSubView('patterns');
    }
  }

  // =========================================================================
  // Patterns Sub-view
  // =========================================================================

  function renderPatternsSubView() {
    var data = dataLoader.get('patterns');
    if (!data) {
      dataLoader.load('patterns', 'data/patterns_catalog.json').then(function(d) {
        if (d) renderPatternGrid(d);
      });
      return;
    }
    renderPatternGrid(data);
  }

  function renderPatternGrid(data) {
    var gridEl = document.getElementById('chronicle-pattern-grid');
    if (!gridEl) return;

    var patterns = data.patterns || [];
    var html = '';

    for (var i = 0; i < patterns.length; i++) {
      var p = patterns[i];

      // Apply arc filter
      if (arcFilter && p.arc !== arcFilter) continue;

      html += renderPatternCard(p);
    }

    if (!html) {
      html = '<p class="empty-state">No patterns found for the selected filter.</p>';
    }

    gridEl.innerHTML = html;
  }

  function renderPatternCard(pattern) {
    var p = pattern;
    var arcColor = ARC_COLORS[p.arc] || '#94a3b8';
    var fmtName = cardRenderer.formatPatternName(p.name);

    var html = '<div class="pattern-card" data-name="' + escapeAttr(p.name) + '" data-arc="' + escapeAttr(p.arc || '') + '">';

    // Header: arc badge + name
    html += '<div class="pattern-card-header">';
    html += '<span class="badge" style="background:' + arcColor + ';color:#fff;font-size:0.65rem;padding:1px 6px">' + escapeHtml(p.arc || '') + '</span>';
    html += '<span class="pattern-card-name">' + escapeHtml(fmtName) + '</span>';
    html += '</div>';

    // Description (truncated via CSS)
    if (p.description) {
      html += '<div class="pattern-card-desc">' + escapeHtml(p.description) + '</div>';
    }

    // Stats
    html += '<div class="pattern-card-stats">';
    html += '<span><span class="pattern-card-stat-value">' + (p.attestation_count || 0) + '</span> attestations</span>';
    html += '<span><span class="pattern-card-stat-value">' + (p.tradition_count || 0) + '</span> traditions</span>';
    html += '</div>';

    // Motif tags (first 6 only)
    var motifs = p.motif_codes || [];
    if (motifs.length > 0) {
      html += '<div class="pattern-card-motifs">';
      var limit = Math.min(6, motifs.length);
      for (var m = 0; m < limit; m++) {
        html += '<span class="motif-tag">' + escapeHtml(motifs[m]) + '</span>';
      }
      if (motifs.length > 6) {
        html += '<span class="motif-tag">+' + (motifs.length - 6) + '</span>';
      }
      html += '</div>';
    }

    html += '</div>';
    return html;
  }

  // =========================================================================
  // Arc Filter
  // =========================================================================

  function handleArcFilter(arc) {
    // Toggle: same arc deselects, different arc selects
    if (arcFilter === arc) {
      arcFilter = null;
    } else {
      arcFilter = arc;
    }

    // Update button states
    var btns = container.querySelectorAll('.arc-filter-btn');
    for (var i = 0; i < btns.length; i++) {
      var btnArc = btns[i].getAttribute('data-arc');
      if (arcFilter && btnArc === arcFilter) {
        btns[i].style.background = ARC_COLORS[btnArc];
        btns[i].style.color = '#fff';
      } else {
        btns[i].style.background = 'transparent';
        btns[i].style.color = ARC_COLORS[btnArc];
      }
    }

    // Update mini-map highlight
    if (miniMap) {
      miniMap.highlightArc(arcFilter);
    }

    // Re-render pattern grid with filter
    var data = dataLoader.get('patterns');
    if (data) {
      renderPatternGrid(data);
    }
  }

  // =========================================================================
  // Pattern Selection & Detail
  // =========================================================================

  function selectPattern(name) {
    selectedPatternName = name;
    var data = dataLoader.get('patterns');
    if (!data) return;

    var pattern = findPattern(data, name);
    if (!pattern) return;

    renderPatternDetail(pattern, data);
  }

  function renderPatternDetail(pattern, data) {
    var detailEl = document.getElementById('chronicle-pattern-detail');
    if (!detailEl) return;

    var p = pattern;
    var arcColor = ARC_COLORS[p.arc] || '#94a3b8';
    var fmtName = cardRenderer.formatPatternName(p.name);
    var motifs = data.motifs || {};

    var html = '<div class="pattern-detail" data-arc="' + escapeAttr(p.arc || '') + '">';

    // Header: name + arc badge + confidence
    html += '<div class="pattern-detail-header">';
    html += '<span class="pattern-detail-name">' + escapeHtml(fmtName) + '</span>';
    html += '<span class="badge" style="background:' + arcColor + ';color:#fff">' + escapeHtml(ARC_NAMES[p.arc] || p.arc || '') + '</span>';
    if (p.confidence != null) {
      html += '<span class="badge" style="background:rgba(245,158,11,0.2);color:#fbbf24">' + p.confidence.toFixed(3) + '</span>';
    }
    html += '<button class="btn btn-small pattern-detail-close" title="Close">&times;</button>';
    html += '</div>';

    // Full description
    if (p.description) {
      html += '<div class="pattern-detail-desc">' + escapeHtml(p.description) + '</div>';
    }

    // Stats row
    html += '<div class="pattern-detail-stats">';
    html += renderDetailStat(p.attestation_count || 0, 'Attestations');
    html += renderDetailStat(p.tradition_count || 0, 'Traditions');
    html += renderDetailStat((p.motif_codes || []).length, 'Motifs');
    html += renderDetailStat((p.related_entities || []).length, 'Entities');
    html += '</div>';

    // Motif Codes section
    var motifCodes = p.motif_codes || [];
    if (motifCodes.length > 0) {
      html += '<div class="pattern-detail-section">';
      html += '<div class="pattern-detail-section-title">Motif Codes</div>';
      html += '<div class="pattern-card-motifs">';
      for (var i = 0; i < motifCodes.length; i++) {
        var code = motifCodes[i];
        var motifInfo = motifs[code];
        var label = motifInfo ? motifInfo.label : '';
        html += '<span class="motif-tag" title="' + escapeAttr(code) + '">';
        html += '<strong>' + escapeHtml(code) + '</strong>';
        if (label) {
          html += ' ' + escapeHtml(label);
        }
        html += '</span>';
      }
      html += '</div>';
      html += '</div>';
    }

    // Traditions section
    var traditions = p.traditions || [];
    if (traditions.length > 0) {
      html += '<div class="pattern-detail-section">';
      html += '<div class="pattern-detail-section-title">Traditions</div>';
      html += '<div class="pattern-tradition-tags">';
      for (var t = 0; t < traditions.length; t++) {
        html += '<span class="motif-tag">' + escapeHtml(traditions[t]) + '</span>';
      }
      html += '</div>';
      html += '</div>';
    }

    // Related Entities section
    var entities = p.related_entities || [];
    if (entities.length > 0) {
      html += '<div class="pattern-detail-section">';
      html += '<div class="pattern-detail-section-title">Related Entities</div>';
      html += '<div class="pattern-entity-tags">';
      for (var e = 0; e < entities.length; e++) {
        html += '<span class="pattern-entity-tag" data-entity="' + escapeAttr(entities[e]) + '">';
        html += escapeHtml(entities[e]);
        html += '</span>';
      }
      html += '</div>';
      html += '</div>';
    }

    html += '</div>';

    detailEl.innerHTML = html;

    // Scroll to top of content area
    var contentEl = document.getElementById('chronicle-patterns-content');
    if (contentEl) {
      contentEl.scrollTop = 0;
    }
  }

  function renderDetailStat(value, label) {
    return '<div class="pattern-detail-stat">' +
      '<div class="pattern-detail-stat-value">' + value + '</div>' +
      '<div class="pattern-detail-stat-label">' + escapeHtml(label) + '</div>' +
    '</div>';
  }

  function closePatternDetail() {
    selectedPatternName = null;
    var detailEl = document.getElementById('chronicle-pattern-detail');
    if (detailEl) {
      detailEl.innerHTML = '';
    }
  }

  // =========================================================================
  // Validation Sub-view
  // =========================================================================

  function renderValidationSubView() {
    var data = dataLoader.get('validation');
    if (!data) {
      dataLoader.load('validation', 'data/validation_summary.json').then(function(d) {
        if (d) renderValidation(d);
      });
      return;
    }
    renderValidation(data);
  }

  function renderValidation(data) {
    var el = document.getElementById('chronicle-validation');
    if (!el) return;

    var html = '';
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
      html += '<div class="tier-cards" id="chronicle-tier-cards">';
      for (var t = 0; t < tiers.length; t++) {
        html += renderTierCard(tiers[t]);
      }
      html += '</div>';

      // Expanded tier tests (rendered below the card row)
      html += '<div id="chronicle-tier-tests"></div>';
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

    el.innerHTML = html;

    // Render any initially expanded tiers
    refreshExpandedTierTests(data);
  }

  function renderValidationStat(value, label) {
    return '<div class="validation-stat">' +
      '<div class="validation-stat-value">' + value + '</div>' +
      '<div class="validation-stat-label">' + escapeHtml(label) + '</div>' +
    '</div>';
  }

  // =========================================================================
  // Tier Cards
  // =========================================================================

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
    // Only show score if there are actual tests, otherwise show insight count or description
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
    var card = container.querySelector('.tier-card[data-tier-id="' + tierId + '"]');
    if (card) {
      card.classList.toggle('expanded', expandedTiers[tierId]);
    }

    // Refresh the expanded tests area
    var data = dataLoader.get('validation');
    if (data) {
      refreshExpandedTierTests(data);
    }
  }

  function refreshExpandedTierTests(data) {
    var testsEl = document.getElementById('chronicle-tier-tests');
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

    // Re-render expanded tier tests
    var data = dataLoader.get('validation');
    if (data) {
      refreshExpandedTierTests(data);
    }
  }

  // =========================================================================
  // Audit Cases
  // =========================================================================

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

    // Re-render audit cases
    var data = dataLoader.get('validation');
    if (!data) return;

    var casesEl = container.querySelector('.audit-cases');
    if (!casesEl) return;

    var cases = data.audit_cases || [];
    var html = '<div class="pattern-detail-section-title" style="margin-bottom:8px">Audit Cases (' + cases.length + ')</div>';
    for (var c = 0; c < cases.length; c++) {
      html += renderAuditCase(cases[c], c);
    }
    casesEl.innerHTML = html;
  }

  // =========================================================================
  // Utilities
  // =========================================================================

  function findPattern(data, name) {
    var patterns = data.patterns || [];
    for (var i = 0; i < patterns.length; i++) {
      if (patterns[i].name === name) return patterns[i];
    }
    return null;
  }

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

  // =========================================================================
  // View Registration
  // =========================================================================

  function activate() {}
  function deactivate() {}

  tabRouter.register('chronicle', {
    init: init,
    activate: activate,
    deactivate: deactivate,
    onRoute: onRoute
  });
})();
