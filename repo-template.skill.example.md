---
name: repo-orchestrator
description: "Example skill for routing work and maintaining canonical repo artifacts in a repo that uses Repo Template."
argument-hint: "Task, intake item, or maintenance request"
---

# Repo Orchestrator

Use this skill when a repo is managed through canonical truth docs, plans, research, decisions, worklogs, and optional upstream-intake review.

## What This Skill Produces

- correctly routed repo artifacts
- explicit separation between truth, plans, research, decisions, and logs
- stable IDs and authoring metadata
- operator escalation only when the decision actually needs it

## Procedure

1. Identify the work unit.
   - Is this truth maintenance, planning, exploration, execution, or upstream review?

2. Route it to the correct artifact layer.
   - `SPEC.md`
   - `STATUS.md`
   - `PLANS.md`
   - `INBOX.md`
   - `research/`
   - `records/decisions/`
   - `records/agent-worklogs/`
   - `upstream-intake/`

3. Assign the right stable ID when the artifact needs one.
   - `IBX-*`
   - `RSH-*`
   - `DEC-*`
   - `LOG-*`
   - `UPS-*`

4. Write the artifact with provenance.
   - Include `Opened: YYYY-MM-DD HH-mm-ss KST`
   - Include `Recorded by agent: <agent-id>`

5. Preserve the separation rules.
   - Do not write speculation straight into `PLANS.md`.
   - Do not let execution logs masquerade as decisions.
   - Do not let inbox entries become long-term truth.

6. If Git commits are created, add commit trailers.
   - `Repo-Agent`
   - `Repo-Artifact`
   - `Repo-Project`

7. If the task is recurring upstream maintenance, use `upstream-intake/` instead of inventing a parallel workflow.

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
