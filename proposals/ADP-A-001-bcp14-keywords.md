# ADP-A-001: Declare BCP 14 key words and bind the validation rules

| Field       | Value                                  |
|-------------|----------------------------------------|
| **ID**      | ADP-A-001                              |
| **Target**  | ADP-1 (`spec/ADP-1.md`)                |
| **Resolves**| ADP-D-012                              |
| **Bump**    | Patch: ADP-1 1.0.0 → 1.0.1             |
| **Author**  | Contributor (agent-drafted, ADP-0 §8)  |
| **Drafted** | 2026-11-15                             |

---

## Outcome and impact

**In one line:** this changes what ADP-1's words mean, not what any
validator does, and it unblocks the fixes for the CRITICAL defects.

| Area | Effect when applied |
|------|---------------------|
| ADP-1 text | The 10 uppercase key words become binding with BCP 14 meaning. Lowercase words stay plain English. The 18 V-/R- rules become explicit MUST-reject requirements. |
| Envelopes and validators | No envelope changes verdict. The schemas already reject what the rules reject, except V-01, which stays open as ADP-D-009. |
| Version | ADP-1 1.0.0 → 1.0.1 (patch) |
| Defect register | ADP-D-012 → RESOLVED. ADP-D-008 and D-009 get a firm basis for their grades. |
| Downstream | CRITICAL fixes (D-003/006/007, D-004/009) can be written as MUST rules. The Internet-Draft needs the BCP 14 statement anyway. |
| Risk | ADP-0 §5.5 reading of C2; see Conformance impact. |

Merging this proposal does not apply it. Application is a separate
change (see Application).

---

## Anchor

**ADP-D-012** (HIGH). ADP-1 uses MUST, MUST NOT and SHOULD in ten
places but never says how to interpret them. RFC 2119 appears only in
the §10 comparison table. The §7.1 and §7.2 validation tables use no
key word at all, so their binding strength is undefined. The grades
of ADP-D-008 and ADP-D-009 depend on this.

Evidence at `0ff059d` (current `main`):

```
$ grep -n "RFC 2119\|BCP 14\|RFC 8174" spec/ADP-1.md
384:| RFC 2119 | Complementary vocabularies. RFC 2119 governs   |
387:|          | An ADP envelope may quote RFC 2119 terms when  |

$ grep -nwE 'MUST|SHOULD|MAY|REQUIRED|SHALL|RECOMMENDED|OPTIONAL' spec/ADP-1.md | cut -d: -f1 | paste -sd' ' -
123 124 192 238 242 247 338 339 347 357

$ grep -cE '^\| [VR]-[0-9]{2} ' spec/ADP-1.md
18
```

The lowercase forms are "must" on lines 271 and 280 (§6 "Use when"),
"may" on lines 359 and 387, and "optional" or "Optional" in headings
and comments. Each describes a situation and is not meant as a
requirement. Under RFC 8174 they stay non-normative, which matches
how they read now.

---

## Change

Three changes to `spec/ADP-1.md`. Nothing else changes: no
renumbering, no wording elsewhere, no schema.

### C1: Key-word statement (new unnumbered section after the Abstract)

Before (lines 22–26):

```
ADP governs the envelope, not the content. It does not tell agents
what to think. It structures how they receive instructions and
return results.

---
```

After:

```
ADP governs the envelope, not the content. It does not tell agents
what to think. It structures how they receive instructions and
return results.

---

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and
"OPTIONAL" in this document are to be interpreted as described in
BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all
capitals, as shown here.

---
```

### C2: Binding strength of the validation tables (§7 introduction)

Before (lines 305–306):

```
Validation is a pure function. Envelope in, result out. No
network calls. No state. No model-specific logic.
```

After:

```
Validation is a pure function. Envelope in, result out. No
network calls. No state. No model-specific logic.

A validator MUST reject a dispatch envelope that fails any rule in
§7.1, and MUST reject a report envelope that fails any rule in §7.2.
```

