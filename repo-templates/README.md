# Repo Templates

This directory contains the concrete starter templates for the repo operating model in [../repo-operating-model.md](../repo-operating-model.md).

Use these files when bootstrapping a repo that follows this model.

## What To Copy

Copy these templates into the managed repo using the same relative layout:

- `SPEC.template.md` -> `SPEC.md`
- `STATUS.template.md` -> `STATUS.md`
- `PLANS.template.md` -> `PLANS.md`
- `INBOX.template.md` -> `INBOX.md`
- `research/RSH.template.md` -> `research/RSH-YYYYMMDD-NNN-short-title.md`
- `records/decisions/DEC.template.md` -> `records/decisions/DEC-YYYYMMDD-NNN-short-title.md`
- `records/agent-worklogs/LOG.template.md` -> `records/agent-worklogs/LOG-YYYYMMDD-NNN-short-title.md`

Do not duplicate the upstream review files here.
Use the canonical package in [../upstream-intake/README.md](../upstream-intake/README.md).

## Shared Rules

- `SPEC.md`, `STATUS.md`, and `PLANS.md` are rewritten as accepted truth changes.
- `INBOX.md` is ephemeral and should be purged after routing.
- `research/` stores curated findings, not raw logs.
- `records/decisions/` is append-only by new decision file.
- `records/agent-worklogs/` is append-only by new entry or ongoing log file updates.
- Stable IDs should be preserved in every durable artifact.
- Stable-ID-bearing artifacts should open with `Opened: YYYY-MM-DD HH-mm-ss KST` and `Recorded by agent: <agent-id>`.

## Stable ID Prefixes

- `IBX-*` for inbox intake
- `RSH-*` for research memos
- `DEC-*` for decisions
- `LOG-*` for agent worklogs
- `UPS-*` for upstream intake cycles

## Usage Notes

- Keep `SPEC.md` durable and compact.
- Keep `STATUS.md` focused on what is currently true.
- Keep `PLANS.md` limited to accepted future direction.
- Keep `INBOX.md` low-friction so intake does not get lost.
- Keep `research/` for reusable exploration that depends on repo context but is not yet accepted direction.
- Keep decisions and worklogs separate even when they cross-reference heavily.
- Keep `Recorded by agent` separate from ownership fields when the orchestrator writes a record based on another agent's work.
- Let the off-Git runtime resolve deeper message, event, lineage, and commit provenance from `agent-id`.
