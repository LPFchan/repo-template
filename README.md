# repo-template

A repo operating system for projects managed by one operator plus many agents. Gives every project a canonical home for truth, memory, direction, and execution provenance.

## Getting Started

Give your agent this prompt, pointing at the target repo:

> Fetch the latest repo-template from `LPFchan/repo-template`. Copy `scaffold/` contents into the target repo root. Follow the canonical rules in `records/REPO.md`. Enable `upstream-intake/` only if the target repo tracks an upstream. Wire local hooks. Seed at least one real artifact to verify routing boundaries.

## Scaffold Map

| Path | Answers |
| --- | --- |
| `records/REPO.md` | How this repo operates |
| `records/SPEC.md` | What this repo is |
| `records/STATUS.md` | Where this repo currently sits |
| `records/PLANS.md` | What's planned for this repo |
| `records/INBOX.md` | Capture waiting for triage |
| `records/research/` | What we learned from exploration |
| `records/decisions/` | What we decided and why |
| `records/upstream-intake/` | Upstream changes we reviewed |
| `skills/` | Repeatable procedural workflows |
| `AGENTS.md` | Agent instructions entrypoint |
| `CLAUDE.md` | Thin shim pointing to `AGENTS.md` |

Agent instruction files stay thin. Canonical policy lives in `records/REPO.md`.

## Commit Format

Every normal commit must carry:

```text
<subject line>

timestamp: YYYY-MM-DD HH-mm-ss KST
changes:
- ...
rationale:
- ...
checks:
- ...

project: <project-id>
agent: <agent-id>
role: orchestrator|worker|subagent|operator
commit: LOG-YYYYMMDD-HHMMSS-<agent-suffix>
artifacts: DEC-..., RSH-...   (optional; no LOG-*)
```

Generate a compliant skeleton:

```bash
sh scripts/new-commit-message.sh --subject "feat: your change" --agent <agent-id>
```

Commit with `git commit -F <generated-file>`. Hand-written `git commit -m` is rejected by the hooks.

## Enforcement

- `.githooks/prepare-commit-msg` — rejects non-generated normal commits
- `.githooks/commit-msg` — validates execution contract
- Bootrap/migration commits are the only exception path

Run `sh scripts/install-hooks.sh` to enable tracked hooks locally.

## Upgrading an Adopted Repo

To upgrade an already-adopted repo to the current template contract:

> This repo already uses repo-template. Fetch the latest from `LPFchan/repo-template`. Merge upstream policy into `records/REPO.md`, `AGENTS.md`, and `CLAUDE.md` verbatim. Merge hooks and scripts. Do not paraphrase upstream policy. Preserve local extensions under an explicit `Local Divergence` section. Do not weaken existing enforcement.

## Template Sync Checks

`scaffold/manifest.txt` lists template-owned paths. Upstream-intake guidance is
managed file by file; project reports and additional files stay project-owned.
Skill guidance is also managed file by file. Custom skills, helper assets, and
generated caches remain project-owned, including additional files inside a
template skill directory. New template skill assets must be listed explicitly
in the manifest; the regression suite checks coverage of every shipped file.
`scaffold/seed-manifest-v2.txt` supplies missing registers without replacing existing
content. Keeping seeds separate also protects projects running an older sync
script during their first upgrade. A v2.0.1 reader installs the new script first;
missing registers and managed AGENTS.md updates are applied by its next run
through the atomic publication paths. Existing project data stays unchanged
during that first legacy upgrade.

Run the regression suite with `python3 -m unittest discover -s tests -v`.
It uses temporary local Git repositories and needs Bash, Git, and Python 3.
Set `ADOPTED_REPO_UNDER_TEST` to an adopted checkout to additionally verify its
installed sync script preserves its exact upstream-intake files.
The cross-filesystem test uses the checkout's parent for its adopted repo. If
that shares `/tmp`'s filesystem, set `CROSS_FILESYSTEM_TEST_ROOT` to a writable
directory on another filesystem; CI uses `/dev/shm`. The test reports a skip
when distinct filesystems are unavailable.

Atomic missing-register initialization requires hard-link support on the adopted
filesystem. Unsupported filesystems fail with an explicit capability error; the
missing register stays absent, temporary staging is cleaned, and existing
project records remain intact. Initialize a missing register manually or use a
filesystem with hard-link support. A direct-copy fallback would reintroduce
partial-register and concurrent-overwrite risks. This is tested with injected
unsupported-operation errors; no exFAT or SMB mount was used for validation.
