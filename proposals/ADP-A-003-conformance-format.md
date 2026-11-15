# ADP-A-003: Conformance suite format and first ADP-1 vectors

| Field       | Value                                  |
|-------------|----------------------------------------|
| **ID**      | ADP-A-003                              |
| **Target**  | ADP-0 (`spec/ADP-0.md`); creates `conformance/` |
| **Resolves**| No defect. Fulfils ADP-0 §5.5 (see Anchor) |
| **Bump**    | ADP-0 1.0.0 → 1.1.0. ADP-1: none       |
| **Author**  | Contributor (agent-drafted, ADP-0 §8)  |
| **Drafted** | 2026-11-15                             |

---

## Outcome and impact

**In one line:** ADP gets an answer key. Every validation rule gets example
envelopes with a known verdict, so any validator, in any language, can
prove it follows ADP.

| Area | Effect when applied |
|------|---------------------|
| ADP-0 | New §5.6 *Conformance suite format*: layout, vector file shape, coverage rule, and how a known defect is marked. ADP-0 1.0.0 → 1.1.0. |
| `conformance/` | Created, with 26 vectors for ADP-1 §7: 5 passing and 21 failing. Every rule from V-01 to V-10 and R-01 to R-08 has at least one of each. |
| CI | New check `scripts/ci/check_conformance.py`, run in the `schema` job. It checks vector shape and coverage, and checks that the published schemas give each vector's expected verdict. |
| Schemas | No change. 24 of the 26 vectors already agree with the schemas. The 2 that do not are existing OPEN defects (ADP-D-004, ADP-D-009). They are marked, not hidden. |
| Implementations | ADP-0 §5.5 bars any "ADP conformant" claim until `conformance/` exists. After this proposal, such a claim becomes possible and testable. |
| ADP-A-002 | Its vectors (G-1 to G-9) are written in this format. ADP-A-003 must be applied before step 2 of ADP-A-002. |

Merging this proposal does not apply it. Application is a separate
change (see Application).

---

## Anchor

**ADP-0 §5.5:** "The first proposal accepted under ADP-0 that touches
validation MUST create `conformance/` with its format defined in that
proposal. No reference implementation may claim ADP conformance before
`conformance/` exists."

**ADP-A-002, Q5 (maintainer answer: option b):** a separate proposal,
ADP-A-003, creates `conformance/` and its format. ADP-A-002 adds only its
own vectors.

**Note for the record.** The ADP-A-001 Decision (`d9f7255`) says
`conformance/` "is created by ADP-A-002". The Q5 answer on ADP-A-002 moved
that to this proposal. Only the maintainer can amend a Decision line
(ADP-0 §5.3), so this proposal does not touch ADP-A-001.

Evidence at `50d18d3` (current `main`):

```
$ ls conformance
ls: conformance: No such file or directory

$ grep -n "conformance" scripts/ci/check_schema.py
(no output, exit 1)
```

---

## Change

### C1: ADP-0, new §5.6 *Conformance suite format*

Before: ADP-0 §5.5 requires the suite but defines no format. There is no
§5.6.

After: the text below is inserted after §5.5, before §6.

> ### 5.6 Conformance suite format
>
> #### 5.6.1 Layout
>
> ```
> conformance/
> └── <doc>/                  # adp-1, adp-2, … (lowercase document id)
>     └── <rule>/             # V-05, R-07, G-7, 7.3, … or _valid
>         └── <expect>-<slug>.json
> ```
>
> `<expect>` is `pass` or `fail`. `<slug>` is lowercase ASCII letters,
> digits and hyphens. A vector that passes every rule of a document lives
> under `_valid/`.
>
> #### 5.6.2 Vector file
>
> Each vector is one JSON file (RFC 8259), UTF-8, with these fields:
>
> | Field | Required | Meaning |
> |---|---|---|
> | `adp_conformance` | yes | Format version of this section. `"1"`. |
> | `target` | yes | `{"doc": "ADP-1", "since": "1.0.0", "kind": "dispatch"}`. `kind` names the input shape the target document defines. |
> | `rules` | yes | Rule ids this vector exercises. A `fail` vector MUST list exactly one. A `pass` vector MAY list several. |
> | `expect` | yes | `"pass"` or `"fail"`. MUST match the directory name prefix. |
> | `description` | yes | One sentence: what is in the input and why it gets the expected verdict. |
> | `known_defect` | no | An `ADP-D-NNN` id. See §5.6.4. |
> | `input` | yes | The document under test, in the shape `target.kind` names. |
>
> #### 5.6.3 Rules for vectors
>
> 1. A `fail` vector MUST violate exactly the one rule it lists, and
>    otherwise satisfy every rule of its target document. It SHOULD be a
>    `pass` vector with one change.
> 2. A vector's `expect` MUST follow the normative spec text, not any
>    schema or implementation (ADP-0 §3.2 rule 1).
> 3. No vector may be written for an input whose verdict depends on an
>    open internal contradiction in normative text (ADP-0 §3.2 rule 2).
>    Such inputs wait for the proposal that resolves the contradiction.
> 4. Coverage: every rule in a target document's validation tables MUST
>    have at least one `pass` and one `fail` vector. A `pass` vector covers
>    every rule in its `rules` list.
> 5. Vectors are changed only through an accepted proposal (ADP-0 §5.4
>    step 2), like any other normative artifact.
>
> #### 5.6.4 Known defects
>
> When a published schema or implementation disagrees with a vector, and
> the disagreement is an OPEN entry in `DEFECTS.md`, the vector carries
> `known_defect` with that id. Checks then expect the disagreement:
>
> - the defect is OPEN and the artifact disagrees: the check passes;
> - the defect is OPEN and the artifact agrees: the check fails, because the
>   marker is stale and must be removed;
> - the defect is not OPEN and the vector still has the marker: the check
>   fails.
>
> A marker never changes `expect`. The vector states what the spec
> requires. The marker records that a known artifact does not do that yet.

