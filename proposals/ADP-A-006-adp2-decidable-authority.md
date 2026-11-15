# ADP-A-006: Make ADP-2 authority checks decidable

| Field       | Value                                  |
|-------------|----------------------------------------|
| **ID**      | ADP-A-006                              |
| **Target**  | ADP-2 (`spec/ADP-2.md`), `schema/`, `conformance/adp-2/`, `scripts/ci/check_conformance.py` |
| **Resolves**| ADP-D-018, ADP-D-019, ADP-D-020, ADP-D-021, ADP-D-022 |
| **Bump**    | Major: ADP-2 1.0.0 → 2.0.0 (see Version impact, Q6) |
| **Author**  | Contributor (agent-drafted, ADP-0 §8)  |
| **Drafted** | 2026-11-16                             |

---

## Outcome and impact

**In one line:** after this, two independent ADP-2 validators give the same
answer on the same grant and dispatch, because every check is defined
exactly. Anything a validator cannot see is named as the runtime's job.

| Area | Effect when applied |
|------|---------------------|
| ADP-2 text | Grant ids, paths and globs, and glob "overlap" get exact definitions. The codebase event record gets a document format and its own pure check. `AT-VERIFY` and codebase events are no longer inferred from a dispatch. New rule G-10 (grant document well-formed). |
| Validators | Two pure functions: `validate(dispatch, grant_chain)` for G-1 to G-7 and G-10, and `validate_record(record)` for G-9. Both are fully decidable from their inputs. |
| Safety | A path with a `..` or `.` segment, or a leading `/`, matches no glob. `src/../scripts/hooks/pre-push` cannot pass as `src/**`. Overlap is checked conservatively, so a write scope that might touch a protected path is always rejected. |
| Schemas | `grant.schema.json`: version grammar and UTC expiry. New `record.schema.json`, which checks G-9 completely. |
| CI | `check_conformance.py` checks ADP-2 grant and record vectors against their schemas. These are the first ADP-2 verdicts CI verifies. |
| Version | ADP-2 1.0.0 → 2.0.0, because one schema change tightens a published verdict (Q6). |
| Defect register | D-018 to D-022 → RESOLVED. 18 OPEN → 13 OPEN. |
| Not changed | ADP-1, and G-2, G-5, G-6, G-8. |

Merging this proposal does not apply it. Application is a separate
change (see Application).

---

## Anchor

