# ADP-0: Specification Governance and Change Process

| Field        | Value                                   |
|--------------|-----------------------------------------|
| **ID**       | ADP-0                                   |
| **Title**    | Specification Governance and Change Process |
| **Version**  | 1.0.0                                   |
| **Status**   | Draft                                   |
| **License**  | Apache 2.0                              |
| **Date**     | 2026-11-15                              |
| **Governs**  | All ADP-N documents, `schema/`, `conformance/`, `examples/`, `DEFECTS.md` |

---

## Abstract

ADP-0 defines how the Agent Dispatch Protocol changes. It defines
which artifacts are normative, how defects are recorded, how
changes are proposed and accepted, the order in which an accepted
change is applied, and how a change maps to a version bump.

ADP-0 governs process, not protocol. It defines no keyword, field,
or validation rule of ADP itself.

The key words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY in this
document are to be interpreted as described in RFC 2119.

---

## 1. Motivation

ADP-1 declares a frozen keyword set and a semver contract, but
defines no mechanism by which its own text may be corrected or
extended. A frozen standard with no governed change path has two
failure modes: silent edits that break the freeze, or permanent
defects that nobody is allowed to fix. Both have occurred in
practice:

- The repository's `spec/ADP-1.md` held README content from the
  initial commit until restoration (commit `a9e1a4b`), undetected.
- The restored ADP-1 text contradicts itself and its schemas in at
  least eleven places, with no register in which to record them.

ADP-0 closes that gap.

---

## 2. Bootstrap

No process exists before ADP-0. ADP-0 is therefore adopted directly
by the maintainer (§8) without a prior proposal. This is the only
document in the ADP corpus permitted to enter without a proposal.
Every subsequent change to ADP-0 itself follows §5.

---

## 3. Artifact Classes

Every file in the repository belongs to exactly one class.

| Class           | Artifacts                                   | Binding |
|-----------------|---------------------------------------------|---------|
| **Normative**   | `spec/ADP-N.md` (N ≥ 1) text not marked     | Yes     |
|                 | informative; `schema/*.json`;               |         |
|                 | `conformance/` vectors                      |         |
| **Informative** | Sections of `spec/ADP-N.md` whose heading   | No      |
|                 | carries the suffix `(Informative)`;         |         |
|                 | `examples/`; `README.md`                    |         |
| **Process**     | `spec/ADP-0.md`; `DEFECTS.md`;              | On the  |
|                 | `proposals/`                                | process |
| **Legal**       | `LICENSE`                                   | Legal   |

### 3.1 Default classification

Spec text is normative unless explicitly marked informative. A
section becomes informative only through an accepted proposal that
adds the `(Informative)` suffix. Classification is never inferred
from wording such as "guidance" or "example".

### 3.2 Precedence

When normative artifacts disagree:

1. Spec text takes precedence over `schema/` and `conformance/`.
   A schema or vector that disagrees with unambiguous spec text is
   a defect in the schema or vector.
2. Where spec text contradicts itself, no artifact takes precedence.
   The contradiction is a defect and is resolved only by an
   accepted proposal (§5). Implementations MUST NOT pick a reading
   and claim conformance on that basis.
3. Informative artifacts never take precedence over normative ones.
   An informative artifact that contradicts normative text is a
   defect in the informative artifact.

---

## 4. Defect Register

### 4.1 Location and identity

All known defects are recorded in `DEFECTS.md` at the repository
root. Each defect has a permanent identifier `ADP-D-NNN`,
zero-padded, assigned sequentially. Identifiers are never reused.

### 4.2 Entry format

```
### ADP-D-NNN
Artifact    : <class> — <file> <section | rule | line>
Says        : <the governing normative statement, quoted or cited>
Does        : <what the artifact actually says or accepts>
Evidence    : <reproducible check, at commit <hash>>
Severity    : CRITICAL | HIGH | MEDIUM | LOW
Status      : OPEN | RESOLVED | WONTFIX | SUPERSEDED
Resolved by : <ADP-A-NNN and commit hash, or —>
Notes       : <optional>
```

### 4.3 Evidence rule

Every entry MUST carry evidence verifiable against a named commit:
a quoted line with its location, or a command whose output
demonstrates the defect. An entry whose evidence cannot be
reproduced at the named commit MUST NOT be filed. A defect
described from memory, summary, or another conversation is not
evidence.

### 4.4 Severity

Severity is determined by the clause violated and the artifact
class, not by judgment of impact:

| Violated clause / class                          | Severity  |
|--------------------------------------------------|-----------|
| Normative MUST, or freeze (§3.5 of ADP-1)        | HIGH      |
| Normative MUST where conformant envelopes are    | CRITICAL  |
| rejected or non-conformant envelopes accepted    |           |
| Normative SHOULD                                 | MEDIUM    |
| Internal contradiction in normative text         | HIGH      |
| Informative artifact contradicts normative text  | LOW       |
| Informative artifact internally inconsistent     | LOW       |

A grade that departs from this table MUST state the reason in
`Notes`. Departures without a stated reason are themselves defects.

### 4.5 Append-only

Entries are never deleted. Only `Status`, `Resolved by`, and
`Notes` change after filing. A mistaken entry is closed as
`WONTFIX` with the reason, not removed. A defect replaced by a
broader one is closed as `SUPERSEDED` naming its successor.

---

## 5. Change Process

### 5.1 Proposal

