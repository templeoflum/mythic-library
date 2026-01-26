#!/usr/bin/env python3
"""
MythOS Explorer — Interactive browser UI for verifying entity mappings,
ACP coordinates, and co-occurrence data.

Usage:
    python scripts/explorer/server.py
    # Opens http://localhost:8421
"""
import io
import json
import sqlite3
import sys
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integration.acp_loader import ACPLoader

DB_PATH = PROJECT_ROOT / "data" / "mythic_patterns.db"
ACP_PATH = PROJECT_ROOT / "ACP"
MAPPINGS_PATH = PROJECT_ROOT / "outputs" / "mappings" / "entity_to_archetype.json"
RESULTS_PATH = PROJECT_ROOT / "outputs" / "metrics" / "validation_results.json"
MOTIFS_PATH = PROJECT_ROOT / "outputs" / "metrics" / "motif_signatures.json"

PORT = 8421

# ── Global data loaded at startup ─────────────────────────────────────────────
acp: ACPLoader = None
db: sqlite3.Connection = None
mappings: list = []
validation_results: dict = {}
motif_signatures: dict = {}


def load_data():
    global acp, db, mappings, validation_results, motif_signatures

    print("Loading ACP...")
    acp = ACPLoader(str(ACP_PATH))
    s = acp.summary()
    print(f"  {s['archetypes']} archetypes, {s['primordials']} primordials")

    print("Loading database...")
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    row = db.execute("SELECT COUNT(*) as c FROM entities").fetchone()
    print(f"  {row['c']} entities")

    print("Loading mappings...")
    if MAPPINGS_PATH.exists():
        with open(MAPPINGS_PATH, "r", encoding="utf-8") as f:
            mappings = json.load(f)
    print(f"  {len(mappings)} mappings")

    if RESULTS_PATH.exists():
        with open(RESULTS_PATH, "r", encoding="utf-8") as f:
            validation_results = json.load(f)

    if MOTIFS_PATH.exists():
        with open(MOTIFS_PATH, "r", encoding="utf-8") as f:
            motif_signatures = json.load(f)


# ── API handlers ──────────────────────────────────────────────────────────────

def api_summary():
    """Overall stats for the dashboard."""
    row = db.execute("""
        SELECT
            (SELECT COUNT(*) FROM entities) as entities,
            (SELECT COUNT(*) FROM segments) as segments,
            (SELECT COUNT(*) FROM texts) as texts,
            (SELECT COUNT(*) FROM entity_mentions) as mentions,
            (SELECT COUNT(*) FROM motif_tags) as motif_tags,
            (SELECT COUNT(DISTINCT tradition) FROM texts) as traditions
    """).fetchone()
    return {
        "library": dict(row),
        "acp": acp.summary(),
        "mappings": {
            "total": len(mappings),
            "mapped_entities": len(mappings),
            "total_entities": row["entities"],
            "coverage_pct": round(len(mappings) / max(row["entities"], 1) * 100, 1),
        },
        "validation": validation_results.get("summary", {}),
    }


def api_entities(params):
    """List all entities with mapping status."""
    search = params.get("q", [""])[0].lower()
    sort = params.get("sort", ["mentions"])[0]
    mapped_only = params.get("mapped", [""])[0] == "true"
    unmapped_only = params.get("unmapped", [""])[0] == "true"

    # Build mapping lookup
    mapping_by_name = {m["library_entity"]: m for m in mappings}

    rows = db.execute("""
        SELECT e.entity_id, e.canonical_name, e.entity_type, e.total_mentions,
               GROUP_CONCAT(DISTINCT t.tradition) as traditions
        FROM entities e
        JOIN entity_mentions em ON e.entity_id = em.entity_id
        JOIN segments s ON em.segment_id = s.segment_id
        JOIN texts t ON s.text_id = t.text_id
        GROUP BY e.entity_id
        ORDER BY e.total_mentions DESC
    """).fetchall()

    result = []
    for r in rows:
        name = r["canonical_name"]
        if search and search not in name.lower():
            continue

        m = mapping_by_name.get(name)
        if mapped_only and not m:
            continue
        if unmapped_only and m:
            continue

        entry = {
            "name": name,
            "type": r["entity_type"],
            "mentions": r["total_mentions"],
            "traditions": sorted(set(r["traditions"].split(","))) if r["traditions"] else [],
            "mapped": m is not None,
        }
        if m:
            entry["mapping"] = {
                "acp_id": m["acp_archetype_id"],
                "acp_name": m["acp_name"],
                "confidence": m["confidence"],
                "method": m["method"],
            }
        result.append(entry)

    if sort == "name":
        result.sort(key=lambda x: x["name"].lower())
    elif sort == "confidence":
        result.sort(key=lambda x: (x.get("mapping", {}).get("confidence", 0)), reverse=True)

    return {"entities": result, "count": len(result)}


