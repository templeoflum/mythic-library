# ACP data model, as the code reads it

This page describes the Archetypal Coordinate Protocol (ACP) data the way the
code in this repo actually reads it. It does not describe what the data
should be. Where the schema documents and the code differ, the code is
described, and the difference is listed under
[Where the code disagrees](#where-the-code-disagrees).

The counts come from main at 2e33fe2 (22 Oct 2026). They will drift as the
data changes. Re-count them before quoting them anywhere.

The readers covered here:

| Reader | File | Used by |
|---|---|---|
| Loader | `integration/acp_loader.py` (`ACPLoader`) | the integration layer (`unified_loader`, `entity_mapper` and others), v2 validation, the enrichment scripts, the explorer export |
| Validator | `ACP/tools/validate.js` | `node tools/validate.js` from `ACP/`, `scripts/run_checks.sh` |
| Hygiene walker | `scripts/hygiene/acp_entries.py` (`extract_entries`) | `audit_hygiene.py` and the `fix_*` scripts in `scripts/hygiene/` |
| Coordinate deriver | `ACP/tools/derive_coordinates.js` | run by hand on stub files; it rewrites ACP files |

The schema documents are `ACP/schema/UNIVERSAL_ARCHETYPE_SCHEMA.md`,
`relationships.jsonld`, `axes.jsonld`, `primordials.jsonld`,
`dynamics.jsonld`, `correspondences.jsonld` and `ACP_CONTEXT.jsonld`. No code
opens `relationships.jsonld`, `axes.jsonld` or `dynamics.jsonld` by name.
The validator reads them only as ordinary entry files, because it scans
`schema/`. The axis list and the bidirectional list are hardcoded in each
reader.

## Files and how entries are found

There are 94 `.jsonld` files under `ACP/`. Each reader finds entries in its
own way.

| Shape in the file | Loader | Validator | Hygiene walker |
|---|---|---|---|
| Folders scanned | `schema/primordials.jsonld`, then `archetypes/`, `divination/`, `psychology/`, `modern/`, `calibration/` | `schema/`, `calibration/`, `archetypes/`, `divination/`, `psychology/`, `modern/`; skips `legacy` and `node_modules` | all of `ACP/` (`rglob("*.jsonld")`) |
| Extensions | `.jsonld` | `.jsonld` and `.json` | `.jsonld` |
| `entries[]` | yes | yes, no `@id` needed | yes |
| `@graph[]` | only if there is no `entries[]` | only items with both `@id` and `@type` | only if there is no `entries[]` |
| a single entry at the top level (`@id` on the file) | yes | only if it also has `spectralCoordinates` | yes |
| `suits[].cards[]` | only cards with both `@id` and `spectralCoordinates` | yes, no `@id` needed | yes |
| `acts[].stages[]` | only stages with both `@id` and `spectralCoordinates` | yes, no `@id` needed | yes |
| a `suits[]` or `acts[]` group that has its own `@id` | no | no | yes, as an entry |

The validator also reads `expectedInstantiates` and `expectedRelationships`
when `instantiates` and `relationships` are absent. The other readers do not.

None of the scanned folders holds a `.json` file today. The five `.json`
files under `ACP/` are in `tools/` and `.claude/`, which the validator does
not scan. So the extension difference has no effect at present.

The hygiene walker yields 1074 entries, and every `@id` among them is
distinct.

## Entry types

The loader sorts each entry it reads into one of three buckets. The checks
run in this order, and the first match wins:

1. `@type` is `System` or `skos:ConceptScheme` → `systems`
2. `@id` starts with `primordial:` → `primordials`
3. the entry has `spectralCoordinates` → `archetypes`

Anything else is not kept. If the same `@id` appears twice, the last file
read wins.

The validator does not use `@type` to decide what to check. Every entry it
collects with `spectralCoordinates` gets the coordinate checks. Primordials
and calibration points are among them, and so they also take part in the
collision check.

`@type` values across the 1074 walker entries:

| `@type` | Count |
|---|---|
| Archetype | 936 |
| CulturalArchetype | 35 |
| Relationship | 21 |
| NarrativeStage | 18 |
| CalibrationPoint | 17 |
| ContextStub | 12 |
| Axis | 8 |
| skos:ConceptScheme | 5 |
| GeodesicCollection | 4 |
| skos:Collection | 4 |
| (none) | 4 |
| System | 3 |
| Aspect | 2 |
| Epithet, RelationshipMatrix, CalibrationAnalysis, SymbolicSystem, NarrativeSystem | 1 each |

997 of these are archetype-like by the loader's rule: they have coordinates,
are not primordials, and are not `System` or `skos:ConceptScheme`. There are
24 primordials.

## Fields

No reader enforces a required-field list. What each one reads:

| Field | Shape | Read by |
|---|---|---|
| `@id` | string, `prefix:local` | all |
| `@type` | string | loader (bucket rule above), hygiene (missing-instantiates check, `Archetype` only) |
| `name` | string | loader (name index, aliases) |
| `aliases` | list of strings or of `{name, fidelity, ...}` | loader (alias index) |
| `spectralCoordinates` | object, the 8 axis keys → number | all |
| `instantiates` | list of `{primordial, weight, aspects?, note(s)?}` | validator (weights), hygiene (primordial IDs), deriver (`estimatedWeight` or `weight`) |
| `relationships` | list of `{type, target, ...}` | all |
| `description`, `keywords` | string, list | the deriver reads `keywords`; validation tests read `description` |

UNIVERSAL_ARCHETYPE_SCHEMA.md › Validation Rules, rule 6, asks every entry for
a description, coordinates, at least one instantiation and at least one
keyword. No code checks that rule. Hygiene check 6 covers only the
instantiation part, and only for `@type` `Archetype`.

How often each field appears on the 997 archetype-like entries:

| Field | Entries |
|---|---|
| `@id`, `@type`, `name`, `description`, `spectralCoordinates` | 997 |
| `instantiates` | 980 |
| `keywords` | 979 |
| `relationships` | 972 |
| `coreFunction` / `symbolicCore` | 949 |
| `domains` | 935 |
| `culturalEchoes` | 895 |
| `narrativeRoles` | 890 |
| `correspondences` | 882 |
| `psychologicalMapping` | 828 |
| `aliases` | 594 |
| `domain` (singular) | 249 |
| `shadowDynamics` | 235 |
| `systemCode` / `belongsToSystem` | 132 |

Many more fields are specific to one system (tarot, I Ching, runes and the
rest). No shared code reads them.

`instantiates` items come in these shapes: `{aspects, primordial, weight}`
2132, `{primordial, weight}` 26, and with an added `notes` 4 or `note` 2.

## Coordinate axes

The axes come in the same order in the loader, the validator, the deriver and
`fix_polar_coordinates.py`:

| # | Key | Pole at 0 | Pole at 1 |
|---|---|---|---|
| 1 | `order-chaos` | Order | Chaos |
| 2 | `creation-destruction` | Creation | Destruction |
| 3 | `light-shadow` | Light | Shadow |
| 4 | `active-receptive` | Active | Receptive |
| 5 | `individual-collective` | Individual | Collective |
| 6 | `ascent-descent` | Ascent | Descent |
| 7 | `stasis-transformation` | Stasis | Transformation |
| 8 | `voluntary-fated` | Voluntary | Fated |

The pole names come from `negativePoleName` and `positivePoleName` in
`schema/axes.jsonld`. The axis entries there are `axis:<key>`, but
coordinate objects use the bare key, without `axis:`.

How each reader handles the range [0, 1]:

- The validator reports an error for any value outside [0.0, 1.0] or not a
  number. It treats a `null` or missing axis as a placeholder: all eight null
  is a valid stub, and some but not all present is an error ("partial
  coordinates not allowed"). It also checks instantiation weights for [0, 1].
- The loader does no range check. `get_coordinates` fills a missing axis with
  0.5. A `null` value would be passed through as `None`. No such entry exists
  today.
- The deriver clamps each derived value to [0, 1].

No entry today has a null axis, and no value is out of range.

## Relationships

A relationship is `{type, target, ...}` inside an entry's `relationships`
list. The source is the entry that holds it.

The loader's `get_all_relationships(type_filter)` copies each relationship,
adds `source`, and filters on an exact `type` match. Type names are
compared as written, so a `rel:`-prefixed type would not match. No data uses
that prefix today.

Across all 1074 walker entries there are 4100 relationships, under 48 type names. The common ones are:

| Type | Count | Bidirectional in schema | Strength property in schema | What the data carries |
|---|---|---|---|---|
| CULTURAL_ECHO | 2627 | yes | `fidelity` | `fidelity` on 2617, from 0.3 to 0.95 |
| COMPLEMENT | 401 | yes | `polarity` | `strength` on 63, `dynamic` on 65 |
| POLAR_OPPOSITE | 218 | yes, `requiresAxis` | `polarity` | `axis` on 212, written `axis:<key>`; `strength` on 51 |
| TENSION | 120 | yes | — | no strength property |
| CONTAINED_BY | 112 | no, inverse of CONTAINS | `containmentRatio` | |
| EVOLUTION | 107 | no | `transformationDepth` | `trigger` 34, `direction` 33, `source` 29 |
| CONTAINS | 78 | no, inverse of CONTAINED_BY | `containmentRatio` | |
| MIRRORS | 71 | yes | `fidelity` | no `fidelity` on any |
| SHADOW | 58 | no | `activationThreshold` | `activation` on 28, `strength` on 26 |
| DEVOLUTION | 49 | no | `transformationDepth` | |
| ANTAGONIST | 49 | yes | `narrativeIntensity` | `strength` on 17, `dynamic` on 17 |
| PARENT | 28 | not in schema | — | |
| CHILD_OF | 26 | not in schema | — | |

The rest are rare, and many appear once (TWIN, OPPOSITION, MEDIATOR and
others). CONSTELLATION has a `targets` or `members` list in place of a single
`target` on 4 entries, and SYNTHESIS uses `sources`. Most relationships of every type carry a free-text `note`,
`notes` or `description`.

`schema/relationships.jsonld` defines 21 types:

- Bidirectional: POLAR_OPPOSITE, COMPLEMENT, CULTURAL_ECHO, MIRRORS,
  ANTAGONIST, ALLY, TENSION, CONSTELLATION.
- Directed: SHADOW, EVOLUTION, DEVOLUTION, SYNTHESIS, DECOMPOSITION,
  CONTAINS / CONTAINED_BY, PRECEDES / SUCCEEDS, TRANSCENDS,
  INSTANTIATES / EXEMPLIFIES, SUBLIMATION. The slashed pairs are declared
  `inverseOf` each other.

Its `strengthSemantics` names one strength property for each kind:
`polarity`, `fidelity`, `activationThreshold`, `transformationDepth`,
`containmentRatio`, `narrativeIntensity`, `instantiationWeight` and
`sequencePosition`.

Fidelity is read in these places:

- `validation/v2_tests/echo_coherence.py` reads `fidelity` on CULTURAL_ECHO
  and tests it against coordinate distance.
- `validation/v2_tests/relationship_geometry.py` carries it along for
  POLAR_OPPOSITE, COMPLEMENT, SHADOW, EVOLUTION and ANTAGONIST.
- Alias `fidelity` feeds the entity mapper.

The validator never reads `fidelity`.

Of the string targets, 155 do not resolve to any `@id` in the walker's
entries. By prefix: `arch` 103, no prefix 31, `vedic` 9, `persian` 5,
`mesoamerican` 2, and one each of `japanese`, `incan`, `polynesian`,
`roman` and `shadow`. Another 8 targets are not strings.

## ID prefixes

IDs are `prefix:local`. Counts over the walker's entries:

arch 337, tarot 83, iching 72, astrology 34, nakshatra 27, rune 24,
primordial 24, rel 21, tonalpohualli 20, tzolkin 20, ogham 20,
calibration 19, persian 18, journey 18, incan 17, mbti 16, socionics 16,
alchemy 15, bolen 15. Smaller prefixes make up the rest.

Primordial IDs use hyphens (`primordial:great-mother`). Some psychology IDs
use underscores (`jungian:great_mother`). How each reader treats the local
part:

- The loader takes IDs as written.
- Hygiene maps four underscore primordials (`divine_child`, `great_mother`,
  `great_father`, `wise_elder`) to their hyphen forms. It checks primordial
  references against a hardcoded set of 24.
- The deriver goes the other way: it turns every hyphen into an underscore
  and looks the ID up in its own table of 24 underscore-keyed primordial
  coordinates.
- The validator treats a target whose local part contains `_` as a "system
  reference" and does not try to resolve it.

## Where the code disagrees

| Topic | Loader | Validator | Hygiene | Notes |
|---|---|---|---|---|
| Which nested entries count | cards and stages need `@id` and coordinates | cards and stages counted with or without `@id`; `@graph` items need `@id` and `@type` | everything with an `@id`, including `suits`/`acts` groups | The three readers count different totals from the same files. |
| `@graph` together with `entries[]` | `entries[]` only | both | `entries[]` only | |
| Bidirectional types | not used | POLAR_OPPOSITE, COMPLEMENT, TENSION, CULTURAL_ECHO, MIRRORS, TWIN | CULTURAL_ECHO only (check 5 and `fix_missing_reverse`) | The schema's list adds ANTAGONIST, ALLY and CONSTELLATION and has no TWIN. |
| Missing reverse link | — | warning | issue (CULTURAL_ECHO only) | |
| POLAR_OPPOSITE axis | — | `checkPolarOpposites` reads `rel.axis`, but `collectRelationship` never stores `axis`, so the check never fires | — | The data writes `axis:<key>`, but coordinates use the bare key. `relationship_geometry._parse_axis_name` strips the prefix. |
| Primordial instantiation | — | listed as check 5 in the file header; no code implements it | check 6: missing `instantiates`, `@type` `Archetype` only | No reader checks `CulturalArchetype` entries. |
| Unresolved targets | — | warns only for 21 known prefixes; `arch:` is not one of them, and targets with `_` in the local part are skipped | flags any target containing `:` and of at most 5 words | 103 of the 155 unresolved targets are `arch:`, which the validator does not report. |
| Primordial set | whatever `schema/primordials.jsonld` holds | whatever its scan finds | hardcoded 24 | The deriver has its own hardcoded 24, keyed with underscores. |
| Underscore vs hyphen | as written | `_` means "system reference", unchecked | underscore → hyphen for 4 IDs | The deriver converts hyphen → underscore. |
| Missing or null axis | missing becomes 0.5 | all null is a stub; partial is an error | not checked | |
| Weight field | not read | `weight` or `estimatedWeight` | not read | The deriver prefers `estimatedWeight` and defaults to 0.5. |
| Collisions | not checked | distance under 0.05 is an error, including primordials and calibration points | not checked | |
| Fidelity vs distance | — | not checked | — | Schema rule 5. Only `echo_coherence.py` tests it, statistically. |
| MIRRORS fidelity | — | — | — | The schema gives MIRRORS `fidelity`; no MIRRORS relationship in the data carries it. |
| Strength property names | — | — | — | The schema names `polarity`, `activationThreshold` and the rest; apart from `fidelity` on CULTURAL_ECHO and one `sequencePosition` on a PRECEDES, no relationship carries any of them. Some carry a generic `strength` (COMPLEMENT 63, POLAR_OPPOSITE 51, SHADOW 26, ANTAGONIST 17), and SHADOW also uses `activation`. No code reads the schema's names. |
| File extensions | `.jsonld` | `.jsonld` and `.json` | `.jsonld` | No effect today. |
