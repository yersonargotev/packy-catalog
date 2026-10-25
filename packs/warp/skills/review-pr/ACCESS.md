---
name: review-pr
description: Review a pull request diff and write structured feedback to review.json for the workflow to publish. Use when reviewing a checked-out PR from local artifacts like pr_diff.txt and pr_description.txt and producing machine-readable review output instead of posting directly to GitHub.
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

Select three independent contexts before reviewing:
- `TARGET_REPO`: the intended PR branch checkout, including repository-local
  `review-pr-local`, security and spec companion guidance when applicable.
- `INPUT_DIR`: the explicitly selected artifact directory containing the exact
  annotated diff, PR description and optional spec context. Default only to the
  selected target checkout, never the helper/cache location.
- `OUTPUT_DIR` and `SCRATCH_DIR`: explicit writable artifact and disposable state
  locations outside immutable source/snapshot/prepared trees.

Set `SKILL_ROOT` to the returned `resource_root`. Run repository inspection from
`TARGET_REPO`; read input artifacts using absolute paths under `INPUT_DIR`.
Generate only `$OUTPUT_DIR/review.json` and selected scratch artifacts. Local
companions remain target-repository guidance; do not automatically substitute
`warp:check-impl-against-spec` or invent security/local Catalog dependencies.

When the resolver is requested, invoke the returned helper with explicit target
context and explicit output. `OZ_REPO_ROOT` is mandatory for cached execution:

```sh
OZ_REPO_ROOT="$TARGET_REPO" python3 -B "$SKILL_ROOT/scripts/resolve_spec_context.py" \
  --repo "$REPO_SLUG" --pr "$PR_NUMBER" > "$SCRATCH_DIR/spec_context.md"
```

`REPO_SLUG` and PR number identify that target PR. Set `OZ_REPO_ROOT` before
importing the helper; direct API callers also supply `workspace=Path(TARGET_REPO)`
to `resolve_spec_context_for_pr` / `read_local_spec_files`. The native resolver's
script-location fallback is unsuitable for cached use. Its remote path needs an
authorized existing token and GitHub read access; retrieval never resolves tokens
or invokes APIs. A previously provided spec artifact stays an explicit input.
Use the generated scratch spec path when applicable; never infer artifacts from
cache placement. Missing intended artifacts or required runtime access stop that
branch rather than consulting cache/decoy specs.

Run the mandatory final validator from the returned tree against the exact input:

```sh
python3 -B "$SKILL_ROOT/scripts/validate_review_json.py" \
  --review-json "$OUTPUT_DIR/review.json" --diff "$INPUT_DIR/pr_diff.txt"
```

The schema, annotation-only inline locations, severity/evidence/suggestion rules,
pre-verdict audit and validation loop below remain mandatory. Produce the review
artifact only; do not post reviews/comments. Python bytecode and dependencies,
if needed, belong to separate writable scratch, not the cached tree.

# Review PR Skill

Review the current pull request and write the output to `$OUTPUT_DIR/review.json`.

## Context

- The working directory is the explicitly selected TARGET_REPO PR branch checkout.
- Read the exact annotated diff at `$INPUT_DIR/pr_diff.txt`.
- Read the PR description at `$INPUT_DIR/pr_description.txt`.
- If the explicitly supplied or scratch-generated `spec_context.md` exists, it contains spec context for implementation-vs-spec validation.
- When the prompt references `.agents/skills/review-pr/scripts/resolve_spec_context.py`, use the returned resolver with OZ_REPO_ROOT and explicit scratch output as specified above to materialize `spec_context.md` on demand instead of expecting spec content to be embedded in the prompt.
- Focus on files and lines changed by this PR.
- Do not post comments or reviews to GitHub directly.

## Review Scope

