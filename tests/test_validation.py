"""Automated tests for the ACP validation pipeline.

Tests determinism, known-good outputs, and module correctness.
Run with: pytest tests/ -v
"""
import json
import sys
from pathlib import Path

import pytest
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from integration.acp_loader import ACPLoader, AXES
from integration.library_loader import LibraryLoader
from integration.entity_mapper import EntityMapper
from validation.test_coordinate_accuracy import CoordinateValidation
from validation.test_motif_clustering import MotifClustering
from validation.calibrate_coordinates import CoordinateCalibrator
from validation.statistical_tests import StatisticalTests
from validation.alternative_metrics import AlternativeMetrics
from validation.data_quality import DataQualityAuditor

ACP_PATH = PROJECT_ROOT / "ACP"
DB_PATH = PROJECT_ROOT / "data" / "mythic_patterns.db"


# ── Fixtures ─────────────────────────────────────────────────

@pytest.fixture(scope="session")
def acp():
    return ACPLoader(str(ACP_PATH))


@pytest.fixture(scope="session")
def library():
    lib = LibraryLoader(str(DB_PATH))
    yield lib
    lib.close()


@pytest.fixture(scope="session")
def mapper(acp, library):
    m = EntityMapper(acp, library)
    m.auto_map_all()
    return m


# ── ACP Loader Tests ─────────────────────────────────────────

class TestACPLoader:
    def test_loads_archetypes(self, acp):
        assert acp.summary()["archetypes"] >= 500

    def test_loads_primordials(self, acp):
        assert acp.summary()["primordials"] >= 20

    def test_axes_count(self):
        assert len(AXES) == 8

    def test_coordinate_dimensions(self, acp):
        for arch_id, arch_data in acp.archetypes.items():
            coords = acp.get_coordinates(arch_id)
            if coords is not None:
                assert coords.shape == (8,), f"Wrong shape for {arch_id}"
                assert all(0 <= c <= 1 for c in coords), f"Coords out of range for {arch_id}"

    def test_known_archetype_exists(self, acp):
        """Zeus should be in the ACP."""
        zeus_ids = [aid for aid in acp.archetypes if "ZEUS" in aid.upper()]
        assert len(zeus_ids) >= 1

    def test_aliases_present(self, acp):
        """At least some archetypes should have aliases."""
        alias_count = sum(
            len(d.get("aliases", [])) for d in acp.archetypes.values()
        )
        assert alias_count > 100


# ── Library Loader Tests ─────────────────────────────────────

class TestLibraryLoader:
    def test_entity_count(self, library):
        entities = library.get_all_entities()
        assert len(entities) == 173

    def test_segment_count(self, library):
        assert library.get_segment_count() == 4000

    def test_summary_keys(self, library):
        s = library.summary()
        for key in ["entities", "entity_mentions", "segments", "motifs", "motif_tags"]:
            assert key in s

    def test_cooccurrence_symmetric(self, library):
        """Co-occurrence should be symmetric."""
        c1 = library.get_entity_cooccurrence("Zeus", "Apollo")
        c2 = library.get_entity_cooccurrence("Apollo", "Zeus")
        assert c1 == c2

    def test_known_cooccurrence(self, library):
        """Zeus and Apollo should co-occur in Greek texts."""
        c = library.get_entity_cooccurrence("Zeus", "Apollo")
        assert c > 0

    def test_motif_codes(self, library):
        codes = library.get_all_motif_codes()
        assert len(codes) > 100


# ── Entity Mapper Tests ──────────────────────────────────────

class TestEntityMapper:
    def test_maps_minimum_entities(self, mapper):
        assert len(mapper.mappings) >= 100

    def test_known_mappings(self, mapper):
        """Check specific known entity-archetype pairs."""
        zeus = mapper.get_mapping("Zeus")
        assert zeus is not None
        assert "ZEUS" in zeus.acp_archetype_id.upper()

        odin = mapper.get_mapping("Odin")
        assert odin is not None
        assert "ODIN" in odin.acp_archetype_id.upper()

    def test_tradition_aware(self, mapper):
        """Norse Odin should map to Norse archetype, not Greek."""
        odin = mapper.get_mapping("Odin")
        assert odin is not None
        assert "NO-" in odin.acp_archetype_id or "NO" in odin.acp_archetype_id

    def test_no_self_mapping(self, mapper):
        """No entity should map to itself as a different entity."""
        names = [m.library_entity for m in mapper.mappings]
        assert len(names) == len(set(names)), "Duplicate library entity in mappings"

    def test_unmapped_list(self, mapper):
        unmapped = mapper.get_unmapped_entities()
        assert len(unmapped) > 0
        assert "Achilles" in unmapped  # Known unmapped hero


# ── Coordinate Validation Tests ──────────────────────────────

