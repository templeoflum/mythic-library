# Reusable additive edition pipeline

Offline, source-only maintenance tools for adding complete, source-verified
reading editions. They reuse a reading room's existing section builder, reader
core, and reader tests rather than copying or replacing their implementation.
Python 3.10 or newer and Node.js are required by the current reader and tools.
The pipeline itself uses only standard-library modules.

## Exact support-package contents

Keep exactly these four files under `maintenance/edition-pipeline/` in the
source repository:

- `edition_pipeline.py`: baseline capture, isolated preparation, and validation
- `test_negative_gates.py`: portable positive-control and negative-gate checks
- `test_source_scan_pins.py`: focused source-scan hash and byte-count regressions
- `README.md`: this operating guide and file allowlist

No edition fixtures, import manifests, baselines, audit evidence, source books,
archives, test outputs, credentials, or machine-specific input locations belong
in this support package. The directory is source-only and must not be copied into
`dist/` or included in the hosted-file allowlist. Source persistence and deployment
are separate operations. These tools do not perform either operation.

The pipeline snapshots `maintenance/` along with `dist/`, `scripts/`, `tests/`,
`.openai/`, and an existing `.gitignore`. Future preparation carries the same
maintenance files forward and validates their original pins. Previously captured
baselines remain governed by their original exact file lists. Adding maintenance
to an existing source repository is a separately reviewed source-only change.

## Safety boundary

The tools contain no network, credential, Git-write, sharing, publication, or
deployment operations. Baseline capture may read local Git status and commit ID.
Successful gate results always say `review_required: true` and
`publication_allowed: false`. A passing result is evidence for a separate review,
not authority to publish. All executed reader/build/test scripts must come from a
trusted, reviewed baseline; this wrapper is not a sandbox for arbitrary scripts.

## Four stages

1. **Source audit:** obtain exact primary-host files and verify title, creator
   roles, print/digital edition, natural contents/body divisions, source
   differences, and a bounded rights basis. Retain original bytes and the
   illustrated bundle when needed. Hash checks do not replace this judgment.
2. **Baseline:** capture the approved room's catalog, source specifications,
   navigation records, and exact protected-file hashes. A Git-backed baseline
   must be clean. Local commit information is recorded without changing Git.
3. **Prepare:** verify the audit and pinned assets, copy the baseline into a new
   empty candidate, append the approved catalog/spec entry, and copy source assets
   without normalization. Reuse the existing section builder.
4. **Gate and review:** preserve old records, bookmarks, and protected files;
   enforce an exact hosted-file allowlist; run full-room reader checks; and emit
   exact proposed source-transfer hashes for review.

## Commands

Run from the repository root. Example paths are placeholders; place audit inputs
and results outside the maintenance package and outside hosted `dist/`.

```sh
python3 maintenance/edition-pipeline/edition_pipeline.py baseline \
  --root APPROVED_ROOM --output BASELINE_JSON

python3 maintenance/edition-pipeline/edition_pipeline.py prepare \
  --base-root APPROVED_ROOM --baseline BASELINE_JSON \
  --import-json VERIFIED_IMPORT_JSON --candidate NEW_EMPTY_CANDIDATE \
  --output REVIEW_MANIFEST_JSON

python3 maintenance/edition-pipeline/edition_pipeline.py validate \
  --root CANDIDATE --baseline BASELINE_JSON \
  --import-json VERIFIED_IMPORT_JSON --output REVIEW_MANIFEST_JSON

python3 maintenance/edition-pipeline/test_negative_gates.py \
  --candidate CANDIDATE --baseline BASELINE_JSON \
  --import-json VERIFIED_IMPORT_JSON --output NEGATIVE_RESULTS_JSON

python3 maintenance/edition-pipeline/test_source_scan_pins.py
```

The focused source-scan suite runs six regressions with synthetic fixtures and
needs no edition assets or candidate arguments.

`validate` and the negative suite accept repeated `--import-json` arguments for
an already-prepared additive batch, in new-catalog order. `prepare` intentionally
handles one new edition per run. A failed source must not inflate the shelf count.
The pipeline's `--fast` validation skips full reader suites, but still verifies
files, original metadata/bookmarks, and section rebuilding. It is suitable for
negative-gate testing, not release readiness.

`import-baseline --records RECORDS_JSON --files PINS_JSON --output BASELINE_JSON`
converts the earlier independently pinned record/hash format. It does not create
a historical fixed-title-count projection.

## Portable negative tests

All four input/output flags are required. The suite first runs full validation on
a clean isolated copy. An invalid starting candidate blocks the suite rather than
making every negative case appear to pass. Each mutation then gets its own fresh
copy. A case passes only for `GateError` at its expected diagnostic; unrelated
exceptions and acceptance of the defect are failures.

The thirteen cases exercise prior source corruption, prior metadata changes, old
bookmark drift, UI edits, unexpected hosted files, new-source corruption,
unavailable stubs, incorrect primary-section counts, traversal, missing source
anchors, private audit-path leaks in catalog and reader attribution, and executable
source assets. Selections come
from supplied manifests. Byte mutation always changes the pin; no story word,
book ID, title count, or edition-specific section index is assumed.

The output records a full positive control, each negative result, and whether the
candidate's protected files and external input files remained unchanged. A case
without an applicable fixture, such as old-book preservation for an empty
baseline, is explicitly marked `not_applicable`; it is never counted as rejected.
`complete_negative_coverage` is false when any case is inapplicable. A successful
exit means all applicable cases were rejected and all checked inputs were
unchanged; require complete coverage for a regression claim covering all cases.