def api_entity_detail(params):
    """Detailed view of a single entity."""
    name = params.get("name", [""])[0]
    if not name:
        return {"error": "name parameter required"}

    row = db.execute("""
        SELECT entity_id, canonical_name, entity_type, total_mentions
        FROM entities WHERE canonical_name = ?
    """, (name,)).fetchone()

    if not row:
        return {"error": f"Entity '{name}' not found"}

    entity_id = row["entity_id"]

    # Aliases
    aliases = [r["alias_name"] for r in db.execute(
        "SELECT alias_name FROM entity_aliases WHERE entity_id = ?", (entity_id,)
    ).fetchall()]

    # Traditions + mention counts
    traditions = db.execute("""
        SELECT t.tradition, COUNT(*) as count
        FROM entity_mentions em
        JOIN segments s ON em.segment_id = s.segment_id
        JOIN texts t ON s.text_id = t.text_id
        WHERE em.entity_id = ?
        GROUP BY t.tradition ORDER BY count DESC
    """, (entity_id,)).fetchall()

    # Top co-occurring entities
    cooccurrences = db.execute("""
        SELECT e2.canonical_name, COUNT(*) as count
        FROM entity_mentions em1
        JOIN entity_mentions em2 ON em1.segment_id = em2.segment_id
        JOIN entities e2 ON em2.entity_id = e2.entity_id
        WHERE em1.entity_id = ? AND em2.entity_id != ?
        GROUP BY e2.entity_id ORDER BY count DESC LIMIT 20
    """, (entity_id, entity_id)).fetchall()

    # Top motifs
    motifs = db.execute("""
        SELECT m.motif_code, m.label, COUNT(*) as count
        FROM motif_tags mt
        JOIN entity_mentions em ON mt.segment_id = em.segment_id
        JOIN motifs m ON mt.motif_code = m.motif_code
        WHERE em.entity_id = ?
        GROUP BY m.motif_code ORDER BY count DESC LIMIT 15
    """, (entity_id,)).fetchall()

    # Sample segments
    samples = db.execute("""
        SELECT s.segment_id, s.content, t.title, t.tradition
        FROM entity_mentions em
        JOIN segments s ON em.segment_id = s.segment_id
        JOIN texts t ON s.text_id = t.text_id
        WHERE em.entity_id = ?
        ORDER BY RANDOM() LIMIT 5
    """, (entity_id,)).fetchall()

    # ACP mapping
    mapping_by_name = {m["library_entity"]: m for m in mappings}
    m = mapping_by_name.get(name)
    acp_data = None
    if m:
        arch_id = m["acp_archetype_id"]
        coords = acp.get_coordinates(arch_id)
        nearby = acp.get_nearby(arch_id, threshold=0.4)
        instantiations = acp.get_instantiations(arch_id)
        acp_aliases = acp.get_alias_info(arch_id)

        acp_data = {
            "archetype_id": arch_id,
            "archetype_name": m["acp_name"],
            "confidence": m["confidence"],
            "method": m["method"],
            "coordinates": {
                axis: round(float(v), 4)
                for axis, v in zip(
                    ["order-chaos", "creation-destruction", "light-shadow",
                     "active-receptive", "individual-collective", "ascent-descent",
                     "stasis-transformation", "voluntary-fated"],
                    coords
                )
            } if coords is not None else None,
            "nearby": [
                {"id": nid, "name": acp.archetypes[nid].get("name", nid), "distance": round(d, 4)}
                for nid, d in nearby[:10]
            ],
            "instantiates": instantiations,
            "aliases": [
                {"name": a.get("name", a) if isinstance(a, dict) else a,
                 "fidelity": a.get("fidelity", None) if isinstance(a, dict) else None}
                for a in acp_aliases
            ],
        }

    return {
        "name": name,
        "type": row["entity_type"],
        "mentions": row["total_mentions"],
        "aliases": aliases,
        "traditions": [{"tradition": r["tradition"], "count": r["count"]} for r in traditions],
        "cooccurrences": [{"entity": r["canonical_name"], "count": r["count"]} for r in cooccurrences],
        "motifs": [{"code": r["motif_code"], "label": r["label"], "count": r["count"]} for r in motifs],
        "samples": [{"id": r["segment_id"], "text": r["content"][:500], "title": r["title"], "tradition": r["tradition"]} for r in samples],
        "acp": acp_data,
    }


def api_coordinates(params):
    """All mapped entities with their 8D coordinates for visualization."""
    axes = ["order-chaos", "creation-destruction", "light-shadow",
            "active-receptive", "individual-collective", "ascent-descent",
            "stasis-transformation", "voluntary-fated"]

    # Which two axes to project onto
    x_axis = params.get("x", ["order-chaos"])[0]
    y_axis = params.get("y", ["creation-destruction"])[0]

    points = []
    for m in mappings:
        coords = acp.get_coordinates(m["acp_archetype_id"])
        if coords is None:
            continue

        xi = axes.index(x_axis) if x_axis in axes else 0
        yi = axes.index(y_axis) if y_axis in axes else 1

        # Get mention count from DB
        row = db.execute(
            "SELECT total_mentions FROM entities WHERE canonical_name = ?",
            (m["library_entity"],)
        ).fetchone()

        # Get primordial info
        instantiations = acp.get_instantiations(m["acp_archetype_id"])
        primordials = [inst.get("primordial", "").split(":")[-1] for inst in instantiations if inst.get("primordial")]

        points.append({
            "name": m["library_entity"],
            "acp_name": m["acp_name"],
            "x": round(float(coords[xi]), 4),
            "y": round(float(coords[yi]), 4),
            "all_coords": {axis: round(float(v), 4) for axis, v in zip(axes, coords)},
            "mentions": row["total_mentions"] if row else 0,
            "confidence": m["confidence"],
            "method": m["method"],
            "primordials": primordials,
        })

    return {"points": points, "x_axis": x_axis, "y_axis": y_axis, "axes": axes}


def api_cooccurrence(params):
    """Co-occurrence data between mapped entities."""
    name = params.get("name", [""])[0]
    min_count = int(params.get("min", ["2"])[0])

    mapping_by_name = {m["library_entity"]: m for m in mappings}

    if name:
        # Co-occurrences for a specific entity
        row = db.execute(
            "SELECT entity_id FROM entities WHERE canonical_name = ?", (name,)
        ).fetchone()
        if not row:
            return {"error": f"Entity '{name}' not found"}

        pairs = db.execute("""
            SELECT e2.canonical_name, COUNT(*) as count
            FROM entity_mentions em1
            JOIN entity_mentions em2 ON em1.segment_id = em2.segment_id
            JOIN entities e2 ON em2.entity_id = e2.entity_id
            WHERE em1.entity_id = ? AND em2.entity_id != ?
            GROUP BY e2.entity_id HAVING count >= ?
            ORDER BY count DESC
        """, (row["entity_id"], row["entity_id"], min_count)).fetchall()

        result = []
        for p in pairs:
            other_name = p["canonical_name"]
            m1 = mapping_by_name.get(name)
            m2 = mapping_by_name.get(other_name)
            dist = None
            if m1 and m2:
                dist = acp.calculate_distance(m1["acp_archetype_id"], m2["acp_archetype_id"])
                if dist is not None:
                    dist = round(dist, 4)

            result.append({
                "entity": other_name,
                "count": p["count"],
                "distance": dist,
                "both_mapped": m1 is not None and m2 is not None,
            })

        return {"entity": name, "pairs": result}
    else:
        # Top co-occurring pairs globally
        pairs = db.execute("""
            SELECT e1.canonical_name as e1, e2.canonical_name as e2, COUNT(*) as count
            FROM entity_mentions em1
            JOIN entity_mentions em2 ON em1.segment_id = em2.segment_id
            JOIN entities e1 ON em1.entity_id = e1.entity_id
            JOIN entities e2 ON em2.entity_id = e2.entity_id
            WHERE em1.entity_id < em2.entity_id
            GROUP BY em1.entity_id, em2.entity_id HAVING count >= ?
            ORDER BY count DESC LIMIT 100
        """, (min_count,)).fetchall()

        result = []
        for p in pairs:
            m1 = mapping_by_name.get(p["e1"])
            m2 = mapping_by_name.get(p["e2"])
            dist = None
            if m1 and m2:
                dist = acp.calculate_distance(m1["acp_archetype_id"], m2["acp_archetype_id"])
                if dist is not None:
                    dist = round(dist, 4)

            result.append({
                "entity1": p["e1"],
                "entity2": p["e2"],
                "count": p["count"],
                "distance": dist,
                "both_mapped": m1 is not None and m2 is not None,
            })

        return {"pairs": result}


