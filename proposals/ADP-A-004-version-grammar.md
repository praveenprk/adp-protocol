# ADP-A-004: `adp_version` grammar and the major-version check

| Field       | Value                                  |
|-------------|----------------------------------------|
| **ID**      | ADP-A-004                              |
| **Target**  | ADP-1 (`spec/ADP-1.md`), `schema/`, `conformance/adp-1/` |
| **Resolves**| ADP-D-004, ADP-D-009                   |
| **Bump**    | Patch: ADP-1 1.0.1 → 1.0.2 (see Version impact, Q2) |
| **Author**  | Contributor (agent-drafted, ADP-0 §8)  |
| **Drafted** | 2026-11-15                             |

---

## Outcome and impact

**In one line:** `adp_version` gets one exact grammar (SemVer 2.0.0), and
an envelope from a major version ADP-1 does not know (`2.0.0`, `0.9.0`) is
rejected, as §7.3 already requires.

| Area | Effect when applied |
|------|---------------------|
| ADP-1 text | V-01 and R-01 name SemVer 2.0.0. New rules V-11 and R-09: major version is 1. §7.3 says which major is known. §9 says pre-release and build suffixes are allowed and do not affect compatibility. |
| Envelopes and validators | Now rejected: `01.0.0`, `1.00.0`, `1.0.0-01`, `"1.0.0\n"`, `2.0.0`, `0.9.0`, `2.0.0-rc.1`. Now accepted: `1.0.0-rc.1`, `1.0.0+build.5`. `1.x.y` without a suffix is unchanged. |
| Schemas | `adp_version` pattern replaced in both schemas (C3). Needs this proposal ACCEPTED (`check-schema-gate`). |
| Conformance | Both `known_defect` markers removed. One vector moves from `7.3/` to `V-11/`. 12 vectors added (C2). |
| Version | ADP-1 1.0.1 → 1.0.2 (patch, erratum), if Q2 is answered as recommended. |
| Defect register | ADP-D-004 and ADP-D-009 → RESOLVED. 15 OPEN → 13 OPEN; CRITICAL open: D-003, D-006. |
| Examples, README | No change. All three examples use `1.0.0`. |
| Out of scope | §7.3 "ignore unknown optional fields" against V-09 and `additionalProperties: false`. That is the extensions cluster (ADP-D-003, D-006, D-007), handled by the next proposal. No vector here depends on it. |

Merging this proposal does not apply it. Application is a separate
change (see Application).

---

## Anchor

**ADP-D-004** (CRITICAL). §7.3 says "Parsers MUST reject unknown major
versions." No V- or R- rule checks the major version, and the schemas
accept `2.0.0`.

**ADP-D-009** (CRITICAL). V-01 and R-01 require `adp_version` to be
"parseable as semver". The schema pattern rejects valid SemVer
(`1.0.0-rc.1`) and accepts invalid SemVer (`01.0.0`). Its Notes leave
open "whether pre-release versions are meaningful for ADP"; §9 below
answers that.

One root cause: the `adp_version` string has no exact grammar, in the
spec or in the schemas. Both defects are fixed by the same pattern, so
ADP-0 §5.1 allows one proposal.

Evidence at `ec8f2cc` (current `main`):

```
$ grep -n "V-01\|R-01\|reject unknown major\|^Semver" spec/ADP-1.md
325:| V-01 | `adp_version` present and parseable as semver      |
340:| R-01 | `adp_version` present and parseable as semver      |
351:Parsers MUST reject unknown major versions.
379:Semver. `adp_version` field in every envelope.

$ grep -n '"pattern"' schema/*.json
schema/report.schema.json:12:      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$",
schema/dispatch.schema.json:12:      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$",
```

The current pattern under `jsonschema` 4.26.0 (Python), T = valid:

```
'1.0.0'=T '01.0.0'=T '1.00.0'=T '1.0.0-rc.1'=F '1.0.0+build.5'=F
'2.0.0'=T '0.9.0'=T '1.0.0\n'=T '1.0'=F
```

**New finding, same rule.** `"1.0.0\n"` (with a trailing newline) is
accepted by Python's `re`, because `$` also matches before a final
newline. ECMAScript's `$` does not: Node gives `false` for the same
pattern and input. So the published schema gives different verdicts
depending on the validator's language. `"1.0.0\n"` is not SemVer, so V-01
already requires rejecting it. This is the same defect as `01.0.0`
(non-conformant input accepted), found while drafting. It is recorded
in ADP-D-009's Notes at application, not filed separately (Q4).

