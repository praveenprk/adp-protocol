# ADP-A-002: Authorised automation types and per-session grants

| Field       | Value                                  |
|-------------|----------------------------------------|
| **ID**      | ADP-A-002                              |
| **Target**  | New document ADP-2 (`spec/ADP-2.md`)   |
| **Resolves**| No defect. Addresses a need (see Anchor) |
| **Bump**    | None for ADP-1. ADP-2 enters at 1.0.0, Draft |
| **Author**  | Contributor (agent-drafted, ADP-0 §8)  |
| **Drafted** | 2026-11-15                             |
| **Revised** | 2026-11-15, after maintainer review on PR #8 |

---

## Outcome and impact

**In one line:** ADP gains a contract for *who may ask an agent to do what*.
Codebase create and delete need a human signature, scaled to blast radius.
Everything else runs under a session grant that can never cover the agent's
own guardrails.

| Area | Effect when applied |
|------|---------------------|
| ADP-1 | None. No text, schema or verdict changes. |
| New normative text | `spec/ADP-2.md`: eight automation types, mapping of the ADP-1 keywords, the grant document, the codebase event classes with blast radius (R1 to R3), invariants G-1 to G-9. |
| Envelopes | ADP-1-only envelopes stay valid. An ADP-2-conformant dispatch also lists exactly one grant id in `dispatch.anchor`. |
| Human touch points | Ruling, RFC/SPEC approval and merge stay human-only, and no grant can confer them. Codebase create and delete need a human-signed record. The signer chooses its span, capped by blast radius: R1 up to a cycle, R2 up to a session, R3 one event only. |
| Guardrails | G-7: a grant's write scope never overlaps its `protected` paths. An agent cannot be granted write access to its own enforcement. |
| Conformance | Adds ADP-2 vectors only. `conformance/` and its format come from ADP-A-003 (Q5 option b), which must be applied first. |
| Risk | The validator proves only that the orchestrator *asked* within authority. Proving that the agent *acted* within it is the runtime's job (ADP-2 §6). |

Merging this proposal does not apply it. Application is a separate
change (see Application).

---

## Anchor

No defect is filed for this, so the proposal addresses a need (ADP-0 §5.1).

**Need.** The maintainer has ruled that creating or deleting a codebase is a
human-signed event only. Everything else an agent does runs under a
per-session grant, limited to authorised automation types. The example given
is a chat platform that calls an MCP server, which then works in a codebase.
The maintainer also gives rulings and approves RFCs and SPECs before
execution, and merges at the end. Between those two points, execution is
automated.

ADP-1 has no place to express any of this. Evidence at `0ff059d` (current
`main`):

```
$ sed -n 46,58p spec/ADP-1.md
ADP governs:
- The structure of a dispatch envelope (orchestrator → agent)
- The structure of a report envelope (agent → orchestrator)
- A fixed keyword vocabulary for work item directives
- Compression tiers for judgment-density-indexed verbosity
- A validation contract for envelope conformance

ADP does not govern:
- Prompt engineering technique
- Model selection
- Agent internal reasoning
- Transport mechanism
- Application-layer semantics of work items

$ grep -n -iE 'authori|grant|permission|human' spec/ADP-1.md
(no output, exit 1)

$ grep -n '"create", "modify"' schema/dispatch.schema.json
125:          "enum": ["create", "modify"],
```

So the protocol cannot say whether an orchestrator was *allowed* to issue a
dispatch, and it has no way to tell a codebase create apart from any other
`PRODUCE`. A codebase delete cannot be expressed at all.

The chain in the example crosses three systems: chat platform, MCP server,
codebase. If each one keeps a private rule, the rules do not compose, so this
needs a shared contract.

---

## Change

### Amend versus new document (ADP-0 §5.2)

**New document: ADP-2, Dispatch Authority.** Authority is a new contract with
its own invariants: scope, delegation that only narrows, and a human-signed
root. It does not correct or extend the ADP-1 envelope. **ADP-1 is not
changed** in its text, its schemas or its verdicts.

### Before

No text. Authority is outside ADP-1 §2 Scope (evidence above).

### After: `spec/ADP-2.md`