def api_validation():
    """Return the validation results."""
    return validation_results


def api_motifs(params):
    """Motif data."""
    code = params.get("code", [""])[0]
    if code and code in motif_signatures:
        sig = motif_signatures[code]
        # Also get the motif label from DB
        row = db.execute("SELECT label, category FROM motifs WHERE motif_code = ?", (code,)).fetchone()
        return {
            "code": code,
            "label": row["label"] if row else "",
            "category": row["category"] if row else "",
            **sig,
        }

    # List all motifs with entity counts
    rows = db.execute("""
        SELECT m.motif_code, m.label, m.category, COUNT(DISTINCT mt.segment_id) as segment_count
        FROM motifs m
        JOIN motif_tags mt ON m.motif_code = mt.motif_code
        GROUP BY m.motif_code
        ORDER BY segment_count DESC LIMIT 100
    """).fetchall()

    return {
        "motifs": [
            {"code": r["motif_code"], "label": r["label"], "category": r["category"], "segments": r["segment_count"]}
            for r in rows
        ]
    }


# ── Request handler ───────────────────────────────────────────────────────────

API_ROUTES = {
    "/api/summary": lambda p: api_summary(),
    "/api/entities": api_entities,
    "/api/entity": api_entity_detail,
    "/api/coordinates": api_coordinates,
    "/api/cooccurrence": api_cooccurrence,
    "/api/validation": lambda p: api_validation(),
    "/api/motifs": api_motifs,
}


class ExplorerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path in API_ROUTES:
            handler = API_ROUTES[path]
            try:
                import inspect
                sig = inspect.signature(handler)
                if len(sig.parameters) > 0:
                    data = handler(params)
                else:
                    data = handler()
            except Exception as e:
                data = {"error": str(e)}
                import traceback
                traceback.print_exc()

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

        elif path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(get_html().encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress request logging


# ── HTML Frontend ─────────────────────────────────────────────────────────────

def get_html():
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MythOS Explorer</title>
<style>
:root {
  --bg: #0e1117;
  --surface: #161b22;
  --surface2: #1c2333;
  --border: #30363d;
  --text: #c9d1d9;
  --text-dim: #8b949e;
  --accent: #58a6ff;
  --accent2: #bc8cff;
  --green: #3fb950;
  --orange: #d29922;
  --red: #f85149;
  --radius: 8px;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }

/* Layout */
.app { display: flex; height: 100vh; }
.sidebar { width: 260px; background: var(--surface); border-right: 1px solid var(--border); display: flex; flex-direction: column; flex-shrink: 0; }
.sidebar h1 { font-size: 16px; padding: 16px; border-bottom: 1px solid var(--border); color: var(--accent); letter-spacing: 1px; }
.nav { padding: 8px; flex: 1; }
.nav-item { display: block; width: 100%; padding: 10px 12px; background: none; border: none; color: var(--text-dim); text-align: left; cursor: pointer; border-radius: var(--radius); font-size: 14px; transition: all 0.15s; }
.nav-item:hover { background: var(--surface2); color: var(--text); }
.nav-item.active { background: var(--surface2); color: var(--accent); font-weight: 600; }
.nav-item .count { float: right; font-size: 12px; background: var(--border); padding: 1px 8px; border-radius: 10px; }

.main { flex: 1; overflow-y: auto; padding: 24px; }
.main h2 { font-size: 20px; margin-bottom: 16px; color: var(--text); font-weight: 600; }

/* Cards */
.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; margin-bottom: 16px; }
.card h3 { font-size: 14px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; }

/* Stats grid */
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-bottom: 24px; }
.stat { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; }
.stat .value { font-size: 28px; font-weight: 700; color: var(--accent); }
.stat .label { font-size: 12px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }

/* Search */
.search-bar { display: flex; gap: 8px; margin-bottom: 16px; }
.search-bar input { flex: 1; background: var(--surface2); border: 1px solid var(--border); color: var(--text); padding: 10px 14px; border-radius: var(--radius); font-size: 14px; outline: none; }
.search-bar input:focus { border-color: var(--accent); }
.search-bar select { background: var(--surface2); border: 1px solid var(--border); color: var(--text); padding: 8px 12px; border-radius: var(--radius); font-size: 13px; outline: none; cursor: pointer; }

/* Filters */
.filters { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
.filter-btn { padding: 6px 14px; background: var(--surface2); border: 1px solid var(--border); color: var(--text-dim); border-radius: 20px; cursor: pointer; font-size: 13px; transition: all 0.15s; }
.filter-btn:hover { border-color: var(--accent); color: var(--text); }
.filter-btn.active { background: var(--accent); color: var(--bg); border-color: var(--accent); font-weight: 600; }

/* Tables */
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th { text-align: left; padding: 10px 12px; border-bottom: 2px solid var(--border); color: var(--text-dim); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer; user-select: none; }
th:hover { color: var(--accent); }
td { padding: 10px 12px; border-bottom: 1px solid var(--border); }
tr:hover { background: var(--surface2); }
.clickable { cursor: pointer; }
.clickable:hover td { color: var(--accent); }

/* Badges */
.badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }
.badge-mapped { background: rgba(63,185,80,0.15); color: var(--green); }
.badge-unmapped { background: rgba(248,81,73,0.15); color: var(--red); }
.badge-method { background: rgba(88,166,255,0.15); color: var(--accent); }

