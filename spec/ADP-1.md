# ADP-1: Agent Dispatch Protocol Specification

| Field        | Value                                   |
|--------------|-----------------------------------------|
| **ID**       | ADP-1                                   |
| **Title**    | Agent Dispatch Protocol                 |
| **Version**  | 1.0.2                                   |
| **Status**   | Draft                                   |
| **License**  | Apache 2.0                              |
| **Date**     | 2026-11-15                              |

---

## Abstract

ADP is a structured protocol for the instruction boundary between
an orchestrator and an agent. It defines a keyword vocabulary, an
envelope schema, a report schema, compression tiers, and a
validation contract. Transport-agnostic. Model-agnostic.
Framework-agnostic.

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

## 1. Problem

The instruction boundary between orchestrators and agents has no
protocol. Every framework reinvents it as unstructured prose.
Prompt templates, task YAML, message dicts, markdown instructions
— all are string concatenation with no structural contract between
sender and receiver.

MCP standardized the tool interface (agent → service). OpenAPI
standardized API description (service → consumer). Nothing
standardizes the instruction interface (orchestrator → agent).

ADP fills this gap.

---

## 2. Scope

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

---

## 3. Keyword Vocabulary

10 keywords. Fixed at v1.0.0. Uppercase in envelopes. Each is a
structural directive with defined semantics.

### 3.1 Action Keywords

| Keyword     | Semantics                                      |
|-------------|-------------------------------------------------|
| `PRODUCE`   | Create named artifact at named path.            |
| `BIND`      | Make irreversible decision. Lock with rationale.|
|             | No deferral permitted on a BIND item.           |
| `CONFIRM`   | Verify condition holds. Assert, do not decide.  |
| `SURFACE`   | Flag finding to orchestrator. Stop. Do not      |
|             | resolve. Do not act beyond the flag.            |
| `DEFER`     | Explicitly not deciding. Name the owner and     |
|             | gate where resolution belongs.                  |

### 3.2 Context Keywords

| Keyword     | Semantics                                      |
|-------------|-------------------------------------------------|
| `READ`      | Required context. Agent consumes before work.   |
|             | Section-level specificity preferred.            |
| `IGNORE`    | Isolation boundary. Content from IGNORE sources |
|             | is treated as contamination.                    |

### 3.3 Output Keywords

| Keyword     | Semantics                                      |
|-------------|-------------------------------------------------|
| `REPORT`    | Structured handoff to orchestrator. Agent       |
|             | returns exactly these items. Nothing more.      |
| `EXIT`      | Binary pass/fail completion condition. Agent    |
|             | self-checks every EXIT before declaring done.   |

### 3.4 Scope Keywords

| Keyword     | Semantics                                      |
|-------------|-------------------------------------------------|
| `ANCHOR`    | Traceable governing reference for this dispatch.|
| `SOURCE`    | Origin section in governing document that       |
|             | motivates a specific work item.                 |

### 3.5 Extensibility

The keyword set is frozen at v1.0.0. No new keywords in any
1.x.y release.

Extensions are carried as namespaced metadata on work items,
envelope, or report. Namespace format: `x-{namespace}-{name}`.

```yaml
work_items:
  - keyword: "BIND"
    description: "choose superseding structure"
    metadata:
      x-contextos-seam: 4
      x-contextos-source: "SPEC-027 §5"
```

Validators MUST ignore unknown `x-` metadata fields.
Validators MUST reject unknown keywords.

---

## 4. Dispatch Envelope Schema

A dispatch envelope carries an instruction from orchestrator to
agent. Transport-agnostic. Serializable as YAML, JSON, TOML,
MessagePack, protobuf, or fixed-width binary.

### 4.1 Required Fields

```yaml
adp_version: "1.0.0"

dispatch:
  agent: string          # agent identifier
  anchor: [string]       # at least one traceable reference
  
context:
  read: [ReadEntry]      # at least one entry

exit: [string]           # at least one completion condition

report: [string]         # at least one handoff item
```

### 4.2 Optional Fields

```yaml
dispatch:
  model: string          # model identifier
  tier: integer          # compression tier (1, 2, 3)
  gate: string           # gate identifier
  branch: string         # version control branch

context:
  ignore: [string]       # isolation patterns

produce: [ProduceEntry]  # output artifacts

work_items: [WorkItem]   # directive-bearing work items
```