The ADP-0 header becomes Version 1.1.0, and one row is added to the Revision
Log:

```
| <applied> | 1.1.0. §5.6 Conformance suite format: layout,  |
|            | vector file, rules for vectors, known-defect   |
|            | markers. ADP-A-003.                            |
```

### C2: `conformance/adp-1/`, the first 26 vectors

All have `target` `{"doc": "ADP-1", "since": "1.0.0", ...}`. Base inputs:

- **Dispatch base:** `adp_version` `"1.0.0"`; `dispatch.agent`
  `"impl-agent"`; `dispatch.anchor` `["SPEC-001"]`; `context.read`
  `[{"path": "docs/spec.md"}]`; one work item `PRODUCE` / `"write module"`;
  `exit` `["tests pass"]`; `report` `["commit_hash"]`.
- **Report base:** status `COMPLETE`, one `exit_results` entry with
  `result: true`, one item `commit_hash`.

| Path (under `conformance/adp-1/`) | Rules | Change from base | Expect | Schema at `50d18d3` |
|---|---|---|---|---|
| `_valid/pass-dispatch-minimal.json` | V-01…V-10 | none | pass | pass |
| `_valid/pass-dispatch-all-optional.json` | V-01…V-10 | + model, tier 2, gate, branch, ignore, produce | pass | pass |
| `_valid/pass-report-complete.json` | R-01…R-06 | none | pass | pass |
| `R-07/pass-blocked.json` | R-07 | status BLOCKED, item `blocker` | pass | pass |
| `R-08/pass-surface.json` | R-08 | status SURFACE, item `finding` | pass | pass |
| `V-01/fail-missing-version.json` | V-01 | no `adp_version` | fail | fail |
| `V-01/fail-not-semver.json` | V-01 | `"1.0"` | fail | fail |
| `V-01/fail-leading-zero.json` | V-01 | `"01.0.0"` | fail | **pass**, `known_defect: ADP-D-009` |
| `V-02/fail-empty-agent.json` | V-02 | agent `""` | fail | fail |
| `V-03/fail-empty-anchor.json` | V-03 | anchor `[]` | fail | fail |
| `V-04/fail-empty-read.json` | V-04 | read `[]` | fail | fail |
| `V-05/fail-empty-exit.json` | V-05 | exit `[]` | fail | fail |
| `V-06/fail-empty-report.json` | V-06 | report `[]` | fail | fail |
| `V-07/fail-no-produce-no-work-items.json` | V-07 | no `work_items` | fail | fail |
| `V-08/fail-unknown-keyword.json` | V-08 | keyword `DELETE` | fail | fail |
| `V-09/fail-unknown-top-level-field.json` | V-09 | + `extra` (at 1.0.0) | fail | fail |
| `V-10/fail-tier-4.json` | V-10 | tier 4 | fail | fail |
| `7.3/fail-unknown-major.json` | §7.3 | `"2.0.0"` | fail | **pass**, `known_defect: ADP-D-004` |
| `R-01/fail-missing-version.json` | R-01 | no `adp_version` | fail | fail |
| `R-02/fail-empty-agent.json` | R-02 | agent `""` | fail | fail |
| `R-03/fail-empty-anchor.json` | R-03 | anchor `[]` | fail | fail |
| `R-04/fail-unknown-status.json` | R-04 | status `DONE` | fail | fail |
| `R-05/fail-empty-exit-results.json` | R-05 | exit_results `[]` | fail | fail |
| `R-06/fail-empty-items.json` | R-06 | items `[]` | fail | fail |
| `R-07/fail-blocked-without-blocker.json` | R-07 | status BLOCKED, no `blocker` | fail | fail |
| `R-08/fail-surface-without-finding.json` | R-08 | status SURFACE, no `finding` | fail | fail |

The **Schema** column is what `schema/*.json` at `50d18d3` returned for
these inputs. It was measured with jsonschema 4.26.0 (Draft 2020-12) in a
throwaway virtualenv outside the repository. 24 rows agree, and the 2 rows
that disagree are the two OPEN defects marked in the table.

**Not covered, on purpose** (§5.6.3 rule 3, or no rule exists):