/* Confidence bar */
.conf-bar { display: inline-flex; align-items: center; gap: 6px; }
.conf-track { width: 60px; height: 6px; background: var(--border); border-radius: 3px; overflow: hidden; }
.conf-fill { height: 100%; border-radius: 3px; }
.conf-high { background: var(--green); }
.conf-med { background: var(--orange); }
.conf-low { background: var(--red); }

/* Detail panel */
.detail-panel { position: fixed; top: 0; right: -500px; width: 500px; height: 100vh; background: var(--surface); border-left: 1px solid var(--border); z-index: 100; transition: right 0.25s; overflow-y: auto; padding: 24px; }
.detail-panel.open { right: 0; }
.detail-panel .close-btn { position: absolute; top: 12px; right: 12px; background: none; border: none; color: var(--text-dim); font-size: 24px; cursor: pointer; }
.detail-panel .close-btn:hover { color: var(--text); }
.detail-panel h2 { font-size: 24px; margin-bottom: 4px; }
.detail-panel .subtitle { color: var(--text-dim); margin-bottom: 20px; }

.detail-section { margin-bottom: 20px; }
.detail-section h4 { font-size: 12px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; padding-bottom: 4px; border-bottom: 1px solid var(--border); }

/* Coordinate radar */
.coord-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.coord-row { display: flex; justify-content: space-between; align-items: center; padding: 4px 0; font-size: 13px; }
.coord-label { color: var(--text-dim); }
.coord-val { font-weight: 600; font-family: 'SF Mono', 'Consolas', monospace; }
.coord-bar-track { flex: 1; height: 4px; background: var(--border); margin: 0 10px; border-radius: 2px; position: relative; }
.coord-bar-fill { position: absolute; top: 0; height: 100%; border-radius: 2px; background: var(--accent); }

/* Canvas */
.scatter-container { position: relative; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
canvas { display: block; }
.axis-selectors { display: flex; gap: 12px; margin-bottom: 12px; align-items: center; }
.axis-selectors label { color: var(--text-dim); font-size: 13px; }
.axis-selectors select { background: var(--surface2); border: 1px solid var(--border); color: var(--text); padding: 6px 10px; border-radius: var(--radius); font-size: 13px; }

/* Co-occurrence */
.pair-row { display: flex; align-items: center; gap: 12px; padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 14px; }
.pair-names { flex: 1; }
.pair-count { font-weight: 700; color: var(--accent); min-width: 40px; text-align: right; }
.pair-dist { color: var(--text-dim); font-family: monospace; min-width: 60px; text-align: right; }

/* Tags */
.tag { display: inline-block; padding: 2px 8px; margin: 2px; border-radius: 4px; font-size: 12px; background: var(--surface2); border: 1px solid var(--border); color: var(--text-dim); }

/* Sample text */
.sample { background: var(--surface2); border-radius: var(--radius); padding: 12px; margin-bottom: 8px; font-size: 13px; line-height: 1.6; }
.sample .meta { font-size: 11px; color: var(--text-dim); margin-top: 6px; }

/* Tooltip */
.tooltip { position: absolute; background: var(--surface2); border: 1px solid var(--border); border-radius: var(--radius); padding: 8px 12px; font-size: 12px; pointer-events: none; z-index: 200; max-width: 250px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }

/* Loading */
.loading { text-align: center; padding: 40px; color: var(--text-dim); }
</style>
</head>
<body>
<div class="app">
  <div class="sidebar">
    <h1>MYTHOS EXPLORER</h1>
    <div class="nav">
      <button class="nav-item active" data-view="dashboard">Dashboard</button>
      <button class="nav-item" data-view="entities">Entities <span class="count" id="entity-count">-</span></button>
      <button class="nav-item" data-view="coordinates">Coordinate Space</button>
      <button class="nav-item" data-view="cooccurrence">Co-occurrence</button>
      <button class="nav-item" data-view="motifs">Motifs</button>
      <button class="nav-item" data-view="validation">Validation</button>
    </div>
  </div>
  <div class="main" id="main">
    <div class="loading">Loading...</div>
  </div>
</div>
<div class="detail-panel" id="detail-panel">
  <button class="close-btn" onclick="closeDetail()">&times;</button>
  <div id="detail-content"></div>
</div>
<div class="tooltip" id="tooltip" style="display:none"></div>
<script>
const API = '';
let currentView = 'dashboard';
let summaryData = null;

// ── Navigation ──────────────────────────────────────
document.querySelectorAll('.nav-item').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentView = btn.dataset.view;
    renderView(currentView);
  });
});

async function fetchJSON(url) {
  const res = await fetch(API + url);
  return res.json();
}

async function init() {
  summaryData = await fetchJSON('/api/summary');
  document.getElementById('entity-count').textContent = summaryData.library.entities;
  renderView('dashboard');
}

function renderView(view) {
  closeDetail();
  const main = document.getElementById('main');
  main.innerHTML = '<div class="loading">Loading...</div>';

  switch(view) {
    case 'dashboard': renderDashboard(); break;
    case 'entities': renderEntities(); break;
    case 'coordinates': renderCoordinates(); break;
    case 'cooccurrence': renderCooccurrence(); break;
    case 'motifs': renderMotifs(); break;
    case 'validation': renderValidation(); break;
  }
}

