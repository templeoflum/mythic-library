// Mythic System Explorer — Mini Map
// Compact read-only SVG node map for the Chronicle patterns sidebar

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var nodes = window.MiroGlyph.nodes;
  var NODES = nodes.NODES;
  var NONTION = nodes.NONTION;
  var calculatePositions = nodes.calculatePositions;

  var svgEl = null;
  var nodesGroup = null;
  var positions = {};

  var NS = 'http://www.w3.org/2000/svg';
  var ASSUMED_WIDTH = 280;
  var NODE_RADIUS = 12;
  var NONTION_RADIUS = 14;

  function render(containerEl, options) {
    if (!containerEl) return;

    var opts = options || {};
    var width = opts.width || ASSUMED_WIDTH;
    var height = opts.height || ASSUMED_WIDTH;

    // Clear previous content
    containerEl.innerHTML = '';

    // Create SVG element
    svgEl = document.createElementNS(NS, 'svg');
    svgEl.setAttribute('viewBox', '0 0 ' + width + ' ' + height);
    svgEl.setAttribute('width', '100%');
    svgEl.setAttribute('height', '100%');
    svgEl.classList.add('mini-map-svg');
    containerEl.appendChild(svgEl);

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

    var g = document.createElementNS(NS, 'g');
    g.classList.add('minimap-node');
    g.setAttribute('data-node-id', nodeId);

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

  window.MiroGlyph.miniMap = {
    render: render,
    highlightArc: highlightArc,
    highlightNodes: highlightNodes
  };
})();