- Prioritize correctness, security, error handling, and meaningful performance issues.
- Treat comment quality and test quality as first-class review priorities alongside those — not as optional nits to mention only if time allows; check both against the repository's own conventions before finalizing your verdict.
- If the consuming repository provides a local `security-review-pr` companion skill or the prompt requests a security pass, apply it as supplemental guidance on code PRs and fold any security findings into the same `review.json` rather than emitting a separate output.
- When `spec_context.md` exists, use the repository's local `check-impl-against-spec` skill if available and treat material spec drift as a review concern.
- Include style or nit comments only when you can provide a concrete suggestion block.
- If a concern involves untouched code, mention it in top-level `body` instead of an inline comment.
- Do not suggest adding test cases that only vary constructor inputs or struct fields when the existing test already covers the meaningful behavior. Only suggest new tests when they exercise a distinct code path or edge case.
- When a PR is clearly a V0 or initial implementation, frame robustness suggestions (timeouts, retries, lifecycle management) as optional future work rather than blocking concerns, unless they risk correctness, security, or data loss.

## Repository-specific guidance

Before reviewing, actively check whether the consuming repository ships a companion `review-pr-local` skill that specializes this one for its own conventions: if the prompt names one, read it there; otherwise look for one in the repository itself (for example, at `.agents/skills/review-pr-local/SKILL.md`, though a repository may place or name its specialization differently). If a companion exists, read it and apply its guidance as part of this review. If none turns up either way, rely on the core contract alone.

The companion is expected to specialize this skill's commenting and testing guidance with the repository's own conventions. It may never change the output JSON schema, the severity labels, the safety rules, the evidence rules, the suggestion-block constraints, or the diff-line-annotation contract described elsewhere in this skill.

## Diff Line Annotations

The diff file uses these prefixes:

- `[OLD:n]` for deleted lines on the old side. Use `"LEFT"`.
- `[NEW:n]` for added lines on the new side. Use `"RIGHT"`.
- `[OLD:n,NEW:m]` for unchanged context. Use `"RIGHT"` with line `m`.

Treat these annotations as the only source of truth for inline comment locations. For every inline comment you emit, first identify the exact annotated line in `pr_diff.txt` (or the inlined PR diff) and copy its path, side, and line number into `review.json`. Do not infer line numbers from prose, rendered GitHub views, file lengths, surrounding spec text, or unannotated snippets. If you cannot point to a specific `[NEW:n]`, `[OLD:n]`, or `[OLD:n,NEW:m]` line in the annotated diff, put the feedback in top-level `body` instead of `comments`.

## Comment Requirements

Every comment body must start with one of these labels:

- `🚨 [CRITICAL]` for bugs, security issues, crashes, or data loss.
- `⚠️ [IMPORTANT]` for logic problems, edge cases, or missing error handling.
- `💡 [SUGGESTION]` for worthwhile improvements or better patterns.
- `🧹 [NIT]` for cleanup only when the comment includes a suggestion block.

A confirmed violation of the repository's commenting or testing guidelines can warrant `⚠️ [IMPORTANT]` on its own — regardless of how clean the rest of the PR is. Do not default these to `🧹 [NIT]`/`💡 [SUGGESTION]` just because the surrounding code looks good.

Write comments with these constraints:

- Be concise, direct, and actionable.
- Do not add compliments or hedging.
- Prefer single-line comments.
- Keep ranges to at most 10 lines.
- Restrict inline comments to lines that appear explicitly in the annotated PR diff.
- Only create file-level or inline comments for files that exist in this PR's diff.
- If the relevant file or line is not part of the diff, put the feedback in top-level `body` instead of `comments`.
- Before adding each comment object, verify that its `path`, `side`, `line`, and optional `start_line`/`start_side` correspond to real annotations in the same file's diff section.

## Suggestion Blocks

When proposing a code change, use:

```suggestion
<replacement code here>
```

Rules:

