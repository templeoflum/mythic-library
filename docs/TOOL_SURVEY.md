# Tool survey

A record of whether each runnable tool in the repo runs on `main` (da35a4e, 2026-10-22).
It covers `scripts/`, `validation/`, `integration/`, `ACP/tools/`, `ACP/calibration/` and `ACP/launch.sh`.
Every Python file with a `__main__` block in those folders is listed, along with every Node script and shell script.

## How it was run

- A clean copy of `main` was made with `git archive`, outside the checkout. Each tool ran there with stdin from `/dev/null` and a 900 s timeout.
- Software: Python 3.14 in a venv with `requirements.txt`, and Node 22.
- `scripts/database/create_db.py` ran first. The database was restored from that first build before each later tool ran.
- Tracked files were reset after each tool. Gitignored outputs (`outputs/`, the database) were kept, so later tools could read what earlier ones wrote. The order matches the table.
- Tools that change data were run with `--dry-run` where they offer it. Tools that fetch from the network or start a server were not run.
- No tool needs a GPU.

Status key:

- **runs**: exits 0.
- **crash**: exits with an uncaught exception.
- **needs input**: stops cleanly because an argument or a file is missing.
- **verdict**: exits non-zero because of what it found.
- **skipped**: not run.

"Tracked files changed" lists files under git that the run left modified. Those changes were discarded in the copy.

## Results

