# Decisions

This directory stores durable decision records.

## Naming

Create one file per meaningful decision:

- `DEC-YYYYMMDD-NNN-short-title.md`

## Decision Hygiene

- Decision records are append-only by new file.
- If a decision changes later, create a new `DEC-*` that supersedes the old one.
- Do not fold raw execution history into a decision record.

## Required Opening

Each decision file should begin with:

- `# DEC-YYYYMMDD-NNN: <Short Decision Title>`
- `Opened: YYYY-MM-DD HH-mm-ss KST`
- `Recorded by agent: <agent-id>`

## Recommended Shape

- Metadata
- Decision
- Context
- Options considered
- Rationale
- Consequences
