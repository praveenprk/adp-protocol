# ADP-A-007: Make ADP-1's text and its validation contract agree

| Field       | Value                                  |
|-------------|----------------------------------------|
| **ID**      | ADP-A-007                              |
| **Target**  | ADP-1 (`spec/ADP-1.md`), ADP-2 (`spec/ADP-2.md`, one note), `schema/report.schema.json`, `conformance/adp-1/`, `examples/tier3-impl.yaml` |
| **Resolves**| ADP-D-001, ADP-D-002, ADP-D-008, ADP-D-010, ADP-D-013, ADP-D-024, ADP-D-025 |
| **Bump**    | Patch: ADP-1 1.1.0 → 1.1.1; ADP-2 2.0.0 → 2.0.1 (see Version impact, Q6) |
| **Author**  | Contributor (agent-drafted, ADP-0 §8)  |
| **Drafted** | 2026-11-17                             |

---

## Outcome and impact

**In one line:** after this, a validator that implements only ADP-1 §7
gives the same verdict as the published schemas, and ADP-1 text that no
validator can check says so instead of claiming to be a rule.

| Area | Effect when applied |
|------|---------------------|
| ADP-1 text | `SOURCE` is not a keyword; the origin of a work item is its `source` field. `COMPLETE` with a failed exit is invalid (new R-13). Field types and required entry fields are written down (new §4.5, §5.5) and checked (new V-13, R-12). Tier selection is informative, with one rule for when several signals apply. Deduplication (§8) is a SHOULD NOT that validators do not check. |
| Validators | 26 rules instead of 23. Every rejection the published schemas make is now named by a rule. |
| Schemas | `report.schema.json` rejects a `COMPLETE` report with a failed exit result. `dispatch.schema.json` does not change. |
| Conformance | 15 vectors added, 3 `_valid` vectors list the new rules. 68 ADP-1 vectors. |
| Examples | The tier 3 example no longer carries a `BIND` work item. |
| Version | ADP-1 1.1.0 → 1.1.1 and ADP-2 2.0.0 → 2.0.1, both Patch (Q6). |
| Defect register | 7 defects → RESOLVED: all 6 open HIGH defects, plus ADP-D-013 (LOW). 13 OPEN → 6 OPEN, none HIGH. |
| Not changed | The 10 keywords, `dispatch.schema.json`, the version rules (§7.3, §9), and every ADP-2 rule. |

Merging this proposal does not apply it. Application is a separate
change (see Application).

---

## Scenarios

One job throughout: a bank's orchestrator dispatches an agent to fix
a loan-interest rounding bug from `LOAN-12 §4`. The agent edits
`interest.rs`. EXIT: "tests pass", "auditor review recorded".

| Q | Envelope | Today | With the recommendation | With the alternative |
|---|----------|-------|-------------------------|----------------------|
| Q1 | Origin written as `keyword: SOURCE`, as `source:` and as `x-bank-source:` | Three valid places. An auditor's tool that searches one of them misses the others. | One place: `source: "LOAN-12 §4"`. The `SOURCE` keyword fails V-08. | 11th keyword: Major bump; every 1.x validator rejects it. |
| Q2 | `status: COMPLETE`, "auditor review recorded" `result: false` | Valid. The job shows as done without the review. | Fails R-13. The agent reports `BLOCKED` with the reason. | "Done" stays unchecked. |
| Q3 | `produce: [{action: modify}]`, no `path` | The schema rejects it; §7 does not. Validators built from the text accept it. | Fails V-13. Every validator agrees and names the rule. | The schema and the text disagree; "conformant" depends on the vendor. |
| Q4 | Work items `BIND` (pick a rounding method) + `CONFIRM` (tests) | The table gives tier 1 and tier 2. | Tier 1: lowest wins. Informative; validators check only 1–3 (V-10). | A validator tier rule: envelopes valid today fail (Major). |
| Q5 | The dispatch repeats the commit format from a READ document | Both MUST NOT and SHOULD. | SHOULD NOT; validators do not check it. | A MUST that nothing can check. |
| Q6 | Any envelope the published schemas accept today | n/a | Still accepted, except the Q2 case. Patch: 1.1.1 / 2.0.1. | Major: a breaking-change signal with nothing broken. |

---

## Anchor

All seven defects share one root: ADP-1 §7 says "A validator MUST reject
a dispatch envelope that fails any rule in §7.1", so §7 is the
validation contract. The rest of ADP-1 does not line up with it:

