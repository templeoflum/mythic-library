# Miroglyph Cleanup Plan

**Created:** 2026-01-30
**Status:** COMPLETE
**Last Updated:** 2026-01-30

## Summary

All major issues have been resolved. The Mythic System Explorer is fully functional with three working views (Atlas, Codex, Chronicle).

---

## Resolved Issues

### Issue 1: Browser Caching (FIXED)
- **Symptom:** Atlas layout broken in regular browser window
- **Cause:** Browser cached old CSS
- **Solution:** Works in incognito; users should clear cache or hard refresh (Ctrl+Shift+R)

### Issue 2: Tab Switching Broken (FIXED - commit 114dbe5)
- **Symptom:** Clicking Codex/Chronicle tabs didn't change views - Atlas stayed visible
- **Cause:** `display: grid !important` on `#view-atlas.view-content` was overriding `display: none` from `.view-content[hidden]`
- **Solution:** Added explicit `#view-atlas.view-content[hidden] { display: none !important; }` rule

### Issue 3: Traversal Editor Duplication (FIXED - commit 34a32aa)
- **Symptom:** Clicking a node added it twice; saving created duplicate paths; groups created twice
- **Cause:** Event handlers being attached multiple times due to missing initialization guards
- **Solution:** Added initialization guards to view-atlas.js and paths.js, plus 50ms debounce protection

### Issue 4: Node ID Not Visible in Current Path (FIXED - commit 34a32aa)
- **Symptom:** Current path sequence showed colored blocks without node IDs
- **Cause:** CSS specificity issue - view-atlas.css `.node-chip.arc-*` rules overriding the white text color
- **Solution:** Added explicit `color: white` to `.path-sequence .node-chip.arc-*` rules in styles.css

---

## Completed Phases

### Phase 1: Diagnose the CSS/Caching Issue - COMPLETE

- [x] **1.1** Clear all browser cache completely and test http:// access
- [x] **1.2** Test in incognito/private window to rule out caching
- [x] **1.3** Check browser dev tools Network tab to see if CSS is being loaded
- [x] **1.4** Check browser dev tools Elements tab to see computed styles
- [x] **1.5** Check for JS errors in console
- [x] **1.6** Document exact steps to reproduce the issue

### Phase 2: Fix the Root Cause - COMPLETE

- [x] **2.1** Caching: Users should use incognito or clear cache
- [x] **2.2** Tab switching: Fixed CSS specificity issue
- [x] **2.3** CSS specificity: Added hidden rule override
- [x] **2.4** Test fix in both file:// and http:// modes

### Phase 3: Update Documentation - COMPLETE

- [x] **3.1** CLAUDE.md reflects current 3-view architecture
- [x] **3.2** README.md has correct file structure
- [x] **3.3** CHANGELOG.md updated with fixes
- [x] **3.4** This cleanup plan finalized

### Phase 4: Code Cleanup - COMPLETE

- [x] **4.1** Added initialization guards to prevent duplicate setup
- [x] **4.2** Added debounce protection to critical functions
- [x] **4.3** All JS modules have proper guards

### Phase 5: Testing & Verification - COMPLETE

- [x] **5.1** Atlas view: Three-pane layout renders correctly
- [x] **5.2** Atlas view: Nodes display in concentric rings
- [x] **5.3** Atlas view: Node clicks update left panel AND add to sequence (once)
- [x] **5.4** Atlas view: Traversal save/load works (no duplicates)
- [x] **5.5** Atlas view: Groups feature works (no duplicates)
- [x] **5.6** Codex view: Loads and displays correctly
- [x] **5.7** Chronicle view: Loads and displays correctly
- [x] **5.8** Tab switching works between all views

### Phase 6: Final Commit & Documentation - COMPLETE

- [x] **6.1** All fixes committed with clear messages
- [x] **6.2** CHANGELOG.md updated
- [x] **6.3** Pushed to remote

---

## File Structure (Current)

```
miroglyph/
├── index.html              # Main HTML - 3 views structure
├── CLAUDE.md               # Dev guide
├── README.md               # Overview
├── css/
│   ├── styles.css          # Base styles, CSS variables
│   ├── tabs.css            # Tab nav, shared components
│   ├── view-atlas.css      # Atlas three-pane layout
│   ├── view-codex.css      # Codex card grid
│   └── view-chronicle.css  # Chronicle patterns/validation
├── js/
│   ├── nodes.js            # 19-node definitions
│   ├── storage.js          # LocalStorage persistence
│   ├── data-loader.js      # JSON fetching with cache
│   ├── nav.js              # Cross-navigation utilities
│   ├── tab-router.js       # View switching
│   ├── global-search.js    # Omni-search
│   ├── canvas.js           # SVG rendering
│   ├── card-renderer.js    # Card rendering utils
│   ├── enrichment.js       # ACP data loader
│   ├── paths.js            # Traversal management (with init guards)
│   ├── node-drawer.js      # Node detail drawer
│   ├── detail-sheet.js     # Archetype/entity details
│   ├── view-atlas.js       # Atlas view controller (with init guards)
│   ├── view-codex.js       # Codex view controller
│   ├── mini-map.js         # Compact node map
│   ├── view-chronicle.js   # Chronicle view controller
│   └── app.js              # Boot sequence
└── data/                   # Pre-exported JSON data
    ├── archetypes_catalog.json
    ├── entities_catalog.json
    ├── patterns_catalog.json
    ├── validation_summary.json
    ├── node_profiles.json
    └── archetype_affinities.json
```

---

## Troubleshooting

### Layout looks wrong / CSS not applying
1. Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
2. Or use incognito/private window
3. Clear browser cache if persistent

### Codex/Chronicle tabs don't load data
- Must use HTTP server (not file:// protocol)
- Run: `python scripts/serve_miroglyph.py`
- Access: `http://localhost:8080`

### Duplicate actions in traversal editor
- Hard refresh to clear stale event listeners
- If persists after refresh, clear localStorage

---

## Notes

- The `explore.bat` launches Python server on port 8080
- `serve_miroglyph.py` has no-cache headers but browser may still cache aggressively
- All views now have initialization guards to prevent duplicate event handlers
