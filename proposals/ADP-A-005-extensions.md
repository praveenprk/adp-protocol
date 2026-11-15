# ADP-A-005: Where extensions live, and when unknown fields are ignored

| Field       | Value                                  |
|-------------|----------------------------------------|
| **ID**      | ADP-A-005                              |
| **Target**  | ADP-1 (`spec/ADP-1.md`), `schema/`, `conformance/adp-1/` |
| **Resolves**| ADP-D-003, ADP-D-006, ADP-D-007        |
| **Bump**    | Minor: ADP-1 1.0.2 → 1.1.0 (see Version impact, Q5) |
| **Author**  | Contributor (agent-drafted, ADP-0 §8)  |
| **Drafted** | 2026-11-16                             |

---

## Outcome and impact

**In one line:** extensions get one defined home (a `metadata` object
with `x-` keys), and a validator can read envelopes from a newer minor
version without rejecting them, while still catching typos in versions it
knows.

| Area | Effect when applied |
|------|---------------------|
| ADP-1 text | §3.5 defines where extensions live and the exact key format. §4.2 and §5.1 gain an optional `metadata` field. §7.3 says when unknown fields are ignored. V-09 covers every level. New rules V-12, R-10, R-11. |
| Envelopes and validators | Now accepted: `metadata` on the dispatch and report envelopes, and unknown fields in an envelope whose minor version is newer than the validator's. No envelope that passes today fails afterwards. |
| Schemas | Both schemas restructured (C3): one "closed" overlay that applies only to minor versions the schema implements (0 and 1), plus a shared `Metadata` definition. Needs this proposal ACCEPTED (`check-schema-gate`). |
| Conformance | 15 vectors added, 2 changed (C2). No `known_defect` markers: no vector existed for these defects, because ADP-D-003 is an open contradiction (ADP-0 §5.6.3 rule 3). |
| Version | ADP-1 1.0.2 → 1.1.0 (minor: new optional field). |
| Defect register | ADP-D-003, D-006, D-007 → RESOLVED. 13 OPEN → 10 OPEN; no CRITICAL left open. |
| Examples, README | No change. `examples/tier1-design.yaml` already uses work-item `metadata` with valid keys. |
| Out of scope | Whether a validator MUST accept every envelope that passes every rule (ADP-A-001 A5). The schemas enforce §4/§5 field shapes (for example `produce[].path` required) that no table rule names. That is a separate gap; see "Not in this proposal". |

Merging this proposal does not apply it. Application is a separate
change (see Application).

---

## Anchor

Three defects, one root: ADP-1 does not say where an unknown field may
appear, or when a validator must accept one. The schemas answer with
`additionalProperties: false` everywhere, which contradicts the text in
three places.

- **ADP-D-003** (CRITICAL). §7.3: "Parsers MUST accept unknown minor
  versions (ignore unknown optional fields)." V-09: "No unknown top-level
  fields outside schema." A 1.1.0 envelope with a new optional field is
  rejected. The two sentences contradict each other.
- **ADP-D-006** (CRITICAL). §3.5: extensions are carried "on work items,
  envelope, or report". The spec defines `metadata` only on a work item,
  and the schemas reject extensions anywhere else.
- **ADP-D-007** (HIGH). §3.5 gives the format `x-{namespace}-{name}` with
  no character set. The schema allows only `^x-[a-z]+-[a-z0-9-]+$` and
  rejects everything else. That rule has no normative basis.

Evidence at `8d9c9ff` (current `main`):

```
$ grep -n "Extensions are carried\|envelope, or report\|MUST ignore unknown\|V-09\|accept unknown minor\|always ignored" spec/ADP-1.md
121:Extensions are carried as namespaced metadata on work items,
122:envelope, or report. Namespace format: `x-{namespace}-{name}`.
133:Validators MUST ignore unknown `x-` metadata fields.
333:| V-09 | No unknown top-level fields outside schema         |
354:Parsers MUST accept unknown minor versions (ignore unknown
356:Unknown `x-` namespaced metadata fields are always ignored.

$ grep -c '"additionalProperties": false' schema/dispatch.schema.json schema/report.schema.json
schema/dispatch.schema.json:7
schema/report.schema.json:4
```

