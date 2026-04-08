You are implementing a generic repo operating system for a repo managed by one operator plus many agents.

Goal:
Create a repo-native system that keeps truth, status, plans, research, decisions, execution logs, and optional upstream review clearly separated but tightly linked.

What to build:

1. One canonical `repo-operating-model.md` document that acts as the rules layer.
2. One ready-to-copy `scaffold/` directory containing:
   - optional thin `AGENTS.md` and `CLAUDE.md` compatibility files for tools that look for repo-root instructions
   - `SPEC.md`
   - `STATUS.md`
   - `PLANS.md`
   - `INBOX.md`
   - `research/`
   - `records/decisions/`
   - `records/agent-worklogs/`
   - optional-but-recommended `upstream-intake/`
3. Optional `skills/` only if the target environment supports reusable procedural skills.
4. One provenance model using stable IDs, KST opened timestamps, agent IDs, and commit trailers.
5. Optional local git hook enforcement for commit provenance when the target repo wants commit-time checks.
6. Optional CI enforcement for commit provenance on push and pull request when the target repo wants remote checks.

Behavioral requirements:

- Do not treat the repo like a transcript dump.
- Do not mix truth, plans, research, decisions, and logs into one document type.
- The orchestrator should decide where incoming work belongs.
- Messenger or chat intake must not write truth docs directly.
- Research must stay separate from raw execution logs.
- Decisions must stay separate from raw execution logs.
- Upstream intake should be one subsystem of the overall repo model, not the whole system.

Stable ID requirements:

- `IBX-*` for inbox intake
- `RSH-*` for research
- `DEC-*` for decisions
- `LOG-*` for worklogs
- `UPS-*` for upstream review
- numbering is per day and per artifact type
- each stable-ID-bearing artifact should include:
  - `Opened: YYYY-MM-DD HH-mm-ss KST`
  - `Recorded by agent: <agent-id>`

Commit provenance requirements:

- after adoption, every commit should include:
  - `project: <project-id>`
  - `agent: <agent-id>`
  - `role: orchestrator|worker|subagent|operator`
  - `artifacts: <artifact-id>[, <artifact-id>...]`
- artifact-less commits should be bootstrap or migration exceptions only

Commit hook option:

- when requested, add a tracked `commit-msg` hook plus validator script that checks commit provenance trailers
- the hook should allow explicit bootstrap or migration exceptions

CI option:

- when requested, add a workflow that checks every commit in the pushed or pull-request range
- CI should reuse the same provenance rules as the local hook

Structure requirements:

- keep the operating rules in one canonical document
- make `scaffold/` the copyable skeleton, not a loose library of snippets
- allow thin compatibility entrypoints such as `AGENTS.md` or `CLAUDE.md`, but keep them subordinate to the canonical rules
- close the shape gap for durable artifact directories by making each local `README.md` define both the rules and a canonical example shape when practical
- keep optional procedural skills outside the scaffold
- avoid separate instruction and launcher-prompt layers unless the target environment truly needs them

Implementation steps:

1. Inspect the target repo and identify where process docs should live.
2. Create `repo-operating-model.md`.
3. Create `scaffold/` with the canonical repo surfaces.
4. Add `upstream-intake/` inside the scaffold when the repo needs recurring upstream review.
5. Add `skills/` only if the environment supports them.
6. Seed the system with at least one real artifact when practical.
7. Validate that the routing boundaries are explicit.
8. Validate that commit provenance and artifact provenance reinforce each other.
9. If commit-time enforcement was requested, wire in the hook and document installation.
10. If remote enforcement was requested, add the CI workflow and document how it relates to the local hook.
11. Summarize what is canonical, what is optional, and what should be copied verbatim.

Quality bar:

- generic, not product-specific
- concrete, not vague
- opinionated enough for agents to route work consistently
- clean separation of truth, plans, research, decisions, and logs
- lightweight repo-local provenance with deeper Off-Git lookup through `agent-id`