All five defects come from one root: ADP-2 states checks that a pure
validator cannot decide from its inputs. They were filed while applying
ADP-A-002 (PR #18, `b1ea4fa`).

| Defect | Gap | Fixed by |
|--------|-----|----------|
| ADP-D-018 | G-9 must be checked, but the record is not a validator input and has no format | C1.4, C1.6, C1.7 |
| ADP-D-019 | Glob dialect and glob "overlap" undefined | C1.3 |
| ADP-D-020 | How a grant id is told apart in `dispatch.anchor` | C1.2 |
| ADP-D-021 | `AT-VERIFY` depends on facts outside the envelope | C1.1 |
| ADP-D-022 | Required grant fields, version grammar, unknown fields undefined | C1.2, C1.5 |

Evidence: the entries in `DEFECTS.md` at `c4a4d65` (current `main`),
each with line-numbered `grep` output.

**A related gap found while drafting, in the same root.** §3 says a
`create` at the root of a new codebase implies `AT-CODEBASE-CREATE`.
G-2 forbids any grant from listing that type, so under G-3 such a dispatch
could never pass. A validator also cannot tell from a dispatch that a
codebase is new. C1.1 removes the inference: codebase events are
authorised by records (G-9) and enforced by the runtime.

---

## Change

### C1: `spec/ADP-2.md`

**C1.1: §3 Keyword mapping.** Four rows change. The rest of the table and
the `SOURCE` note are unchanged.

Before:

```
| `CONFIRM` | `AT-READ`; also `AT-VERIFY` if checking the condition requires running anything | Asserts. Never writes. |
| `PRODUCE`, `produce[]` | `AT-WRITE` | Each `path` MUST match `scope.write`. A `create` at the root of a new codebase implies `AT-CODEBASE-CREATE` instead. |
| `EXIT`, `exit[]` | `AT-REPORT`; also `AT-VERIFY` if checking the condition requires running anything | |
| *(no element)* | `AT-VCS`, `AT-TOOL` | Cannot be inferred from an ADP-1 envelope. Declared in the grant and enforced by the runtime (§6). |
| *(no element)* | `AT-CODEBASE-DELETE` | ADP-1 has no delete action. A codebase delete cannot be dispatched under ADP-1. |
```

After:

```
| `CONFIRM` | `AT-READ` | Asserts. Never writes. |
| `PRODUCE`, `produce[]` | `AT-WRITE` | Each `path` MUST match `scope.write` (§4.2). |
| `EXIT`, `exit[]` | `AT-REPORT` | |
| *(no element)* | `AT-VERIFY`, `AT-VCS`, `AT-TOOL` | Cannot be inferred from an ADP-1 envelope: whether a condition needs anything run is not visible in it. Declared in the grant and enforced by the runtime (§6). |
| *(no element)* | `AT-CODEBASE-CREATE`, `AT-CODEBASE-DELETE` | Never inferred from a dispatch. A codebase event is authorised only by a record (§4.3, G-9) and enforced by the runtime (§6). |
```

**C1.2: §4 Grant document.** In the YAML block,
`adp_grant_version: "1.0.0"` becomes `adp_grant_version: "2.0.0"`. Append
after the block:

```
`adp_grant_version` is the ADP-2 version the grant follows, written as
a SemVer 2.0.0 version.

Every field shown is REQUIRED, with these exceptions:

- `root` and `parent`: at least one is present;
- each key under `scope`: an absent list grants nothing.

`expires_at` is an RFC 3339 date-time in UTC, ending in `Z`. Unknown
fields are ignored. Every field that limits authority is required, so
a misspelt field fails closed.
```

§4.1, append:

```
An entry of `dispatch.anchor` is a grant id when it equals the `id` of a
grant in the grant chain given to the validator (§6). Every other entry
is an ordinary reference.
```

**C1.3: new §4.2 Paths and globs** (after §4.1):

```
### 4.2 Paths and globs

A path is relative, uses `/` between segments, and is compared byte for
byte. A path with a leading `/`, an empty segment, or a `.` or `..`
segment matches no glob.

A glob is a path whose segments may contain `*`, which matches any run
of characters within one segment, including none. A segment that is
exactly `**` matches zero or more whole segments. No other character is
special. `scope.read`, `scope.write`, `scope.branches` and `protected`
are lists of globs. A path matches a list when it matches any glob in it.

Two globs overlap when one's literal prefix equals the other's or is a
leading run of segments of it. A literal prefix is the run of segments
before the first segment that contains `*`. Two lists overlap when any
pair of their globs overlaps. This test may report an overlap where no
single path matches both globs. It never misses one.
```

**C1.4: new §4.3 Codebase event record** (after §4.2):

````
### 4.3 Codebase event record

```yaml
adp_record_version: "2.0.0"
record:
  id: string              # unique, never reused
  classes: [string]       # event classes (§2.1), at least one
  boundary:
    sandbox_roots: [string]
    namespaces: [string]
    codebases: [string]
    max_events: integer   # optional, at least 1
  span: string            # "event" | "session" | "cycle"
  signed_by: string
  signature: string
```

Every field is REQUIRED except `max_events`, and except the three
`boundary` lists, of which at least one is present.
`adp_record_version` follows the rule for `adp_grant_version` (§4).
A record is not a grant and never appears in a grant chain.
````

**C1.5: §5 Invariants.**

- G-1: "exactly one grant id" → "exactly one grant id (§4.1)".
- G-4: append "Matching follows §4.2."
- G-7: first sentence → "`scope.write` MUST NOT overlap `protected`
  (§4.2)." The rest of G-7 is unchanged.
- G-9: "The record MUST state:" → "The record (§4.3) MUST state:".
- Append after G-9:

  ```
  - **G-10** A grant MUST follow §4: every required field present,
    `expires_at` in UTC, and `adp_grant_version` a SemVer 2.0.0 version
    whose major version the validator implements.
  ```

**C1.6: §6 Validation and enforcement.** Replace the Validator bullet:

```
- **Validators.** Two pure functions, like ADP-1 §7:
  - `validate(dispatch, grant_chain)` checks G-1 to G-7 and G-10.
    `grant_chain` is the grant the dispatch lists and its ancestors.
  - `validate_record(record)` checks G-9 and the record format (§4.3).

  Each checks that signature fields are present and non-empty. A
  signature is verified only when the caller supplies the key.
```

Runtime bullet: "`AT-VCS`, `AT-TOOL`, G-8," → "`AT-VERIFY`, `AT-VCS`,
`AT-TOOL`, codebase events against their records (G-9), the coverage
clause of G-7, G-8,". The rest is unchanged.

**C1.7: header and Revision Log.** Version `1.0.0` → `2.0.0`. Date
becomes the date of application. Append:

```
| <applied>  | 2.0.0. Grant id, paths, globs and overlap       |
|            | defined (§4.1, §4.2); codebase event record and |
|            | validate_record (§4.3, §6); AT-VERIFY and       |
|            | codebase events not inferred (§3); G-10.        |
|            | ADP-A-006, resolves ADP-D-018 to ADP-D-022.     |
```

### C2: `conformance/adp-2/`

Changed, all 18 existing vectors:

- every grant's `adp_grant_version` becomes `"2.0.0"`;
- every G-9 input becomes a full record document (§4.3) with
  `adp_record_version` and `id`, keeping its classes, boundary and span;
- every `target.since` becomes `"2.0.0"`.

No existing verdict changes.

Added (15). New kinds: `grant`, whose input is one grant document, and
`record`, whose input is one record document. `codebase-record` is renamed
to `record`.

| Vector | Kind | Input | Expect |
|--------|------|-------|--------|
| `G-1/pass-other-anchor-entries` | authority | anchor `[SPEC-001, CHG-4821, grant-1]` | pass |
| `G-1/fail-grant-not-in-chain` | authority | anchor `[SPEC-001, grant-7]`, chain holds only `grant-1` | fail |
| `G-3/pass-exit-without-verify` | authority | grant types `[AT-READ, AT-WRITE]`, dispatch has `exit` | pass |
| `G-4/pass-single-star` | authority | write `[src/*.py]`, produce `src/a.py` | pass |
| `G-4/fail-star-crosses-slash` | authority | write `[src/*]`, produce `src/fees/a.py` | fail |
| `G-4/fail-dot-dot-segment` | authority | produce `src/../scripts/hooks/pre-push` | fail |
| `G-7/fail-literal-in-protected` | authority | write `[src/**, scripts/hooks/pre-push]` | fail |
| `G-10/pass-unknown-field` | grant | grant with an extra `note` field | pass |
| `G-10/pass-later-minor` | grant | `adp_grant_version` `2.4.0` | pass |
| `G-10/fail-missing-protected` | grant | no `protected` | fail |
| `G-10/fail-expiry-not-utc` | grant | `expires_at` `2026-11-16T23:00:00+05:30` | fail |
| `G-10/fail-unknown-major` | grant | `adp_grant_version` `3.0.0` | fail |
| `G-9/pass-scratch-cycle` | record | `CREATE-SCRATCH`, span `cycle`, sandbox root | pass |
| `G-9/fail-event-namespace-only` | record | `ARCHIVE`, span `event`, boundary has only `namespaces` | fail |
| `G-9/fail-empty-boundary` | record | `boundary` `{}` | fail |

After C2 there are 33 ADP-2 vectors. Every rule G-1 to G-7, G-9 and G-10
has at least one `pass` and one `fail` vector.

### C3: `schema/`

- **`grant.schema.json`:**
  - `adp_grant_version` gets the ADP-1 version pattern with major `2`
    instead of `1`;
  - `expires_at` gets the pattern
    `^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?Z(?![\s\S])`;
  - nothing else changes. Unknown fields stay allowed, as C1.2 states.
- **New `record.schema.json`:** §4.3 as JSON Schema, plus G-9 in full:
  - `if` the classes include an R3 class, `span` is `event`;
  - `if` they include an R2 class, `span` is `event` or `session`;
  - `if` `span` is `event`, `boundary` holds exactly one codebase and no
    other list.

Checked while drafting: prototypes of both schemas pass the Draft 2020-12
metaschema. They give the intended verdict on 18 probe inputs, covering
every grant and record case in C2.

### C4: `scripts/ci/check_conformance.py`

`SCHEMAS` gains:

```python
"ADP-2": {"grant": "schema/grant.schema.json",
          "record": "schema/record.schema.json"},
```

Vectors of kind `authority` relate a dispatch to a chain of grants, which
no schema can check. They stay shape-checked only, as today.

---

## Version impact

**Major** (ADP-2 1.0.0 → 2.0.0), ADP-0 §7 "Validator tightening not
required by existing text". This applies to one change: `adp_grant_version`
gets a grammar. Today `grant.schema.json` accepts any non-empty string
there, and ADP-2 never said the field is SemVer.

The other changes are not Major:

- **The UTC pattern** is an erratum, ADP-0 §6(a). §4 already says
  "RFC 3339 UTC".
- **Dropping the `AT-VERIFY` and codebase-event inferences** is a
  relaxation.
- **The other new definitions** (grant id, globs, overlap, the record
  format) change no published verdict, because no published artifact
  could check them before.

ADP-0 §7 has no exemption for Draft documents. ADP-2 was published a day
before this draft and has no implementation, so the bump costs only a
number. Q6 offers the Minor alternative and what it gives up.

---

## Conformance impact

C2 in full. Against the published `grant.schema.json`, verdict flips
(before → after):

- `G-10/fail-expiry-not-utc`: T → F (erratum);
- `G-10/fail-unknown-major`: T → F;
- every existing grant at `"1.0.0"` would flip T → F, which is why C2
  moves them to `"2.0.0"`.

`record.schema.json` is new, so nothing flips there. No authority-kind
verdict changes against the ADP-2 text, except the two the text change
makes: `G-3/pass-exit-without-verify` and `G-1/pass-other-anchor-entries`
were undecidable before and pass now.

---

## Alternatives

| # | Option | Why not |
|---|--------|---------|
| A1 | Pass records into `validate(dispatch, grant_chain, records)` and link them through `dispatch.anchor` | The validator still cannot tell from a dispatch that a codebase event happens, so the link would be unchecked. A record is valid or not on its own, so `validate_record` is the honest boundary. |
| A2 | Adopt an existing glob dialect (POSIX `fnmatch`, gitignore, git wildmatch) by reference | POSIX `fnmatch` has no `**`. gitignore and wildmatch differ in details (leading `/`, trailing `/`, negation) and have no stable standard text. Two paragraphs of our own leave nothing to interpretation. |
| A3 | Exact glob intersection for G-7 | Decidable, but it needs an automaton product in every implementation. The prefix test is a few lines, never misses an overlap, and errs toward rejecting the grant, which is the safe side for a guardrail. |
| A4 | Recognise grant ids by a syntax (e.g. a `grant:` prefix) | It needs a naming convention that ADP-1 `anchor` values do not have, and the chain is already in hand. Membership needs no convention. |
| A5 | Keep `AT-VERIFY` inferred, and let the dispatch declare which conditions run code | It adds a field to every EXIT or CONFIRM for a check the runtime must make anyway. |
| A6 | Reject unknown grant fields | It is not needed for safety: every authority-limiting field is required, so a typo fails closed. It would also tighten another published verdict. |
| A7 | Leave the version grammar out, which keeps the bump Minor | `adp_grant_version` would stay a free string, and no validator could reject an unknown major (the ADP-D-004 problem, in ADP-2). D-022 would stay partly open. See Q6. |

---

## Questions for the maintainer

For Q1 to Q6, the recommendation below was sent to the maintainer in a
working session and matches the drafted default. The maintainer's answers
were given in that session and are quoted as English translations.
These answers shape the draft. They do not accept it. Only the Decision
section below accepts or rejects the proposal (ADP-0 §5.3).

| # | Question | Recommendation (setting and reason) | Maintainer answer | Effect on this draft |
|---|----------|-------------------------------------|-------------------|----------------------|
| Q1 | How is the codebase event record checked (ADP-D-018)? | **As its own document (§4.3), by a separate pure function `validate_record(record)`. The runtime matches events to records.** A record is valid or not on its own, and a validator cannot see from a dispatch that an event happens (A1 rejected). | Accepted the recommendation. Translated: "Q6 as per rec as sensible choice. Checked PR 19. Go as rec as sensible defaults." | Settled as drafted. |
| Q2 | Which glob dialect, and what is "overlap" (ADP-D-019)? | **ADP-2's own minimal dialect (`*` within a segment, `**` for whole segments). Paths with `.`, `..` or a leading `/` match nothing. Overlap uses the conservative literal-prefix test.** It is exact, small, safe against path traversal, and never misses an overlap (A2, A3 rejected). | Accepted the recommendation. Translated: "Q6 as per rec as sensible choice. Checked PR 19. Go as rec as sensible defaults." | Settled as drafted. |
| Q3 | How does a validator recognise a grant id in `dispatch.anchor` (ADP-D-020)? | **By membership: an entry is a grant id if it equals the id of a grant in the chain given.** No naming convention is needed (A4 rejected). | Accepted the recommendation. Translated: "Q6 as per rec as sensible choice. Checked PR 19. Go as rec as sensible defaults." | Settled as drafted. |
| Q4 | What about `AT-VERIFY` and codebase events, which a pure validator cannot infer (ADP-D-021)? | **Never inferred from a dispatch. They are declared in the grant or the record, and enforced by the runtime, like `AT-VCS` and `AT-TOOL` today.** This makes G-3 decidable (A5 rejected). | Accepted the recommendation. Translated: "Q6 as per rec as sensible choice. Checked PR 19. Go as rec as sensible defaults." | Settled as drafted. |
| Q5 | Grant document rules (ADP-D-022)? | **Every field required except `root`/`parent` (one of them) and the `scope` keys. `expires_at` in UTC. Unknown fields ignored. New rule G-10.** Every authority-limiting field is required, so typos fail closed (A6 rejected). | Accepted the recommendation. Translated: "Q6 as per rec as sensible choice. Checked PR 19. Go as rec as sensible defaults." | Settled as drafted. |
| Q6 | Bump class? | **Major, ADP-2 → 2.0.0, with SemVer for `adp_grant_version`.** ADP-0 §7 has no Draft exemption, and the cost now is only a number. The alternative is Minor (1.1.0) without the version grammar (A7), which leaves D-022 partly open. | Accepted the recommendation. Translated: "Q6 as per rec as sensible choice. Checked PR 19. Go as rec as sensible defaults." | Settled as drafted. |

---

## Application (if ACCEPTED), per ADP-0 §5.4

1. **SPEC:** C1.
2. **CONFORMANCE:** C2.
3. **SCHEMA:** C3.

   Steps 1–3 land in one commit:
   `spec(adp-2): decidable authority checks and codebase event record — ADP-A-006, ADP-D-018, ADP-D-019, ADP-D-020, ADP-D-021, ADP-D-022`.
4. **IMPLEMENTATION:** C4, in its own commit.
   `check_conformance.py` and `check-schema-gate` MUST pass after it.
5. **INFORMATIVE:** `README.md` structure listing: add
   `record.schema.json` and `grant.schema.json` under `schema/`.
6. **REGISTER:** ADP-D-018 to ADP-D-022 → RESOLVED,
   `Resolved by: ADP-A-006, <commit>`.

---

## Decision

ACCEPTED 2026-11-16 by the maintainer (ADP-0 §5.3). Apply as written,
with the answers recorded under the questions for the maintainer.
