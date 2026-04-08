# repo-template

repo-template is a framework for running ambitious projects without losing coherence. It gives every project a canonical home for memory, direction, research, and execution, so scattered ideas, buried decisions, drifting specs, and disconnected execution history stop derailing the work.

## Core Pieces

- Canonical truth
  - `SPEC.md`, `STATUS.md`, and `PLANS.md` keep the project's source of truth, current reality, and accepted future direction distinct.
- Intake and routing
  - `INBOX.md` and the orchestrator make sure new work lands in the right place instead of disappearing into chat.
- Durable memory
  - `research/`, `records/decisions/`, and `records/agent-worklogs/` preserve what was learned, what was decided, and what actually happened.
- Provenance
  - Stable IDs and commit trailers keep artifacts, agents, and commits connected over time.
- Optional upstream maintenance
  - `upstream-intake/` gives upstream-tracking projects a disciplined review and escalation system.

## This Repo Includes

- [repo-operating-model.md](repo-operating-model.md)
  - The canonical rules layer.
- [scaffold/README.md](scaffold/README.md)
  - The ready-to-copy repo skeleton.
- [skills/README.md](skills/README.md)
  - Optional procedural workflows for environments that support reusable skills.
- [recreate-prompt.md](recreate-prompt.md)
  - The quick-start prompt for rebuilding this system in another repo.

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
