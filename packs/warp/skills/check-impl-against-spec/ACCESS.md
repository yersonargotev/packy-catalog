---
name: check-impl-against-spec
description: Compare a pull request's implementation against spec context in spec_context.md and feed any material mismatches into review.json. Use during PR review when approved or repository spec context is available.
---

## On-demand context

Use the initiating descriptor's `surface` and `snapshot_id` for this procedure
and every nested request, including requests made by a delegate:

```sh
packy get skill warp:<skill> --surface <initiating-surface> --snapshot <initiating-snapshot-id> --json
```

Read and follow prepared Warp entries at the authored links below. Native skill
registrations and installed sibling copies are unnecessary. Carry the same host,
snapshot, target project, and writable scratch/output context in delegate briefs.
Selection changes affect new independent requests only. Keep previously returned
paths; if retained content is missing, stop and restore that exact revision.
Never substitute a newer revision or another Pack's similarly named workflow.

Resolve supporting files relative to this entry and `resource_root`, reading
only the active branch's references. Resolve repository paths, specs, review
inputs and generated files against the intended target project. Select writable
scratch/output separately from immutable resource trees. Retrieval supplies
instructions only: model, worker, MCP, credential, repository, scheduler, runtime
and validation prerequisites remain unverified until checked in the active host.
Honor the source's approvals, domain boundaries, stopping rules and fallbacks.

Use only controls actually exposed by the initiating host. On Codex, use its
available local subagent launch, message/resume and wait controls; on Claude Code,
use its available Agent control and supported original-author follow-up. Check
available model identifiers and whether model selection is per child or per run.
Use separate launches when only run-wide model selection exists. If a required
control is absent, report the limitation and stop that branch unless its source
explicitly provides a fallback. A lifecycle success is not validation evidence.
Use the host's question control (with the source's choices and free-text option),
or ask in conversation and wait for the actual reply when no question tool exists.
Use available host file, shell, search and computer-use controls where applicable;
access does not provision Warp/Oz tools or remote execution. Remote-only checks
require an actual authorized remote capability; otherwise report the gap and use
only the source-defined fallback. Obtaining these instructions grants no approval
to launch workers, post external content, commit, push or schedule anything.

# Check implementation against spec

Use this skill only when `spec_context.md` exists during PR review.

## Goal

Determine whether the implementation in the checked-out PR materially matches the approved spec context. This is a supplement to the normal code review, not a separate output.

## Inputs

- `spec_context.md` contains the spec context to compare against. It may include both product spec content (intended behavior, acceptance criteria) and tech spec content (implementation details, file changes).
- `pr_diff.txt` contains the annotated diff for the PR.
- `pr_description.md` may contain additional scope or rationale.
- The working tree contains the PR branch contents.

## Process

1. Read `spec_context.md` and extract the concrete commitments it makes:
   - required behaviors (from the product spec)
   - required files or subsystems to change (from the tech spec)
   - stated constraints
   - required follow-up steps, validation, or migrations
2. Compare those commitments against the actual implementation in `pr_diff.txt` and the checked-out files.
3. Treat small implementation-level adjustments as acceptable when they preserve the spec's intent. Do not flag harmless differences in naming, structure, or low-level technique.
4. Flag a mismatch only when it is material, such as:
   - required behavior in the product spec is missing
   - the implementation contradicts a spec decision
   - the change introduces significant unplanned scope
   - a required validation, migration, or compatibility step from the tech spec is absent

## Outputs

- Do not create a separate report file.
- Fold spec-alignment findings into `review.json`.
- Put broad spec-drift concerns in the review summary.
- Add inline comments only when the mismatch can be tied to changed lines in the diff.
- Treat material spec drift as at least an important concern.
- If the implementation matches the spec closely enough, do not add comments just to mention alignment.

## Boundaries

- Do not require literal one-to-one implementation of the spec when the PR achieves the same outcome safely.
- Do not speculate about spec details that are not actually present in `spec_context.md`.
- Do not post to GitHub directly.
