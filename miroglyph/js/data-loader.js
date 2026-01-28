// MiroGlyph — Shared Data Loader
// Fetches and caches JSON files for all tabs

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  const cache = {};
  const loading = {};

  async function load(key, url) {
    if (cache[key]) return cache[key];
    if (loading[key]) return loading[key];

    loading[key] = fetch(url).then(async (res) => {
      if (!res.ok) throw new Error(`Failed to load ${url}: ${res.status}`);
      const data = await res.json();
      cache[key] = data;
      delete loading[key];
      return data;
    }).catch(err => {
      delete loading[key];
      console.warn(`DataLoader: ${key} failed:`, err.message);
      return null;
    });

    return loading[key];
  }

  function get(key) {
    return cache[key] || null;
  }

  function isLoaded(key) {
    return key in cache;
  }

  window.MiroGlyph.dataLoader = { load, get, isLoaded };
})();
