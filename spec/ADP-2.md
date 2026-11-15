# ADP-2: Dispatch Authority

| Field        | Value                                   |
|--------------|-----------------------------------------|
| **ID**       | ADP-2                                   |
| **Title**    | Dispatch Authority                      |
| **Version**  | 1.0.0                                   |
| **Status**   | Draft                                   |
| **License**  | Apache 2.0                              |
| **Date**     | 2026-11-16                              |

---

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and
"OPTIONAL" in this document are to be interpreted as described in
BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all
capitals, as shown here.

---

## 1. Terms

- **Codebase:** a version-control repository. It is identified by its
  canonical remote URL, or by its root path on one host if it has no remote.
- **Automation type:** a class of effect an agent can cause. The set of
  types is closed (§2).
- **Grant:** a document, separate from any dispatch envelope, that
  authorises a set of automation types over a scope for one session.
- **Human-signed record:** a record of an act by a named human, carrying a
  signature that can be checked against that human's key.

---

## 2. Automation types

| Tier | Type | Effect | Authority |
|---|---|---|---|
| Implicit | `AT-REPORT` | Communicate with the orchestrator only | Any valid dispatch |
| Grantable | `AT-READ` | Read named paths or resources | Per-session grant |
| | `AT-VERIFY` | Run checks (tests, linters, CI status) without changing tracked state | Per-session grant |
| | `AT-WRITE` | Create or modify files inside an existing codebase | Per-session grant |
| | `AT-VCS` | Commit, push to a non-default branch, open a pull request | Per-session grant |
| | `AT-TOOL` | Call an external tool or service, such as an MCP server | Per-session grant |
| Human-signed | `AT-CODEBASE-CREATE` | Bring a codebase into existence (§2.1) | Human-signed record, span by radius (G-9) |
| | `AT-CODEBASE-DELETE` | Archive or destroy a codebase (§2.1) | Human-signed record, span by radius (G-9) |

The following are **not** automation types. No grant and no human-signed
record confers them on an agent: a ruling, approving an RFC or SPEC,
merging to a codebase's default branch, and issuing or changing a grant.

### 2.1 Codebase events and blast radius

`AT-CODEBASE-CREATE` and `AT-CODEBASE-DELETE` each cover the event classes
below. Each class has a blast radius, R1 (contained) to R3 (irreversible or
public).

| Class | Type | Event | Reversible | Radius |
|---|---|---|---|---|
| `CREATE-SCRATCH` | create | New codebase under a declared sandbox root, with no remote | Yes | R1 |
| `CREATE-PRIVATE` | create | New codebase with a private remote inside a declared namespace | Yes | R2 |
| `CREATE-PUBLIC` | create | New codebase that is public or outside every declared namespace, including a fork | No. Once public, content can be copied | R3 |
| `DELETE-SCRATCH` | delete | Delete a `CREATE-SCRATCH` codebase made in the same cycle | Not needed. Nothing else depends on it | R1 |
| `ARCHIVE` | delete | Make a codebase read-only, keeping its history | Yes | R2 |
| `DELETE` | delete | Permanently remove a codebase, or the only copy of any of its commits | No | R3 |

These are **not** codebase events: adding or removing a worktree, creating
or deleting a non-default branch, and cloning an existing codebase (same
identity). They fall under `AT-VCS` or `AT-WRITE`. Deleting a local clone
is a `DELETE` if the clone holds commits that exist on no other copy.

A **cycle** is the span from the maintainer's approval of an RFC and SPEC
to the pull request that work produces. A **session** is one agent session
under one grant.

---

## 3. Keyword mapping

A dispatch *implies* the union of the types that its fields and work items
map to below.

| ADP-1 element | Implies | Notes |
|---|---|---|
| `READ`, `context.read[]` | `AT-READ` | Each `path` MUST match `scope.read`. |
| `IGNORE`, `context.ignore[]` | none | Narrows what the agent reads. Never needs authority. |
| `CONFIRM` | `AT-READ`; also `AT-VERIFY` if checking the condition requires running anything | Asserts. Never writes. |
| `PRODUCE`, `produce[]` | `AT-WRITE` | Each `path` MUST match `scope.write`. A `create` at the root of a new codebase implies `AT-CODEBASE-CREATE` instead. |
| `BIND` | `AT-WRITE` | A bound decision is a written record. "Irreversible" in ADP-1 §3.1 locks the decision. It does not destroy anything. |
| `SURFACE`, `DEFER`, `REPORT`, `report[]` | `AT-REPORT` | |
| `EXIT`, `exit[]` | `AT-REPORT`; also `AT-VERIFY` if checking the condition requires running anything | |
| `ANCHOR`, `dispatch.anchor[]` | none | Carries the grant reference (§4.1). |
| *(no element)* | `AT-VCS`, `AT-TOOL` | Cannot be inferred from an ADP-1 envelope. Declared in the grant and enforced by the runtime (§6). |
| *(no element)* | `AT-CODEBASE-DELETE` | ADP-1 has no delete action. A codebase delete cannot be dispatched under ADP-1. |

