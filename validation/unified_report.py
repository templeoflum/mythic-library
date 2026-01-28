"""Generate unified validation report across all three systems."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUTS = PROJECT_ROOT / "outputs"


def generate_unified_report(results: dict) -> str:
    """Generate markdown report covering all tiers including Miroglyph."""
    lines = []
    lines.append("# Unified Mythic System — Validation Report")
    lines.append("")
    lines.append(f"Generated: {results.get('timestamp', datetime.now(timezone.utc).isoformat())}")
    lines.append(f"Mode: {results.get('mode', 'unknown')}")
    lines.append("")

    # System overview
    s = results.get("summary", {})
    lines.append("## System Overview")
    lines.append("")
    lines.append("| System | Metric | Value |")
    lines.append("|--------|--------|-------|")
    lines.append(f"| ACP | Archetypes | {s.get('archetypes', '?')} |")
    lines.append(f"| ACP | Primordials | {s.get('primordials', '?')} |")
    lines.append(f"| Library | Entities | {s.get('library_entities', '?')} |")
    lines.append(f"| Library | Segments | {s.get('library_segments', '?')} |")
    lines.append(f"| Library | Entities Mapped | {s.get('entities_mapped', '?')} ({s.get('mapping_rate', '?')}%) |")
    lines.append(f"| Miroglyph | Nodes | 18 (3 arcs x 6 conditions) |")
    lines.append("")

    # Verdict summary
    verdict = results.get("verdict", {})
    lines.append("## Verdict Summary")
    lines.append("")
    lines.append("| Tier | Focus | Verdict |")
    lines.append("|------|-------|---------|")
    for tier_key, tier_name in [
        ("tier_a", "A: ACP Internal Coherence"),
        ("tier_b", "B: Library-ACP External Validity"),
        ("tier_c", "C: Miroglyph Structural Validity"),
        ("tier_d", "D: Cross-System Integration"),
        ("tier_e", "E: Expert Review"),
    ]:
        tier = verdict.get(tier_key, {})
        lines.append(f"| {tier_name} | {tier.get('label', '—')} | **{tier.get('verdict', '?')}** |")
    lines.append("")

    overall = verdict.get("overall", {})
    lines.append(f"**Overall: {overall.get('verdict', '?')}** — {overall.get('label', '')}")
    lines.append("")

    # ── Tier A ──
    lines.append("## Tier A: ACP Internal Coherence")
    lines.append("")
    for t in verdict.get("tier_a", {}).get("tests", []):
        status = "PASS" if t["pass"] else "FAIL"
        lines.append(f"- {t['name']}: **{status}**")
    lines.append("")

    # ── Tier B ──
    lines.append("## Tier B: Library-ACP External Validity")
    lines.append("")
    for t in verdict.get("tier_b", {}).get("tests", []):
        status = "PASS" if t["pass"] else "FAIL"
        lines.append(f"- {t['name']}: **{status}**")
    lines.append("")

    # ── Tier C: Miroglyph ──
    lines.append("## Tier C: Miroglyph Structural Validity")
    lines.append("")

    miro = results.get("miroglyph_structure", {})
    miro_v = miro.get("verdicts", {})

    for tkey, tname in [
        ("test7_arc_separation", "Test 7: Arc Separation"),
        ("test8_condition_progression", "Test 8: Condition Progression"),
        ("test9_polarity_pairs", "Test 9: Polarity Pairs"),
    ]:
        tv = miro_v.get(tkey, {})
        status = "PASS" if tv.get("pass") else "FAIL"
        lines.append(f"### {tname}: **{status}**")
        lines.append("")
        lines.append(f"Criterion: {tv.get('criterion', '—')}")
        lines.append(f"Result: {tv.get('detail', '—')}")
        lines.append("")

    # Arc separation details
    t7 = miro.get("test7_arc_separation", {})
    if t7:
        lines.append("#### Arc Separation Details")
        lines.append("")
        lines.append(f"- Within-arc mean distance: {t7.get('within_arc_mean_dist', '?')}")
        lines.append(f"- Between-arc mean distance: {t7.get('between_arc_mean_dist', '?')}")
        lines.append(f"- Mann-Whitney p: {t7.get('mann_whitney_p', '?')}")
        lines.append(f"- Silhouette (k=3): {t7.get('silhouette_k3', '?')}")
        lines.append("")
        alt = t7.get("alternative_silhouettes", {})
        if alt:
            lines.append("| k (arcs) | Silhouette |")
            lines.append("|----------|-----------|")
            lines.append(f"| 3 (current) | {t7.get('silhouette_k3', '?')} |")
            for k, s in sorted(alt.items()):
                lines.append(f"| {k} | {s} |")
            lines.append("")

    # Condition progression details
    t8 = miro.get("test8_condition_progression", {})
    if t8:
        current = t8.get("current_bins_6", {})
        lines.append("#### Condition Progression Details")
        lines.append("")
        all_bins = t8.get("all_bin_counts", {})
        if all_bins:
            lines.append("| Bins | Significant Axes |")
            lines.append("|------|-----------------|")
            for bk in sorted(all_bins.keys()):
                bv = all_bins[bk]
                marker = " (current)" if bk == "6" else ""
                lines.append(f"| {bk}{marker} | {bv.get('significant_axes', '?')} |")
            lines.append("")

    # Polarity pairs details
    t9 = miro.get("test9_polarity_pairs", {})
    if t9:
        lines.append("#### Polarity Pair Details")
        lines.append("")
        lines.append("| Pair | Distance |")
        lines.append("|------|----------|")
        for p in t9.get("polarity_pairs", []):
            lines.append(f"| {p.get('pair', '?')} (polarity) | {p.get('distance', '?'):.4f} |")
        for p in t9.get("non_polarity_pairs", []):
            lines.append(f"| {p.get('pair', '?')} | {p.get('distance', '?'):.4f} |")
        lines.append("")
        if t9.get("best_pairing"):
            lines.append(f"Empirically strongest pairing: {t9['best_pairing']}")
            lines.append(f"Current pairing optimal: {t9.get('current_is_optimal', False)}")
            lines.append("")

    # ── Tier D: Function-First Summary ──
    lines.append("## Tier D: Function-First Structural Assessment")
    lines.append("")

    t10 = miro.get("test10_structural_optimality", {})
    if t10:
        lines.append("### Recommendations")
        lines.append("")
        for rec in t10.get("recommendations", []):
            lines.append(f"- {rec}")
        lines.append("")

        lines.append(f"**Structure confirmed: {t10.get('structure_confirmed', False)}**")
        lines.append("")

        if not t10.get("structure_confirmed", True):
            lines.append("### What the Data Suggests")
            lines.append("")
            if t10.get("optimal_arcs") != t10.get("current_arcs"):
                lines.append(f"- **Arcs**: Current {t10['current_arcs']} arcs should be "
                             f"revised to {t10['optimal_arcs']} based on silhouette analysis")
            if t10.get("optimal_conditions") != t10.get("current_conditions"):
                lines.append(f"- **Conditions**: Current {t10['current_conditions']} conditions "
                             f"should be revised to {t10['optimal_conditions']}")
            if not t10.get("polarity_optimal"):
                lines.append(f"- **Polarity**: Alternative pairing {t10.get('best_polarity_pairing')} "
                             f"shows stronger opposition")
            if t10.get("irrelevant_axes"):
                lines.append(f"- **Axes**: These axes do not differentiate arcs: "
                             f"{t10['irrelevant_axes']}")
            lines.append("")
            lines.append("**Interpretation**: The arc motif-to-pattern mapping likely "
                         "needs refinement. The patterns assigned to each arc may share "
                         "too many entities across traditions, causing arc centroids to "
                         "converge. This is a mapping hypothesis issue, not necessarily "
                         "a flaw in the Miroglyph topology itself.")
            lines.append("")

    # ── Tier E ──
    lines.append("## Tier E: Expert Review")
    lines.append("")
    lines.append("**Status**: Audit cases generated, awaiting human review.")
    lines.append("See `outputs/audits/human_audit_cases.json`")
    lines.append("")

    # ── Footer ──
    lines.append("---")
    lines.append("*Generated by the Unified Mythic System Validation Suite*")
    lines.append(f"*Philosophy: Function first, everything else is negotiable*")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    # Load latest validation results
    results_path = OUTPUTS / "metrics" / "v2_validation_results.json"
    if not results_path.exists():
        print("No validation results found. Run validation first:")
        print("  python -m validation.v2_run")
        sys.exit(1)

    with open(results_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    report = generate_unified_report(results)

    report_path = OUTPUTS / "reports" / "unified_validation_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Unified report saved to {report_path}")
