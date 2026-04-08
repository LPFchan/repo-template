You are implementing a generic repo operating system for a repo managed by one operator plus many agents.

Goal:
Create a repo-native system that keeps canonical truth, accepted plans, exploratory research, curated decisions, execution logs, and optional upstream-intake review clearly separated but strongly linked.

What to build:

1. A canonical repo operating model document.
2. Starter templates for:
   - `SPEC.md`
   - `STATUS.md`
   - `PLANS.md`
   - `INBOX.md`
   - `research/`
   - `records/decisions/`
   - `records/agent-worklogs/`
3. A reusable upstream-intake package as a subdirectory.
4. Example instruction, skill, and thin prompt files when the target repo supports them.
5. A provenance model using stable IDs, opened timestamps, agent ids, and Git commit trailers.

Behavioral requirements:

- Do not treat the repo like a transcript dump.
- Do not mix truth, plans, research, decisions, and logs into one document type.
- The orchestrator layer should decide where incoming work belongs.
- Messenger or chat intake should not directly write truth docs.
- Research should be separate from raw execution logs.
- Decisions should be separate from execution logs.
- Upstream intake should be one subsystem of the overall repo model, not the whole system.

Required artifact layers:

- `SPEC.md`
- `STATUS.md`
- `PLANS.md`
- `INBOX.md`
- `research/`
- `records/decisions/`
- `records/agent-worklogs/`
- `upstream-intake/`

Provenance requirements:

- stable artifact ids such as `IBX-*`, `RSH-*`, `DEC-*`, `LOG-*`, and `UPS-*`
- `Opened: YYYY-MM-DD HH-mm-ss KST`
- `Recorded by agent: <agent-id>`
- Git commit trailers:
  - `Repo-Agent: <agent-id>`
  - `Repo-Artifact: <artifact-id>`
  - `Repo-Project: <project-id>`

Structure requirements:

- Make one root document the canonical repo operating model.
- Put starter templates in a dedicated template directory.
- Put upstream review in a dedicated subpackage.
- Keep prompts thin.
- Keep skills procedural.
- Keep detailed rules in one canonical layer instead of duplicating them everywhere.

Implementation steps:

1. Inspect the target repo and identify where process docs belong.
2. Create the repo operating model.
3. Create the starter templates.
4. Create the upstream-intake subpackage.
5. Add example instruction, skill, and prompt entrypoints if the repo supports them.
6. Seed the system with at least one real artifact in each meaningful layer when possible.
7. Validate that truth, plans, research, decisions, and logs are clearly separated.
8. Validate that provenance is explicit and lightweight in-repo.
9. Summarize what is canonical and how future agents should use it.

Deliverables:

- root operating model
- starter template package
- upstream-intake package
- example instruction, skill, and prompt files
- provenance rules

Quality bar:

- generic, not product-specific
- concrete, not vague
- reusable, not one-off
- clean separation of artifact layers
- lightweight repo-local provenance with stronger off-Git lookup
