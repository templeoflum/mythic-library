#!/usr/bin/env python3
"""
MythOS Validation Suite: ACP + Library Integration.

Tests whether ACP 8-dimensional coordinates predict narrative co-occurrence
patterns in the mythic library corpus.
"""
import io
import json
import sys

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integration.acp_loader import ACPLoader
from integration.library_loader import LibraryLoader
from integration.entity_mapper import EntityMapper
from validation.test_coordinate_accuracy import CoordinateValidation
from validation.test_motif_clustering import MotifClustering
from validation.calibrate_coordinates import CoordinateCalibrator
from validation.statistical_tests import StatisticalTests
from validation.alternative_metrics import AlternativeMetrics

ACP_PATH = PROJECT_ROOT / "ACP"
DB_PATH = PROJECT_ROOT / "data" / "mythic_patterns.db"
OUTPUTS = PROJECT_ROOT / "outputs"


def main():
    print("=" * 60)
    print("  ACP Validation Suite")
    print("  ACP + Mythic Library Integration")
    print("=" * 60)
    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"  Run: {timestamp}\n")

    # ── Load ACP ──────────────────────────────────────────────
    print("Loading ACP...")
    acp = ACPLoader(str(ACP_PATH))
    acp_summary = acp.summary()
    print(f"  Archetypes:  {acp_summary['archetypes']}")
    print(f"  Primordials: {acp_summary['primordials']}")
    print(f"  Systems:     {acp_summary['systems']}")
    print(f"  Aliases:     {acp_summary['alias_entries']}")

    # ── Load Library ──────────────────────────────────────────
    print("\nLoading Library...")
    library = LibraryLoader(str(DB_PATH))
    lib_summary = library.summary()
    print(f"  Entities:    {lib_summary['entities']}")
    print(f"  Mentions:    {lib_summary['entity_mentions']}")
    print(f"  Segments:    {lib_summary['segments']}")
    print(f"  Motif tags:  {lib_summary['motif_tags']}")

    # ── Entity Mapping ────────────────────────────────────────
    print("\n" + "-" * 60)
    print("PHASE 1: Entity Mapping")
    print("-" * 60)

    mapper = EntityMapper(acp, library)
    map_summary = mapper.auto_map_all()

    print(f"  Tradition-aware matches: {map_summary.get('tradition_aware_matches', map_summary.get('acp_alias_matches', 0) + map_summary.get('exact_name_matches', 0))}")
    print(f"  Library alias matches:  {map_summary['library_alias_matches']}")
    print(f"  Total mapped:           {map_summary['total_mapped']} / {map_summary['total_entities']}")
    pct = map_summary['total_mapped'] / max(map_summary['total_entities'], 1) * 100
    print(f"  Coverage:               {pct:.1f}%")

    # Show mappings
    print(f"\n  Mapped entities:")
    for m in sorted(mapper.mappings, key=lambda x: -x.confidence):
        print(f"    [{m.confidence:.2f}] {m.library_entity:20s} -> {m.acp_name:20s} ({m.method})")

    # Unmapped
    unmapped = mapper.get_unmapped_entities()
    print(f"\n  Unmapped ({len(unmapped)}):")
    for name in unmapped[:20]:
        print(f"    - {name}")
    if len(unmapped) > 20:
        print(f"    ... and {len(unmapped) - 20} more")

    # Fuzzy suggestions
    fuzzy = mapper.suggest_fuzzy_matches(threshold=0.6)
    if fuzzy:
        print(f"\n  Fuzzy suggestions ({len(fuzzy)}):")
        for entity, candidates in fuzzy[:10]:
            top = candidates[0]
            print(f"    {entity:20s} ~> {top['acp_name']:20s} (similarity: {top['similarity']:.2f})")

    # Save mappings
    mappings_path = OUTPUTS / "mappings" / "entity_to_archetype.json"
    mapper.save_mappings(str(mappings_path))
    print(f"\n  Saved: {mappings_path}")

    unmapped_path = OUTPUTS / "mappings" / "unmapped_entities.json"
    with open(unmapped_path, "w", encoding="utf-8") as f:
        json.dump(unmapped, f, indent=2)

    fuzzy_path = OUTPUTS / "mappings" / "fuzzy_suggestions.json"
    with open(fuzzy_path, "w", encoding="utf-8") as f:
        json.dump(
            [{"entity": e, "candidates": c} for e, c in fuzzy],
            f, indent=2, ensure_ascii=False,
        )

    # ── Coordinate Validation ─────────────────────────────────
    print("\n" + "-" * 60)
    print("PHASE 2: Coordinate Distance vs Co-occurrence")
    print("-" * 60)

    validator = CoordinateValidation(acp, library, mapper)

    # Check for entities sharing the same ACP archetype
    arch_to_entities = {}
    for m in mapper.mappings:
        arch_to_entities.setdefault(m.acp_archetype_id, []).append(m.library_entity)
    shared = {k: v for k, v in arch_to_entities.items() if len(v) > 1}
    if shared:
        print(f"\n  Note: {len(shared)} ACP archetypes have multiple library entities:")
        for arch_id, entities in list(shared.items())[:8]:
            arch_name = acp.archetypes[arch_id].get("name", arch_id)
            print(f"    {arch_name}: {', '.join(entities)}")

    coord_results = validator.test_distance_correlation()

    def print_correlation(label, results):
        if "error" in results:
            print(f"  ERROR: {results['error']}")
            return

        print(f"\n  {label}:")
        print(f"  Total entity pairs:    {results['total_pairs']}")
        print(f"  With co-occurrence:    {results['pairs_with_cooccurrence']}")
        print(f"  Without co-occurrence: {results['pairs_without_cooccurrence']}")

        all_p = results["all_pairs"]
        print(f"    Pearson r:  {all_p['pearson_r']:+.4f}  (p={all_p['pearson_p']:.6f})")
        print(f"    Spearman r: {all_p['spearman_r']:+.4f}  (p={all_p['spearman_p']:.6f})")

        if "nonzero_pairs" in results:
            nz = results["nonzero_pairs"]
            print(f"    Non-zero only ({nz['count']} pairs):")
            print(f"      Pearson r:  {nz['pearson_r']:+.4f}  (p={nz['pearson_p']:.6f})")
            print(f"      Spearman r: {nz['spearman_r']:+.4f}  (p={nz['spearman_p']:.6f})")

        print(f"  Hypothesis: {results['hypothesis']}")
        print(f"  -> {results['interpretation']}")

        stats = results["stats"]
        print(f"  Distance: mean={stats['mean_distance']:.3f}, std={stats['std_distance']:.3f}")
        print(f"  Co-occur: mean={stats['mean_cooccurrence']:.1f}, max={stats['max_cooccurrence']}")

    print_correlation("All mapped entities", coord_results)

    if coord_results.get("top_cooccurring"):
        print(f"\n  Top co-occurring pairs:")
        for item in coord_results["top_cooccurring"][:10]:
            e1, e2 = item["entities"]
            print(f"    {e1:15s} + {e2:15s}  dist={item['distance']:.3f}  coocc={item['cooccurrence']}")

    if coord_results.get("outliers"):
        print(f"\n  Outliers ({len(coord_results['outliers'])}):")
        for o in coord_results["outliers"][:5]:
            e1, e2 = o["entities"]
            print(f"    [{o['anomaly_type']}] {e1} + {e2}: "
                  f"dist={o['distance']:.3f}, coocc={o['cooccurrence']}")

    # Re-run excluding "Set" (known false positive: common English word)
    coord_results_clean = validator.test_distance_correlation(exclude_entities=["Set"])
    print_correlation("Excluding 'Set' (false positive entity)", coord_results_clean)

    # ── Per-Tradition Correlation ────────────────────────────
    print("\n" + "-" * 60)
    print("PHASE 2b: Per-Tradition Correlation")
    print("-" * 60)

    tradition_results = validator.test_per_tradition_correlation(min_entities=3)
    print(f"  Traditions analyzed: {len(tradition_results)}")
    print(f"\n  {'Tradition':15s} {'Entities':>8s} {'Pairs':>6s} {'w/cooc':>6s} {'Spearman r':>10s} {'p-value':>10s}")
    print("  " + "-" * 58)
    for trad, data in sorted(tradition_results.items(), key=lambda x: x[1].get('spearman_r', 0)):
        if 'note' in data:
            print(f"  {trad:15s} {data['entity_count']:8d} {data['pair_count']:6d}    -- {data['note']}")
        else:
            r = data['spearman_r']
            p = data['spearman_p']
            sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
            print(f"  {trad:15s} {data['entity_count']:8d} {data['pair_count']:6d} {data['pairs_with_cooccurrence']:6d} {r:10.4f} {p:10.6f} {sig}")

    # ── Primordial Clustering ─────────────────────────────────
    print("\n" + "-" * 60)
    print("PHASE 3: Primordial Clustering")
    print("-" * 60)

    prim_results = validator.test_primordial_clustering()
    print(f"  Analyzed {len(prim_results)} primordial categories")

    if prim_results:
        sorted_prims = sorted(prim_results.items(), key=lambda x: x[1]["mean_distance"])
        print(f"\n  Most cohesive (tightest clusters):")
        for prim, data in sorted_prims[:5]:
            print(f"    {prim:20s}  {data['archetype_count']} archetypes, "
                  f"mean_dist={data['mean_distance']:.3f} (std={data['std_distance']:.3f})")

        print(f"\n  Most spread (loosest clusters):")
        for prim, data in sorted_prims[-3:]:
            print(f"    {prim:20s}  {data['archetype_count']} archetypes, "
                  f"mean_dist={data['mean_distance']:.3f} (std={data['std_distance']:.3f})")

    # ── Motif Clustering ──────────────────────────────────────
    print("\n" + "-" * 60)
    print("PHASE 4: Thompson Motif Signatures")
    print("-" * 60)

    motif_analyzer = MotifClustering(acp, library, mapper)
    motif_results = motif_analyzer.find_motif_category_patterns()

    summary = motif_results["summary"]
    print(f"  Motifs analyzed:   {summary['total_motifs_analyzed']}")
    print(f"  Tightly clustered: {summary['clustered_count']}")
    print(f"  Broadly spread:    {summary['spread_count']}")
    print(f"  Categories:        {summary['categories_analyzed']}")

    if motif_results.get("global_mean"):
        print(f"\n  Global mean (across all mapped entities):")
        for axis, val in motif_results["global_mean"].items():
            print(f"    {axis:25s}: {val:.4f}")

    if motif_results.get("category_centroids"):
        print(f"\n  Category centroids (mean-centered dominant axis):")
        for cat, data in sorted(motif_results["category_centroids"].items()):
            dom = data['dominant_axis']
            direction = data.get('dominant_direction', '?')
            dev = data.get('deviation_from_mean', {}).get(dom, 0)
            print(f"    {cat}: {data['motif_count']:3d} motifs, "
                  f"dominant = {dom} ({direction}, dev={dev:+.4f})")

    # ── Coordinate Calibration ───────────────────────────────
    print("\n" + "-" * 60)
    print("PHASE 5: Coordinate Calibration")
    print("-" * 60)

    calibrator = CoordinateCalibrator(acp, library, mapper)
    cal_result = calibrator.calibrate(
        learning_rate=0.02,
        max_steps=1000,
        max_shift=0.15,
        exclude_entities=["Set"]
    )

    print(f"  Entities calibrated: {cal_result['entity_count']}")
    print(f"  Loss: {cal_result['initial_loss']:.4f} -> {cal_result['final_loss']:.4f} ({cal_result['loss_reduction_pct']}% reduction)")
    print(f"  Mean shift: {cal_result['mean_shift']:.4f}")
    print(f"  Max shift:  {cal_result['max_shift']:.4f}")

    # Apply calibration and re-test
    calibrator.apply_calibration(cal_result['calibrated_coordinates'])
    cal_coord_results = validator.test_distance_correlation(exclude_entities=["Set"])
    print_correlation("After calibration (excluding 'Set')", cal_coord_results)

    # ── Statistical Rigor (Phase 5) ─────────────────────────
    # Reload ACP to get clean (uncalibrated) coordinates for statistical tests
    print("\n" + "-" * 60)
    print("PHASE 6: Statistical Rigor")
    print("-" * 60)

    acp_clean = ACPLoader(str(ACP_PATH))
    mapper_clean = EntityMapper(acp_clean, library)
    mapper_clean.auto_map_all()
    stat_tests = StatisticalTests(acp_clean, library, mapper_clean)

    # 6a. Permutation test
    print("\n  6a. Permutation Test (1000 shuffles)...")
    perm_result = stat_tests.permutation_test(
        n_permutations=1000, exclude_entities=["Set"], seed=42
    )
    if "error" not in perm_result:
        null = perm_result["null_distribution"]
        print(f"      Observed Spearman r:  {perm_result['observed_spearman_r']}")
        print(f"      Null mean ± std:      {null['mean']} ± {null['std']}")
        print(f"      Null 5th-95th %%ile:   [{null['percentile_5']}, {null['percentile_95']}]")
        print(f"      Empirical p-value:    {perm_result['empirical_p_value']}")
        print(f"      -> {perm_result['conclusion']}")
    else:
        print(f"      ERROR: {perm_result['error']}")

    # 6b. Bootstrap confidence intervals
    print("\n  6b. Bootstrap Confidence Intervals (1000 resamples)...")
    boot_result = stat_tests.bootstrap_confidence_intervals(
        n_bootstrap=1000, exclude_entities=["Set"], seed=42
    )
    if "error" not in boot_result:
        sp = boot_result["spearman"]
        pe = boot_result["pearson"]
        print(f"      Spearman r = {sp['observed']}  95% CI [{sp['ci_lower']}, {sp['ci_upper']}]")
        print(f"      Pearson r  = {pe['observed']}  95% CI [{pe['ci_lower']}, {pe['ci_upper']}]")
    else:
        print(f"      ERROR: {boot_result['error']}")

    # 6c. Effect size
    print("\n  6c. Effect Size Report...")
    effect_result = stat_tests.effect_size_report(exclude_entities=["Set"])
    if "error" not in effect_result:
        print(f"      Spearman r² = {effect_result['r_squared_spearman']} "
              f"({effect_result['variance_explained_pct']}% variance explained)")
        print(f"      Cohen's q   = {effect_result['cohens_q']} ({effect_result['effect_strength']} effect)")
    else:
        print(f"      ERROR: {effect_result['error']}")

    # 6d. Multiple comparison correction for per-tradition tests
    print("\n  6d. Multiple Comparison Correction...")
    tradition_pvals = {}
    for trad, data in tradition_results.items():
        if "spearman_p" in data:
            tradition_pvals[trad] = data["spearman_p"]

    if tradition_pvals:
        mc_result = StatisticalTests.benjamini_hochberg(tradition_pvals)
        print(f"      {mc_result['n_tests']} traditions tested")
        print(f"      Significant after Bonferroni:          {mc_result['n_significant_bonferroni']}")
        print(f"      Significant after Benjamini-Hochberg:  {mc_result['n_significant_bh']}")
        for trad, data in sorted(mc_result["bh_results"].items(),
                                  key=lambda x: x[1]["adjusted_p"]):
            sig = "*" if data["significant_after_correction"] else ""
            print(f"        {trad:15s}  p={data['original_p']:.6f}  adj_p={data['adjusted_p']:.6f} {sig}")
    else:
        mc_result = {}
        print("      No tradition p-values available")

    # 6e. Cross-validation for calibration
    print("\n  6e. Cross-Validation (5-fold)...")
    cv_result = stat_tests.cross_validate_calibration(
        k=5, exclude_entities=["Set"], seed=42
    )
    if "error" not in cv_result:
        agg = cv_result["aggregate"]
        print(f"      {agg['valid_folds']}/{cv_result['k']} valid folds")
        if agg["mean_spearman_r"] is not None:
            print(f"      Mean held-out Spearman r = {agg['mean_spearman_r']} ± {agg['std_spearman_r']}")
        for fold in cv_result["fold_results"]:
            if "spearman_r" in fold:
                print(f"        Fold {fold['fold']}: r={fold['spearman_r']}, "
                      f"train={fold['train_pairs']}, test={fold['test_pairs']}")
            else:
                print(f"        Fold {fold['fold']}: {fold.get('note', 'failed')}")
        print(f"      -> {cv_result['conclusion']}")
    else:
        print(f"      ERROR: {cv_result['error']}")

    # 6f. Holdout tradition tests
    print("\n  6f. Holdout Tradition Tests...")
    holdout_traditions = ["norse", "greek", "indian", "egyptian"]
    holdout_results = {}
    for trad in holdout_traditions:
        hr = stat_tests.holdout_tradition_test(
            holdout_tradition=trad, exclude_entities=["Set"]
        )
        holdout_results[trad] = hr
        if "error" in hr:
            print(f"      {trad:12s}: {hr['error']}")
        elif "note" in hr:
            print(f"      {trad:12s}: {hr['note']} ({hr['test_entities']} entities, {hr['test_pairs']} pairs)")
        else:
            print(f"      {trad:12s}: r={hr['spearman_r']}, p={hr['spearman_p']:.6f}, "
                  f"test_entities={hr['test_entities']}, test_pairs={hr['test_pairs']}, "
                  f"cal_loss_reduction={hr['calibration_loss_reduction_pct']}%")

    # ── Alternative Metrics (Phase 6) ────────────────────────
    print("\n" + "-" * 60)
    print("PHASE 7: Alternative Metrics")
    print("-" * 60)

    alt_metrics = AlternativeMetrics(acp_clean, library, mapper_clean)

    # 7a. Cosine vs Euclidean
    print("\n  7a. Cosine vs Euclidean Distance...")
    cosine_result = alt_metrics.cosine_similarity_test(exclude_entities=["Set"])
    if "error" not in cosine_result:
        print(f"      Euclidean Spearman r:  {cosine_result['euclidean']['spearman_r']}")
        print(f"      Cosine Spearman r:     {cosine_result['cosine']['spearman_r']}")
        print(f"      Winner: {cosine_result['winner']} (by {cosine_result['improvement']})")
    else:
        print(f"      ERROR: {cosine_result['error']}")

    # 7b. Per-axis correlation
    print("\n  7b. Per-Axis Correlation (which axes predict co-occurrence?)...")
    axis_result = alt_metrics.per_axis_correlation(exclude_entities=["Set"])
    if "ranking" in axis_result:
        for item in axis_result["ranking"]:
            sig = "*" if item["spearman_p"] < 0.05 else ""
            print(f"      {item['axis']:25s}  r={item['spearman_r']:+.4f}  p={item['spearman_p']:.6f} {sig}")
        print(f"      Strongest: {axis_result['strongest_axis']}")
        print(f"      Weakest:   {axis_result['weakest_axis']}")

    # 7c. Axis-weighted distance
    print("\n  7c. Axis-Weighted Distance...")
    weighted_result = alt_metrics.axis_weighted_distance_test(exclude_entities=["Set"])
    if "error" not in weighted_result:
        print(f"      Unweighted Spearman r: {weighted_result['unweighted']['spearman_r']}")
        print(f"      Weighted Spearman r:   {weighted_result['weighted']['spearman_r']}")
        print(f"      Winner: {weighted_result['winner']} (by {weighted_result['improvement']})")
        print(f"      Weights: ", end="")
        top_weights = sorted(weighted_result["weights"].items(), key=lambda x: -x[1])[:3]
        print(", ".join(f"{a}={w}" for a, w in top_weights))
    else:
        print(f"      ERROR: {weighted_result['error']}")

    # 7d. Mantel test
    print("\n  7d. Mantel Test (1000 permutations)...")
    mantel_result = alt_metrics.mantel_test(
        n_permutations=1000, exclude_entities=["Set"], seed=42
    )
    if "error" not in mantel_result:
        null = mantel_result["null_distribution"]
        print(f"      Observed Pearson r:  {mantel_result['observed_pearson_r']}")
        print(f"      Null mean ± std:     {null['mean']} ± {null['std']}")
        print(f"      Empirical p-value:   {mantel_result['empirical_p_value']}")
    else:
        print(f"      ERROR: {mantel_result['error']}")

    # 7e. Motif-mediated similarity
    print("\n  7e. Motif-Mediated Similarity (Jaccard)...")
    motif_sim_result = alt_metrics.motif_similarity_test(exclude_entities=["Set"])
    if "error" not in motif_sim_result:
        dvc = motif_sim_result["distance_vs_cooccurrence"]
        jvc = motif_sim_result["jaccard_vs_cooccurrence"]
        dvj = motif_sim_result["distance_vs_jaccard"]
        print(f"      Pairs with shared motifs: {motif_sim_result['pairs_with_shared_motifs']}")
        print(f"      ACP dist vs co-occurrence:     r={dvc['spearman_r']}")
        print(f"      Motif Jaccard vs co-occurrence: r={jvc['spearman_r']}")
        print(f"      ACP dist vs Jaccard:            r={dvj['spearman_r']}")
        print(f"      Better predictor: {motif_sim_result['better_predictor_of_cooccurrence']}")
    else:
        print(f"      ERROR: {motif_sim_result['error']}")

    # ── Save Results ──────────────────────────────────────────
    print("\n" + "-" * 60)
    print("Saving Results")
    print("-" * 60)

    results = {
        "timestamp": timestamp,
        "summary": {
            "acp_archetypes": acp_summary["archetypes"],
            "acp_primordials": acp_summary["primordials"],
            "library_entities": lib_summary["entities"],
            "library_segments": lib_summary["segments"],
            "library_motif_tags": lib_summary["motif_tags"],
            "mapped_entities": map_summary["total_mapped"],
            "unmapped_entities": len(unmapped),
            "mapping_coverage_pct": round(pct, 1),
        },
        "entity_mapping": map_summary,
        "coordinate_validation": coord_results,
        "coordinate_validation_clean": coord_results_clean,
        "per_tradition_correlation": tradition_results,
        "primordial_clustering": prim_results,
        "motif_analysis": {
            "summary": motif_results["summary"],
            "global_mean": motif_results.get("global_mean", {}),
            "category_centroids": motif_results.get("category_centroids", {}),
        },
        "calibration": {
            "params": cal_result["params"],
            "initial_loss": cal_result["initial_loss"],
            "final_loss": cal_result["final_loss"],
            "loss_reduction_pct": cal_result["loss_reduction_pct"],
            "mean_shift": cal_result["mean_shift"],
            "max_shift": cal_result["max_shift"],
            "post_calibration_correlation": cal_coord_results.get("all_pairs", {}),
        },
        "statistical_rigor": {
            "permutation_test": perm_result,
            "bootstrap_ci": boot_result,
            "effect_size": effect_result,
            "multiple_comparison": mc_result,
            "cross_validation": cv_result,
            "holdout_traditions": holdout_results,
        },
        "alternative_metrics": {
            "cosine_similarity": cosine_result,
            "per_axis_correlation": axis_result,
            "axis_weighted_distance": weighted_result,
            "mantel_test": mantel_result,
            "motif_similarity": motif_sim_result,
        },
    }

    results_path = OUTPUTS / "metrics" / "validation_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {results_path}")

    # Save full motif signatures separately (can be large)
    motif_path = OUTPUTS / "metrics" / "motif_signatures.json"
    with open(motif_path, "w", encoding="utf-8") as f:
        json.dump(motif_results["motif_signatures"], f, indent=2, ensure_ascii=False)
    print(f"  Saved: {motif_path}")

    # Save calibrated coordinates
    cal_path = OUTPUTS / "metrics" / "calibrated_coordinates.json"
    cal_output = {
        "params": cal_result["params"],
        "metrics": {
            "initial_loss": cal_result["initial_loss"],
            "final_loss": cal_result["final_loss"],
            "loss_reduction_pct": cal_result["loss_reduction_pct"],
            "mean_shift": cal_result["mean_shift"],
        },
        "calibrated_coordinates": cal_result["calibrated_coordinates"],
    }
    with open(cal_path, "w", encoding="utf-8") as f:
        json.dump(cal_output, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {cal_path}")

    print(f"\n{'='*60}")
    print("  Validation Complete")
    print(f"{'='*60}")

    library.close()


if __name__ == "__main__":
    main()