**SemVer versions.** "semver" in ADP-1 names no version. SemVer 2.0.0
item 2 says X, Y and Z "MUST NOT contain leading zeroes", and item 10
defines `+` build metadata. SemVer 1.0.0 has neither rule. It allows
`01.0.0` and has no build metadata. Both versions allow a `-`
pre-release suffix. Sources: https://semver.org/spec/v2.0.0.html,
https://semver.org/spec/v1.0.0.html. This matters for the bump (Q2).

---

## Change

### C1: `spec/ADP-1.md`

**C1.1: V-01 and R-01** (lines 325, 340).

Before:

```
| V-01 | `adp_version` present and parseable as semver      |
| R-01 | `adp_version` present and parseable as semver      |
```

After:

```
| V-01 | `adp_version` present and valid SemVer 2.0.0       |
| R-01 | `adp_version` present and valid SemVer 2.0.0       |
```

**C1.2: new rules.** Append V-11 after V-10 in §7.1, and R-09 after R-08
in §7.2:

```
| V-11 | `adp_version` major version is 1 (§7.3)            |
```

```
| R-09 | `adp_version` major version is 1 (§7.3)            |
```

**C1.3: §7.3** (lines 349–354). Before:

```
### 7.3 Version Compatibility

Parsers MUST reject unknown major versions.
Parsers MUST accept unknown minor versions (ignore unknown
optional fields).
Unknown `x-` namespaced metadata fields are always ignored.
```

After (one sentence added, existing lines unchanged):

```
### 7.3 Version Compatibility

Parsers MUST reject unknown major versions.
Parsers MUST accept unknown minor versions (ignore unknown
optional fields).
Unknown `x-` namespaced metadata fields are always ignored.

For ADP-1 the only known major version is 1 (V-11, R-09).
```

**C1.4: §9** (line 379). Before:

```
Semver. `adp_version` field in every envelope.
```

After:

```
Semantic Versioning 2.0.0 (https://semver.org/spec/v2.0.0.html).
`adp_version` field in every envelope. A pre-release or build
metadata suffix is allowed (`1.1.0-rc.1`, `1.0.2+build.5`).
Compatibility (§7.3) depends on the major version only.
```

**C1.5: version and revision log.** Header Version `1.0.1` → `1.0.2`
(same column width). Date becomes the date of application. Append to the
Revision Log:

```
| <applied>  | 1.0.2. `adp_version` is SemVer 2.0.0 (§9,      |
|            | V-01, R-01); major version 1 checked by new    |
|            | V-11 and R-09 (§7.3). ADP-A-004, resolves      |
|            | ADP-D-004 and ADP-D-009.                       |
```

No other line in ADP-1 changes. No section is renumbered.

### C2: `conformance/adp-1/`

All vectors keep `"since": "1.0.0"`. The rules were already required by
the 1.0.0 text (ADP-0 §6; see Version impact). Inputs are the existing
dispatch or report base vector with only `adp_version` changed (ADP-0
§5.6.3 rule 1).

Changed:

| Vector | Change |
|--------|--------|
| `V-01/fail-leading-zero.json` | `known_defect` removed. |
| `7.3/fail-unknown-major.json` | Moved to `V-11/fail-major-2.json`. `rules` becomes `["V-11"]`. `known_defect` removed. Directory `7.3/` is then empty and removed. |
| `_valid/pass-dispatch-minimal.json`, `_valid/pass-dispatch-all-optional.json` | `"V-11"` appended to `rules`. |
| `_valid/pass-report-complete.json` | `"R-09"` appended to `rules`. |

Added (12):

