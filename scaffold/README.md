# Scaffold

This directory is the canonical repo skeleton for a managed repo.

Copy its contents into the target repo as-is. Do not treat it like a loose grab-bag of snippets.

## Layout

```text
SPEC.md
STATUS.md
PLANS.md
INBOX.md
research/
  README.md
records/
  decisions/
    README.md
  agent-worklogs/
    README.md
upstream-intake/
  ...
```

## Required And Optional Parts

Required:

- `SPEC.md`
- `STATUS.md`
- `PLANS.md`
- `INBOX.md`
- `research/`
- `records/decisions/`
- `records/agent-worklogs/`

Optional but recommended:

- `upstream-intake/`

Keep `upstream-intake/` if the repo is a fork, tracks upstream closely, or wants recurring upstream review. Otherwise remove it or leave it dormant.

## Stable IDs

Use these prefixes:

- `IBX-*`
- `RSH-*`
- `DEC-*`
- `LOG-*`
- `UPS-*`

Numbering is per day and per artifact type. Any agent may claim the next ID by checking the least available `NNN`.

Every stable-ID-bearing artifact should include:

- `Opened: YYYY-MM-DD HH-mm-ss KST`
- `Recorded by agent: <agent-id>`

## How To Use The Directory READMEs

`research/README.md`, `records/decisions/README.md`, and `records/agent-worklogs/README.md` are shape docs.

You can either:

- keep them as naming-and-structure guides, or
- replace them once the first real `RSH-*`, `DEC-*`, or `LOG-*` file lands

## Commit Provenance

Once the target repo adopts this system, every commit should carry:

- `project: <project-id>`
- `agent: <agent-id>`
- `role: orchestrator|worker|subagent|operator`
- `artifacts: <artifact-id>[, <artifact-id>...]`
