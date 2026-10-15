# Adding a verified edition

The hosted reader only uses `dist/catalog.json`, `dist/sections.json`, and the
UTF-8 reading files and preserved source assets. Original digital source files and
explicitly labeled derived transcriptions remain distinct. Source verification and
build instructions stay here.

1. Verify the edition's actual title, credited people, completeness, language,
   and rights against its primary-source catalog and the actual text. Preserve
   the entire text file, including every original notice. Do not normalize
   line endings or strip a byte-order mark.
2. Copy only the verified book into `dist/books/`. Add its truthful edition
   details, byte count, and SHA-256 to `dist/catalog.json`. Use a short shelf
   caption and an existing small shelf group where appropriate. `edition_note`
   is for material edition caveats; the reader shows it in the edition panel.
   Use `author_label` for a selector/editor rather than silently calling them an
   author; use `editor` for a separately credited editor. Preserve distinct
   versions and conflicting/missing source attributions in the edition note and
   spec. Do not invent a translator or silently resolve a historical attribution.
3. Add an independently checked entry in `scripts/edition_specs.json` with the
   pinned SHA-256, primary opening, and natural primary section count. For new
   sources, use `builder: "anchored"`, a `defaultSectionId`, and ordered
   `sections`. The first section starts at source offset zero and has no `line`.
   Every later section names an exact complete source `line`, an `id`, `label`,
   and `kind` (`front`, `primary`, or `back`). Set `count` and zero-based
   `occurrence` for repeated headings. Optional `group` preserves a source's
   own grouping in Contents. Optional `headingAnchors` names exact source lines
   whose paragraphs are verified headings, including mixed-case or accented
   titles. Each anchor uses the same `line` / `count` / `occurrence` contract.
   Never store guessed character offsets.
   When the reading text omits material present in the illustrated edition,
   preserve the exact audited HTML/image ZIP in `dist/books/` as well. Record the
   same `preservation_archive` object in the catalog and `preservationArchive` in
   the spec: `path`, `sha256`, `bytes`, `source`, `html_entry`, `html_sha256`.
   The builder checks the archive hash, CRCs and embedded HTML hash. The reader
   links the intact download. Disclose format differences; do not describe a
   plain-text copy as a full illustrated facsimile.
4. Primary sections follow natural source divisions. Front matter, licenses,
   editorial notes, appendices, and indexes remain reachable. Decide whether
   appended source poems are primary or supplementary from the edition itself.
   Confirm the default section's first passage starts the work, not its editor's
   introduction. Short UI labels must not change source text.
5. Generate `dist/sections.json` with `python3 scripts/build_sections.py`.
   Changed hashes, missing/duplicate headings, unexpected section counts, or
   non-contiguous spans fail the build. A changed edition requires new source
   verification; do not update its pinned hash merely to make a check pass.
6. Run all checks below, review the actual first and last passage of each new
   title, and compare existing book manifests with the previous revision.
   Source bytes and existing source-anchored reading places must remain intact.

```sh
node --check dist/app.js
node --check dist/reader-core.js
python3 scripts/build_yoruba.py --check
python3 scripts/build_sections.py --check
node tests/test_core.cjs
node tests/test_interactions.cjs
node tests/test_candidate_preservation.cjs
node tests/test_fourteen_preservation.cjs
node tests/test_fifteen_preservation.cjs
git diff --check
```

The core test reconstructs every original file from section, passage, and block
spans, checks all primary openings, bounded passages, and preserved notices.
The interaction simulation exercises every title's open, continue, return,
supplementary isolation, section crossings, and ending. It is not a browser
render. Keep the native browser-verification limitations explicit in REVIEW.md.

## Explicit verse layout (opt-in)

Unindented verse must be verified against the original edition, not guessed from
short lines. Anchored specs may set `textFormat` to `"verse"`, `"prose"`, or
`"auto"` at edition or section level. A section overrides the edition default;
omission means the existing automatic behavior. Edition defaults apply to every
section, so explicitly override prose front matter and notes. Verified
`headingAnchors` take priority, including within verse sections.

For mixed sections, use `textFormatRanges` on that section. Each entry has a
`format` with the same three values and exact whole-line `start` and `end`
anchors, each written as `{ "line": "Exact source line", "count": 1,
"occurrence": 0 }`. Counts are global within the source, occurrences zero-based.
The end anchor is exclusive; omit `end` only to reach the section end. Ranges
must be ordered, non-overlapping, nonempty, and wholly within that section.
The builder rejects missing/ambiguous anchors and emits UTF-16 offsets after
checking the original byte/hash pin. Never put guessed numeric offsets in a spec.
Range formats override section defaults; an `"auto"` range restores the existing
heuristics. Use range boundaries to isolate verse from captions, prose arguments,
and editorial notes, even when the source omits a separating blank line.

The core preserves every source character and every stanza separator. It keeps
short stanzas intact and splits long explicit verse only after original complete
lines, targeting 420 words and no more than 48 nonempty verse lines per passage.
A single unusually long source line is kept intact even if it exceeds the word
target. Existing automatically classified verse keeps its original behavior.
Continuations retain their original block identity and source offsets; bookmark
validation, navigation, and offset algorithms are unchanged. Existing prose CSS
still reflows wrapped lines; the existing verse class retains line breaks.

