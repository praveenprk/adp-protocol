# Changelog

Release notes for each ADP document version. Newest first.

- **Normative history:** the spec's own Revision Log. If this file and a
  spec disagree, the spec wins (ADP-0 §3).
- **Tag:** each version is tagged `adp-N/vX.Y.Z` on the merge commit
  that put it on `main`, and has a GitHub Release.
- **Status:** every document is a Draft. Releases are marked pre-release.

## Latest

| Document | Version | Tag |
|----------|---------|-----|
| ADP-0 Governance | 1.1.0 | `adp-0/v1.1.0` |
| ADP-1 Agent Dispatch Protocol | 1.1.1 | `adp-1/v1.1.1` |
| ADP-2 Dispatch Authority | 2.0.1 | `adp-2/v2.0.1` |

---

## ADP-1: Agent Dispatch Protocol

| Version | Date | Bump | Change | Upgrade impact | Defects closed | Proposal | PR |
|---------|------|------|--------|----------------|----------------|----------|----|
| 1.1.1 | 2026-11-17 | Patch | `SOURCE` is the `source` field, not a keyword. Field constraints written down (§4.5, §5.5) and checked by new V-13 and R-12. `COMPLETE` requires every exit result `true` (new R-13). Tier selection is informative, lowest tier wins on conflict. Deduplication is SHOULD NOT. | A `COMPLETE` report with a failed exit result is now rejected: report `BLOCKED` instead. Nothing else the published schemas accepted is rejected. | D-001, D-002, D-008, D-010, D-013, D-024, D-025 | ADP-A-007 | #21, #22 |
| 1.1.0 | 2026-11-16 | Minor | Extensions live in `metadata` on the work item, dispatch and report, with keys `x-{namespace}-{name}`. Unknown fields are rejected at every level for a known minor version, ignored for a higher one. New V-12, R-10, R-11. | Move extension keys into `metadata`. A misspelt field is now rejected. | D-003, D-006, D-007 | ADP-A-005 | #15, #16 |
| 1.0.2 | 2026-11-16 | Patch | `adp_version` is SemVer 2.0.0; major version 1 checked by new V-11 and R-09. | An envelope with a non-SemVer version, or a major version other than 1, is rejected. | D-004, D-009 | ADP-A-004 | #13, #14 |
| 1.0.1 | 2026-11-15 | Patch | Key words per BCP 14. The §7.1 and §7.2 rules bind validators. | None for envelopes. | D-012 | ADP-A-001 | #7, #11 |
| 1.0.0 | 2026-11-15 | — | Initial specification (written 2026-06-26): 10 keywords frozen, dispatch and report envelopes, compression tiers, validation contract. | — | — | — | #2 |

## ADP-2: Dispatch Authority

| Version | Date | Bump | Change | Upgrade impact | Defects closed | Proposal | PR |
|---------|------|------|--------|----------------|----------------|----------|----|
| 2.0.1 | 2026-11-17 | Patch | §3 note: `SOURCE` is not an ADP-1 keyword. Editorial. | None. | — | ADP-A-007 | #21, #22 |
| 2.0.0 | 2026-11-17 | Major | Grant id, paths, globs and overlap defined (§4.1, §4.2). Codebase event record and `validate_record` (§4.3, §6). AT-VERIFY and codebase events are never inferred (§3). Every limiting grant field required (G-10). | Grants use `adp_grant_version` 2.x, carry every limiting field, and give `expires_at` in UTC (`Z`). Records are full documents checked by `validate_record`. | D-018, D-019, D-020, D-021, D-022 | ADP-A-006 | #19, #20 |
| 1.0.0 | 2026-11-16 | — | Initial Draft: approval-rooted, session-bound grants; human signature for creating or deleting a codebase; approval and merge stay human. | — | — | ADP-A-002 | #8, #10, #17 |

## ADP-0: Governance

| Version | Date | Bump | Change | Upgrade impact | Defects closed | Proposal | PR |
|---------|------|------|--------|----------------|----------------|----------|----|
| 1.1.0 | 2026-11-15 | Minor | §5.6 conformance suite format: layout, vector file, rules for vectors, known-defect markers. | Conformance vectors follow §5.6. | — | ADP-A-003 | #9, #12 |
| 1.0.0 | 2026-11-15 | — | Initial governance: artifact classes and precedence, defect register, proposal process, application order, errata, version impact, maintainer roles. | — | — | — | #3 |

---

## Adding a release

In every PR that changes a document's version:

1. Add a row at the top of that document's table, and update **Latest**.
2. After the maintainer merges, tag the merge commit `adp-N/vX.Y.Z` and
   publish a GitHub Release (pre-release while the document is a Draft)
   whose notes are the row.
