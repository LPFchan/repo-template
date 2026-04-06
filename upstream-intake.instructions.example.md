---
description: "Example instruction file for reviewing upstream releases, compare windows, sync candidates, merge decisions, or weekly intake reports in a downstream fork."
---

# Upstream Intake Instructions

Use this instruction when the task is to review, summarize, triage, or merge upstream work into a downstream fork.

## Core Goal

Do not treat upstream review as a changelog paraphrase.
Translate upstream work into concrete downstream decisions.

The agent is allowed and encouraged to use internet sources to resolve ambiguity.
When the question depends on vendor policy, billing, pricing, legal terms, official product positioning, or external release behavior, look up the relevant official sources instead of guessing.
Prefer official vendor docs, terms, pricing pages, release notes, or upstream PR context.

When the template or report asks what a change "actually means" or means "in practice," do not answer with a restatement of the upstream note.
Drill down until the behavioral consequence is explicit.

Use this pattern:

- What concrete behavior changes if this lands?
- Who notices first: operator, plugin author, end user, maintainer, or nobody?
- Where does the change show up first: onboarding, config, runtime behavior, error handling, UI, docs, tests, or upgrade flow?
- What problem disappears, and what new cost or constraint appears?
- What would a user or operator literally experience differently next review cycle?
- If nothing user-visible changes, what maintenance or architectural pressure changes instead?

Then force the explanation through these ambiguity checks:

- Name the concrete referent for any phrase like `vendor-specific`, `some cases`, `this path`, `that surface`, or `this behavior`.
- State the exact upstream feature, provider, vendor, contract, or runtime path being discussed.
- State the exact local downstream surface affected.
- State what is changing and what is not changing.
- State whether the change is about policy, implementation, or both.
- State at least one literal user or operator scenario.
- State the evidence source category behind the claim: upstream release notes, upstream PR or commit, official vendor docs or terms, local code, or local policy docs.

If a sentence still works without naming the concrete product, vendor, feature, or path, it is too vague and must be rewritten.

## Required Workflow

1. Define the exact upstream window being reviewed.
2. Gather evidence from release notes and, when needed, the underlying commits, PRs, docs, and code paths.
3. Group related changes into candidate decisions instead of treating every commit as equally important.
4. For each candidate change, fill or mirror the fields in [weekly-upstream-intake-template.md](weekly-upstream-intake-template.md).
   - Do not leave referents implicit.
   - If needed, use internet lookup to resolve vendor, product, pricing, legal, or policy ambiguity before filling the record.
5. Classify the result as `accept`, `adapt`, `decline`, or `defer pending operator decision`.
6. Apply the local autonomy boundary before taking action.
7. Produce an operator-facing brief that separates:
   - decisions made autonomously
   - decisions requiring operator input

By default, store the full internal record and the lighter operator brief as separate artifacts.

## Operator Brief Requirements

The internal record should contain the exhaustive field coverage and detailed reasoning.
The operator brief should be a translation layer for humans.
Do not mirror every internal-record field as a labeled bullet list unless the user explicitly wants that style.
Prefer a short, conversational mini-brief for each operator-facing item, optionally followed by compact bullets for options, recommendation, or blocked work.

## Decision Rules

- If the fix belongs to shared core, prefer the upstream-shaped implementation.
- If the local fix is tied into fork-only surfaces, keep the local version and adapt upstream ideas into it.
- If the upstream patch changes policy, decide the policy first by escalating to the operator, then choose the implementation that matches that decision.
- Do not silently override a security-relevant upstream change. If the right move is to localize, defer, or decline it, escalate.
- Treat plugin-facing contracts, migration-sensitive surfaces, onboarding, user workflow changes, and public product direction as escalation-sensitive.

## Output Standard

A complete upstream review should leave behind:

- a decision record that matches [weekly-upstream-intake-template.md](weekly-upstream-intake-template.md)
- a separate operator-facing summary using [operator-weekly-brief-template.md](operator-weekly-brief-template.md)
- explicit notes on verification, compatibility details, and follow-up work

The operator-facing brief must be understandable without prior chat context.
Do not rely on shorthand like `vendor-specific path` unless the vendor and path are named in the same item.