---
name: spec-driven-implementation
description: Drive a spec-first workflow for substantial features by writing PRODUCT.md before implementation, writing TECH.md when warranted, and keeping both specs updated as implementation evolves. Use when starting a significant feature, planning agent-driven implementation, or when the user wants product and tech specs checked into source control.
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

# spec-driven-implementation

Drive a spec-first workflow for substantial features in Warp.

## Overview

Use this skill for significant features where a written spec will improve implementation quality, reduce ambiguity, or make review easier. Be pragmatic: not every change needs specs.

Specs should usually live in:

- `specs/<linear-ticket-number>/PRODUCT.md`
- `specs/<linear-ticket-number>/TECH.md`

For example:

- `specs/APP-1234/PRODUCT.md`
- `specs/APP-1234/TECH.md`

`specs/` should contain only ticket-named directories as direct children. Do not create engineer-named subdirectories or feature-slug directories there.

If a relevant Linear issue does not already exist, create one before writing specs. Use the Linear MCP tools directly:

- `list_teams` to find the appropriate team
- `list_issue_labels` to inspect the expected labels/tags
- `save_issue` to create the issue with the appropriate team and labels

If the correct team or labels are not obvious from the request and surrounding context, use the host's question control to clarify rather than guessing.

These specs should largely be written by agents, not by hand, and should be checked into source control so they can be reviewed and kept current with the code.

## When specs are required

Strongly prefer specs when the change is substantial, such as:

- product or architectural ambiguity
- expected implementation size around 1k+ LOC
- deep or cross-cutting stack changes
- risky behavior changes where regressions would be expensive
- work where agent quality will improve materially from clearer inputs

Specs are often unnecessary for:

- small, local bug fixes
- straightforward refactors
- narrow UI tweaks with little ambiguity

For pure UI changes, the product spec is often useful while the tech spec may be unnecessary.

## Workflow

### 1. Decide whether the feature needs specs

Evaluate the size, ambiguity, and risk of the feature. If specs will not meaningfully improve execution or review, skip them and focus on verification instead.

### 2. Write the product spec first

Before implementation, create `PRODUCT.md` describing the desired user-facing behavior.

Use [warp:write-product-spec]({{packy.access:warp:write-product-spec}}) to produce it. The product spec should define:

- what problem is being solved
- the desired user experience
- invariants and edge cases
- success criteria
- how the behavior will be validated

If the feature has UI or interaction design, ask for a Figma mock if one exists. If there is no mock, continue but call that out explicitly in the product spec.

Reference the Linear issue in the spec when one exists. Because specs live under `specs/<linear-ticket-number>/...`, this should usually be straightforward.

### 3. Write the tech spec when warranted

Use [warp:write-tech-spec]({{packy.access:warp:write-tech-spec}}) for substantial or ambiguous implementation work.

Prefer a tech spec when:

- the implementation spans multiple subsystems
- architecture or extensibility matters
- there are meaningful tradeoffs to document
- reviewers will benefit more from reviewing the plan than the raw code

It is acceptable to write the tech spec after an e2e prototype if that leads to a more accurate implementation plan. Do not force a premature tech spec when the implementation details are still too uncertain.

### 4. Implement approved specs

After the specs are approved, use [warp:implement-specs]({{packy.access:warp:implement-specs}}) to build from the approved `PRODUCT.md` and `TECH.md`.

The implementation can often be pushed in the same PR as the product and tech specs. As the engineer iterates, keep `PRODUCT.md`, `TECH.md`, code changes, and tests in that same PR so the review reflects the feature that will actually ship.

For large features, the implementer may optionally offer:

- `PROJECT_LOG.md` to track explored paths, checkpoints, and current implementation state
- `DECISIONS.md` to capture concrete product and technical decisions made during design and implementation

These are optional aids, not required outputs.

### 5. Keep specs current during implementation

If implementation changes from the spec, update the spec rather than leaving it stale.

Update `PRODUCT.md` when:

- user-facing behavior changes
- success criteria change
- UX details or edge cases change

Update `TECH.md` when:

- the implementation approach changes
- architectural boundaries move
- risks, dependencies, or rollout details change
- the testing or validation plan changes

The checked-in specs should describe the feature that actually ships, not just the initial intent. Keep those spec updates in the same PR as the related code changes whenever practical.

### 6. Verify behavior against the spec

Before considering the work complete, make sure verification maps back to the specs. Prefer tests and artifacts that validate the product behavior directly:

- unit tests and regression coverage that follow the repository's local testing conventions
- integration tests for critical user flows
- loom walkthroughs or equivalent feature demonstrations when appropriate
- screenshots or videos when useful for UI-heavy work

## Best Practices

- Be pragmatic above all else.
- Write specs to improve input quality for agents, not as ceremony.
- Keep product specs behavior-oriented and implementation-light.
- Keep tech specs implementation-oriented and grounded in current codebase patterns.
- When a spec references relevant code chunks, include the inspected commit SHA in the file reference when possible and link the reference to the exact GitHub `blob/<sha>/...#Lx-Ly` lines.
- Use review time to validate specs and behavior, not to over-index on code style nits.

## Related Skills

- `warp:implement-specs`
- `warp:write-product-spec`
- `warp:write-tech-spec`