**A gap the defects do not name.** V-09 says "top-level", but the schemas
also reject unknown fields inside `dispatch`, `context`, read entries,
produce entries and work items. The report has no unknown-field rule at
all, yet its schema rejects them at every level. C1 makes the text match
what the schemas already do (Q3).

---

## Change

### C1: `spec/ADP-1.md`

**C1.1: §3.5** (lines 121–122 and 133). Before:

```
Extensions are carried as namespaced metadata on work items,
envelope, or report. Namespace format: `x-{namespace}-{name}`.
```

```
Validators MUST ignore unknown `x-` metadata fields.
Validators MUST reject unknown keywords.
```

After:

```
Extensions are carried in a `metadata` object on a work item
(§4.3), on the dispatch envelope (§4.2), or on the report envelope
(§5.1). Each key in a `metadata` object has the form
`x-{namespace}-{name}`. `{namespace}` is one or more lowercase
ASCII letters. `{name}` is one or more lowercase ASCII letters,
digits, or hyphens. Values are not constrained.
```

```
Validators MUST ignore every `metadata` entry whose key has this
form, and MUST reject a `metadata` key that does not (V-12, R-11).
Validators MUST reject unknown keywords.
```

The YAML example between them is unchanged.

**C1.2: §4.2.** Append one line to the code block, after
`work_items: [WorkItem]   # directive-bearing work items`:

```
metadata: object         # namespaced extensions (§3.5)
```

with a blank line before it, matching the block's layout.

**C1.3: §5.1.** After the code block that ends with
`items: [ReportItem]`, insert:

````
Optional:

```yaml
metadata: object         # namespaced extensions (§3.5)
```
````

**C1.4: §7.1 and §7.2.** V-09 changes, and three rows are added:

```
| V-09 | No unknown field in any §4 object (§7.3)           |
```

```
| V-12 | Every `metadata` key has the §3.5 form             |
```

(after V-11), and after R-09:

```
| R-10 | No unknown field in any §5 object (§7.3)           |
| R-11 | Every `metadata` key has the §3.5 form             |
```

**C1.5: §7.3** (lines 354–356). Before:

```
Parsers MUST accept unknown minor versions (ignore unknown
optional fields).
Unknown `x-` namespaced metadata fields are always ignored.
```

After:

```
Parsers MUST accept unknown minor versions. When the minor
version in `adp_version` is higher than every minor version the
validator implements, the validator MUST ignore fields it does not
know, at every level, instead of applying V-09 and R-10.
`metadata` entries follow §3.5 in every version.
```

The first line ("Parsers MUST reject unknown major versions.") and the
last ("For ADP-1 the only known major version is 1 …") are unchanged.

**C1.6: version and revision log.** Header Version `1.0.2` → `1.1.0`.
Date becomes the date of application. Append:

```
| <applied>  | 1.1.0. Extensions in `metadata` on work item,  |
|            | dispatch and report (§3.5, §4.2, §5.1); key    |
|            | form defined; unknown fields ignored only for  |
|            | a higher minor (§7.3); V-09 every level; new   |
|            | V-12, R-10, R-11. ADP-A-005, resolves          |
|            | ADP-D-003, ADP-D-006 and ADP-D-007.            |
```

No section is renumbered.

### C2: `conformance/adp-1/`

New vectors use `"since": "1.1.0"` and `adp_version` `1.1.0`, except where
the table says otherwise. Each one is a base vector with one change
(ADP-0 §5.6.3 rule 1).

Changed:

| Vector | Change |
|--------|--------|
| `_valid/pass-dispatch-all-optional.json` | Adds top-level `metadata` `{"x-acme-trace": "t1"}` and work-item `metadata` `{"x-acme-seam": 4}`. `rules` gains `V-12`. |
| `_valid/pass-dispatch-minimal.json`, `_valid/pass-report-complete.json` | `rules` gains `V-12` / `R-10`, `R-11`. |

`V-09` is already in the dispatch `_valid` vectors' `rules`.

Added (15):

