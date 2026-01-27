"""Phase 5: Statistical rigor tests for ACP validation.

Provides:
- Permutation test (null model)
- Bootstrap confidence intervals
- K-fold cross-validation for calibration
- Holdout tradition generalization test
- Multiple comparison correction (Bonferroni / Benjamini-Hochberg)
- Effect size reporting
"""
import numpy as np
from scipy.stats import spearmanr, pearsonr
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from integration.acp_loader import ACPLoader, AXES
from integration.library_loader import LibraryLoader
from integration.entity_mapper import EntityMapper
from validation.calibrate_coordinates import CoordinateCalibrator


class StatisticalTests:
    def __init__(self, acp: ACPLoader, library: LibraryLoader, mapper: EntityMapper):
        self.acp = acp
        self.library = library
        self.mapper = mapper

    def _get_distance_cooccurrence_arrays(
        self, exclude_entities: Optional[List[str]] = None
    ) -> Tuple[np.ndarray, np.ndarray, List[Tuple[str, str]]]:
        """Extract parallel arrays of distances and co-occurrences for all valid pairs."""
        exclude = set(exclude_entities or [])
        valid = [
            m for m in self.mapper.mappings
            if m.library_entity not in exclude
            and self.acp.get_coordinates(m.acp_archetype_id) is not None
        ]

        distances = []
        cooccurrences = []
        pairs = []

        for i, m1 in enumerate(valid):
            for m2 in valid[i + 1:]:
                dist = self.acp.calculate_distance(
                    m1.acp_archetype_id, m2.acp_archetype_id
                )
                if dist is None:
                    continue
                coocc = self.library.get_entity_cooccurrence(
                    m1.library_entity, m2.library_entity
                )
                distances.append(dist)
                cooccurrences.append(coocc)
                pairs.append((m1.library_entity, m2.library_entity))

        return np.array(distances), np.array(cooccurrences), pairs

    # ── Permutation Test ──────────────────────────────────────

    def permutation_test(
        self,
        n_permutations: int = 1000,
        exclude_entities: Optional[List[str]] = None,
        seed: int = 42,
    ) -> Dict:
        """Test if real ACP coordinates predict co-occurrence better than random assignments.

        Shuffles entity-to-archetype mappings n_permutations times. For each shuffle,
        recomputes all pairwise distances using the shuffled coordinates and measures
        Spearman correlation with the (unchanged) co-occurrence data.

        Returns the observed correlation, distribution of null correlations, and
        empirical p-value (fraction of permutations that beat the observed value).
        """
        rng = np.random.default_rng(seed)
        exclude = set(exclude_entities or [])

        # Get valid mappings with coordinates
        valid = [
            m for m in self.mapper.mappings
            if m.library_entity not in exclude
            and self.acp.get_coordinates(m.acp_archetype_id) is not None
        ]
        n = len(valid)

        # Pre-compute co-occurrence matrix (fixed across permutations)
        coocc_flat = []
        pair_indices = []
        for i in range(n):
            for j in range(i + 1, n):
                coocc = self.library.get_entity_cooccurrence(
                    valid[i].library_entity, valid[j].library_entity
                )
                coocc_flat.append(coocc)
                pair_indices.append((i, j))

        coocc_array = np.array(coocc_flat)
        n_pairs = len(coocc_flat)

        if n_pairs < 10:
            return {"error": "Insufficient pairs for permutation test", "n_pairs": n_pairs}

        # Collect all coordinate vectors
        all_coords = np.array([
            self.acp.get_coordinates(m.acp_archetype_id) for m in valid
        ])

        # Observed correlation (real assignment)
        real_distances = np.array([
            float(np.linalg.norm(all_coords[i] - all_coords[j]))
            for i, j in pair_indices
        ])
        observed_r, observed_p = spearmanr(real_distances, coocc_array)

        # Permutation loop: shuffle which coordinate vector is assigned to which entity
        null_correlations = []
        for _ in range(n_permutations):
            perm = rng.permutation(n)
            shuffled_coords = all_coords[perm]
            perm_distances = np.array([
                float(np.linalg.norm(shuffled_coords[i] - shuffled_coords[j]))
                for i, j in pair_indices
            ])
            r, _ = spearmanr(perm_distances, coocc_array)
            null_correlations.append(float(r))

        null_array = np.array(null_correlations)

        # Empirical p-value: fraction of null correlations <= observed
        # (we expect negative correlation, so count how many null values are
        #  as negative or more negative than observed)
        empirical_p = float(np.mean(null_array <= observed_r))

        return {
            "observed_spearman_r": round(float(observed_r), 4),
            "observed_spearman_p": round(float(observed_p), 6),
            "n_permutations": n_permutations,
            "n_entities": n,
            "n_pairs": n_pairs,
            "empirical_p_value": round(empirical_p, 4),
            "null_distribution": {
                "mean": round(float(null_array.mean()), 4),
                "std": round(float(null_array.std()), 4),
                "min": round(float(null_array.min()), 4),
                "max": round(float(null_array.max()), 4),
                "percentile_5": round(float(np.percentile(null_array, 5)), 4),
                "percentile_95": round(float(np.percentile(null_array, 95)), 4),
            },
            "conclusion": (
                "SIGNIFICANT: Real ACP coordinates predict co-occurrence better than random"
                if empirical_p < 0.05 else
                "NOT SIGNIFICANT: Random coordinates perform comparably to real ACP"
            ),
        }

    # ── Bootstrap Confidence Intervals ────────────────────────

    def bootstrap_confidence_intervals(
        self,
        n_bootstrap: int = 1000,
        confidence: float = 0.95,
        exclude_entities: Optional[List[str]] = None,
        seed: int = 42,
    ) -> Dict:
        """Compute bootstrap 95% confidence intervals for Spearman and Pearson correlations.

        Resamples entity pairs with replacement and recomputes correlations.
        """
        rng = np.random.default_rng(seed)
        distances, cooccurrences, _ = self._get_distance_cooccurrence_arrays(exclude_entities)

        n_pairs = len(distances)
        if n_pairs < 10:
            return {"error": "Insufficient pairs for bootstrap", "n_pairs": n_pairs}

        # Observed values
        obs_spearman, _ = spearmanr(distances, cooccurrences)
        obs_pearson, _ = pearsonr(distances, cooccurrences)

        # Bootstrap
        spearman_samples = []
        pearson_samples = []
        for _ in range(n_bootstrap):
            idx = rng.choice(n_pairs, size=n_pairs, replace=True)
            d_boot = distances[idx]
            c_boot = cooccurrences[idx]
            # Check variance (constant arrays break correlation)
            if len(set(d_boot)) < 2 or len(set(c_boot)) < 2:
                continue
            sr, _ = spearmanr(d_boot, c_boot)
            pr, _ = pearsonr(d_boot, c_boot)
            spearman_samples.append(float(sr))
            pearson_samples.append(float(pr))

        alpha = 1 - confidence
        lo = alpha / 2 * 100
        hi = (1 - alpha / 2) * 100

        sp_arr = np.array(spearman_samples)
        pe_arr = np.array(pearson_samples)

        return {
            "n_bootstrap": n_bootstrap,
            "n_valid_samples": len(spearman_samples),
            "n_pairs": n_pairs,
            "confidence_level": confidence,
            "spearman": {
                "observed": round(float(obs_spearman), 4),
                "ci_lower": round(float(np.percentile(sp_arr, lo)), 4),
                "ci_upper": round(float(np.percentile(sp_arr, hi)), 4),
                "bootstrap_mean": round(float(sp_arr.mean()), 4),
                "bootstrap_std": round(float(sp_arr.std()), 4),
            },
            "pearson": {
                "observed": round(float(obs_pearson), 4),
                "ci_lower": round(float(np.percentile(pe_arr, lo)), 4),
                "ci_upper": round(float(np.percentile(pe_arr, hi)), 4),
                "bootstrap_mean": round(float(pe_arr.mean()), 4),
                "bootstrap_std": round(float(pe_arr.std()), 4),
            },
        }

    # ── K-Fold Cross-Validation for Calibration ──────────────

    def cross_validate_calibration(
        self,
        k: int = 5,
        learning_rate: float = 0.02,
        max_steps: int = 1000,
        max_shift: float = 0.15,
        exclude_entities: Optional[List[str]] = None,
        seed: int = 42,
    ) -> Dict:
        """K-fold cross-validation for coordinate calibration.

        Splits entity pairs into k folds. For each fold:
        1. Train calibration on k-1 folds (optimize coordinates using those pairs' co-occurrence)
        2. Test on held-out fold (compute correlation on unseen pairs)

        This checks whether calibration generalizes or overfits.
        """
        rng = np.random.default_rng(seed)
        exclude = set(exclude_entities or [])

        # Build training data at the calibrator level
        calibrator = CoordinateCalibrator(self.acp, self.library, self.mapper)
        arch_ids, original_coords, targets = calibrator._build_training_data(
            list(exclude) if exclude else None
        )
        n = len(arch_ids)
        target_distances = 1.0 - targets

        # Build flat list of pair indices
        pair_indices = [(i, j) for i in range(n) for j in range(i + 1, n)]
        n_pairs = len(pair_indices)

        if n_pairs < k * 2:
            return {"error": f"Insufficient pairs ({n_pairs}) for {k}-fold CV"}

        # Shuffle and split into folds
        perm = rng.permutation(n_pairs)
        fold_size = n_pairs // k
        folds = []
        for f in range(k):
            start = f * fold_size
            end = start + fold_size if f < k - 1 else n_pairs
            folds.append(set(perm[start:end].tolist()))

        fold_results = []
        for fold_idx in range(k):
            test_set = folds[fold_idx]
            train_set = set(range(n_pairs)) - test_set

            train_pairs = [pair_indices[p] for p in train_set]
            test_pairs = [pair_indices[p] for p in test_set]

            # Train: gradient descent using only train pairs
            coords = original_coords.copy()
            n_train = len(train_pairs)

            for step in range(max_steps):
                grad = np.zeros_like(coords)
                for i, j in train_pairs:
                    diff = coords[i] - coords[j]
                    dist = np.sqrt(np.sum(diff ** 2)) + 1e-8
                    target = target_distances[i, j]
                    scale = 2 * (dist - target) / dist
                    grad[i] += scale * diff
                    grad[j] -= scale * diff

                grad /= max(n_train, 1)
                coords -= learning_rate * grad
                coords = np.clip(coords, 0.0, 1.0)
                shift = np.clip(coords - original_coords, -max_shift, max_shift)
                coords = original_coords + shift

            # Test: compute correlation on held-out pairs
            test_distances = []
            test_targets = []
            for i, j in test_pairs:
                d = float(np.linalg.norm(coords[i] - coords[j]))
                test_distances.append(d)
                # Use actual co-occurrence (not target distance) for correlation
                test_targets.append(targets[i, j])

            test_dist_arr = np.array(test_distances)
            test_tgt_arr = np.array(test_targets)

            if len(set(test_distances)) >= 2 and len(set(test_targets)) >= 2:
                sr, sp = spearmanr(test_dist_arr, test_tgt_arr)
                fold_results.append({
                    "fold": fold_idx,
                    "train_pairs": n_train,
                    "test_pairs": len(test_pairs),
                    "spearman_r": round(float(sr), 4),
                    "spearman_p": round(float(sp), 6),
                })
            else:
                fold_results.append({
                    "fold": fold_idx,
                    "train_pairs": n_train,
                    "test_pairs": len(test_pairs),
                    "note": "Insufficient variance in test fold",
                })

        # Aggregate
        valid_folds = [f for f in fold_results if "spearman_r" in f]
        if valid_folds:
            rs = [f["spearman_r"] for f in valid_folds]
            mean_r = np.mean(rs)
            std_r = np.std(rs)
        else:
            mean_r = None
            std_r = None

        return {
            "k": k,
            "total_pairs": n_pairs,
            "fold_results": fold_results,
            "aggregate": {
                "mean_spearman_r": round(float(mean_r), 4) if mean_r is not None else None,
                "std_spearman_r": round(float(std_r), 4) if std_r is not None else None,
                "valid_folds": len(valid_folds),
            },
            "conclusion": (
                f"Cross-validated Spearman r = {mean_r:.4f} ± {std_r:.4f} "
                f"({len(valid_folds)}/{k} valid folds)"
                if mean_r is not None else
                "Cross-validation failed: insufficient variance in folds"
            ),
        }

    # ── Holdout Tradition Test ────────────────────────────────

    def holdout_tradition_test(
        self,
        holdout_tradition: str,
        learning_rate: float = 0.02,
        max_steps: int = 1000,
        max_shift: float = 0.15,
        exclude_entities: Optional[List[str]] = None,
    ) -> Dict:
        """Calibrate on all traditions except one, test on the held-out tradition.

        Tests whether calibration generalizes across cultural boundaries.
        """
        exclude = set(exclude_entities or [])

        # Classify mappings by tradition
        entities = self.library.get_all_entities()
        entity_dict = {e.canonical_name: e for e in entities}

        train_entities = []
        test_entities = []
        for m in self.mapper.mappings:
            if m.library_entity in exclude:
                continue
            if self.acp.get_coordinates(m.acp_archetype_id) is None:
                continue
            e = entity_dict.get(m.library_entity)
            if not e:
                continue
            if e.primary_tradition == holdout_tradition:
                test_entities.append(m)
            else:
                train_entities.append(m)

        if len(test_entities) < 3:
            return {
                "error": f"Insufficient test entities for tradition '{holdout_tradition}'",
                "test_count": len(test_entities),
            }

        # Calibrate using only train entities
        # We need to build training data manually for the subset
        calibrator = CoordinateCalibrator(self.acp, self.library, self.mapper)

        # Exclude holdout tradition entities from calibration
        holdout_entity_names = [m.library_entity for m in test_entities]
        all_exclude = list(exclude) + holdout_entity_names

        cal_result = calibrator.calibrate(
            learning_rate=learning_rate,
            max_steps=max_steps,
            max_shift=max_shift,
            exclude_entities=all_exclude,
        )

        # Apply calibration in-memory
        calibrator.apply_calibration(cal_result["calibrated_coordinates"])

        # Test on holdout tradition: compute distance-co-occurrence correlation
        test_distances = []
        test_cooccurrences = []
        for i, m1 in enumerate(test_entities):
            for m2 in test_entities[i + 1:]:
                dist = self.acp.calculate_distance(
                    m1.acp_archetype_id, m2.acp_archetype_id
                )
                if dist is None:
                    continue
                coocc = self.library.get_entity_cooccurrence(
                    m1.library_entity, m2.library_entity
                )
                test_distances.append(dist)
                test_cooccurrences.append(coocc)

        # Restore original coordinates (undo in-memory calibration)
        # Re-load from the original archetype data by resetting spectralCoordinates
        for arch_id, new_coords in cal_result["calibrated_coordinates"].items():
            if arch_id in self.acp.archetypes:
                # We need original coords — they were overwritten. Use the shift_details.
                shift = cal_result["shift_details"].get(arch_id, {}).get("per_axis", {})
                original = {}
                for axis in AXES:
                    original[axis] = round(new_coords[axis] - shift.get(axis, 0), 4)
                self.acp.archetypes[arch_id]["spectralCoordinates"] = original

        if len(test_distances) < 3:
            return {
                "error": "Insufficient test pairs",
                "holdout_tradition": holdout_tradition,
                "test_entities": len(test_entities),
                "test_pairs": len(test_distances),
            }

        if len(set(test_distances)) < 2 or len(set(test_cooccurrences)) < 2:
            return {
                "holdout_tradition": holdout_tradition,
                "train_entities": len(train_entities),
                "test_entities": len(test_entities),
                "test_pairs": len(test_distances),
                "note": "Insufficient variance in holdout pairs",
            }

        sr, sp = spearmanr(test_distances, test_cooccurrences)
        pairs_with_coocc = sum(1 for c in test_cooccurrences if c > 0)

        return {
            "holdout_tradition": holdout_tradition,
            "train_entities": len(train_entities),
            "test_entities": len(test_entities),
            "test_pairs": len(test_distances),
            "pairs_with_cooccurrence": pairs_with_coocc,
            "calibration_loss_reduction_pct": cal_result["loss_reduction_pct"],
            "spearman_r": round(float(sr), 4),
            "spearman_p": round(float(sp), 6),
        }

    # ── Multiple Comparison Correction ────────────────────────

    @staticmethod
    def benjamini_hochberg(p_values: Dict[str, float], alpha: float = 0.05) -> Dict:
        """Apply Benjamini-Hochberg FDR correction to a set of p-values.

        Returns corrected p-values and which tests remain significant.
        """
        labels = list(p_values.keys())
        pvals = np.array([p_values[l] for l in labels])
        n = len(pvals)

        # Sort p-values
        sorted_idx = np.argsort(pvals)
        sorted_pvals = pvals[sorted_idx]

        # BH critical values
        bh_critical = np.array([(i + 1) / n * alpha for i in range(n)])

        # Find largest k where p(k) <= (k/n)*alpha
        significant = sorted_pvals <= bh_critical

        # Adjusted p-values (Yekutieli step-up)
        adjusted = np.zeros(n)
        adjusted[sorted_idx[-1]] = sorted_pvals[-1]
        for i in range(n - 2, -1, -1):
            adj = sorted_pvals[i] * n / (i + 1)
            adjusted[sorted_idx[i]] = min(adj, adjusted[sorted_idx[i + 1]])
        adjusted = np.minimum(adjusted, 1.0)

        results = {}
        for i, label in enumerate(labels):
            results[label] = {
                "original_p": round(float(pvals[i]), 6),
                "adjusted_p": round(float(adjusted[i]), 6),
                "significant_after_correction": bool(adjusted[i] < alpha),
            }

        bonferroni = {
            label: {
                "original_p": round(float(pvals[i]), 6),
                "adjusted_p": round(float(min(pvals[i] * n, 1.0)), 6),
                "significant_after_correction": bool(pvals[i] * n < alpha),
            }
            for i, label in enumerate(labels)
        }

        return {
            "method": "Benjamini-Hochberg FDR",
            "alpha": alpha,
            "n_tests": n,
            "n_significant_bh": sum(1 for r in results.values() if r["significant_after_correction"]),
            "n_significant_bonferroni": sum(1 for r in bonferroni.values() if r["significant_after_correction"]),
            "bh_results": results,
            "bonferroni_results": bonferroni,
        }

    # ── Effect Size Reporting ─────────────────────────────────

    def effect_size_report(
        self, exclude_entities: Optional[List[str]] = None
    ) -> Dict:
        """Report effect sizes: r², Cohen's q, and explained variance.

        - r² (coefficient of determination): proportion of variance explained
        - Cohen's q: standardized difference between correlations (vs r=0)
        - Practical interpretation thresholds
        """
        distances, cooccurrences, _ = self._get_distance_cooccurrence_arrays(exclude_entities)

        if len(distances) < 10:
            return {"error": "Insufficient pairs"}

        sr, sp = spearmanr(distances, cooccurrences)
        pr, pp = pearsonr(distances, cooccurrences)

        # r-squared
        r_squared_spearman = sr ** 2
        r_squared_pearson = pr ** 2

        # Cohen's q (comparing observed r to null r=0)
        # q = 0.5 * |ln((1+r1)/(1-r1)) - ln((1+r2)/(1-r2))|
        def fisher_z(r):
            r = np.clip(r, -0.999, 0.999)
            return 0.5 * np.log((1 + r) / (1 - r))

        cohens_q = abs(fisher_z(sr) - fisher_z(0))

        # Interpretation
        if abs(sr) >= 0.5:
            strength = "large"
        elif abs(sr) >= 0.3:
            strength = "medium"
        elif abs(sr) >= 0.1:
            strength = "small"
        else:
            strength = "negligible"

        return {
            "spearman_r": round(float(sr), 4),
            "spearman_p": round(float(sp), 6),
            "pearson_r": round(float(pr), 4),
            "pearson_p": round(float(pp), 6),
            "r_squared_spearman": round(float(r_squared_spearman), 4),
            "r_squared_pearson": round(float(r_squared_pearson), 4),
            "variance_explained_pct": round(float(r_squared_spearman * 100), 2),
            "cohens_q": round(float(cohens_q), 4),
            "effect_strength": strength,
            "interpretation": (
                f"Spearman r={sr:.4f} explains {r_squared_spearman*100:.1f}% of variance. "
                f"Cohen's q={cohens_q:.3f} ({strength} effect). "
                f"{'Statistically significant' if sp < 0.05 else 'Not statistically significant'} "
                f"(p={sp:.6f})."
            ),
        }

    # ── Convenience: run all Phase 5 tests ────────────────────

    def run_all(
        self,
        exclude_entities: Optional[List[str]] = None,
        n_permutations: int = 1000,
        n_bootstrap: int = 1000,
        k_folds: int = 5,
        holdout_traditions: Optional[List[str]] = None,
        tradition_p_values: Optional[Dict[str, float]] = None,
        seed: int = 42,
    ) -> Dict:
        """Run the complete Phase 5 statistical rigor suite."""

        results = {}

        # 1. Permutation test
        results["permutation_test"] = self.permutation_test(
            n_permutations=n_permutations,
            exclude_entities=exclude_entities,
            seed=seed,
        )

        # 2. Bootstrap CIs
        results["bootstrap_ci"] = self.bootstrap_confidence_intervals(
            n_bootstrap=n_bootstrap,
            exclude_entities=exclude_entities,
            seed=seed,
        )

        # 3. Cross-validation
        results["cross_validation"] = self.cross_validate_calibration(
            k=k_folds,
            exclude_entities=exclude_entities,
            seed=seed,
        )

        # 4. Effect size
        results["effect_size"] = self.effect_size_report(
            exclude_entities=exclude_entities,
        )

        # 5. Multiple comparison correction (if tradition p-values provided)
        if tradition_p_values:
            results["multiple_comparison"] = self.benjamini_hochberg(tradition_p_values)

        # 6. Holdout tradition tests
        if holdout_traditions:
            results["holdout_traditions"] = {}
            for trad in holdout_traditions:
                results["holdout_traditions"][trad] = self.holdout_tradition_test(
                    holdout_tradition=trad,
                    exclude_entities=exclude_entities,
                )

        return results
