---
name: council
description: Run a model-diverse subagent council to investigate the same problem from multiple perspectives, compare findings, and produce a final recommendation. Use this skill whenever the user asks for a council, second opinions, multiple agents/models to evaluate one question, parallel investigation, red-team/blue-team comparison, or help deciding between competing technical approaches.
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

Treat the source's named model families and identifiers as preferences to check against the current harness. Disclose substitutions and any perspective-only fallback before launching. Explicit orchestration still requires the source-defined approval after presenting the roster.

# Council

Use this skill to coordinate multiple subagents investigating the same question, with different models first and different assigned perspectives second, then synthesize their reports into one recommendation.

This skill is best for judgment-heavy tasks: architecture tradeoffs, risky bug fixes, code review red-teaming, rollout decisions, incident analysis, and “is this alternative worth pursuing?” questions.

## Workflow

### 1. Frame the council question

State the decision the council should answer in one sentence. Identify:

- the competing options or hypothesis under review;
- the codebase, branch, PR, issue, design, or artifact to inspect;
- whether agents should be read-only or may make code changes;
- the final decision criteria, such as correctness, risk, implementation cost, testability, rollout safety, or product behavior.

If the user’s request is ambiguous, ask only the minimum clarification needed. Otherwise choose sensible defaults and proceed.

### 2. Choose council members

Prioritize model diversity. A council should not default to three agents on the same model with different angles; use that only when the available launch configuration cannot provide multiple useful models, or when the user explicitly asks for one model. If model diversity is unavailable, say so briefly before falling back to perspective-only diversity.

Preferred default roster for a three-member council:

- Opus 4.7 or the strongest available Claude/Opus reasoning model: architecture, correctness, and edge-case analysis.
- GPT 5.5 or the strongest available GPT/Codex model: implementation-grounded review, feasibility, and test strategy.
- An open-source model such as Kimi 2.6, GLM 5.1, or the strongest available OSS/local model: contrarian critique, hidden assumptions, and alternative framing.

If one of these exact models is unavailable in the active harness, use the closest available model from that family and note the substitution. If no open-source model is available, use a third distinct frontier model if possible; otherwise use the strongest remaining model with a deliberately adversarial or specialist angle.

Assign both a model and an angle to each member. Avoid making the angles redundant with the models; for example, do not ask all members to do general architecture review. Useful angle combinations include:

- architect/correctness reviewer;
- implementation/testability reviewer;
- red-team, security, performance, or product-risk reviewer;
- contrarian “argue against the obvious solution” reviewer.

Select models with the host's actual per-child controls; use separate launches if model selection is run-wide. If the requested model resolves differently than expected, treat the resolved launch settings as authoritative and continue unless they make the task infeasible.

When using non-default harnesses, choose valid model IDs for that harness. For example, Claude Code may expose `claude-opus-4-7`, Codex may expose `gpt-5.5`, and open-source models depend on the currently configured local or remote provider. Do not invent unsupported model IDs; if a desired model is not available, select the closest supported substitute and preserve the intended angle diversity.

For read-only investigations, keep all children in the same checkout and explicitly tell them not to edit files. For implementation or prototyping councils, give each local child its own git worktree and branch so they cannot collide.

### 3. Brief before launching

For explicit orchestration requests, briefly tell the user which council members you plan to launch and what each will investigate, then wait for approval before calling the host's subagent launch control.

The shared brief should include:

- repository path or artifact location;
- current branch or base context;
- the exact question to answer;
- relevant background and known concerns;
- required files/symbols to inspect, if known;
- constraints, especially read-only/no commits/no PRs;
- expected report format.

Keep launch prompts short enough that task titles stay compact. If a long brief causes launch validation issues, launch with a minimal prompt and send the full brief to the child agents immediately afterward.

### 4. Ask for structured reports

Ask every council member to return:

1. exact file paths, symbols, docs, or evidence inspected;
2. the current behavior or current implementation;
3. the alternative being evaluated;
4. correctness risks and edge cases;
5. implementation and testing cost;
6. recommendation: keep current approach, pursue alternative, or use a hybrid;
7. confidence level and unknowns.

Encourage independence. Do not share one child’s findings with the others unless you are intentionally doing a second-round critique.

### 5. Collect reports

Read completion messages as they arrive. Do not rely on lifecycle success alone; the useful output is in the child’s report.

If a report is missing key evidence or makes an unsupported claim, send a focused follow-up question to that same child rather than launching a replacement. Reuse existing children for follow-ups because they retain context.

### 6. Synthesize the recommendation

Compare the reports by evidence quality, not by vote count. In the final answer:

- lead with the recommendation;
- call out consensus and disagreements;
- explain why the recommended option wins against the decision criteria;
- explicitly address the user’s stated concern;
- include relevant file paths/symbols without overloading the answer;
- distinguish “do now” from optional future hardening;
- mention confidence and material unknowns.

Prefer a concise decision memo over a transcript summary. The user needs the distilled recommendation, not every intermediate detail.

## Final answer template

Use this shape unless the task calls for something different:

```markdown
## Recommendation

[One or two sentences with the decision.]

## Why

- [Key reason 1]
- [Key reason 2]
- [Key reason 3]

## Tradeoffs and risks

- [Risk or caveat]
- [Testing/rollout implication]

## Final call

[Concrete next step: merge current change, pursue alternative, hybrid, run tests, etc.]
```

## Practical notes

- If the council is read-only, tell children not to modify files, commit, create branches, or open PRs.
- If the council involves PR or branch work, follow the repository’s normal version-control rules and use isolated worktrees for parallel local edits.
- If the council is about code review feedback, mark review comments resolved only after the underlying issue is actually addressed.
- Do not expose internal child agent IDs in user-facing summaries unless the user explicitly asks for them.