The text below becomes the normative body of `spec/ADP-2.md`, with the
standard header table (ID ADP-2, Version 1.0.0, Status Draft, Apache 2.0)
and a Revision Log. ADP-2 declares BCP 14 key words in its own Conventions
section, in the same words ADP-A-001 proposes for ADP-1, so the two documents
read the same way whichever is applied first.

---

> #### Conventions
>
> The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
> "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and
> "OPTIONAL" in this document are to be interpreted as described in
> BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all
> capitals, as shown here.
>
> #### 1. Terms
>
> - **Codebase:** a version-control repository. It is identified by its
>   canonical remote URL, or by its root path on one host if it has no remote.
> - **Automation type:** a class of effect an agent can cause. The set of
>   types is closed (§2).
> - **Grant:** a document, separate from any dispatch envelope, that
>   authorises a set of automation types over a scope for one session.
> - **Human-signed record:** a record of an act by a named human, carrying a
>   signature that can be checked against that human's key.
>
> #### 2. Automation types
>
> | Tier | Type | Effect | Authority |
> |---|---|---|---|
> | Implicit | `AT-REPORT` | Communicate with the orchestrator only | Any valid dispatch |
> | Grantable | `AT-READ` | Read named paths or resources | Per-session grant |
> | | `AT-VERIFY` | Run checks (tests, linters, CI status) without changing tracked state | Per-session grant |
> | | `AT-WRITE` | Create or modify files inside an existing codebase | Per-session grant |
> | | `AT-VCS` | Commit, push to a non-default branch, open a pull request | Per-session grant |
> | | `AT-TOOL` | Call an external tool or service, such as an MCP server | Per-session grant |
> | Human-signed | `AT-CODEBASE-CREATE` | Bring a codebase into existence (§2.1) | Human-signed record, span by radius (G-9) |
> | | `AT-CODEBASE-DELETE` | Archive or destroy a codebase (§2.1) | Human-signed record, span by radius (G-9) |
>
> The following are **not** automation types. No grant and no human-signed
> record confers them on an agent: a ruling, approving an RFC or SPEC,
> merging to a codebase's default branch, and issuing or changing a grant.
>
> ##### 2.1 Codebase events and blast radius
>
> `AT-CODEBASE-CREATE` and `AT-CODEBASE-DELETE` each cover the event classes
> below. Each class has a blast radius, R1 (contained) to R3 (irreversible or
> public).
>
> | Class | Type | Event | Reversible | Radius |
> |---|---|---|---|---|
> | `CREATE-SCRATCH` | create | New codebase under a declared sandbox root, with no remote | Yes | R1 |
> | `CREATE-PRIVATE` | create | New codebase with a private remote inside a declared namespace | Yes | R2 |
> | `CREATE-PUBLIC` | create | New codebase that is public or outside every declared namespace, including a fork | No. Once public, content can be copied | R3 |
> | `DELETE-SCRATCH` | delete | Delete a `CREATE-SCRATCH` codebase made in the same cycle | Not needed. Nothing else depends on it | R1 |
> | `ARCHIVE` | delete | Make a codebase read-only, keeping its history | Yes | R2 |
> | `DELETE` | delete | Permanently remove a codebase, or the only copy of any of its commits | No | R3 |
>
> These are **not** codebase events: adding or removing a worktree, creating
> or deleting a non-default branch, and cloning an existing codebase (same
> identity). They fall under `AT-VCS` or `AT-WRITE`. Deleting a local clone
> is a `DELETE` if the clone holds commits that exist on no other copy.
>
> A **cycle** is the span from the maintainer's approval of an RFC and SPEC
> to the pull request that work produces. A **session** is one agent session
> under one grant.
>
> #### 3. Keyword mapping
>
> A dispatch *implies* the union of the types that its fields and work items
> map to below.
>
> | ADP-1 element | Implies | Notes |
> |---|---|---|
> | `READ`, `context.read[]` | `AT-READ` | Each `path` MUST match `scope.read`. |
> | `IGNORE`, `context.ignore[]` | none | Narrows what the agent reads. Never needs authority. |
> | `CONFIRM` | `AT-READ`; also `AT-VERIFY` if checking the condition requires running anything | Asserts. Never writes. |
> | `PRODUCE`, `produce[]` | `AT-WRITE` | Each `path` MUST match `scope.write`. A `create` at the root of a new codebase implies `AT-CODEBASE-CREATE` instead. |
> | `BIND` | `AT-WRITE` | A bound decision is a written record. "Irreversible" in ADP-1 §3.1 locks the decision. It does not destroy anything. |
> | `SURFACE`, `DEFER`, `REPORT`, `report[]` | `AT-REPORT` | |
> | `EXIT`, `exit[]` | `AT-REPORT`; also `AT-VERIFY` if checking the condition requires running anything | |
> | `ANCHOR`, `dispatch.anchor[]` | none | Carries the grant reference (§4.1). |
> | *(no element)* | `AT-VCS`, `AT-TOOL` | Cannot be inferred from an ADP-1 envelope. Declared in the grant and enforced by the runtime (§6). |
> | *(no element)* | `AT-CODEBASE-DELETE` | ADP-1 has no delete action. A codebase delete cannot be dispatched under ADP-1. |
>
> `SOURCE` is left out. Whether it is a keyword is open as ADP-D-001 and
> ADP-D-002. Either way it implies nothing.
>
> #### 4. Grant document
>
> ```yaml
> adp_grant_version: "1.0.0"
> grant:
>   id: string              # unique, never reused
>   session: string         # the session this grant is bound to
>   issuer: string          # orchestrator identity
>   root:                   # required unless parent is present
>     kind: string          # "approval" | "ruling"
>     ref: [string]         # e.g. the approved RFC and SPEC
>     signed_by: string
>     signature: string
>   parent: string          # id of the delegating grant, if any
>   expires_at: string      # RFC 3339 UTC
>   types: [string]         # grantable types only (§2)
>   scope:
>     codebases: [string]
>     read: [string]        # globs
>     write: [string]       # globs
>     branches: [string]    # patterns; never a default branch
>     tools: [string]       # "<server>/<tool>"
>   protected: [string]     # globs; see G-7
> ```
>
> ##### 4.1 Binding a dispatch to a grant
>
> A dispatch is bound to a grant by listing the grant `id` in
> `dispatch.anchor`. ADP-1 already requires that field and defines it as the
> "traceable governing reference", so the binding needs no change to ADP-1.
>
> #### 5. Invariants
>
> - **G-1** A dispatch MUST list exactly one grant id in `dispatch.anchor`.
> - **G-2** `grant.types` MUST contain only grantable types. A grant that
>   lists a human-signed type, or anything §2 says is not an automation type,
>   is invalid.
> - **G-3** The types a dispatch implies (§3) MUST be a subset of the
>   `types` of the grant it lists.
> - **G-4** Every `context.read[].path` MUST match `scope.read`. Every
>   `produce[].path` MUST match `scope.write`.
> - **G-5** Delegation only narrows. In a child grant, `types` and each
>   `scope` list MUST be subsets of the parent's, `protected` MUST be a
>   superset of the parent's, and `expires_at` MUST NOT be later than the
>   parent's.
> - **G-6** Following `parent` links MUST reach, within 5 hops, a grant
>   whose `root` is a human-signed record.
> - **G-7** `scope.write` MUST NOT overlap `protected`. `protected` MUST
>   cover at least the paths where grants are stored and the paths of the
>   enforcing runtime, such as hooks, guards, routing tables and agent
>   contracts. An agent is never granted write access to its own guardrails.
> - **G-8** A grant ends at `expires_at` or when its session ends,
>   whichever comes first. A grant is never renewed. Continuing requires a
>   new grant with a new root.
> - **G-9** An agent MAY carry out a codebase event (§2.1) only under a
>   human-signed record that is not a grant. The record MUST state:
>   - `classes`: the event classes it covers;
>   - `boundary`: the sandbox roots, namespaces or exact codebases it covers,
>     plus an optional maximum event count;
>   - `span`: `event`, `session` or `cycle`.
>
>   `span` is REQUIRED and has no default. The human signer chooses it,
>   within the widest span allowed for the highest radius among `classes`:
>
>   | Radius | Allowed `span` |
>   |---|---|
>   | R1 | `event`, `session`, `cycle` |
>   | R2 | `event`, `session` |
>   | R3 | `event` only |
>
>   An `event` record names exactly one codebase and is used once. A record
>   whose `span` is wider than its radius allows is invalid.
>
> #### 6. Validation and enforcement
>
> - **Validator.** `validate(dispatch, grant_chain)` is a pure function,
>   like ADP-1 §7. It checks G-1 to G-7 and G-9 against the documents it is
>   given. It checks that a signature field is present and well-formed. It
>   verifies a signature only when the caller supplies the key.
> - **Runtime.** Everything that cannot be seen in the documents is the
>   job of the executing system: `AT-VCS`, `AT-TOOL`, G-8, and what the agent
>   actually does on disk. A valid dispatch proves that the orchestrator
>   *asked* within its authority. It does not prove that the agent *acted*
>   within it.