### 4.3 Field Definitions

**ReadEntry:**
```yaml
path: string             # file or resource path
sections: [string]       # optional section references
```

**ProduceEntry:**
```yaml
path: string             # output artifact path
action: string           # "create" | "modify"
```

**WorkItem:**
```yaml
keyword: string          # one of the 10 defined keywords
description: string      # the directive content
source: string           # optional — origin reference
metadata: object         # optional — namespaced extensions
```

### 4.4 Constraint

At least one of `produce` or `work_items` MUST be present.
An envelope with neither is a validation failure — it
instructs nothing.

---

## 5. Report Envelope Schema

A report envelope carries results from agent to orchestrator.

### 5.1 Required Fields

```yaml
adp_version: "1.0.0"

report:
  agent: string
  anchor: [string]
  status: string         # "COMPLETE" | "BLOCKED" | "SURFACE"

exit_results: [ExitResult]

items: [ReportItem]
```

### 5.2 Field Definitions

**ExitResult:**
```yaml
condition: string        # echoes the EXIT condition
result: boolean          # pass or fail
```

**ReportItem:**
```yaml
key: string
value: string
```

### 5.3 Status Values

Three values. Fixed.

| Status     | Semantics                                    |
|------------|----------------------------------------------|
| `COMPLETE` | All EXIT conditions passed. Work done.       |
| `BLOCKED`  | Agent cannot proceed. `items` MUST include   |
|            | at least one entry with key `blocker`        |
|            | describing what is missing.                  |
| `SURFACE`  | Agent found something requiring orchestrator |
|            | judgment. `items` MUST include at least one  |
|            | entry with key `finding`.                    |

### 5.4 Chaining Constraint

Report items referencing produced artifacts MUST include the
artifact path from the dispatch envelope's `produce` section.
A report that references state outside the envelope is
non-conformant.

The report IS the handoff to the next agent. No separate
chaining mechanism. The next agent's `context.read` includes
the prior agent's report and/or produced artifacts.

---

## 6. Compression Tiers

Compression ratio indexed to judgment density of the task.
Tier selection is orchestrator's responsibility. The protocol
defines what each tier retains and strips. Same keyword
grammar across all tiers — different density.

### Tier 1 — High Judgment (40–50% compression)

Retains rationale, cross-references, tradeoff framing,
SOURCE per work item. Agent makes irreversible decisions
that shape downstream work.

Use when: the agent must choose between competing options
and the wrong choice cascades.

### Tier 2 — Medium Judgment (55–65% compression)

Retains constraints, assertion shapes, invariant references.
Strips rationale and options-considered.

Use when: the agent asserts against a shape already decided,
but must interpret edge cases.

### Tier 3 — Low Judgment (65–75% compression)

Retains directives, paths, field names, EXIT conditions.
Strips all rationale, all cross-references beyond immediate
source. Pure imperative.

Use when: the agent executes a shape already decided and
tested. It needs coordinates, not cartography.

### Tier Selection Guidance

| Signal                                        | Tier |
|-----------------------------------------------|------|
| Work items contain BIND                       | 1    |
| Work items contain only CONFIRM + PRODUCE     | 3    |
| Work items mix BIND + CONFIRM                 | 2    |
| Agent is expected to SURFACE findings         | 1–2  |
| Agent executes against known passing criteria | 3    |

---

## 7. Validation Contract

Validation is a pure function. Envelope in, result out. No
network calls. No state. No model-specific logic.

A validator MUST reject a dispatch envelope that fails any rule in
§7.1, and MUST reject a report envelope that fails any rule in §7.2.

### 7.1 Dispatch Validation Rules

| Rule | Check                                              |
|------|----------------------------------------------------|
| V-01 | `adp_version` present and valid SemVer 2.0.0       |
| V-02 | `dispatch.agent` non-empty string                  |
| V-03 | `dispatch.anchor` non-empty array                  |
| V-04 | `context.read` non-empty array                     |
| V-05 | `exit` non-empty array                             |
| V-06 | `report` non-empty array                           |
| V-07 | At least one of `produce` or `work_items` present  |
| V-08 | Every `work_items[].keyword` in defined vocabulary  |
| V-09 | No unknown top-level fields outside schema         |
| V-10 | `dispatch.tier` if present is 1, 2, or 3           |
| V-11 | `adp_version` major version is 1 (§7.3)            |

