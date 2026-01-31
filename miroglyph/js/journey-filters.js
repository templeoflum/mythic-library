// Journey Mapper - Motif Filtering Logic
// Filters motifs based on node's evidence markers and Thompson category mappings

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  // Thompson category descriptions for UI
  const THOMPSON_CATEGORIES = {
    'A': 'Mythological Motifs',
    'B': 'Animals',
    'C': 'Tabu',
    'D': 'Magic',
    'E': 'The Dead',
    'F': 'Marvels',
    'G': 'Ogres',
    'H': 'Tests',
    'J': 'The Wise and the Foolish',
    'K': 'Deceptions',
    'L': 'Reversal of Fortune',
    'M': 'Ordaining the Future',
    'N': 'Chance and Fate',
    'P': 'Society',
    'Q': 'Rewards and Punishments',
    'R': 'Captives and Fugitives',
    'S': 'Unnatural Cruelty',
    'T': 'Sex',
    'U': 'The Nature of Life',
    'V': 'Religion',
    'W': 'Traits of Character',
    'X': 'Humor',
    'Z': 'Miscellaneous Groups of Motifs'
  };

  /**
   * Get filtered motifs for a node based on its evidence markers
   * @param {Object} nodeTemplate - The node template from node_templates.json
   * @param {Object} patternsData - The patterns catalog data
   * @returns {Object} - { primary: [], secondary: [], all: [] }
   */
  function getFilteredMotifs(nodeTemplate, patternsData) {
    if (!nodeTemplate || !nodeTemplate.evidence_markers || !patternsData || !patternsData.motifs) {
      return { primary: [], secondary: [], all: [] };
    }

    var markers = nodeTemplate.evidence_markers;
    var thompsonPrimary = markers.thompson_primary || [];
    var thompsonSecondary = markers.thompson_secondary || [];
    var allMotifs = patternsData.motifs;

    var primary = [];
    var secondary = [];

    // Iterate through all motifs and categorize by Thompson category
    Object.keys(allMotifs).forEach(function(code) {
      var motif = allMotifs[code];
      var category = motif.category || code.charAt(0);

      var motifObj = {
        code: code,
        label: motif.label,
        category: category,
        categoryName: THOMPSON_CATEGORIES[category] || 'Unknown'
      };

      if (thompsonPrimary.indexOf(category) !== -1) {
        motifObj.markerType = 'primary';
        motifObj.markerName = markers.primary_name;
        primary.push(motifObj);
      } else if (thompsonSecondary.indexOf(category) !== -1) {
        motifObj.markerType = 'secondary';
        motifObj.markerName = markers.secondary_name;
        secondary.push(motifObj);
      }
    });

    // Sort by code
    primary.sort(function(a, b) { return a.code.localeCompare(b.code); });
    secondary.sort(function(a, b) { return a.code.localeCompare(b.code); });

    return {
      primary: primary,
      secondary: secondary,
      all: primary.concat(secondary)
    };
  }

  /**
   * Search/filter motifs by query
   * @param {Array} motifs - Array of motif objects
   * @param {string} query - Search query
   * @returns {Array} - Filtered motifs
   */
  function searchMotifs(motifs, query) {
    if (!query || !query.trim()) return motifs;

    var q = query.toLowerCase().trim();
    return motifs.filter(function(m) {
      return m.code.toLowerCase().indexOf(q) !== -1 ||
             m.label.toLowerCase().indexOf(q) !== -1 ||
             (m.categoryName && m.categoryName.toLowerCase().indexOf(q) !== -1);
    });
  }

  /**
   * Filter archetypes by search query
   * @param {Array} archetypes - Array of archetype objects
   * @param {string} query - Search query
   * @returns {Array} - Filtered archetypes
   */
  function searchArchetypes(archetypes, query) {
    if (!query || !query.trim()) return archetypes;

    var q = query.toLowerCase().trim();
    return archetypes.filter(function(a) {
      return (a.name && a.name.toLowerCase().indexOf(q) !== -1) ||
             (a.id && a.id.toLowerCase().indexOf(q) !== -1) ||
             (a.tradition && a.tradition.toLowerCase().indexOf(q) !== -1);
    });
  }

  /**
   * Filter entities by search query
   * @param {Array} entities - Array of entity objects
   * @param {string} query - Search query
   * @returns {Array} - Filtered entities
   */
  function searchEntities(entities, query) {
    if (!query || !query.trim()) return entities;

    var q = query.toLowerCase().trim();
    return entities.filter(function(e) {
      return (e.name && e.name.toLowerCase().indexOf(q) !== -1) ||
             (e.primary_tradition && e.primary_tradition.toLowerCase().indexOf(q) !== -1) ||
             (e.type && e.type.toLowerCase().indexOf(q) !== -1);
    });
  }

  /**
   * Get a random item from an array
   * @param {Array} arr - Array to pick from
   * @returns {*} - Random item or null
   */
  function getRandomItem(arr) {
    if (!arr || arr.length === 0) return null;
    return arr[Math.floor(Math.random() * arr.length)];
  }

  /**
   * Get suggested archetypes for a node (top ranked by affinity)
   * @param {string} nodeId - The node ID
   * @param {Object} affinities - Archetype affinities data
   * @param {number} limit - Max number to return
   * @returns {Array} - Array of archetype rankings
   */
  function getSuggestedArchetypes(nodeId, affinities, limit) {
    limit = limit || 8;
    if (!affinities || !affinities.node_rankings || !affinities.node_rankings[nodeId]) {
      return [];
    }
    return affinities.node_rankings[nodeId].slice(0, limit);
  }

  /**
   * Get suggested entities for a node (those mapped to this node)
   * @param {string} nodeId - The node ID
   * @param {Object} entitiesData - Entities catalog data
   * @param {number} limit - Max number to return
   * @returns {Array} - Array of entities
   */
  function getSuggestedEntities(nodeId, entitiesData, limit) {
    limit = limit || 8;
    if (!entitiesData || !entitiesData.entities) {
      return [];
    }

    var matching = entitiesData.entities.filter(function(e) {
      if (!e.nearest_node) return false;
      var nearestId = typeof e.nearest_node === 'object' ? e.nearest_node.node_id : e.nearest_node;
      return nearestId === nodeId;
    });

    // Sort by total mentions (popularity)
    matching.sort(function(a, b) {
      return (b.total_mentions || 0) - (a.total_mentions || 0);
    });

    return matching.slice(0, limit);
  }

  /**
   * Get Thompson category info
   * @param {string} category - Single letter category
   * @returns {Object} - { code, name }
   */
  function getThompsonCategory(category) {
    return {
      code: category,
      name: THOMPSON_CATEGORIES[category] || 'Unknown'
    };
  }

  // Export
  window.MiroGlyph.journeyFilters = {
    getFilteredMotifs: getFilteredMotifs,
    searchMotifs: searchMotifs,
    searchArchetypes: searchArchetypes,
    searchEntities: searchEntities,
    getRandomItem: getRandomItem,
    getSuggestedArchetypes: getSuggestedArchetypes,
    getSuggestedEntities: getSuggestedEntities,
    getThompsonCategory: getThompsonCategory,
    THOMPSON_CATEGORIES: THOMPSON_CATEGORIES
  };
})();
