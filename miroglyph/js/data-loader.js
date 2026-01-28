// Mythic System Explorer — Shared Data Loader
// Fetches, caches JSON, and builds cross-reference indices

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var cache = {};
  var loading = {};

  // Cross-reference indices (built after all catalogs loaded)
  var indices = {
    archetypeById: {},       // id -> archetype object
    entityByName: {},        // name -> entity object
    entitiesByNode: {},      // node_id -> entity[]
    archetypesByNode: {},    // node_id -> archetype[] (from affinities)
    entitiesByArchetype: {}, // archetype_id -> entity[]
    patternsByArc: {},       // arc_code -> pattern[]
    patternByName: {}        // name -> pattern object
  };

  function load(key, url) {
    if (cache[key]) return Promise.resolve(cache[key]);
    if (loading[key]) return loading[key];

    loading[key] = fetch(url).then(function(res) {
      if (!res.ok) throw new Error('Failed to load ' + url + ': ' + res.status);
      return res.json();
    }).then(function(data) {
      cache[key] = data;
      delete loading[key];
      return data;
    }).catch(function(err) {
      delete loading[key];
      console.warn('DataLoader: ' + key + ' failed:', err.message);
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

  // Load all catalogs and build indices
  function loadAll() {
    return Promise.all([
      load('archetypes', 'data/archetypes_catalog.json'),
      load('entities', 'data/entities_catalog.json'),
      load('patterns', 'data/patterns_catalog.json'),
      load('validation', 'data/validation_summary.json'),
      load('profiles', 'data/node_profiles.json'),
      load('affinities', 'data/archetype_affinities.json')
    ]).then(function() {
      buildIndices();
      return indices;
    });
  }

  function buildIndices() {
    var arch = cache.archetypes;
    var ent = cache.entities;
    var pat = cache.patterns;
    var aff = cache.affinities;

    // Archetype by ID
    if (arch && arch.archetypes) {
      arch.archetypes.forEach(function(a) {
        indices.archetypeById[a.id] = a;
      });
    }

    // Entity by name + entities by archetype + entities by node
    if (ent && ent.entities) {
      ent.entities.forEach(function(e) {
        indices.entityByName[e.name] = e;

        // By archetype
        if (e.mapping && e.mapping.archetype_id) {
          var aid = e.mapping.archetype_id;
          if (!indices.entitiesByArchetype[aid]) indices.entitiesByArchetype[aid] = [];
          indices.entitiesByArchetype[aid].push(e);
        }

        // By nearest node
        var nodeId = null;
        if (e.nearest_node && typeof e.nearest_node === 'object') {
          nodeId = e.nearest_node.node_id;
        } else if (typeof e.nearest_node === 'string') {
          nodeId = e.nearest_node;
        }
        if (nodeId) {
          if (!indices.entitiesByNode[nodeId]) indices.entitiesByNode[nodeId] = [];
          indices.entitiesByNode[nodeId].push(e);
        }
      });
    }

    // Archetypes by node (from affinities node_rankings)
    if (aff && aff.node_rankings) {
      Object.keys(aff.node_rankings).forEach(function(nodeId) {
        indices.archetypesByNode[nodeId] = aff.node_rankings[nodeId];
      });
    }

    // Patterns by arc + by name
    if (pat && pat.patterns) {
      pat.patterns.forEach(function(p) {
        indices.patternByName[p.name] = p;
        var arc = p.arc;
        if (!indices.patternsByArc[arc]) indices.patternsByArc[arc] = [];
        indices.patternsByArc[arc].push(p);
      });
    }

    console.log('Data indices built:', {
      archetypes: Object.keys(indices.archetypeById).length,
      entities: Object.keys(indices.entityByName).length,
      patterns: Object.keys(indices.patternByName).length,
      nodesMapped: Object.keys(indices.entitiesByNode).length
    });
  }

  function getIndex(name) {
    return indices[name] || {};
  }

  window.MiroGlyph.dataLoader = {
    load: load,
    loadAll: loadAll,
    get: get,
    isLoaded: isLoaded,
    getIndex: getIndex
  };
})();
