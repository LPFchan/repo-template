# Agent Instructions

This repo uses repo-template.

Treat `AGENTS.md` as the canonical editable agent-instructions file for the repo.
It should enforce repo behavior while deferring canonical policy details to `REPO.md`.

## Read First

- `REPO.md`
- `SPEC.md`
- `STATUS.md`
- `PLANS.md`
- `INBOX.md`

If the repo includes reusable workflows, then also read `skills/README.md` and the relevant `skills/<name>/SKILL.md`.

When writing into an artifact directory, read that directory's `README.md` first. If it includes a default shape or canonical example, follow it.

## Operating Rules

- Keep durable truth in repo files, not only in chat.
- Route work using the routing ladder in `REPO.md`.
- Preserve the boundary between `SPEC.md`, `STATUS.md`, `PLANS.md`, `INBOX.md`, `research/`, `records/decisions/`, and `records/agent-worklogs/`.
- Worker agents should prefer worklogs, evidence, and proposals. The orchestrator or operator owns truth-doc updates unless the operator explicitly allows a different flow.
- If the repo tracks upstream on a cadence, use `upstream-intake/` instead of inventing a parallel workflow.
- When creating artifacts or commits, follow the stable-ID and provenance rules in `REPO.md`.
- Prefer the local `README.md` shape over ad hoc formatting when it defines one.
- If commit hooks are enabled, your commit message must satisfy the repo provenance check before the commit is allowed.
- If CI commit checks are enabled, your pushed commits must satisfy the same provenance rules remotely.

## Enforcement

When you write or update repo artifacts, adherence to the repo's ruleset is required.

- Do not invent a new document shape when the repo already provides a canonical surface, directory `README.md`, or explicit template.
- Do not collapse truth, plans, decisions, research, inbox intake, and worklogs into one mixed artifact.
- Do not write chatty transcripts where the repo expects normalized records.
- If an artifact would need to diverge from the established shape, make the smallest justified deviation and keep the core fields and section order intact.
- If the repo guidance and the requested output appear to conflict, follow the repo rules and explain the tension in the artifact or handoff.
- Do not bypass commit provenance checks by omitting required trailers unless the commit is an explicit bootstrap or migration exception.

## Skills

`skills/<name>/SKILL.md` files are reusable procedures for bounded workflows.

- Keep them procedural.
- Do not duplicate canonical repo policy inside them.
- Use them to standardize repeatable tasks, escalation triggers, and output shape.
