# Miroglyph Cleanup Plan

**Created:** 2026-01-30
**Status:** Phase 1-2 Complete

## Resolved Issues

### Issue 1: Browser Caching (FIXED)
- **Symptom:** Atlas layout broken in regular browser window
- **Cause:** Browser cached old CSS
- **Solution:** Works in incognito; users should clear cache or hard refresh (Ctrl+Shift+R)

### Issue 2: Tab Switching Broken (FIXED - commit 114dbe5)
- **Symptom:** Clicking Codex/Chronicle tabs didn't change views - Atlas stayed visible
- **Cause:** `display: grid !important` on `#view-atlas.view-content` was overriding `display: none` from `.view-content[hidden]`
- **Solution:** Added explicit `#view-atlas.view-content[hidden] { display: none !important; }` rule and removed `!important` from grid rules

---

## Remaining Issues

### 1. Dual Access Mode Problem
- **file:// access**: Atlas three-pane layout works, but Codex/Chronicle tabs fail (need HTTP for JSON data fetching)
- **http:// access (Python server)**: Codex/Chronicle work, but Atlas layout is broken (CSS grid not applying - appears to be browser caching issue)

### 2. Documentation Out of Sync
- README.md was partially updated but may still have inconsistencies
- CLAUDE.md references old file structure
- Directory structure changed from 5 tabs to 3 views but not all docs reflect this

### 3. Code Structure
- View files renamed from `tab-*.js` to `view-*.js`
- CSS files renamed from `tab-*.css` to `view-*.css`
- HTML restructured: removed `.atlas-layout-three` wrapper div

---

## Cleanup Tasks

### Phase 1: Diagnose the CSS/Caching Issue - COMPLETE

- [x] **1.1** Clear all browser cache completely and test http:// access
- [x] **1.2** Test in incognito/private window to rule out caching - **Atlas layout works in incognito**
- [x] **1.3** Check browser dev tools Network tab to see if CSS is being loaded - **CSS loads correctly**
- [x] **1.4** Check browser dev tools Elements tab to see computed styles on `#view-atlas`
- [x] **1.5** If CSS loads but grid doesn't apply, check for JS errors in console
- [x] **1.6** Document exact steps to reproduce the issue - **Documented above**

**Findings:**
1. CSS caching was causing layout issues in regular browser
2. Tab switching was broken due to CSS specificity issue with `!important`

### Phase 2: Fix the Root Cause - COMPLETE

- [x] **2.1** Caching: Users should use incognito or clear cache (no code change needed)
- [x] **2.2** Tab switching: Fixed CSS specificity issue (commit 114dbe5)
- [x] **2.3** CSS specificity: Added `#view-atlas.view-content[hidden] { display: none !important; }`
- [ ] **2.4** Test fix in both file:// and http:// modes - **PENDING USER VERIFICATION**

### Phase 3: Update Documentation

- [ ] **3.1** Update `miroglyph/CLAUDE.md`:
  - Current 3-view architecture (Atlas/Codex/Chronicle)
  - Correct file listing
  - How to run (both methods)

- [ ] **3.2** Update `miroglyph/README.md`:
  - Verify all file paths are correct
  - Update any remaining references to old tab names
  - Add troubleshooting section for caching issues

- [ ] **3.3** Update root `README.md` if it references miroglyph structure

- [ ] **3.4** Consider adding a `DEVELOPMENT.md` with:
  - How to run locally
  - Known issues
  - Browser compatibility notes

### Phase 4: Code Cleanup

- [ ] **4.1** Remove any remaining debug code (console.logs, test styles)
- [ ] **4.2** Verify all JS modules export/import correctly
- [ ] **4.3** Check for unused CSS rules from old structure
- [ ] **4.4** Ensure consistent code style across files

### Phase 5: Testing & Verification

- [ ] **5.1** Test Atlas view: Three-pane layout renders correctly
- [ ] **5.2** Test Atlas view: Nodes display in concentric rings
- [ ] **5.3** Test Atlas view: Node clicks update left panel AND add to sequence
- [ ] **5.4** Test Atlas view: Traversal save/load works
- [ ] **5.5** Test Atlas view: Groups feature works
- [ ] **5.6** Test Codex view: Archetypes sub-tab loads and displays
- [ ] **5.7** Test Codex view: Entities sub-tab loads and displays
- [ ] **5.8** Test Chronicle view: Patterns sub-tab works
- [ ] **5.9** Test Chronicle view: Validation sub-tab works
- [ ] **5.10** Test in multiple browsers (Chrome, Firefox, Edge)

### Phase 6: Final Commit & Documentation

- [ ] **6.1** Commit all fixes with clear commit message
- [ ] **6.2** Update CHANGELOG.md with changes made
- [ ] **6.3** Push to remote

---

## File Inventory

### Current Structure (Verified)
```
miroglyph/
├── index.html              # Main HTML - 3 views structure
├── CLAUDE.md               # Dev guide (needs update)
├── README.md               # Overview (partially updated)
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
│   ├── paths.js            # Traversal management
│   ├── node-drawer.js      # Node detail drawer
│   ├── detail-sheet.js     # Archetype/entity details
│   ├── view-atlas.js       # Atlas view controller
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

## Priority Order

1. **HIGH**: Phase 1 (Diagnose) - Can't fix what we don't understand
2. **HIGH**: Phase 2 (Fix) - Core functionality must work
3. **MEDIUM**: Phase 5 (Testing) - Verify everything works
4. **MEDIUM**: Phase 3 (Docs) - Keep docs accurate
5. **LOW**: Phase 4 (Code cleanup) - Nice to have
6. **LOW**: Phase 6 (Final) - Wrap up

---

## Notes

- The explore.bat launches Python server on port 8080
- serve_miroglyph.py has no-cache headers but browser may still cache
- Atlas view uses CSS Grid with `display: grid !important`
- Codex/Chronicle need HTTP server to fetch JSON data files
