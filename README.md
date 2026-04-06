# Upstream Intake Kit

This directory is a generic, reusable upstream-intake kit for downstream forks.

It is not tied to any one product, upstream project, or repository layout.
Use it as a starting point when you want to add a disciplined upstream-review workflow to another fork.

## What This System Is For

This system is meant to solve a recurring maintenance problem:

- upstream changes keep arriving
- some should land as-is
- some need adaptation into fork-specific surfaces
- some should be declined
- some require an operator or maintainer decision before they can land

The system treats upstream review as a decision workflow, not a changelog summary.

## Core Model

The workflow produces two separate artifacts by default:

- a full internal decision record
- a separate operator-facing brief

The internal record is where exhaustive reasoning lives.
The operator brief is where that reasoning gets translated into a shorter human-facing summary.

## What Lives Here

1. [weekly-upstream-intake-template.md](weekly-upstream-intake-template.md)
   - Full internal record template.
2. [operator-weekly-brief-template.md](operator-weekly-brief-template.md)
   - Shorter operator-facing brief template.
3. [intake-method.md](intake-method.md)
   - The analysis method, drill-down rules, and decision shapes.
4. [compatibility-watchlist.md](compatibility-watchlist.md)
   - Standing list of compatibility-sensitive surfaces.
5. [known-local-overrides.md](known-local-overrides.md)
   - Register of intentional fork-specific divergences.
6. [decision-carry-forward.md](decision-carry-forward.md)
   - Register of standing decisions to carry into later reviews.
7. [reports/README.md](reports/README.md)
   - Report storage guidance.
8. [upstream-intake.instructions.example.md](upstream-intake.instructions.example.md)
   - Example canonical instruction file for agent-capable repos.
9. [weekly-upstream-intake.skill.example.md](weekly-upstream-intake.skill.example.md)
   - Example procedural skill/workflow file.
10. [weekly-upstream-intake.prompt.example.md](weekly-upstream-intake.prompt.example.md)
   - Example thin launcher prompt.
11. [recreate-upstream-intake-system.prompt.md](recreate-upstream-intake-system.prompt.md)
   - A prompt you can hand to another agent to recreate this system in a different repo.

## How To Reuse It

1. Copy this directory into the target repo.
2. Decide where the canonical upstream-intake package should live in that repo.
3. Adjust links and file locations to match the target repo's conventions.
4. If the target repo supports agent prompts, skills, or instructions, adapt the example files rather than copying them blindly.
5. Seed the system with one real upstream review artifact so the workflow is grounded in real repo behavior.

## Canonical Split

When porting this system, keep the responsibilities separated:

- prompt: thin launcher
- skill or workflow: procedure
- instruction: canonical behavioral rules
- templates and method docs: canonical output shape and analysis method
- internal record: exhaustive reasoning
- operator brief: shorter human translation

That split reduces drift and keeps one source of truth for each kind of rule.

## Notes

The files ending in `.example.md` are intentionally generic examples.
They are not meant to be auto-loaded as active repo configuration without adaptation.