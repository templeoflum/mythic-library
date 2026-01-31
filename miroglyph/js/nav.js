// Mythic System Explorer — Cross-Navigation Module
// Provides toNode/toArchetype/toEntity/toPattern/back for linking across views

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var history = [];
  var suppressHistory = false;

  // Breadcrumb trail - last N items viewed with their display names
  var breadcrumbs = [];
  var MAX_BREADCRUMBS = 5;

  function currentRoute() {
    return window.location.hash.slice(1) || 'atlas';
  }

  function pushRoute(route) {
    if (!suppressHistory) {
      history.push(currentRoute());
    }
    window.location.hash = route;
  }

  function addBreadcrumb(type, id, displayName) {
    // Don't add duplicates of the last item
    if (breadcrumbs.length > 0) {
      var last = breadcrumbs[breadcrumbs.length - 1];
      if (last.type === type && last.id === id) {
        return;
      }
    }

    breadcrumbs.push({
      type: type,
      id: id,
      name: displayName || id
    });

    // Keep only last N items
    if (breadcrumbs.length > MAX_BREADCRUMBS) {
      breadcrumbs.shift();
    }

    // Dispatch event for UI update
    window.dispatchEvent(new CustomEvent('breadcrumbsUpdated', {
      detail: { breadcrumbs: breadcrumbs }
    }));
  }

  function getBreadcrumbs() {
    return breadcrumbs.slice();
  }

  function clearBreadcrumbs() {
    breadcrumbs = [];
    window.dispatchEvent(new CustomEvent('breadcrumbsUpdated', {
      detail: { breadcrumbs: breadcrumbs }
    }));
  }

  // Navigate to a node in the Atlas view and open its drawer
  function toNode(nodeId, displayName) {
    addBreadcrumb('node', nodeId, displayName || nodeId);
    pushRoute('atlas/' + nodeId);
  }

  // Navigate to an archetype detail in the Codex
  function toArchetype(archetypeId, displayName) {
    addBreadcrumb('archetype', archetypeId, displayName || archetypeId);
    pushRoute('codex/archetype/' + encodeURIComponent(archetypeId));
  }

  // Navigate to an entity detail in the Codex
  function toEntity(entityName) {
    addBreadcrumb('entity', entityName, entityName);
    pushRoute('codex/entity/' + encodeURIComponent(entityName));
  }

  // Navigate to a pattern in the Chronicle
  function toPattern(patternName, displayName) {
    var fmtName = displayName || patternName.replace(/_/g, ' ').replace(/\b\w/g, function(c) { return c.toUpperCase(); });
    addBreadcrumb('pattern', patternName, fmtName);
    pushRoute('chronicle/pattern/' + encodeURIComponent(patternName));
  }

  // Navigate to the validation sub-view
  function toValidation() {
    pushRoute('chronicle/validation');
  }

  // Navigate to a breadcrumb item
  function toBreadcrumb(item) {
    if (item.type === 'node') toNode(item.id, item.name);
    else if (item.type === 'archetype') toArchetype(item.id, item.name);
    else if (item.type === 'entity') toEntity(item.id);
    else if (item.type === 'pattern') toPattern(item.id, item.name);
  }

  // Go back to previous state
  function back() {
    if (history.length > 0) {
      suppressHistory = true;
      window.location.hash = history.pop();
      suppressHistory = false;
    } else {
      // Default: go to view root
      var view = currentRoute().split('/')[0] || 'atlas';
      window.location.hash = view;
    }
  }

  // Parse a hash route into segments
  // e.g. "codex/archetype/arch:GR-APOLLO" → { view: "codex", subview: "archetype", id: "arch:GR-APOLLO" }
  function parseRoute(hash) {
    var parts = (hash || '').split('/');
    return {
      view: parts[0] || 'atlas',
      subview: parts[1] || null,
      id: parts.slice(2).join('/') || null  // rejoin in case id has slashes
    };
  }

  // Random discovery - pick a random item of a given type
  function surpriseMe(type) {
    var dataLoader = window.MiroGlyph.dataLoader;
    if (!dataLoader) return;

    var items = [];

    if (type === 'archetype') {
      var archData = dataLoader.get('archetypes');
      if (archData && archData.archetypes) {
        items = archData.archetypes;
        if (items.length > 0) {
          var rand = items[Math.floor(Math.random() * items.length)];
          toArchetype(rand.id, rand.name);
        }
      }
    } else if (type === 'entity') {
      var entData = dataLoader.get('entities');
      if (entData && entData.entities) {
        items = entData.entities;
        if (items.length > 0) {
          var rand = items[Math.floor(Math.random() * items.length)];
          toEntity(rand.name);
        }
      }
    } else if (type === 'pattern') {
      var patData = dataLoader.get('patterns');
      if (patData && patData.patterns) {
        items = patData.patterns;
        if (items.length > 0) {
          var rand = items[Math.floor(Math.random() * items.length)];
          toPattern(rand.name);
        }
      }
    } else if (type === 'node') {
      var nodes = window.MiroGlyph.nodes;
      if (nodes && nodes.NODES) {
        items = nodes.NODES;
        if (items.length > 0) {
          var rand = items[Math.floor(Math.random() * items.length)];
          toNode(rand.id, rand.title);
        }
      }
    } else if (type === 'motif') {
      var patData = dataLoader.get('patterns');
      if (patData && patData.motifs) {
        var codes = Object.keys(patData.motifs);
        if (codes.length > 0) {
          var randCode = codes[Math.floor(Math.random() * codes.length)];
          // Navigate to codex motifs with search
          window.location.hash = 'codex';
          setTimeout(function() {
            var viewCodex = window.MiroGlyph.viewCodex;
            if (viewCodex && viewCodex.switchSubTab) {
              viewCodex.switchSubTab('motifs');
              var searchInput = document.querySelector('#codex-search');
              if (searchInput) {
                searchInput.value = randCode;
                searchInput.dispatchEvent(new Event('input'));
              }
            }
          }, 100);
        }
      }
    }
  }

  window.MiroGlyph.nav = {
    toNode: toNode,
    toArchetype: toArchetype,
    toEntity: toEntity,
    toPattern: toPattern,
    toValidation: toValidation,
    toBreadcrumb: toBreadcrumb,
    back: back,
    parseRoute: parseRoute,
    currentRoute: currentRoute,
    getBreadcrumbs: getBreadcrumbs,
    clearBreadcrumbs: clearBreadcrumbs,
    surpriseMe: surpriseMe
  };
})();