// ── Dashboard ───────────────────────────────────────
async function renderDashboard() {
  const d = summaryData || await fetchJSON('/api/summary');
  const main = document.getElementById('main');
  const mapped = d.mappings.mapped_entities;
  const total = d.mappings.total_entities;
  main.innerHTML = `
    <h2>Dashboard</h2>
    <div class="stats">
      <div class="stat"><div class="value">${d.library.texts}</div><div class="label">Texts</div></div>
      <div class="stat"><div class="value">${d.library.traditions}</div><div class="label">Traditions</div></div>
      <div class="stat"><div class="value">${d.library.entities}</div><div class="label">Entities</div></div>
      <div class="stat"><div class="value">${d.library.segments.toLocaleString()}</div><div class="label">Segments</div></div>
      <div class="stat"><div class="value">${d.library.mentions.toLocaleString()}</div><div class="label">Mentions</div></div>
      <div class="stat"><div class="value">${d.acp.archetypes}</div><div class="label">ACP Archetypes</div></div>
      <div class="stat"><div class="value">${mapped}/${total}</div><div class="label">Mapped (${d.mappings.coverage_pct}%)</div></div>
      <div class="stat"><div class="value">${d.library.motif_tags.toLocaleString()}</div><div class="label">Motif Tags</div></div>
    </div>
    <div class="card">
      <h3>Mapping Coverage</h3>
      <div style="height:24px;background:var(--border);border-radius:12px;overflow:hidden;margin-bottom:8px">
        <div style="height:100%;width:${d.mappings.coverage_pct}%;background:var(--green);border-radius:12px"></div>
      </div>
      <div style="display:flex;justify-content:space-between;font-size:13px;color:var(--text-dim)">
        <span>${mapped} mapped</span>
        <span>${total - mapped} unmapped</span>
      </div>
    </div>
    <div class="card">
      <h3>Quick Actions</h3>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button class="filter-btn" onclick="document.querySelector('[data-view=entities]').click()">Browse Entities</button>
        <button class="filter-btn" onclick="document.querySelector('[data-view=coordinates]').click()">View Coordinate Space</button>
        <button class="filter-btn" onclick="document.querySelector('[data-view=cooccurrence]').click()">Explore Co-occurrence</button>
      </div>
    </div>
  `;
}

// ── Entities ────────────────────────────────────────
let entityFilter = 'all';
let entitySearch = '';
let entitySort = 'mentions';

async function renderEntities() {
  const params = new URLSearchParams();
  if (entitySearch) params.set('q', entitySearch);
  params.set('sort', entitySort);
  if (entityFilter === 'mapped') params.set('mapped', 'true');
  if (entityFilter === 'unmapped') params.set('unmapped', 'true');

  const data = await fetchJSON('/api/entities?' + params);
  const main = document.getElementById('main');

  const mapped = data.entities.filter(e => e.mapped).length;
  const unmapped = data.entities.filter(e => !e.mapped).length;

  main.innerHTML = `
    <h2>Entities</h2>
    <div class="search-bar">
      <input type="text" placeholder="Search entities..." value="${entitySearch}" id="entity-search">
      <select id="entity-sort">
        <option value="mentions" ${entitySort==='mentions'?'selected':''}>Sort: Mentions</option>
        <option value="name" ${entitySort==='name'?'selected':''}>Sort: Name</option>
        <option value="confidence" ${entitySort==='confidence'?'selected':''}>Sort: Confidence</option>
      </select>
    </div>
    <div class="filters">
      <button class="filter-btn ${entityFilter==='all'?'active':''}" data-filter="all">All (${data.count})</button>
      <button class="filter-btn ${entityFilter==='mapped'?'active':''}" data-filter="mapped">Mapped (${mapped})</button>
      <button class="filter-btn ${entityFilter==='unmapped'?'active':''}" data-filter="unmapped">Unmapped (${unmapped})</button>
    </div>
    <table>
      <thead><tr>
        <th>Entity</th>
        <th>Type</th>
        <th>Mentions</th>
        <th>Traditions</th>
        <th>Mapping</th>
        <th>Confidence</th>
      </tr></thead>
      <tbody>
        ${data.entities.map(e => `
          <tr class="clickable" onclick="showEntityDetail('${e.name.replace(/'/g,"\\'")}')">
            <td><strong>${e.name}</strong></td>
            <td>${e.type || '-'}</td>
            <td>${e.mentions}</td>
            <td>${e.traditions.length}</td>
            <td>${e.mapped
              ? `<span class="badge badge-mapped">${e.mapping.acp_name}</span> <span class="badge badge-method">${e.mapping.method}</span>`
              : '<span class="badge badge-unmapped">unmapped</span>'}</td>
            <td>${e.mapped ? renderConfidence(e.mapping.confidence) : '-'}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;

  document.getElementById('entity-search').addEventListener('input', e => {
    entitySearch = e.target.value;
    renderEntities();
  });
  document.getElementById('entity-sort').addEventListener('change', e => {
    entitySort = e.target.value;
    renderEntities();
  });
  main.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      entityFilter = btn.dataset.filter;
      renderEntities();
    });
  });
}

function renderConfidence(c) {
  const pct = Math.round(c * 100);
  const cls = c >= 0.8 ? 'conf-high' : c >= 0.5 ? 'conf-med' : 'conf-low';
  return `<div class="conf-bar"><div class="conf-track"><div class="conf-fill ${cls}" style="width:${pct}%"></div></div><span style="font-size:12px">${c.toFixed(2)}</span></div>`;
}

