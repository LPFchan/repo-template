# Agent Worklogs

This directory stores execution history for runs, sessions, agents, and subagents.

## Naming

Create one file per run or workstream:

- `LOG-YYYYMMDD-NNN-short-title.md`

## Worklog Hygiene

- Worklogs are append-only.
- If a correction is needed, append a new entry rather than rewriting old history.
- Do not turn worklogs into decision records or truth docs.

## Required Opening

Each worklog should begin with:

- `# LOG-YYYYMMDD-NNN: <Short Run Or Task Title>`
- `Opened: YYYY-MM-DD HH-mm-ss KST`
- `Recorded by agent: <agent-id>`

## Recommended Shape

- Metadata
- Task
- Scope
- Timestamped entries with actions, files touched, checks run, outputs, blockers, and next steps