---

## Version impact

- **ADP-1:** none. No text, schema or verdict changes. No row of ADP-0 §7
  applies.
- **ADP-2:** a new document. It enters as Draft at 1.0.0 and has its own
  version line. Later changes to it follow ADP-0 §7.
- **ADP-0:** none. `spec/ADP-2.md` is Normative under the existing §3 row
  `spec/ADP-N.md (N ≥ 1)`.

---

## Conformance impact

- **ADP-1 vectors:** none. `conformance/` does not exist yet.
- **ADP-2:** defines a new validator, so it touches validation. The
  ADP-A-001 Decision (`d9f7255`) named this proposal as the one that
  creates `conformance/` (ADP-0 §5.5). The maintainer has since chosen Q5
  option (b): **ADP-A-003** (Conformance suite format) creates
  `conformance/` and its format. This proposal adds only the ADP-2 vectors,
  at least one passing and one failing for each of G-1 to G-7 and G-9, in
  the ADP-A-003 format.
- **Dependency:** ADP-A-003 MUST be applied before step 2 of this
  proposal's application. Accepting this proposal does not need to wait for
  ADP-A-003.
- **Schemas:** a `schema/grant.schema.json` would be added at ADP-0 §5.4
  step 3. The CI job `schema` already requires an ACCEPTED proposal for any
  change under `schema/`.

