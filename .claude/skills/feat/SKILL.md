---
name: feat
description: >
  Full feature-development pipeline for the who-is repo — plan, design, review, implement, then
  hand off to the git skill for branch/commit/PR. Use when the user says "/feat", "build a
  feature", "let's build X", or wants a new capability built end-to-end. Supports an auto mode
  that runs the whole pipeline through merge without stopping for confirmation.
---

# /feat

End-to-end feature workflow. Invoke the `git` skill for every git/GitHub operation — never run
raw `git`/`gh` commands directly from this skill.

## Modes

- **Guided (default)** — stop at every gate below for user confirmation.
- **Auto** — user says "run everything automatically" / "auto" / "just ship it end-to-end", at
  invocation or mid-flow. Skips the design-brief gate and the post-test wait (see below). Every
  other rule (commit convention, squash-merge, no force-push) still applies.

## Pipeline

1. **Plan** — read `docs/` (per this repo's CLAUDE.md) and scope what's being built. Ask the user
   only what's genuinely ambiguous — don't ask about things a sensible default already covers.
2. **Design** — propose the approach: files touched, data/API shape if relevant, key tradeoffs.
   Give the user a short brief (what's being built, key design choice, files touched — no essay)
   and wait for confirmation before writing code. Auto mode: skip the wait, proceed.
3. **Self-review the design** — run it through the ponytail ladder and karpathy-guidelines
   (already mandated repo-wide) before touching code: trim speculative scope, prefer the smallest
   correct approach.
4. **Implement** — invoke `git` skill to create the `<type>/<feature-name>` branch, then write the
   code, committing as work lands per the git skill's convention.
5. **Review the diff** — before opening the PR, review the changes for correctness and
   over-engineering (use `/code-review` or `/ponytail-review` as appropriate) and fix findings.
6. **PR** — invoke `git` skill to push and open the PR, title matching the commit convention.
7. **Handoff** — tell the user the PR is open and ask them to manually test.
   - Guided mode: stop here. Wait for the user's explicit "commit" / "merge" instruction on this
     PR before touching it again.
   - Auto mode: skip the manual-test wait — invoke `git` skill's merge step directly.

## Notes

- This skill never merges without either explicit user go-ahead per-PR, or standing auto-mode
  authorization from this session.
- Every commit and PR follows the `git` skill's conventions — don't duplicate that logic here.
