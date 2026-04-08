# Repo Operating Model

## Purpose

This document defines a generic repo-local operating model for projects managed through one operator plus many agents.

The goal is to make each repo understandable, writable, and auditable without letting canonical truth dissolve into chat history, ad hoc notes, or noisy execution logs.

Concrete starter templates for these repo artifacts live in `repo-templates/`.
The reusable upstream review package lives in `upstream-intake/`.

## Core Principle

Each project repo should separate these things on purpose:

1. Canonical truth
2. Accepted future direction
3. Curated exploration
4. Curated decisions
5. Raw operational activity
6. Recurring upstream maintenance

The system should keep all six connected, but it should not store them in the same document type.

## Canonical Artifact Set

Every repo using this model should have these canonical surfaces:

| Surface | Role | Truth level | Mutability |
| --- | --- | --- | --- |
| `SPEC.md` | The canonical statement of what the project is supposed to be. | highest | rewritten as truth changes |
| `STATUS.md` | The current operational state of the project, including active phases, progress, blockers, and near-term reality. | high | rewritten as state changes |
| `PLANS.md` | Accepted future direction that survived triage but is not yet current truth. | medium-high | rewritten as plans change |
| `INBOX.md` | Ephemeral scratch disk for intake waiting to be triaged. | low | append during intake, purge after routing |
| `research/` | Curated exploratory memos that are useful to retain but are not automatically accepted direction. | medium | append by new research memo |
| `upstream-intake/` | Canonical upstream review system, including internal records and operator briefs. | high for upstream policy | append by cadence |
| `records/decisions/` | Curated durable decisions with rationale and consequences. | high | append-only by new decision record |
| `records/agent-worklogs/` | Append-only execution history for sessions, agents, and subagents. | operational | append-only |

## What Belongs Where

### `SPEC.md`

`SPEC.md` answers: what is this project supposed to be?

It should contain:

- product thesis
- primary user-facing object
- canonical interaction model
- major system responsibilities
- important invariants and non-goals
- rules that should remain true across implementation phases

It should not contain:

- temporary blockers
- untriaged ideas
- verbose execution history
- week-by-week status narration

### `STATUS.md`

`STATUS.md` answers: what is true right now?

It should contain:

- current implementation phases or tracks
- in-progress work
- known blockers and risks
- current repo posture
- recent meaningful changes to project reality
- what is active, paused, or done

It should not contain:

- raw inbox capture
- speculative ideas that were not accepted
- full reasoning transcripts
- permanent design truth that belongs in `SPEC.md`

### `PLANS.md`

`PLANS.md` answers: what future direction has been accepted, but is not current truth yet?

It should contain:

- accepted future initiatives
- sequenced future work
- deferred but endorsed plans
- product bets that survived triage

It should not contain:

- raw brainstorm dump
- messenger transcripts
- day-to-day execution status
- rationale that belongs in a decision record

### `INBOX.md`

`INBOX.md` answers: what came in that has not been fully routed yet?

It should contain:

- quick ideas from the operator
- messenger intake
- reminders
- rough follow-ups
- items captured by agents that need triage

It is intentionally a scratch disk, not a record of truth.

### `research/`

`research/` answers: what did we learn from repo-contextual exploration that is worth keeping, even if it is not accepted direction yet?

It should contain:

- research question
- why the exploration belongs to this repo
- relation to current direction
- findings
- promising directions
- dead ends or discarded paths
- recommended routing
- related ids

It should not contain raw execution trace that belongs in `records/agent-worklogs/`.

### `upstream-intake/`

`upstream-intake/` answers: what changed upstream, what did we decide, and what needs operator attention?

### `records/decisions/`

`records/decisions/` answers: what meaningful product, architecture, or workflow decision was made, and why?

It should contain only decisions that materially affect the project.

### `records/agent-worklogs/`

`records/agent-worklogs/` answers: what did a given session, agent, or subagent actually do?

It should contain:

- task summaries
- actions taken
- files touched
- commands or checks run
- outputs produced
- blockers encountered
- decisions referenced

## Separation Rules

The following separations are mandatory:

- `SPEC.md` is not a changelog.
- `STATUS.md` is not a transcript.
- `PLANS.md` is not a scratchpad.
- `INBOX.md` is not durable truth.
- `research/` is not the same as `records/agent-worklogs/`.
- `records/decisions/` is not the same as `records/agent-worklogs/`.
- off-Git operational memory is not a substitute for repo-local canonical docs.

This separation is good hygiene because it lets future operators and future agents answer different questions quickly:

- “What is the project?” -> `SPEC.md`
- “Where are we now?” -> `STATUS.md`
- “What are we planning next?” -> `PLANS.md`
- “What did we learn from exploration?” -> `research/`
- “What decision did we make?” -> `records/decisions/`
- “What actually happened during execution?” -> `records/agent-worklogs/`

## Role Model

### Operator

The operator is the final authority for product direction, escalations, and truth acceptance.

### Orchestrator Agent

The orchestrator agent owns synthesis and routing.

It may:

- triage inbox items
- classify whether an intake belongs to research, implementation, planning, or truth updates
- create or update repo-local canonical docs
- create research memos
- create decision records
- create or append worklogs
- translate messenger intake into repo artifacts
- escalate high-risk or product-shaping choices to the operator

It should be the default writer of `SPEC.md`, `STATUS.md`, and `PLANS.md` when changes are made by agents.

### Worker Agents

Worker agents execute bounded tasks.

They may:

- append to their worklogs
- propose changes to truth docs through the orchestrator
- attach evidence, summaries, and outputs

They must not directly update `SPEC.md`, `STATUS.md`, or `PLANS.md` unless the operator explicitly approves that flow.

### Messenger Surfaces

Messenger channels are intake and control surfaces.

They may:

- create inbox items
- request approvals
- deliver summaries
- surface blocked states
- return links or references to routed artifacts

They must not directly write canonical truth docs.

## Stable ID System

Every routed artifact should carry stable IDs so provenance survives after `INBOX.md` is cleaned up.

For this operating model:

- `project-id` identifies the repo or workspace
- `agent-id` identifies one conversation or run, 1:1
- subagents receive their own `agent-id`s
- off-Git lineage resolves whether an `agent-id` was a top-level run or a child run, plus parent-child relationships between agents

Recommended prefixes:

- `IBX-YYYYMMDD-NNN` for inbox intake items
- `RSH-YYYYMMDD-NNN` for research memos
- `DEC-YYYYMMDD-NNN` for decisions
- `LOG-YYYYMMDD-NNN` for agent worklogs
- `UPS-YYYYMMDD-NNN` for upstream intake cycles or records

Every stable-ID-bearing artifact should open with at least:

- `Opened: YYYY-MM-DD HH-mm-ss KST`
- `Recorded by agent: <agent-id>`

Stable ID alone is enough to connect repo artifacts to each other.
It is not enough, by itself, to pinpoint the exact off-Git conversation or message that led to a change.
For exact attribution, the stable ID should be paired with timestamp and `agent-id`.
The off-Git runtime should resolve deeper provenance, including messages, events, subagent lineage, and Git actions, from that `agent-id`.

## Git Provenance Reinforcement

Git history should reinforce the same provenance model from the commit side.

Recommended commit trailers:

- `Repo-Agent: <agent-id>`
- `Repo-Artifact: <IBX|RSH|DEC|LOG|UPS-id>`
- `Repo-Project: <project-id>`

Optional trailers:

- `Repo-Parent-Agent: <agent-id>`
- `Repo-Role: orchestrator|worker|subagent`

## Routing Policy

Every intake item should be triaged into one or more of the following paths:

| Intake shape | Destination |
| --- | --- |
| rough idea or unprocessed reminder | `INBOX.md` |
| repo-contextual exploration worth retaining | `research/` |
| accepted future direction | `PLANS.md` |
| current operational reality or active blocker | `STATUS.md` |
| durable product or system truth | `SPEC.md` |
| meaningful choice with rationale | `records/decisions/` |
| actual execution trace | `records/agent-worklogs/` |
| upstream review or sync decision | `upstream-intake/` |

One intake item may route to multiple destinations.

## Write Policy

### Canonical Truth Docs

`SPEC.md`, `STATUS.md`, and `PLANS.md` may be updated only by:

- the operator
- the orchestrator agent
- an operator-approved automated flow acting in the orchestrator role

### `INBOX.md`

`INBOX.md` may be written by:

- messenger intake bridges
- the operator
- the orchestrator agent

It should be treated as ephemeral scratch state.

### Decision Records

Decision records are append-only.
If a previous decision changes, create a new `DEC-*` record that supersedes the old one and link them explicitly.

### Agent Worklogs

Agent worklogs are append-only.
If correction is needed, append a correction entry or follow-up note instead of overwriting execution history.

## Reflection Rule

Messenger intake never writes truth docs directly.

Instead:

1. intake is captured into off-Git operational memory
2. a short repo-local handle is written to `INBOX.md`
3. the orchestrator triages the item
4. accepted information is reflected into the right durable repo artifact
5. the inbox entry is purged once reflection is complete

## Minimal Document Contracts

Every stable-ID-bearing file or entry should include:

- stable id
- opened timestamp in `YYYY-MM-DD HH-mm-ss KST`
- recorded by agent id
- related ids

Then the specific artifact adds its own required fields.

## Anti-Patterns To Avoid

- using `INBOX.md` as a long-term memory dump
- putting speculative ideas straight into `PLANS.md`
- using `STATUS.md` as a substitute for `SPEC.md`
- treating research memos like raw execution logs
- treating every exploratory session like accepted project direction
- burying important decisions only inside worklogs
- rewriting worklogs into hindsight-clean stories
- letting worker agents directly edit truth docs without orchestrator control
- storing all meaningful project context only in off-Git chat history

## Practical Outcome

If this model is followed, a repo gains:

- a clear source of truth
- a clean current-state view
- a curated plan surface
- an ephemeral intake surface
- a reusable exploration surface
- durable decision memory
- auditable execution history
- traceable upstream maintenance