| Vector | Input change | Why |
|--------|--------------|-----|
| `V-09/fail-unknown-nested-field.json` | `dispatch.extra` | V-09 covers every §4 object |
| `V-09/fail-unknown-read-entry-field.json` | `context.read[0].extra`, at `1.0.0` | every level, every known minor |
| `V-09/fail-bare-x-key.json` | top-level `x-acme-trace` | an extension outside `metadata` is an unknown field (Q1) |
| `V-09/pass-unknown-fields-higher-minor.json` | `1.2.0`, top-level `priority`, `dispatch.extra` | §7.3: newer minor, unknown fields ignored (ADP-D-003) |
| `V-12/pass-envelope-metadata.json` | top-level `metadata` `{"x-acme-trace": "t1"}` | ADP-D-006 |
| `V-12/fail-uppercase-namespace.json` | work-item `metadata` `{"x-Acme-thing": 1}` | §3.5 form (ADP-D-007) |
| `V-12/fail-no-x-prefix.json` | top-level `metadata` `{"trace": 1}` | §3.5 form |
| `V-12/fail-bad-key-higher-minor.json` | `1.2.0`, top-level `metadata` `{"x-Acme-thing": 1}` | §3.5 holds in every version |
| `R-10/pass-unknown-fields-higher-minor.json` | `1.2.0`, top-level `extra`, `items[0].note` | §7.3 |
| `R-10/fail-unknown-top-level-field.json` | top-level `extra` | R-10 |
| `R-10/fail-unknown-nested-field.json` | `report.extra` | R-10 |
| `R-11/pass-report-metadata.json` | top-level `metadata` `{"x-acme-trace": "t1"}` | ADP-D-006 |
| `R-11/fail-uppercase-namespace.json` | top-level `metadata` `{"x-Acme-thing": 1}` | §3.5 form |
| `V-01/pass-minor-1-with-metadata.json` | `1.1.0` with top-level `metadata` | the version that defines `metadata` validates |
| `V-09/pass-metadata-is-known.json` | `1.0.0` with top-level `metadata` | a 1.1 validator knows `metadata` whatever the declared minor |

After C2 there are 53 vectors. Every rule V-01 to V-12 and R-01 to R-11
has at least one `pass` and one `fail` vector (ADP-0 §5.6.3 rule 4).

### C3: `schema/dispatch.schema.json`, `schema/report.schema.json`

Same change in both files:

1. Remove every `"additionalProperties": false` (7 in dispatch, 4 in
   report). Field shapes, `required`, types, enums and `minItems` are
   unchanged.
2. Add a shared definition, and point every `metadata` at it (top level
   in both files, plus `WorkItem.metadata` in dispatch):

   ```json
   "Metadata": {
     "type": "object",
     "propertyNames": { "pattern": "^x-[a-z]+-[a-z0-9-]+$" },
     "description": "Namespaced extensions (ADP-1 §3.5; V-12, R-11)"
   }
   ```

   The key pattern is the one the dispatch schema already uses, so no
   work-item verdict changes.
3. Add the closed overlay at the root, applied only to minor versions
   this schema implements:

   ```json
   "if": { "properties": { "adp_version": { "pattern": "^1\\.[01]\\." } } },
   "then": { "$ref": "#/$defs/Closed" }
   ```

   `Closed` lists the allowed property names of each object with
   `propertyNames` + `enum`. For dispatch:

   ```json
   "Closed": {
     "$comment": "V-09: unknown fields are rejected when the minor version is one this schema implements (ADP-1 §7.3). Update the if-pattern above when a minor version is added.",
     "propertyNames": { "enum": ["adp_version", "dispatch", "context", "produce", "work_items", "exit", "report", "metadata"] },
     "properties": {
       "dispatch": { "propertyNames": { "enum": ["agent", "anchor", "model", "tier", "gate", "branch"] } },
       "context": {
         "propertyNames": { "enum": ["read", "ignore"] },
         "properties": { "read": { "items": { "propertyNames": { "enum": ["path", "sections"] } } } }
       },
       "produce": { "items": { "propertyNames": { "enum": ["path", "action"] } } },
       "work_items": { "items": { "propertyNames": { "enum": ["keyword", "description", "source", "metadata"] } } }
     }
   }
   ```

   For report: root `["adp_version", "report", "exit_results", "items", "metadata"]`;
   `report` `["agent", "anchor", "status"]`; `exit_results[]`
   `["condition", "result"]`; `items[]` `["key", "value"]`. The `$comment`
   names R-10.
