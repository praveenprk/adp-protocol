# ADP-A-002: Authorised automation types and per-session grants

| Field       | Value                                  |
|-------------|----------------------------------------|
| **ID**      | ADP-A-002                              |
| **Target**  | New document ADP-2 (`spec/ADP-2.md`)   |
| **Resolves**| No defect. Addresses a need (see Anchor) |
| **Bump**    | None for ADP-1. ADP-2 enters at 1.0.0, Draft |
| **Author**  | Contributor (agent-drafted, ADP-0 §8)  |
| **Drafted** | 2026-11-15                             |

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
> | Human-signed | `AT-CODEBASE-CREATE` | Bring a codebase into existence | Human-signed record, one per event |
> | | `AT-CODEBASE-DELETE` | Destroy a codebase | Human-signed record, one per event |
>
> The following are **not** automation types. No grant and no human-signed
> record confers them on an agent: a ruling, approving an RFC or SPEC,
> merging to a codebase's default branch, and issuing or changing a grant.
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
> - **G-9** `AT-CODEBASE-CREATE` and `AT-CODEBASE-DELETE` each REQUIRE a
>   human-signed record that names the codebase, is used for one event only,
>   and is not a grant.
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
- **ADP-2:** defines a new validator, so it touches validation. Under
  ADP-0 §5.5, the first accepted proposal that touches validation MUST
  create `conformance/`. If this proposal is accepted before any other
  proposal that touches validation, it carries that duty. It would then also
  define the vector format and add, for each of G-1 to G-7 and G-9, at least
  one vector that passes and one that fails. See question Q5.
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

| # | Question | Draft default |
|---|----------|---------------|
| Q1 | For codebase create and delete: may an agent carry out the act once a human has signed that one event, or must the human perform it? | The agent may carry it out with a per-event human-signed record (G-9). |
| Q2 | Should the human-signed tier also include data deletion, schema migration and security changes? | No. It is kept to the two events in the ruling. Raising the risk class of a work item is a factory matter, not part of ADP-2. |
| Q3 | Which signature mechanism: a signed git commit or tag, an SSH or GPG signature over the grant's sha256, or something else? | Deferred. G-6 and G-9 fix the field, not the algorithm. |
| Q4 | Does "codebase" include the hosted remote, so that creating a repository on a forge counts as a create? | Yes. Identity is the canonical remote URL (§1). |
| Q5 | Should this proposal create `conformance/` (ADP-0 §5.5), or should it wait for a validation proposal against ADP-1 to create it first? | Wait. ADP-2 vectors are added once `conformance/` exists. |

---

## Application (if ACCEPTED), per ADP-0 §5.4

1. **SPEC:** add `spec/ADP-2.md` with the text above, in one commit:
   `spec(adp-2): add Dispatch Authority — ADP-A-002`.
2. **CONFORMANCE:** ADP-2 vectors (G-1 to G-7 and G-9, one passing and one
   failing each), or `conformance/` itself, depending on Q5.
3. **SCHEMA:** `schema/grant.schema.json`.
4. **IMPLEMENTATION:** none exists.
5. **INFORMATIVE:** one row for ADP-2 in the `README.md` structure listing.
6. **REGISTER:** no defect to resolve.

---

## Decision

Pending. To be recorded by the maintainer (ADP-0 §5.3) as one line
beginning `ACCEPTED`, `REJECTED` or `DEFERRED`, with the date and the
reason.
