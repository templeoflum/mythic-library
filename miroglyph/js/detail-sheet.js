// Mythic System Explorer — Detail Sheet
// Renders inline detail views for archetypes and entities

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var AXIS_SHORT = [
    'Ord-Chaos', 'Cre-Dest', 'Light-Shadow', 'Act-Recep',
    'Ind-Coll', 'Asc-Desc', 'Sta-Trans', 'Vol-Fated'
  ];

  // --- Archetype Detail ---

  function renderArchetypeDetail(archetype) {
    var a = archetype;
    var cardRenderer = window.MiroGlyph.cardRenderer;
    var dataLoader = window.MiroGlyph.dataLoader;

    var html = '<div class="detail-sheet">';

    // Back button
    html += '<button class="back-btn" data-action="back">' +
      '\u2190 Back to Archetypes' +
    '</button>';

    // Header
    html += '<div class="detail-header">';
    html += '<div class="detail-title">' + escapeHtml(a.name) + '</div>';
    html += '<div class="detail-subtitle">' + escapeHtml(a.id);
    if (a.system) {
      html += ' <span class="badge badge-system">' + escapeHtml(a.system) + '</span>';
    }
    html += '</div>';
    html += '</div>';

    // Description
    if (a.description) {
      html += '<div class="detail-desc">' + escapeHtml(a.description) + '</div>';
    }

    // 3-column detail grid
    html += '<div class="detail-grid">';

    // Column 1: 8D Coordinates
    html += '<div class="detail-section">';
    html += '<div class="detail-section-title">8D Coordinates</div>';
    if (a.coordinates && a.coordinates.length === 8) {
      html += '<div class="coord-bars">';
      for (var i = 0; i < 8; i++) {
        var val = a.coordinates[i];
        var pct = Math.round(val * 100);
        html += '<div class="coord-row">';
        html += '<span class="coord-label">' + AXIS_SHORT[i] + '</span>';
        html += '<div class="coord-track">';
        html += '<div class="coord-fill" style="width:' + pct + '%"></div>';
        html += '<div class="coord-marker" style="left:' + pct + '%"></div>';
        html += '</div>';
        html += '<span class="coord-value">' + val.toFixed(2) + '</span>';
        html += '</div>';
      }
      html += '</div>';
    } else {
      html += '<p class="hint">No coordinate data.</p>';
    }
    html += '</div>';

    // Column 2: Primordials
    html += '<div class="detail-section">';
    html += '<div class="detail-section-title">Primordials</div>';
    if (a.primordials && a.primordials.length > 0) {
      for (var p = 0; p < a.primordials.length; p++) {
        var prim = a.primordials[p];
        var primName = (prim.id || '').replace('primordial:', '');
        var wPct = Math.round((prim.weight || 0) * 100);
        html += '<div class="coord-row">';
        html += '<span class="coord-label">' + escapeHtml(primName) + '</span>';
        html += '<div class="coord-track">';
        html += '<div class="coord-fill primordial-fill" style="width:' + wPct + '%"></div>';
        html += '</div>';
        html += '<span class="coord-value">' + (prim.weight || 0).toFixed(2) + '</span>';
        html += '</div>';
      }
    } else {
      html += '<p class="hint">No primordial data.</p>';
    }
    html += '</div>';

    // Column 3: Nearest Nodes
    html += '<div class="detail-section">';
    html += '<div class="detail-section-title">Nearest Nodes</div>';
    if (a.nearest_nodes && a.nearest_nodes.length > 0) {
      for (var n = 0; n < a.nearest_nodes.length; n++) {
        var nn = a.nearest_nodes[n];
        var affPct = Math.round((nn.affinity || 0) * 100);
        html += '<div class="coord-row" data-action="toNode" data-node-id="' + escapeAttr(nn.node_id) + '" style="cursor:pointer">';
        html += '<span class="coord-label">';
        html += cardRenderer.renderNodeBadge(nn.node_id);
        html += '</span>';
        html += '<div class="coord-track">';
        html += '<div class="coord-fill node-fill" style="width:' + affPct + '%"></div>';
        html += '</div>';
        html += '<span class="coord-value">' + (nn.affinity || 0).toFixed(3) + '</span>';
        html += '</div>';
      }
    } else {
      html += '<p class="hint">No node data.</p>';
    }
    html += '</div>';

    html += '</div>'; // end detail-grid

    // Relationships grouped by type
    if (a.relationships && a.relationships.length > 0) {
      html += '<div class="detail-section" style="margin-bottom:var(--spacing-lg)">';
      html += '<div class="detail-section-title">Relationships</div>';

      var grouped = {};
      for (var r = 0; r < a.relationships.length; r++) {
        var rel = a.relationships[r];
        var type = rel.type || 'OTHER';
        if (!grouped[type]) grouped[type] = [];
        grouped[type].push(rel);
      }

      var types = Object.keys(grouped);
      for (var t = 0; t < types.length; t++) {
        var groupType = types[t];
        var rels = grouped[groupType];
        html += '<div class="rel-group">';
        html += '<div class="rel-group-title">' + escapeHtml(groupType.replace(/_/g, ' ')) + '</div>';
        for (var ri = 0; ri < rels.length; ri++) {
          var relItem = rels[ri];
          html += '<div class="rel-item" data-action="toArchetype" data-id="' + escapeAttr(relItem.target) + '">';
          html += '<span class="rel-item-name">' + escapeHtml(relItem.target) + '</span>';
          if (relItem.fidelity != null) {
            html += '<span class="rel-item-fidelity">' + relItem.fidelity.toFixed(2) + '</span>';
          }
          html += '</div>';
        }
        html += '</div>';
      }

      html += '</div>';
    }

    // Source entities
    var entitiesByArch = dataLoader ? dataLoader.getIndex('entitiesByArchetype') : {};
    var sourceEntities = entitiesByArch[a.id] || [];
    if (sourceEntities.length > 0) {
      html += '<div class="detail-section">';
      html += '<div class="detail-section-title">Source Entities (' + sourceEntities.length + ')</div>';
      html += '<div class="source-entities">';
      for (var se = 0; se < sourceEntities.length; se++) {
        var eName = sourceEntities[se].name;
        html += '<span class="source-entity-tag" data-action="toEntity" data-name="' +
          escapeAttr(eName) + '">' +
          escapeHtml(eName) +
        '</span>';
      }
      html += '</div>';
      html += '</div>';
    }

    html += '</div>'; // end detail-sheet
    return html;
  }

  // --- Entity Detail ---

  function renderEntityDetail(entity) {
    var e = entity;
    var cardRenderer = window.MiroGlyph.cardRenderer;
    var dataLoader = window.MiroGlyph.dataLoader;
    var enrichment = window.MiroGlyph.enrichment;
    var nodesModule = window.MiroGlyph.nodes;

    var html = '<div class="detail-sheet">';

    // Back button
    html += '<button class="back-btn" data-action="back">' +
      '\u2190 Back to Entities' +
    '</button>';

    // Header
    html += '<div class="detail-header">';
    html += '<div class="detail-title">' + escapeHtml(e.name) + '</div>';
    html += '<div class="detail-subtitle">';
    if (e.type) {
      html += '<span class="badge badge-system">' + escapeHtml(e.type) + '</span> ';
    }
    if (e.primary_tradition) {
      html += '<span class="badge">' + escapeHtml(e.primary_tradition) + '</span>';
    }
    html += '</div>';
    html += '</div>';

    // Summary line
    var mentions = e.total_mentions || 0;
    var texts = e.text_count || 0;
    var traditions = e.tradition_count || 0;
    html += '<div class="detail-desc">' +
      mentions + ' mentions across ' + texts + ' texts, ' + traditions + ' traditions' +
    '</div>';

    // Connection Chain
    html += renderConnectionChain(e, dataLoader, nodesModule);

    // 8D Coordinate Comparison
    html += renderCoordinateComparison(e, enrichment);

    // All Node Affinities grid
    if (e.top_nodes && e.top_nodes.length > 0) {
      var nearestNodeId = resolveNearestNodeId(e);

      html += '<div class="detail-section" style="margin-bottom:var(--spacing-lg)">';
      html += '<div class="detail-section-title">All Node Affinities</div>';
      html += '<div class="affinity-grid">';

      for (var i = 0; i < e.top_nodes.length; i++) {
        var tn = e.top_nodes[i];
        var isNearest = nearestNodeId && tn.node_id === nearestNodeId;
        var cellClass = 'affinity-cell' + (isNearest ? ' nearest' : '');
        html += '<div class="' + cellClass + '">';
        html += '<div class="affinity-cell-id">' + escapeHtml(tn.node_id) + '</div>';
        html += '<div class="affinity-cell-val">' + (tn.affinity || 0).toFixed(3) + '</div>';
        html += '</div>';
      }

      html += '</div>';
      html += '</div>';
    }

    html += '</div>'; // end detail-sheet
    return html;
  }

  // --- Connection Chain ---

  function renderConnectionChain(entity, dataLoader, nodesModule) {
    var e = entity;
    var hasMappingArch = !!(e.mapping && e.mapping.archetype_id);
    var chainNodeId = resolveChainNodeId(e);
    var hasNode = !!chainNodeId;

    var html = '<div class="chain-visual">';

    // Card 1: Library Entity
    html += '<div class="chain-card chain-card-library">';
    html += '<div class="chain-card-label">Library Entity</div>';
    html += '<div class="chain-card-name">' + escapeHtml(e.name) + '</div>';
    html += '<div class="chain-card-meta">';
    if (e.type) html += escapeHtml(e.type) + '<br>';
    if (e.primary_tradition) html += escapeHtml(e.primary_tradition) + '<br>';
    html += (e.total_mentions || 0) + ' mentions';
    html += '</div>';
    html += '</div>';

    // Arrow 1
    html += '<div class="' + (hasMappingArch ? 'chain-arrow' : 'chain-broken') + '">';
    html += hasMappingArch ? '\u2192' : '\u2717';
    html += '</div>';

    // Card 2: ACP Archetype
    if (hasMappingArch) {
      var archId = e.mapping.archetype_id;
      var archName = e.mapping.archetype_name || archId;
      var archLookup = dataLoader ? dataLoader.getIndex('archetypeById')[archId] : null;
      if (archLookup) {
        archName = archLookup.name;
      }

      var confidence = 0;
      if (e.mapping.score != null) {
        confidence = e.mapping.score;
      } else if (e.mapping.confidence != null) {
        confidence = e.mapping.confidence;
      }

      html += '<div class="chain-card chain-card-acp" data-action="toArchetype" data-id="' + escapeAttr(archId) + '">';
      html += '<div class="chain-card-label">ACP Archetype</div>';
      html += '<div class="chain-card-name">' + escapeHtml(archName) + '</div>';
      html += '<div class="chain-card-meta">';
      html += '<code>' + escapeHtml(archId) + '</code><br>';
      html += 'Confidence: ' + confidence.toFixed(2);
      html += '</div>';
      html += '</div>';
    } else {
      html += '<div class="chain-card chain-card-acp" style="opacity:0.5">';
      html += '<div class="chain-card-label">ACP Archetype</div>';
      html += '<div class="chain-card-name">No mapping found</div>';
      html += '</div>';
    }

    // Arrow 2
    html += '<div class="' + (hasNode ? 'chain-arrow' : 'chain-broken') + '">';
    html += hasNode ? '\u2192' : '\u2717';
    html += '</div>';

    // Card 3: Miroglyph Node
    if (hasNode) {
      var nodeData = nodesModule ? nodesModule.getNode(chainNodeId) : null;
      var nodeTitle = nodeData ? nodeData.title : '';
      var nodeAffinity = 0;
      if (e.nearest_node && typeof e.nearest_node === 'object') {
        nodeAffinity = e.nearest_node.affinity || 0;
      }

      html += '<div class="chain-card chain-card-miroglyph" data-action="toNode" data-node-id="' + escapeAttr(chainNodeId) + '">';
      html += '<div class="chain-card-label">Miroglyph Node</div>';
      html += '<div class="chain-card-name">' + escapeHtml(chainNodeId) + '</div>';
      html += '<div class="chain-card-meta">';
      if (nodeTitle) html += escapeHtml(nodeTitle) + '<br>';
      html += 'Affinity: ' + nodeAffinity.toFixed(3);
      html += '</div>';
      html += '</div>';
    } else {
      html += '<div class="chain-card chain-card-miroglyph" style="opacity:0.5">';
      html += '<div class="chain-card-label">Miroglyph Node</div>';
      html += '<div class="chain-card-name">Cannot trace</div>';
      html += '</div>';
    }

    html += '</div>'; // end chain-visual
    return html;
  }

  // --- Coordinate Comparison ---

  function renderCoordinateComparison(entity, enrichment) {
    var e = entity;
    if (!e.coordinates || e.coordinates.length !== 8) return '';

    var nearestNodeId = resolveNearestNodeId(e);
    var nodeCoords = null;

    if (nearestNodeId && enrichment && enrichment.isLoaded()) {
      var profile = enrichment.getNodeProfile(nearestNodeId);
      if (profile && profile.mean_coordinates) {
        nodeCoords = profile.mean_coordinates;
      }
    }

    var html = '<div class="coord-compare" style="margin-bottom:var(--spacing-lg)">';
    html += '<div class="detail-section-title">8D Coordinate Comparison</div>';

    // Legend
    if (nodeCoords) {
      html += '<div class="coord-compare-legend">';
      html += '<span>';
      html += '<span class="coord-compare-swatch" style="background:var(--color-library)"></span>';
      html += 'Entity';
      html += '</span>';
      html += '<span>';
      html += '<span class="coord-compare-swatch" style="background:var(--color-miroglyph)"></span>';
      html += 'Node Centroid';
      html += '</span>';
      html += '</div>';
    }

    // Axis rows
    for (var i = 0; i < 8; i++) {
      var entVal = e.coordinates[i];
      var entPct = Math.round(entVal * 100);

      html += '<div class="coord-compare-row">';
      html += '<span class="coord-label" style="width:70px;text-align:right;flex-shrink:0;font-size:0.65rem">' +
        AXIS_SHORT[i] + '</span>';

      html += '<div class="coord-compare-track">';
      html += '<div class="coord-compare-marker coord-compare-marker-entity" style="left:' + entPct + '%"></div>';
      if (nodeCoords) {
        var nodeVal = nodeCoords[i] || 0.5;
        var nodePct = Math.round(nodeVal * 100);
        html += '<div class="coord-compare-marker coord-compare-marker-node" style="left:' + nodePct + '%"></div>';
      }
      html += '</div>';

      html += '<span class="coord-value" style="width:35px">' + entVal.toFixed(2) + '</span>';
      html += '</div>';
    }

    html += '</div>';
    return html;
  }

  // --- Helpers ---

  function resolveNearestNodeId(entity) {
    if (entity.nearest_node) {
      if (typeof entity.nearest_node === 'object') {
        return entity.nearest_node.node_id;
      }
      return entity.nearest_node;
    }
    return null;
  }

  function resolveChainNodeId(entity) {
    // Prefer tracing_chain.node if available, fall back to nearest_node
    if (entity.mapping && entity.mapping.tracing_chain && entity.mapping.tracing_chain.node) {
      return entity.mapping.tracing_chain.node;
    }
    return resolveNearestNodeId(entity);
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

  window.MiroGlyph.detailSheet = {
    renderArchetypeDetail: renderArchetypeDetail,
    renderEntityDetail: renderEntityDetail
  };
})();
