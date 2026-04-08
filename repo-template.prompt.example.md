---
name: "Repo Orchestrator"
description: "Example thin launcher prompt for routing work and maintaining a repo that uses Repo Template."
argument-hint: "Task, intake item, or maintenance request"
agent: "agent"
---

Run the repo operating workflow for the provided task.

Use the canonical rules here:

- [repo-operating-model.md](repo-operating-model.md)
- [repo-template.instructions.example.md](repo-template.instructions.example.md)
- [repo-template.skill.example.md](repo-template.skill.example.md)
- [repo-templates/README.md](repo-templates/README.md)

When the work is recurring upstream maintenance, also use:

- [upstream-intake/README.md](upstream-intake/README.md)

Expected outcome:

1. Route the work into the correct repo artifact layer.
2. Preserve separation between truth, plans, research, decisions, and logs.
3. Use stable IDs and authoring metadata where required.
4. Escalate only when the decision truly needs operator judgment.
