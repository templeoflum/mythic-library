// Mythic System Explorer — Enrichment Module
// Loads ACP node profiles and archetype affinities from JSON files
// Pure data module — rendering is handled by node-drawer.js

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var profiles = null;
  var affinities = null;
  var loaded = false;

  function load(profilesUrl, affinitiesUrl) {
    return Promise.all([
      fetch(profilesUrl || 'data/node_profiles.json'),
      fetch(affinitiesUrl || 'data/archetype_affinities.json')
    ]).then(function(responses) {
      var promises = [];
      if (responses[0].ok) {
        promises.push(responses[0].json().then(function(data) { profiles = data; }));
      } else {
        promises.push(Promise.resolve());
      }
      if (responses[1].ok) {
        promises.push(responses[1].json().then(function(data) { affinities = data; }));
      } else {
        promises.push(Promise.resolve());
      }
      return Promise.all(promises);
    }).then(function() {
      loaded = !!(profiles && affinities);
      if (loaded) {
        console.log('Enrichment data loaded:', {
          nodes: Object.keys(profiles.node_profiles || {}).length,
          archetypes: affinities.n_archetypes_scored
        });
      }
    }).catch(function(err) {
      console.log('Enrichment data not available:', err.message);
    });
  }

  function isLoaded() {
    return loaded;
  }

  function getNodeProfile(nodeId) {
    if (!profiles || !profiles.node_profiles) return null;
    return profiles.node_profiles[nodeId] || null;
  }

  function getArcProfile(arcCode) {
    if (!profiles || !profiles.arc_profiles) return null;
    return profiles.arc_profiles[arcCode] || null;
  }

  function getConditionProfile(condCode) {
    if (!profiles || !profiles.condition_profiles) return null;
    return profiles.condition_profiles[String(condCode)] || null;
  }

  function getNodeArchetypes(nodeId, topN) {
    topN = topN || 10;
    if (!affinities || !affinities.node_rankings) return [];
    var rankings = affinities.node_rankings[nodeId] || [];
    return rankings.slice(0, topN);
  }

  window.MiroGlyph.enrichment = {
    load: load,
    isLoaded: isLoaded,
    getNodeProfile: getNodeProfile,
    getArcProfile: getArcProfile,
    getConditionProfile: getConditionProfile,
    getNodeArchetypes: getNodeArchetypes
  };
})();
