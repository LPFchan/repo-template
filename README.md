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

The installed sync script requires template version 2.0.6 or newer and rejects
older or malformed versions before changing project files. This floor covers
both mixed skill ownership and the separate workflow maintenance boundary.
The recorded template version updates even when only the upstream manifest or
version changes. Only the canonical header marker is updated; later policy
examples, local content, line endings, and permissions are preserved.

The explicitly managed `sync-preflight.py` helper is loaded from the freshly
cloned scaffold. Before the current reader writes project files, it checks both
lexical and resolved destination containment, refuses uncommitted changes at
managed destinations and their descendants, and renders AGENTS/policy updates.
Staged, unstaged, untracked, and ignored data at those destinations must be
committed or moved aside by the caller. Unrelated project records, custom skills,
caches, and a legacy workflow's `sync.log` remain allowed and preserved. The
caller owns the resulting commit and must commit managed changes before another
direct sync. Rendering failures are fatal and do not advance the recorded version.
Legacy readers retain their own pre-loop behavior during their initial upgrade;
the full preflight applies when the newly installed script is invoked.

`scaffold/template-sync.yml` is an adoption artifact. Install or upgrade it through
a separately reviewed change to `.github/workflows/template-sync.yml`; it is
outside the automatic sync manifest. Sync reports workflow drift without changing
workflow files, keeping content updates within the standard `GITHUB_TOKEN`
permissions. The installed script rejects managed or seed manifests that target
workflow paths or their ancestors before changing project files. Older installed
workflows need a separate reviewed upgrade to gain
the generated commit provenance, temporary log handling, and bounded staging.
The current workflow requires a clean checkout, preserves the scheduled or
manually selected branch, and stages only its captured sync changes. Its logs,
path list, and generated commit message stay under `RUNNER_TEMP`.
Workflow commit provenance uses the unique canonical `Project id` in
`records/SPEC.md`, accepting its plain or backtick-wrapped form. Missing, invalid,
or ambiguous IDs stop the commit rather than falling back to a repository name.

Run the regression suite with `python3 -m unittest discover -s tests -v`.
It uses temporary local Git repositories and needs Bash, Git, and Python 3.
Workflow tests execute the shipped shell blocks with local bare remotes, the real
commit generator, validator, and hooks, including no-op and failure paths.
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
