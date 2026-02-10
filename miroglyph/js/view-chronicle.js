// Mythic System Explorer — Chronicle View
// Dual sub-view: Mythic Paths (mini-map + pattern grid) and My Journeys (aggregated traversals)

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var dataLoader = window.MiroGlyph.dataLoader;
  var nav = window.MiroGlyph.nav;
  var tabRouter = window.MiroGlyph.tabRouter;
  var miniMap = window.MiroGlyph.miniMap;
  var cardRenderer = window.MiroGlyph.cardRenderer;
  var journeyAggregator = window.MiroGlyph.journeyAggregator;

  // --- State ---
  var currentSubView = 'paths'; // 'paths' or 'journeys'
  var selectedPatternName = null;
  var arcFilter = null;              // null, 'D', 'R', or 'E'
  var container = null;

  // Journey state
  var journeyRecords = [];
  var selectedJourneyId = null;
  var journeySourceFilter = null;   // null | 'explorer' | 'journey'
  var journeySortOrder = 'newest';  // 'newest' | 'oldest' | 'name'

  // --- Arc Metadata ---
  var ARC_COLORS = { D: '#8b5cf6', R: '#3b82f6', E: '#10b981' };
  var ARC_NAMES = { D: 'Descent', R: 'Resonance', E: 'Emergence' };

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
    html += '<button class="chronicle-sub-tab active" data-subtab="paths">Mythic Paths</button>';
    html += '<button class="chronicle-sub-tab" data-subtab="journeys">My Journeys</button>';
    html += '</div>';

    // Arc filter buttons (paths sub-view only)
    html += '<div class="patterns-arc-filters" id="chronicle-arc-filters">';
    html += '<button class="btn btn-small arc-filter-btn" data-arc="D" style="border-color:' + ARC_COLORS.D + ';color:' + ARC_COLORS.D + '">D</button>';
    html += '<button class="btn btn-small arc-filter-btn" data-arc="R" style="border-color:' + ARC_COLORS.R + ';color:' + ARC_COLORS.R + '">R</button>';
    html += '<button class="btn btn-small arc-filter-btn" data-arc="E" style="border-color:' + ARC_COLORS.E + ';color:' + ARC_COLORS.E + '">E</button>';
    html += '<button class="btn btn-small btn-surprise" id="chronicle-surprise" title="Random pattern">\u2728</button>';
    html += '</div>';

    html += '</div>'; // filter-bar

    // Mythic Paths sub-view
    html += '<div class="patterns-layout" id="chronicle-patterns">';
    html += '<div class="patterns-map-sidebar">';
    html += '<div class="patterns-map-container" id="chronicle-minimap"></div>';
    html += '</div>';
    html += '<div class="patterns-content" id="chronicle-patterns-content">';
    html += '<div id="chronicle-pattern-detail"></div>';
    html += '<div class="pattern-grid" id="chronicle-pattern-grid"></div>';
    html += '</div>';
    html += '</div>';

    // My Journeys sub-view
    html += '<div class="journeys-layout" id="chronicle-journeys" style="display:none">';
    html += '<div class="journeys-sidebar">';
    html += '<div class="journeys-map-container" id="chronicle-journeys-minimap"></div>';
    html += '</div>';
    html += '<div class="journeys-content">';
    html += '<div id="chronicle-journey-detail"></div>';
    html += '<div class="journeys-controls" id="chronicle-journeys-controls"></div>';
    html += '<div class="journey-list" id="chronicle-journey-list"></div>';
    html += '</div>';
    html += '</div>';

    html += '</div>'; // chronicle-layout

    container.innerHTML = html;

    // Render mini-map into Mythic Paths (default visible)
    var mapContainer = document.getElementById('chronicle-minimap');
    if (mapContainer && miniMap) {
      miniMap.render(mapContainer);
    }

    // Load and render data
    renderPatternsSubView();
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

      // Surprise Me button
      var surpriseBtn = e.target.closest('#chronicle-surprise');
      if (surpriseBtn) {
        if (nav && nav.surpriseMe) {
          nav.surpriseMe('pattern');
        }
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

      // Journey detail close button
      var journeyCloseBtn = e.target.closest('.journey-detail-close');
      if (journeyCloseBtn) {
        closeJourneyDetail();
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

      // Motif tag click - navigate to Codex Motifs sub-tab with filter
      var motifTag = e.target.closest('.motif-tag-clickable');
      if (motifTag) {
        var motifCode = motifTag.getAttribute('data-motif-code');
        if (motifCode) {
          window.location.hash = 'codex';
          setTimeout(function() {
            var viewCodex = window.MiroGlyph.viewCodex;
            if (viewCodex && viewCodex.switchSubTab) {
              viewCodex.switchSubTab('motifs');
              var searchInput = document.querySelector('#codex-search');
              if (searchInput) {
                searchInput.value = motifCode;
                searchInput.dispatchEvent(new Event('input'));
              }
            }
          }, 100);
        }
        return;
      }

      // Source filter button
      var sourceBtn = e.target.closest('.source-filter-btn');
      if (sourceBtn) {
        handleSourceFilter(sourceBtn.getAttribute('data-source'));
        return;
      }

      // Journey card click
      var journeyCard = e.target.closest('.journey-card');
      if (journeyCard) {
        var journeyId = journeyCard.getAttribute('data-journey-id');
        if (journeyId) {
          selectJourney(journeyId);
        }
        return;
      }
    });

    // Sort dropdown change
    container.addEventListener('change', function(e) {
      if (e.target.closest('.journeys-sort')) {
        journeySortOrder = e.target.value;
        loadAndRenderJourneys();
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
    var journeysEl = document.getElementById('chronicle-journeys');
    var arcFilters = document.getElementById('chronicle-arc-filters');

    if (name === 'paths') {
      if (patternsEl) patternsEl.style.display = '';
      if (journeysEl) journeysEl.style.display = 'none';
      if (arcFilters) arcFilters.style.display = '';

      // Re-render mini-map into Mythic Paths sidebar
      var mapContainer = document.getElementById('chronicle-minimap');
      if (mapContainer && miniMap) {
        miniMap.render(mapContainer);
        // Restore arc filter highlight if active
        if (arcFilter) {
          miniMap.highlightArc(arcFilter);
        }
      }
    } else if (name === 'journeys') {
      if (patternsEl) patternsEl.style.display = 'none';
      if (journeysEl) journeysEl.style.display = '';
      if (arcFilters) arcFilters.style.display = 'none';

      // Re-render mini-map into My Journeys sidebar
      var jMapContainer = document.getElementById('chronicle-journeys-minimap');
      if (jMapContainer && miniMap) {
        miniMap.render(jMapContainer);
      }

      // Load journey data fresh each time (picks up new saves)
      loadAndRenderJourneys();
    }
  }

  // =========================================================================
  // Route Handling
  // =========================================================================

  function onRoute(params) {
    if (!params) return;

    if (params.subview === 'pattern' && params.id) {
      switchSubView('paths');
      var patternName = decodeURIComponent(params.id);
      selectPattern(patternName);
    } else if (params.subview === 'journeys') {
      switchSubView('journeys');
    } else if (params.subview === 'journey' && params.id) {
      switchSubView('journeys');
      selectJourney(decodeURIComponent(params.id));
    } else {
      switchSubView('paths');
    }
  }

  // =========================================================================
  // Mythic Paths Sub-view
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

    // Motif tags - show first 8 with "more" indicator, full list in detail view
    var motifs = p.motif_codes || [];
    if (motifs.length > 0) {
      html += '<div class="pattern-card-motifs">';
      var limit = Math.min(8, motifs.length);
      for (var m = 0; m < limit; m++) {
        html += '<span class="motif-tag">' + escapeHtml(motifs[m]) + '</span>';
      }
      if (motifs.length > 8) {
        html += '<span class="motif-tag motif-more">+' + (motifs.length - 8) + ' more</span>';
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

    // Motif Codes section - now clickable and navigable
    var motifCodes = p.motif_codes || [];
    if (motifCodes.length > 0) {
      html += '<div class="pattern-detail-section">';
      html += '<div class="pattern-detail-section-title">Motif Codes (' + motifCodes.length + ')</div>';
      html += '<div class="pattern-card-motifs" style="max-height:200px;overflow-y:auto">';
      // Show ALL motifs, not truncated
      for (var i = 0; i < motifCodes.length; i++) {
        var code = motifCodes[i];
        var motifInfo = motifs[code];
        var label = motifInfo ? motifInfo.label : '';
        html += '<span class="motif-tag motif-tag-clickable" data-motif-code="' + escapeAttr(code) + '" title="Click to view in Codex">';
        html += '<strong>' + escapeHtml(code) + '</strong>';
        if (label) {
          html += ' ' + escapeHtml(label);
        }
        html += '</span>';
      }
      html += '</div>';
      html += '</div>';
    }

    // Traditions section - show ALL, use flex-wrap
    var traditions = p.traditions || [];
    if (traditions.length > 0) {
      html += '<div class="pattern-detail-section">';
      html += '<div class="pattern-detail-section-title">Traditions (' + traditions.length + ')</div>';
      html += '<div class="pattern-tradition-tags" style="max-height:150px;overflow-y:auto">';
      // Show ALL traditions, not truncated
      for (var t = 0; t < traditions.length; t++) {
        html += '<span class="motif-tag">' + escapeHtml(traditions[t]) + '</span>';
      }
      html += '</div>';
      html += '</div>';
    }

    // Related Entities section - show ALL entities, scrollable
    var entities = p.related_entities || [];
    if (entities.length > 0) {
      html += '<div class="pattern-detail-section">';
      html += '<div class="pattern-detail-section-title">Related Entities (' + entities.length + ')</div>';
      html += '<div class="pattern-entity-tags" style="max-height:200px;overflow-y:auto">';
      // Show ALL entities, not truncated
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
  // My Journeys Sub-view
  // =========================================================================

  function loadAndRenderJourneys() {
    if (!journeyAggregator) return;

    journeyRecords = journeyAggregator.loadAll(journeySortOrder);
    renderJourneyControls();
    renderJourneyList();

    // Re-select if we had a selection
    if (selectedJourneyId) {
      var found = false;
      for (var i = 0; i < journeyRecords.length; i++) {
        if (journeyRecords[i].id === selectedJourneyId) {
          found = true;
          break;
        }
      }
      if (found) {
        renderJourneyDetail(selectedJourneyId);
      } else {
        selectedJourneyId = null;
        clearJourneyDetail();
      }
    }
  }

  function renderJourneyControls() {
    var controlsEl = document.getElementById('chronicle-journeys-controls');
    if (!controlsEl) return;

    var filtered = getFilteredJourneys();

    var html = '';

    // Source filter pills
    html += '<div class="journeys-filter-bar">';
    html += '<button class="source-filter-btn' + (journeySourceFilter === null ? ' active' : '') + '" data-source="all">All</button>';
    html += '<button class="source-filter-btn' + (journeySourceFilter === 'explorer' ? ' active' : '') + '" data-source="explorer">Atlas</button>';
    html += '<button class="source-filter-btn' + (journeySourceFilter === 'journey' ? ' active' : '') + '" data-source="journey">Journey</button>';

    // Sort dropdown
    html += '<select class="journeys-sort">';
    html += '<option value="newest"' + (journeySortOrder === 'newest' ? ' selected' : '') + '>Newest</option>';
    html += '<option value="oldest"' + (journeySortOrder === 'oldest' ? ' selected' : '') + '>Oldest</option>';
    html += '<option value="name"' + (journeySortOrder === 'name' ? ' selected' : '') + '>Name A\u2013Z</option>';
    html += '</select>';

    // Count badge
    html += '<span class="journeys-count">' + filtered.length + ' journey' + (filtered.length !== 1 ? 's' : '') + '</span>';

    html += '</div>';

    controlsEl.innerHTML = html;
  }

  function getFilteredJourneys() {
    if (!journeySourceFilter) return journeyRecords;

    var filtered = [];
    for (var i = 0; i < journeyRecords.length; i++) {
      if (journeyRecords[i].source === journeySourceFilter) {
        filtered.push(journeyRecords[i]);
      }
    }
    return filtered;
  }

  function handleSourceFilter(source) {
    if (source === 'all') {
      journeySourceFilter = null;
    } else {
      // Toggle off if clicking the same filter
      if (journeySourceFilter === source) {
        journeySourceFilter = null;
      } else {
        journeySourceFilter = source;
      }
    }
    renderJourneyControls();
    renderJourneyList();
  }

  function renderJourneyList() {
    var listEl = document.getElementById('chronicle-journey-list');
    if (!listEl) return;

    var filtered = getFilteredJourneys();

    if (filtered.length === 0) {
      var emptyMsg = journeySourceFilter
        ? 'No ' + (journeySourceFilter === 'explorer' ? 'Atlas' : 'Journey Mapper') + ' traversals found.'
        : 'No journeys recorded yet. Create traversals in the Atlas or walk networks in the Journey Mapper to see them here.';
      listEl.innerHTML = '<div class="journeys-empty">' + escapeHtml(emptyMsg) + '</div>';
      return;
    }

    var html = '';
    for (var i = 0; i < filtered.length; i++) {
      html += renderJourneyCard(filtered[i]);
    }

    listEl.innerHTML = html;
  }

  function renderJourneyCard(record) {
    var r = record;
    var isSelected = selectedJourneyId === r.id;
    var sourceLabel = r.source === 'explorer' ? 'Atlas' : 'Journey';
    var sourceCls = r.source === 'explorer' ? 'source-explorer' : 'source-journey';

    var html = '<div class="journey-card' + (isSelected ? ' selected' : '') + '" data-journey-id="' + escapeAttr(r.id) + '" style="border-left-color:' + r.color + '">';

    // Header row: source badge + color dot + name + date
    html += '<div class="journey-card-header">';
    html += '<span class="journey-source-badge ' + sourceCls + '">' + sourceLabel + '</span>';
    html += '<span class="journey-color-dot" style="background:' + r.color + '"></span>';
    html += '<span class="journey-card-name">' + escapeHtml(r.name) + '</span>';
    if (r.created_date) {
      html += '<span class="journey-card-date">' + formatDate(r.created_date) + '</span>';
    }
    html += '</div>';

    // Sequence row: arc-colored node chips (max 6 + overflow)
    var seq = r.sequence || [];
    if (seq.length > 0) {
      html += '<div class="journey-card-sequence">';
      var limit = Math.min(6, seq.length);
      for (var i = 0; i < limit; i++) {
        var nodeId = seq[i];
        var chipColor = getNodeChipColor(nodeId);
        html += '<span class="node-chip-small" style="background:' + chipColor + '">' + escapeHtml(nodeId) + '</span>';
        if (i < limit - 1 || seq.length > limit) {
          html += '<span class="node-chip-arrow">\u2192</span>';
        }
      }
      if (seq.length > 6) {
        html += '<span class="node-chip-more">+' + (seq.length - 6) + ' more</span>';
      }
      html += '</div>';
    }

    // Meta row: context info + badges
    html += '<div class="journey-card-meta">';
    if (r.network_name) {
      html += '<span class="journey-context">' + escapeHtml(r.network_name) + '</span>';
    }
    if (r.archetype_summary) {
      html += '<span class="journey-context">' + escapeHtml(r.archetype_summary) + '</span>';
    }
    if (r.group_name) {
      html += '<span class="journey-context">' + escapeHtml(r.group_name) + '</span>';
    }
    if (r.is_circuit) {
      html += '<span class="badge-circuit">Circuit</span>';
    }
    if (r.completed) {
      html += '<span class="badge-completed">Completed</span>';
    }
    if (r.notes && Object.keys(r.notes).length > 0) {
      html += '<span class="badge-notes">' + Object.keys(r.notes).length + ' notes</span>';
    }
    html += '</div>';

    html += '</div>';
    return html;
  }

  // =========================================================================
  // Journey Selection & Detail
  // =========================================================================

  function selectJourney(journeyId) {
    selectedJourneyId = journeyId;

    // Update card selection
    var cards = container.querySelectorAll('.journey-card');
    for (var i = 0; i < cards.length; i++) {
      if (cards[i].getAttribute('data-journey-id') === journeyId) {
        cards[i].classList.add('selected');
      } else {
        cards[i].classList.remove('selected');
      }
    }

    renderJourneyDetail(journeyId);
  }

  function renderJourneyDetail(journeyId) {
    var detailEl = document.getElementById('chronicle-journey-detail');
    if (!detailEl) return;

    var record = null;
    for (var i = 0; i < journeyRecords.length; i++) {
      if (journeyRecords[i].id === journeyId) {
        record = journeyRecords[i];
        break;
      }
    }
    if (!record) {
      detailEl.innerHTML = '';
      return;
    }

    var r = record;
    var sourceLabel = r.source === 'explorer' ? 'Atlas' : 'Journey Mapper';
    var sourceCls = r.source === 'explorer' ? 'source-explorer' : 'source-journey';

    var html = '<div class="journey-detail" style="border-left-color:' + r.color + '">';

    // Header
    html += '<div class="journey-detail-header">';
    html += '<span class="journey-source-badge ' + sourceCls + '">' + sourceLabel + '</span>';
    html += '<span class="journey-detail-name">' + escapeHtml(r.name) + '</span>';
    if (r.completed) {
      html += '<span class="badge-completed">Completed</span>';
    }
    if (r.is_circuit) {
      html += '<span class="badge-circuit">Circuit</span>';
    }
    html += '<button class="btn btn-small journey-detail-close" title="Close">&times;</button>';
    html += '</div>';

    // Description (Explorer only)
    if (r.description) {
      html += '<div class="journey-detail-desc">' + escapeHtml(r.description) + '</div>';
    }

    // Stats row
    var seq = r.sequence || [];
    var arcBreakdown = getArcBreakdown(seq);

    html += '<div class="journey-detail-stats">';
    html += renderJourneyStat(seq.length, 'Nodes');
    html += renderJourneyStat(arcBreakdown.D || 0, 'Descent');
    html += renderJourneyStat(arcBreakdown.R || 0, 'Resonance');
    html += renderJourneyStat(arcBreakdown.E || 0, 'Emergence');
    if (arcBreakdown.other > 0) {
      html += renderJourneyStat(arcBreakdown.other, 'Other');
    }
    html += '</div>';

    // Full sequence visualization
    if (seq.length > 0) {
      html += '<div class="journey-detail-section">';
      html += '<div class="journey-detail-section-title">Sequence</div>';
      html += '<div class="journey-detail-sequence">';
      for (var s = 0; s < seq.length; s++) {
        var nodeId = seq[s];
        var chipColor = getNodeChipColor(nodeId);
        html += '<span class="node-chip-small" style="background:' + chipColor + '">' + escapeHtml(nodeId) + '</span>';
        if (s < seq.length - 1) {
          html += '<span class="node-chip-arrow">\u2192</span>';
        }
      }
      html += '</div>';
      html += '</div>';
    }

    // Context info
    if (r.network_name || r.archetype_summary || r.group_name || r.created_date) {
      html += '<div class="journey-detail-section">';
      html += '<div class="journey-detail-section-title">Context</div>';
      html += '<div class="journey-detail-context">';
      if (r.network_name) {
        html += '<div><strong>Network:</strong> ' + escapeHtml(r.network_name) + '</div>';
      }
      if (r.archetype_summary) {
        html += '<div><strong>Archetypes:</strong> ' + escapeHtml(r.archetype_summary) + '</div>';
      }
      if (r.group_name) {
        html += '<div><strong>Group:</strong> ' + escapeHtml(r.group_name) + '</div>';
      }
      if (r.created_date) {
        html += '<div><strong>Created:</strong> ' + escapeHtml(formatDate(r.created_date)) + '</div>';
      }
      html += '</div>';
      html += '</div>';
    }

    // Notes (JM only)
    if (r.notes && typeof r.notes === 'object') {
      var noteKeys = Object.keys(r.notes);
      if (noteKeys.length > 0) {
        html += '<div class="journey-detail-section">';
        html += '<div class="journey-detail-section-title">Notes (' + noteKeys.length + ')</div>';
        for (var n = 0; n < noteKeys.length; n++) {
          var nk = noteKeys[n];
          var noteColor = getNodeChipColor(nk);
          html += '<div class="journey-note-card" style="border-left-color:' + noteColor + '">';
          html += '<div class="journey-note-node">' + escapeHtml(nk) + '</div>';
          html += '<div class="journey-note-text">' + escapeHtml(r.notes[nk]) + '</div>';
          html += '</div>';
        }
        html += '</div>';
      }
    }

    html += '</div>';

    detailEl.innerHTML = html;

    // Draw path on mini-map
    if (miniMap && seq.length >= 2) {
      miniMap.clearPaths();
      miniMap.drawPath(seq, r.color, 2);
      miniMap.highlightNodes(seq);
    }

    // Scroll to top of content area
    var contentEl = detailEl.closest('.journeys-content');
    if (contentEl) {
      contentEl.scrollTop = 0;
    }
  }

  function renderJourneyStat(value, label) {
    return '<div class="journey-detail-stat">' +
      '<div class="journey-detail-stat-value">' + value + '</div>' +
      '<div class="journey-detail-stat-label">' + escapeHtml(label) + '</div>' +
    '</div>';
  }

  function closeJourneyDetail() {
    selectedJourneyId = null;

    var detailEl = document.getElementById('chronicle-journey-detail');
    if (detailEl) {
      detailEl.innerHTML = '';
    }

    // Clear mini-map highlights
    if (miniMap) {
      miniMap.clearPaths();
      miniMap.highlightNodes(null);
    }

    // Remove selection from cards
    var cards = container.querySelectorAll('.journey-card');
    for (var i = 0; i < cards.length; i++) {
      cards[i].classList.remove('selected');
    }
  }

  function clearJourneyDetail() {
    var detailEl = document.getElementById('chronicle-journey-detail');
    if (detailEl) {
      detailEl.innerHTML = '';
    }
  }

  // =========================================================================
  // Helpers
  // =========================================================================

  function getNodeChipColor(nodeId) {
    if (!nodeId) return '#94a3b8';
    var arc = nodeId.charAt(0);
    return ARC_COLORS[arc] || '#fbbf24';
  }

  function getArcBreakdown(sequence) {
    var counts = { D: 0, R: 0, E: 0, other: 0 };
    for (var i = 0; i < sequence.length; i++) {
      var arc = sequence[i].charAt(0);
      if (counts[arc] !== undefined) {
        counts[arc]++;
      } else {
        counts.other++;
      }
    }
    return counts;
  }

  function formatDate(dateStr) {
    if (!dateStr) return '';
    try {
      var d = new Date(dateStr);
      if (isNaN(d.getTime())) return dateStr;
      return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
    } catch (e) {
      return dateStr;
    }
  }

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