4. The top-level `description` changes from "… per ADP-1 v1.0.0" to
   "… per ADP-1". It has been stale since 1.0.1.

**Drift guard.** The field names appear twice: once in `properties` and
once in `Closed`. A name missing from `Closed` fails
`_valid/pass-dispatch-all-optional.json`, which sets every field. A name
missing from `properties` loses its type check, and the existing
per-field `fail` vectors catch that. No extra CI script is needed.

**Checked while drafting.** A prototype built this way from the current
schemas passes the Draft 2020-12 metaschema. It gives the intended
verdict on all 21 probe inputs. They cover every case in C2, plus
`1.10.0` with an unknown field and an unknown keyword at `1.2.0`. All 38
existing vectors and the 3 examples keep their verdicts.

---

## Version impact

**Minor** (ADP-1 1.0.2 → 1.1.0), ADP-0 §7 "New optional field; validator
relaxation not required by existing text".

- **C1.2 and C1.3** add an optional field (`metadata` on both envelopes).
  §3.5 already allowed extensions there, but named no field, so picking
  one is not an erratum (ADP-0 §6(a) needs unambiguous text).
- **C1.5** resolves the D-003 contradiction. Envelopes at a higher minor
  version now pass where the schemas rejected them. That is a
  relaxation.
- **Nothing tightens.** No envelope that passes the current schemas fails
  after C3. Every new `fail` vector already fails today:
  - C1.1 sets the key format to the dispatch schema's existing pattern;
  - C1.4 makes V-09 cover every level, and R-10 the report, which is
    what the schemas already enforce.

  So no part is "Validator tightening not required by existing text"
  (Major). Q5 asks the maintainer to confirm this reading. An
  implementation that followed the old text literally (top level only)
  would now have to reject more.

---

## Conformance impact

C2 in full. Verdict flips against the published schemas (before →
after):

- `V-09/pass-unknown-fields-higher-minor`,
  `R-10/pass-unknown-fields-higher-minor`: F → T (ADP-D-003).
- `V-12/pass-envelope-metadata`, `R-11/pass-report-metadata`,
  `V-01/pass-minor-1-with-metadata`, `V-09/pass-metadata-is-known`, and
  the changed `_valid/pass-dispatch-all-optional`: F → T (ADP-D-006).
- No T → F flips.

No existing vector's `expect` changes.

---

## Alternatives

| # | Option | Why not |
|---|--------|---------|
| A1 | Allow bare `x-` keys anywhere (`x-acme-trace:` at top level), as well as or instead of `metadata` | Two places for the same thing. It also weakens V-09: `x-` becomes an escape from the unknown-field check at every level. One `metadata` object keeps extensions in one place, as work items already do. |
| A2 | Always ignore unknown fields (drop V-09) | Typos pass silently. A misspelt `ignor:` under `context` would drop an isolation boundary without any error. In an instruction protocol that is a safety failure, not a convenience. |
| A3 | Always reject unknown fields (drop the §7.3 parenthetical) | A 1.0 validator could not read any 1.1 envelope that uses a new field, so a minor bump would break old validators. That defeats SemVer minor (ADP-1 §9). |
| A4 | Relax the schemas to check unknown fields at the top level only, to match V-09's current text | It loosens what the published schemas check today and loses typo detection inside `dispatch`, `context` and work items, for no gain. |
| A5 | Let any `x-` key into `metadata` (no character set) | Then `x-Acme-thing` and `x-acme-thing` are different keys from the same owner, and a namespace is not reliably comparable. The schema's lowercase rule already holds for every published example. |
| A6 | Two complete schemas per kind (strict and lenient) chosen by version | Every field would be defined twice. The overlay repeats only field names, and the vectors catch any drift. |

---

## Not in this proposal

