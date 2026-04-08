# repo-template

repo-template is a framework for running ambitious projects without losing coherence. It gives every project a canonical home for memory, direction, research, and execution, so scattered ideas, buried decisions, drifting specs, and disconnected execution history stop derailing the work.

## Core Pieces

| Piece | What it does |
| --- | --- |
| Canonical truth | `SPEC.md`, `STATUS.md`, and `PLANS.md` keep the project's source of truth, current reality, and accepted future direction distinct. |
| Intake and routing | `INBOX.md` and the orchestrator make sure new work lands in the right place instead of disappearing into chat. |
| Durable memory | `research/`, `records/decisions/`, and `records/agent-worklogs/` preserve what was learned, what was decided, and what actually happened. |
| Provenance | Stable IDs and commit trailers keep artifacts, agents, and commits connected over time. |
| Optional upstream maintenance | `upstream-intake/` gives upstream-tracking projects a disciplined review and escalation system. |
| Agent compatibility | Optional `AGENTS.md` and `CLAUDE.md` provide tool-specific entrypoints that defer to the same canonical repo rules. |
| Commit enforcement | Optional git hooks can reject commits that miss required provenance trailers. |
| Remote enforcement | Optional CI can re-check commit provenance on push and pull request. |

## This Repo Includes

| Surface | Role |
| --- | --- |
| [scaffold/REPO.md](scaffold/REPO.md) | The canonical repo contract that ships with adopted repos. |
| [skills/README.md](skills/README.md) | Optional procedural workflows for environments that support reusable skills. |
| [recreate-prompt.md](recreate-prompt.md) | The quick-start prompt for rebuilding this system in another repo. |

## Getting Started

1. As the operator, give your agent [recreate-prompt.md](recreate-prompt.md) and point it at the target repo.
2. Tell the agent whether `upstream-intake/` should stay active, stay dormant, or be omitted for that repo.
3. Have the agent instantiate the [scaffold/](scaffold/) around the real project, including `project-id`, `SPEC.md`, `STATUS.md`, `PLANS.md`, and `INBOX.md`.
4. Review the first seeded artifacts together, especially the initial `IBX-*`, `LOG-*`, and `DEC-*` items, and correct any routing mistakes early.
5. If your environment supports reusable workflows, then layer in [skills/README.md](skills/README.md). Otherwise stop at the scaffold.

## Instruction File Mapping

- `AGENTS.md`
  - Best as the canonical editable repo-level instructions file for agentic tools.
  - Keep it thin and point it back to `REPO.md`.
- `CLAUDE.md`
  - Anthropic Claude Code project memory file.
  - Keep it as a thin shim that points to `AGENTS.md`.
- `SKILL.md`
  - A reusable workflow file that lives under `skills/<name>/SKILL.md`.
  - Use it for bounded procedures, outputs, and escalation triggers, not repo-wide truth.

## Writing Discipline

repo-template now treats artifact shape as part of the contract, not just nice-to-have docs.

- The local directory `README.md` should explain what belongs there and show the preferred finished artifact shape.
- Agents should read that guide before creating new `RSH-*`, `DEC-*`, `LOG-*`, or upstream intake artifacts.
- Not every surface needs the same amount of structure. `SPEC.md` and research memos may stay intentionally lightweight when the repo needs flexibility more than uniformity.

## Commit Checks

repo-template can also enforce commit provenance at commit time.

- `.githooks/commit-msg` runs a tracked commit-message check.
- `scripts/check-commit-standards.sh` validates the required trailers.
- `scripts/check-commit-range.sh` validates every commit in a git range.
- `scripts/install-hooks.sh` enables the tracked hooks for the local clone.
- `.github/workflows/commit-standards.yml` re-checks commit provenance in CI on push and pull request.

Normal commits should include:

- `project: <project-id>`
- `agent: <agent-id>`
- `role: orchestrator|worker|subagent|operator`
- `artifacts: <artifact-id>[, <artifact-id>...]`

Bootstrap or migration exceptions must be explicit in the commit message.

Artifact linkage should stay useful, not bureaucratic.

- A normal commit should reference at least one relevant artifact, but that artifact does not need to be newly created.
- Agents should prefer appending to the current relevant `LOG-*` when the same workstream continues.
- A new `LOG-*` should be created only when the work is distinct enough that a separate execution record improves clarity.

## Prompt For Adopted Repos

Use a migration prompt like this when introducing both local hooks and CI to an already-adopted repo:

```text
This repo already uses repo-template. Introduce commit provenance enforcement without losing repo-specific workflow rules.

Reference source:
- /Users/yeowool/Documents/repo-template/scaffold/REPO.md
- /Users/yeowool/Documents/repo-template/scaffold/AGENTS.md
- /Users/yeowool/Documents/repo-template/scaffold/CLAUDE.md
- /Users/yeowool/Documents/repo-template/.githooks/commit-msg
- /Users/yeowool/Documents/repo-template/scripts/check-commit-standards.sh
- /Users/yeowool/Documents/repo-template/scripts/check-commit-range.sh
- /Users/yeowool/Documents/repo-template/scripts/install-hooks.sh
- /Users/yeowool/Documents/repo-template/.github/workflows/commit-standards.yml

Goals:
1. Add local git-hook enforcement for commit provenance.
2. Add CI enforcement so pushed commits and PR commits are checked remotely too.
3. Merge these rules into the repo's existing `AGENTS.md` and `CLAUDE.md` if they already exist.

Rules:
- Preserve existing repo-specific instructions, commands, and workflow notes.
- Keep `AGENTS.md` and `CLAUDE.md` thin, but make them explicitly require compliant commit messages when hooks or CI are enabled.
- Treat `AGENTS.md` as the editable source of agent rules and `CLAUDE.md` as a pointer shim where possible.
- If the repo already has hooks or CI, merge with them instead of replacing them blindly.
- Reuse repo-template's commit checks unless the target repo already has a stronger equivalent.
- Treat bootstrap or migration exceptions as explicit exceptions only.
- Do not weaken existing enforcement during the merge.

Execution:
- Inspect existing local hooks, CI workflows, `AGENTS.md`, and `CLAUDE.md`.
- Add or merge the local `commit-msg` hook path and validator scripts.
- Add or merge the CI workflow so commit provenance is checked on push and pull request.
- Update agent instruction files so they tell agents to satisfy the checks rather than bypass them.
- Summarize any intentional divergences from repo-template.
```

## Provenance Rules

Stable artifact types use these prefixes:

| Prefix | Artifact type |
| --- | --- |
| `IBX-*` | Inbox intake |
| `RSH-*` | Research memos |
| `DEC-*` | Decisions |
| `LOG-*` | Worklogs |
| `UPS-*` | Upstream intake cycles |

Stable-ID-bearing artifacts should open with:

| Field | Required value |
| --- | --- |
| `Opened` | `YYYY-MM-DD HH-mm-ss KST` |
| `Recorded by agent` | `<agent-id>` |

After a repo adopts this system, every commit should carry these lowercase trailers:

| Trailer | Value |
| --- | --- |
| `project:` | `<project-id>` |
| `agent:` | `<agent-id>` |
| `role:` | `orchestrator|worker|subagent|operator` |
| `artifacts:` | `<artifact-id>[, <artifact-id>...]` |

Artifact-less commits should be treated as bootstrap or migration exceptions only.
