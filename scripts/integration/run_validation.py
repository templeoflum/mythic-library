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

ACP_PATH = PROJECT_ROOT / "ACP"
DB_PATH = PROJECT_ROOT / "data" / "mythic_patterns.db"
OUTPUTS = PROJECT_ROOT / "outputs"


def main():
    print("=" * 60)
    print("  MythOS Validation Suite")
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

    print(f"\n{'='*60}")
    print("  Validation Complete")
    print(f"{'='*60}")

    library.close()


if __name__ == "__main__":
    main()
