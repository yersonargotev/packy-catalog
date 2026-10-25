---
name: brandalf
description: Guides creation, revision, and review of Warp- or Oz-branded assets. Use when working on launch pages, docs, HTML/CSS components, UI mockups, prompts, social assets, copy, presentations, or any other branded deliverable that should look and sound unmistakably Warp or Oz.
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
only the source-defined fallback. Retrieval is content access, not invocation of any workflow or proactive feedback
trigger. It grants no approval to launch workers, access credentials, post external
content, commit, push or schedule anything. Execute only the requested procedure
under its preserved source contract and the active host/user authorization.

## Reviewed execution context

The hosted brand source is a runtime input, not part of offline retrieval. Fetch
it only when performing branding. Standalone Brandalf asks whether to retry or
proceed when unavailable; the walkthrough caller has its own explicit fallback.

# Brandalf

Use this skill as the entrypoint for Warp and Oz branding work.

## Source of truth

The canonical brand skill lives at:

`https://warp-brand-site.vercel.app/brand/skill`

Before creating or revising any Warp- or Oz-branded asset, read that URL and use its contents as the source of truth for:

- visual style
- color usage
- typography
- voice and tone
- component rules
- naming and capitalization
- implementation guidance

Do not rely on memory when the hosted skill can be fetched.

## Workflow

1. Fetch the hosted brand skill from `https://warp-brand-site.vercel.app/brand/skill`.
2. Extract the guidance relevant to the asset being created.
3. Apply those rules to the requested output.
4. When presenting the result, briefly note any important brand constraints that materially shaped the output.

## Scope

Use Brandalf for assets related to:

- Warp
- Oz
- Warp Drive
- agentic development / ADE materials that are explicitly branded for Warp or Oz

## If the source is unavailable

If the hosted skill cannot be fetched, say that the canonical branding source was unavailable and ask the user whether to proceed with best-effort branding guidance or to retry fetching it.
