# Upstream Intake

This directory is the reusable upstream-review and fork-maintenance package inside Repo Template.

Use this package when a repo needs a disciplined way to review upstream releases, compare windows, sync candidates, or merge decisions without collapsing into changelog-summary mode.

## What This Subpackage Is For

This system is meant to solve a recurring maintenance problem:

- upstream changes keep arriving
- some should land as-is
- some need adaptation into local surfaces
- some should be declined
- some require operator or maintainer judgment before they can land

The system treats upstream review as a decision workflow, not a changelog summary.

## What Lives Here

1. [weekly-upstream-intake-template.md](weekly-upstream-intake-template.md)
   - Full internal decision record template.
2. [operator-weekly-brief-template.md](operator-weekly-brief-template.md)
   - Shorter operator-facing brief template.
3. [intake-method.md](intake-method.md)
   - The analysis method, drill-down rules, and decision shapes.
4. [compatibility-watchlist.md](compatibility-watchlist.md)
   - Standing list of compatibility-sensitive surfaces.
5. [known-local-overrides.md](known-local-overrides.md)
   - Register of intentional local divergences.
6. [decision-carry-forward.md](decision-carry-forward.md)
   - Register of standing decisions to carry into later reviews.
7. [reports/README.md](reports/README.md)
   - Report storage guidance.
8. [examples/upstream-intake.instructions.example.md](examples/upstream-intake.instructions.example.md)
   - Example canonical instruction file.
9. [examples/weekly-upstream-intake.skill.example.md](examples/weekly-upstream-intake.skill.example.md)
   - Example procedural skill file.
10. [examples/weekly-upstream-intake.prompt.example.md](examples/weekly-upstream-intake.prompt.example.md)
   - Example thin launcher prompt.
11. [recreate-upstream-intake-system.prompt.md](recreate-upstream-intake-system.prompt.md)
   - A prompt for recreating just this upstream-intake package in another repo.

## Working Model

The workflow produces two separate artifacts by default:

- a full internal decision record
- a separate operator-facing brief

Both artifacts from the same intake cycle should share the same `UPS-*` review id.

The internal record is where exhaustive reasoning lives.
The operator brief is where that reasoning gets translated into a shorter human-facing summary.

## Canonical Split

When porting this package, keep the responsibilities separated:

- prompt: thin launcher
- skill or workflow: procedure
- instruction: canonical behavioral rules
- templates and method docs: canonical output shape and analysis method
- internal record: exhaustive reasoning
- operator brief: shorter human translation

That split reduces drift and keeps one source of truth for each kind of rule.
