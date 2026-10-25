---
name: research
description: Delegate noisy investigation to one or more subagents so the orchestrator's context stays clean, then work from the distilled answer. Use this skill whenever answering a question would require reading many files, long logs, large diffs, or wide codebase surveys — i.e. when producing the answer generates far more noise than the answer itself. Use it for "how does X work", "where is Y used", "what's the root cause of Z", "summarize this PR/log" style questions, and reach for it liberally before reading a pile of files inline.
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

Use only advertised model identifiers. The source's `gpt-6-luna-medium` and `gpt-6-luna-xhigh` are search-role examples, not portable model IDs. Disclose any substitution and its reasoning setting. Verify that workers are local; if local workers or a suitable search model are unavailable, report the limitation before delegation.

# Research

Use this skill to answer a question by delegating the *work of finding the answer* to a subagent, so that the byproducts of that work — file contents, log noise, dead-end reads — never enter your own context. You get back a distilled answer plus the evidence that supports it, and you stay sharp for the actual task.

## Why this matters

Your context window is your most valuable and limited resource. Reading twenty files to discover that three of them mattered permanently pollutes your context with seventeen files of noise, degrading every subsequent decision you make. A subagent absorbs that noise on your behalf and hands you only the signal. Think of it as asking a colleague to dig through the archives and report back, rather than dumping the whole archive on your desk.

## When to use it

Reach for research delegation when **the cost of producing the answer is far greater than the answer itself**. Strong signals:

- You'd need to read many files to find the few that are relevant.
- You'd need to wade through long test output, CI logs, or stack traces to extract a failure.
- You'd need to survey how a pattern, API, or symbol is used across the whole repo.
- You'd need to read and summarize a large diff or PR.
- The question has several independent sub-parts that could be investigated separately.

**Examples — good fits:**

- "What's the root cause of this failing test?" (the subagent reads the logs and traces the code; you get the cause)
- "How is `SessionManager` used across the codebase?" (the subagent greps and reads; you get a summary with call sites)
- "Summarize what this 4,000-line PR changes and why." (the subagent reads the diff; you get the shape of it)

**Examples — do NOT delegate:**

- Reading 2–3 files you already know you need. Just read them directly; delegation adds latency for no context savings.
- A single `grep` or one-line lookup. Do it yourself.
- **Anything where you need the raw material for your next step.** If you're about to *edit* the files you'd be reading, delegating is counterproductive — you'd just have to re-read them yourself to make the change. Research delegation pays off when the output is a *conclusion*, not when it's *material you'll work on directly*.

The cost of a subagent is real (latency and tokens), so the test is always: does the noise I'd avoid outweigh that cost?

## How to do it

### Spawn locally with a search model

Always spawn research subagents as **local** agents, never remote — including when the parent is a factory or cloud agent.

Pick the model for the search task, not your own. Research subagents should search and distill, not analyze: prefer an available lightweight search model at medium reasoning for simple search, and higher reasoning for more involved requests (for example, tracing data flow through call sites).

### Single vs. parallel

Default to a **single subagent**. Spawn **multiple subagents in parallel** only when the question genuinely decomposes into independent sub-parts that don't need to share intermediate findings — for example, "how does auth work AND how does billing work AND how does the rate limiter work" are three independent investigations that can run at once. Parallelism is a capability worth using when the parts are truly independent, since separate subagents can investigate simultaneously; but don't force a single coherent question into artificial fragments.

### Brief the subagent well

The subagent does not share your intent, so spell it out. A good research brief includes:

- The exact question to answer.
- Where to look (repo path, branch, suspected files/symbols if you know them).
- That it is **read-only** — it should investigate and report, not modify files, unless the task explicitly calls for changes.
- The output you want back (see below).

### Ask for signal, not transcript

Tell the subagent to return a **distilled answer plus its supporting evidence**, not a raw dump. Specifically:

1. The direct answer to the question.
2. The key evidence: exact file paths and symbols (e.g. `src/session.rs:142`, `fn reconnect`), so you can jump straight to what matters.
3. Anything surprising or any caveats/unknowns it hit.

The whole point is that the noise stays with the subagent. If a report comes back bloated, send a focused follow-up to the *same* subagent asking it to tighten the answer — it retains its context and can refine cheaply.

## After you get the answer

Work from the distilled result. If you later find you need the underlying files to make edits, read them directly at that point — now you know exactly which ones matter, so you read three files instead of twenty.
