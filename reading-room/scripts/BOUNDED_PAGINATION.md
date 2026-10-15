# Opt-in bounded prose passages

An audited anchored edition or section may set `pagination: "bounded"`.
`"legacy"` is the default; a section overrides the edition's setting. Existing
edition metadata is never changed automatically. The builder rejects unknown
policies and emits the resolved non-default policy only on opted-in sections.

Bounded mode uses the existing 420-word target and 525-word normal upper budget.
It removes the minimum-fill exception that can join a short paragraph to a large
one, and carries trailing headings with the next prose block when needed to
avoid an oversized group. Long prose is split only at existing sentence
boundaries. Each fragment retains its original paragraph identity and exact
UTF-16 source offsets. No source bytes, chapter boundaries, chapter IDs, bookmark
validation or offset lookup algorithms change.

Source-natural internal heading groups may optionally start new passages without
creating new chapter sections. Set `passageBreakAnchors` on a bounded section to
an ordered list of exact `{ "line": "Original heading", "count": 1,
"occurrence": 0 }` anchors. As with heading anchors, counts are global and
occurrences are zero-based. Each break must also be listed in that section's
`headingAnchors`, lie strictly inside the section, and be unique and in source
order. Missing, ambiguous, out-of-section or unaudited anchors fail the build.
The output uses `passageBreakStarts` in UTF-16 units. Adjacent heading lines stay
together rather than producing an orphaned heading-only page.

This policy does not guarantee a hard bound for arbitrary malformed or indivisible
source content. A single sentence or unaudited verse block may itself exceed the
budget; it is never silently rewritten, truncated or arbitrarily subdivided.
If sentence segmentation is unavailable, source preservation takes precedence.
The independent primary-passage release gate stays at 600 words and must reject
any remaining oversized page. Do not raise that gate to admit a source.

Checks:

```sh
node tests/test_bounded_pagination.cjs
python3 tests/test_bounded_specs.py
node tests/test_bounded_dom.cjs
node tests/test_bounded_preservation.cjs EXACT_APPROVED_27_BASELINE EXACT_ORIGINAL_22_BASELINE
```

Run the complete existing source, interaction and collection suites as well,
then independently check the actual new source contracts. Synthetic and DOM
simulation tests do not establish rendered-browser, mobile or screen-reader QA.