`SOURCE` is left out. Whether it is a keyword is open as ADP-D-001 and
ADP-D-002. Either way it implies nothing.

---

## 4. Grant document

```yaml
adp_grant_version: "1.0.0"
grant:
  id: string              # unique, never reused
  session: string         # the session this grant is bound to
  issuer: string          # orchestrator identity
  root:                   # required unless parent is present
    kind: string          # "approval" | "ruling"
    ref: [string]         # e.g. the approved RFC and SPEC
    signed_by: string
    signature: string
  parent: string          # id of the delegating grant, if any
  expires_at: string      # RFC 3339 UTC
  types: [string]         # grantable types only (§2)
  scope:
    codebases: [string]
    read: [string]        # globs
    write: [string]       # globs
    branches: [string]    # patterns; never a default branch
    tools: [string]       # "<server>/<tool>"
  protected: [string]     # globs; see G-7
```

### 4.1 Binding a dispatch to a grant

A dispatch is bound to a grant by listing the grant `id` in
`dispatch.anchor`. ADP-1 already requires that field and defines it as the
"traceable governing reference", so the binding needs no change to ADP-1.

---

## 5. Invariants

- **G-1** A dispatch MUST list exactly one grant id in `dispatch.anchor`.
- **G-2** `grant.types` MUST contain only grantable types. A grant that
  lists a human-signed type, or anything §2 says is not an automation type,
  is invalid.
- **G-3** The types a dispatch implies (§3) MUST be a subset of the
  `types` of the grant it lists.
- **G-4** Every `context.read[].path` MUST match `scope.read`. Every
  `produce[].path` MUST match `scope.write`.
- **G-5** Delegation only narrows. In a child grant, `types` and each
  `scope` list MUST be subsets of the parent's, `protected` MUST be a
  superset of the parent's, and `expires_at` MUST NOT be later than the
  parent's.
- **G-6** Following `parent` links MUST reach, within 5 hops, a grant
  whose `root` is a human-signed record.
- **G-7** `scope.write` MUST NOT overlap `protected`. `protected` MUST
  cover at least the paths where grants are stored and the paths of the
  enforcing runtime, such as hooks, guards, routing tables and agent
  contracts. An agent is never granted write access to its own guardrails.
- **G-8** A grant ends at `expires_at` or when its session ends,
  whichever comes first. A grant is never renewed. Continuing requires a
  new grant with a new root.
- **G-9** An agent MAY carry out a codebase event (§2.1) only under a
  human-signed record that is not a grant. The record MUST state:
  - `classes`: the event classes it covers;
  - `boundary`: the sandbox roots, namespaces or exact codebases it covers,
    plus an optional maximum event count;
  - `span`: `event`, `session` or `cycle`.

  `span` is REQUIRED and has no default. The human signer chooses it,
  within the widest span allowed for the highest radius among `classes`:

  | Radius | Allowed `span` |
  |---|---|
  | R1 | `event`, `session`, `cycle` |
  | R2 | `event`, `session` |
  | R3 | `event` only |

  An `event` record names exactly one codebase and is used once. A record
  whose `span` is wider than its radius allows is invalid.

---

## 6. Validation and enforcement

- **Validator.** `validate(dispatch, grant_chain)` is a pure function,
  like ADP-1 §7. It checks G-1 to G-7 and G-9 against the documents it is
  given. It checks that a signature field is present and well-formed. It
  verifies a signature only when the caller supplies the key.
- **Runtime.** Everything that cannot be seen in the documents is the
  job of the executing system: `AT-VCS`, `AT-TOOL`, G-8, and what the agent
  actually does on disk. A valid dispatch proves that the orchestrator
  *asked* within its authority. It does not prove that the agent *acted*
  within it.

---

## Recommended span for R2 classes (Informative)

`span` stays a required field with no default (G-9). A default would sign
something the human did not choose. For the two R2 classes, the
recommended choice is:

| Class | Recommended `span` | Why |
|---|---|---|
| `CREATE-PRIVATE` | `session` | A session usually sets up one piece of work and may need a scratch remote more than once. The repository stays private and can be deleted. |
| `ARCHIVE` | `event` | It acts on a codebase that already exists and has value. One codebase, one signature. |

`cycle` is not allowed for R2. A cycle can run for several sessions and
several days, and a private remote created early in it would outlive the
human's view of the work.

---

## Revision Log

| Date       | Change                                          |
|------------|-------------------------------------------------|
| 2026-11-16 | 1.0.0. Initial Draft. ADP-A-002.                |