Feature checks, in addition to the full-room checks:

```sh
node tests/test_explicit_verse.cjs
python3 tests/test_verse_specs.py
node tests/test_reader_format_dom.cjs
node tests/test_verse_preservation.cjs PINNED_PRE_FEATURE_CHECKOUT
```

The differential test compares every prior block, passage and bookmark endpoint
against the exact pre-feature reader at 180/420/700-word targets, with source and
metadata hashes intact. It does not waive an immutable historical engine pin.
This feature requires a separate exact source review and a freshly captured
approved baseline before the additive edition pipeline can admit new verse
editions. Original fixed-count/hash historical tests remain unchanged; their
intentional pre-feature engine/UI guards cannot directly approve this patch.

Book data is loaded as bytes and decoded with `ignoreBOM: true`: this preserves
an original UTF-8 byte-order mark rather than silently removing it. Source
hashes are checked against those original bytes before rendering.

Use the existing owner-private Site identity and the supported publication
workflow. Do not publish until the parent has reviewed this batch.

## Individual source attribution

New anchored specs may set `readerAttribution` on one section. Supply a clear
`display`, exact `sourceEvidence` contained in that section, people/language/place
labels as printed, and the verification limit. The generator checks that exact
evidence within that section and emits `sourceAttribution` for reader context.
This is distinct from older audit-only `sourceAttribution` fields, which remain
unchanged. Never infer individual tale attribution from a collection-level shelf.

A descriptive catalog `title` may be paired with `bibliographic_title` and
`display_title_note`; the reader must show the distinction. `illustrator` is a
separate credit. `qualification_notes` preserves further source-specific caveats
in edition details. None of these fields rewrites the source text.

## Ikom 1913 edition

The fourteen-edition candidate adds only Project Gutenberg 70959. The 33 numbered
stories and unnumbered Latin tale are 34 primary sections. Original narrator
credits and the attached editorial notes remain in source order within their tales.
Every tale has exact readerAttribution evidence; tale VII explicitly discloses
uncertain local provenance. The Latin tale has no invented English translation.
The preface, plates/captions, printer colophon, eleven footnotes, transcriber notes
and Gutenberg license are separately reachable supplementary sections. The complete
illustrated ZIP includes both full-size plate images linked through a href.

The thirteen-edition preservation suite compares every old catalog record except
two approved shelf labels, every prior source spec/section record, 25 core/source
asset hashes and 1,064 bookmark endpoints. Yoruba Legends was absent from that historical fourteen-edition baseline. The
separate derived addition below does not alter any of those fourteen records.

## Yoruba Legends: derived scan-collated transcription

The fifteen-edition candidate adds all forty printed narratives from the 1929
Sheldon Press edition, credited only as printed to M. I. Ogumefu, B.A. It uses the
pinned repaired JSON collation, not raw OCR. The two input fixtures are retained
unchanged outside dist; the raw OCR and broader source audit remain separate.

Run `python3 scripts/build_yoruba.py` before `build_sections.py` to regenerate the
derived UTF-8 reading asset and its test audit. Both repair inputs and the
unchanged 98-page PDF have independent SHA-256 and byte-count pins in that builder.
`--check` validates them and the exact generated bytes without writing files.
The catalog and edition spec pin the final derived file and the preserved PDF.
Core/source tests also verify the PDF signature, byte count and SHA-256.

The derived TXT explicitly says it is scan-collated and has four unresolved
readings. It is never described as an original clean TXT. The original source
scan has its own open link and download link. The old fourteen editions retain
their original source/download labels. The total shelf count says reading editions.

Narrative I opens by default. Eight supplementary sections retain title/credit,
dedication/publication, the complete four-paragraph preface, original contents,
the separate Stories of Tortoise divider, source qualifications, normalization
policy, and the exact four uncertainty contexts. The original contents/body
variants in IX and XX remain distinct. Embedded verse retains its original text
and line breaks, with four spaces of rendering indentation per line so the
unchanged pagination core recognizes verse. Source underbars are not modernized.

Four literal narrative uncertainty markers remain, plus four repeated excerpts
in the supplementary register. In this derived edition only, safe text/mark DOM
nodes highlight the markers without changing textContent or source offsets.
No source string is interpreted as HTML. The marker CSS has light/night styles.

Preservation tests compare all fourteen old catalog records, source specs and
complete section records, 21 source/notices/archive assets, all 1,340 section
bookmark endpoints (including 1,132 primary endpoints), and unchanged navigation,
storage and core behavior. The only historical UI hash exceptions are explicit
exact before/after transforms for five JavaScript hunks and one CSS addition;
all source/core identity checks remain active. Older eleven/thirteen preservation
suites retain their historical shelf and exclusion assertions, alongside the
new edition. No old catalog record or old source specification is edited.

This is an isolated local candidate, not a deployment or a rights/quarantine
change. Native rendered-browser behavior has not been verified here.
