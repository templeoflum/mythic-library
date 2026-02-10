// Mythic System Explorer — Journey Aggregator
// Reads both localStorage sources and returns normalized journey records

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var EXPLORER_KEY = 'miroglyph_v4_data';
  var JM_KEY = 'miroglyph_networks';

  var ARC_COLORS = { D: '#8b5cf6', R: '#3b82f6', E: '#10b981' };

  function dominantArcColor(sequence) {
    if (!sequence || sequence.length === 0) return '#fbbf24';
    var counts = { D: 0, R: 0, E: 0 };
    for (var i = 0; i < sequence.length; i++) {
      var c = sequence[i].charAt(0);
      if (counts[c] !== undefined) counts[c]++;
    }
    var best = 'D';
    if (counts.R > counts[best]) best = 'R';
    if (counts.E > counts[best]) best = 'E';
    return ARC_COLORS[best] || '#fbbf24';
  }

  function readJSON(key) {
    try {
      var raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function loadExplorerTraversals() {
    var data = readJSON(EXPLORER_KEY);
    if (!data || !Array.isArray(data.paths)) return [];

    var groups = data.groups || [];
    var groupMap = {};
    for (var g = 0; g < groups.length; g++) {
      groupMap[groups[g].id] = groups[g].name;
    }

    var results = [];
    for (var i = 0; i < data.paths.length; i++) {
      var p = data.paths[i];
      results.push({
        id: p.path_id,
        name: p.name || 'Untitled',
        source: 'explorer',
        sequence: p.sequence || [],
        color: p.color || '#fbbf24',
        description: p.description || '',
        completed: true,
        created_date: p.created_date || '',
        is_circuit: p.is_circuit || false,
        notes: null,
        network_name: null,
        network_id: null,
        group_name: p.group_id ? (groupMap[p.group_id] || null) : null,
        archetype_summary: null
      });
    }
    return results;
  }

  function loadJMTraversals() {
    var data = readJSON(JM_KEY);
    if (!data || !Array.isArray(data.networks)) return [];

    var results = [];
    for (var n = 0; n < data.networks.length; n++) {
      var net = data.networks[n];
      var config = net.configuration || {};
      var archSummary = '';
      if (config.primary_archetype && config.secondary_archetype) {
        archSummary = (config.primary_archetype.name || '') + ' + ' + (config.secondary_archetype.name || '');
      }

      var traversals = net.traversals || [];
      for (var t = 0; t < traversals.length; t++) {
        var tr = traversals[t];
        var seq = tr.sequence || [];
        var isCircuit = seq.length >= 2 && seq[0] === seq[seq.length - 1];
        results.push({
          id: tr.traversal_id,
          name: tr.name || 'Untitled',
          source: 'journey',
          sequence: seq,
          color: dominantArcColor(seq),
          description: '',
          completed: !!tr.completed,
          created_date: net.created_date || '',
          is_circuit: isCircuit,
          notes: tr.notes || null,
          network_name: net.name || null,
          network_id: net.network_id || null,
          group_name: null,
          archetype_summary: archSummary || null
        });
      }
    }
    return results;
  }

  function loadAll(sortOrder) {
    var all = loadExplorerTraversals().concat(loadJMTraversals());

    if (sortOrder === 'oldest') {
      all.sort(function(a, b) {
        return (a.created_date || '').localeCompare(b.created_date || '');
      });
    } else if (sortOrder === 'name') {
      all.sort(function(a, b) {
        return (a.name || '').localeCompare(b.name || '');
      });
    } else {
      // 'newest' (default)
      all.sort(function(a, b) {
        return (b.created_date || '').localeCompare(a.created_date || '');
      });
    }

    return all;
  }

  function findById(id) {
    var all = loadAll();
    for (var i = 0; i < all.length; i++) {
      if (all[i].id === id) return all[i];
    }
    return null;
  }

  window.MiroGlyph.journeyAggregator = {
    loadAll: loadAll,
    findById: findById
  };
})();
