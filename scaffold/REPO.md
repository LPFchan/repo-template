# Repo Operating Model

This document is the canonical repo contract for repo-template-style repos.

## Purpose

Use this model when a repo is managed by one operator plus many agents and you want the repo itself to remain legible over time.

The goal is simple:

- keep canonical truth in-repo
- keep noisy activity out of truth docs
- keep provenance explicit
- let the orchestrator route work without inventing new storage rules each time

This file is part of the ready-to-copy scaffold for adopted repos.

## Core Surfaces

Every repo using this system should separate these surfaces:

| Surface | Role | Mutability |
| --- | --- | --- |
| `SPEC.md` | Durable statement of what the project is supposed to be. | rewritten |
| `STATUS.md` | What is true right now operationally. | rewritten |
| `PLANS.md` | Accepted future direction that is not current truth yet. | rewritten |
| `INBOX.md` | Ephemeral capture waiting for triage. | append then purge |
| `research/` | Curated research memos worth keeping. | append by new file |
| `records/decisions/` | Durable decision records with rationale. | append-only by new file |
| `records/agent-worklogs/` | Execution history for runs, agents, and subagents. | append-only |
| `skills/` | Required procedural workflows for repeatable agent tasks. | edit by skill |
| `upstream-intake/` | Optional upstream review subsystem for repos that track an upstream. | append by cadence |

## Agent Compatibility Files

Some coding agents look for repo-root instruction files such as `AGENTS.md` or `CLAUDE.md`.

When a repo using this model includes them:

- they should act as entrypoints into the canonical rules, not competing policy documents
- they should stay short enough that they do not drift from `REPO.md`
- `AGENTS.md` should be the main editable agent-instructions file when both files exist
- `CLAUDE.md` should be a thin shim that points to `AGENTS.md` when the tool supports it
- `SKILL.md` stays separate because it defines a bounded reusable procedure, not repo-wide policy
- `skills/` should ship with adopted repos as repo-native procedural documentation, even when the agent runtime does not auto-load skills
- optional repo subsystems may have optional companion skills

Recommended split:

- `REPO.md`
  - canonical rules
- `AGENTS.md`
  - canonical editable agent-instructions file
- `CLAUDE.md`
  - Claude Code shim that points to `AGENTS.md`
- `skills/<name>/SKILL.md`
  - procedure for one repeatable workflow

## Artifact Writing Discipline

Macro structure is not enough on its own. Agents should not improvise document shape when the repo already defines one.

When writing repo artifacts:

- read the nearest canonical surface, directory `README.md`, and any explicit template before drafting
- if the local `README.md` includes a default shape or canonical example, follow it by default
- use the established section order only when the surface actually defines one and it helps the repo stay legible
- write normalized repo records, not external transcripts or stream-of-consciousness notes
- keep facts, decisions, open questions, and next steps clearly separated
- summarize evidence and outcomes instead of pasting raw command output unless the literal output is the artifact
- prefer short declarative bullets or paragraphs over vague filler

When a directory exists to store a durable artifact type, it should ideally include:

- a `README.md` that explains what belongs there
- a default shape or canonical example inside that same `README.md` when that artifact type benefits from it

That single guide helps future agents copy a house style instead of inventing one.

## Separation Rules

These boundaries are mandatory:

- `SPEC.md` is not a changelog.
- `STATUS.md` is not a transcript.
- `PLANS.md` is not a brainstorm dump.
- `INBOX.md` is not durable truth.
- `research/` is not raw execution history.
- `records/decisions/` is not the same as `records/agent-worklogs/`.
- Off-Git memory is not a substitute for repo-local canonical docs.

That separation gives future operators and future agents fast answers to different questions:

- What is the project? -> `SPEC.md`
- What is true right now? -> `STATUS.md`
- What future work is actually accepted? -> `PLANS.md`
- What did we learn from exploration? -> `research/`
- What did we decide and why? -> `records/decisions/`
- What actually happened during execution? -> `records/agent-worklogs/`

## Roles

### Operator

The operator is the final authority for product direction, escalation outcomes, and acceptance of truth changes.

### Orchestrator Agent

The orchestrator owns synthesis and routing.

It may:

- triage inbox items
- run daily inbox pressure reviews
- classify work into the right artifact layer
- update `SPEC.md`, `STATUS.md`, and `PLANS.md`
- create research memos
- create decision records
- append or create worklogs
- translate external capture into repo artifacts
- escalate non-obvious product, architecture, workflow, or policy calls

