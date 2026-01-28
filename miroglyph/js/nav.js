// Mythic System Explorer — Cross-Navigation Module
// Provides toNode/toArchetype/toEntity/toPattern/back for linking across views

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  const history = [];
  let suppressHistory = false;

  function currentRoute() {
    return window.location.hash.slice(1) || 'atlas';
  }

  function pushRoute(route) {
    if (!suppressHistory) {
      history.push(currentRoute());
    }
    window.location.hash = route;
  }

  // Navigate to a node in the Atlas view and open its drawer
  function toNode(nodeId) {
    pushRoute('atlas/' + nodeId);
  }

  // Navigate to an archetype detail in the Codex
  function toArchetype(archetypeId) {
    pushRoute('codex/archetype/' + encodeURIComponent(archetypeId));
  }

  // Navigate to an entity detail in the Codex
  function toEntity(entityName) {
    pushRoute('codex/entity/' + encodeURIComponent(entityName));
  }

  // Navigate to a pattern in the Chronicle
  function toPattern(patternName) {
    pushRoute('chronicle/pattern/' + encodeURIComponent(patternName));
  }

  // Navigate to the validation sub-view
  function toValidation() {
    pushRoute('chronicle/validation');
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

  window.MiroGlyph.nav = {
    toNode: toNode,
    toArchetype: toArchetype,
    toEntity: toEntity,
    toPattern: toPattern,
    toValidation: toValidation,
    back: back,
    parseRoute: parseRoute,
    currentRoute: currentRoute
  };
})();
