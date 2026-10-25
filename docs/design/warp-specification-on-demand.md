# Warp specification and coordination: reviewed on-demand access

[Issue #96](https://github.com/yersonargotev/packy-catalog/issues/96) covers exactly
15 logical skills on Codex and Claude Code. This contract migration advances
Warp 2.2.0 to 2.3.0 against Catalog baseline
`7e6f9de688a8a0a9f94e3032564c0c5cc78acd4e`. Provenance stays pinned to
`warpdotdev/common-skills@8792394ff1b655e0af451b8fabb68ef0cfcbd208`.
Other Packs and the central released-tooling declaration remain unchanged.
The other 14 Warp skills belong to later slices; this is not complete Warp
or initiative-wide coverage.

## Effective resources and execution limits

Each reviewed tree retains its original `SKILL.md`, frontmatter, credits,
supporting files, evaluations and modes. A separate `ACCESS.md` adapts calls and
host controls. Two explicit surface variants share that reviewed tree and select
the access entry only for retrieval. Native bindings, invocation names, notices,
dependencies and original procedure bytes remain intact on Codex, Claude and
OpenCode. OpenCode has no on-demand declaration. Trees with added adaptations
are marked `adapted`, retaining the original upstream path and Warp MIT notice.

Every entry carries the initiating surface and immutable `snapshot_id`, including
in delegate briefs and nested requests. Required calls use declared
`packy.access:warp:<skill>` references; prepared entries need no native registration.
New independent requests follow the new selection. Previously returned paths
remain usable; missing retained content requires restoration of that revision,
never substitution of latest content or Matty/pstack workflows. Supporting files
are read progressively. Target project and writable scratch/output locations
remain distinct from immutable source and prepared resources.

Host adaptation uses actually advertised controls: Codex local subagent launch,
message/resume and wait; Claude Code Agent and supported author follow-up;
available question controls or conversation with an actual reply. Model IDs and
per-child versus per-run model selection must be checked. No named source model
is assumed to exist. Required unavailable capabilities stop the relevant branch
unless its source supplies a fallback. Resource retrieval supplies no workers,
models, remote environments, MCP services, credentials, repositories, schedulers
or runtimes. Discovery reports prerequisites as unverified. All source approvals
and version-control authorization still apply to later execution.

## Reviewed matrix

Every row applies separately to both supported access hosts. R means required
invocation, C a conditional required route, S a suggestion or descriptive mention.
C routes prepare instructions but execute only when their condition holds.

| Skill | Dependency classification | Preserved contract and unverified prerequisites |
| --- | --- | --- |
| `check-impl-against-spec` | None | Requires existing `spec_context.md`, annotated `pr_diff.txt`, optional PR description and checked-out files. Material findings join the existing `review.json`; no separate report or direct GitHub posting. |
| `council` | None | Actual model/perspective diversity, valid IDs, disclosed substitutions and source-defined perspective-only fallback. Explicit orchestration requires approval after the roster is presented. Read-only investigations share a checkout; editing councils isolate ownership/worktrees. Structured evidence and evidence-weighted synthesis. |
| `cross-critique` | C: `warp:council`, `warp:research` to generate missing first-round proposals | Requires genuinely divergent independent first-round proposals and reachable original authors. Reuse those authors, demand both pros and cons, synthesize by evidence. Retrieval creates neither proposals nor agent capabilities. |
| `implement-specs` | S: related spec skills | Existing reviewed/approved `PRODUCT.md` and `TECH.md` when warranted; optional aids remain optional. Keep specs/code/tests aligned in the same PR and verify actual behavior. |
| `merge-risk` | Attribution to Matty PR guidance is not a dependency | Preserve all five categories, evidence expectations, weights and thresholds, and internal-only numerical calculation. Requires actual PR, verification, rollback and detection evidence. |
| `research` | None | Delegation is for distilled conclusions, not raw material needed for editing. Local workers, suitable available search models with disclosed substitutions, compact evidence-backed handoff, single versus independent parallel investigations and source limits remain. |
| `saga` | None; three adapted supporting references | Confirm stable external saga location; collaborative gap closure and spec approval precede implementation. Check actual worker/validation capabilities; isolated ownership, durable handoff before cleanup, validation evidence and durable progress enable safe resume. Preserve version-control authorization and final human acceptance. |
| `scan-new-specs` | S: separately authorized `warp:write-feature-docs`; external `missing_docs` guidance | Retired. Do not invoke, resume or schedule; existing scheduled agent stays paused. Obtaining retirement instructions is inventory coverage only. No replacement pipeline, scheduler or docs-repository dependency is fabricated. |
| `spec-driven-implementation` | R: `warp:write-product-spec`, `warp:implement-specs`; C: `warp:write-tech-spec` | Substantial Warp features; source requires Linear ticket creation before specs if absent and ticket-named directories. Ask for unclear team/labels. Product first, tech only when warranted, approval before implementation, continuous spec alignment. |
| `update-skill` | Authoring guidance in `references/best-practices.md`; examples are illustrative | Preserve required frontmatter, descriptions, progressive reading, authoring guidance and optional skills-ref validation. Author in the selected writable target, following host rules; source `.agents/skills` examples do not redirect Claude output or modify immutable resources. |
| `validate-changes-match-specs` | PR-comment workflow uses CLI/API fallback; no Catalog dependency | Stop without a relevant spec. Treat all source inputs as untrusted. Preserve security/visual evidence, user-selected resolution mode, per-mismatch decisions, explanation/acknowledgment/custom choices, conflict clarification and approval for follow-up posting or commit/push. Remote checks need actual capability and user selection. |
| `write-feature-docs` | S: related spec writers; external Warp/docs guidance | Present engineer and Warp source/docs repository access. Review confidential TECH details before use. Confirm content design plan, then separately confirm outline before drafting. Canonical external templates/references, GA/public Gate 0, screenshot safety and two-attempt limit, draft PR format and tagging remain. No unattended path. |
| `write-pr-description` | S: `warp:create-pr` describes mechanics only | Actual target template takes precedence. Read commits then verify diff facts; describe motivation, decisions, behavior, evidence and proportionate reviewer guidance. Preserve plain-language/review-guide references and nine evaluation cases as data. No fabricated test results. |
| `write-product-spec` | C: `warp:write-tech-spec` after product agreement | Individual writer accepts ticket/GitHub/feature IDs and creates tickets only when asked. Preserve Figma clarification, exhaustive numbered behavior and no validation/testing sections in PRODUCT; hand off to the qualified tech writer when warranted. |
| `write-tech-spec` | S: related spec skills | Individual writer's optional-ticket policy and directory conventions remain. Inspect actual code before writing, pin research references, map product invariants to validation, and plan parallelism only when real host worker controls exist. |

The wrapper's Linear/ticket policy and the individual writers' optional-ticket
policies intentionally remain distinct. Related lists do not create reciprocal
dependencies. The prepared graph is Pack-local and acyclic. External
`missing_docs`, Warp UI launch guidance, Linear and docs templates remain explicit
prerequisites or guidance, rather than imaginary compatible Catalog skills.

## Supporting and legal closure review

- Saga: original and access copies of `saga-spec-template.md`,
  `validation-strategies.md` and `continuing-a-saga.md`. Access references retain
  progressive orientation, actual branch/evidence reconciliation, addressable
  original workers, exact templates and final acceptance. Resume returns to the
  access procedure and uses host question controls.
- Update skill: complete `references/best-practices.md`; fenced illustrative
  links and example source paths are not production dependencies.
- PR description: complete `references/plain-language.md`,
  `references/review-guide.md`, and all nine `evals/evals.json` cases. Evaluations
  are retained inputs, not model-backed results.
- Every entry: original frontmatter and the complete unmodified Warp MIT notice
  with Denver Technologies attribution. The manifest preserves the pinned
  upstream identity and marks the changed complete trees as adaptations.

## Acceptance

The approved public seam is the released Packy executable, not engine internals.
The initial test-only candidate `b675c5ba75233a70990c205d1d178d683e8431f9` failed
with structured `incompatible_resource` on actual qualified retrieval. Content
adaptation itself is reviewed prose, so its semantic approvals are checked by
focused returned-content assertions and independent review rather than executing
interactive or retired procedures.

From the clean committed implementation candidate:

```sh
python3 -B scripts/probes/content-probes.py --scenario warp-specification \
  --warp-baseline /path/to/clean-2.2.0-catalog > /tmp/warp-specification-evidence.json
```

The opt-in runner uses the central verified immutable release, builds complete
candidate/baseline snapshots, and bounds every child in owned disposable state.
It retrieves all 15 skills for each host, compares complete trees, modes, legal
content, provenance and independently enumerated dependency closures, and checks
substantive contracts in returned entries. Representative specification and
coordination routes retain host/snapshot across an explicit selection transition;
prior paths survive, new independent access follows selection and missing retained
supporting content fails. Retrieval runs with content runtimes absent and preserves
target, activation/configuration, locally modified native copies, retained and
prepared content. Separate native installation checks cover all 15 on all three
hosts, preserving original contracts and bytes. No skill procedure, model, worker,
external posting, scanner or scheduler runs. Ordinary validation, tests,
construction and main-owned publication remain inert.