| Vector | `adp_version` | Kind | Why |
|--------|---------------|------|-----|
| `V-01/pass-prerelease.json` | `1.0.0-rc.1` | dispatch | SemVer 2.0.0 item 9 |
| `V-01/pass-build-metadata.json` | `1.0.0+build.5` | dispatch | SemVer 2.0.0 item 10 |
| `V-01/fail-prerelease-leading-zero.json` | `1.0.0-01` | dispatch | item 9: numeric identifiers have no leading zeroes |
| `V-01/fail-minor-leading-zero.json` | `1.00.0` | dispatch | item 2 |
| `V-01/fail-trailing-newline.json` | `"1.0.0\n"` | dispatch | not SemVer; Python and ECMAScript disagree today |
| `V-11/pass-unknown-minor.json` | `1.7.0` | dispatch | §7.3: unknown minor MUST be accepted |
| `V-11/fail-major-0.json` | `0.9.0` | dispatch | major 0 is not known |
| `V-11/fail-major-2-prerelease.json` | `2.0.0-rc.1` | dispatch | a suffix does not change the major |
| `R-01/pass-prerelease.json` | `1.0.0-rc.1` | report | as V-01 |
| `R-01/fail-leading-zero.json` | `01.0.0` | report | as V-01 |
| `R-09/pass-unknown-minor.json` | `1.7.0` | report | as V-11 |
| `R-09/fail-major-2.json` | `2.0.0` | report | as V-11 |

Each `fail` vector breaks exactly one rule: every version above that
fails V-11 is valid SemVer, and every version that fails V-01 has major
1 or is not parseable at all. After C2 there are 38 vectors, and every
rule V-01 to V-11 and R-01 to R-09 has at least one `pass` and one
`fail` vector (ADP-0 §5.6.3 rule 4).

### C3: `schema/dispatch.schema.json`, `schema/report.schema.json`

The `adp_version` property in both files. Before:

```json
"adp_version": {
  "type": "string",
  "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$",
  "description": "Semver protocol version"
},
```

After:

```json
"adp_version": {
  "type": "string",
  "pattern": "^1\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)(-(0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)(\\.(0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*)?(\\+[0-9A-Za-z-]+(\\.[0-9A-Za-z-]+)*)?(?![\\s\\S])",
  "description": "ADP-1 protocol version: SemVer 2.0.0 with major version 1 (ADP-1 §9; V-01, V-11, R-01, R-09)",
  "$comment": "Ends with (?![\\s\\S]), not $: in Python re, $ also matches before a final newline. [0-9], not \\d: in Python re, \\d matches non-ASCII digits."
},
```

The pattern is the SemVer 2.0.0 grammar (item 2, 9 and 10), with major
fixed to `1`. It uses no feature outside the ECMA-262 subset that JSON
Schema recommends. Checked while drafting, with `jsonschema` 4.26.0 and
Node's `RegExp`:

```
          1.0.0 1.0.0\n 1.0.0-rc.1 1.0.0+b.1 01.0.0 2.0.0 1.0.0-01
Python    T     F       T          T         F      F     F
Node      T     F       T          T         F      F     F
```

Both schemas still pass the Draft 2020-12 metaschema (checked with
`Draft202012Validator.check_schema`).

---

## Version impact

**Patch** (ADP-1 1.0.1 → 1.0.2), as an erratum under ADP-0 §6(a), if
"semver" is read as SemVer 2.0.0 (Q2).

- **C3 and C2** bring the schemas and vectors into agreement with text
  that already exists. §7.3 already says "MUST reject unknown major
  versions". V-01/R-01 already say "parseable as semver". ADP-0 §6 says
  errata take a patch bump "even when the corrected artifact accepts or
  rejects envelopes differently afterwards".
