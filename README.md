# repo-template

A repo operating system for projects managed by one operator plus many agents. Gives every project a canonical home for truth, memory, direction, and execution provenance.

## Getting Started

Give your agent this prompt, pointing at the target repo:

> Fetch the latest repo-template from `LPFchan/repo-template`. Copy `scaffold/` contents into the target repo root. Follow the canonical rules in `records/REPO.md`. Enable `upstream-intake/` only if the target repo tracks an upstream. Wire local hooks. Seed at least one real artifact to verify routing boundaries.

## Scaffold Map

| Path | Answers |
| --- | --- |
| `records/REPO.md` | How this repo operates |
| `records/SPEC.md` | What this repo is |
| `records/STATUS.md` | Where this repo currently sits |
| `records/PLANS.md` | What's planned for this repo |
| `records/INBOX.md` | Capture waiting for triage |
| `records/research/` | What we learned from exploration |
| `records/decisions/` | What we decided and why |
| `records/upstream-intake/` | Upstream changes we reviewed |
| `skills/` | Repeatable procedural workflows |
| `AGENTS.md` | Agent instructions entrypoint |
| `CLAUDE.md` | Thin shim pointing to `AGENTS.md` |

Agent instruction files stay thin. Canonical policy lives in `records/REPO.md`.

## Commit Format

Every normal commit must carry:

```text
<subject line>

timestamp: YYYY-MM-DD HH-mm-ss KST
changes:
- ...
rationale:
- ...
checks:
- ...

project: <project-id>
agent: <agent-id>
role: orchestrator|worker|subagent|operator
commit: LOG-YYYYMMDD-HHMMSS-<agent-suffix>
artifacts: DEC-..., RSH-...   (optional; no LOG-*)
```

Generate a compliant skeleton:

```bash
sh scripts/new-commit-message.sh --subject "feat: your change" --agent <agent-id>
```

Commit with `git commit -F <generated-file>`. Hand-written `git commit -m` is rejected by the hooks.

## Enforcement

- `.githooks/prepare-commit-msg` — rejects non-generated normal commits
- `.githooks/commit-msg` — validates execution contract
- Bootrap/migration commits are the only exception path

Run `sh scripts/install-hooks.sh` to enable tracked hooks locally.

## Upgrading an Adopted Repo

To upgrade an already-adopted repo to the current template contract:

> This repo already uses repo-template. Fetch the latest from `LPFchan/repo-template`. Merge upstream policy into `records/REPO.md`, `AGENTS.md`, and `CLAUDE.md` verbatim. Merge hooks and scripts. Do not paraphrase upstream policy. Preserve local extensions under an explicit `Local Divergence` section. Do not weaken existing enforcement.
