# AGENTS.md

Repository rules for every contributor, human or automated, whatever
the model or tool. Tool-specific files (`CLAUDE.md` and the like) only
point here. Rules that bind agents also bind humans.

Informative (ADP-0 §3). How ADP itself changes is ADP-0, not this file.

## Read first

1. `spec/ADP-0.md`: artifact classes, defect register, proposals, roles
2. `DEFECTS.md`: known defects, with evidence
3. `spec/ADP-1.md`: the protocol

Once per clone, before the first commit: `scripts/hooks/install`.

## Roles

- Only the maintainer pushes to `main`, merges, and records proposal
  decisions (ADP-0 §5.3, §8).
- Contributors file defects with evidence (ADP-0 §4.3) and author
  proposals (ADP-0 §5.1). They do not merge or decide.

## Branches

`type/ANCHOR-short-description`, e.g. `spec/ADP-A-001-bcp14-keywords`.
One concern per branch. Stack branches linearly when one depends on
another.

## Commits

```
type(scope): description — ANCHOR[, ANCHOR…]
```

- **type:** `feat fix test refactor docs chore design spec schema
  governance conformance experiment`
- **scope:** the artifact, e.g. `adp-0`, `adp-1`, `defects`, `schema`,
  `examples`
- **anchor:** at least one of `ADP-N`, `ADP-D-NNN`, `ADP-A-NNN`, and it
  must resolve to an existing document, defect, or proposal
- No co-author or AI attribution lines.
- One concern per commit. Do not reformat, re-wrap, or "fix" any file
  outside the change you were asked to make.

## History

- Merge commits only. Never squash-merge or rebase-merge.
- Never rewrite (rebase, amend, force-push) a commit that is pushed or
  cited as evidence. Evidence cites hashes, and rewriting them breaks
  the evidence (ADP-0 §4.3).
- Never bypass hooks or checks (`--no-verify`).

## Evidence and scratch work

Run evidence scripts, virtualenvs, and scratch files outside the
repository. Report what a check printed, not what it should print.

## Enforcement

| Rule | Mechanism |
|------|-----------|
| Push to `main` only via PR; merge commits only; no force-push or deletion of `main` | GitHub ruleset `adp-ruleset` |
| Commit format, anchor resolves, no attribution lines | `scripts/hooks/commit-msg`; CI job `commits` |
| No push to `main`, no force-push, no remote deletion (local guardrail) | `scripts/hooks/pre-push` |
| Schemas pass the metaschema; examples validate | CI job `schema` |
| `schema/` changes need an ACCEPTED proposal | CI job `schema` (`scripts/ci/check-schema-gate`) |
| `DEFECTS.md` append-only, IDs sequential, fields valid | CI job `defects` |
| Everything else | Review by the maintainer |

Inherits the eng-principles change-control practice (ENG-STD-005).
