# repo-template

repo-template is a framework for running ambitious projects without losing coherence. It gives every project a canonical home for memory, direction, research, and execution, so scattered ideas, buried decisions, drifting specs, and disconnected execution history stop derailing the work.

## What Is Canonical

- [repo-operating-model.md](repo-operating-model.md)
  - The rules layer for the system. This replaces a separate instruction file.
- [scaffold/README.md](scaffold/README.md)
  - The ready-to-copy repo skeleton.
- [skills/README.md](skills/README.md)
  - Optional procedural glue for environments that support reusable skills.
- [recreate-prompt.md](recreate-prompt.md)
  - The single recreate prompt for rebuilding this system in another repo.

## Layout

```text
repo-operating-model.md
recreate-prompt.md
scaffold/
  SPEC.md
  STATUS.md
  PLANS.md
  INBOX.md
  research/
  records/
  upstream-intake/
skills/
  repo-orchestrator/
  upstream-intake/
```

## Getting Started

1. As the operator, give your agent [recreate-prompt.md](recreate-prompt.md) and point it at the target repo.
2. Tell the agent whether `upstream-intake/` should stay active, stay dormant, or be omitted for that repo.
3. Have the agent instantiate the [scaffold/](scaffold/) around the real project, including `project-id`, `SPEC.md`, `STATUS.md`, `PLANS.md`, and `INBOX.md`.
4. Review the first seeded artifacts together, especially the initial `IBX-*`, `LOG-*`, and `DEC-*` items, and correct any routing mistakes early.
5. If your environment supports reusable workflows, then layer in [skills/README.md](skills/README.md). Otherwise stop at the scaffold.

## Provenance Rules

Stable artifact types use these prefixes:

- `IBX-*` for inbox intake
- `RSH-*` for research memos
- `DEC-*` for decisions
- `LOG-*` for worklogs
- `UPS-*` for upstream intake cycles

Stable-ID-bearing artifacts should open with:

- `Opened: YYYY-MM-DD HH-mm-ss KST`
- `Recorded by agent: <agent-id>`

After a repo adopts this system, every commit should carry these lowercase trailers:

- `project: <project-id>`
- `agent: <agent-id>`
- `role: orchestrator|worker|subagent|operator`
- `artifacts: <artifact-id>[, <artifact-id>...]`

Artifact-less commits should be treated as bootstrap or migration exceptions only.

## Design Goal

This repo is meant to be generic enough for any codebase, but opinionated enough that operators and agents can work for a long time without losing track of what is true, what is planned, what was learned, and what actually happened.
