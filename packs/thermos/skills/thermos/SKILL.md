---
name: thermos
description: "Run combined correctness/security and maintainability branch reviews, then synthesize the findings."
disable-model-invocation: true
---

# Thermos

Run two independent review passes using the Thermos rubrics. Apply this workflow
when the user requests Thermos or a combined deep review. The task is a review:
return findings without editing files, posting comments, committing, or merging.

## Prepare one scope

1. Determine the requested PR, branch comparison, or worktree changes. Resolve
   the PR target or repository's default branch and merge base for branch
   comparisons; use `git diff <base>...HEAD` only for committed branch changes.
   Include staged, unstaged, and relevant untracked files for a worktree review.
   Record the base/head commits and changed paths so both reviewers inspect the
   same version. If the scope changes during review, reconcile affected findings.
2. Gather the scoped diff, changed-file contents, relevant repository guidance,
   and spec or issue when available. Let reviewers read affected callers and
   dependencies to verify consequences outside the diff.
3. Read both complete rubrics from the installed sibling skills:
   [thermo-nuclear-review](../thermo-nuclear-review/SKILL.md) and
   [thermo-nuclear-code-quality-review](../thermo-nuclear-code-quality-review/SKILL.md).
   Resolve their installed locations through the host's skill metadata if these
   relative paths are unavailable. These skills preserve explicit invocation;
   pass their text directly when a worker cannot load them. If a rubric cannot
   be read, report the missing dependency instead of substituting a shorter audit.

## Run both reviews

Launch independent workers concurrently when the host exposes and permits
delegation. Use the host's actual tool schema and available agent types:

| Surface | Reviewer dispatch |
| --- | --- |
| Claude Code | Select the installed `thermo-nuclear-review-subagent` and `thermo-nuclear-code-quality-review-subagent` through the available agent tool. Pass the complete matching rubric in each task; Claude cannot preload these manual-only skills. |
| Codex | Select those custom roles if exposed by the session's delegation tool. Otherwise assign available general review workers with the complete corresponding rubric and the work contract below. |
| OpenCode | Select the installed subagents through its task/delegation tool. Supply each matching rubric explicitly if skill loading is restricted. |

Each worker receives the **same** scope, diff, file context, guidance, and spec,
plus its own complete rubric. Assign this work contract explicitly:

- Correctness reviewer: bugs, breaking behavior, security, developer experience,
  and feature-gate leaks using `thermo-nuclear-review`.
- Quality reviewer: maintainability, structural simplification, the 1k-line
  threshold, branching growth, and boundaries using
  `thermo-nuclear-code-quality-review`.
- Audit independently before reading the other review. Report only problems
  introduced by the scoped changes; inspect accessible dependencies before
  asserting impact. Return prioritized findings with file:line evidence,
  impact, remedy, and coverage gaps. Make no edits or external writes and
  launch no nested workers.
- The correctness reviewer reads existing PR/MR discussion only **after** its
  independent audit and only when it has medium-or-higher findings. Validate
  and attribute incorporated findings; disclose unavailable discussion access.

Do not assume Cursor's `Task`, `run_in_background`, or `shell`/`explore` agent
names exist on another host. If named agents are unavailable, a general worker
with the full assignment above is sufficient. If delegation is unavailable or
prohibited, run the two complete rubrics as separate sequential passes in the
current session and disclose that they did not have independent contexts.
If capacity allows only one worker at a time, run them sequentially with the
same captured inputs. Wait for both passes to finish; report failed or incomplete
passes as coverage gaps, never as clean reviews.

## Synthesize

Return findings first, prioritized and deduplicated across passes. Use overlap
as corroboration, not as a reason to inflate severity. Resolve disagreements
against the code and requested behavior. Give a unified verdict, the strongest
evidence, and remaining uncertainty. If worker summaries are already visible,
avoid repeating them wholesale. Report no findings only when both complete
passes support that conclusion, and distinguish it from incomplete coverage.
