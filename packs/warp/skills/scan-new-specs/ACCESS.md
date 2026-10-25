---
name: scan-new-specs
description: DEPRECATED and retired as of 2026-08-20. Do not invoke, and do not schedule. This skill scanned for merged PRODUCT.md specs and auto-drafted docs PRs, which produced documentation for features that had not shipped. Docs for newly shipped features are now triggered by the weekly release and gated on documentation-worthiness by the missing_docs skill in warpdotdev/docs. If you were about to run this skill to find docs gaps, run missing_docs in drift-watch mode instead.
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

**Retired inventory only. Do not invoke this skill and do not schedule it. Its existing scheduled agent stays paused.** Reading or obtaining this resource never authorizes execution, revival, resumption, scheduler access or scheduling. The alternatives below are guidance for a separate authorized request; `missing_docs` remains external to the Catalog.

# scan-new-specs (deprecated)

**Retired 2026-08-20. Do not invoke this skill and do not schedule it.**

Its scheduled agent (`0ITuF9vNJ1RiO00Szlm1fW`) is paused and stays paused.

## Why it was retired

The skill fired on **spec merge**, which happens before a feature ships. Two failures followed from that single design choice:

- **It drafted docs for unreleased and sometimes abandoned work.** A merged spec is not a shipped feature. The agent had no evidence of what users had actually received, so pages were written for behavior that had not landed, or had landed differently, or never landed at all.
- **It treated every spec as a docs task.** Nothing asked whether a change warranted documentation. Pure UI changes, small intuitive additions, and behind-the-scenes work all became draft PRs, and the docs repo accumulated unvetted content debt faster than anyone could review it.

## What replaces it

The `missing_docs` skill in `warpdotdev/docs`, running in drift-watch mode. It differs in the two ways that matter:

- **Release-triggered.** `scripts/check_new_release.py` gates each run on a new stable release, so the pipeline sees what actually shipped rather than what was planned. A daily schedule does per-release work.
- **Gated on worthiness.** Every candidate is evaluated against `.agents/references/docs-worthiness-criteria.md` before anything is drafted, with a default of no docs and a requirement to name concrete evidence. Verdicts, including rejections, are recorded in `references/changelog_decisions.md` so nothing is re-litigated.

Anything genuinely worth documenting re-surfaces there once it ships.

## If you were about to run this

- **Looking for docs gaps?** Run `missing_docs` in drift-watch mode from the `warpdotdev/docs` repo.
- **You are an engineer who wants docs for your feature?** For a separate authorized request, obtain `warp:write-feature-docs` with the pinned command above and follow its returned entry interactively. It still works, and it still walks you through spec research and outline confirmation. It no longer runs headlessly.
- **Setting up a scheduled docs agent?** Use `missing_docs`, not this. Scheduling this skill reintroduces exactly the flooding it was retired for.

## Related skills

- `missing_docs` (in `warpdotdev/docs`) — the release-triggered, worthiness-gated replacement
- `warp:write-feature-docs` — still supported for direct, interactive use by an engineer