---

## Alternatives

| # | Option | Why not |
|---|--------|---------|
| A1 | Amend ADP-1 with an optional `dispatch.grant` field (minor bump) | Authority is a new contract (ADP-0 §5.2). It is also blocked by ADP-D-003: the published schemas reject unknown fields, so a 1.1.0 envelope with a new field fails today. |
| A2 | Carry the grant as `x-` metadata on the envelope | Blocked by ADP-D-006, which leaves no envelope-level metadata slot. And ADP-1 §3.5 says validators MUST *ignore* unknown `x-` fields, so an authority check carried there can never be enforced. |
| A3 | Leave authority to each implementation | The maintainer's example crosses three systems. Private rules do not compose across hops. |
| A4 | Add a keyword (`AUTHORIZE`, `DELETE`) | Breaks the keyword freeze in ADP-1 §3.5 and forces a major bump. |
| A5 | Treat `BIND` as human-signed because ADP-1 calls it irreversible | `BIND` locks a decision and destroys nothing. The maintainer reserved human signature for codebase create and delete only. Widening that is question Q2, not a side effect of one word. |
| A6 | Embed the grant inline in each dispatch instead of referencing it | One grant covers many dispatches in a session. Embedding it would copy it into every envelope, which goes against the ADP-1 §8 deduplication rule. It would also let a dispatch edit its own grant. |

---

## Questions for the maintainer

Answers come from the maintainer's review on PR #8. They are recorded here so
the proposal reads complete. They are not the Decision (ADP-0 §5.3).

| # | Question | Maintainer answer | Effect on this draft |
|---|----------|-------------------|----------------------|
| Q1 | For codebase create and delete: may an agent carry out the act once a human has signed, and at what granularity? | "What kind of creation and deletion? There could be a boundary for smaller blast radius. Agent MAY carry it out with a per-event or per-session per-cycle human sign record." | Added §2.1 (six event classes, radius R1 to R3, cycle and session defined). G-9 now carries `classes`, `boundary` and `span`. |
| Q1a | How wide may an R2 record's span be? | "Configurable, up to session. Let the user decide. Choose your best recommendation." | Settled. In G-9, R2 allows `event` or `session`, and `span` is required with no default. Recommendation below. |
| Q2 | Should the human-signed tier also include data deletion, schema migration and security changes? | "Correct. Don't raise risk class." | Settled. Kept to the two events. |
| Q3 | Which signature mechanism? | "Field first, algo later." | Settled. G-6 and G-9 fix the fields only. |
| Q4 | Does "codebase" include the hosted remote? | "Go with best recommendation." | Settled as drafted: yes. Recommendation below. |
| Q5 | Should this proposal create `conformance/`? | "Option (b)." | Settled. ADP-A-003 creates `conformance/` and its format. This proposal adds only ADP-2 vectors. |

