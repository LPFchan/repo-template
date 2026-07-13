---
name: housekeeping
version: 1.0
description: Read-only adversarial repository-boundary audit. Inventories the complete physical workspace — tracked, ignored, generated, cached, backed-up — challenges every item's right to exist where it lives, and produces a ranked audit, an operator decision sheet, and a gated migration sequence. Never deletes or moves anything. Trigger on "housekeeping", "boundary audit", "repo audit", "audit the workspace", "what can we delete", or similar.
argument-hint: "Repository or subtree to audit; optional focus (tracked-only, ignored-only, backups, artifacts)"
---

# Housekeeping

Use this skill when the operator wants an adversarial audit of what physically lives in a repository and whether each item honestly earns its location, name, and retention cost.

Use it with:

- [../../AGENTS.md](../../AGENTS.md)

This skill is **read-only**. It inventories, measures, cross-checks, and reasons. It proposes. It never deletes, moves, renames, or rewrites anything until the operator approves the decision sheet. Every conclusion must be backed by evidence gathered during the pass, not assumption.

## Posture

Treat every tracked file, ignored file, directory, generated artifact, database, cache, backup, checkpoint, log, browser profile, nested repository, and temporary workspace as requiring justification for its existence, location, name, and retention.

These are **not** sufficient justifications, and you must reject them explicitly wherever they appear:

- "it has always lived there"
- "it is ignored by Git"
- "it might be useful someday"
- "it is historical"

Challenge the status quo aggressively. Distinguish the **intended** architecture from what has **physically** landed.

## What This Skill Produces

1. **A ranked, evidence-backed audit** — every finding cites measured size, count, path, and the trace that supports it.
2. **An explicit operator decision sheet** — the choices only the operator can make.
3. **A migration sequence with destructive gates** — ordered steps, each with a stop-and-confirm before anything irreversible.
4. **A contradictions-and-gaps list** — where docs, code, tests, and physical reality disagree.
5. **Estimated reductions** — disk space reclaimed and tracked lines removed.

## Core Rules

- Read-only until the decision sheet is approved. No `rm`, `mv`, `git rm`, `git mv`, truncation, or rewrite of any audited artifact during the pass.
- Verify before recommending deletion. "Suspected orphan" is a hypothesis, not a verdict — trace it to ground.
- Inventory the **complete physical workspace**, not just tracked files. Ignored and untracked residue is in scope.
- Measure. Every retention claim carries a number: size, count, age, or reference count.
- Separate every conclusion into one of the five verdict categories below. Do not invent categories for neatness.

## Procedure

### Step 0: Establish Scope and Baseline

Confirm the audit root (repository or subtree) and any focus the operator named. Then capture a baseline:

- total workspace size vs. tracked size vs. ignored/untracked size
- top-level directory inventory with per-directory size and file count
- the `.gitignore` / ignore rules in effect, and what they are actually hiding

### Step 1: Physical Inventory

Enumerate the full tree — tracked **and** ignored **and** untracked. For each top-level directory and each notable item, record:

- **size** and **file count**
- **lifecycle class** — is it source, mutable state, expensive cache, build stage, release artifact, model artifact, evidence, backup, or disposable residue?
- **name/location honesty** — does its current name and path express that lifecycle truthfully?
- **age / staleness** — last modified; is it a stale generation superseded by a newer one?
- **duplication** — is it a duplicate, superseded, or contradictory copy of something else?

Flag nested repositories, browser profiles, checkpoints, optimizer state, upload chunks, archives, logs, and reports specifically — these accumulate silently.

### Step 2: Interrogate Each Item

For every item of consequence, ask and answer:

- Why does this directory exist at all?
- Is "ignored by Git" hiding an incoherent local data architecture?
- Did historical migrations leave duplicate, stale, superseded, or contradictory artifacts?
- If generated: is it reproducible, and from exactly which **retained** inputs? (An artifact whose inputs are gone is not reproducible — say so.)
- If a backup: is it independent, verified, encrypted, and restore-tested? Untested backups are not backups.
- If a checkpoint / log / archive / report: does its current value still justify its storage cost?
- Do active code, tests, guides, truth docs, and embedded paths agree with physical reality?

### Step 3: Trace Suspected Orphans

Do not declare code or files orphaned by absence of obvious use. Trace each suspected orphan through:

- imports and references
- entrypoints and shell scripts
- documentation and truth docs
- git history
- live/runtime usage

Only after the trace comes back empty may it move from "suspected orphan" to a verified verdict. Record the trace as evidence.

### Step 4: Assign Verdicts

Place every conclusion into exactly one category:

1. **Verified safe deletion** — traced, measured, nothing depends on it, reproducible or valueless.
2. **Verified move or rename** — keep it, but its location or name lies about its lifecycle.
3. **Retain, with concrete reason** — stays put; state the specific reason (not "might be useful").
4. **Operator policy decision required** — the call depends on operator intent, retention policy, or risk tolerance you cannot resolve.
5. **Unresolved, requiring targeted verification** — needs a specific further check before any verdict; name the check.

### Step 5: Propose the Smallest Coherent Boundary

Propose the **smallest coherent lifecycle boundary** for the repository — what should be tracked, what should be ignored-but-organized, what should live outside the repo entirely. Do not add structure merely for tidiness. Anchor the proposal to intended architecture, and name where physical reality currently diverges from it.

### Step 6: Synthesize the Deliverables

Produce all five outputs listed above. The migration sequence must order steps so that reversible cleanups precede irreversible ones, and every irreversible step is preceded by an explicit destructive gate (a stop-and-confirm). Include estimated disk and tracked-line reductions.

## Using Subagents

For a workspace of any size, dispatch **read-only** subagents to run independent audits in parallel — e.g. one per top-level directory, or one per concern (tracked source, ignored residue, backups, generated artifacts). Give each the read-only posture and the Step 1–3 questions. Then **synthesize and cross-check** their findings yourself: reconcile disagreements, dedupe overlapping claims, and re-verify anything a single subagent asserted without a trace. A finding survives only if it holds after cross-check.

## Escalation Triggers

Escalate to the operator when:

- a verdict hinges on retention policy, compliance, or risk tolerance you cannot determine → category 4.
- backups cannot be confirmed independent, verified, encrypted, or restore-tested → do not classify them as safe; surface the gap.
- physical reality contradicts a truth doc, test, or embedded path → list it in the contradictions output rather than silently resolving it.

## Quality Bar

- read-only throughout; nothing destructive runs before the decision sheet is approved
- every finding carries measured evidence (size, count, path, trace)
- every suspected orphan is traced before any deletion verdict
- every conclusion sits in exactly one of the five verdict categories
- the migration sequence gates every irreversible step
- rejected non-justifications ("always been there", "it's ignored", "might be useful", "historical") are called out, not accepted
- implementation waits for explicit operator approval of the decision sheet
