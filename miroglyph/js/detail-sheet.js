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

    // Source entities - clickable with count
    var entitiesByArch = dataLoader ? dataLoader.getIndex('entitiesByArchetype') : {};
    var sourceEntities = entitiesByArch[a.id] || [];
    if (sourceEntities.length > 0) {
      html += '<div class="detail-section">';
      html += '<div class="detail-section-title">';
      html += 'Source Entities ';
      html += '<span class="badge" style="font-size:0.6rem">' + sourceEntities.length + '</span>';
      html += '</div>';
      html += '<div class="source-entities" style="max-height:200px;overflow-y:auto">';
      // Show ALL source entities, scrollable
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

    // Related Archetypes (from relationships + nearby by spectral distance)
    html += renderRelatedArchetypes(a, dataLoader);

    html += '</div>'; // end detail-sheet
    return html;
  }

  // --- Related Archetypes ---
  function renderRelatedArchetypes(archetype, dataLoader) {
    if (!dataLoader) return '';

    var related = [];
    var seen = {};
    seen[archetype.id] = true;

    // From explicit relationships
    if (archetype.relationships && archetype.relationships.length > 0) {
      for (var i = 0; i < archetype.relationships.length && related.length < 12; i++) {
        var rel = archetype.relationships[i];
        if (!seen[rel.target]) {
          var archById = dataLoader.getIndex('archetypeById');
          var targetArch = archById[rel.target];
          var displayName = targetArch ? targetArch.name : rel.target;
          related.push({
            id: rel.target,
            name: displayName,
            reason: rel.type ? rel.type.replace(/_/g, ' ') : 'Related'
          });
          seen[rel.target] = true;
        }
      }
    }

    // From same node (if we have nearest nodes)
    if (archetype.nearest_nodes && archetype.nearest_nodes.length > 0) {
      var primaryNode = archetype.nearest_nodes[0].node_id;
      var archsByNode = dataLoader.getIndex('archetypesByNode');
      var sameNode = archsByNode[primaryNode] || [];

      for (var j = 0; j < sameNode.length && related.length < 16; j++) {
        var arch = sameNode[j];
        var archId = arch.archetype_id || arch.id;
        if (!seen[archId]) {
          var archById = dataLoader.getIndex('archetypeById');
          var archData = archById[archId];
          if (archData) {
            related.push({
              id: archId,
              name: archData.name,
              reason: 'Same node (' + primaryNode + ')'
            });
            seen[archId] = true;
          }
        }
      }
    }

    if (related.length === 0) return '';

    var html = '<div class="related-section">';
    html += '<div class="related-section-title">Related Archetypes <span class="badge" style="font-size:0.6rem">' + related.length + '</span></div>';
    html += '<div class="related-items">';
    for (var r = 0; r < related.length; r++) {
      html += '<span class="related-item" data-action="toArchetype" data-id="' + escapeAttr(related[r].id) + '" title="' + escapeAttr(related[r].reason) + '">';
      html += escapeHtml(related[r].name);
      html += '</span>';
    }
    html += '</div>';
    html += '</div>';

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

    // Summary line with more data
    var mentions = e.total_mentions || 0;
    var texts = e.text_count || 0;
    var traditions = e.tradition_count || 0;
    html += '<div class="detail-desc">' +
      mentions + ' mentions across ' + texts + ' texts, ' + traditions + ' traditions' +
    '</div>';

    // Mapping data badges (fidelity, distance, method)
    if (e.mapping) {
      html += '<div class="entity-mapping-badges" style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:var(--spacing-lg)">';

      // Fidelity badge
      if (e.mapping.fidelity != null) {
        var fidelityClass = e.mapping.fidelity >= 0.8 ? 'fidelity-high' :
                            (e.mapping.fidelity >= 0.5 ? 'fidelity-medium' : 'fidelity-low');
        html += '<span class="fidelity-badge ' + fidelityClass + '">';
        html += 'Fidelity: ' + e.mapping.fidelity.toFixed(2);
        html += '</span>';
      }

      // Distance badge
      if (e.mapping.distance != null) {
        html += '<span class="distance-badge">';
        html += 'ACP Distance: ' + e.mapping.distance.toFixed(4);
        html += '</span>';
      }

      // Method badge
      if (e.mapping.method) {
        html += '<span class="badge" style="background:rgba(99,102,241,0.2);color:#818cf8">';
        html += 'Method: ' + escapeHtml(e.mapping.method);
        html += '</span>';
      }

      html += '</div>';
    }

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

    // Related Entities section (share same archetype or similar node)
    html += renderRelatedEntities(e, dataLoader);

    // Related Patterns section (patterns featuring this entity)
    html += renderRelatedPatterns(e, dataLoader);

    html += '</div>'; // end detail-sheet
    return html;
  }

  // --- Related Entities ---
  function renderRelatedEntities(entity, dataLoader) {
    if (!dataLoader) return '';

    var related = [];
    var seen = {};
    seen[entity.name] = true;

    // Find entities sharing the same archetype
    if (entity.mapping && entity.mapping.archetype_id) {
      var entitiesByArch = dataLoader.getIndex('entitiesByArchetype');
      var sameArch = entitiesByArch[entity.mapping.archetype_id] || [];
      for (var i = 0; i < sameArch.length && related.length < 8; i++) {
        if (!seen[sameArch[i].name]) {
          related.push({ name: sameArch[i].name, reason: 'Same archetype' });
          seen[sameArch[i].name] = true;
        }
      }
    }

    // Find entities sharing the same node
    var nodeId = resolveNearestNodeId(entity);
    if (nodeId) {
      var entitiesByNode = dataLoader.getIndex('entitiesByNode');
      var sameNode = entitiesByNode[nodeId] || [];
      for (var j = 0; j < sameNode.length && related.length < 12; j++) {
        if (!seen[sameNode[j].name]) {
          related.push({ name: sameNode[j].name, reason: 'Same node' });
          seen[sameNode[j].name] = true;
        }
      }
    }

    if (related.length === 0) return '';

    var html = '<div class="related-section">';
    html += '<div class="related-section-title">Related Entities <span class="badge" style="font-size:0.6rem">' + related.length + '</span></div>';
    html += '<div class="related-items">';
    for (var r = 0; r < related.length; r++) {
      html += '<span class="related-item" data-action="toEntity" data-name="' + escapeAttr(related[r].name) + '" title="' + escapeAttr(related[r].reason) + '">';
      html += escapeHtml(related[r].name);
      html += '</span>';
    }
    html += '</div>';
    html += '</div>';

    return html;
  }

  // --- Related Patterns ---
  function renderRelatedPatterns(entity, dataLoader) {
    if (!dataLoader) return '';

    var patData = dataLoader.get('patterns');
    if (!patData || !patData.patterns) return '';

    var patterns = patData.patterns;
    var related = [];

    for (var i = 0; i < patterns.length; i++) {
      var pat = patterns[i];
      var entities = pat.related_entities || [];
      if (entities.indexOf(entity.name) !== -1) {
        related.push(pat.name);
      }
    }

    if (related.length === 0) return '';

    var html = '<div class="related-section">';
    html += '<div class="related-section-title">Related Patterns <span class="badge" style="font-size:0.6rem">' + related.length + '</span></div>';
    html += '<div class="related-items">';
    for (var r = 0; r < related.length; r++) {
      var fmtName = related[r].replace(/_/g, ' ').replace(/\b\w/g, function(c) { return c.toUpperCase(); });
      html += '<span class="related-item" data-action="toPattern" data-name="' + escapeAttr(related[r]) + '">';
      html += escapeHtml(fmtName);
      html += '</span>';
    }
    html += '</div>';
    html += '</div>';

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