### Worker Agents

Worker agents execute bounded tasks.

They may:

- append to worklogs
- propose truth changes through the orchestrator
- create evidence, summaries, and implementation outputs

They should not update `SPEC.md`, `STATUS.md`, or `PLANS.md` directly unless the operator explicitly allows that flow.

### External Capture Surfaces

External capture surfaces are capture and control channels.

They may:

- create or append inbox capture
- request approvals
- deliver summaries
- surface blocked states

They must not write truth docs directly.

### Capture Packets

Raw external source events are immutable Off-Git events.
Do not treat every raw source event as a separate repo artifact.
Do not treat a full external-tool history as one giant inbox item.

Use capture packets as mutable working envelopes around one or more relevant raw source events.

A capture packet may be:

- appended as new related source events arrive
- edited into a clearer operator-intent summary
- split when it contains multiple independent asks
- merged when several source events are one meaningful thread
- summarized into `INBOX.md` as an `IBX-*`
- routed into durable repo artifacts after triage

Triage should happen per meaningful capture packet.
Routed repo artifacts should copy a short summary, the stable inbox ID, and any needed external provenance handle instead of relying on raw external source staying visible.

## Inbox Pressure Review

`INBOX.md` is an ephemeral scratch disk for untriaged capture.
It is not a backlog, roadmap, brainstorm archive, or project digest.

Run a daily inbox pressure review when the project receives substantial capture.
This review is focus-protecting triage.
It is not an unconditional digest of every random idea.

During the review:

- group related `IBX-*` entries and capture packets into meaningful clusters
- identify stale, duplicate, low-confidence, noisy, or "maybe later" capture
- ask whether each meaningful cluster should route, research, plan, discard, or stay held
- promote only items that survived triage and have an accepted destination
- report counts or clusters of held, discarded, stale, or noisy capture instead of summarizing every low-signal item
- preserve `IBX-*` as a permanent provenance ID even if the inbox line is deleted

Do not update `SPEC.md`, `STATUS.md`, `PLANS.md`, `research/`, or `records/decisions/` directly from raw inbox pressure.
The orchestrator or operator-approved routing step owns promotion.

## Promotion Discipline

Promotion should be sparse.
Do not mirror one evolving thought into every repo surface.

Raw shaping may stay in external capture, generic notes, off-Git capture packets, or `INBOX.md` while the thought is still forming.
Repo artifacts are a refinery: each layer should receive only the part that belongs there, when it is ready.

Use each layer for its distinct job:

- `INBOX.md`
  - ephemeral routed capture
- `research/`
  - reusable exploration, evidence, framing, rejected paths, and open questions
- `records/decisions/`
  - meaningful accepted choices and why the winning choice won
- `PLANS.md`
  - accepted future work that survived triage
- `SPEC.md`
  - concise durable product or system truth after the argument is settled
- `STATUS.md`
  - current operational reality
- `upstream-intake/`
  - upstream review, upstream conflict, carry-forward, and operator escalation for upstream-related choices
- `records/agent-worklogs/`
  - execution history, not truth, decision, plan, or research mirrors

A research memo may remain research forever.
A decision record should exist only when a real product, architecture, workflow, trust, upstream, or repo-operating choice has been made.
`SPEC.md`, `STATUS.md`, and `PLANS.md` should receive concise outcomes, not copied debate.

One task may touch multiple layers, but each touched layer must have its own distinct job.

## Orchestrator Routing Ladder

When new work arrives, the orchestrator should classify it in this order:

1. Is this untriaged capture?
   - Route to `INBOX.md`.
2. Is this recurring upstream review?
   - Route to `upstream-intake/`.
3. Is this durable truth about what the project is?
   - Route to `SPEC.md`.
4. Is this current operational reality?
   - Route to `STATUS.md`.
5. Is this accepted future direction?
   - Route to `PLANS.md`.
6. Is this reusable exploration or horizon-expansion work?
   - Route to `research/`.
7. Is this a meaningful decision with rationale?
   - Route to `records/decisions/`.
8. Is this execution history?
   - Route to `records/agent-worklogs/`.

One task may legitimately touch multiple layers. For example:

- a research session can create `RSH-*` plus a `LOG-*`
- a product choice can create `DEC-*` and update `PLANS.md`
- implementation progress can append `LOG-*` and update `STATUS.md`

