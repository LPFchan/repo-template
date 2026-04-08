---
name: repo-orchestrator
description: "Route work into the correct artifact layer in a repo that uses Repo Template."
argument-hint: "Task, intake item, or maintenance request"
---

# Repo Orchestrator

Use this skill with:

- [../../repo-operating-model.md](../../repo-operating-model.md)
- [../../scaffold/README.md](../../scaffold/README.md)

## What This Skill Produces

- correctly routed repo artifacts
- clear separation between truth, plans, research, decisions, and logs
- stable IDs plus lightweight provenance
- operator escalation only when a real judgment call exists

## Procedure

1. Classify the work in routing order.
   - Is this untriaged intake?
   - Is this recurring upstream review?
   - Is this durable truth?
   - Is this current operational reality?
   - Is this accepted future direction?
   - Is this reusable research?
   - Is this a durable decision?
   - Is this execution history?

2. Route it to the correct artifact layer.
   - `SPEC.md`
   - `STATUS.md`
   - `PLANS.md`
   - `INBOX.md`
   - `research/`
   - `records/decisions/`
   - `records/agent-worklogs/`
   - `upstream-intake/`

3. Assign stable IDs when needed.
   - `IBX-*`
   - `RSH-*`
   - `DEC-*`
   - `LOG-*`
   - `UPS-*`
   - Use the least available `NNN` for that date and artifact type.

4. Write the artifact with provenance.
   - Include `Opened: YYYY-MM-DD HH-mm-ss KST`
   - Include `Recorded by agent: <agent-id>`

5. Preserve the separation rules.
   - Do not write speculation straight into `PLANS.md`.
   - Do not let worklogs masquerade as decisions.
   - Do not let inbox entries become long-term truth.
   - Do not treat research memos as raw transcripts.

6. If the task crosses layers, create multiple artifacts deliberately.
   - Example: `RSH-*` plus `LOG-*`
   - Example: `DEC-*` plus `PLANS.md`
   - Example: `LOG-*` plus `STATUS.md`

7. If Git commits are created, add commit trailers.
   - `project: <project-id>`
   - `agent: <agent-id>`
   - `role: orchestrator|worker|subagent|operator`
   - `artifacts: <artifact-id>[, <artifact-id>...]`

8. If the task is recurring upstream maintenance, use `upstream-intake/` instead of inventing a parallel workflow.

## Escalation Triggers

Escalate instead of guessing when the work:

- changes durable product or system truth
- changes public contracts or compatibility posture
- resolves a real policy conflict
- changes operator-facing workflow in a non-obvious way
- overrides a security-sensitive upstream change

## Quality Bar

- clear routing
- clear provenance
- clean separation of layers
- reusable artifacts instead of chat-only outcomes