- **The §7 tables do not cover everything the schemas check.** Examples:
  `produce[].path` is required and `action` is an enum, read entries need
  `path`, and `exit_results[]` needs `condition` and `result`. These come
  from the §4/§5 field definitions, and no V- or R- rule names them.
  ADP-A-001 A5 left "MUST accept an envelope that passes every rule" to
  this cluster. Adding it now would make every such schema check
  non-normative. Recommendation: file it as its own defect after this
  proposal is applied.
- **ADP-1 §8** "MUST NOT carry" against "Deduplication is a SHOULD" is
  still unfiled (HIGH). It is unrelated to extensions.

---

## Questions for the maintainer

For Q1 to Q5, the recommendation below was sent to the maintainer in a
working session and matches the drafted default. The maintainer's answers
were given in that session and are quoted as English translations.
These answers shape the draft. They do not accept it. Only the Decision
section below accepts or rejects the proposal (ADP-0 §5.3).

| # | Question | Recommendation (setting and reason) | Maintainer answer | Effect on this draft |
|---|----------|-------------------------------------|-------------------|----------------------|
| Q1 | Where do envelope- and report-level extensions go? | **A top-level `metadata` object on each envelope, as on work items. Bare `x-` keys elsewhere stay unknown fields.** One place for extensions, and V-09 keeps catching typos (A1 rejected). | Accepted the recommendation. Translated: "Go with rec, Q1-Q5 all yes, chosen as sensible defaults and settings." | Settled as drafted. |
| Q2 | When are unknown fields ignored (ADP-D-003)? | **Only when the envelope's minor version is higher than any minor the validator implements. Otherwise they are rejected at every level.** Old validators can read newer minors, and typos in known versions are still caught (A2, A3 rejected). | Accepted the recommendation. Translated: "Go with rec, Q1-Q5 all yes, chosen as sensible defaults and settings." | Settled as drafted. |
| Q3 | V-09 says "top-level", but the schemas check every level, and reports have no rule. Align the text with the schemas? | **Yes: V-09 covers every §4 object, and new R-10 covers every §5 object.** It matches what the published schemas already enforce, so no envelope's verdict changes (A4 rejected). | Accepted the recommendation. Translated: "Go with rec, Q1-Q5 all yes, chosen as sensible defaults and settings." | Settled as drafted. |
| Q4 | What character set do `metadata` keys use (ADP-D-007)? | **The schema's existing pattern `^x-[a-z]+-[a-z0-9-]+$`, with any other key rejected (V-12, R-11).** No verdict changes, and keys stay comparable (A5 rejected). | Accepted the recommendation. Translated: "Go with rec, Q1-Q5 all yes, chosen as sensible defaults and settings." | Settled as drafted. |
| Q5 | Bump class? | **Minor, 1.0.2 → 1.1.0.** It adds a new optional field and one relaxation, and no published-schema verdict tightens. | Accepted the recommendation. Translated: "Go with rec, Q1-Q5 all yes, chosen as sensible defaults and settings." | Settled as drafted. |

---

## Application (if ACCEPTED), per ADP-0 §5.4

1. **SPEC:** C1.
2. **CONFORMANCE:** C2.
3. **SCHEMA:** C3, hand-edited so that the diff shows only the changes
   above (no reformatting).

   Steps 1–3 land in one commit:
   `spec(adp-1): metadata on envelopes and version-gated unknown fields — ADP-A-005, ADP-D-003, ADP-D-006, ADP-D-007`.
   `check_schema.py`, `check_conformance.py` and `check-schema-gate`
   MUST pass on it.
4. **IMPLEMENTATION:** none exists. `check_conformance.py` needs no
   change.
5. **INFORMATIVE:** none. README line 53 ("Extensions via namespaced
   metadata") stays accurate.
6. **REGISTER:** ADP-D-003, ADP-D-006 and ADP-D-007 → RESOLVED,
   `Resolved by: ADP-A-005, <commit>`.

---

## Decision

ACCEPTED 2026-11-16 by the maintainer (ADP-0 §5.3). Apply as written,
with the answers recorded under the questions for the maintainer.
