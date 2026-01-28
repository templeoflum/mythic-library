// MiroGlyph — Tab Router
// Manages tab navigation, lazy initialization, and hash-based routing

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  let activeTabId = null;
  const tabs = {};

  function register(tabId, module) {
    tabs[tabId] = {
      init: module.init,
      activate: module.activate || function() {},
      deactivate: module.deactivate || function() {},
      initialized: false,
    };
  }

  function switchTo(tabId) {
    if (tabId === activeTabId) return;
    if (!tabs[tabId]) return;

    // Deactivate current
    if (activeTabId && tabs[activeTabId]) {
      const oldContent = document.getElementById('tab-content-' + activeTabId);
      if (oldContent) oldContent.hidden = true;
      const oldBtn = document.querySelector('[data-tab="' + activeTabId + '"]');
      if (oldBtn) oldBtn.classList.remove('tab-active');
      tabs[activeTabId].deactivate();
    }

    // Activate new
    activeTabId = tabId;
    const tab = tabs[tabId];
    const content = document.getElementById('tab-content-' + tabId);
    const btn = document.querySelector('[data-tab="' + tabId + '"]');

    if (content) content.hidden = false;
    if (btn) btn.classList.add('tab-active');

    if (!tab.initialized) {
      tab.init(content);
      tab.initialized = true;
    }
    tab.activate();

    // Update hash without triggering hashchange
    history.replaceState(null, '', '#' + tabId);
  }

  function getActiveTab() {
    return activeTabId;
  }

  function init() {
    // Set up nav click handlers
    document.querySelectorAll('[data-tab]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        switchTo(btn.dataset.tab);
      });
    });

    // Read hash or default to topology
    const hash = window.location.hash.slice(1);
    const startTab = (hash && tabs[hash]) ? hash : 'topology';
    switchTo(startTab);

    // Handle browser back/forward
    window.addEventListener('hashchange', function() {
      const h = window.location.hash.slice(1);
      if (h && tabs[h]) switchTo(h);
    });
  }

  window.MiroGlyph.tabRouter = { register, switchTo, getActiveTab, init };
})();