- Match the exact indentation of the original file.
- Include only replacement code.
- The block content replaces **exactly** the lines `start_line`–`line` inclusive. Every line inside the block becomes the new file content for that range, and GitHub leaves all other lines untouched.
- Do **not** include lines outside that range. Lines above `start_line` and below `line` remain in the file; repeating them inside the block causes them to appear twice after the suggestion is committed.
- Never open the block with a line that already appears immediately above `start_line`, and never close the block with a line that already appears immediately below `line`. If you need those lines as anchors, widen `start_line` or `line` so they are actually part of the replaced range.
- Count brace, bracket, paren, and block-delimiter depth (`{`, `[`, `(`, `end`, etc.) across the original replaced lines and ensure the replacement ends at the same depth. Do not emit phantom closing tokens, and do not drop required ones.
- When unsure of the surrounding context, widen `start_line`/`line` to include enough real lines from the diff rather than guessing at surrounding tokens.
- For multi-line suggestions, set `start_line` and `start_side` to the first line, and `line` and `side` to the last line.

## Output Format

Create `review.json` with this shape:

```json
{
  "verdict": "REJECT",
  "body": "## Overview\n...\n\n## Concerns\n- ...\n\n## Verdict\nFound: 1 critical, 2 important, 3 suggestions\n\n**Request changes**",
  "comments": [
    {
      "path": "path/to/file",
      "line": 42,
      "side": "RIGHT",
      "start_line": 40,
      "start_side": "RIGHT",
      "body": "⚠️ [IMPORTANT] Short explanation\n\n```suggestion\nreplacement\n```"
    }
  ]
}
```

Field rules:

- `verdict` is required and must be exactly the string `"APPROVE"` or `"REJECT"` (uppercase). Map your final recommendation as: `Approve` or `Approve with nits` → `"APPROVE"`; `Request changes` → `"REJECT"`. The `verdict` and the human-readable recommendation in top-level `body` must agree.
- Top-level `body` is the GitHub review body and is required. Use `body`, not `summary`, for the review overview and final recommendation.
- `comments` is required and must be an array. Use an empty array when there are no inline comments.
- `path` must be relative to the repository root.
- `line` is required and must target the correct side.
- `start_line` is optional and only for multi-line ranges. When `start_line` is present, `start_side` is required and must be `"LEFT"` or `"RIGHT"`.
- `side` must be `"LEFT"` or `"RIGHT"`.

## Body Requirements

The top-level `body` must include:

- A high-level overview of the PR.
- Important concerns and any untouched-code concerns that could not be commented inline.
- Issue counts in the format `Found: X critical, Y important, Z suggestions`.
- A final recommendation of `Approve`, `Approve with nits`, or `Request changes`. This recommendation must match the top-level `verdict` field (`Approve` / `Approve with nits` → `"APPROVE"`; `Request changes` → `"REJECT"`).

## Pre-Verdict Audit

Before drafting the top-level `body` or choosing `verdict`, complete this audit — a holistic read-through of the diff is not sufficient.

- **Comments**: List every comment (doc comment or inline) the diff adds or changes, one by one with its file:line. For each one, check it individually against the repository's own commenting guidelines, whatever form those take — or, if the repository defines none, judge it against the commenting distribution of existing code in the project (density, tone, what existing comments explain vs. omit). Evaluate compliance independently of the comment's writing quality, technical accuracy, or how subtle/important the issue it describes is: none of those qualities excuses a violation of an applicable guideline or a clear mismatch with the codebase's own norms.
- **Tests**: Check every test the diff adds or changes against the repository's own testing guidelines, whatever form those take.

## Final Checks

Before returning or uploading `review.json`:

- Fix invalid JSON if validation fails.
- Confirm line numbers match the annotated diff.
- Run the bundled validator against the exact annotated diff you reviewed:
    ```sh
    python3 -B "$SKILL_ROOT/scripts/validate_review_json.py" --review-json "$OUTPUT_DIR/review.json" --diff "$INPUT_DIR/pr_diff.txt"
    ```
  If the script reports any invalid comments, fix `review.json` and rerun it. Do not return or upload `review.json` until this validator passes. If the script path is not present at that exact location, locate `validate_review_json.py` under the loaded `review-pr` skill directory and run that copy with the same arguments.
- Do not run `gh pr review`, `gh pr comment`, `gh api`, or any other command that posts to GitHub.

Your only output is the final `$OUTPUT_DIR/review.json`.
