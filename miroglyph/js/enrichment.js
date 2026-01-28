// MiroGlyph v4 - Enrichment Module
// Loads ACP node profiles and archetype affinities from JSON files

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  const AXES = [
    'order-chaos', 'creation-destruction', 'light-shadow', 'active-receptive',
    'individual-collective', 'ascent-descent', 'stasis-transformation', 'voluntary-fated'
  ];

  const AXIS_SHORT = {
    'order-chaos': 'Ord-Chaos',
    'creation-destruction': 'Cre-Dest',
    'light-shadow': 'Light-Shadow',
    'active-receptive': 'Act-Recep',
    'individual-collective': 'Ind-Coll',
    'ascent-descent': 'Asc-Desc',
    'stasis-transformation': 'Sta-Trans',
    'voluntary-fated': 'Vol-Fated'
  };

  let profiles = null;
  let affinities = null;
  let loaded = false;

  async function load(profilesUrl, affinitiesUrl) {
    try {
      const [profileRes, affinityRes] = await Promise.all([
        fetch(profilesUrl || 'data/node_profiles.json'),
        fetch(affinitiesUrl || 'data/archetype_affinities.json')
      ]);

      if (profileRes.ok) {
        profiles = await profileRes.json();
      }
      if (affinityRes.ok) {
        affinities = await affinityRes.json();
      }

      loaded = !!(profiles && affinities);
      if (loaded) {
        console.log('Enrichment data loaded:', {
          nodes: Object.keys(profiles.node_profiles || {}).length,
          archetypes: affinities.n_archetypes_scored
        });
        showEnrichmentPanel();
      }
    } catch (err) {
      console.log('Enrichment data not available:', err.message);
    }
  }

  function isLoaded() {
    return loaded;
  }

  function showEnrichmentPanel() {
    const panel = document.getElementById('enrichment-panel');
    if (panel) panel.hidden = false;
  }

  function getNodeProfile(nodeId) {
    if (!profiles) return null;
    return profiles.node_profiles?.[nodeId] || null;
  }

  function getArcProfile(arcCode) {
    if (!profiles) return null;
    return profiles.arc_profiles?.[arcCode] || null;
  }

  function getConditionProfile(condCode) {
    if (!profiles) return null;
    return profiles.condition_profiles?.[String(condCode)] || null;
  }

  function getNodeArchetypes(nodeId, topN) {
    topN = topN || 10;
    if (!affinities) return [];
    const rankings = affinities.node_rankings?.[nodeId] || [];
    return rankings.slice(0, topN);
  }

  function renderNodeEnrichment(nodeId) {
    const container = document.getElementById('node-enrichment');
    if (!container || !loaded) return;

    if (nodeId === '∅') {
      container.innerHTML = '<p class="hint">Nontion: center reset point — outside coordinate space.</p>';
      return;
    }

    const profile = getNodeProfile(nodeId);
    const archetypes = getNodeArchetypes(nodeId, 5);

    if (!profile) {
      container.innerHTML = '<p class="hint">No profile data available.</p>';
      return;
    }

    let html = '';

    // Coordinate bars
    html += '<div class="enrichment-coords">';
    html += '<div class="enrichment-label">ACP Profile <span class="enrichment-meta">';
    html += `n=${profile.n_entities}, ${profile.method || 'direct'}</span></div>`;

    const coords = profile.mean_coordinates || [];
    for (let i = 0; i < AXES.length; i++) {
      const val = coords[i] || 0.5;
      const pct = Math.round(val * 100);
      const axisName = AXIS_SHORT[AXES[i]] || AXES[i];
      html += `<div class="axis-bar">`;
      html += `<span class="axis-name">${axisName}</span>`;
      html += `<div class="axis-track"><div class="axis-fill" style="width:${pct}%"></div>`;
      html += `<div class="axis-marker" style="left:${pct}%"></div></div>`;
      html += `<span class="axis-val">${val.toFixed(2)}</span>`;
      html += `</div>`;
    }
    html += '</div>';

    // Top archetypes
    if (archetypes.length > 0) {
      html += '<div class="enrichment-archetypes">';
      html += '<div class="enrichment-label">Top Archetypes</div>';
      for (const arch of archetypes) {
        const aff = arch.affinity || 0;
        const pct = Math.round(aff * 100);
        html += `<div class="archetype-entry">`;
        html += `<span class="arch-name">${arch.name}</span>`;
        html += `<div class="arch-bar"><div class="arch-fill" style="width:${pct}%"></div></div>`;
        html += `<span class="arch-val">${aff.toFixed(2)}</span>`;
        html += `</div>`;
      }
      html += '</div>';
    }

    // Dominant primordials
    const prims = profile.dominant_primordials || [];
    if (prims.length > 0) {
      html += '<div class="enrichment-primordials">';
      html += '<div class="enrichment-label">Dominant Primordials</div>';
      for (const p of prims.slice(0, 3)) {
        const name = (p.primordial_id || '').replace('primordial:', '');
        html += `<span class="primordial-tag">${name} (${p.mean_weight.toFixed(2)})</span> `;
      }
      html += '</div>';
    }

    container.innerHTML = html;
  }

  function clearEnrichment() {
    const container = document.getElementById('node-enrichment');
    if (container) {
      container.innerHTML = '<p class="hint">Hover a node to see its mythic profile.</p>';
    }
  }

  window.MiroGlyph.enrichment = {
    load,
    isLoaded,
    getNodeProfile,
    getArcProfile,
    getConditionProfile,
    getNodeArchetypes,
    renderNodeEnrichment,
    clearEnrichment
  };
})();
