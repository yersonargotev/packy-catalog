# Issue tracker

Use GitHub Issues and pull requests in `yersonargotev/packy-catalog` through
GitHub CLI (`gh`). The integration branch is `main`. Resolve readiness through
[triage-labels.md](triage-labels.md).

## Operations

- Fetch an issue and its complete conversation with `gh issue view <number>
  --repo yersonargotev/packy-catalog --json number,title,body,state,labels,comments`.
  Follow declared dependencies and normative links before implementation.
- Search existing delivery work with `gh pr list --state all`, `git branch -a`,
  `git worktree list`, and the commit history. Reuse only unambiguous work.
- Create a pull request targeting `main` with `gh pr create --base main
  --body-file <file>`. Include `Closes #<number>` in its body.
- Inspect the candidate and conversation with `gh pr view <number>` and
  `gh api repos/yersonargotev/packy-catalog/pulls/<number>/reviews`.
- Inspect required checks with `gh pr checks <number> --required`, and inspect
  failures with `gh run view <run-id> --log-failed`. `Validate Catalog Project`
  is the required validation check. Re-read branch protection before merging.
- Before integration, run the read-only closing-reference guard:
  `python3 -B scripts/delivery.py preflight --pr <number> --head <candidate>
  --expect yersonargotev/packy-catalog#<issue>`. For a prerequisite, use
  `--expect-none` instead. An explicit expected set is required.
- Integrate through `python3 -B scripts/delivery.py merge --pr <number>
  --head <candidate> --expect yersonargotev/packy-catalog#<issue>` only after
  checks, independent review, and exact-candidate verification pass. This
  operation automatically repeats the guard before the protected GitHub CLI
  squash merge with exact-head matching. Never use an administrative bypass
  or weaken protection. Keep published branch history append-only.
- For prerequisite delivery, capture the approved issue with `delivery.py
  qualify --issue <issue>` before integration and pass its successful JSON as
  `--qualification <file>` to `delivery.py merge --expect-none`. The operation
  checks qualification before merging and re-reads state, configured readiness,
  scope, and conversation after confirmed integration. Resume implementation
  only after unchanged qualification passes. A change or incomplete tracker
  evidence produces an exception; resolve it through qualification, without
  automatic tracker repair. Read the [delivery walkthrough](../delivery.md)
  for commands, evidence, and pending-queue recovery.
- Post delivery evidence through `gh pr comment <number> --body-file <file>`.
  Verify closure through `gh issue view <number> --json state,closedAt`; if the
  closing reference did not close it after integration, use `gh issue close`.

The repository's existing main-push publication workflow owns Catalog Snapshot
publication, as described in [README.md](../../README.md#publish). Delivery must
not manually publish a second release or change workflow authority.
