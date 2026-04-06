---
name: "Weekly Upstream Intake"
description: "Example thin launcher prompt for reviewing an upstream release or compare window in a downstream fork."
argument-hint: "Release tag, compare window, or refs to review"
agent: "agent"
---

Run the upstream-intake workflow for the provided upstream window.

Use the canonical workflow and rules here:

- [upstream-intake.instructions.example.md](upstream-intake.instructions.example.md)
- [weekly-upstream-intake.skill.example.md](weekly-upstream-intake.skill.example.md)
- [weekly-upstream-intake-template.md](weekly-upstream-intake-template.md)
- [operator-weekly-brief-template.md](operator-weekly-brief-template.md)
- [intake-method.md](intake-method.md)

Expected outputs:

1. A full internal record under [reports/internal-records/README.md](reports/internal-records/README.md)
2. A separate operator brief under [reports/operator-briefs/README.md](reports/operator-briefs/README.md)

Do not keep the result at release-note summary level.
Use internet lookup when vendor policy, pricing, legal terms, or external product behavior affects the decision.
Escalate anything that changes product direction, compatibility contracts, or security posture.