class TestCoordinateValidation:
    def test_correlation_has_expected_keys(self, acp, library, mapper):
        v = CoordinateValidation(acp, library, mapper)
        result = v.test_distance_correlation(exclude_entities=["Set"])
        assert "all_pairs" in result
        assert "spearman_r" in result["all_pairs"]
        assert "pearson_r" in result["all_pairs"]

    def test_negative_correlation(self, acp, library, mapper):
        """ACP distance should negatively correlate with co-occurrence."""
        v = CoordinateValidation(acp, library, mapper)
        result = v.test_distance_correlation(exclude_entities=["Set"])
        assert result["all_pairs"]["spearman_r"] < 0

    def test_deterministic(self, acp, library, mapper):
        """Same inputs should give same outputs."""
        v = CoordinateValidation(acp, library, mapper)
        r1 = v.test_distance_correlation(exclude_entities=["Set"])
        r2 = v.test_distance_correlation(exclude_entities=["Set"])
        assert r1["all_pairs"]["spearman_r"] == r2["all_pairs"]["spearman_r"]


# ── Statistical Tests ────────────────────────────────────────

class TestStatisticalTests:
    def test_permutation_deterministic(self, acp, library, mapper):
        """Same seed should give same permutation result."""
        # Use fresh ACP to avoid calibrated coords
        acp_fresh = ACPLoader(str(ACP_PATH))
        mapper_fresh = EntityMapper(acp_fresh, library)
        mapper_fresh.auto_map_all()
        st = StatisticalTests(acp_fresh, library, mapper_fresh)

        r1 = st.permutation_test(n_permutations=50, exclude_entities=["Set"], seed=42)
        r2 = st.permutation_test(n_permutations=50, exclude_entities=["Set"], seed=42)
        assert r1["empirical_p_value"] == r2["empirical_p_value"]

    def test_bootstrap_ci_excludes_zero(self, acp, library, mapper):
        """Bootstrap CI should exclude zero (signal is real)."""
        acp_fresh = ACPLoader(str(ACP_PATH))
        mapper_fresh = EntityMapper(acp_fresh, library)
        mapper_fresh.auto_map_all()
        st = StatisticalTests(acp_fresh, library, mapper_fresh)

        result = st.bootstrap_confidence_intervals(
            n_bootstrap=100, exclude_entities=["Set"], seed=42
        )
        sp = result["spearman"]
        assert sp["ci_upper"] < 0, "Bootstrap CI should be entirely negative"

    def test_benjamini_hochberg(self):
        """BH correction should work on known p-values."""
        pvals = {"a": 0.01, "b": 0.04, "c": 0.5}
        result = StatisticalTests.benjamini_hochberg(pvals, alpha=0.05)
        assert result["n_tests"] == 3
        assert result["bh_results"]["a"]["adjusted_p"] < result["bh_results"]["c"]["adjusted_p"]


# ── Alternative Metrics Tests ────────────────────────────────

class TestAlternativeMetrics:
    def test_cosine_has_winner(self, acp, library, mapper):
        acp_fresh = ACPLoader(str(ACP_PATH))
        mapper_fresh = EntityMapper(acp_fresh, library)
        mapper_fresh.auto_map_all()
        am = AlternativeMetrics(acp_fresh, library, mapper_fresh)
        result = am.cosine_similarity_test(exclude_entities=["Set"])
        assert result["winner"] in ("cosine", "euclidean")

    def test_per_axis_ranks_all_axes(self, acp, library, mapper):
        acp_fresh = ACPLoader(str(ACP_PATH))
        mapper_fresh = EntityMapper(acp_fresh, library)
        mapper_fresh.auto_map_all()
        am = AlternativeMetrics(acp_fresh, library, mapper_fresh)
        result = am.per_axis_correlation(exclude_entities=["Set"])
        assert len(result["ranking"]) == 8
        assert result["strongest_axis"] is not None

    def test_mantel_deterministic(self, acp, library, mapper):
        acp_fresh = ACPLoader(str(ACP_PATH))
        mapper_fresh = EntityMapper(acp_fresh, library)
        mapper_fresh.auto_map_all()
        am = AlternativeMetrics(acp_fresh, library, mapper_fresh)
        r1 = am.mantel_test(n_permutations=50, exclude_entities=["Set"], seed=42)
        r2 = am.mantel_test(n_permutations=50, exclude_entities=["Set"], seed=42)
        assert r1["empirical_p_value"] == r2["empirical_p_value"]


# ── Data Quality Tests ───────────────────────────────────────