| Defect | Gap | Fixed by |
|--------|-----|----------|
| ADP-D-001 | §3 says 10 keywords; §3.1–§3.4 define 11. V-08's "defined vocabulary" has no single meaning. | C1.1 |
| ADP-D-002 | The origin of a work item is a keyword, a field and an extension key at once. | C1.1, C1.2 |
| ADP-D-008 | §5.3 defines `COMPLETE` as "all EXIT conditions passed"; no rule checks it. | C1.5, C3 |
| ADP-D-024 | The schemas reject envelopes that fail no §7 rule (missing `path`, empty `description`, …). | C1.4, C1.6 |
| ADP-D-010 | Tier selection rows give two tiers for one envelope. | C1.7 |
| ADP-D-013 | The tier 3 example carries a `BIND` item, against the tier table. | C5 |
| ADP-D-025 | §8 states deduplication as both MUST NOT and SHOULD. | C1.8 |

The first four are requirements outside §7 that §7 should hold or name.
The last three are statements that sound like requirements but cannot be
checked from an envelope; they are marked as such. ADP-D-013 depends on
ADP-D-010 (its own notes say so).

Evidence: the entries in `DEFECTS.md` at `f6fd6ca` (current `main`).

---

## Change

### C1: `spec/ADP-1.md`

**C1.1: §3.4 Scope Keywords.** Remove the `SOURCE` row. Append after
the table:

```
The origin of a work item in a governing document is carried in the
work item's `source` field (§4.3). `SOURCE` is not a keyword.
```

§3 "10 keywords. Fixed at v1.0.0." is unchanged and now true. In §6
Tier 1, "SOURCE per work item" → "`source` per work item".

**C1.2: §3.5 example.** The example stops carrying the origin a second
time as an extension key.

Before:

```yaml
work_items:
  - keyword: "BIND"
    description: "choose superseding structure"
    metadata:
      x-contextos-seam: 4
      x-contextos-source: "SPEC-027 §5"
```

After:

```yaml
work_items:
  - keyword: "BIND"
    description: "choose superseding structure"
    source: "SPEC-027 §5"
    metadata:
      x-contextos-seam: 4
```

**C1.3: §4.3 Field Definitions.** Two comments change:

- ProduceEntry `action: string  # "create" | "modify"` →
  `action: string  # optional — "create" | "modify"`.
- WorkItem `source: string  # optional — origin reference` →
  `source: string  # optional — origin section in a governing document`.

**C1.4: new §4.5 Field Constraints** (after §4.4):

```
### 4.5 Field Constraints

Each constraint is checked by exactly one rule (§7.1).

| Field                          | Constraint                                   | Rule |
|--------------------------------|----------------------------------------------|------|
| `adp_version`                  | SemVer 2.0.0 with major version 1            | V-01, V-11 |
| `dispatch.agent`               | Non-empty string                             | V-02 |
| `dispatch.anchor`              | Non-empty array                              | V-03 |
| `dispatch.anchor[]`            | Non-empty string                             | V-13 |
| `dispatch.model`, `dispatch.gate`, `dispatch.branch` | String                 | V-13 |
| `dispatch.tier`                | 1, 2 or 3                                    | V-10 |
| `context.read`                 | Non-empty array                              | V-04 |
| `context.read[]`               | `path` present, a non-empty string; `sections`, if present, an array of strings | V-13 |
| `context.ignore`               | Array of strings                             | V-13 |
| `produce` or `work_items`      | At least one present                         | V-07 |
| `produce[]`                    | `path` present, a non-empty string; `action`, if present, `create` or `modify` | V-13 |
| `work_items[].keyword`         | Present, one of the 10 keywords (§3.1–§3.4)  | V-08 |
| `work_items[]`                 | `description` present, a non-empty string; `source`, if present, a string | V-13 |
| `exit`                         | Non-empty array                              | V-05 |
| `report`                       | Non-empty array                              | V-06 |
| `exit[]`, `report[]`           | Non-empty string                             | V-13 |
| `metadata`, at every level     | An object                                    | V-13 |
| `metadata` keys                | The §3.5 form                                | V-12 |
| Every §4 object                | No unknown field (§7.3)                      | V-09 |
```

**C1.5: §5.3 Status Values.** The `COMPLETE` row:

Before: `| COMPLETE | All EXIT conditions passed. Work done. |`

After: `| COMPLETE | All EXIT conditions passed. Work done. Every `exit_results[].result` MUST be `true`. |`