// ── Entity Detail ───────────────────────────────────
async function showEntityDetail(name) {
  const data = await fetchJSON('/api/entity?name=' + encodeURIComponent(name));
  if (data.error) return;

  const panel = document.getElementById('detail-panel');
  const content = document.getElementById('detail-content');

  let acpHtml = '';
  if (data.acp) {
    const a = data.acp;
    acpHtml = `
      <div class="detail-section">
        <h4>ACP Mapping</h4>
        <div style="margin-bottom:8px">
          <strong>${a.archetype_name}</strong> <span class="badge badge-method">${a.method}</span>
          ${renderConfidence(a.confidence)}
        </div>
        <div style="font-size:12px;color:var(--text-dim);margin-bottom:8px">ID: ${a.archetype_id}</div>
        ${a.aliases.length ? `<div style="margin-bottom:8px">${a.aliases.map(al => `<span class="tag">${al.name}${al.fidelity ? ' ('+al.fidelity+')' : ''}</span>`).join('')}</div>` : ''}
        ${a.instantiates.length ? `<div style="margin-bottom:8px"><strong>Primordials:</strong> ${a.instantiates.map(i => `<span class="tag">${(i.primordial||'').split(':').pop()} (${i.weight||'?'})</span>`).join('')}</div>` : ''}
      </div>
      ${a.coordinates ? `
      <div class="detail-section">
        <h4>Spectral Coordinates</h4>
        ${Object.entries(a.coordinates).map(([axis, val]) => `
          <div class="coord-row">
            <span class="coord-label">${axis}</span>
            <div class="coord-bar-track"><div class="coord-bar-fill" style="width:${val*100}%;background:${val>0.5?'var(--accent)':'var(--accent2)'}"></div></div>
            <span class="coord-val">${val.toFixed(3)}</span>
          </div>
        `).join('')}
      </div>` : ''}
      ${a.nearby.length ? `
      <div class="detail-section">
        <h4>Nearby Archetypes (d &lt; 0.4)</h4>
        ${a.nearby.map(n => `<div style="display:flex;justify-content:space-between;padding:3px 0;font-size:13px"><span>${n.name}</span><span style="color:var(--text-dim)">${n.distance.toFixed(3)}</span></div>`).join('')}
      </div>` : ''}
    `;
  }

  content.innerHTML = `
    <h2>${data.name}</h2>
    <div class="subtitle">${data.type || 'entity'} &middot; ${data.mentions} mentions &middot; ${data.traditions.length} traditions</div>

    ${data.aliases.length ? `<div class="detail-section"><h4>Aliases</h4>${data.aliases.map(a => `<span class="tag">${a}</span>`).join('')}</div>` : ''}

    <div class="detail-section">
      <h4>Traditions</h4>
      ${data.traditions.map(t => `<div style="display:flex;justify-content:space-between;padding:2px 0;font-size:13px"><span>${t.tradition}</span><span style="color:var(--text-dim)">${t.count}</span></div>`).join('')}
    </div>

    ${acpHtml}

    <div class="detail-section">
      <h4>Top Co-occurring Entities</h4>
      ${data.cooccurrences.slice(0,12).map(c => `
        <div class="pair-row" style="cursor:pointer" onclick="showEntityDetail('${c.entity.replace(/'/g,"\\'")}')">
          <span class="pair-names">${c.entity}</span>
          <span class="pair-count">${c.count}</span>
        </div>
      `).join('')}
    </div>

    ${data.motifs.length ? `
    <div class="detail-section">
      <h4>Associated Motifs</h4>
      ${data.motifs.map(m => `<div style="display:flex;justify-content:space-between;padding:2px 0;font-size:13px"><span><strong>${m.code}</strong> ${m.label}</span><span style="color:var(--text-dim)">${m.count}</span></div>`).join('')}
    </div>` : ''}

    <div class="detail-section">
      <h4>Sample Passages</h4>
      ${data.samples.map(s => `<div class="sample">${s.text}${s.text.length>=500?'...':''}<div class="meta">${s.title} &middot; ${s.tradition}</div></div>`).join('')}
    </div>
  `;

  panel.classList.add('open');
}

function closeDetail() {
  document.getElementById('detail-panel').classList.remove('open');
}

// ── Coordinates ─────────────────────────────────────
let coordXAxis = 'order-chaos';
let coordYAxis = 'creation-destruction';

async function renderCoordinates() {
  const data = await fetchJSON(`/api/coordinates?x=${coordXAxis}&y=${coordYAxis}`);
  const main = document.getElementById('main');

  main.innerHTML = `
    <h2>Coordinate Space</h2>
    <div class="axis-selectors">
      <label>X Axis:</label>
      <select id="x-axis">${data.axes.map(a => `<option value="${a}" ${a===coordXAxis?'selected':''}>${a}</option>`).join('')}</select>
      <label>Y Axis:</label>
      <select id="y-axis">${data.axes.map(a => `<option value="${a}" ${a===coordYAxis?'selected':''}>${a}</option>`).join('')}</select>
    </div>
    <div class="scatter-container">
      <canvas id="scatter" width="900" height="600"></canvas>
    </div>
    <div class="card" style="margin-top:16px">
      <h3>Legend</h3>
      <div style="font-size:13px;color:var(--text-dim)">
        Circle size = mention count. Color = mapping confidence (green=high, orange=medium, red=low).
        Click a point to view entity details. Axes range from 0.0 to 1.0.
      </div>
    </div>
  `;

  document.getElementById('x-axis').addEventListener('change', e => { coordXAxis = e.target.value; renderCoordinates(); });
  document.getElementById('y-axis').addEventListener('change', e => { coordYAxis = e.target.value; renderCoordinates(); });

  drawScatter(data);
}

function drawScatter(data) {
  const canvas = document.getElementById('scatter');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  const pad = 60;

  ctx.fillStyle = '#0e1117';
  ctx.fillRect(0, 0, W, H);

  // Grid
  ctx.strokeStyle = '#21262d';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 10; i++) {
    const x = pad + (W - 2*pad) * i / 10;
    const y = pad + (H - 2*pad) * i / 10;
    ctx.beginPath(); ctx.moveTo(x, pad); ctx.lineTo(x, H-pad); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(pad, y); ctx.lineTo(W-pad, y); ctx.stroke();

    ctx.fillStyle = '#484f58';
    ctx.font = '11px monospace';
    ctx.textAlign = 'center';
    ctx.fillText((i/10).toFixed(1), x, H-pad+16);
    ctx.textAlign = 'right';
    ctx.fillText((1-i/10).toFixed(1), pad-8, y+4);
  }

  // Axis labels
  ctx.fillStyle = '#8b949e';
  ctx.font = '13px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(data.x_axis, W/2, H-10);
  ctx.save();
  ctx.translate(14, H/2);
  ctx.rotate(-Math.PI/2);
  ctx.fillText(data.y_axis, 0, 0);
  ctx.restore();

  // Points
  const maxMentions = Math.max(...data.points.map(p => p.mentions), 1);
  const pointData = [];

  data.points.forEach(p => {
    const px = pad + (W - 2*pad) * p.x;
    const py = pad + (H - 2*pad) * (1 - p.y);
    const r = 4 + Math.sqrt(p.mentions / maxMentions) * 16;

    let color;
    if (p.confidence >= 0.8) color = 'rgba(63,185,80,0.7)';
    else if (p.confidence >= 0.5) color = 'rgba(210,153,34,0.7)';
    else color = 'rgba(248,81,73,0.7)';

    ctx.beginPath();
    ctx.arc(px, py, r, 0, Math.PI*2);
    ctx.fillStyle = color;
    ctx.fill();
    ctx.strokeStyle = color.replace('0.7', '1');
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Label for larger points
    if (r > 8) {
      ctx.fillStyle = '#c9d1d9';
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(p.name, px, py - r - 4);
    }

    pointData.push({...p, px, py, r});
  });

  // Hover/click
  canvas.onclick = e => {
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    for (const p of pointData) {
      if (Math.hypot(mx - p.px, my - p.py) < p.r + 2) {
        showEntityDetail(p.name);
        return;
      }
    }
  };

  canvas.onmousemove = e => {
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const tooltip = document.getElementById('tooltip');

    for (const p of pointData) {
      if (Math.hypot(mx - p.px, my - p.py) < p.r + 2) {
        tooltip.style.display = 'block';
        tooltip.style.left = (e.clientX + 12) + 'px';
        tooltip.style.top = (e.clientY - 10) + 'px';
        tooltip.innerHTML = `<strong>${p.name}</strong> &rarr; ${p.acp_name}<br>
          ${data.x_axis}: ${p.x.toFixed(3)}<br>
          ${data.y_axis}: ${p.y.toFixed(3)}<br>
          Mentions: ${p.mentions}<br>
          ${p.primordials.length ? 'Primordials: ' + p.primordials.join(', ') : ''}`;
        canvas.style.cursor = 'pointer';
        return;
      }
    }
    tooltip.style.display = 'none';
    canvas.style.cursor = 'default';
  };
}

