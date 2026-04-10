# repo-template

repo-template is a framework for running ambitious projects without losing coherence. It gives every project a canonical home for memory, direction, research, and execution, so scattered ideas, buried decisions, drifting specs, and disconnected execution history stop derailing the work.

## Core Pieces

| Piece | What it does |
| --- | --- |
| Canonical truth | `SPEC.md`, `STATUS.md`, and `PLANS.md` keep the project's source of truth, current reality, and accepted future direction distinct. |
| Capture and routing | `INBOX.md` and the orchestrator make sure new capture lands in the right place instead of disappearing into external tools. |
| Inbox pressure review | A daily IBX review can cluster, discard, hold, research, route, or promote capture without turning every idea into a future-direction digest. |
| Sparse promotion | Exploratory shaping can stay in external capture or inbox; durable artifacts receive concise outcomes only when that layer has a distinct job. |
| Durable memory | `research/`, `records/decisions/`, and commit-backed `LOG-*` records preserve what was learned, what was decided, and what actually happened. |
| Provenance | Stable IDs and commit trailers keep artifacts, agents, and commits connected over time. |
| Procedural skills | `skills/` ships inside the scaffold so repeatable agent workflows are documented in the adopted repo. |
| Optional upstream maintenance | `upstream-intake/` gives upstream-tracking projects a disciplined review and escalation system. Omit it when the repo is not tracking an upstream. |
| Agent compatibility | Optional `AGENTS.md` and `CLAUDE.md` provide tool-specific entrypoints that defer to the same canonical repo rules. |
| Commit enforcement | Optional git hooks can reject commits that miss required provenance trailers. |
| Remote enforcement | Optional CI can re-check commit provenance on push and pull request. |

## This Repo Includes

| Surface | Role |
| --- | --- |
| [scaffold/REPO.md](scaffold/REPO.md) | The canonical repo contract that ships with adopted repos. |
| [scaffold/skills/README.md](scaffold/skills/README.md) | Required procedural workflows that ship with adopted repos as root `skills/`. |
| [recreate-prompt.md](recreate-prompt.md) | The quick-start prompt for rebuilding this system in another repo. |

## Getting Started

1. As the operator, give your agent [recreate-prompt.md](recreate-prompt.md) and point it at the target repo.
2. Tell the agent whether the optional `upstream-intake/` module should stay active, stay dormant, or be omitted for that repo. If it is omitted, omit its companion `skills/upstream-intake/` skill too.
3. Have the agent copy the contents of [scaffold/](scaffold/) into the target repo root, including `REPO.md`, `SPEC.md`, `STATUS.md`, `PLANS.md`, `INBOX.md`, and root `skills/`.
4. Keep the required baseline skills: `skills/repo-orchestrator/` and `skills/daily-inbox-pressure-review/`.
5. Review the first seeded artifacts together, especially the initial `IBX-*`, `DEC-*`, and commit-backed `LOG-*` records, and correct any routing mistakes early.

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
- Agents should read that guide before creating new `RSH-*`, `DEC-*`, `UPS-*`, or other file-backed artifacts.
- Not every surface needs the same amount of structure. `SPEC.md` and research memos may stay intentionally lightweight when the repo needs flexibility more than uniformity.

## Inbox Pressure

`INBOX.md` is an ephemeral pressure valve.
Operators may capture low-confidence ideas, external-tool fragments, transcripts, dictated notes, links, pivots, and "maybe later" thoughts there.

The daily inbox review should protect focus:

- group related capture before deciding what matters
- identify stale, noisy, duplicate, and low-signal clusters
- route, research, plan, discard, or leave meaningful capture packets
- promote only survived triage
- report counts or clusters of noisy/held/discarded items instead of summarizing every fragment

## Sparse Promotion

repo-template is a refinery, not a mirror maze.

- Keep raw shaping in external capture, generic notes, off-Git capture packets, or `INBOX.md` while the thought is still forming.
- Keep research in `research/` unless a meaningful choice has actually been accepted.
- Write `DEC-*` only for a real accepted product, architecture, workflow, trust, upstream, or repo-operating choice.
- Update `SPEC.md`, `STATUS.md`, and `PLANS.md` with concise outcomes, not copied debate.
- Touch multiple layers only when each layer has a distinct job.

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
- `commit: LOG-...[, LOG-...]`

Optional:

- `artifacts: <artifact-id>[, <artifact-id>...]`

Normal commit bodies should use:

- `timestamp:`
- `changes:`
- `rationale:`
- `checks:`
- optional `notes:`

Bootstrap or migration exceptions must be explicit in the commit message.

Commit-backed execution should stay useful, not bureaucratic.

- `commit:` is the canonical execution record for the commit.
- `artifacts:` is optional and should reference only related non-`LOG-*` durable artifacts.
- Multiple `LOG-*` ids in `commit:` mean the landed commit absorbs earlier execution records whose separate commits will not remain separate landed history.

## Prompt For Adopted Repos

Use a migration prompt like this when introducing both local hooks and CI to an already-adopted repo:

```text
This repo already uses repo-template. Introduce commit-backed execution enforcement without losing repo-specific workflow rules.

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
1. Add local git-hook enforcement for the commit-backed execution contract.
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
- Require `project:`, `agent:`, `role:`, and `commit:` on normal commits.
- Treat `artifacts:` as optional and forbid `LOG-*` inside it.
- Require the lowercase commit body keys `timestamp:`, `changes:`, `rationale:`, and `checks:` with `notes:` optional.

Execution:
- Inspect existing local hooks, CI workflows, `AGENTS.md`, and `CLAUDE.md`.
- Add or merge the local `commit-msg` hook path and validator scripts.
- Add or merge the CI workflow so the commit-backed execution contract is checked on push and pull request.
- Update agent instruction files so they tell agents to satisfy the checks rather than bypass them.
- Summarize any intentional divergences from repo-template.
```

## Provenance Rules

Stable artifact types use these prefixes:

| Prefix | Artifact type |
| --- | --- |
| `IBX-*` | Inbox capture |
| `RSH-*` | Research memos |
| `DEC-*` | Decisions |
| `LOG-*` | Commit-backed execution records |
| `UPS-*` | Upstream intake cycles |

File-backed stable-ID-bearing artifacts should open with:

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
| `commit:` | `LOG-YYYYMMDD-HHMMSS-<agent-suffix>[, LOG-...]` |

Optional:

| Trailer | Value |
| --- | --- |
| `artifacts:` | `<artifact-id>[, <artifact-id>...]` |

Commits without the required execution trailers should be treated as bootstrap or migration exceptions only.
