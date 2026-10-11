# Implement and verify

Read the vendored workflow at [`implement.md`](implement.md) and apply it
against the ready issue with the commit/review ordering adapted below. The
vendored source remains unchanged; this delivery-specific ordering takes
precedence over its closing review-before-commit sequence.

Use structured editing capabilities when available. In a command-only
environment, keep edits small and independently parseable. Discover tools by
name and purpose, then load only the selected contracts needed for the active
gate. Run independent checks with separately observable results and preserve
each failure status.

1. Implement the issue with its TDD and incremental-check guidance.
2. Commit the complete candidate locally and require a clean worktree. Record
   its exact SHA before running the complete automated suite and `/code-review`.
   Use the qualified starting commit as the review's fixed point and the
   complete fetched issue as its Spec source. The review compares that base
   with the committed candidate, so uncommitted work cannot disappear from it.
3. Run the complete automated suite and both independent review axes on that
   unchanged SHA, then perform the manual scenarios below. A local candidate
   commit is not permission to push or open a change request; the next gate
   owns publication.

For every repair, repeat this sequence with a new candidate commit before
review. Published history remains append-only. Any candidate change invalidates
the affected evidence and returns to this sequence.

Before dispatching each independent review context, share available verification
receipts with the exact candidate SHA, command or scenario, outcome, and artifact
location. Each reviewer still inspects the fixed-base diff independently for
its own axis; receipts do not replace that judgment or inherit another verdict.
Reuse a passing check only for the unchanged SHA and applicable scenario.
Rerun missing, stale, failed, or finding-affected checks. Reviewers may request
targeted independent execution when the evidence warrants it. Keep the complete
automated suite and required CI gates intact.

A seam is pre-agreed when the issue or its agent brief identifies an observable
public interface. Before writing tests against any other seam, propose it and
pause for confirmation. When TDD is impractical, record the concrete reason and
prove behavior at the nearest public boundary.

Adjudicate every Standards and Spec finding. For accepted findings, run one
repair cycle; this gate's `/code-review` reruns both axes
in independent contexts. Review passes only when both axes pass on the exact
unchanged candidate.

After review, derive manual verification from the actual changed surface:

- For a CLI, run the real command with isolated state and check output, exit
  status, and effects.
- For a web interface, use Browser, Chrome, or another available interactive
  tool to exercise and inspect the visible behavior.
- For an API, call its public endpoint in an authorized local or test
  environment.
- For a library, exercise a minimal consumer through its public interface.

Use local, sandbox, or explicitly authorized test environments. Mark manual
verification `Not applicable` only when no practical user-observable path
exists, and record the concrete reason. Check the complete expected final
state, including required absences and cleanup of verification state.

A manual-verification finding starts one repair cycle. This gate's sequence
establishes full-suite and review proof for the new candidate; then every
affected manual scenario runs again. Before opening a change request, require a
clean worktree and bind the full suite, Standards, Spec, and manual-verification
results to the exact candidate SHA.

**Complete when:** the clean exact candidate implements every criterion,
passes the complete automated suite and both independent review axes, and
passes every applicable manual scenario or carries a concrete non-applicability
reason.