// ── Co-occurrence ───────────────────────────────────
async function renderCooccurrence() {
  const data = await fetchJSON('/api/cooccurrence?min=3');
  const main = document.getElementById('main');

  const maxCount = Math.max(...data.pairs.map(p => p.count), 1);

  main.innerHTML = `
    <h2>Co-occurrence Pairs</h2>
    <div class="search-bar">
      <input type="text" placeholder="Filter by entity name..." id="coocc-search">
      <select id="coocc-min">
        <option value="2">Min count: 2</option>
        <option value="3" selected>Min count: 3</option>
        <option value="5">Min count: 5</option>
        <option value="10">Min count: 10</option>
      </select>
    </div>
    <div class="card">
      <h3>Top co-occurring entity pairs</h3>
      <div style="color:var(--text-dim);font-size:12px;margin-bottom:12px">
        Count = shared segments. Distance = ACP Euclidean distance (lower = more similar).
      </div>
      <table>
        <thead><tr><th>Entity 1</th><th>Entity 2</th><th>Co-occurrences</th><th>ACP Distance</th><th>Status</th></tr></thead>
        <tbody id="coocc-body">
          ${data.pairs.map(p => `
            <tr>
              <td><span class="clickable" onclick="showEntityDetail('${p.entity1.replace(/'/g,"\\'")}')" style="color:var(--accent)">${p.entity1}</span></td>
              <td><span class="clickable" onclick="showEntityDetail('${p.entity2.replace(/'/g,"\\'")}')" style="color:var(--accent)">${p.entity2}</span></td>
              <td>
                <div style="display:flex;align-items:center;gap:8px">
                  <div style="width:80px;height:6px;background:var(--border);border-radius:3px;overflow:hidden">
                    <div style="height:100%;width:${p.count/maxCount*100}%;background:var(--accent);border-radius:3px"></div>
                  </div>
                  ${p.count}
                </div>
              </td>
              <td style="font-family:monospace;color:${p.distance !== null ? (p.distance < 0.5 ? 'var(--green)' : p.distance > 1.0 ? 'var(--red)' : 'var(--text)') : 'var(--text-dim)'}">${p.distance !== null ? p.distance.toFixed(3) : 'n/a'}</td>
              <td>${p.both_mapped ? '<span class="badge badge-mapped">both mapped</span>' : '<span class="badge badge-unmapped">partial</span>'}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;

  document.getElementById('coocc-search').addEventListener('input', async e => {
    const q = e.target.value.toLowerCase();
    const rows = document.querySelectorAll('#coocc-body tr');
    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(q) ? '' : 'none';
    });
  });

  document.getElementById('coocc-min').addEventListener('change', async e => {
    const data2 = await fetchJSON('/api/cooccurrence?min=' + e.target.value);
    // Re-render with new min
    const tbody = document.getElementById('coocc-body');
    const max2 = Math.max(...data2.pairs.map(p => p.count), 1);
    tbody.innerHTML = data2.pairs.map(p => `
      <tr>
        <td><span class="clickable" onclick="showEntityDetail('${p.entity1.replace(/'/g,"\\'")}')" style="color:var(--accent)">${p.entity1}</span></td>
        <td><span class="clickable" onclick="showEntityDetail('${p.entity2.replace(/'/g,"\\'")}')" style="color:var(--accent)">${p.entity2}</span></td>
        <td>
          <div style="display:flex;align-items:center;gap:8px">
            <div style="width:80px;height:6px;background:var(--border);border-radius:3px;overflow:hidden">
              <div style="height:100%;width:${p.count/max2*100}%;background:var(--accent);border-radius:3px"></div>
            </div>
            ${p.count}
          </div>
        </td>
        <td style="font-family:monospace;color:${p.distance !== null ? (p.distance < 0.5 ? 'var(--green)' : p.distance > 1.0 ? 'var(--red)' : 'var(--text)') : 'var(--text-dim)'}">${p.distance !== null ? p.distance.toFixed(3) : 'n/a'}</td>
        <td>${p.both_mapped ? '<span class="badge badge-mapped">both mapped</span>' : '<span class="badge badge-unmapped">partial</span>'}</td>
      </tr>
    `).join('');
  });
}

