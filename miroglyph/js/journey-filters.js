// Journey Mapper - Search and Selection Logic
// Provides search/filter functions for archetypes, entities, and motifs
// Motifs are now free choice (any motif in any position), no evidence marker filtering

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
             (m.categoryName && m.categoryName.toLowerCase().indexOf(q) !== -1) ||
             (m.category && THOMPSON_CATEGORIES[m.category] &&
              THOMPSON_CATEGORIES[m.category].toLowerCase().indexOf(q) !== -1);
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
    searchMotifs: searchMotifs,
    searchArchetypes: searchArchetypes,
    searchEntities: searchEntities,
    getRandomItem: getRandomItem,
    getThompsonCategory: getThompsonCategory,
    THOMPSON_CATEGORIES: THOMPSON_CATEGORIES
  };
})();
