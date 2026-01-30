// MiroGlyph v4 - Storage (LocalStorage + JSON Import/Export)

(function() {
  const STORAGE_KEY = 'miroglyph_v4_data';
  const CONFIG_KEY = 'miroglyph_v4_config';

  // Default empty state
  const defaultState = {
    version: '4.0.0',
    paths: [],
    groups: []
  };

  // Load data from LocalStorage
  function load() {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      if (data) {
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed.paths)) {
          return {
            version: parsed.version || '4.0.0',
            paths: parsed.paths || [],
            groups: parsed.groups || []
          };
        }
      }
    } catch (e) {
      console.error('Failed to load from LocalStorage:', e);
    }
    return { ...defaultState };
  }

  // Save data to LocalStorage
  function save(data) {
    try {
      const toSave = {
        version: '4.0.0',
        lastModified: new Date().toISOString(),
        paths: data.paths || [],
        groups: data.groups || []
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave));
      return true;
    } catch (e) {
      console.error('Failed to save to LocalStorage:', e);
      return false;
    }
  }

  // Export as JSON file
  function exportJSON(data) {
    const exportData = {
      miroglyph_version: '4.0.0',
      exported_at: new Date().toISOString(),
      paths: data.paths,
      groups: data.groups || []
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `miroglyph_traversals_${formatDate(new Date())}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // Import from JSON file
  function importJSON(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target.result);

          // Handle both old and new format
          const paths = data.paths || [];

          const normalized = {
            version: data.miroglyph_version || '4.0.0',
            paths: paths,
            groups: data.groups || []
          };

          resolve(normalized);
        } catch (err) {
          reject(new Error('Failed to parse JSON: ' + err.message));
        }
      };

      reader.onerror = () => {
        reject(new Error('Failed to read file'));
      };

      reader.readAsText(file);
    });
  }

  // Export a single path as JSON
  function exportPath(path) {
    const exportData = {
      miroglyph_version: '4.0.0',
      exported_at: new Date().toISOString(),
      path: path
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    const safeName = path.name.replace(/[^a-z0-9]/gi, '_').toLowerCase();
    a.download = `miroglyph_${safeName}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // Helper: format date for filename
  function formatDate(date) {
    return date.toISOString().split('T')[0];
  }

  // Generate UUID for paths
  function generateId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  // Clear all data
  function clear() {
    localStorage.removeItem(STORAGE_KEY);
  }

  // Load configuration (miroglyph orientation)
  function loadConfig() {
    try {
      const config = localStorage.getItem(CONFIG_KEY);
      if (config) {
        return JSON.parse(config);
      }
    } catch (e) {
      console.error('Failed to load config:', e);
    }
    return { configuration: 'inverted' }; // default
  }

  // Save configuration
  function saveConfig(config) {
    try {
      localStorage.setItem(CONFIG_KEY, JSON.stringify(config));
      return true;
    } catch (e) {
      console.error('Failed to save config:', e);
      return false;
    }
  }

  // Export storage functions
  window.MiroGlyph = window.MiroGlyph || {};
  window.MiroGlyph.storage = {
    load,
    save,
    exportJSON,
    importJSON,
    exportPath,
    generateId,
    clear,
    loadConfig,
    saveConfig
  };
})();