class TestDataQuality:
    def test_audit_no_flags(self, acp, library, mapper):
        acp_fresh = ACPLoader(str(ACP_PATH))
        mapper_fresh = EntityMapper(acp_fresh, library)
        mapper_fresh.auto_map_all()
        dq = DataQualityAuditor(acp_fresh, library, mapper_fresh)
        result = dq.entity_mention_audit(sample_size=50, seed=42)
        total_flags = sum(result["flags"].values())
        assert total_flags == 0, f"Expected 0 flags, got {result['flags']}"

    def test_unmapped_analysis(self, acp, library, mapper):
        acp_fresh = ACPLoader(str(ACP_PATH))
        mapper_fresh = EntityMapper(acp_fresh, library)
        mapper_fresh.auto_map_all()
        dq = DataQualityAuditor(acp_fresh, library, mapper_fresh)
        result = dq.unmapped_entity_analysis()
        assert result["total_entities"] == 173
        assert result["mapped"] + result["unmapped"] == result["total_entities"]

    def test_dedup_check(self, acp, library, mapper):
        acp_fresh = ACPLoader(str(ACP_PATH))
        mapper_fresh = EntityMapper(acp_fresh, library)
        mapper_fresh.auto_map_all()
        dq = DataQualityAuditor(acp_fresh, library, mapper_fresh)
        result = dq.cross_tradition_deduplication_check()
        assert "shared_archetypes" in result
        assert result["shared_archetypes"]["cross_tradition"] <= 5  # Should be very few


# ── Calibration Tests ────────────────────────────────────────

class TestCalibration:
    def test_calibration_improves(self, acp, library, mapper):
        """Calibration should reduce loss."""
        cal = CoordinateCalibrator(acp, library, mapper)
        result = cal.calibrate(
            learning_rate=0.02, max_steps=100, max_shift=0.15,
            exclude_entities=["Set"]
        )
        assert result["final_loss"] < result["initial_loss"]

    def test_calibration_respects_bounds(self, acp, library, mapper):
        """Calibrated coordinates should stay in [0, 1]."""
        cal = CoordinateCalibrator(acp, library, mapper)
        result = cal.calibrate(
            learning_rate=0.02, max_steps=100, max_shift=0.15,
            exclude_entities=["Set"]
        )
        for arch_id, coords in result["calibrated_coordinates"].items():
            # coords is a dict of axis_name -> float
            for axis, v in coords.items():
                assert 0 <= v <= 1, f"Coordinate {axis}={v} out of bounds for {arch_id}"


# ── Report Generation Tests ──────────────────────────────────

class TestReportGeneration:
    def test_report_generates(self):
        """Report generator should produce valid markdown from mock data."""
        from validation.run import generate_report

        mock_results = {
            "timestamp": "2026-01-27T00:00:00Z",
            "mode": "quick",
            "summary": {
                "acp_archetypes": 539,
                "library_entities": 173,
                "library_segments": 4000,
                "mapped_entities": 109,
                "mapping_coverage_pct": 63.0,
            },
            "coordinate_validation": {
                "all_pairs": {"spearman_r": -0.0946, "pearson_r": -0.0834},
            },
            "per_tradition_correlation": {},
            "motif_analysis": {"summary": {}, "global_mean": {}},
            "calibration": {
                "initial_loss": 0.12, "final_loss": 0.08,
                "loss_reduction_pct": 33.7,
                "post_calibration": {"spearman_r": -0.233},
            },
            "statistical_rigor": {
                "permutation_test": {"empirical_p_value": 0.053, "n_permutations": 1000},
                "bootstrap_ci": {"spearman": {"ci_lower": -0.121, "ci_upper": -0.070, "observed": -0.095}},
                "effect_size": {"r_squared_spearman": 0.009, "variance_explained_pct": 0.89, "cohens_q": 0.095, "effect_strength": "negligible"},
                "multiple_comparison": {"n_significant_bh": 0, "n_tests": 12},
                "cross_validation": {"aggregate": {"mean_spearman_r": -0.225, "std_spearman_r": 0.041}},
                "holdout_traditions": {},
            },
            "alternative_metrics": {
                "cosine_similarity": {"euclidean": {"spearman_r": -0.095}, "cosine": {"spearman_r": -0.036}},
                "per_axis_correlation": {"ranking": []},
                "axis_weighted_distance": {"weighted": {"spearman_r": -0.142}, "unweighted": {"spearman_r": -0.095}},
                "mantel_test": {"observed_pearson_r": -0.063, "empirical_p_value": 0.029},
                "motif_similarity": {"jaccard_vs_cooccurrence": {"spearman_r": 0.749}, "distance_vs_jaccard": {"spearman_r": -0.110}},
            },
            "data_quality": {
                "entity_mention_audit": {"sample_size": 100, "flags": {"no_context": 0, "short_mention": 0, "tiny_segment": 0, "duplicate_offset": 0}},
                "normalized_cooccurrence": {"best_method": "raw"},
                "deduplication_check": {"shared_archetypes": {"cross_tradition": 1}},
                "unmapped_analysis": {"unmapped": 64, "total_entities": 173, "mention_mass": {"pct_unmapped": 44.0}, "by_type": {"hero": {"count": 42}}},
            },
        }

        report = generate_report(mock_results)
        assert "# ACP Validation Report" in report
        assert "Statistical Rigor" in report
        assert "Conclusions" in report
        assert len(report) > 500