### 7.2 Report Validation Rules

| Rule | Check                                              |
|------|----------------------------------------------------|
| R-01 | `adp_version` present and valid SemVer 2.0.0       |
| R-02 | `report.agent` non-empty string                    |
| R-03 | `report.anchor` non-empty array                    |
| R-04 | `report.status` is COMPLETE, BLOCKED, or SURFACE   |
| R-05 | `exit_results` non-empty array                     |
| R-06 | `items` non-empty array                            |
| R-07 | If status BLOCKED: items contains key `blocker`    |
| R-08 | If status SURFACE: items contains key `finding`    |
| R-09 | `adp_version` major version is 1 (§7.3)            |

### 7.3 Version Compatibility

Parsers MUST reject unknown major versions.
Parsers MUST accept unknown minor versions (ignore unknown
optional fields).
Unknown `x-` namespaced metadata fields are always ignored.

For ADP-1 the only known major version is 1 (V-11, R-09).

---

## 8. Deduplication Rule

A dispatch envelope MUST NOT carry content that is structurally
available to the agent through its READ context. If a role
boundary, commit format, or behavioral constraint exists in a
document the agent is directed to READ, restating it in the
dispatch is redundant and non-conformant.

Exception: EXIT conditions that tighten or specialize the
agent's general contract for this specific dispatch ARE
included. They are additive, not duplicative.

Deduplication is a SHOULD for v1.0.0 (not mechanically
enforced by the validator — requires semantic understanding
of READ content). Future versions may introduce content-hash
deduplication.

---

## 9. Versioning

Semantic Versioning 2.0.0 (https://semver.org/spec/v2.0.0.html).
`adp_version` field in every envelope. A pre-release or build
metadata suffix is allowed (`1.1.0-rc.1`, `1.0.2+build.5`).
Compatibility (§7.3) depends on the major version only.

| Change                            | Bump  |
|-----------------------------------|-------|
| Keyword addition or removal       | Major |
| Envelope schema breaking change   | Major |
| New optional field                | Minor |
| Spec clarification, no schema Δ   | Patch |

Keywords are frozen at v1.0.0. A major bump is not expected.
If 2.0.0 is ever needed, the original design was wrong.

---

## 10. Relationship to Existing Standards

| Standard | Relationship                                   |
|----------|------------------------------------------------|
| RFC 2119 | Complementary vocabularies. RFC 2119 governs   |
|          | specification documents (system behavior). ADP |
|          | governs dispatch envelopes (agent behavior).   |
|          | An ADP envelope may quote RFC 2119 terms when  |
|          | referencing spec constraints. ADP keywords do  |
|          | not appear in specs.                           |
| MCP      | Orthogonal layers. MCP governs tool calls      |
|          | (agent → service). ADP governs instructions    |
|          | (orchestrator → agent).                        |
| OpenAPI  | Different concerns. OpenAPI describes APIs.    |
|          | ADP describes instruction envelopes.           |
| HTTP     | ADP is payload schema, not transport. ADP      |
|          | envelopes can ride on HTTP, file I/O, stdin,   |
|          | message queues, or hardware buses.             |

---

## 11. What ADP Is Not

- Not a prompt engineering framework.
- Not model-specific.
- Not framework-coupled.
- Not transport-specific.
- Not an agent runtime or orchestrator.

---

## Revision Log

| Date       | Change                                         |
|------------|-------------------------------------------------|
| 2026-06-26 | Initial specification. Keywords frozen. Four    |
|            | open questions closed: extensibility (freeze +  |
|            | namespace), negotiation (not in v1), chaining   |
|            | (report IS handoff), versioning (semver, major  |
|            | not expected).                                  |
| 2026-11-15 | 1.0.1. Key words per BCP 14 (Conventions);      |
|            | §7.1/§7.2 rules bind validators (§7). ADP-A-001, |
|            | resolves ADP-D-012.                             |
| 2026-11-15 | 1.0.2. `adp_version` is SemVer 2.0.0 (§9,      |
|            | V-01, R-01); major version 1 checked by new    |
|            | V-11 and R-09 (§7.3). ADP-A-004, resolves      |
|            | ADP-D-004 and ADP-D-009.                       |
