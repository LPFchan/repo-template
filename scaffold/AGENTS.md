# Agent Instructions

`AGENTS.md` is the canonical editable agent-instructions file. It enforces repo behavior while deferring canonical policy to `records/REPO.md`.

## Read First

- `records/REPO.md`
- `records/SPEC.md`
- `records/STATUS.md`
- `records/PLANS.md`
- `records/INBOX.md`
- `skills/README.md`
- `skills/commit-generator/SKILL.md` (before creating a commit)

Before a repeatable workflow, read the relevant `skills/<name>/SKILL.md`. Before writing into an artifact directory, read its `README.md` and follow its prescriptive shape when it defines one.

## Rules

- Keep durable truth in repo files, not only in external tools.
- Route work using the routing ladder in `records/REPO.md`.
- Preserve the boundary between `records/SPEC.md`, `records/STATUS.md`, `records/PLANS.md`, `records/INBOX.md`, `records/research/`, `records/decisions/`, commit-backed `LOG-*`, and `records/upstream-intake/`.
- Worker agents produce evidence, proposals, and compliant `LOG-*` commits. The orchestrator or operator owns truth-doc updates unless the operator explicitly allows otherwise.
- Treat `records/INBOX.md` as pressure, not a backlog. Cluster capture; promote only survived triage.
- Promote sparsely. Do not mirror one thought into research, decisions, plans, spec, status, upstream, and execution records.
- Every normal commit must be created from a skeleton registered by `scripts/new-commit-message.sh` and must pass local and remote provenance checks.
- Follow the stable-ID and provenance rules in `records/REPO.md`.
- Do not put `LOG-*` ids inside `artifacts:`.
- Do not invent a document shape when the repo already provides a canonical surface, directory `README.md`, or template.
- Do not promote exploratory debate into truth docs or decisions until there is a concise accepted outcome.
- Do not turn an inbox review into a digest of every low-confidence idea. Report counts or clusters.
- Do not write chatty transcripts where the repo expects normalized records.
- Do not bypass commit provenance checks unless the commit is an explicit bootstrap or migration exception.

## Skills

`skills/<name>/SKILL.md` files are reusable procedures for bounded workflows. Keep them procedural; do not duplicate canonical policy from `records/REPO.md`.