(wrapped to the table's width as the other rows are).

**C1.6: new §5.5 Field Constraints** (after §5.4):

```
### 5.5 Field Constraints

Each constraint is checked by exactly one rule (§7.2).

| Field                          | Constraint                                   | Rule |
|--------------------------------|----------------------------------------------|------|
| `adp_version`                  | SemVer 2.0.0 with major version 1            | R-01, R-09 |
| `report.agent`                 | Non-empty string                             | R-02 |
| `report.anchor`                | Non-empty array                              | R-03 |
| `report.anchor[]`              | Non-empty string                             | R-12 |
| `report.status`                | `COMPLETE`, `BLOCKED` or `SURFACE`           | R-04 |
| `exit_results`                 | Non-empty array                              | R-05 |
| `exit_results[]`               | `condition` present, a non-empty string; `result` present, a boolean | R-12 |
| `items`                        | Non-empty array                              | R-06 |
| `items[]`                      | `key` present, a non-empty string; `value` present, a string, which may be empty | R-12 |
| `metadata`                     | An object                                    | R-12 |
| `metadata` keys                | The §3.5 form                                | R-11 |
| Every §5 object                | No unknown field (§7.3)                      | R-10 |

Status-dependent rules are R-07, R-08 and R-13 (§5.3).
```

**C1.7: §6 Tier Selection.** The heading
`### Tier Selection Guidance` becomes
`### Tier Selection Guidance (Informative)`. Remove the row
`| Work items mix BIND + CONFIRM | 2 |`. Append after the table:

```
When more than one signal applies, use the lowest tier number among
them. A lower tier keeps more context, which is the safe side when the
agent must use judgment. Validators check only that `dispatch.tier` is
1, 2 or 3 (V-10). They do not check the tier against the work items.
```

**C1.8: §8 Deduplication Rule.** Two paragraphs change. The Exception
paragraph is unchanged.

Before:

```
A dispatch envelope MUST NOT carry content that is structurally
available to the agent through its READ context. If a role
boundary, commit format, or behavioral constraint exists in a
document the agent is directed to READ, restating it in the
dispatch is redundant and non-conformant.
...
Deduplication is a SHOULD for v1.0.0 (not mechanically
enforced by the validator — requires semantic understanding
of READ content). Future versions may introduce content-hash
deduplication.
```

After:

```
A dispatch envelope SHOULD NOT carry content that is structurally
available to the agent through its READ context. If a role
boundary, commit format, or behavioral constraint exists in a
document the agent is directed to READ, restating it in the
dispatch is redundant.
...
Validators do not check this rule: checking it requires
understanding the READ content. Future versions may introduce
content-hash deduplication.
```

**C1.9: §7 tables.** §7.1 V-08 and three new rows:

```
| V-08 | Every `work_items[].keyword` is one of the 10 keywords (§3.1–§3.4) |
| V-13 | Field types and entry fields per §4.5              |
```

§7.2, appended:

```
| R-12 | Field types and entry fields per §5.5              |
| R-13 | If status COMPLETE: every `exit_results[].result` is true |
```

**C1.10: header and Revision Log.** Version `1.1.0` → `1.1.1`. Date
becomes the date of application. Append:

```
| <applied>  | 1.1.1. SOURCE is the `source` field, not a     |
|            | keyword (§3.4); field constraints (§4.5, §5.5)  |
|            | checked by new V-13 and R-12; COMPLETE needs   |
|            | every exit result true (§5.3, new R-13); tier  |
|            | selection informative (§6); deduplication a    |
|            | SHOULD NOT (§8). ADP-A-007, resolves ADP-D-001, |
|            | ADP-D-002, ADP-D-008, ADP-D-010, ADP-D-013,    |
|            | ADP-D-024 and ADP-D-025.                       |
```

### C2: `spec/ADP-2.md`

§3, the note under the table:

Before:

```
`SOURCE` is left out. Whether it is a keyword is open as ADP-D-001 and
ADP-D-002. Either way it implies nothing.
```

After:

```
`SOURCE` is not an ADP-1 keyword (ADP-1 §3.4). A work item's `source`
field implies nothing.
```

Header version `2.0.0` → `2.0.1`, date of application, and a Revision
Log row: "2.0.1. §3 note: `SOURCE` is not a keyword. ADP-A-007."

### C3: `conformance/adp-1/`

Changed (no verdict changes):

- `_valid/pass-dispatch-minimal.json` and `_valid/pass-dispatch-all-optional.json`:
  `rules` gains `V-13`;
- `_valid/pass-report-complete.json`: `rules` gains `R-12` and `R-13`.

Added (15). Each is a `_valid` vector with one change.

| Vector | Input change | Expect |
|--------|--------------|--------|
| `V-08/fail-source-keyword` | work item keyword `SOURCE` | fail |
| `V-13/pass-produce-without-action` | `produce: [{"path": "src/a.py"}]` | pass |
| `V-13/pass-work-item-source` | work item with `source: "SPEC-001 §2"` | pass |
| `V-13/fail-produce-without-path` | `produce: [{"action": "create"}]` | fail |
| `V-13/fail-unknown-action` | `action: "delete"` | fail |
| `V-13/fail-empty-description` | work item `description: ""` | fail |
| `V-13/fail-read-entry-without-path` | `context.read: [{"sections": ["§1"]}]` | fail |
| `V-13/fail-empty-anchor-entry` | `dispatch.anchor: ["SPEC-001", ""]` | fail |
| `V-13/fail-model-not-string` | `dispatch.model: 4` | fail |
| `R-12/pass-empty-item-value` | item `value: ""` | pass |
| `R-12/fail-exit-result-without-result` | `exit_results: [{"condition": "tests pass"}]` | fail |
| `R-12/fail-result-not-boolean` | `result: "yes"` | fail |
| `R-12/fail-item-without-value` | `items: [{"key": "commit_hash"}]` | fail |
| `R-13/pass-blocked-with-failed-exit` | status `BLOCKED`, one exit `false`, a `blocker` item | pass |
| `R-13/fail-complete-with-failed-exit` | status `COMPLETE`, a second exit with `result: false` | fail |

`V-08/fail-source-keyword` could not be written before: its verdict
depended on an open contradiction (ADP-0 §5.6.3 rule 3).

After C3 there are 68 ADP-1 vectors, and every rule V-01 to V-13 and
R-01 to R-13 has at least one `pass` and one `fail` vector.

### C4: `schema/report.schema.json`

`allOf` gains:

```json
{
  "$comment": "R-13: a COMPLETE report has no failed exit result (ADP-1 §5.3).",
  "if": { "properties": { "report": { "properties": { "status": { "const": "COMPLETE" } } } } },
  "then": { "properties": { "exit_results": { "items": { "properties": { "result": { "const": true } } } } } }
}
```

`dispatch.schema.json` does not change: it already enforces §4.5
exactly, and its keyword enum already lists the 10 keywords.

Checked while drafting: the prototype passes the Draft 2020-12
metaschema. On the 15 inputs above, the published dispatch schema and
the prototype report schema give the intended verdict for every one. No
existing ADP-1 vector changes verdict under the prototype.

### C5: `examples/tier3-impl.yaml`

Line 29, `keyword: "BIND"` → `keyword: "PRODUCE"`. The item applies a
shape the design already fixed ("per DESIGN Seam 4 shape"), which is
production, not an irreversible decision.

---

## Version impact

**ADP-1: Patch, 1.1.0 → 1.1.1.** Each part, against ADP-0 §6 and §7:

- **`SOURCE` (C1.1, C1.2):** erratum, ADP-0 §6(b). It resolves a
  contradiction, and the published schema already rejects `SOURCE`, so
  no verdict changes. It is not a "keyword removal": the keyword count
  §3 states, and the schema enforces, stays at 10.
- **`COMPLETE` (C1.5, C4):** erratum, ADP-0 §6(a). §5.3 already
  defines `COMPLETE` as "All EXIT conditions passed", so the schema
  change is required by existing text. R-13 restates §5.3 in the table.
- **Field constraints (C1.3, C1.4, C1.6):** ADP-1 §9, "Spec
  clarification, no schema Δ". The published schemas already give every
  verdict §4.5 and §5.5 state. This is not "validator tightening not
  required by existing text" (ADP-0 §7) against any published artifact.
  It is tightening against a validator that implements §7 alone, and no
  such validator exists (Q6).
- **Tier selection (C1.7):** section reclassified informative, Patch
  (ADP-0 §7).
- **Deduplication (C1.8):** erratum, ADP-0 §6(b). No published
  artifact checks §8, so no verdict changes.

**ADP-2: Patch, 2.0.0 → 2.0.1.** Editorial (ADP-0 §7): the note's
claim ("implies nothing") is unchanged; only the reference to open
defects goes.

---

## Conformance impact

C3 in full. Against the published schemas, one verdict flips
(before → after):

- `R-13/fail-complete-with-failed-exit`: T → F (erratum, §6(a)).

Every other added vector already gets its expected verdict from the
published schemas. No existing vector changes verdict.

---

## Alternatives

| # | Option | Why not |
|---|--------|---------|
| A1 | Make `SOURCE` the 11th keyword | A keyword addition is Major (ADP-0 §7), contradicts §3.5 ("No new keywords in any 1.x.y release"), and changes the published schema. `source` already carries the same information as a field. |
| A2 | `COMPLETE` also requires an `exit_results` entry for every EXIT of the dispatch | Not decidable from a report alone: the dispatch is not a validator input (§7 "Envelope in, result out"). The orchestrator can check it. |
| A3 | Require `produce[].action` | The published schema does not require it, so requiring it tightens a published verdict (Major). §4.3 never said it was required either. |
| A4 | List field constraints inside the V-13 and R-12 rows | The rows would be long and still need the type of every field. One table per envelope, with one rule per constraint, keeps every fail vector to exactly one rule (ADP-0 §5.6.3 rule 1). |
| A5 | Keep tier selection normative and add a validator rule for it | Tier choice is "orchestrator's responsibility" (§6). A rule would reject envelopes that are valid today (Major) for a judgment call. |
| A6 | Keep §8 as MUST NOT, enforced by the orchestrator | A MUST that no validator and no runtime can check is not testable, and the text already says it needs semantic understanding. |
| A7 | One proposal per defect group (five proposals) | The groups share one root and the same §7 tables. Five proposals would mean five ADP-1 patch releases and five rounds of the same table edits. |

---

## Questions for the maintainer

| # | Question | Recommendation (setting and reason) | Maintainer answer | Effect on this draft |
|---|----------|-------------------------------------|-------------------|----------------------|
| Q1 | Is `SOURCE` a keyword (ADP-D-001, ADP-D-002)? | **No. The origin of a work item is the `source` field; `SOURCE` leaves the keyword table.** The keyword count, the schema and §3.5's freeze already say 10 (A1 rejected). | Accepted as sensible default (2026-11-17). | Settled as drafted. |
| Q2 | What does `COMPLETE` require (ADP-D-008)? | **Every `exit_results[].result` is `true` (new R-13).** It is what §5.3 already says, and it is decidable from the report (A2 rejected). | Accepted as sensible default (2026-11-17). | Settled as drafted. |
| Q3 | How are field types and entry fields made part of the contract (ADP-D-024)? | **Write them down as §4.5 and §5.5, exactly as the published schemas enforce them, checked by new V-13 and R-12. `action` stays optional.** No published verdict changes (A3, A4 rejected). | Accepted as sensible default (2026-11-17). | Settled as drafted. |
| Q4 | How is the tier contradiction resolved (ADP-D-010, ADP-D-013)? | **Tier selection becomes informative; the "mix BIND + CONFIRM" row goes; when signals conflict, the lowest tier wins. The tier 3 example's `BIND` becomes `PRODUCE`.** Tier choice is the orchestrator's judgment (A5 rejected). | Accepted as sensible default (2026-11-17). | Settled as drafted. |
| Q5 | MUST NOT or SHOULD NOT for deduplication (ADP-D-025)? | **SHOULD NOT, and §8 says validators do not check it.** It cannot be checked from an envelope (A6 rejected). | Accepted as sensible default (2026-11-17). | Settled as drafted. |
| Q6 | Bump class and bundling? | **One proposal; Patch for both: ADP-1 1.1.1, ADP-2 2.0.1.** Every part is an erratum, a reclassification, or a clarification with no change to any published schema verdict except R-13, which §5.3 already required (A7 rejected). | Accepted as sensible default (2026-11-17). | Settled as drafted. |

---

## Application (if ACCEPTED), per ADP-0 §5.4

1. **SPEC:** C1, C2.
2. **CONFORMANCE:** C3.
3. **SCHEMA:** C4.

   Steps 1–3 land in one commit:
   `spec(adp-1): align the text with the validation contract — ADP-A-007, ADP-D-001, ADP-D-002, ADP-D-008, ADP-D-010, ADP-D-024, ADP-D-025`.
4. **IMPLEMENTATION:** none. `check_conformance.py` picks up the new
   rule rows from the §7 tables and needs no change.
5. **INFORMATIVE:** C5, in its own commit, anchored to ADP-D-013.
6. **REGISTER:** ADP-D-001, ADP-D-002, ADP-D-008, ADP-D-010,
   ADP-D-013, ADP-D-024 and ADP-D-025 → RESOLVED,
   `Resolved by: ADP-A-007, <commit>`.

---

## Decision
