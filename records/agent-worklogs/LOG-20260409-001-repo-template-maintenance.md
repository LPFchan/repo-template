# LOG-20260409-001: repo-template maintenance

Opened: 2026-04-09 20-02-40 KST
Recorded by agent: codex

## Metadata

- Run type: orchestrator
- Goal: maintain repo-template's operating model without adding unnecessary artifact churn
- Related ids: LOG-20260409-001

## Task

Maintain repo-template and keep a compact execution record for repo-operating-model changes.

## Scope

- In scope: template docs, scaffold contract, agent guidance, procedural skills, lightweight verification, commit provenance
- Out of scope: product-specific policy for any adopted repo

## Entry 2026-04-09 20-02-40 KST

- Action: added sparse promotion / refinery discipline to the repo-template contract
- Files touched: `scaffold/REPO.md`, `scaffold/AGENTS.md`, `skills/repo-orchestrator/SKILL.md`, `README.md`, `records/agent-worklogs/LOG-20260409-001-repo-template-maintenance.md`
- Checks run: `git diff --check`; `sh -n scripts/check-commit-standards.sh scripts/check-commit-range.sh scripts/install-hooks.sh`; sample `scripts/check-commit-standards.sh` invocation
- Output: clarified that evolving thoughts can stay in external capture, inbox, or research and should not be mirrored into every canonical surface
- Blockers: none
- Next: commit with `LOG-20260409-001` and push

## Entry 2026-04-09 20-08-07 KST

- Action: renamed current template-facing mutable capture vocabulary to capture packet
- Files touched: `scaffold/REPO.md`, `scaffold/INBOX.md`, `skills/daily-inbox-pressure-review/SKILL.md`, `README.md`, `records/agent-worklogs/LOG-20260409-001-repo-template-maintenance.md`
- Checks run: `git diff --check`; terminology search across README, scaffold, and skills
- Output: living policy, inbox field names, and skill prompts now use capture packet; historical worklog traces were left untouched
- Blockers: none
- Next: commit with `LOG-20260409-001` when the template change set is ready

## Entry 2026-04-09 20-11-03 KST

- Action: made capture vocabulary generic across the template
- Files touched: `README.md`, `recreate-prompt.md`, `scaffold/AGENTS.md`, `scaffold/INBOX.md`, `scaffold/REPO.md`, `skills/README.md`, `skills/daily-inbox-pressure-review/SKILL.md`, `skills/repo-orchestrator/SKILL.md`, `records/agent-worklogs/LOG-20260409-001-repo-template-maintenance.md`
- Checks run: `rg -n -i "messenger|voice-note|voice note|\\bchat\\b|intake span|intake spans|raw message|source event ids|Active Intake|inbox intake" README.md recreate-prompt.md scaffold/REPO.md scaffold/INBOX.md scaffold/AGENTS.md skills/README.md skills/daily-inbox-pressure-review/SKILL.md skills/repo-orchestrator/SKILL.md`; `git diff --check`; `sh -n scripts/check-commit-standards.sh scripts/check-commit-range.sh scripts/install-hooks.sh`; sample `scripts/check-commit-standards.sh` invocation
- Output: moved live policy wording toward external capture, raw source events, and capture packets; preserved stable repo names such as `INBOX.md`, `IBX-*`, and `upstream-intake/`
- Blockers: none
- Next: commit with `LOG-20260409-001` and push
