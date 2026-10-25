---
name: resolve-merge-conflicts
description: Resolve Git merge conflicts by extracting only unresolved paths, conflict hunks, and compact diffs instead of loading whole files into context. Use when a merge, rebase, cherry-pick, or stash pop stops on conflicts, when `git status` shows unmerged paths, or when files contain conflict markers.
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

Set `TARGET_REPO` to the intended repository and `SKILL_ROOT` to the returned
`resource_root`. Every helper invocation below supplies `--repo "$TARGET_REPO"`;
run subsequent Git commands from that same checkout. The helper reads compact
conflict/index-stage context only; obtaining it does not modify or stage files.
Keep scratch outside immutable resources and resolve one file at a time.

# Resolve Merge Conflicts

## Overview

Resolve conflicts without opening full files unless the compact view is insufficient. Start with a summary, then inspect one conflicted file at a time.

## Workflow

1. Start with a summary.

```bash
python3 -B "$SKILL_ROOT/scripts/extract_conflict_context.py" --repo "$TARGET_REPO"
```

Use the summary to identify which files are unresolved, which index stages exist, and how many text hunks each file contains.

2. Drill into one file.

```bash
python3 -B "$SKILL_ROOT/scripts/extract_conflict_context.py" --repo "$TARGET_REPO" --file path/to/file
```

Prefer this over reading the whole file. The script prints only nearby context, the `ours` / `base` / `theirs` sections for each hunk, and a compact unified diff between `ours` and `theirs`.

3. Resolve the file.

- Take one side wholesale with `git checkout --ours -- path/to/file` or `git checkout --theirs -- path/to/file` when appropriate.
- Otherwise edit the file directly and remove the conflict markers.
- Read more of the file only if the compact output is not enough to decide the correct merge.

4. Re-check unresolved files.

```bash
python3 -B "$SKILL_ROOT/scripts/extract_conflict_context.py" --repo "$TARGET_REPO"
git diff --name-only --diff-filter=U
```

5. Validate the resolution.

- Ensure no unmerged paths remain.
- Ensure no `<<<<<<<`, `=======`, or `>>>>>>>` markers remain in the resolved files.
- Run targeted tests, builds, or linters for the touched area.
- Stage the resolved files.

## Commands

### Summary only

```bash
python3 -B "$SKILL_ROOT/scripts/extract_conflict_context.py" --repo "$TARGET_REPO"
```

### Detailed view for one file

```bash
python3 -B "$SKILL_ROOT/scripts/extract_conflict_context.py" --repo "$TARGET_REPO" --file path/to/file
```

### Detailed view for all conflicted files

```bash
python3 -B "$SKILL_ROOT/scripts/extract_conflict_context.py" --repo "$TARGET_REPO" --all
```

### JSON output

```bash
python3 -B "$SKILL_ROOT/scripts/extract_conflict_context.py" --repo "$TARGET_REPO" --file path/to/file --json
```

### Tune output size

```bash
python3 -B "$SKILL_ROOT/scripts/extract_conflict_context.py" --repo "$TARGET_REPO" \
  --file path/to/file \
  --context 3 \
  --max-lines 60
```

## Notes

- Use the script before opening conflicted files directly.
- Resolve one file at a time to keep context small.
- Expect marker-based text conflicts and index-only conflicts such as add/add or modify/delete. The script summarizes both, and it falls back to index-stage previews when the worktree file has no conflict markers.