// ── Motifs ───────────────────────────────────────────
async function renderMotifs() {
  const data = await fetchJSON('/api/motifs');
  const main = document.getElementById('main');

  main.innerHTML = `
    <h2>Thompson Motifs</h2>
    <div class="search-bar">
      <input type="text" placeholder="Search motifs..." id="motif-search">
    </div>
    <table>
      <thead><tr><th>Code</th><th>Category</th><th>Label</th><th>Segments</th></tr></thead>
      <tbody id="motif-body">
        ${data.motifs.map(m => `
          <tr>
            <td><strong>${m.code}</strong></td>
            <td>${m.category || '-'}</td>
            <td>${m.label}</td>
            <td>${m.segments}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;

  document.getElementById('motif-search').addEventListener('input', e => {
    const q = e.target.value.toLowerCase();
    document.querySelectorAll('#motif-body tr').forEach(row => {
      row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
  });
}

// ── Validation ──────────────────────────────────────
async function renderValidation() {
  const data = await fetchJSON('/api/validation');
  const main = document.getElementById('main');

  if (!data || !data.coordinate_validation) {
    main.innerHTML = '<h2>Validation</h2><p>No validation results found. Run the validation suite first.</p>';
    return;
  }

  const cv = data.coordinate_validation;
  const cvClean = data.coordinate_validation_clean || {};
  const pc = data.primordial_clustering || {};

  const primSorted = Object.entries(pc).sort((a,b) => a[1].mean_distance - b[1].mean_distance);

  main.innerHTML = `
    <h2>Validation Results</h2>
    <div class="stats">
      <div class="stat"><div class="value">${cv.total_pairs || '-'}</div><div class="label">Entity Pairs</div></div>
      <div class="stat"><div class="value">${cv.all_pairs ? cv.all_pairs.pearson_r.toFixed(4) : '-'}</div><div class="label">Pearson r (all)</div></div>
      <div class="stat"><div class="value">${cvClean.all_pairs ? cvClean.all_pairs.pearson_r.toFixed(4) : '-'}</div><div class="label">Pearson r (excl. Set)</div></div>
      <div class="stat"><div class="value">${cv.hypothesis || '-'}</div><div class="label">Hypothesis</div></div>
    </div>

    <div class="card">
      <h3>Correlation: All Entities</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;font-size:14px">
        <div>
          <strong>All pairs (${cv.total_pairs})</strong><br>
          Pearson r: <code>${cv.all_pairs?.pearson_r?.toFixed(4)}</code> (p=${cv.all_pairs?.pearson_p?.toFixed(6)})<br>
          Spearman r: <code>${cv.all_pairs?.spearman_r?.toFixed(4)}</code> (p=${cv.all_pairs?.spearman_p?.toFixed(6)})
        </div>
        <div>
          <strong>Non-zero pairs (${cv.nonzero_pairs?.count || '-'})</strong><br>
          Pearson r: <code>${cv.nonzero_pairs?.pearson_r?.toFixed(4)}</code> (p=${cv.nonzero_pairs?.pearson_p?.toFixed(6)})<br>
          Spearman r: <code>${cv.nonzero_pairs?.spearman_r?.toFixed(4)}</code> (p=${cv.nonzero_pairs?.spearman_p?.toFixed(6)})
        </div>
      </div>
      <div style="margin-top:12px;padding:12px;background:var(--surface2);border-radius:var(--radius)">
        <strong>${cv.hypothesis}</strong>: ${cv.interpretation}
      </div>
    </div>

    ${cvClean.all_pairs ? `
    <div class="card">
      <h3>Correlation: Excluding "Set" (known false positive)</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;font-size:14px">
        <div>
          <strong>All pairs (${cvClean.total_pairs})</strong><br>
          Pearson r: <code>${cvClean.all_pairs?.pearson_r?.toFixed(4)}</code> (p=${cvClean.all_pairs?.pearson_p?.toFixed(6)})<br>
          Spearman r: <code>${cvClean.all_pairs?.spearman_r?.toFixed(4)}</code> (p=${cvClean.all_pairs?.spearman_p?.toFixed(6)})
        </div>
        <div>
          <strong>Non-zero pairs (${cvClean.nonzero_pairs?.count || '-'})</strong><br>
          Pearson r: <code>${cvClean.nonzero_pairs?.pearson_r?.toFixed(4)}</code><br>
          Spearman r: <code>${cvClean.nonzero_pairs?.spearman_r?.toFixed(4)}</code>
        </div>
      </div>
      <div style="margin-top:12px;padding:12px;background:var(--surface2);border-radius:var(--radius)">
        <strong>${cvClean.hypothesis}</strong>: ${cvClean.interpretation}
      </div>
    </div>` : ''}

    ${cv.top_cooccurring ? `
    <div class="card">
      <h3>Top Co-occurring Pairs</h3>
      <table>
        <thead><tr><th>Entity 1</th><th>Entity 2</th><th>Distance</th><th>Co-occurrences</th></tr></thead>
        <tbody>
          ${cv.top_cooccurring.slice(0,15).map(p => `
            <tr>
              <td>${p.entities[0]}</td>
              <td>${p.entities[1]}</td>
              <td style="font-family:monospace">${p.distance.toFixed(3)}</td>
              <td>${p.cooccurrence}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>` : ''}

    ${cv.outliers ? `
    <div class="card">
      <h3>Outliers</h3>
      <table>
        <thead><tr><th>Type</th><th>Entity 1</th><th>Entity 2</th><th>Distance</th><th>Co-occurrences</th></tr></thead>
        <tbody>
          ${cv.outliers.map(o => `
            <tr>
              <td><span class="tag">${o.anomaly_type}</span></td>
              <td>${o.entities[0]}</td>
              <td>${o.entities[1]}</td>
              <td style="font-family:monospace">${o.distance.toFixed(3)}</td>
              <td>${o.cooccurrence}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>` : ''}

    ${primSorted.length ? `
    <div class="card">
      <h3>Primordial Clustering</h3>
      <table>
        <thead><tr><th>Primordial</th><th>Archetypes</th><th>Mean Distance</th><th>Std</th><th>Cohesion</th></tr></thead>
        <tbody>
          ${primSorted.map(([name, d]) => `
            <tr>
              <td><strong>${name}</strong></td>
              <td>${d.archetype_count}</td>
              <td style="font-family:monospace">${d.mean_distance.toFixed(3)}</td>
              <td style="font-family:monospace">${d.std_distance.toFixed(3)}</td>
              <td>
                <div style="width:120px;height:6px;background:var(--border);border-radius:3px;overflow:hidden">
                  <div style="height:100%;width:${Math.max(0, 100-(d.mean_distance*100))}%;background:${d.mean_distance < 0.5 ? 'var(--green)' : d.mean_distance < 0.7 ? 'var(--orange)' : 'var(--red)'};border-radius:3px"></div>
                </div>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>` : ''}
  `;
}

// Close detail on Escape
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeDetail(); });

// ── Init ────────────────────────────────────────────
init();
</script>
</body>
</html>"""


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    load_data()
    server = HTTPServer(("127.0.0.1", PORT), ExplorerHandler)
    url = f"http://127.0.0.1:{PORT}"
    print(f"\n  MythOS Explorer running at {url}")
    print(f"  Press Ctrl+C to stop\n")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        db.close()
        server.server_close()


if __name__ == "__main__":
    main()
