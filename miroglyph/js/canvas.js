// MiroGlyph v4 - Canvas Rendering (SVG)

(function() {
  const { ARCS, NODES, NONTION, calculatePositions, getNode } = window.MiroGlyph.nodes;

  // Canvas state
  let svg = null;
  let positions = {};
  let centerX = 0;
  let centerY = 0;

  // Layer groups for proper z-ordering
  let traversalsGroup = null;
  let previewGroup = null;
  let nodesGroup = null;

  // Initialize the SVG canvas
  function init() {
    svg = document.getElementById('canvas');
    if (!svg) return;

    // Get dimensions
    const rect = svg.getBoundingClientRect();
    centerX = rect.width / 2;
    centerY = rect.height / 2;

    // Calculate positions based on canvas size
    const minDim = Math.min(rect.width, rect.height);
    const innerRadius = minDim * 0.15;
    const ringSpacing = minDim * 0.12;

    positions = calculatePositions(centerX, centerY, innerRadius, ringSpacing);

    // Clear and set viewBox
    svg.innerHTML = '';
    svg.setAttribute('viewBox', `0 0 ${rect.width} ${rect.height}`);

    // Create layer groups (order matters for z-index)
    drawRingGuides(innerRadius, ringSpacing);
    traversalsGroup = createGroup('traversals-layer');
    previewGroup = createGroup('preview-layer');
    nodesGroup = createGroup('nodes-layer');

    // Draw all nodes
    drawNodes();

    // Handle resize
    window.addEventListener('resize', debounce(handleResize, 250));
  }

  // Create SVG group element
  function createGroup(id) {
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.id = id;
    svg.appendChild(g);
    return g;
  }

  // Draw circular ring guides
  function drawRingGuides(innerRadius, ringSpacing) {
    const guideGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    guideGroup.id = 'ring-guides';

    for (let i = 0; i < 3; i++) {
      const radius = innerRadius + (i * ringSpacing);
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('cx', centerX);
      circle.setAttribute('cy', centerY);
      circle.setAttribute('r', radius);
      circle.classList.add('ring-guide');
      guideGroup.appendChild(circle);
    }

    svg.appendChild(guideGroup);
  }

  // Draw all 19 nodes
  function drawNodes() {
    // Draw 18 nodes
    NODES.forEach(node => {
      drawNode(node.id, node);
    });

    // Draw Nontion at center
    drawNode('∅', NONTION);
  }

  // Draw a single node
  function drawNode(nodeId, nodeData) {
    const pos = positions[nodeId];
    if (!pos) return;

    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.classList.add('node-group');
    g.setAttribute('data-node-id', nodeId);

    // Determine color
    let color;
    if (nodeId === '∅') {
      color = NONTION.color;
    } else {
      color = nodeData.arc.color;
    }

    // Node circle
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', pos.x);
    circle.setAttribute('cy', pos.y);
    circle.setAttribute('r', nodeId === '∅' ? 22 : 18);
    circle.setAttribute('fill', color);
    circle.setAttribute('stroke', color);
    circle.classList.add('node-circle');
    g.appendChild(circle);

    // Node ID label
    const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    label.setAttribute('x', pos.x);
    label.setAttribute('y', pos.y + 5);
    label.classList.add('node-label');
    label.textContent = nodeId;
    g.appendChild(label);

    // Title label (below node)
    if (nodeId !== '∅') {
      const titleLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      titleLabel.setAttribute('x', pos.x);
      titleLabel.setAttribute('y', pos.y + 34);
      titleLabel.classList.add('node-title-label');
      const title = nodeData.title.length > 18
        ? nodeData.title.substring(0, 16) + '...'
        : nodeData.title;
      titleLabel.textContent = title;
      g.appendChild(titleLabel);
    }

    nodesGroup.appendChild(g);
  }

  // Draw a traversal path
  function drawTraversal(sequence, color, isPreview = false) {
    if (sequence.length < 2) return;

    const targetGroup = isPreview ? previewGroup : traversalsGroup;

    // Create path element for smooth curves
    const pathData = buildPathData(sequence);

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', pathData);
    path.setAttribute('stroke', color);
    path.classList.add('traversal-line');
    if (isPreview) {
      path.classList.add('preview');
    }

    targetGroup.appendChild(path);
  }

  // Build SVG path data from sequence
  function buildPathData(sequence) {
    const points = sequence.map(nodeId => positions[nodeId]).filter(p => p);
    if (points.length < 2) return '';

    // Simple line path
    let d = `M ${points[0].x} ${points[0].y}`;
    for (let i = 1; i < points.length; i++) {
      d += ` L ${points[i].x} ${points[i].y}`;
    }

    return d;
  }

  // Clear all traversals
  function clearTraversals() {
    if (traversalsGroup) traversalsGroup.innerHTML = '';
  }

  // Clear preview
  function clearPreview() {
    if (previewGroup) previewGroup.innerHTML = '';
  }

  // Mark node as in sequence
  function markNodeInSequence(nodeId, inSequence) {
    const group = nodesGroup.querySelector(`[data-node-id="${nodeId}"]`);
    if (group) {
      if (inSequence) {
        group.classList.add('in-sequence');
      } else {
        group.classList.remove('in-sequence');
      }
    }
  }

  // Clear all sequence marks
  function clearSequenceMarks() {
    nodesGroup.querySelectorAll('.node-group.in-sequence').forEach(g => {
      g.classList.remove('in-sequence');
    });
  }

  // Get node ID from click event
  function getNodeFromEvent(event) {
    const target = event.target.closest('.node-group');
    if (target) {
      return target.getAttribute('data-node-id');
    }
    return null;
  }

  // Handle resize
  function handleResize() {
    init();
    // Trigger redraw of traversals
    if (window.MiroGlyph.paths) {
      window.MiroGlyph.paths.redraw();
    }
  }

  // Debounce helper
  function debounce(fn, delay) {
    let timeout;
    return function(...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  // Get position for a node
  function getPosition(nodeId) {
    return positions[nodeId];
  }

  // Select a node — highlight it and dim all others
  function selectNode(nodeId) {
    if (!nodesGroup) return;
    var allGroups = nodesGroup.querySelectorAll('.node-group');
    for (var i = 0; i < allGroups.length; i++) {
      var g = allGroups[i];
      var gId = g.getAttribute('data-node-id');
      if (gId === nodeId) {
        g.classList.add('selected');
        g.classList.remove('dimmed');
        // Set glow color from the node's arc color
        var node = window.MiroGlyph.nodes.getNode(nodeId);
        var color = '';
        if (nodeId === '\u2205') {
          color = node ? node.color : '#f59e0b';
        } else {
          color = node && node.arc ? node.arc.color : '#6366f1';
        }
        g.style.setProperty('--glow-color', color);
      } else {
        g.classList.remove('selected');
        g.classList.add('dimmed');
      }
    }
  }

  // Clear all selection and dimming state
  function clearSelection() {
    if (!nodesGroup) return;
    var allGroups = nodesGroup.querySelectorAll('.node-group');
    for (var i = 0; i < allGroups.length; i++) {
      allGroups[i].classList.remove('selected');
      allGroups[i].classList.remove('dimmed');
      allGroups[i].style.removeProperty('--glow-color');
    }
  }

  // Export canvas functions
  window.MiroGlyph.canvas = {
    init,
    drawTraversal,
    clearTraversals,
    clearPreview,
    markNodeInSequence,
    clearSequenceMarks,
    getNodeFromEvent,
    getPosition,
    selectNode,
    clearSelection
  };
})();