Touch multiple layers only when each layer receives distinct information.
Do not copy the same evolving thought into research, decision, plan, spec, status, upstream, and log surfaces.

## Write Rules

- `SPEC.md`, `STATUS.md`, and `PLANS.md` should be updated only by the operator or orchestrator.
- `INBOX.md` is an aggressive scratch disk. Purge entries once they are reflected elsewhere or explicitly discarded.
- Daily inbox review should reduce pressure by clustering, routing, holding, or purging capture; it should not generate a larger digest by default.
- `research/` keeps curated findings only.
- `records/decisions/` is append-only by new decision file.
- `records/agent-worklogs/` is append-only by appended entries or, when clarity requires it, a new log file.
- `upstream-intake/` should preserve its own paired internal-record and operator-brief workflow.
- Truth docs should reflect the latest accepted state, not every intermediate thought.

### Worklog Reuse Policy

Do not create a new `LOG-*` just to satisfy provenance.

Append to the latest relevant `LOG-*` when:

- the same workstream, goal, or blocker is still in scope
- the new work is part of the same execution thread
- an additional entry preserves clarity

Create a new `LOG-*` only when:

- the work is a distinct new stream or bounded task
- a new agent or subagent is doing materially separate execution
- the prior log would become confusing, bloated, or misleading if reused
- the new work deserves its own execution record for future retrieval

## Stable IDs

This model assumes:

- `project-id` identifies the repo or workspace
- `agent-id` identifies one conversation or run, 1:1
- subagents receive their own `agent-id`
- Off-Git systems resolve parent-child lineage, messages, events, and commit history from `agent-id`

Recommended prefixes:

- `IBX-YYYYMMDD-NNN`
- `RSH-YYYYMMDD-NNN`
- `DEC-YYYYMMDD-NNN`
- `LOG-YYYYMMDD-NNN`
- `UPS-YYYYMMDD-NNN`

Numbering is per day and per artifact type. Any agent may claim the next ID by checking the least available `NNN`.

Every stable-ID-bearing artifact should open with:

- `Opened: YYYY-MM-DD HH-mm-ss KST`
- `Recorded by agent: <agent-id>`

## Commit Provenance

After a repo adopts this system, every commit should include these trailers:

- `project: <project-id>`
- `agent: <agent-id>`
- `role: orchestrator|worker|subagent|operator`
- `artifacts: <artifact-id>[, <artifact-id>...]`

Rules:

- `artifacts:` may list more than one stable ID, comma-separated.
- A normal commit should always reference at least one relevant artifact, newly created or updated.
- Artifact-less commits should be treated as bootstrap or migration exceptions only.
- The commit side and the repo-artifact side should reinforce the same provenance graph.

Normal commits do not require a brand-new `LOG-*`.

- Prefer appending to an existing relevant `LOG-*` when the same workstream is continuing.
- Create a new `LOG-*` only when it improves clarity.
- Commits may reference `LOG-*`, `DEC-*`, `RSH-*`, `UPS-*`, or another relevant artifact type as appropriate.

## Commit-Time Enforcement

If the repo enables commit hooks, every attempted commit should be checked against these provenance rules.

Recommended minimum enforcement:

- reject commits that do not include `project:`, `agent:`, `role:`, and `artifacts:`
- reject roles outside `orchestrator|worker|subagent|operator`
- reject empty or malformed artifact ID lists
- allow explicit bootstrap or migration exceptions

The goal is not perfect policy automation. The goal is to stop obviously non-compliant commits before they land.

Best practice is to use both:

- local git hooks for fast feedback before the commit is created
- CI for remote re-validation on push or pull request

## Off-Git Provenance

Repo artifacts stay lightweight on purpose.

In-repo provenance answers:

- what artifact this is
- when it was opened
- which agent wrote the record

The Off-Git runtime should answer:

- which conversation or run the `agent-id` maps to
- whether the agent was top-level or a subagent
- which source events produced the artifact
- which commits belong to that `agent-id`

## Scaffold Rule

`scaffold/` is a ready-to-copy repo skeleton, not a loose library of files to cherry-pick casually.

Use it when you want a managed repo to share one canonical layout so humans and agents know exactly where work belongs.

In this template, scaffold files live under `scaffold/`.
After adoption, the scaffold contents belong at the target repo root.
For example, `scaffold/skills/repo-orchestrator/SKILL.md` becomes `skills/repo-orchestrator/SKILL.md` in the adopted repo.