| Tool | Args | Status | Time | Tracked files changed | Note |
|---|---|---|---|---|---|
| scripts/database/create_db.py | | runs | 1 s | none | builds `data/mythic_patterns.db` (gitignored) |
| scripts/database/query_patterns.py | `--query flood` | runs | <1 s | none | |
| scripts/acquire.py | `status` | runs | <1 s | none | |
| scripts/acquire.py | `next` | runs | <1 s | none | |
| scripts/acquire.py | `fetch …` | skipped | | | network |
| scripts/catalog.py | `report` | runs | <1 s | none | |
| scripts/catalog.py | `status` | needs input | | | needs a text ID and a status. When they are missing it prints `usage: catalog.py status TEXT_ID NEW_STATUS` with an example (exit 2) |
| scripts/add_critical_texts.py | | runs | <1 s | none | all entries already present |
| scripts/add_gap_texts.py | | runs | <1 s | none | all entries already present |
| scripts/add_missing_greek.py | | runs | <1 s | none | all entries already present |
| scripts/add_priority_texts.py | | runs | <1 s | none | |
| scripts/add_regional_texts.py | | runs | <1 s | none | |
| scripts/add_tier2_texts.py | | runs | <1 s | none | |
| scripts/add_tier3_texts.py | | runs | <1 s | none | |
| scripts/add_tier4_texts.py | | runs | <1 s | none | |
| scripts/load_curated.py | | runs | <1 s | sources/discoveries.json | |
| scripts/analyze_gaps.py | | runs | <1 s | none | |
| scripts/audit_archetype_completeness.py | | runs | <1 s | ACP/tools/completeness_audit.json | |
| scripts/audit_reviewer.py | `--status` | runs | <1 s | none | without `--status` it is an interactive review session; not run |
| scripts/conduct_audit.py | | needs input | | | needs `outputs/audits/human_audit_cases.json`, which `validation/v2_run.py` writes. When the file is missing it prints a usage message naming that step (exit 1). After it, the tool runs (exit 0). |
| scripts/diagnose_arc_overlap.py | | runs | 2 s | none | |
| scripts/enrich_from_correspondences.py | `--dry-run` | runs | <1 s | none | |
| scripts/enrich_minor_arcana.py | `--dry-run` | runs | <1 s | none | |
| scripts/enrich_phase2_domains.py | `--dry-run` | runs | <1 s | none | |
| scripts/enrich_phase2_echoes.py | `--dry-run` | runs | <1 s | none | |
| scripts/enrich_phase3_aliases.py | `--dry-run` | runs | <1 s | none | |
| scripts/enrich_phase3_stubs.py | `--dry-run` | runs | <1 s | none | |
| scripts/enrich_priority_systems.py | `--dry-run` | runs | <1 s | none | |
| scripts/fix_remaining_stubs.py | | runs | <1 s | none | dry run unless `--apply` |
| scripts/enrichment_queue.py | | runs | <1 s | ACP/tools/enrichment_queue.json, enrichment_priority.json | |
| scripts/explorer/find_suspects.py | | runs | <1 s | none | |
| scripts/explorer/server.py | | skipped | | | starts a web server |
| scripts/serve_miroglyph.py | | skipped | | | starts a web server |
| scripts/export_explorer_data.py | | runs | 1 s | miroglyph/data/entities_catalog.json, patterns_catalog.json | skips the validation summary when `outputs/metrics/v2_validation_results.json` is absent (warning, not an error) |
| scripts/extract/extract_entities.py | | runs | 60 s | data/entities.json, entity_catalog.json | |
| scripts/generate_guides.py | | runs | <1 s | none | |
| scripts/hygiene/audit_hygiene.py | | runs | <1 s | none | writes `outputs/hygiene_audit.json` |
| scripts/hygiene/fix_broken_targets.py | `--dry-run` | runs | <1 s | none | |
| scripts/hygiene/fix_missing_reverse.py | `--dry-run` | runs | <1 s | none | |
| scripts/hygiene/fix_primordial_ids.py | `--dry-run` | runs | <1 s | none | |
| scripts/hygiene/fix_rel_type_prefix.py | `--dry-run` | runs | <1 s | none | |
| scripts/hygiene/fix_undefined_primordials.py | `--dry-run` | runs | <1 s | none | |
| scripts/integration/setup_integration.py | | runs | <1 s | none | |
| scripts/integration/add_archetypes.py | | runs | <1 s | 3 ACP archetype files | no dry-run flag; rewrites AF_ORISHA, IN_PANTHEON, ME_PANTHEON |
| scripts/integration/run_validation.py | | runs | 89 s | none | writes `outputs/mappings/`, `outputs/metrics/` |
| scripts/motif/build_motif_index.py | | runs | <1 s | none | |
| scripts/motif/tag_motifs.py | | runs | 710 s | data/motif_tags.json, motif_distribution.json | slowest tool |
| scripts/normalize/audit_corpus.py | | runs | <1 s | sources/corpus_audit.json | |
| scripts/normalize/extract_pdf.py | | runs | 71 s | 21 files (sources/, texts/*/normalized/) | `datetime.utcnow()` deprecation warning |
| scripts/normalize/normalize_text.py | | runs | 1 s | 106 files (texts/*/normalized/) | `datetime.utcnow()` deprecation warning |
| scripts/normalize/select_best.py | | runs | <1 s | sources/best_versions.json | |
| scripts/segment/segment_text.py | | runs | 3 s | 96 files (texts/*/segments/) | |
| scripts/validate_enrichment.py | | runs | <1 s | none | |
| scripts/verify/verify_text.py | `texts --detect` | runs | 4 s | none | |
| scripts/bulk_download.py | | skipped | | | network |
| scripts/discover.py | | skipped | | | network |
| scripts/fetch/gutenberg.py | | skipped | | | network |
| scripts/fetch/internet_archive.py | | skipped | | | network |
| integration/node_profiler.py | | runs | 1 s | none | writes `outputs/miroglyph/node_profiles.json` |
| integration/unified_loader.py | | runs | 1 s | none | |
| validation/add_shadow_evolution.py | | runs | <1 s | 10 ACP archetype files | no dry-run flag; adds entries in place |
| validation/fix_polar_coordinates.py | `--dry-run` | runs | <1 s | none | writes a log to `outputs/metrics/` even on a dry run |
| validation/run.py | `--quick` | runs | 84 s | none | |
| validation/v2_run.py | `--quick` | runs | 30 s | none | writes `outputs/audits/`, `outputs/metrics/`, `outputs/reports/` |
| validation/unified_report.py | | runs | <1 s | none | writes `outputs/reports/unified_validation_report.md` |
| validation/v2_tests/miroglyph_structure_v2.py | | runs | 1 s | none | crashed when run by path (`ModuleNotFoundError: No module named 'integration'`); fixed by adding the project root to `sys.path`, as its siblings do. Writes `outputs/validation/miroglyph_structure_v2.json` |
| ACP/tools/validate.js | | verdict | <1 s | none | exits 1 on its own findings (see #11) |
| ACP/calibration/validate.js | | runs | <1 s | none | |
| ACP/tools/derive_coordinates.js | `--all` | runs | <1 s | 20 ACP files | rewrites coordinates in place; with no args it prints usage and exits 1 |
| ACP/launch.sh | | skipped | | | opens a browser and starts a web server |

Other checks:

- `pytest` passes: 69 tests.
- `miroglyph/` has no build step. It is static HTML, CSS and JS that reads `miroglyph/data/`.
- The other modules in `validation/` and `validation/v2_tests/` have no `__main__` block. They run through `validation/run.py` and `validation/v2_run.py`, which both ran.

## Run order

Most tools stand alone once `data/mythic_patterns.db` exists. These are the ordering needs that were found:

1. `python scripts/database/create_db.py` builds the database that the query, integration and validation tools read.
2. `python -m validation.v2_run --quick` (or `--full`) writes `outputs/audits/human_audit_cases.json`. `python scripts/conduct_audit.py` reads that file.
3. `python scripts/export_explorer_data.py` includes the validation summary only when `outputs/metrics/v2_validation_results.json` exists, so run it after step 2.

`catalog.py status` has no order dependency. It needs its two arguments, a text ID from `catalog.py list` and the new status.

## Summary

- 59 run, one of them after a fix (`validation/v2_tests/miroglyph_structure_v2.py`, which crashed when run by path)
- 2 need input: `catalog.py status` and `conduct_audit.py`
- 1 exits on its verdict: `ACP/tools/validate.js`
- 8 skipped

This note records only whether each tool ran. It does not record what the tools reported.