### Recommendation for Q1a: R2 span

`span` stays a required field with no default. A default would sign
something the human did not choose. The recommended choice, written into
ADP-2 as informative guidance:

| Class | Recommended `span` | Why |
|---|---|---|
| `CREATE-PRIVATE` | `session` | A session usually sets up one piece of work and may need a scratch remote more than once. The repository stays private and can be deleted. |
| `ARCHIVE` | `event` | It acts on a codebase that already exists and has value. One codebase, one signature. |

`cycle` is not allowed for R2. A cycle can run for several sessions and
several days, and a private remote created early in it would outlive the
human's view of the work.

### Recommendation for Q4: hosted remote

Yes. Creating a repository on a forge (GitHub, GitLab, etc.) is a codebase
create. Deleting or archiving one is a codebase delete. A codebase's
identity is its canonical remote URL. A codebase with no remote is
identified by host and root path (§1). Reasons:

- Most of the blast radius is on the forge, not on disk. Visibility,
  forks, CI secrets and webhooks all live there.
- The maintainer's example (chat platform → MCP server → codebase) reaches
  codebases through forge APIs, so a rule that only covers the local
  filesystem would miss the main path.
- One identity per codebase lets a single signed record cover the local
  clone and the remote together, with no double signing.

### Q5: context (as given before the answer)

- **What `conformance/` is.** A directory of test vectors: envelopes, each
  with its expected verdict (pass or fail) and the rule it exercises. ADP-0
  §5.4 step 2 needs it so that every changed rule has one passing and one
  failing vector. ADP-0 §5.5 forbids any implementation from claiming ADP
  conformance until it exists.
- **Why it lands here.** ADP-0 §5.5 says the first accepted proposal that
  touches validation creates it. The ADP-A-001 Decision (`d9f7255`) reads
  that A-001 does not touch validation, and states that `conformance/` "is
  created by ADP-A-002". ADP-2 defines a new validator, so it does touch
  validation.
- **What creating it costs here.** This proposal would also have to define
  the vector format: file layout, how the expected verdict is written, and
  how a vector names its rule and spec version. ADP-0 §5.1 says a proposal
  MUST NOT bundle unrelated changes, and a suite format for all of ADP is a
  separate concern from authority.
- **Options:**
  - **(a)** A-002 defines the format and creates `conformance/` with its
    G-1 to G-9 vectors. This matches the A-001 Decision text, but makes
    A-002 a bundle.
  - **(b)** A small separate proposal, ADP-A-003 *Conformance suite
    format*, creates `conformance/` and the format, plus the first vectors
    for ADP-1 §7. A-002 then adds only its own vectors. This respects §5.1,
    but needs the maintainer to say so, because the A-001 Decision names
    A-002.
- **Draft recommendation:** (b). The format is shared by every later
  proposal, so it should be reviewed on its own.

---

## Application (if ACCEPTED), per ADP-0 §5.4

1. **SPEC:** add `spec/ADP-2.md` with the text above, in one commit:
   `spec(adp-2): add Dispatch Authority — ADP-A-002`.
2. **CONFORMANCE:** ADP-2 vectors (G-1 to G-7 and G-9, one passing and one
   failing each), in the ADP-A-003 format. ADP-A-003 must be applied first
   (Q5).
3. **SCHEMA:** `schema/grant.schema.json`.
4. **IMPLEMENTATION:** none exists.
5. **INFORMATIVE:** one row for ADP-2 in the `README.md` structure listing.
6. **REGISTER:** no defect to resolve.

---

## Decision

Pending. To be recorded by the maintainer (ADP-0 §5.3) as one line
beginning `ACCEPTED`, `REJECTED` or `DEFERRED`, with the date and the
reason.
