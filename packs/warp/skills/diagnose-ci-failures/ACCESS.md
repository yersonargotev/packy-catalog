---
name: diagnose-ci-failures
description: Diagnose CI failures for a PR using the GitHub CLI, extract error logs, and generate a plan to fix them. Use when the user asks to check CI status, pull CI issues, triage test failures, or investigate PR build failures.
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

Use the intended PR checkout and authenticated read-only GitHub CLI access.
Write the reviewable plan to an explicit user-selected or disposable writable
path. If `create_plan` is unavailable, write that plan as a document with the same
sections and present it for user review; diagnosis does not apply code changes.
An offer to create a missing PR is not permission to create one and is not a
required `create-pr` dependency. The error-resolution reference below is Warp's
own prepared guidance; retrieval does not execute those repairs.

# diagnose-ci-failures

Programmatically diagnose CI failures for a PR and generate a plan to fix them.

## Overview

This skill provides a deterministic workflow to check CI status for a PR, extract failure logs, analyze errors, and create a plan (not code changes) to resolve issues. The output is always a plan document that can be reviewed before execution.

## Workflow

### 1. Verify PR exists for current branch

Get the current branch and check if a PR exists:

```bash
# Get current branch
git branch --show-current

# Check for PR
GH_PAGER=cat gh pr view <branch-name> --json number,title,url,state
```

If no PR exists, inform the user and offer to create one using the `create-pr` skill.

### 2. Check CI status

Fetch the status of all CI checks:

```bash
GH_PAGER=cat gh pr view <branch-name> --json statusCheckRollup
```

Parse the output to identify:
- Completed checks vs. in-progress checks
- Successful checks
- Failed checks with their names and details URLs

If CI is still running, inform the user which checks have already failed or passed, highlight the checks that are still running, and suggest waiting for completion before diagnosis.

### 3. Extract failure logs

For each failed check, pull the logs using the run ID from the status check:

```bash
GH_PAGER=cat gh run view <run-id> --log-failed
```

Focus on extracting:
- Error messages and their locations (file paths, line numbers)
- Compilation errors (unused imports, type mismatches, etc.)
- Linting/clippy errors with specific lint names
- Test failure messages and stack traces
- Build failures and their root causes

### 4. Categorize errors

Group errors by type:
- **Formatting issues**: `cargo fmt` failures
- **Linting issues**: `cargo clippy` warnings/errors
- **Compilation errors**: Type errors, missing imports, signature mismatches
- **Test failures**: Failing tests with their names and failure reasons
- **Platform-specific issues**: WASM, Linux, macOS, Windows-specific failures

### 5. Generate fix plan

Create a plan document (using `create_plan` tool) with:
- **Problem Statement**: Summary of failing checks
- **Current State**: What errors were found and where
- **Proposed Changes**: Specific fixes needed for each error category
- **Validation Steps**: Commands to verify fixes (fmt, clippy, tests, presubmit)

The plan should reference [warp:fix-errors]({{packy.access:warp:fix-errors}}) for detailed guidance on resolving specific error types.

## Important Notes

- **GitHub CLI paging**: Set `GH_PAGER=cat` on every `gh` invocation. The GitHub CLI does not support `--no-pager` as a global option; `GH_PAGER` and `PAGER` are its documented paging controls
- **Always create a plan first**: Never make code changes directly. Generate a plan for user review
- **Check test status in CI**: Even if tests fail locally, verify they passed in CI before flagging as issues
- **Unrelated test failures**: If tests passed in CI but fail locally, they may be environment-specific or flaky
- **Multiple error types**: Fix one category at a time (e.g., all clippy errors before tests)
- **Cross-reference fix-errors skill**: For detailed error resolution strategies, use [warp:fix-errors]({{packy.access:warp:fix-errors}})

## Common CI Check Names

- `Formatting + Clippy (MacOS)`
- `Formatting + Clippy (Linux)`
- `Run MacOS tests`
- `Run Linux tests`
- `Run Windows tests`
- `Check CI results` (summary check)
- `WASM build`

## Example Commands

**Get PR status with details:**
```bash
GH_PAGER=cat gh pr view --json number,title,state,statusCheckRollup
```

**Get logs from specific failed run:**
```bash
GH_PAGER=cat gh run view 12345678 --log-failed
```

**Check for specific error in logs:**
```bash
GH_PAGER=cat gh run view 12345678 --log-failed 2>&1 | grep -A 5 "error:"
```
