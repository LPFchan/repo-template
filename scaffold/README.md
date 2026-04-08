# Scaffold

This directory is the canonical repo skeleton for a managed repo.

Copy its contents into the target repo as-is. Do not treat it like a loose grab-bag of snippets.

## Layout

```text
AGENTS.md
CLAUDE.md
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

- `AGENTS.md`
- `CLAUDE.md`
- `upstream-intake/`

Keep `upstream-intake/` if the repo is a fork, tracks upstream closely, or wants recurring upstream review. Otherwise remove it or leave it dormant.

## Agent Instruction Entry Points

`AGENTS.md` and `CLAUDE.md` are compatibility surfaces for agentic tools that look for repo-root instructions.

- Keep both thin.
- Point them back to `repo-operating-model.md`.
- Do not fork the policy layer into multiple files.
- Keep reusable workflows in `skills/<name>/SKILL.md`, not in these entrypoint files.

## Artifact Writing Rule

The scaffold should not stop at macro structure.

For durable artifact directories, prefer shipping one strong `README.md` that includes:

- scope and rules
- the default section shape
- a canonical finished example when useful

Agents should read that local guide before inventing a new layout.

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
They should also show the default finished artifact shape inline.

You can either:

- keep them as naming-and-structure guides, or
- keep them permanently as agent guidance even after the first real `RSH-*`, `DEC-*`, or `LOG-*` file lands

## Commit Provenance

Once the target repo adopts this system, every commit should carry:

- `project: <project-id>`
- `agent: <agent-id>`
- `role: orchestrator|worker|subagent|operator`
- `artifacts: <artifact-id>[, <artifact-id>...]`

## Hooking This Up

If you want commit-time enforcement in an adopted repo:

1. Copy `.githooks/commit-msg` and `scripts/check-commit-standards.sh` into the target repo.
2. Copy `scripts/check-commit-range.sh` and `.github/workflows/commit-standards.yml` if you also want CI enforcement.
3. Run `scripts/install-hooks.sh` once in that repo.
4. Make sure agents know that bootstrap or migration exceptions must be explicit.
