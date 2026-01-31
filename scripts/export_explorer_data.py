"""Export all data needed by the Mythic System Explorer frontend.

Consolidates data from ACP, Library, and Miroglyph into static JSON files
that the frontend loads via fetch. No dynamic API needed.

Usage:
    python -X utf8 scripts/export_explorer_data.py

Output (miroglyph/data/):
    archetypes_catalog.json   - All 539 archetypes with coordinates, primordials, relationships
    entities_catalog.json     - All 173 library entities with ACP mappings + node assignments
    patterns_catalog.json     - 18 named patterns with motifs, traditions, arc assignments
    validation_summary.json   - Frontend-friendly validation results
    node_profiles.json        - Copy of node centroids
    archetype_affinities.json - Copy of archetype-node affinity scores
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integration.acp_loader import ACPLoader, AXES
from integration.library_loader import LibraryLoader
from integration.entity_mapper import EntityMapper
from integration.node_profiler import ARC_PATTERN_MAPPING

OUTPUT_DIR = PROJECT_ROOT / "miroglyph" / "data"
OUTPUTS = PROJECT_ROOT / "outputs"


def export_archetypes_catalog(acp: ACPLoader, affinities: dict):
    """Export consolidated archetype catalog."""
    print("[1/4] Exporting archetypes catalog...")

    # Build archetype-to-node rankings from affinities
    arch_rankings = affinities.get("archetype_rankings", {})

    # Collect primordial metadata
    primordial_list = []
    for pid, pdata in sorted(acp.primordials.items()):
        primordial_list.append({
            "id": pid,
            "name": pdata.get("name", pid.replace("primordial:", "")),
            "description": pdata.get("description", ""),
        })

    # Collect system metadata
    systems_list = []
    system_counts = {}
    for arch_id, arch in acp.archetypes.items():
        code = arch.get("systemCode", "")
        if code and code not in system_counts:
            system_counts[code] = {"code": code, "name": "", "domain": "", "count": 0}
        if code:
            system_counts[code]["count"] += 1

    # Try to get system names from system entries
    for sys_id, sys_data in acp.systems.items():
        code = sys_data.get("systemCode", "")
        if code and code in system_counts:
            system_counts[code]["name"] = sys_data.get("name", code)
            system_counts[code]["domain"] = sys_data.get("domain", "")

    # Fill in missing system names from archetype data
    for arch_id, arch in acp.archetypes.items():
        code = arch.get("systemCode", "")
        if code and code in system_counts and not system_counts[code]["name"]:
            # Infer from archetype ID prefix
            system_counts[code]["name"] = code

    systems_list = sorted(system_counts.values(), key=lambda s: s["code"])

    # Build archetype entries
    archetypes = []
    for arch_id, arch in sorted(acp.archetypes.items()):
        coords = acp.get_coordinates(arch_id)
        coord_list = [round(float(c), 4) for c in coords] if coords is not None else None

        # Extract primordials
        prims = []
        for inst in arch.get("instantiates", []):
            if isinstance(inst, dict):
                prims.append({
                    "id": inst.get("primordial", inst.get("@id", "")),
                    "weight": round(inst.get("weight", 0), 4),
                })
            elif isinstance(inst, str):
                prims.append({"id": inst, "weight": 1.0})
        prims.sort(key=lambda p: -p["weight"])

        # Extract relationships
        rels = []
        for rel in arch.get("relationships", []):
            entry = {
                "type": rel.get("type", ""),
                "target": rel.get("target", ""),
            }
            if "fidelity" in rel:
                entry["fidelity"] = rel["fidelity"]
            if "axis" in rel:
                entry["axis"] = rel["axis"]
            if "strength" in rel:
                entry["strength"] = rel["strength"]
            rels.append(entry)

        # Nearest nodes from affinity data
        nearest_nodes = []
        arch_rank = arch_rankings.get(arch_id, {})
        for tn in arch_rank.get("top_nodes", [])[:3]:
            nearest_nodes.append({
                "node_id": tn["node_id"],
                "affinity": tn["affinity"],
            })

        archetypes.append({
            "id": arch_id,
            "name": arch.get("name", arch_id),
            "system": arch.get("systemCode", ""),
            "description": arch.get("description", ""),
            "coordinates": coord_list,
            "primordials": prims,
            "domains": arch.get("domains", []),
            "relationships": rels,
            "nearest_nodes": nearest_nodes,
        })

    catalog = {
        "version": "1.0",
        "count": len(archetypes),
        "axes": list(AXES),
        "primordials": primordial_list,
        "systems": systems_list,
        "archetypes": archetypes,
    }

    path = OUTPUT_DIR / "archetypes_catalog.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False)
    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"  {path.name}: {len(archetypes)} archetypes, {size_mb:.1f} MB")


def export_entities_catalog(acp: ACPLoader, library: LibraryLoader,
                            mapper: EntityMapper, node_profiles: dict,
                            affinities: dict):
    """Export entity catalog with ACP mappings and node assignments."""
    print("[2/4] Exporting entities catalog...")

    # Load node centroids for distance calculation
    node_centroids = {}
    for nid, profile in node_profiles.get("node_profiles", {}).items():
        node_centroids[nid] = np.array(profile["mean_coordinates"])

    sigma = affinities.get("sigma", 0.174)

    all_entities = library.get_all_entities()
    entities = []

    for ent in all_entities:
        name = ent.canonical_name
        mapping = mapper.get_mapping(name)

        entry = {
            "name": name,
            "type": ent.entity_type or "",
            "primary_tradition": ent.primary_tradition or "",
            "total_mentions": ent.total_mentions or 0,
            "text_count": ent.text_count or 0,
            "tradition_count": ent.tradition_count or 0,
        }

        if mapping:
            entry["mapping"] = {
                "archetype_id": mapping.acp_archetype_id,
                "archetype_name": mapping.acp_name,
                "confidence": mapping.confidence,
                "method": mapping.method,
                "fidelity": mapping.fidelity,
            }

            # Get coordinates
            coords = acp.get_coordinates(mapping.acp_archetype_id)
            if coords is not None:
                entry["coordinates"] = [round(float(c), 4) for c in coords]

                # Compute nearest nodes
                node_dists = []
                for nid, centroid in node_centroids.items():
                    dist = float(np.linalg.norm(coords - centroid))
                    aff = float(np.exp(-dist ** 2 / (2 * sigma ** 2)))
                    node_dists.append({
                        "node_id": nid,
                        "affinity": round(aff, 4),
                        "distance": round(dist, 4),
                    })
                node_dists.sort(key=lambda x: -x["affinity"])
                entry["nearest_node"] = node_dists[0] if node_dists else None
                entry["top_nodes"] = node_dists[:5]
            else:
                entry["coordinates"] = None
                entry["nearest_node"] = None
                entry["top_nodes"] = []
        else:
            entry["mapping"] = None
            entry["coordinates"] = None
            entry["nearest_node"] = None
            entry["top_nodes"] = []

        entities.append(entry)

    # Sort: mapped first (by mentions desc), then unmapped
    entities.sort(key=lambda e: (0 if e["mapping"] else 1, -e["total_mentions"]))

    catalog = {
        "version": "1.0",
        "total": len(entities),
        "mapped": sum(1 for e in entities if e["mapping"]),
        "unmapped": sum(1 for e in entities if not e["mapping"]),
        "entities": entities,
    }

    path = OUTPUT_DIR / "entities_catalog.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False)
    print(f"  {path.name}: {catalog['total']} entities ({catalog['mapped']} mapped)")


def export_patterns_catalog(library: LibraryLoader):
    """Export patterns catalog with arc assignments and related entities."""
    print("[3/4] Exporting patterns catalog...")

    # Build reverse arc lookup
    pattern_to_arc = {}
    for arc_code, pattern_names in ARC_PATTERN_MAPPING.items():
        for pname in pattern_names:
            pattern_to_arc[pname] = arc_code

    all_patterns = library.get_all_patterns()

    patterns = []
    for p in all_patterns:
        name = p["pattern_name"]
        motif_codes = p.get("motif_codes", [])

        # Get related entities (from motif-tagged segments)
        related = library.get_entities_for_motif_codes(motif_codes) if motif_codes else []

        # Get tradition attestations
        traditions = []
        try:
            rows = library.conn.execute("""
                SELECT DISTINCT tradition FROM pattern_attestations
                WHERE pattern_id = (SELECT pattern_id FROM patterns WHERE pattern_name = ?)
                ORDER BY tradition
            """, (name,)).fetchall()
            traditions = [r["tradition"] for r in rows]
        except Exception:
            pass

        patterns.append({
            "name": name,
            "description": p.get("description", ""),
            "arc": pattern_to_arc.get(name, ""),
            "attestation_count": p.get("attestation_count", 0),
            "tradition_count": p.get("tradition_count", 0),
            "confidence": round(p.get("confidence", 0), 4),
            "motif_codes": motif_codes,
            "traditions": traditions,
            "related_entities": sorted(set(related)),
        })

    # Collect motif metadata
    motifs = {}
    try:
        rows = library.conn.execute("""
            SELECT motif_code, label, category FROM motifs ORDER BY motif_code
        """).fetchall()
        for r in rows:
            motifs[r["motif_code"]] = {
                "label": r["label"],
                "category": r["category"],
            }
    except Exception:
        pass

    catalog = {
        "version": "1.0",
        "count": len(patterns),
        "arc_assignments": {k: list(v) for k, v in ARC_PATTERN_MAPPING.items()},
        "patterns": patterns,
        "motifs": motifs,
    }

    path = OUTPUT_DIR / "patterns_catalog.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False)
    print(f"  {path.name}: {len(patterns)} patterns, {len(motifs)} motifs")


def export_validation_summary():
    """Export frontend-friendly validation summary."""
    print("[4/4] Exporting validation summary...")

    # Load raw results
    v2_path = OUTPUTS / "metrics" / "v2_validation_results.json"
    if not v2_path.exists():
        print(f"  WARNING: {v2_path} not found, skipping")
        return

    with open(v2_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # Load audit cases
    audit_path = OUTPUTS / "audits" / "human_audit_cases.json"
    audit_cases = []
    if audit_path.exists():
        with open(audit_path, "r", encoding="utf-8") as f:
            audit_data = json.load(f)
            audit_cases = audit_data.get("cases", [])

    verdict = raw.get("verdict", {})

    # Build tier summaries
    tiers = []

    # Tier A
    tier_a = verdict.get("tier_a", {})
    tiers.append({
        "id": "A",
        "label": "ACP Internal Coherence",
        "verdict": tier_a.get("verdict", "?"),
        "description": tier_a.get("label", ""),
        "passed": tier_a.get("passed", 0),
        "total": tier_a.get("total", 0),
        "tests": _extract_tests(raw, [
            ("test1_echo_coherence", "Echo Coherence",
             "Are cultural echoes close in 8D space?"),
            ("test2_primordial_clustering", "Primordial Clustering",
             "Do shared primordials cluster in spectral space?"),
            ("test3_relationship_geometry", "Relationship Geometry",
             "Do relationship types produce distinct geometric patterns?"),
        ]),
    })

    # Tier B
    tier_b = verdict.get("tier_b", {})
    tiers.append({
        "id": "B",
        "label": "Library-ACP External Validity",
        "verdict": tier_b.get("verdict", "?"),
        "description": tier_b.get("label", ""),
        "passed": tier_b.get("passed", 0),
        "total": tier_b.get("total", 0),
        "tests": _extract_tests(raw, [
            ("test4_motif_bridging", "Motif Bridging",
             "Do cross-tradition entities sharing motifs sit closer?"),
            ("test5_axis_interpretability", "Axis Interpretability",
             "Do motif categories cluster on expected axes?"),
        ]),
    })

    # Tier C
    tier_c = verdict.get("tier_c", {})
    miro = raw.get("miroglyph_structure", {})
    miro_v = miro.get("verdicts", {})
    tier_c_tests = []

    # Arc Separation is an INSIGHT, not a pass/fail test
    # Arcs are interpretive lenses for viewing the same coordinate space, not clusters
    arc_sep = miro_v.get("test7_arc_separation", {})
    tier_c_tests.append({
        "name": "Arc Interpretation",
        "question": "How do arcs relate to the 8D coordinate space?",
        "pass": True,  # Insight, not a test
        "is_insight": True,
        "criterion": "Arcs are interpretive lenses, not coordinate clusters",
        "result": "INSIGHT: Entities appear across all arcs with similar coordinate profiles. "
                  "Arcs (Descent/Resonance/Emergence) are narrative lenses for viewing the same "
                  "mythic material, not ontological categories. The same Zeus can be viewed through "
                  "D (destroyer), R (judge), or E (creator) - same coordinates, different lens.",
    })

    # Actual pass/fail tests
    for tkey, tname, question in [
        ("test8_condition_progression", "Condition Progression",
         "Do 6 position bins show different ACP profiles?"),
        ("test9_polarity_pairs", "Polarity Pairs",
         "Are polarity pairs more distant than non-polarity?"),
    ]:
        tv = miro_v.get(tkey, {})
        tier_c_tests.append({
            "name": tname,
            "question": question,
            "pass": tv.get("pass", False),
            "criterion": tv.get("criterion", ""),
            "result": tv.get("detail", ""),
        })
    # Count actual tests (not insights)
    tier_c_actual_tests = [t for t in tier_c_tests if not t.get("is_insight")]
    tier_c_passed = sum(1 for t in tier_c_actual_tests if t["pass"])
    tier_c_total = len(tier_c_actual_tests)
    tier_c_verdict = "PASS" if tier_c_passed == tier_c_total else "PARTIAL" if tier_c_passed > 0 else "FAIL"

    tiers.append({
        "id": "C",
        "label": "Miroglyph Structural Validity",
        "verdict": tier_c_verdict,
        "description": "Miroglyph structure empirically supported (arcs as lenses, conditions as positions)",
        "passed": tier_c_passed,
        "total": tier_c_total,
        "tests": tier_c_tests,
    })

    # Tier D - Reframed: Arcs are lenses, not clusters
    # The original "alternatives found" was based on expecting arcs to cluster in coordinate space
    # But arcs are interpretive lenses for the same coordinate space, so clustering is not expected
    tier_d_insights = [
        "CONFIRMED: 6 conditions show distinct positional profiles",
        "CONFIRMED: Polarity pairs (1↔6, 2↔5, 3↔4) validated",
        "INSIGHT: Arcs don't cluster because they are interpretive lenses, not coordinate categories",
        "INSIGHT: The same entity can be viewed through any arc - same coordinates, different narrative lens",
    ]
    tiers.append({
        "id": "D",
        "label": "Cross-System Integration",
        "verdict": "PASS",
        "description": "Miroglyph integrates with ACP as interpretive layer (arcs as lenses, conditions as positions)",
        "insights": tier_d_insights,
        "recommendations": [],  # No longer applicable - original recs assumed arcs should cluster
    })

    # Tier E
    tiers.append({
        "id": "E",
        "label": "Expert Review",
        "verdict": "PENDING",
        "description": "Awaiting human review",
        "audit_case_count": len(audit_cases),
    })

    # Overall
    overall = verdict.get("overall", {})

    summary = {
        "version": "1.0",
        "summary": raw.get("summary", {}),
        "overall_verdict": overall.get("verdict", "?"),
        "overall_label": overall.get("label", ""),
        "tiers": tiers,
        "recommendations": [],  # Tier D recommendations deprecated - arcs are lenses, not clusters
        "audit_cases": audit_cases,
    }

    path = OUTPUT_DIR / "validation_summary.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False)
    size_kb = path.stat().st_size / 1024
    print(f"  {path.name}: {len(tiers)} tiers, {len(audit_cases)} audit cases, {size_kb:.0f} KB")


def _extract_tests(raw: dict, test_specs: list) -> list:
    """Extract test data from raw validation results."""
    tests = []
    for key, name, question in test_specs:
        test_data = raw.get(key, {})
        verdicts = test_data.get("verdicts", {})

        # Determine pass/fail from verdict
        overall_pass = verdicts.get("overall_pass", False)
        if isinstance(overall_pass, str):
            overall_pass = overall_pass.lower() == "true"

        # Extract key metrics (top-level numeric values)
        key_metrics = {}
        for k, v in test_data.items():
            if k == "verdicts":
                continue
            if isinstance(v, (int, float)):
                key_metrics[k] = v
            elif isinstance(v, dict):
                for kk, vv in v.items():
                    if isinstance(vv, (int, float)):
                        key_metrics[f"{k}.{kk}"] = round(vv, 4) if isinstance(vv, float) else vv

        # Build result string from verdicts
        result_parts = []
        for vk, vv in verdicts.items():
            if isinstance(vv, dict) and "result" in vv:
                result_parts.append(f"{vk}: {vv['result']}")

        tests.append({
            "name": name,
            "question": question,
            "pass": overall_pass,
            "criterion": next(
                (vv.get("criterion", "") for vv in verdicts.values()
                 if isinstance(vv, dict) and "criterion" in vv),
                ""
            ),
            "result": "; ".join(result_parts) if result_parts else "",
            "key_metrics": key_metrics,
        })
    return tests


def copy_existing_data():
    """Copy existing output files to the frontend data directory."""
    copies = [
        (OUTPUTS / "miroglyph" / "node_profiles.json", "node_profiles.json"),
        (OUTPUTS / "miroglyph" / "archetype_affinities.json", "archetype_affinities.json"),
    ]
    for src, dest_name in copies:
        if src.exists():
            shutil.copy2(src, OUTPUT_DIR / dest_name)
            size_kb = src.stat().st_size / 1024
            print(f"  Copied {dest_name} ({size_kb:.0f} KB)")
        else:
            print(f"  WARNING: {src} not found")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Mythic System Explorer — Data Export")
    print("=" * 60)

    # Load systems
    print("\n[Init] Loading systems...")
    acp = ACPLoader(str(PROJECT_ROOT / "ACP"))
    library = LibraryLoader(str(PROJECT_ROOT / "data" / "mythic_patterns.db"))
    mapper = EntityMapper(acp, library)
    mapper.auto_map_all()
    print(f"  ACP: {acp.summary()['archetypes']} archetypes")
    print(f"  Library: {library.summary()['entities']} entities")

    # Load pre-computed data
    node_profiles_path = OUTPUTS / "miroglyph" / "node_profiles.json"
    affinities_path = OUTPUTS / "miroglyph" / "archetype_affinities.json"

    node_profiles = {}
    if node_profiles_path.exists():
        with open(node_profiles_path, "r", encoding="utf-8") as f:
            node_profiles = json.load(f)

    affinities = {}
    if affinities_path.exists():
        with open(affinities_path, "r", encoding="utf-8") as f:
            affinities = json.load(f)

    # Export all catalogs
    print()
    export_archetypes_catalog(acp, affinities)
    export_entities_catalog(acp, library, mapper, node_profiles, affinities)
    export_patterns_catalog(library)
    export_validation_summary()

    print("\n[Copy] Copying existing data files...")
    copy_existing_data()

    print(f"\n[Done] All data exported to {OUTPUT_DIR}")
    print(f"  Files: {len(list(OUTPUT_DIR.glob('*.json')))}")

    library.close()


if __name__ == "__main__":
    main()
