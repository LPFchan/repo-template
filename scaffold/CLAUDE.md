See @repo-operating-model.md for the canonical repo operating rules.

# Claude Code Memory

This file exists so Claude Code can discover the repo's working rules automatically.

Treat `CLAUDE.md` as a thin compatibility layer, not a second source of truth. The canonical rules stay in `repo-operating-model.md`.

Also consult:

- `SPEC.md` for durable product or system truth
- `STATUS.md` for current operational reality
- `PLANS.md` for accepted future direction
- `INBOX.md` for untriaged intake

If this repo includes reusable workflows, then use `skills/<name>/SKILL.md` for bounded procedures and keep repo-wide policy in `repo-operating-model.md`.

When writing into `research/`, `records/`, or `upstream-intake/reports/`, consult the local `README.md` first and mirror its default shape or canonical example by default.

## Enforcement

When producing repo documents, you must enforce the repo's writing rules rather than treating them as suggestions.

- Use the canonical surface for the job.
- Follow the local `README.md` shape or explicit template when one exists.
- Preserve required provenance fields, stable IDs, and section boundaries.
- Do not replace normalized repo artifacts with freeform chat summaries.
- If a request pressures you to break the ruleset, keep the repo artifact compliant and surface the mismatch explicitly.