Temporary copies use the system temporary directory and are removed after each
check. Set the standard `TMPDIR` environment variable if a particular local
scratch area is needed. Test output must be outside the supplied candidate and
must not overwrite the baseline, imports, source files, or verification reports.
The suite copies only the approved reader/check trees and maintenance directory,
not Git history or private audit trees. Reports and retained sources remain
separate, explicit read-only inputs.

## Import contract

An import JSON has this structure. The abbreviated catalog and spec are
explanatory, not runnable:

```json
{
  "schema_version": 1,
  "catalog": {"id": "new-edition", "path": "books/new-edition.txt"},
  "spec": {"builder": "anchored", "sections": []},
  "runtime_assets": [
    {
      "source": "ABSOLUTE_RETAINED_SOURCE_PATH",
      "target": "books/new-edition.txt",
      "bytes": 123,
      "sha256": "EXACT_SOURCE_SHA256",
      "url": "https://primary-source.example/original.txt"
    }
  ],
  "verification": {
    "status": "verified_complete_digital_edition",
    "source_catalog": "https://primary-source.example/catalog",
    "rights_scope": "USA_only",
    "report": "ABSOLUTE_AUDIT_REPORT_PATH",
    "limits": ["Edition-specific qualifications"]
  }
}
```

Supply complete reader records, exact source pins, and whole-line anchors.
Required catalog fields include edition and creator/rights attribution, source
URL, reading-source path/bytes/hash, shelf, and `available: true`. The anchored
specification must provide matching source hash, primary-opening anchor,
primary-section count, default primary section ID, and complete ordered sections.
Source verification must be complete and use `USA_only` or `explicit_license`
rights scope. This is a technical gate, not an independent legal determination.

The source report must exist; its hash appears in the review manifest. Every
runtime asset must correspond exactly to a catalog reading source, notices, scan,
or preservation archive. The archive and its HTML are independently checked.
Executable assets, traversal, duplicate/overwriting targets, unavailable stubs,
and private audit paths in catalog or specification metadata are rejected.
The specification scan includes reader attribution that becomes hosted section
metadata.

Keep the report, catalog/spec, and asset values aligned. Never update pins merely
to suppress a mismatch; re-verify the source independently. A passage/structure
test does not establish legal clearance or print-scan fidelity.

## Dynamic preservation contract

- Prior catalog records, order, shelves, specifications, and section records
  remain deeply equal. No fixed edition count is built into the gates.
- Every protected prior source, notice, archive, PDF, UI file, builder, test,
  and maintenance file keeps its original hash.
- Only catalog JSON, sections JSON, edition specs, and explicitly declared new
  source assets appear in the proposed additive release-transfer manifest.
- Hosted filenames equal the original runtime set plus exactly the new assets.
- Existing reader code validates both endpoints of every prior section bookmark.
- Full-room source/pagination and interaction tests check byte reconstruction,
  story-first starts, bounded passages, paragraph continuity, source pins, and
  supplementary-bookmark isolation using the room's existing checks.
- UI changes and deliberate revisions to old editions require a separate reviewed
  change path. This additive tool rejects them.

## Moving between environments

Transfer this four-file support directory separately from retained source bytes,
audit reports, and edition-specific JSON inputs. Materialize every referenced
source/report file and update only its location field in the import when moving
environments, preserving all byte/hash pins and provenance. Re-run validation;
never assume a former staging location still exists. Historical baseline
`root_hint` is descriptive, not a requirement to recreate an old absolute path.

Keep reports out of hosted assets and out of this support package: they can
contain local audit locations and diagnostic details. Source-specific audits may
need additional dependencies, which their separate procedures must identify.
Browser/mobile rendering remains separate verification and is never inferred
from DOM simulations or a passing offline suite. Persisting these four files
neither publishes a new edition nor changes access to the reading room.


## Private source persistence

The portable three-file support package is committed under `maintenance/edition-pipeline/` in the private Site source at `86512d24179b588d290b75b9d981b03a17924731`, with narrow `.gitignore` exceptions as the fourth source-only change. Remote fetched file bytes were verified. Live version 9 remains the five-file Lilac release; support persistence did not deploy. Both portable full positive controls and 13 negative cases per candidate pass; future baseline/prepare carries maintenance files and rejects corruption. Receipt: `../mythic-library-publication-ledger/toolkit-source-support-receipt.json`.


## Collected-catalog batches

The batch-aware procedure accepts repeated `--import-json` arguments on both
`prepare` and `validate`. It copies the baseline once, adds all verified sources,
and runs section generation once. Each addition to a room with `collections.json`
must carry a top-level `collection_entry_id` pointing to exactly one existing,
non-readable catalog card. Admission promotes that card; it never creates a new
card or silently assigns two editions to one card. Prior original IDs, titles,
traditions, held-file and quarantine provenance remain unchanged. Reader title,
author, edition, exact source URL and concise edition qualification are copied
from the reviewed import; aliases retain the previous title. Status totals are
recomputed from entries. All unrelated collection fields and cards are exact.

Capture a fresh baseline with this version before the first batch: older
snapshots did not capture the collected catalog's records. The existing 13
negative regressions remain, with five new collection-specific rejection cases.
The latter report NotApplicable for historical baselines without this feature;
duplicate-card rejection requires a multi-edition candidate. Inputs and sources
remain read-only. Publication remains separate and review-gated.

Collection DOM behavior tests now run as part of full additive validation.
These tests must be the portable source-only version (no untracked historical
baseline fixture). Standalone behavior tests verify current reader hashes and
actual runtime behavior; the additive gate independently enforces the exact
baseline and allowed mapped collection promotions. Any test/tool maintenance
change must be separately pinned and reviewed before defining the supported
baseline used for book admission.
