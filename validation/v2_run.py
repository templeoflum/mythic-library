#!/usr/bin/env python3
"""ACP v2 Validation Suite — Cross-Cultural Structural Equivalence.

Usage:
    python -m validation.v2_run              # Full validation (default)
    python -m validation.v2_run --full       # Full validation (explicit)
    python -m validation.v2_run --quick      # Skip permutation tests
    python -m validation.v2_run --report     # Generate markdown report

Run from the project root directory.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integration.acp_loader import ACPLoader
from integration.library_loader import LibraryLoader
from integration.entity_mapper import EntityMapper
from validation.v2_tests.echo_coherence import EchoCoherenceTest
from validation.v2_tests.primordial_clustering import PrimordialClusteringTest
from validation.v2_tests.relationship_geometry import RelationshipGeometryTest
from validation.v2_tests.motif_bridging import MotifBridgingTest
from validation.v2_tests.axis_interpretability import AxisInterpretabilityTest
from validation.v2_tests.human_audit import HumanAuditTest
from validation.v2_tests.miroglyph_structure import MiroStructureTest
from integration.miroglyph_loader import MiroGlyphLoader
from integration.node_profiler import NodeProfiler

ACP_PATH = PROJECT_ROOT / "ACP"
MIRO_SPEC = PROJECT_ROOT / "miroglyph" / "miroglyph_v4_technical_spec.json"
DB_PATH = PROJECT_ROOT / "data" / "mythic_patterns.db"
OUTPUTS = PROJECT_ROOT / "outputs"


def ensure_dirs():
    for subdir in ["metrics", "reports", "audits"]:
        (OUTPUTS / subdir).mkdir(parents=True, exist_ok=True)


def run_validation(full: bool = True) -> dict:
    """Run the complete v2 validation suite."""
    timestamp = datetime.now(timezone.utc).isoformat()

    print("=" * 60)
    print("ACP v2 Validation Suite")
    print("Testing: Cross-Cultural Structural Equivalence")
    print("=" * 60)

    # Initialize shared components
    print("\n[Init] Loading ACP data...")
    acp = ACPLoader(str(ACP_PATH))
    print(f"  Loaded {len(acp.archetypes)} archetypes, {len(acp.primordials)} primordials")

    print("[Init] Loading library...")
    library = LibraryLoader(str(DB_PATH))
    lib_summary = library.summary()
    print(f"  Loaded {lib_summary['entities']} entities, {lib_summary['segments']} segments")

    print("[Init] Mapping entities...")
    mapper = EntityMapper(acp, library)
    map_result = mapper.auto_map_all()
    n_mapped = map_result.get("total_mapped", 0)
    n_total = map_result.get("total_entities", 0)
    print(f"  Mapped {n_mapped}/{n_total} entities")

    results = {
        "version": "v2",
        "timestamp": timestamp,
        "mode": "full" if full else "quick",
        "summary": {
            "archetypes": len(acp.archetypes),
            "primordials": len(acp.primordials),
            "library_entities": lib_summary["entities"],
            "library_segments": lib_summary["segments"],
            "entities_mapped": n_mapped,
            "mapping_rate": round(n_mapped / n_total * 100, 1) if n_total > 0 else 0,
        },
    }

    # ── Test 1: CULTURAL_ECHO Distance Coherence ──────────────
    print("\n[Test 1/6] CULTURAL_ECHO Distance Coherence...")
    echo_test = EchoCoherenceTest(acp)
    results["test1_echo_coherence"] = echo_test.run()
    v = results["test1_echo_coherence"].get("verdicts", {})
    print(f"  Distance test: {'PASS' if v.get('distance_test', {}).get('pass') else 'FAIL'}")
    print(f"  Fidelity test: {'PASS' if v.get('fidelity_test', {}).get('pass') else 'FAIL'}")

    # ── Test 2: Primordial Profile Clustering ─────────────────
    n_perms = 1000 if full else 100
    print(f"\n[Test 2/6] Primordial Profile Clustering ({n_perms} permutations)...")
    prim_test = PrimordialClusteringTest(acp)
    results["test2_primordial_clustering"] = prim_test.run(n_permutations=n_perms)
    v = results["test2_primordial_clustering"].get("verdicts", {})
    print(f"  Correlation test: {'PASS' if v.get('correlation_test', {}).get('pass') else 'FAIL'}")
    print(f"  Cluster test: {'PASS' if v.get('cluster_test', {}).get('pass') else 'FAIL'}")

    # ── Test 3: Typed Relationship Geometric Signatures ───────
    print("\n[Test 3/6] Typed Relationship Geometric Signatures...")
    rel_test = RelationshipGeometryTest(acp)
    results["test3_relationship_geometry"] = rel_test.run()
    v = results["test3_relationship_geometry"].get("verdicts", {})
    print(f"  Polar axis diff: {'PASS' if v.get('polar_axis_diff', {}).get('pass') else 'FAIL'}")
    print(f"  Type differentiation: {'PASS' if v.get('type_differentiation', {}).get('pass') else 'FAIL'}")

    # ── Test 4: Cross-Tradition Motif Bridging ────────────────
    print("\n[Test 4/6] Cross-Tradition Motif Bridging...")
    motif_test = MotifBridgingTest(acp, library, mapper)
    results["test4_motif_bridging"] = motif_test.run()
    v = results["test4_motif_bridging"].get("verdicts", {})
    print(f"  Correlation test: {'PASS' if v.get('correlation_test', {}).get('pass') else 'FAIL'}")
    print(f"  Quartile test: {'PASS' if v.get('quartile_test', {}).get('pass') else 'FAIL'}")

    # ── Test 5: Axis Interpretability Audit ───────────────────
    print("\n[Test 5/6] Axis Interpretability Audit...")
    axis_test = AxisInterpretabilityTest(acp, library, mapper)
    results["test5_axis_interpretability"] = axis_test.run()
    v = results["test5_axis_interpretability"].get("verdicts", {})
    print(f"  Interpretability score: {'PASS' if v.get('interpretability_score', {}).get('pass') else 'FAIL'}")
    print(f"  Top 3 alignment: {'PASS' if v.get('top_3_alignment', {}).get('pass') else 'FAIL'}")

    # ── Test 6: Human Expert Concordance Audit ────────────────
    print("\n[Test 6/6] Generating Human Expert Audit Cases...")
    audit_test = HumanAuditTest(acp)
    results["test6_human_audit"] = audit_test.run()
    print(f"  Generated {results['test6_human_audit'].get('n_cases', 0)} audit cases")

    # Save audit document
    audit_path = audit_test.save_audit(results["test6_human_audit"], str(OUTPUTS / "audits"))
    print(f"  Saved to {audit_path}")

    # ── Tests 7-10: Miroglyph Structure Validation ────────────
    print("\n[Tests 7-10] Miroglyph Structure Validation...")
    miroglyph = MiroGlyphLoader(str(MIRO_SPEC))
    print(f"  Loaded {miroglyph.summary()['nodes']} Miroglyph nodes")

    from integration.unified_loader import UnifiedLoader

    class _QuickUnified:
        """Lightweight wrapper to avoid re-loading everything."""
        def __init__(self, acp, library, miroglyph, mapper):
            self.acp = acp
            self.library = library
            self.miroglyph = miroglyph
            self.mapper = mapper
        def get_entity_coordinates(self, entity_name):
            mapping = self.mapper.get_mapping(entity_name)
            if not mapping:
                return None
            return self.acp.get_coordinates(mapping.acp_archetype_id)

    quick_unified = _QuickUnified(acp, library, miroglyph, mapper)
    profiler = NodeProfiler(quick_unified)
    miro_test = MiroStructureTest(acp, library, mapper, miroglyph, profiler)
    results["miroglyph_structure"] = miro_test.run()

    miro_verdicts = results["miroglyph_structure"].get("verdicts", {})
    tier_c_miro = miro_verdicts.get("tier_c_overall", {})
    print(f"  Tier C (Miroglyph): {'PASS' if tier_c_miro.get('pass') else 'FAIL'}")
    for tkey in ["test7_arc_separation", "test8_condition_progression", "test9_polarity_pairs"]:
        tv = miro_verdicts.get(tkey, {})
        label = tkey.replace("test7_", "").replace("test8_", "").replace("test9_", "")
        print(f"    {label}: {'PASS' if tv.get('pass') else 'FAIL'} — {tv.get('detail', '')}")

    t10 = results["miroglyph_structure"].get("test10_structural_optimality", {})
    for rec in t10.get("recommendations", []):
        print(f"    [Recommendation] {rec}")

    # ── Compute Verdict ───────────────────────────────────────
    results["verdict"] = compute_verdict(results)
    print_verdict(results["verdict"])

    return results


def compute_verdict(results: dict) -> dict:
    """Compute tiered verdict from all test results."""
    def test_passed(key):
        test = results.get(key, {})
        return test.get("verdicts", {}).get("overall_pass", False)

    # Tier A: Internal Geometric Coherence (Tests 1, 2, 3)
    tier_a = [
        ("Test 1: Echo Coherence", test_passed("test1_echo_coherence")),
        ("Test 2: Primordial Clustering", test_passed("test2_primordial_clustering")),
        ("Test 3: Relationship Geometry", test_passed("test3_relationship_geometry")),
    ]
    tier_a_passed = sum(1 for _, p in tier_a if p)

    if tier_a_passed == 3:
        tier_a_verdict = "PASS"
        tier_a_label = "Geometrically self-consistent"
    elif tier_a_passed == 2:
        tier_a_verdict = "PARTIAL"
        tier_a_label = "Mostly consistent, specific weaknesses"
    else:
        tier_a_verdict = "FAIL"
        tier_a_label = "Geometry contradicts relational claims"

    # Tier B: External Predictive Validity (Tests 4, 5)
    tier_b = [
        ("Test 4: Motif Bridging", test_passed("test4_motif_bridging")),
        ("Test 5: Axis Interpretability", test_passed("test5_axis_interpretability")),
    ]
    tier_b_passed = sum(1 for _, p in tier_b if p)

    if tier_b_passed == 2:
        tier_b_verdict = "PASS"
        tier_b_label = "Externally validatable cross-cultural signal"
    elif tier_b_passed == 1:
        tier_b_verdict = "PARTIAL"
        tier_b_label = "Partial external validity"
    else:
        tier_b_verdict = "FAIL"
        tier_b_label = "No external validation"

    # Tier C: Miroglyph Structural Validity (Tests 7-9)
    miro = results.get("miroglyph_structure", {})
    miro_v = miro.get("verdicts", {})
    tier_c = [
        ("Test 7: Arc Separation", miro_v.get("test7_arc_separation", {}).get("pass", False)),
        ("Test 8: Condition Progression", miro_v.get("test8_condition_progression", {}).get("pass", False)),
        ("Test 9: Polarity Pairs", miro_v.get("test9_polarity_pairs", {}).get("pass", False)),
    ]
    tier_c_passed = sum(1 for _, p in tier_c if p)

    if tier_c_passed >= 2:
        tier_c_verdict = "PASS"
        tier_c_label = "Miroglyph structure empirically supported"
    elif tier_c_passed == 1:
        tier_c_verdict = "PARTIAL"
        tier_c_label = "Partial structural support"
    else:
        tier_c_verdict = "FAIL"
        tier_c_label = "Miroglyph structure not supported by data"

    # Tier D: Cross-System Integration (Test 10)
    t10 = miro.get("test10_structural_optimality", {})
    structure_confirmed = t10.get("structure_confirmed", False)
    tier_d_verdict = "CONFIRMED" if structure_confirmed else "ALTERNATIVES_FOUND"
    tier_d_label = ("Current 3x6 structure is optimal"
                    if structure_confirmed else
                    "Data suggests structural alternatives")

    # Tier E: Expert Plausibility (Test 6) — awaiting human review
    tier_e_verdict = "PENDING"
    tier_e_label = "Awaiting human review"

    # Combined verdict
    if tier_a_verdict == "FAIL":
        overall = "REVISE"
        overall_label = "Fundamental geometric inconsistencies; coordinates need reworking"
    elif tier_a_verdict == "PASS" and tier_b_verdict == "PASS":
        overall = "STRONG"
        overall_label = "Internal consistency + external validity (pending expert review)"
    elif tier_a_verdict == "PASS" and tier_b_verdict == "PARTIAL":
        overall = "PROMISING"
        overall_label = "Internal consistency confirmed; partial external signal"
    elif tier_a_verdict == "PASS" and tier_b_verdict == "FAIL":
        overall = "SELF-CONSISTENT BUT UNGROUNDED"
        overall_label = "Coordinates are coherent but don't predict external phenomena"
    elif tier_a_verdict == "PARTIAL":
        overall = "MIXED"
        overall_label = "Partial internal consistency; needs targeted improvements"
    else:
        overall = "INCONCLUSIVE"
        overall_label = "Insufficient evidence for definitive assessment"

    return {
        "tier_a": {
            "verdict": tier_a_verdict,
            "label": tier_a_label,
            "tests": [{
                "name": name, "pass": p,
            } for name, p in tier_a],
            "passed": tier_a_passed,
            "total": 3,
        },
        "tier_b": {
            "verdict": tier_b_verdict,
            "label": tier_b_label,
            "tests": [{
                "name": name, "pass": p,
            } for name, p in tier_b],
            "passed": tier_b_passed,
            "total": 2,
        },
        "tier_c": {
            "verdict": tier_c_verdict,
            "label": tier_c_label,
            "tests": [{
                "name": name, "pass": p,
            } for name, p in tier_c],
            "passed": tier_c_passed,
            "total": 3,
        },
        "tier_d": {
            "verdict": tier_d_verdict,
            "label": tier_d_label,
            "recommendations": t10.get("recommendations", []),
        },
        "tier_e": {
            "verdict": tier_e_verdict,
            "label": tier_e_label,
            "tests": [{"name": "Test 6: Human Audit", "pass": None}],
            "passed": 0,
            "total": 1,
        },
        "overall": {
            "verdict": overall,
            "label": overall_label,
        },
    }


def print_verdict(verdict: dict):
    """Print verdict to console."""
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)

    for tier_key in ["tier_a", "tier_b", "tier_c", "tier_d", "tier_e"]:
        tier = verdict.get(tier_key, {})
        if not tier:
            continue
        label = tier_key.replace("tier_", "Tier ").upper()
        print(f"\n{label}: {tier['verdict']} — {tier['label']}")
        for t in tier.get("tests", []):
            status = "PASS" if t["pass"] else ("PENDING" if t["pass"] is None else "FAIL")
            mark = "+" if t["pass"] else ("?" if t["pass"] is None else "-")
            print(f"  [{mark}] {t['name']}: {status}")
        for rec in tier.get("recommendations", []):
            print(f"  >> {rec}")

    overall = verdict["overall"]
    print(f"\nOVERALL: {overall['verdict']}")
    print(f"  {overall['label']}")
    print("=" * 60)


def generate_report(results: dict) -> str:
    """Generate markdown v2 validation report."""
    lines = []
    lines.append("# ACP v2 Validation Report — Cross-Cultural Structural Equivalence")
    lines.append("")
    lines.append(f"Generated: {results.get('timestamp', 'unknown')}")
    lines.append(f"Mode: {results.get('mode', 'unknown')}")
    lines.append("")

    # Hypothesis
    lines.append("## Hypothesis")
    lines.append("")
    lines.append("The ACP encodes a system of cross-cultural structural equivalence.")
    lines.append("Its coordinates, relationships, and primordial hierarchy form an internally")
    lines.append("coherent and externally meaningful framework. This report tests that claim")
    lines.append("through 6 falsifiable tests across 3 tiers.")
    lines.append("")

    # Summary
    s = results.get("summary", {})
    lines.append("## Data Overview")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| ACP Archetypes | {s.get('archetypes', '?')} |")
    lines.append(f"| Primordials | {s.get('primordials', '?')} |")
    lines.append(f"| Library Entities | {s.get('library_entities', '?')} |")
    lines.append(f"| Library Segments | {s.get('library_segments', '?')} |")
    lines.append(f"| Entities Mapped | {s.get('entities_mapped', '?')} ({s.get('mapping_rate', '?')}%) |")
    lines.append("")

    # ── Test 1 ────────────────────────────────────────────────
    t1 = results.get("test1_echo_coherence", {})
    lines.append("## Test 1: CULTURAL_ECHO Distance Coherence")
    lines.append("")
    lines.append("**Question**: Are archetypes labeled as cultural echoes actually close in 8D space?")
    lines.append("")

    if "error" in t1:
        lines.append(f"**Error**: {t1['error']}")
    else:
        lines.append(f"| Metric | Echo Pairs | Control Pairs |")
        lines.append(f"|--------|-----------|--------------|")
        ed = t1.get("echo_distance", {})
        cd = t1.get("control_distance", {})
        lines.append(f"| N | {t1.get('n_echo_pairs', '?')} | {t1.get('n_control_pairs', '?')} |")
        lines.append(f"| Mean distance | {ed.get('mean', '?')} | {cd.get('mean', '?')} |")
        lines.append(f"| Median distance | {ed.get('median', '?')} | {cd.get('median', '?')} |")
        lines.append("")

        mw = t1.get("mann_whitney", {})
        fc = t1.get("fidelity_correlation", {})
        lines.append("| Test | Result | Pass? |")
        lines.append("|------|--------|-------|")
        v1d = t1.get("verdicts", {}).get("distance_test", {})
        v1f = t1.get("verdicts", {}).get("fidelity_test", {})
        lines.append(f"| Distance (Mann-Whitney) | p={mw.get('p_value', '?')}, d={mw.get('cohens_d', '?')} | {'PASS' if v1d.get('pass') else 'FAIL'} |")
        lines.append(f"| Fidelity correlation | r={fc.get('spearman_r', '?')}, p={fc.get('spearman_p', '?')} | {'PASS' if v1f.get('pass') else 'FAIL'} |")
    lines.append("")

    # ── Test 2 ────────────────────────────────────────────────
    t2 = results.get("test2_primordial_clustering", {})
    lines.append("## Test 2: Primordial Profile Clustering")
    lines.append("")
    lines.append("**Question**: Do archetypes sharing primordial profiles cluster in spectral space?")
    lines.append("")

    if "error" in t2:
        lines.append(f"**Error**: {t2['error']}")
    else:
        corr = t2.get("correlation", {})
        perm = t2.get("permutation_test", {})
        clust = t2.get("cluster_analysis", {})
        lines.append("| Test | Result | Pass? |")
        lines.append("|------|--------|-------|")
        v2c = t2.get("verdicts", {}).get("correlation_test", {})
        v2cl = t2.get("verdicts", {}).get("cluster_test", {})
        lines.append(f"| Primordial-spectral correlation | r={corr.get('spearman_r', '?')}, perm_p={perm.get('empirical_p', '?')} | {'PASS' if v2c.get('pass') else 'FAIL'} |")
        lines.append(f"| Cluster separation | within={clust.get('within_cluster_mean', '?')}, between={clust.get('between_cluster_mean', '?')}, ratio={clust.get('separation_ratio', '?')} | {'PASS' if v2cl.get('pass') else 'FAIL'} |")
    lines.append("")

    # ── Test 3 ────────────────────────────────────────────────
    t3 = results.get("test3_relationship_geometry", {})
    lines.append("## Test 3: Typed Relationship Geometric Signatures")
    lines.append("")
    lines.append("**Question**: Do relationship types produce distinct geometric patterns?")
    lines.append("")

    if "error" in t3:
        lines.append(f"**Error**: {t3['error']}")
    else:
        polar = t3.get("polar_opposite_tests", {})
        kw = t3.get("kruskal_wallis", {})
        lines.append("| Test | Result | Pass? |")
        lines.append("|------|--------|-------|")
        v3p = t3.get("verdicts", {}).get("polar_axis_diff", {})
        v3m = t3.get("verdicts", {}).get("polar_max_axis", {})
        v3k = t3.get("verdicts", {}).get("type_differentiation", {})
        lines.append(f"| Polar axis diff >0.5 | {polar.get('axis_diff_gt_05_pct', '?')}% ({polar.get('axis_diff_gt_05_count', '?')}/{polar.get('n_with_declared_axis', '?')}) | {'PASS' if v3p.get('pass') else 'FAIL'} |")
        lines.append(f"| Polar max-diff = declared | {polar.get('max_diff_matches_declared_pct', '?')}% | {'PASS' if v3m.get('pass') else 'FAIL'} |")
        lines.append(f"| Kruskal-Wallis across types | H={kw.get('statistic', '?')}, p={kw.get('p_value', '?')} | {'PASS' if v3k.get('pass') else 'FAIL'} |")
        lines.append("")

        # Distance by type table
        dbt = t3.get("distance_by_type", {})
        if dbt:
            lines.append("### Distance by Relationship Type")
            lines.append("")
            lines.append("| Type | N | Mean | Median | Std |")
            lines.append("|------|---|------|--------|-----|")
            for rtype in ["POLAR_OPPOSITE", "COMPLEMENT", "SHADOW", "EVOLUTION", "ANTAGONIST", "RANDOM"]:
                d = dbt.get(rtype, {})
                if d:
                    lines.append(f"| {rtype} | {d.get('n_pairs', '?')} | {d.get('mean', '?')} | {d.get('median', '?')} | {d.get('std', '?')} |")
    lines.append("")

    # ── Test 4 ────────────────────────────────────────────────
    t4 = results.get("test4_motif_bridging", {})
    lines.append("## Test 4: Cross-Tradition Motif Bridging")
    lines.append("")
    lines.append("**Question**: Do cross-tradition entities sharing motifs sit closer in ACP space?")
    lines.append("")

    if "error" in t4:
        lines.append(f"**Error**: {t4['error']}")
    else:
        corr = t4.get("correlation", {})
        qc = t4.get("quartile_comparison", {})
        jd = t4.get("jaccard_distribution", {})
        sub = t4.get("three_axis_subset", {})
        bsd = t4.get("binary_sharing_diagnostic", {})
        lines.append(f"Cross-tradition pairs: {t4.get('n_cross_tradition_pairs', '?')}")
        lines.append(f"Jaccard Q25={jd.get('q25', '?')}, Q75={jd.get('q75', '?')} "
                      f"(high-overlap: {jd.get('n_high_overlap', '?')}, low-overlap: {jd.get('n_low_overlap', '?')})")
        lines.append(f"Binary sharing: {bsd.get('sharing_pct', '?')}% share ≥1 motif (diagnostic only)")
        lines.append("")
        lines.append("| Test | Result | Pass? |")
        lines.append("|------|--------|-------|")
        v4c = t4.get("verdicts", {}).get("correlation_test", {})
        v4q = t4.get("verdicts", {}).get("quartile_test", {})
        lines.append(f"| Distance-Jaccard correlation | r={corr.get('spearman_r', '?')}, p={corr.get('spearman_p', '?')} | {'PASS' if v4c.get('pass') else 'FAIL'} |")
        lines.append(f"| Quartile comparison (Q3+ vs Q1-) | high={qc.get('high_overlap_mean_distance', '?')} vs low={qc.get('low_overlap_mean_distance', '?')}, p={qc.get('p_value', '?')} | {'PASS' if v4q.get('pass') else 'FAIL'} |")
        lines.append(f"| 3-axis subset | r={sub.get('spearman_r', '?')}, improvement={sub.get('improvement_over_8d', '?')} | — |")
    lines.append("")

    # ── Test 5 ────────────────────────────────────────────────
    t5 = results.get("test5_axis_interpretability", {})
    lines.append("## Test 5: Axis Interpretability Audit")
    lines.append("")
    lines.append("**Question**: Do motif categories cluster on expected axes?")
    lines.append("")

    if "error" in t5:
        lines.append(f"**Error**: {t5['error']}")
    else:
        lines.append(f"Interpretability score: {t5.get('n_passed', '?')}/{t5.get('n_mappings_tested', '?')} ({t5.get('interpretability_score', 0)*100:.0f}%)")
        lines.append("")
        lines.append("| Motif | Axis | Direction | Group Mean | Global Mean | Delta | p-value | Result |")
        lines.append("|-------|------|-----------|-----------|-------------|-------|---------|--------|")
        for tr in t5.get("test_results", []):
            lines.append(f"| {tr.get('motif_prefix', '?')} | {tr.get('axis', '?')} | {tr.get('direction', '?')} | {tr.get('group_mean', '?')} | {tr.get('global_mean', '?')} | {tr.get('delta', '?')} | {tr.get('p_value', '?')} | {tr.get('result', '?')} |")
    lines.append("")

    # ── Test 6 ────────────────────────────────────────────────
    t6 = results.get("test6_human_audit", {})
    lines.append("## Test 6: Human Expert Concordance Audit")
    lines.append("")
    lines.append("**Status**: Audit cases generated, awaiting human review.")
    lines.append("")
    lines.append(f"Cases generated: {t6.get('n_cases', '?')}")
    cbc = t6.get("cases_by_category", {})
    if cbc:
        lines.append("")
        lines.append("| Category | Count |")
        lines.append("|----------|-------|")
        for cat, count in cbc.items():
            lines.append(f"| {cat} | {count} |")
    lines.append("")
    lines.append("See `outputs/audits/human_audit_cases.json` for the full audit document.")
    lines.append("")

    # ── Verdict ────────────────────────────────────────────────
    verdict = results.get("verdict", {})
    lines.append("## Verdict")
    lines.append("")

    for tier_key, tier_label in [("tier_a", "Tier A — Internal Geometric Coherence"), ("tier_b", "Tier B — External Predictive Validity"), ("tier_c", "Tier C — Expert Plausibility")]:
        tier = verdict.get(tier_key, {})
        lines.append(f"### {tier_label}")
        lines.append("")
        lines.append(f"**{tier.get('verdict', '?')}**: {tier.get('label', '')}")
        lines.append("")
        for t in tier.get("tests", []):
            status = "PASS" if t["pass"] else ("PENDING" if t["pass"] is None else "FAIL")
            lines.append(f"- {t['name']}: **{status}**")
        lines.append("")

    overall = verdict.get("overall", {})
    lines.append(f"### Overall: **{overall.get('verdict', '?')}**")
    lines.append("")
    lines.append(overall.get("label", ""))
    lines.append("")

    # ── Conclusions ─────────────────────────────────────────────
    lines.append("## Conclusions")
    lines.append("")

    tier_a = verdict.get("tier_a", {})
    tier_b = verdict.get("tier_b", {})

    if tier_a.get("verdict") == "PASS":
        lines.append("1. **Internal coherence confirmed**: The ACP's coordinate geometry is consistent with its declared relationships — cultural echoes, polar opposites, complements, and primordial clusters all show the expected geometric signatures.")
    elif tier_a.get("verdict") == "PARTIAL":
        lines.append("1. **Partial internal coherence**: Some but not all of the ACP's relational claims match its geometry. Specific tests that failed indicate areas for coordinate revision.")
    else:
        lines.append("1. **Internal coherence not established**: The ACP's coordinates do not consistently reflect its own declared relationships. The coordinate system needs fundamental revision.")

    if tier_b.get("verdict") == "PASS":
        lines.append("2. **External validity confirmed**: ACP coordinates predict independently-measured cross-tradition phenomena — motif sharing and axis-semantic alignment provide external grounding.")
    elif tier_b.get("verdict") == "PARTIAL":
        lines.append("2. **Partial external validity**: ACP coordinates show some ability to predict external phenomena, but the signal is limited.")
    else:
        lines.append("2. **External validity not established**: ACP coordinates do not predict external cross-cultural measures. The system may be internally consistent but circular.")

    lines.append("3. **Expert review pending**: Human concordance audit has been generated and awaits reviewer scoring.")
    lines.append("")

    # ── Weighted Distance Comparison ─────────────────────────────
    lines.append("## Appendix: Weighted Distance Comparison")
    lines.append("")
    lines.append("Empirical axis weights (from Phase 10 discriminative analysis) applied to all distance calculations.")
    lines.append("Weights: creation-destruction=2.17, order-chaos=1.19, individual-collective=0.93,")
    lines.append("light-shadow=0.80, active-receptive=0.79, voluntary-fated=0.77, stasis-transformation=0.74, ascent-descent=0.20")
    lines.append("")
    lines.append("| Test | Unweighted | Weighted | Improvement |")
    lines.append("|------|-----------|---------|-------------|")

    # Test 1 weighted
    t1_w = t1.get("weighted_comparison", {})
    if t1_w:
        lines.append(f"| Test 1: Echo d | d={t1.get('mann_whitney', {}).get('cohens_d', '?')} | d={t1_w.get('cohens_d', '?')} | {t1_w.get('improvement_over_unweighted', '?')} |")

    # Test 2 weighted
    t2_w = t2.get("weighted_comparison", {})
    if t2_w:
        lines.append(f"| Test 2: Prim r | r={t2.get('correlation', {}).get('spearman_r', '?')} | r={t2_w.get('weighted_spearman_r', '?')} | {t2_w.get('improvement_over_unweighted', '?')} |")

    # Test 3 weighted
    t3_w = t3.get("weighted_comparison", {})
    if t3_w:
        wkw = t3_w.get("weighted_kruskal_wallis", {})
        lines.append(f"| Test 3: KW p | p={t3.get('kruskal_wallis', {}).get('p_value', '?')} | p={wkw.get('p_value', '?')} | {t3_w.get('improvement_kw_p', '?')} |")

    # Test 4 weighted
    t4_w = t4.get("weighted_comparison", {})
    if t4_w:
        lines.append(f"| Test 4: Motif r | r={t4.get('correlation', {}).get('spearman_r', '?')} | r={t4_w.get('weighted_spearman_r', '?')} | {t4_w.get('improvement_over_unweighted', '?')} |")

    lines.append("")
    lines.append("---")
    lines.append("*Generated by the ACP v2 Validation Suite*")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="ACP v2 Validation Suite")
    parser.add_argument("--full", action="store_true", default=True, help="Full validation")
    parser.add_argument("--quick", action="store_true", help="Skip slow tests")
    parser.add_argument("--report", action="store_true", help="Generate markdown report")
    args = parser.parse_args()

    full = not args.quick
    ensure_dirs()

    results = run_validation(full=full)

    # Save JSON results
    json_path = OUTPUTS / "metrics" / "v2_validation_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nResults saved to {json_path}")

    # Generate and save report
    report = generate_report(results)
    report_path = OUTPUTS / "reports" / "v2_validation_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report saved to {report_path}")


if __name__ == "__main__":
    main()
