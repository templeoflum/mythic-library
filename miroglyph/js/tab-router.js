// Mythic System Explorer — View Router
// Manages 3 views (atlas/codex/chronicle) with nested hash routing

(function() {
  window.MiroGlyph = window.MiroGlyph || {};

  var activeViewId = null;
  var views = {};

  function register(viewId, module) {
    views[viewId] = {
      init: module.init,
      activate: module.activate || function() {},
      deactivate: module.deactivate || function() {},
      onRoute: module.onRoute || function() {},
      initialized: false
    };
  }

  function switchTo(viewId, routeParams) {
    if (!views[viewId]) return;

    // Deactivate current view
    if (activeViewId && views[activeViewId] && activeViewId !== viewId) {
      var oldContent = document.getElementById('view-' + activeViewId);
      if (oldContent) oldContent.hidden = true;
      var oldBtn = document.querySelector('[data-view="' + activeViewId + '"]');
      if (oldBtn) oldBtn.classList.remove('tab-active');
      views[activeViewId].deactivate();
    }

    // Activate new view
    activeViewId = viewId;
    var view = views[viewId];
    var content = document.getElementById('view-' + viewId);
    var btn = document.querySelector('[data-view="' + viewId + '"]');

    if (content) content.hidden = false;
    if (btn) btn.classList.add('tab-active');

    if (!view.initialized) {
      view.init(content);
      view.initialized = true;
    }

    view.activate();

    // Pass route params to the view for sub-navigation
    if (routeParams) {
      view.onRoute(routeParams);
    }
  }

  function getActiveView() {
    return activeViewId;
  }

  function handleRoute() {
    var hash = window.location.hash.slice(1) || 'atlas';
    var parsed = window.MiroGlyph.nav.parseRoute(hash);
    switchTo(parsed.view, parsed);
  }

  function init() {
    // Set up nav click handlers
    document.querySelectorAll('[data-view]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        window.location.hash = btn.dataset.view;
      });
    });

    // Initial route
    handleRoute();

    // Handle browser back/forward and hash changes
    window.addEventListener('hashchange', handleRoute);
  }

  window.MiroGlyph.tabRouter = {
    register: register,
    switchTo: switchTo,
    getActiveView: getActiveView,
    init: init
  };
})();
