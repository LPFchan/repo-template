# Repo Template

This repo is a generic operating template for repos managed by one operator plus many agents.

It is designed for projects that want:

- canonical repo-local truth docs
- clean separation between plans, decisions, research, and execution logs
- low-friction intake from chat, messenger, or operator notes
- explicit provenance for agent-written artifacts
- a reusable upstream-intake package for forks and downstream products

This is broader than an upstream-intake kit.
Upstream intake is one subsystem inside the larger repo operating model.

## What This Repo Includes

- [repo-operating-model.md](repo-operating-model.md)
  - The canonical model for how an operator plus agents should manage repo truth, intake, research, decisions, and worklogs.
- [repo-templates/README.md](repo-templates/README.md)
  - Concrete starter templates for `SPEC.md`, `STATUS.md`, `PLANS.md`, `INBOX.md`, research memos, decisions, and agent worklogs.
- [upstream-intake/README.md](upstream-intake/README.md)
  - A reusable upstream-review package for forks, downstream products, or any repo that needs structured upstream maintenance.
- [repo-template.instructions.example.md](repo-template.instructions.example.md)
  - Example repo-level instruction file.
- [repo-template.skill.example.md](repo-template.skill.example.md)
  - Example procedural repo skill.
- [repo-template.prompt.example.md](repo-template.prompt.example.md)
  - Example thin launcher prompt.
- [recreate-repo-template.prompt.md](recreate-repo-template.prompt.md)
  - A prompt for recreating this whole system in another repo.

## Core Model

The repo operating model separates these layers on purpose:

1. Canonical truth
2. Accepted future direction
3. Curated exploration
4. Curated decisions
5. Raw operational activity
6. Recurring upstream maintenance

That separation is the point.
It keeps a repo from turning into a chat dump or a changelog masquerading as truth.

## Canonical Artifact Set

The starter artifact set is:

- `SPEC.md`
- `STATUS.md`
- `PLANS.md`
- `INBOX.md`
- `research/`
- `records/decisions/`
- `records/agent-worklogs/`
- `upstream-intake/`

## Provenance Model

This template assumes:

- `project-id` identifies the repo or workspace
- `agent-id` identifies one conversation or run, 1:1
- subagents get their own `agent-id`s
- deeper lineage is resolved off-Git from `agent-id`

Stable-ID-bearing artifacts should include:

- stable id
- `Opened: YYYY-MM-DD HH-mm-ss KST`
- `Recorded by agent: <agent-id>`

Recommended Git commit trailers:

- `Repo-Agent: <agent-id>`
- `Repo-Artifact: <artifact-id>`
- `Repo-Project: <project-id>`

Optional:

- `Repo-Parent-Agent: <agent-id>`
- `Repo-Role: orchestrator|worker|subagent`

## How To Reuse This Repo

1. Read [repo-operating-model.md](repo-operating-model.md).
2. Copy the starter files from [repo-templates/README.md](repo-templates/README.md) into the target repo.
3. Adapt the example prompt, skill, or instruction files to match the target environment.
4. If the target repo has upstream dependencies or is a fork, copy or adapt [upstream-intake/README.md](upstream-intake/README.md).
5. Seed the system with one real decision, one real worklog, and one real intake item so the repo starts grounded in actual work.

## Design Goal

This template is meant to be generic enough for any repo, but structured enough that an operator and many agents can keep working without losing the source of truth.
