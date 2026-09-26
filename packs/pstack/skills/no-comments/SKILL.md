---
name: no-comments
description: "Spawn Comment Sicko, fix accepted findings, and offer encodings for claimed constraints."
disable-model-invocation: true
---

## Packy host adaptation

This skill originated in Cursor. On Claude Code, Codex, and OpenCode, interpret
Cursor-specific tool names and parameters as examples of the operation, not as
an API contract. Use the host's available tools to achieve the same result.
Delegate only when the host offers subagents and the current instructions permit
it; otherwise perform the steps sequentially. Select a named model only when
that host confirms it is available; otherwise use the parent model or host
default. Never claim a parallel or independent review if it did not occur.
Read `~/.pstack/models.md` only when its `# host` matches the current host;
otherwise use the parent model.

When this skill refers to another pstack skill, read the sibling installed
`SKILL.md` and apply its instructions in the current context. Claude Code's
`disable-model-invocation: true` prevents invoking that skill through its Skill
tool. A user can still invoke each skill explicitly. Replace Cursor transcript,
rule, and cloud-agent paths with the active host's documented equivalents only
when accessible. If required evidence or a capability is unavailable, report the gap and
continue only with independent supported steps. A missing required gate blocks
the action it protects; do not invent a result.

# No comments

Review comments and suppressions in scope. Act on accepted findings.

Use Comment Sicko when that agent is installed. Otherwise assign an available
independent reviewer this brief: identify comments that merely narrate code,
stale comments, workaround comments, `IMPORTANT` or `do not remove` claims,
lint and TypeScript suppressions, and comments that protect a real external
constraint. Require file and line evidence. The reviewer reports findings and
does not edit application code. If no independent reviewer is available,
perform the same audit directly and say that it was not independent.

## Scope

Use the caller's files or diff. Otherwise use the current diff against the base branch, default `main`, including the working tree.

## Steps

1. Run Comment Sicko when installed, or use the reviewer brief above with the
   host's available subagent tool. Pass the scope and ask for `MUST KILL`,
   `RESHAPE`, and `KEEP` findings with reasons. A direct audit uses the same
   categories.
2. Inspect its report and diff. Reject application-code edits, scope escapes, exception-protected deletions, misstated `MUST KILL` reasons, and flags that treat kept intentional code as guilty. Reshape flags on our-code surprises stay actionable. Do not restore those comments. A keep survives only with proof it is about something we cannot change. Audit missed scoped lint and TypeScript suppressions. Correctness or safety suppressions stay actionable `MUST KILL`s. Restore deletions only with exact exceptions and scoped proof. Before accepting thin `IMPORTANT` or `do not remove` kills or keeps, run `/how` or `/why` on their symbol. If a kill is ambiguous, do not restore. If a keep is refuted or still ambiguous, delete it. Revert and rerun one rejected report with the failure named. Reject a second, report it open, and fail `/no-comments`.
3. Fix trivial accepted flags directly by deleting a dead path, dropping a parameter, or using the real API. If any fix needs a shape, run `/architect` once for the accepted set and surrounding code. Stop at the sketch. Architect shapes. Step 4 implements.
4. Implement the smallest root-cause fix in scope. Remove every named workaround. If the root cause is out of scope, land the smallest in-scope fix and report the rest open. The **principle-fix-root-causes** and **principle-redesign-from-first-principles** skills guide intent only. Neither authorizes widening the fence nor fixing instances outside it. Never bolt on symptom guards.
5. Constraint comments say `do not remove`, `do not change wording`, or `talk to X before changing`. Leave keeps about things we cannot change. Offer the cheapest in-scope type, runtime, test, or CI lint. Wait for interactive approval. Unattended and eval require caller pre-approval. If approved, encode then delete. Otherwise delete, report the constraint open, and sketch out-of-scope work.
6. Report the deletion count, restored comments, reruns, architect sketch, fixes, encoding offers, encodings, unenforced constraints, and other open work.
