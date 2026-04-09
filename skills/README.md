# Skills

This directory is optional.

Use it only when the target environment supports reusable procedural skills or workflows.

Each reusable workflow should live at `skills/<name>/SKILL.md`.

What lives here:

- `repo-orchestrator/`
  - Generic routing workflow for truth, status, plans, research, decisions, worklogs, and inbox capture.
- `daily-inbox-pressure-review/`
  - Focus-protecting daily triage for `IBX-*` capture and capture packets.
- `upstream-intake/`
  - Companion workflow for the optional upstream-review module inside `scaffold/`.

Keep skills procedural.
Do not duplicate the canonical rules from `scaffold/REPO.md` inside them.

Use `SKILL.md` for:

- step-by-step procedures
- required inputs and expected outputs
- escalation triggers
- links to supporting templates or reference docs

Do not use `SKILL.md` for:

- repo-wide policy
- general project truth
- local or personal preferences that belong in tool-specific memory files
