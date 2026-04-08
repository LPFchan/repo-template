---
description: "Example instruction file for repos using the Repo Template operating model."
---

# Repo Template Instructions

Use this instruction when the task is to manage a repo as an operator-plus-agents workspace rather than as a loose chat thread.

## Core Goal

Do not treat the repo as a transcript dump.
Translate incoming work into the right repo artifact.

The canonical repo artifact set is:

- `SPEC.md`
- `STATUS.md`
- `PLANS.md`
- `INBOX.md`
- `research/`
- `records/decisions/`
- `records/agent-worklogs/`
- `upstream-intake/`

When work comes in, first decide which layer it belongs to.

## Routing Rules

- Use `INBOX.md` for low-friction capture that has not been fully triaged.
- Use `research/` for reusable exploration that depends on repo context but is not automatically accepted direction.
- Use `PLANS.md` for accepted future direction only.
- Use `STATUS.md` for current operational truth only.
- Use `SPEC.md` for durable truth only.
- Use `records/decisions/` for meaningful product, architecture, or workflow choices with rationale.
- Use `records/agent-worklogs/` for execution history.
- Use `upstream-intake/` when the task is recurring upstream review or fork maintenance.

## Write Authority

- The operator or orchestrator agent owns `SPEC.md`, `STATUS.md`, and `PLANS.md`.
- Worker agents should append worklogs and propose truth changes through the orchestrator.
- Messenger or webhook surfaces may create inbox entries, but they must not directly write truth docs.

## Provenance Rules

- Every stable-ID-bearing artifact should include:
  - stable id
  - `Opened: YYYY-MM-DD HH-mm-ss KST`
  - `Recorded by agent: <agent-id>`
- `agent-id` identifies one conversation or run, 1:1.
- Off-Git systems should resolve deeper lineage from `agent-id`.
- If Git commits are created, use commit trailers:
  - `Repo-Agent: <agent-id>`
  - `Repo-Artifact: <artifact-id>`
  - `Repo-Project: <project-id>`

## Separation Rules

- `SPEC.md` is not a changelog.
- `STATUS.md` is not a transcript.
- `PLANS.md` is not a scratchpad.
- `INBOX.md` is not durable truth.
- `research/` is not the same as `records/agent-worklogs/`.
- `records/decisions/` is not the same as `records/agent-worklogs/`.

## Upstream Review Rule

When the task is about recurring upstream intake, do not improvise a new process.
Use the canonical package in `upstream-intake/`.

## Output Standard

A good repo-operating run should leave behind:

- the right durable artifact in the right layer
- stable IDs and authoring metadata
- clear separation between what is true, what is planned, what was learned, what was decided, and what happened
