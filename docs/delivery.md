# Catalog delivery guard

Run `python3 -B scripts/delivery.py` from a reviewed Catalog checkout with
Python 3.9+ and authenticated GitHub CLI (`gh`) on PATH. This Catalog-owned
tool targets `yersonargotev/packy-catalog` and its `main` integration branch.
It does not execute Pack resources or change the release/publication workflow.

## Read-only preflight

Supply the PR number, full proven candidate SHA, and the exact set of issues
it is intended to close. `--expect-none` explicitly means an empty set;
repeat `--expect owner/repository#number` for a set. Expected issues must
belong to this Catalog. Missing expectations are a usage error.

```sh
python3 -B scripts/delivery.py preflight --pr "$pr" --head "$candidate" \
  --expect yersonargotev/packy-catalog#71
```

The guard reads GitHub's GraphQL
[`closingIssuesReferences`](https://docs.github.com/en/graphql/reference/pulls),
including repository identity, in the same response as the observed head.
It compares sets instead of interpreting closing prose: even a negated closing
phrase can produce a recognized reference. Missing, extra, and wrong-repository
references fail, as do a changed head, a closed PR, or a target other than main.
API failures, partial GraphQL results, malformed fields, and incomplete
connections fail closed. Connections are bounded to 100 entries and must have
matching counts and no next page; larger connections require an explicit
tooling extension rather than accepting truncated evidence.

Successful and failed operations emit one JSON report (`schema_version: 1`).
Preflight evidence includes `repository`, `pull_request`, `candidate_head`,
`observed_head`, `expected_closing_issues`, `recognized_closing_issues`, and
`outcome`. Unknown observed data is `null`, never a successful empty set.
Failures add `error` and exit nonzero. Argument usage errors go to stderr with
exit 2. Each GitHub CLI call has a 60-second deadline. No guard failure repairs
PR prose, closes/reopens issues, or changes labels.

## Prerequisite walkthrough

After qualifying the approved delivery issue, preserve its live snapshot in
delivery-owned scratch space. Set `prerequisite_pr` and `prerequisite_head`
to the reviewed prerequisite's number and exact proven SHA.

```sh
proof_dir="$(mktemp -d)"
python3 -B scripts/delivery.py qualify --issue 71 > "$proof_dir/qualified.json"
# Continue only if qualification exited zero.
python3 -B scripts/delivery.py preflight \
  --pr "$prerequisite_pr" --head "$prerequisite_head" --expect-none
# Complete independent review, manual verification, CI, and protection checks.
python3 -B scripts/delivery.py merge \
  --pr "$prerequisite_pr" --head "$prerequisite_head" --expect-none \
  --qualification "$proof_dir/qualified.json"
```

`merge` invokes the guard automatically and requires the successful qualification
file for an empty expected set. It checks the delivery issue against that
baseline before attempting the merge, confirms integration through GitHub,
then reads the issue again before allowing implementation to resume.
The snapshot includes the issue number, state, title/body, labels, full comment
bodies and authors, and the configured readiness mapping. The mapping comes
from the `ready-for-agent` row in `docs/agents/triage-labels.md`; a missing or
ambiguous mapping fails. Closed, unapproved, or `wontfix` issues fail.

Any snapshot difference, including changed comments or the readiness contract,
conservatively requires requalification. A snapshot checks freshness, not the
semantic adequacy of acceptance criteria or approval to change them. The
delivery owner still evaluates scope, dependencies, and new discussion.
Do not replace the baseline just to make a failing comparison pass. Retain it
until the exception is resolved and implementation may resume; remove only
the delivery-owned scratch directory during cleanup.

## Final delivery walkthrough

After implementing the approved issue, use its singleton expected set. Set
`pr` and `candidate` to the final PR number and proven SHA.

```sh
python3 -B scripts/delivery.py preflight --pr "$pr" --head "$candidate" \
  --expect yersonargotev/packy-catalog#71
# Complete independent review, manual verification, CI, and protection checks.
python3 -B scripts/delivery.py merge --pr "$pr" --head "$candidate" \
  --expect yersonargotev/packy-catalog#71
```

The supported merge operation uses
[`gh pr merge --squash --match-head-commit`](https://cli.github.com/manual/gh_pr_merge),
with no bypass flag. GitHub retains branch protection and required-queue
authority. This guard complements review and CI; it does not grant permission
to merge an unverified candidate. Keep PR metadata stable during integration:
GitHub's head-match control binds the commit, not an atomic lease on PR prose
or issue state. A concurrent metadata edit still requires investigation.

The report records `merge_status: merged` and `integration_commit` only after
GitHub confirms the same candidate was merged. A queued/open PR returns an
integration-pending exception (`merge_status: requested`). If the merge call
fails or times out, `merge_status: unknown` requires tracker inspection before
retrying. A post-merge qualification failure retains the confirmed integration
identity and stops continuation; it does not undo the merge or repair issues.

For a pending queue, inspect GitHub until the proven head is integrated, then
run `qualify --issue 71 --baseline "$proof_dir/qualified.json"` before resuming
prerequisite-dependent work. Re-run affected delivery gates if the candidate
changes. Final delivery still requires checking the integration commit against
the remote branch, verifying issue closure, and cleaning owned worktrees and
branches through the existing delivery workflow. Publication remains owned by
the existing main-push workflow.

## Verification

`./scripts/test.sh` includes controlled GitHub CLI fixtures exercising the
public commands: empty and singleton sets, negation, mismatches, stale heads,
unavailable/incomplete data, protected merge arguments, pending integration,
and qualification before/after prerequisites. These tests never contact or
write the live tracker and remain part of ordinary inert CI.
