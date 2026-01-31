// Mythic System Explorer — Card Renderer
// Shared rendering utilities for archetype and entity cards

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var AXIS_SHORT = [
    'Ord-Chaos', 'Cre-Dest', 'Light-Shadow', 'Act-Recep',
    'Ind-Coll', 'Asc-Desc', 'Sta-Trans', 'Vol-Fated'
  ];

  // --- Sparkline ---

  function renderSparkline(coordinates) {
    if (!coordinates || coordinates.length !== 8) return '';

    var html = '<div class="sparkline">';
    for (var i = 0; i < 8; i++) {
      var pct = Math.round(coordinates[i] * 100);
      html += '<div class="sparkline-bar" style="height:' + pct + '%"></div>';
    }
    html += '</div>';
    return html;
  }

  // --- Node Badge ---

  function renderNodeBadge(nodeId) {
    if (!nodeId) return '';

    if (nodeId === '\u2205') {
      return '<span class="node-badge" style="background:rgba(245,158,11,0.2);color:#fbbf24">' +
        '\u2205' +
      '</span>';
    }

    var arc = nodeId.charAt(0);
    var cssClass = 'node-badge';
    if (arc === 'D' || arc === 'R' || arc === 'E') {
      cssClass += ' node-badge-' + arc;
    }

    return '<span class="' + cssClass + '">' + escapeHtml(nodeId) + '</span>';
  }

  // --- Arc Color Lookup ---

  function getArcColor(nodeId) {
    if (!nodeId) return '';
    if (nodeId === '\u2205') return '#f59e0b';

    var arc = nodeId.charAt(0);
    if (arc === 'D') return '#8b5cf6';
    if (arc === 'R') return '#3b82f6';
    if (arc === 'E') return '#10b981';
    return '';
  }

  // --- Archetype Card ---

  function renderArchetypeCard(archetype) {
    var a = archetype;
    var borderColor = '';
    if (a.nearest_nodes && a.nearest_nodes.length > 0) {
      borderColor = getArcColor(a.nearest_nodes[0].node_id);
    }

    var html = '<div class="arch-card" data-id="' + escapeAttr(a.id) + '" tabindex="0"';
    if (borderColor) {
      html += ' style="border-left-color:' + borderColor + '"';
    }
    html += '>';

    // Header: name + system badge
    html += '<div class="arch-card-header">';
    html += '<span class="arch-card-name">' + escapeHtml(a.name) + '</span>';
    if (a.system) {
      html += '<span class="badge badge-system">' + escapeHtml(a.system) + '</span>';
    }
    html += '</div>';

    // Description (truncated via CSS)
    if (a.description) {
      html += '<div class="arch-card-desc">' + escapeHtml(a.description) + '</div>';
    }

    // Sparkline
    html += renderSparkline(a.coordinates);

    // Top 3 primordials
    if (a.primordials && a.primordials.length > 0) {
      html += '<div class="arch-card-prims">';
      var primCount = Math.min(3, a.primordials.length);
      for (var i = 0; i < primCount; i++) {
        var name = (a.primordials[i].id || '').replace('primordial:', '');
        var weight = (a.primordials[i].weight || 0).toFixed(2);
        html += '<span class="arch-card-prim">' + escapeHtml(name) + ' ' + weight + '</span>';
      }
      html += '</div>';
    }

    // Top 3 nearest nodes
    if (a.nearest_nodes && a.nearest_nodes.length > 0) {
      html += '<div class="arch-card-nodes">';
      var nodeCount = Math.min(3, a.nearest_nodes.length);
      for (var j = 0; j < nodeCount; j++) {
        html += renderNodeBadge(a.nearest_nodes[j].node_id);
      }
      html += '</div>';
    }

    html += '</div>';
    return html;
  }

  // --- Entity Card ---

  function renderEntityCard(entity) {
    var e = entity;
    var borderColor = '';
    var nearestNodeId = null;

    if (e.nearest_node) {
      if (typeof e.nearest_node === 'object') {
        nearestNodeId = e.nearest_node.node_id;
      } else {
        nearestNodeId = e.nearest_node;
      }
      borderColor = getArcColor(nearestNodeId);
    }

    var html = '<div class="entity-card" data-name="' + escapeAttr(e.name) + '" tabindex="0"';
    if (borderColor) {
      html += ' style="border-left-color:' + borderColor + '"';
    }
    html += '>';

    // Header: name + type badge + tradition badge
    html += '<div class="entity-card-header">';
    html += '<span class="entity-card-name">' + escapeHtml(e.name) + '</span>';
    if (e.type) {
      html += '<span class="badge badge-system">' + escapeHtml(e.type) + '</span>';
    }
    if (e.primary_tradition) {
      html += '<span class="badge">' + escapeHtml(e.primary_tradition) + '</span>';
    }
    html += '</div>';

    // Summary
    var mentions = e.total_mentions || 0;
    var texts = e.text_count || 0;
    var traditions = e.tradition_count || 0;
    html += '<div class="entity-card-summary">' +
      mentions + ' mentions, ' + texts + ' texts, ' + traditions + ' traditions' +
    '</div>';

    // Sparkline
    html += renderSparkline(e.coordinates);

    // Mapping info with fidelity and distance badges
    html += '<div class="entity-card-mapping">';
    if (e.mapping && e.mapping.archetype_name) {
      html += '<span class="entity-card-mapping-label">' +
        escapeHtml(e.mapping.archetype_name) +
      '</span>';
      if (e.mapping.score != null) {
        html += ' <span class="badge badge-system">' + e.mapping.score.toFixed(2) + '</span>';
      }
      // Fidelity badge
      if (e.mapping.fidelity != null) {
        var fidelityClass = getFidelityClass(e.mapping.fidelity);
        html += ' <span class="fidelity-badge ' + fidelityClass + '" title="Mapping Fidelity">' +
          e.mapping.fidelity.toFixed(2) + '</span>';
      }
    } else if (e.mapping && e.mapping.archetype_id) {
      html += '<span class="entity-card-mapping-label">' +
        escapeHtml(e.mapping.archetype_id) +
      '</span>';
    } else {
      html += '<span class="badge-unmapped">Unmapped</span>';
    }
    html += '</div>';

    // Distance badge (if available)
    if (e.mapping && e.mapping.distance != null) {
      html += '<div class="entity-card-distance" style="margin-top:4px">';
      html += '<span class="distance-badge" title="ACP Distance">d=' + e.mapping.distance.toFixed(3) + '</span>';
      html += '</div>';
    }

    // Nearest node badge
    if (nearestNodeId) {
      html += '<div class="arch-card-nodes">' + renderNodeBadge(nearestNodeId) + '</div>';
    }

    html += '</div>';
    return html;
  }

  // Helper function for fidelity class
  function getFidelityClass(fidelity) {
    if (fidelity == null) return '';
    if (fidelity >= 0.8) return 'fidelity-high';
    if (fidelity >= 0.5) return 'fidelity-medium';
    return 'fidelity-low';
  }

  // --- Format Pattern Name ---

  function formatPatternName(name) {
    if (!name) return '';
    return name.replace(/_/g, ' ').replace(/\b\w/g, function(c) {
      return c.toUpperCase();
    });
  }

  // --- Utilities ---

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

  window.MiroGlyph.cardRenderer = {
    renderSparkline: renderSparkline,
    renderNodeBadge: renderNodeBadge,
    renderArchetypeCard: renderArchetypeCard,
    renderEntityCard: renderEntityCard,
    formatPatternName: formatPatternName,
    getArcColor: getArcColor
  };
})();
