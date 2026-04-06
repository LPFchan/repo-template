You are implementing a reusable upstream-intake workflow for a downstream fork.

Goal:
Create a repo-native system for reviewing upstream changes on a recurring basis. The system must help maintainers decide whether to accept, adapt, decline, or defer upstream work, while preserving local fork policy, compatibility, and product direction.

What to build:

1. A canonical upstream-intake package in the repo.
2. A full internal decision template for weekly or periodic upstream review.
3. A shorter operator-facing brief template.
4. A method document explaining how to analyze upstream changes.
5. A compatibility watchlist for sensitive surfaces.
6. A known-local-overrides register for intentional fork divergences.
7. A decision-carry-forward register so standing decisions do not get re-litigated every cycle.
8. A report-artifact storage structure with separate folders for internal records and operator briefs.
9. If the repo supports agent instructions, reusable skills, or prompt files, add those too.

Behavioral requirements:

- Do not design this as a changelog-summary system.
- Design it as a fork-maintenance decision system.
- The review unit should be a candidate decision, not a raw commit by default.
- The system must force concrete drill-down on what an upstream change actually means locally.
- The system must separate what can be decided autonomously from what must be escalated.
- The system must preserve local fork knowledge across reviews.

Required analysis coverage for meaningful upstream items:

- exact upstream thing changing
- exact local surface affected
- before state
- after state
- concrete consequence
- what is not changing
- compatibility implications
- overlap with local work
- whether the issue is policy, implementation, or both
- whether the item should be accepted, adapted, declined, or deferred pending operator decision

Operator brief requirements:

- The operator brief must not mirror the internal record field-by-field.
- It should translate the internal reasoning into a shorter human-facing summary.
- It should surface unresolved operator-facing decisions near the top.
- It should allow flexible prose and not read like a rigid checklist.
- When there are real alternatives, present options clearly.
- If there are more than two real options, allow more than two options.

Autonomy and escalation requirements:

- Shared-core fixes should generally prefer the upstream-shaped implementation unless local behavior is already stronger or policy says otherwise.
- Fork-owned product or compatibility surfaces should preserve the local shape and adapt upstream ideas into it.
- If the conflict is about policy rather than implementation, escalate the policy decision first.
- Do not silently local-override security-relevant upstream changes when the real disagreement is about policy.

Anti-vagueness requirements:

- Do not allow vague phrases like `vendor-specific`, `some cases`, `this path`, or `that surface` without naming the referent.
- Require the exact vendor, provider, feature, contract, or path for important items.
- Require at least one literal user, operator, or maintainer scenario for each major item.
- Require a statement of what is not changing.

Internet lookup requirement:

- If conclusions depend on vendor policy, pricing, legal terms, official product positioning, or other external behavior, instruct the agent to use internet lookup and prefer official sources.

Structure requirements:

- Make one directory the canonical source of truth for the upstream-intake system.
- If there are legacy or compatibility entry points elsewhere in the repo, keep them thin and redirect to the canonical package.
- If the repo has prompt files, keep the prompt thin.
- If the repo has skill or workflow files, keep them procedural.
- Put detailed rules in one canonical instruction or method layer rather than duplicating them everywhere.

Implementation steps:

1. Inspect the repo and identify where architecture or process docs live.
2. Identify whether the repo supports agent instructions, reusable skills, or prompt files.
3. Design the upstream-intake package so it fits existing repo conventions.
4. Create the canonical docs, templates, and registers.
5. Wire any prompt, skill, or instruction entrypoints to reference the canonical sources instead of duplicating them.
6. Seed the system with one real upstream review artifact based on an actual upstream release, compare window, or sync candidate.
7. Seed the carry-forward and local-override registers using real conclusions from that sample review.
8. Validate that the operator brief and internal record are clearly separated in purpose and tone.
9. Remove unnecessary duplication across prompt, skill, instruction, and template layers.
10. Summarize what was created, what is canonical, and how future agents should invoke the workflow.

Deliverables:

- canonical upstream-intake package
- internal decision template
- operator brief template
- intake method
- compatibility watchlist
- known local overrides
- decision carry-forward register
- report storage guidance
- sample internal record
- sample operator brief
- thin prompt or launcher if the repo supports it
- procedural skill or workflow if the repo supports it
- canonical instruction or rules if the repo supports it

Quality bar:

- concrete, not vague
- reusable, not one-off
- split internal reasoning from operator communication
- preserve local fork knowledge
- minimize duplicated rules across files
- fit the target repo's conventions rather than imposing arbitrary structure