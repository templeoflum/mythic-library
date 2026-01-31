// Mythic System Explorer — Utility Functions
// Shared helper functions for the application

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  /**
   * Ensures a value is an array
   * @param {*} val - Value to convert
   * @returns {Array} - Array (empty if null/undefined)
   */
  function ensureArray(val) {
    if (!val) return [];
    return Array.isArray(val) ? val : [val];
  }

  /**
   * Truncate array with "more" indicator
   * @param {Array} arr - Array to truncate
   * @param {number} limit - Max items to show
   * @param {Function} showMoreFn - Optional callback for "show more" click
   * @returns {Object} - { items: Array, hasMore: boolean, moreCount: number }
   */
  function truncateWithMore(arr, limit, showMoreFn) {
    if (!arr || arr.length <= limit) {
      return { items: arr || [], hasMore: false, moreCount: 0 };
    }
    return {
      items: arr.slice(0, limit),
      hasMore: true,
      moreCount: arr.length - limit,
      showMore: showMoreFn
    };
  }

  /**
   * HTML-escape a string
   * @param {string} str - String to escape
   * @returns {string} - Escaped string
   */
  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /**
   * Escape string for use in HTML attribute
   * @param {string} str - String to escape
   * @returns {string} - Escaped string
   */
  function escapeAttr(str) {
    return (str || '').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  /**
   * Debounce function execution
   * @param {Function} fn - Function to debounce
   * @param {number} delay - Delay in milliseconds
   * @returns {Function} - Debounced function
   */
  function debounce(fn, delay) {
    var timer = null;
    return function() {
      var context = this;
      var args = arguments;
      clearTimeout(timer);
      timer = setTimeout(function() {
        fn.apply(context, args);
      }, delay);
    };
  }

  /**
   * Format a number with commas
   * @param {number} num - Number to format
   * @returns {string} - Formatted string
   */
  function formatNumber(num) {
    if (num == null) return '';
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }

  /**
   * Get fidelity class based on value
   * @param {number} fidelity - Fidelity value (0-1)
   * @returns {string} - CSS class name
   */
  function getFidelityClass(fidelity) {
    if (fidelity == null) return '';
    if (fidelity >= 0.8) return 'fidelity-high';
    if (fidelity >= 0.5) return 'fidelity-medium';
    return 'fidelity-low';
  }

  /**
   * Get fidelity label
   * @param {number} fidelity - Fidelity value (0-1)
   * @returns {string} - Label text
   */
  function getFidelityLabel(fidelity) {
    if (fidelity == null) return 'Unknown';
    if (fidelity >= 0.8) return 'High';
    if (fidelity >= 0.5) return 'Medium';
    return 'Low';
  }

  /**
   * Deep clone an object
   * @param {Object} obj - Object to clone
   * @returns {Object} - Cloned object
   */
  function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
  }

  /**
   * Generate a simple UUID
   * @returns {string} - UUID string
   */
  function uuid() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16 | 0;
      var v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  /**
   * Capitalize first letter of each word
   * @param {string} str - String to capitalize
   * @returns {string} - Capitalized string
   */
  function titleCase(str) {
    if (!str) return '';
    return str.replace(/\b\w/g, function(c) {
      return c.toUpperCase();
    });
  }

  /**
   * Convert snake_case to Title Case
   * @param {string} str - String in snake_case
   * @returns {string} - Title Case string
   */
  function snakeToTitle(str) {
    if (!str) return '';
    return str.replace(/_/g, ' ').replace(/\b\w/g, function(c) {
      return c.toUpperCase();
    });
  }

  window.MiroGlyph.utils = {
    ensureArray: ensureArray,
    truncateWithMore: truncateWithMore,
    escapeHtml: escapeHtml,
    escapeAttr: escapeAttr,
    debounce: debounce,
    formatNumber: formatNumber,
    getFidelityClass: getFidelityClass,
    getFidelityLabel: getFidelityLabel,
    deepClone: deepClone,
    uuid: uuid,
    titleCase: titleCase,
    snakeToTitle: snakeToTitle
  };
})();
