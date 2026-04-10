You are implementing a generic repo operating system for a repo managed by one operator plus many agents.

Goal:
Create a repo-native system that keeps truth, status, plans, research, decisions, commit-backed execution history, and optional upstream review clearly separated but tightly linked.

What to build:

1. One canonical `REPO.md` document inside `scaffold/` that acts as the rules layer for adopted repos.
2. One ready-to-copy `scaffold/` directory containing:
   - optional thin `AGENTS.md` and `CLAUDE.md` compatibility files for tools that look for repo-root instructions
   - `SPEC.md`
   - `STATUS.md`
   - `PLANS.md`
   - `INBOX.md`
   - `research/`
   - `records/decisions/`
   - required baseline `skills/`
   - optional `upstream-intake/`
   - optional `skills/upstream-intake/` companion workflow when `upstream-intake/` is enabled
3. One provenance model using stable IDs, KST opened timestamps for file-backed artifacts, agent IDs, and commit-backed `LOG-*` execution records.
4. Optional local git hook enforcement for commit provenance when the target repo wants commit-time checks.
5. Optional CI enforcement for commit provenance on push and pull request when the target repo wants remote checks.

Behavioral requirements:

- Do not treat the repo like a transcript dump.
- Do not mix truth, plans, research, decisions, and execution records into one document type.
- The orchestrator should decide where incoming work belongs.
- External capture must not write truth docs directly.
- Inbox capture is ephemeral pressure, not a backlog.
- Daily inbox pressure review must cluster, route, research, plan, discard, or leave capture instead of producing an unconditional digest.
- External capture should be grouped into meaningful capture packets before repo routing.
- Research must stay separate from raw execution history.
- Decisions must stay separate from raw execution history.
- Upstream intake should be one subsystem of the overall repo model, not the whole system.

Stable ID requirements:

- `IBX-*` for inbox capture
- `RSH-*` for research
- `DEC-*` for decisions
- `LOG-*` for commit-backed execution records
- `UPS-*` for upstream review
- file-backed IDs use per-day numbering
- `LOG-*` uses `LOG-YYYYMMDD-HHMMSS-<agent-suffix>`
- each file-backed stable-ID-bearing artifact should include:
  - `Opened: YYYY-MM-DD HH-mm-ss KST`
  - `Recorded by agent: <agent-id>`

Commit provenance requirements:

- after adoption, every commit should include:
  - `project: <project-id>`
  - `agent: <agent-id>`
  - `role: orchestrator|worker|subagent|operator`
  - `commit: LOG-...[, LOG-...]`
- `artifacts:` is optional
- `artifacts:` must not contain any `LOG-*`
- artifact-less commits should be bootstrap or migration exceptions only
- a normal commit is itself the canonical execution record
- additional `LOG-*` ids in `commit:` mean the landed commit absorbs earlier execution records whose separate commits will not remain separate landed history
- `--amend` and `rebase` preserve existing `LOG-*` ids
- merge commits mint their own primary `LOG-*`
- if cherry-pick relocates work and the original will not also land, it may keep the same primary `LOG-*`
- if both original and cherry-picked commits could land, the later commit must mint a new primary `LOG-*`
- new `LOG-*` ids are claimed by scanning the current branch plus the default branch and bumping the KST timestamp by one second until unique
- every normal commit body must include:
  - `timestamp: YYYY-MM-DD HH-mm-ss KST`
  - `changes:`
  - `rationale:`
  - `checks:`
  - optional `notes:`

Commit hook option:

- when requested, add a tracked `commit-msg` hook plus validator script that checks the commit-backed execution contract
- the hook should allow explicit bootstrap or migration exceptions

CI option:

- when requested, add a workflow that checks every commit in the pushed or pull-request range
- CI should reuse the same provenance rules as the local hook

Structure requirements:

- keep the operating rules in one canonical document
- make `scaffold/` the copyable skeleton, not a loose library of snippets
- allow thin compatibility entrypoints such as `AGENTS.md` or `CLAUDE.md`, but keep them subordinate to the canonical rules
- when both exist, make `AGENTS.md` the editable instructions file and `CLAUDE.md` the shim that points to it
- close the shape gap for durable artifact directories by making each local `README.md` define both the rules and a canonical example shape when practical
- keep baseline procedural skills inside the scaffold so they deploy as repo-root `skills/`
- keep upstream review optional; omit both `upstream-intake/` and `skills/upstream-intake/` when the repo does not track an upstream
- avoid separate instruction and launcher-prompt layers unless the target environment truly needs them
- do not add a second backlog artifact for inbox review
- do not add a parallel file-based execution-history surface

Implementation steps:

1. Inspect the target repo and identify where process docs should live.
2. Create `scaffold/REPO.md`.
3. Create `scaffold/` with the canonical repo surfaces, including baseline `skills/`.
4. Add `upstream-intake/` and its companion `skills/upstream-intake/` skill inside the scaffold only when the repo needs recurring upstream review.
5. Validate that the scaffold contents are meant to copy to the target repo root. For example, `scaffold/skills/` in the template becomes root `skills/` after adoption.
6. Seed the system with at least one real artifact when practical.
7. Validate that the routing boundaries are explicit.
8. Validate that commit provenance and artifact provenance reinforce each other.
9. Validate that inbox pressure review is focus-protecting triage, not a giant digest of random ideas.
10. If commit-time enforcement was requested, wire in the hook and document installation.
11. If remote enforcement was requested, add the CI workflow and document how it relates to the local hook.
12. Summarize what is canonical, what is optional, and what should be copied verbatim.

Quality bar:

- generic, not product-specific
- concrete, not vague
- opinionated enough for agents to route work consistently
- clean separation of truth, plans, research, decisions, and logs
- lightweight repo-local provenance with deeper Off-Git lookup through `agent-id`
