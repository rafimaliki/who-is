---
name: git
description: >
  Git workflow automation for the who-is repo — branching, committing, PR creation, and PR
  merging via the gh CLI, following this project's conventional-commit rules. Use whenever the
  user asks to commit, branch, open a PR, or merge a PR in this repo, or when another skill (e.g.
  /feat) needs a git/GitHub operation performed. Triggers: "commit this", "open a PR", "merge the
  PR", "create a branch", "/git".
---

# git

Handles every git/GitHub operation in this repo: branches, commits, PR creation, PR merging.
Global attribution settings already strip the Claude co-author trailer from commits and PRs —
don't add one manually either.

## Commit convention

Type prefixes: `feat:`, `fix:`, `chore:`, `refactor:` (add `test:` / `docs:` only if asked).

Every commit — including WIP ones — uses `<type>: <description>`, lowercase imperative, no
trailing period, subject under ~72 chars. Scope with the feature name when it adds clarity:
`feat(auth): add token refresh`.

## Branch naming

`<type>/<feature-name>` — e.g. `feat/user-auth`, `fix/login-bug`. `feature-name` is kebab-case,
derived from what's being built.

## Workflow

### Start a feature/fix
1. `git status` — confirm the tree is clean; stash or ask if not.
2. Branch off the default branch: `git checkout -b <type>/<feature-name>`.
3. Work happens; every commit follows the convention above.

### Commit
- Stage only the relevant files — never blind `git add -A` unless the user has confirmed
  everything currently untracked/modified is meant to go in.
- Message: `<type>: <description>` (or `<type>(<feature-name>): <description>`).
- No co-author trailer, ever.

### Open a PR
1. `git push -u origin <branch>`.
2. `gh pr create --title "<type>: <description>" --body "..."` — title matches the eventual
   squash-commit message.
3. Body: short summary + test plan. No attribution footer.

### Merge a PR
1. Confirm with the user before merging — irreversible on shared history — unless the calling
   workflow (e.g. `/feat` in auto mode) has explicit standing authorization to merge.
2. Squash-merge only: `gh pr merge <number> --squash --delete-branch`.
3. Edit the squash-commit message to exactly match the PR title — `<type>: <description>` — no
   leftover WIP commit noise.
4. Verify: `gh pr view <number>` shows MERGED.

## Rules

- Never `push --force` to a shared branch without explicit confirmation.
- Never merge without either explicit user go-ahead or an active auto-mode instruction from the
  calling workflow.
- Squash merge only — no merge commits, no rebase-merge — so `main` stays one commit per feature.
- If `gh` isn't authenticated, stop and tell the user to run `gh auth login` — don't work around it.