### C3: Version and revision log

Header, line 7: `| **Version**  | 1.0.0 ...` → `| **Version**  | 1.0.1 ...`
(same column width). The **Date** field becomes the date the change
is applied.

Revision Log: append one row:

```
| <applied> | 1.0.1. Key words per BCP 14 (Conventions);     |
|            | §7.1/§7.2 rules bind validators (§7). ADP-A-001,|
|            | resolves ADP-D-012.                             |
```

---

## Version impact

**Patch** (1.0.0 → 1.0.1), under ADP-1 §9 "Spec clarification, no
schema Δ" and ADP-0 §7 "Editorial change, no normative effect" read
together with the reasoning below.

- C1 fixes the meaning of the ten uppercase key words the text already
  uses. Every one of them is already written in the RFC 2119 form, and
  no lowercase word changes meaning.
- C2 adds no rule. It states the force of the eighteen V- and R- rules
  that §7 already calls "Validation Rules". For every rule, the
  published schemas already reject envelopes that fail it, except
  V-01/R-01, where the schema pattern is wrong (ADP-D-009). This
  proposal does not change any schema's verdict on any envelope.
- So this is not "Validator tightening not required by existing text"
  (Major). The text already requires these checks; C2 makes that
  explicit.

---

## Conformance impact

- **Schemas:** no change. No envelope's verdict changes.
- **Conformance vectors:** `conformance/` does not exist. No vector is
  added, changed or flipped.
- **ADP-0 §5.5:** that clause says the first accepted proposal that
  "touches validation" must create `conformance/`. This proposal reads
  C2 as *not* touching validation, because it adds, removes and
  changes no rule and no verdict. If the maintainer reads it the other
  way, take Alternative A4.
- **Defect register (when applied):** ADP-D-012 is set to RESOLVED.
  ADP-D-008 and ADP-D-009 get a Notes line saying that the §7 tables
  now bind validators (C2). Their grades stay as filed, per ADP-0
  §4.5.

---

## Alternatives

| # | Option | Why not |
|---|--------|---------|
| A1 | Declare RFC 2119 only, without RFC 8174 | Lowercase "must" on lines 271 and 280 could then be read as normative. RFC 8174 makes only uppercase binding, which is what the text intends. |
| A2 | Put the statement in a numbered §1 and renumber | Renumbering breaks every § citation in DEFECTS.md, ADP-0 and this proposal. An unnumbered section changes nothing else. |
| A3 | Add a key word to each of the 18 table rows instead of C2 | Same effect with 18 edits instead of one sentence, and more chance of drift. |
| A4 | Split C2 into its own proposal that also creates `conformance/` (ADP-0 §5.5) | Viable. Choose it if C2 counts as touching validation. It leaves D-012 partly open until that proposal lands. |
| A5 | Also add "a validator MUST accept an envelope that passes every rule" | This would change verdicts where the schemas reject more than the rules (ADP-D-003, D-006, D-007). It belongs in the proposals for those defects. |

---

## Application (if ACCEPTED), per ADP-0 §5.4

1. **SPEC:** C1, C2 and C3 in one commit,
   `spec(adp-1): apply BCP 14 key words and bind validation rules — ADP-A-001, ADP-D-012`.
2. **CONFORMANCE:** none (see Conformance impact).
3. **SCHEMA:** none.
4. **IMPLEMENTATION:** none exists.
5. **INFORMATIVE:** none. `README.md` and `examples/` use no key words.
6. **REGISTER:** ADP-D-012 → RESOLVED, `Resolved by: ADP-A-001, <commit>`.
   Add Notes lines to ADP-D-008 and ADP-D-009.

---

## Decision

Pending. To be recorded by the maintainer (ADP-0 §5.3) as one line
beginning `ACCEPTED`, `REJECTED` or `DEFERRED`, with the date and the
reason.