- **C1.2 and C1.3** add no requirement. V-11/R-09 restate §7.3's MUST in
  the §7 tables, so that §7's "MUST reject … any rule in §7.1" covers
  it. This is the same reasoning ADP-A-001 C2 used (ADP-1 §9 "Spec
  clarification").
- **C1.1 and C1.4** name the SemVer version. This is a clarification
  only if "semver" already meant SemVer 2.0.0. The case for that:
  - SemVer 2.0.0 has been the current SemVer since 2013;
  - ADP-1 was written in 2026;
  - ADP-D-009 was filed and graded on that reading.

  If the maintainer reads "semver" as not settled, then rejecting
  `01.0.0` is "Validator tightening not required by existing text" and
  the bump is Major (ADP-0 §7).
- Pre-release acceptance is required under either SemVer version, since
  both allow a `-` suffix.

---

## Conformance impact

C2 in full. Verdict flips against the published schema (before → after):

- **V-01:** `1.0.0-rc.1`, `1.0.0+build.5` F→T; `01.0.0`, `1.00.0`,
  `"1.0.0\n"` T→F.
- **R-01:** `1.0.0-rc.1` F→T; `01.0.0` T→F.
- **V-11/R-09:** `2.0.0`, `0.9.0` T→F.

No existing vector's `expect` changes. Two markers are removed. The CI check
(`check_conformance.py`) fails if the schema change lands without
removing them, or if the markers are removed without the schema change
(ADP-0 §5.6.4). So steps 1–3 must land in one commit.

---

## Alternatives

| # | Option | Why not |
|---|--------|---------|
| A1 | Reject pre-release and build suffixes (core `X.Y.Z` only) | V-01 says "semver", and every SemVer version allows a pre-release. Rejecting it means changing the spec to match the schema, which reverses ADP-0 §3.2 rule 1 (spec wins). It also leaves no way to label draft protocol versions. |
| A2 | Fold the major check into V-01/R-01 instead of new V-11/R-09 | Then `2.0.0` and `01.0.0` fail the same rule, so a report cannot say which check failed. It also breaks the one-check-per-rule shape of the tables. |
| A3 | Keep `$` at the end of the pattern and file the newline case as its own defect | Same rule (V-01), same pattern, same line. Fixing the pattern twice in two proposals is more churn for the same result. |
| A4 | Use the regex suggested on semver.org as is | It uses `\d`, which matches non-ASCII digits in Python, and `$`, which has the newline problem above. It also allows any major. |
| A5 | Keep `7.3/` as the rule directory for the major check | §7.3 is not a table rule, so the coverage check (§5.6.3 rule 4) does not see it. A table rule makes coverage mechanical. |
| A6 | Accept every major in the schema and leave the major check to implementations | §7 binds validators to the tables, and the schema is the published validator. D-004 would stay open. |

---

## Questions for the maintainer

For Q1 to Q4, the recommendation below was sent to the maintainer in a
working session and matches the drafted default. The maintainer's answers
were given in that session and are quoted as English translations.
These answers shape the draft. They do not accept it. Only the Decision
section below accepts or rejects the proposal (ADP-0 §5.3).

| # | Question | Recommendation (setting and reason) | Maintainer answer | Effect on this draft |
|---|----------|-------------------------------------|-------------------|----------------------|
| Q1 | Are pre-release (`1.0.0-rc.1`) and build metadata (`1.0.0+build.5`) suffixes allowed in `adp_version`? | **Allowed; compatibility uses the major only.** V-01 already says "semver", and SemVer allows them. Rejecting them would change the spec to match a wrong schema (A1 rejected). | Accepted the recommendation. Translated: "Go with rec, Q1-Q4 all yes as sensible defaults and decisions." | Settled as drafted. |
| Q2 | Does "semver" in ADP-1 1.0.0 mean SemVer 2.0.0? | **Yes, so this is a patch (1.0.2) erratum.** 2.0.0 has been the current SemVer since 2013, and ADP-D-009 was graded on that reading. If no, rejecting `01.0.0` is a Major change (ADP-0 §7). | Accepted the recommendation. Translated: "Go with rec, Q1-Q4 all yes as sensible defaults and decisions." | Settled as drafted. |
| Q3 | Should the major check be new rules V-11/R-09, or part of V-01/R-01? | **New rules V-11/R-09.** One check per rule, so a failure names its cause, and the coverage check covers it (A2, A5 rejected). | Accepted the recommendation. Translated: "Go with rec, Q1-Q4 all yes as sensible defaults and decisions." | Settled as drafted. |
| Q4 | Should the `"1.0.0\n"` newline case be fixed here and noted on ADP-D-009, or filed as a new defect? | **Fix it here and add a Notes line on ADP-D-009.** Same rule, same pattern, same root cause (A3 rejected). | Accepted the recommendation. Translated: "Go with rec, Q1-Q4 all yes as sensible defaults and decisions." | Settled as drafted. |

---

## Application (if ACCEPTED), per ADP-0 §5.4

1. **SPEC:** C1.
2. **CONFORMANCE:** C2.
3. **SCHEMA:** C3.

   Steps 1–3 land in one commit:
   `spec(adp-1): SemVer 2.0.0 grammar and major-version check — ADP-A-004, ADP-D-004, ADP-D-009`.
   The CI checks `check_conformance.py` and `check-schema-gate` MUST pass on it.
4. **IMPLEMENTATION:** none exists. `check_conformance.py` needs no change:
   it reads the new rows from the tables.
5. **INFORMATIVE:** none. The examples and README use `1.0.0`.
6. **REGISTER:** ADP-D-004 and ADP-D-009 → RESOLVED,
   `Resolved by: ADP-A-004, <commit>`. ADP-D-009 also gets a Notes line
   for the newline case (Q4).

---

## Decision

