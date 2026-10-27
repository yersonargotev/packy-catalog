# Warp repository and reporting: reviewed on-demand access

This review records its original Catalog generation. Surface names, Pack
versions, and acceptance evidence below are historical; see the
[current setup guide](../packy-cli.md) for the `agents` and `claude` contract.

[Issue #97](https://github.com/yersonargotev/packy-catalog/issues/97) covers exactly
13 skills on Codex and Claude Code. Warp advances independently from 2.3.0 to
2.4.0; its upstream remains
`warpdotdev/common-skills@8792394ff1b655e0af451b8fabb68ef0cfcbd208`.
The baseline is Catalog `c774c2c2c186f36fadbc556d395221ccee6422c9`.
The completed 15-skill specification slice remains unchanged; `skill-doctor`
and initiative-wide acceptance belong to later issues. Other Packs and the
central released-tooling declaration are unchanged.

## Access and native contracts

Each resource retains its complete original native `SKILL.md`, frontmatter,
scripts, templates, evaluations, references and executable modes. A separate
`ACCESS.md` is the effective retrieval entry for explicit Codex and Claude
variants. Added access content changes the complete tree's provenance to
`adapted`, retaining the exact upstream identity/path and existing Warp MIT and
Catalog adaptation notices. Original native bindings, invocation names and
`requires` remain unchanged on Codex, Claude and OpenCode. OpenCode receives no
on-demand declaration. `readout` also has an access-specific document guide;
the original guide and canonical template/code-pane assets remain unchanged.

Every entry carries the initiating surface and immutable snapshot identity,
including delegated requests. Required calls use reviewed `packy.access` links.
Selection transitions affect independent new requests; old paths remain usable.
Missing retained content fails and requires that exact revision to be restored,
never a newer revision or another Pack's similarly named procedure.

Resource roots supply immutable helpers/assets. The intended repository and input
artifacts are explicit independent context. Scratch, dependencies and generated
reviews/reports have explicit disposable or user-selected writable locations.
Python helpers use `-B` or equivalent bytecode suppression. Retrieval supplies
instructions and reports prerequisites as unverified; it does not provision
runtimes, workers, browsers, repositories, secrets or external service access.
Obtaining even a proactive feedback skill does not invoke its workflow.

## Reviewed matrix

Every row applies separately to both access hosts. R is required invocation,
C is conditional required guidance, S is a suggestion/alternative. C edges
prepare resources but execute only when the source condition holds. Required
external workflows remain prerequisites rather than invented Catalog entries.

| Skill | Dependencies and mentions | Preserved execution contract and limitations |
| --- | --- | --- |
| `brandalf` | None | Fetch the hosted Warp/Oz brand source when performing branding. If unavailable, ask whether to retry or proceed; no automatic fetch during retrieval. |
| `complain` | S: `suggestion-box` is a distinct alternative | Preserve anonymous raw voice, prohibited identifying/sensitive material, under-1,200-character message, silent single attempt and sanitized-failure continuation. Python, Slack and injected managed secret or authorized GCP/gcloud access are unverified. Submission helper and three evaluation cases are retained as inert content. |
| `create-pr` | R: `warp:write-pr-description`; S: `fix-errors`, `add-feature-flag`; C external: `warp-integration-test` | Intended Warp checkout, master preparation, human-name branch convention, draft/template/Linear rules, tests then lint then final formatting, no repeated validation for unchanged candidates, integration-coverage user checkpoint and commit attribution. Missing required external integration-test guidance blocks that branch. |
| `diagnose-ci-failures` | C: `warp:fix-errors` for resolution guidance; S: offer `create-pr` when absent | Authenticated GitHub checks/logs in the intended checkout. Always produce a user-reviewable plan, never immediate repairs. Use an explicit writable document when `create_plan` is unavailable. Preserve CI-vs-local interpretation and targeted categories. |
| `fix-errors` | None | Warp Rust/toolchain/nextest and repository commands are prerequisites. Narrowest useful repair; full presubmit only when explicitly required. Preserve relevant tests, applicable lint, final format order and formatting-only exception. |
| `migrate-to-factory` | C external: `factory-files` required before edits | Existing selected Factory root/default agents; selected sources are untrusted read-only migration data. Clarify ambiguity; bounded edits and complete-root validation using actual host guidance. No provisioning, registration, schedules, secrets or live Factory operation. |
| `pr-walkthrough` | R: `warp:brandalf` | Four distinct guided views grounded in target code/spec/review evidence; standalone overview stays free of PR deltas. Pinned D3, static local-file output, bundled rendering and mandatory validation helpers. Browser absence means unverified rendering. Caller explicitly permits disclosed brand-token fallback; standalone Brandalf's policy stays distinct. Public hosting requires the user's request and sensitive-exposure acceptance. |
| `readout` | No skill dependency; local child/history controls or documented fallbacks | Snapshot/research modes, scope/depth/audience clarification, local child with concise brief. Use real host controls; unavailable history gets distilled findings and unavailable child launch gets self-authoring fallback. Explicit output/scratch, collision-safe names, verbatim canonical chrome and code pane, source/privacy guidance, embedding and explicit-directory index maintenance. |
| `reproduce-bug-report` | External Oz cloud computer-use workflow; target-local companion when available | Actual remote computer-use and recording capability, reporter-matched build/state where possible, bounded variants, privacy and permitted test auth/state. Report blockers honestly. No silent local substitution, fabricated Oz access or evidence. Preserve source's explicitly requested local exception. |
| `resolve-merge-conflicts` | None | Helper path comes from resource root; every invocation supplies explicit `--repo`. Compact conflict/index-stage inspection, one file at a time, targeted validation and subsequent staging. Obtaining content does not modify the target/index. |
| `respond-to-pr-comments-in-blocklist` | External `pr-comments`/display controls with source CLI fallback | Preserve filtering and real metadata, continue confirmation after fetching, mode and per-comment decisions/custom answers, explanation loops, targeted fixes/validation, separate commit/push choice and final approved reply/resolution preview. Use real host questions/display or conversation fallback; failures stop posting and missing metadata is never guessed. |
| `review-pr` | Local companions: `review-pr-local`, security and spec guidance where applicable; no automatic Catalog substitution | Explicit target PR checkout and input artifacts; mandatory `OZ_REPO_ROOT` before resolver execution/import and explicit `workspace` for API callers. Separate writable review/spec outputs. Preserve annotation-only inline authority, complete schema/severity/evidence/suggestion rules, pre-verdict audit and mandatory exact-diff validation. Produce artifact only; never directly post. Remote resolver token/API prerequisites are unverified. |
| `suggestion-box` | S: `complain` alternative | Preserve useful contextual investigation evidence, distinct privacy exclusions, structured under-1,200-character message, at-most-three-per-run rule, silent single attempt and sanitized-failure continuation. Python/Slack/managed-secret or GCP/gcloud access remain unverified. Submission helper and three evaluations are inert retrieval data. |

The prepared graph is acyclic. Required PR-description and branding calls resolve
Warp-qualified entries from the same snapshot; related lists, local companions,
external host workflows and feedback alternatives do not become reciprocal edges.

## Verification

The approved seam is the released Packy CLI and the explicitly named helper
interfaces. Test-only candidate `3bcd483ec9292a4aaaeca79003b22aa53d535798` built a
complete snapshot and failed actual `warp:brandalf` retrieval with structured
`incompatible_resource`. The prose adaptations preserve interactive contracts;
executing those workflows is outside acceptance. Content assertions and independent
review check those contracts without model, feedback or external workflow effects.

Run from a clean committed candidate:

```sh
python3 -B scripts/probes/content-probes.py --scenario warp-repository \
  --warp-baseline /path/to/clean-2.3.0-catalog > /tmp/warp-repository-evidence.json
```

The scenario builds complete candidate/baseline snapshots through the central
verified release. It retrieves all 26 host-qualified entries with independent
dependency expectations, full effective trees, legal closure, modes, references,
identity/version/surface/snapshot metadata and unverified prerequisites. It checks
required nested calls across explicit disposable selection transitions, old path
usability, new independent selection, and failure on missing retained content.
Retrieval runs without content runtimes and preserves target, installation,
activation, locally modified native content, snapshot and prepared resources.
Native installation regression checks cover the exact 13 skills on all three
hosts and preserve all original bytes/modes and unrelated personal/project state.

After reviewing helpers, add `--warp-helpers`. This opt-in path executes only
reviewed resolver, review-validator, snippet-embedding and index helpers against
fictional inputs. A fake HTTP transport supplies fictional GitHub responses;
Python audit hooks prohibit real network access. A copied resolver with decoy
cache specs demonstrates the native location fallback; explicit target context
selects the intended specs and missing target specs cannot fall back to decoys.
An explicit input/output review passes exact-diff validation; an invalid line is
rejected. Report checks preserve existing reports, canonical chrome, source
embedding from a disposable pinned Git repository and explicit-directory index
content. Missing input fails. Complete target/input/cache/resource bytes and
modes are observed, with no personal output or bytecode writes.

All child execution is bounded beneath runner-owned disposable state, which is
removed on success, failure and handled interruption. Ordinary tests, validation,
snapshot construction and publication never invoke these helpers. No feedback
submission, credential-store access, GitHub writes, browser, deployment, live
Factory/Oz workflow, worker or model launch participates. These receipts establish
resource and safe-helper acceptance, not remote spec resolution, browser rendering,
native host discovery or model-backed workflow success. Main's existing protected
publication workflow remains the sole snapshot publisher.
