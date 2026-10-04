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
- Merge through `gh pr merge <number> --squash --match-head-commit <candidate>`
  only after checks and review pass. Never use an administrative bypass or
  weaken protection. Keep published branch history append-only.
- Post delivery evidence through `gh pr comment <number> --body-file <file>`.
  Verify closure through `gh issue view <number> --json state,closedAt`; if the
  closing reference did not close it after integration, use `gh issue close`.

The repository's existing main-push publication workflow owns Catalog Snapshot
publication, as described in [README.md](../../README.md#publish). Delivery must
not manually publish a second release or change workflow authority.
