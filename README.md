# Repo Template

This repo packages a generic operating system for repos run by one operator plus many agents.

It keeps these layers separate on purpose:

- canonical truth
- current operational reality
- accepted future plans
- curated research
- durable decisions
- execution history
- optional upstream maintenance

That separation is the product. It keeps a repo from turning into a chat dump or a changelog masquerading as truth.

## What Is Canonical

- [repo-operating-model.md](repo-operating-model.md)
  - The rules layer for the system. This replaces a separate instruction file.
- [scaffold/README.md](scaffold/README.md)
  - The ready-to-copy repo skeleton.
- [skills/README.md](skills/README.md)
  - Optional procedural glue for environments that support reusable skills.
- [recreate.prompt.md](recreate.prompt.md)
  - The single recreate prompt for rebuilding this system in another repo.

## Layout

```text
repo-operating-model.md
recreate.prompt.md
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

1. Read [repo-operating-model.md](repo-operating-model.md).
2. Copy the contents of [scaffold/](scaffold/) into the target repo as-is.
3. Fill in `SPEC.md`, `STATUS.md`, `PLANS.md`, and `INBOX.md`.
4. Keep `upstream-intake/` if the repo is a fork, tracks an upstream closely, or wants recurring upstream review. Otherwise remove it or leave it dormant.
5. Adapt [skills/README.md](skills/README.md) only if the target environment supports reusable skills.
6. Seed the system with at least one real `IBX-*`, `LOG-*`, and `DEC-*` artifact so the repo starts grounded in actual work.

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
