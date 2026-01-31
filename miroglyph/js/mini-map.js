// Mythic System Explorer — Mini Map
// Compact interactive SVG node map for the Chronicle patterns sidebar

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var nodes = window.MiroGlyph.nodes;
  var NODES = nodes.NODES;
  var NONTION = nodes.NONTION;
  var calculatePositions = nodes.calculatePositions;

  var svgEl = null;
  var nodesGroup = null;
  var tooltipEl = null;
  var positions = {};
  var onNodeClickCallback = null;
  var onNodeHoverCallback = null;

  var NS = 'http://www.w3.org/2000/svg';
  var ASSUMED_WIDTH = 280;
  var NODE_RADIUS = 12;
  var NONTION_RADIUS = 14;

  function render(containerEl, options) {
    if (!containerEl) return;

    var opts = options || {};
    var width = opts.width || ASSUMED_WIDTH;
    var height = opts.height || ASSUMED_WIDTH;
    onNodeClickCallback = opts.onNodeClick || null;
    onNodeHoverCallback = opts.onNodeHover || null;

    // Clear previous content
    containerEl.innerHTML = '';

    // Create container for positioning
    containerEl.style.position = 'relative';

    // Create SVG element
    svgEl = document.createElementNS(NS, 'svg');
    svgEl.setAttribute('viewBox', '0 0 ' + width + ' ' + height);
    svgEl.setAttribute('width', '100%');
    svgEl.setAttribute('height', '100%');
    svgEl.classList.add('mini-map-svg');
    containerEl.appendChild(svgEl);

    // Create tooltip element
    tooltipEl = document.createElement('div');
    tooltipEl.className = 'minimap-tooltip';
    tooltipEl.style.cssText = 'position:absolute;display:none;background:var(--color-surface-3);color:var(--color-text);padding:4px 8px;border-radius:4px;font-size:0.7rem;pointer-events:none;z-index:10;white-space:nowrap;box-shadow:0 2px 8px rgba(0,0,0,0.3);border:1px solid var(--color-border)';
    containerEl.appendChild(tooltipEl);

    // Calculate layout parameters
    var cx = width / 2;
    var cy = height / 2;
    var innerR = Math.min(width, height) * 0.16;
    var spacing = Math.min(width, height) * 0.13;

    positions = calculatePositions(cx, cy, innerR, spacing);

    // Draw ring guides
    drawRingGuides(cx, cy, innerR, spacing);

    // Draw nodes
    nodesGroup = document.createElementNS(NS, 'g');
    nodesGroup.setAttribute('id', 'minimap-nodes');
    svgEl.appendChild(nodesGroup);

    drawAllNodes();

    // Add event delegation for interactivity
    wireNodeEvents(containerEl);
  }

  function drawRingGuides(cx, cy, innerR, spacing) {
    var guideGroup = document.createElementNS(NS, 'g');

    for (var i = 0; i < 3; i++) {
      var r = innerR + (i * spacing);
      var circle = document.createElementNS(NS, 'circle');
      circle.setAttribute('cx', cx);
      circle.setAttribute('cy', cy);
      circle.setAttribute('r', r);
      circle.classList.add('ring-guide');
      guideGroup.appendChild(circle);
    }

    svgEl.appendChild(guideGroup);
  }

  function drawAllNodes() {
    // Draw 18 nodes
    for (var i = 0; i < NODES.length; i++) {
      drawNode(NODES[i].id, NODES[i].arc.color, NODE_RADIUS);
    }

    // Draw Nontion at center
    drawNode(NONTION.id, NONTION.color, NONTION_RADIUS);
  }

  function drawNode(nodeId, color, radius) {
    var pos = positions[nodeId];
    if (!pos) return;

    // Look up node title
    var nodeData = nodes.getNode ? nodes.getNode(nodeId) : null;
    var nodeTitle = nodeData ? nodeData.title : '';

    var g = document.createElementNS(NS, 'g');
    g.classList.add('minimap-node');
    g.setAttribute('data-node-id', nodeId);
    g.setAttribute('data-node-title', nodeTitle);
    g.style.cursor = 'pointer';

    // Circle
    var circle = document.createElementNS(NS, 'circle');
    circle.setAttribute('cx', pos.x);
    circle.setAttribute('cy', pos.y);
    circle.setAttribute('r', radius);
    circle.setAttribute('fill', color);
    circle.setAttribute('stroke', color);
    circle.setAttribute('stroke-width', '1');
    circle.setAttribute('fill-opacity', '0.35');
    circle.setAttribute('stroke-opacity', '0.7');
    circle.style.transition = 'all 0.15s ease';
    g.appendChild(circle);

    // Label (ID text only)
    var label = document.createElementNS(NS, 'text');
    label.setAttribute('x', pos.x);
    label.setAttribute('y', pos.y + 3.5);
    label.setAttribute('text-anchor', 'middle');
    label.setAttribute('font-size', '8');
    label.setAttribute('font-weight', '600');
    label.setAttribute('fill', '#f1f5f9');
    label.textContent = nodeId;
    g.appendChild(label);

    nodesGroup.appendChild(g);
  }

  function wireNodeEvents(containerEl) {
    // Mouse events for hover tooltip and click
    nodesGroup.addEventListener('mouseenter', function(e) {
      var nodeGroup = e.target.closest('.minimap-node');
      if (!nodeGroup) return;

      var nodeId = nodeGroup.getAttribute('data-node-id');
      var nodeTitle = nodeGroup.getAttribute('data-node-title');

      // Show tooltip
      if (tooltipEl && nodeTitle) {
        tooltipEl.textContent = nodeId + ': ' + nodeTitle;
        tooltipEl.style.display = 'block';
      } else if (tooltipEl) {
        tooltipEl.textContent = nodeId;
        tooltipEl.style.display = 'block';
      }

      // Highlight effect
      var circle = nodeGroup.querySelector('circle');
      if (circle) {
        circle.setAttribute('stroke-width', '2');
        circle.setAttribute('fill-opacity', '0.6');
      }

      if (onNodeHoverCallback) {
        onNodeHoverCallback(nodeId, true);
      }
    }, true);

    nodesGroup.addEventListener('mouseleave', function(e) {
      var nodeGroup = e.target.closest('.minimap-node');
      if (!nodeGroup) return;

      // Hide tooltip
      if (tooltipEl) {
        tooltipEl.style.display = 'none';
      }

      // Remove highlight (restore based on current state)
      var circle = nodeGroup.querySelector('circle');
      if (circle) {
        circle.setAttribute('stroke-width', '1');
        circle.setAttribute('fill-opacity', '0.35');
      }

      if (onNodeHoverCallback) {
        onNodeHoverCallback(nodeGroup.getAttribute('data-node-id'), false);
      }
    }, true);

    nodesGroup.addEventListener('mousemove', function(e) {
      if (tooltipEl && tooltipEl.style.display !== 'none') {
        var rect = containerEl.getBoundingClientRect();
        tooltipEl.style.left = (e.clientX - rect.left + 10) + 'px';
        tooltipEl.style.top = (e.clientY - rect.top - 20) + 'px';
      }
    });

    nodesGroup.addEventListener('click', function(e) {
      var nodeGroup = e.target.closest('.minimap-node');
      if (!nodeGroup) return;

      var nodeId = nodeGroup.getAttribute('data-node-id');

      if (onNodeClickCallback) {
        onNodeClickCallback(nodeId);
      } else {
        // Default behavior: navigate to Atlas view for this node
        var nav = window.MiroGlyph.nav;
        if (nav && nav.toNode) {
          nav.toNode(nodeId);
        }
      }
    });
  }

  // Shared helper: set opacity on a minimap node group
  // state: 'default', 'active', or 'dimmed'
  function setNodeOpacity(g, state) {
    var circle = g.querySelector('circle');
    var text = g.querySelector('text');
    if (!circle || !text) return;

    if (state === 'active') {
      circle.setAttribute('fill-opacity', '0.65');
      circle.setAttribute('stroke-opacity', '1');
      text.setAttribute('fill-opacity', '1');
    } else if (state === 'dimmed') {
      circle.setAttribute('fill-opacity', '0.08');
      circle.setAttribute('stroke-opacity', '0.15');
      text.setAttribute('fill-opacity', '0.2');
    } else {
      circle.setAttribute('fill-opacity', '0.35');
      circle.setAttribute('stroke-opacity', '0.7');
      text.setAttribute('fill-opacity', '1');
    }
  }

  function highlightArc(arcCode) {
    if (!nodesGroup) return;

    var allNodes = nodesGroup.querySelectorAll('.minimap-node');
    for (var i = 0; i < allNodes.length; i++) {
      var g = allNodes[i];
      var id = g.getAttribute('data-node-id');

      if (arcCode === null) {
        setNodeOpacity(g, 'default');
      } else if (id.charAt(0) === arcCode) {
        setNodeOpacity(g, 'active');
      } else {
        setNodeOpacity(g, 'dimmed');
      }
    }
  }

  function highlightNodes(nodeIds) {
    if (!nodesGroup) return;

    var idSet = {};
    if (nodeIds) {
      for (var i = 0; i < nodeIds.length; i++) {
        idSet[nodeIds[i]] = true;
      }
    }

    var allNodes = nodesGroup.querySelectorAll('.minimap-node');
    for (var j = 0; j < allNodes.length; j++) {
      var g = allNodes[j];
      var id = g.getAttribute('data-node-id');

      if (!nodeIds || nodeIds.length === 0) {
        setNodeOpacity(g, 'default');
      } else if (idSet[id]) {
        setNodeOpacity(g, 'active');
      } else {
        setNodeOpacity(g, 'dimmed');
      }
    }
  }

  // Get current positions for external use (e.g., drawing pattern paths)
  function getPositions() {
    return positions;
  }

  // Draw a traversal path on the mini-map
  function drawPath(nodeIds, color, strokeWidth) {
    if (!svgEl || !nodeIds || nodeIds.length < 2) return null;

    var pathGroup = document.createElementNS(NS, 'g');
    pathGroup.classList.add('minimap-path');

    var pathData = '';
    for (var i = 0; i < nodeIds.length; i++) {
      var pos = positions[nodeIds[i]];
      if (!pos) continue;
      pathData += (i === 0 ? 'M' : 'L') + pos.x + ',' + pos.y;
    }

    if (pathData) {
      var path = document.createElementNS(NS, 'path');
      path.setAttribute('d', pathData);
      path.setAttribute('stroke', color || '#fbbf24');
      path.setAttribute('stroke-width', strokeWidth || 2);
      path.setAttribute('fill', 'none');
      path.setAttribute('stroke-linecap', 'round');
      path.setAttribute('stroke-linejoin', 'round');
      path.setAttribute('opacity', '0.7');
      pathGroup.appendChild(path);
    }

    // Insert before nodes so paths appear behind
    svgEl.insertBefore(pathGroup, nodesGroup);
    return pathGroup;
  }

  // Clear all drawn paths
  function clearPaths() {
    if (!svgEl) return;
    var paths = svgEl.querySelectorAll('.minimap-path');
    for (var i = 0; i < paths.length; i++) {
      paths[i].remove();
    }
  }

  window.MiroGlyph.miniMap = {
    render: render,
    highlightArc: highlightArc,
    highlightNodes: highlightNodes,
    getPositions: getPositions,
    drawPath: drawPath,
    clearPaths: clearPaths
  };
})();