| Input | Why no vector |
|---|---|
| `1.1.0` envelope with an unknown optional field | Open contradiction between V-09 and §7.3 (ADP-D-003). |
| Work item with keyword `SOURCE` | Open contradiction on whether SOURCE is a keyword (ADP-D-001, D-002). |
| `x-` metadata on the envelope, or with uppercase in the namespace | Location and character set undefined (ADP-D-006, D-007). |
| `adp_version` `"1.0.0-rc.1"` | Whether pre-release versions are meaningful is left open in ADP-D-009 Notes. |
| COMPLETE report with a failed exit result | No §7.2 rule checks it (ADP-D-008). |

### C3: CI check

Add `scripts/ci/check_conformance.py` and run it in the existing `schema`
job. It fails the job if any of the following holds:

- a vector breaks §5.6.2 (missing field, `expect` not matching its file
  name, a `fail` vector that lists more or fewer than one rule);
- a rule in the ADP-1 §7.1 or §7.2 tables lacks a `pass` or a `fail`
  vector;
- a schema verdict differs from `expect` and there is no `known_defect`
  marker;
- a `known_defect` marker is stale, as defined in §5.6.4.

For an ADP-1 vector, the schema verdict comes from `schema/dispatch.schema.json`
or `schema/report.schema.json`, chosen by `target.kind`. A vector for a
document with no published schema (ADP-2, until it has one) is checked for
shape and coverage only.

---

## Version impact

- **ADP-0:** 1.0.0 → 1.1.0. A section is added and no existing rule
  changes. ADP-0 §7 says process documents carry their own version. Its
  table classifies protocol changes, so the nearest row is "New optional
  field" (Minor).
- **ADP-1:** none. No text, schema or verdict changes. The vectors state
  what ADP-1 already requires.
- **ADP-A-001** (accepted, not yet applied) changes no verdict, so these
  vectors stay valid when ADP-1 moves to 1.0.1. `since: "1.0.0"` covers
  both.

---

## Conformance impact

This proposal is the conformance suite. It adds 26 vectors and flips none,
since none exist yet. It changes no schema. The two known-defect markers
are removed by the proposals that resolve ADP-D-004 and ADP-D-009, and the
CI check fails until they are.

---

## Alternatives

| # | Option | Why not |
|---|--------|---------|
| A1 | Put the format in a new document, ADP-3 | The format governs how normative artifacts are written and checked. That is process, which is ADP-0's remit, and ADP-0 §5.5 already owns the suite. A separate document would split one concern across two places. |
| A2 | Put the format in `conformance/README.md` | That file is Informative by default (ADP-0 §3.4), so it could not bind vectors. |
| A3 | YAML vectors | YAML 1.1 parsers read some unquoted scalars as booleans or numbers, so a vector could change meaning between parsers. JSON has one reading. `examples/` stay YAML because they are Informative. |
| A4 | One manifest file listing every vector | Every new vector would touch the same file, causing merge conflicts between unrelated proposals. With one file per vector, the diff shows exactly what changed. |
| A5 | Leave out vectors that the schemas get wrong | That hides ADP-D-004 and ADP-D-009 from the suite. A marker keeps the spec's verdict visible and fails CI the moment the defect is fixed without the marker being removed. |
| A6 | Format only, no vectors | The format would be unproven, and ADP-A-002 would be the first to try it. 26 vectors over existing rules exercise every part of §5.6 now. |

---

## Questions for the maintainer

| # | Question | Draft default |
|---|----------|---------------|
| Q1 | Should the format live in ADP-0 as a new §5.6 (as drafted), or in a new document? | ADP-0 §5.6 (A1). |
| Q2 | JSON vectors, as drafted? | Yes (A3). |
| Q3 | Should known-defect markers fail CI when stale (§5.6.4)? | Yes. Otherwise a fixed defect could leave a misleading marker behind. |
| Q4 | Should the ADP-1 vectors be part of this proposal (C2), or a separate one? | Part of this one (A6). They are the format's proof and change no verdict. |
| Q5 | The ADP-A-001 Decision line still names ADP-A-002 as the creator of `conformance/`. Add a note to it? | Your call. Only the maintainer may amend a Decision (ADP-0 §5.3). |

---

## Application (if ACCEPTED), per ADP-0 §5.4

1. **SPEC:** C1 in `spec/ADP-0.md` (§5.6, version, Revision Log).
2. **CONFORMANCE:** C2, all 26 vector files.
3. **SCHEMA:** none.
4. **IMPLEMENTATION:** C3, `scripts/ci/check_conformance.py`, wired into the
   `schema` job. The check MUST pass on the applying commit.
5. **INFORMATIVE:** one `conformance/` row in the `README.md` structure
   listing. `AGENTS.md` Enforcement table: one row for the new check.
6. **REGISTER:** no defect resolved. ADP-D-004 and ADP-D-009 each get a
   Notes line naming the vector that now carries their marker.

Steps 1 and 2 SHOULD land in one commit (ADP-0 §5.4).

---

## Decision

Pending. To be recorded by the maintainer (ADP-0 §5.3) as one line
beginning `ACCEPTED`, `REJECTED` or `DEFERRED`, with the date and the
reason.