Every change to a normative or process artifact requires a proposal
at `proposals/ADP-A-NNN-<slug>.md`. A proposal MUST contain:

- **Anchor** — the ADP-D-NNN entries it resolves, or the need it
  addresses if no defect exists.
- **Change** — the exact normative text before and after, per
  affected artifact.
- **Version impact** — the bump class per §7, with reasoning.
- **Conformance impact** — every conformance vector added, changed,
  or whose verdict flips.
- **Alternatives** — options considered and why each was rejected.
- **Decision** — empty until §5.3.

One proposal MAY resolve several defects when they share a root
cause. A proposal MUST NOT bundle unrelated changes.

### 5.2 Amend versus new document

- **Amend ADP-N** when the change corrects, clarifies, or extends
  the contract ADP-N already defines: same envelope, same keyword
  set, same validation contract.
- **Create ADP-M** when the change defines a new contract with its
  own invariants — for example, a normative transport binding or a
  negotiation protocol.

A new document MUST NOT be created to avoid amending an existing
one. An existing document MUST NOT be amended to avoid defining a
new contract.

### 5.3 Decision

The maintainer (§8) records one of `ACCEPTED`, `REJECTED`, or
`DEFERRED` in the proposal's Decision section, with date and
reason. Only `ACCEPTED` proposals may be applied. Agents MAY author
proposals. Agents MUST NOT record a decision.

### 5.4 Application order

An accepted proposal is applied in this order. Each step is
complete before the next begins.

1. **SPEC** — normative spec text amended; revision log entry added
   naming the proposal.
2. **CONFORMANCE** — `conformance/` vectors added or updated so that
   each changed rule has at least one passing and one failing
   vector.
3. **SCHEMA** — `schema/` updated until every conformance vector
   yields its expected verdict.
4. **IMPLEMENTATION** — any reference implementation updated until
   every conformance vector yields its expected verdict.
5. **INFORMATIVE** — `examples/` and `README.md` brought into line.
6. **REGISTER** — resolved `DEFECTS.md` entries set to `RESOLVED`
   with the proposal ID and commit hash.

Steps 1–3 SHOULD land in a single commit. A commit that changes
`schema/` without a corresponding accepted proposal is
non-conformant to ADP-0.

### 5.5 Conformance suite prerequisite

Until `conformance/` exists, step 2 cannot be satisfied. The first
proposal accepted under ADP-0 that touches validation MUST create
`conformance/` with its format defined in that proposal. No
reference implementation may claim ADP conformance before
`conformance/` exists.

---

## 6. Errata

An **erratum** is a change that does either of the following, and
nothing else:

- (a) brings a schema, vector, or informative artifact into
  agreement with existing unambiguous normative spec text; or
- (b) resolves an internal contradiction in normative spec text in
  a way that does not change the verdict of the published schema
  on any envelope.

Errata still require a proposal (§5.1). Errata take a patch bump
(§7), even when the corrected artifact accepts or rejects envelopes
differently afterwards, because the spec already required the
corrected behavior.

A change that meets neither (a) nor (b) is not an erratum, however
small.

---

## 7. Version Impact

ADP-1 §9 defines the semver contract for the protocol. ADP-0 adds
the following classification rules for proposals:

| Change                                              | Bump  |
|-----------------------------------------------------|-------|
| Erratum per §6                                      | Patch |
| Editorial change, no normative effect               | Patch |
| Section reclassified informative (§3.1)             | Patch |
| New optional field; validator relaxation not        | Minor |
| required by existing text                           |       |
| Keyword addition or removal (not an erratum)        | Major |
| Validator tightening not required by existing text  | Major |
| Envelope schema breaking change                     | Major |

Process documents (ADP-0) carry their own version, independent of
the protocol version.

---

## 8. Roles

| Role          | Holder               | Authority                         |
|---------------|----------------------|-----------------------------------|
| Maintainer    | Repository owner     | Records decisions (§5.3). Files,  |
|               | (`praveenprk`)       | grades, and closes defects.       |
| Contributor   | Any human or agent   | Files defects with evidence.      |
|               |                      | Authors proposals.                |

There is one maintainer. Introducing additional maintainers, a
review quorum, or external standards-body participation is a change
to ADP-0 and follows §5.

---

## 9. Repository Layout

```
adp-protocol/
├── spec/
│   ├── ADP-0.md          # this document (process)
│   └── ADP-1.md          # protocol specification
├── proposals/            # ADP-A-NNN-<slug>.md
├── conformance/          # created by first validation proposal (§5.5)
├── schema/               # normative JSON Schemas
├── examples/             # informative
├── DEFECTS.md            # defect register
├── README.md             # informative
└── LICENSE
```

---

## 10. What ADP-0 Is Not

- Not a contribution guide. Workflow for pull requests, commit
  message format, and code style belong in `CONTRIBUTING.md`.
- Not a code of conduct.
- Not part of the protocol. An envelope's conformance never depends
  on ADP-0.

---

## Revision Log

| Date       | Change                                          |
|------------|-------------------------------------------------|
| 2026-11-15 | Initial draft. Artifact classes and precedence, |
|            | defect register with evidence rule and fixed    |
|            | severity table, proposal process, application   |
|            | order SPEC → CONFORMANCE → SCHEMA → IMPL,       |
|            | errata definition, version impact table,        |
|            | single-maintainer roles. Bootstrapped per §2.   |