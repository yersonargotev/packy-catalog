# Matty alongside an active pstack workflow

This is a historical research record. Its surface support, commands, engine
versions and conclusions describe the generation investigated and are not
current operator guidance. See [current catalog use](../../README.md#use-the-catalog)
and [Packy CLI setup](../packy-cli.md).

Reviewed on 2026-10-23 against this Catalog Project. The scope is the checked-in
Matty 4.0.0 and pstack 4.5.0 sources, with Codex as the main host. This is a
static instruction review, not a claim that the combined workflows have passed
model-backed runtime tests. Versions, bindings, and resource selections come
from the [Matty manifest](../../packs/matty/pack.json) and
[pstack manifest](../../packs/pstack/pack.json).

This is non-normative, installation-specific evidence. Its small installed
selection does not narrow the approved on-demand scope of all 117 Matty, pstack,
and Warp skills on Codex and Claude Code. Resource availability is not runtime
readiness or semantic workflow success. This delivery does not change the live
installed selections. See the [accepted design](../design/on-demand-skills.md).

Current support follows [ADR 0003](../adr/0003-limit-pstack-host-support.md):
pstack OpenCode was subsequently withdrawn while Matty/Warp retain native
installation support. The dated observations below preserve their original
baseline and do not override that policy. Current coverage is in the
[integrated inventory](../on-demand-coverage.md).

## Recommendation

Keep pstack in charge of implementation, verification, delegation, prototypes,
PRs, and autonomous execution. Add a small Matty selection for capabilities
that have a distinct job:

- `codebase-design`
- `domain-modeling`
- `writing-for-agents`
- `wizard`
- `handoff`
- `to-questionnaire`

These six are the lowest-overlap selection identified by this review. Their
individual limits and sources appear in the table below. They are a
recommendation inferred from the instructions, not a machine-enforced
compatibility profile. `handoff` and `to-questionnaire` remain explicitly invoked.
`wizard` is for steps the agent cannot perform itself.

Matty `research` is optional rather than a missing pstack capability. pstack's
[Investigation playbook](../../packs/pstack/skills/codex/poteto-mode/playbooks/investigation.md)
already produces cited explanations and recommendations through `how` and,
for motivation questions, `why`. Matty adds a specific delivery contract:
delegate primary-source research to a background agent and retain a cited
Markdown file in the repository. Keep it when that repeatable output is useful;
a minimal pstack-led selection can omit it.

For a broader installation, add `code-review` and `retro` as supplementary
review tools, and the three `writing-*` article skills for deliberately
interactive writing sessions. Keep their roles narrow. Do not replace a
required pstack review, evidence gate, or execution playbook with one of them.

## Installation and activation are separate questions

The manifests expose 33 Matty skills and 55 pstack skills. Their shared native
skill names are **`tdd` and `teach`**. Both packs declare their skill projections
as exclusive. Installing both complete selections with their original names
therefore creates concrete ownership collisions, independently of whether a
workflow is currently running. The remaining 31 Matty skill names do not collide
with pstack's names. This count does not establish behavioral compatibility.
See the [Matty manifest](../../packs/matty/pack.json) and
[pstack manifest](../../packs/pstack/pack.json).

Codex activation policies also matter. Matty ships `agents/openai.yaml` beside
all 33 skills. Eleven have no `allow_implicit_invocation: false` policy:
`code-review`, `codebase-design`, `diagnosing-bugs`, `domain-modeling`, `grilling`,
`pr`, `prototype`, `research`, `tdd`, `wizard`, and `writing-for-agents`.
The other 22 carry the explicit-only policy. Compare
[Matty grilling metadata](../../packs/matty/skills/productivity/grilling/agents/openai.yaml),
[Matty implement metadata](../../packs/matty/skills/engineering/implement/agents/openai.yaml),
and [Matty research metadata](../../packs/matty/skills/engineering/research/agents/openai.yaml).

pstack's Codex skills use the explicit-only policy except `setup-pstack`.
An explicitly requested pstack workflow can still read its sibling skills as
dependencies. Its execution contract states this distinction directly.
See [pstack TDD](../../packs/pstack/skills/codex/tdd/SKILL.md),
[its activation policy](../../packs/pstack/skills/codex/tdd/agents/openai.yaml),
[setup instructions](../../packs/pstack/skills/codex/setup-pstack/SKILL.md),
and [poteto-mode](../../packs/pstack/skills/codex/poteto-mode/SKILL.md).

Consequently, installing Matty's implicit-capable skills makes them candidates
for selection by their descriptions. Installing its manual skills does not
make all their bodies continuously active. Explicitly running a second workflow
can still introduce conflicting instructions.

## Full Matty assessment

The categories below describe coexistence while pstack owns execution. Every
row links the instruction source behind the assessment.

| Matty skill | Recommendation with pstack active | Reason or limit |
| --- | --- | --- |
| [`codebase-design`](../../packs/matty/skills/engineering/codebase-design/SKILL.md) | Core addition | Supplies deep-module vocabulary, interface design, and testability principles. Keep its local vocabulary convention from renaming pstack's named principles or existing project terminology. |
| [`domain-modeling`](../../packs/matty/skills/engineering/domain-modeling/SKILL.md) | Core addition | Sharpens domain terms and records glossary entries and consequential decisions. Complements pstack's focus on encoding domain structure in code. |
| [`research`](../../packs/matty/skills/engineering/research/SKILL.md) | Optional research delivery contract | Overlaps pstack Investigation, `how`, and `why`. Specifically delegates primary-source research to a background agent and saves a cited Markdown note in the repository. Requires an available, authorized background-agent capability. |
| [`writing-for-agents`](../../packs/matty/skills/productivity/writing-for-agents/SKILL.md) | Core addition | Provides document structure and context-pointer guidance. pstack itself calls for a host skill-authoring guide on agent-facing prose. |
| [`wizard`](../../packs/matty/skills/engineering/wizard/SKILL.md) | Core addition | Produces a script for genuinely human-only steps. Scope confirmation belongs to that manual procedure, not ordinary agent-executable work. |
| [`handoff`](../../packs/matty/skills/productivity/handoff/SKILL.md) | Core addition, manual | Writes a portable summary to the OS temporary directory. Useful across sessions or tools without replacing pstack's pause/pickup procedure for active execution. |
| [`to-questionnaire`](../../packs/matty/skills/productivity/to-questionnaire/SKILL.md) | Core addition, manual | Produces a questionnaire for information held by another person. Run it when that document is the requested deliverable. |
| [`code-review`](../../packs/matty/skills/engineering/code-review/SKILL.md) | Optional supplement | Adds separate Standards and Spec reviewers. Needs a valid diff base and tracker/spec context. Does not satisfy pstack's distinct adversarial, multi-model, or swarm gates by itself. |
| [`retro`](../../packs/matty/skills/engineering/retro/SKILL.md) | Optional supplement, manual | Suggests environment improvements. Overlaps pstack `reflect`; choose one retrospective driver and retain pstack's approval gate for edits to its skills. Needs `writing-for-agents`. |
| [`writing-fragments`](../../packs/matty/skills/in-progress/writing-fragments/SKILL.md) | Optional writing session, manual | Captures unstructured article material. It intentionally interviews the author, so use it outside an unattended implementation run. |
| [`writing-beats`](../../packs/matty/skills/in-progress/writing-beats/SKILL.md) | Optional writing session, manual | Assembles an article one user-selected beat at a time. It overlaps `writing-shape`; pick one shaping driver for an article. |
| [`writing-shape`](../../packs/matty/skills/in-progress/writing-shape/SKILL.md) | Optional writing session, manual | Shapes raw material paragraph by paragraph with the author. Use it for the article session rather than as the default for pstack's technical documentation. |
| [`wait-what`](../../packs/matty/skills/productivity/wait-what/SKILL.md) | Optional, manual | Re-explains the last message. Its body explicitly requests Simplified Technical English; account for that when the conversation normally uses Spanish. |
| [`setup-matt-pocock-skills`](../../packs/matty/skills/engineering/setup-matt-pocock-skills/SKILL.md) | Optional one-time setup, manual | Configures tracker and domain-doc pointers for Matty workflows. It does not install a global Matty execution mode. Review its concrete instruction-file edits when adopting these conventions. |
| [`setup-ts-deep-modules`](../../packs/matty/skills/in-progress/setup-ts-deep-modules/SKILL.md) | Explicit project convention only | Installs dependency-cruiser and imposes a package layout and entry-point rules. No name collision, but it changes the architecture policy. Adopt it only if that policy is wanted. Needs `codebase-design`. |
| [`diagnosing-bugs`](../../packs/matty/skills/engineering/diagnosing-bugs/SKILL.md) | Choose one debugging driver | Its hard gate forbids hypotheses before a demonstrated tight red-capable loop. pstack permits practical fallback verification when a new regression test is impractical. This is a stricter alternative, not a passive extra. |
| [`prototype`](../../packs/matty/skills/engineering/prototype/SKILL.md) | Choose one prototype driver | Requires prototype code near the relevant module/page and capture on a separate prototype branch. pstack requires an isolated scratch directory outside production source. |
| [`pr`](../../packs/matty/skills/engineering/pr/SKILL.md) | Exclude from default selection | Prescribes `Summary`, `Evidence`, and `Merge Danger`. pstack prescribes a different ordered PR-body structure. Both can trigger for the same writing task. |
| [`grilling`](../../packs/matty/skills/productivity/grilling/SKILL.md) | Deliberate interview only | Waits for every round of user decisions and final shared-understanding confirmation. Conflicts with treating reversible execution as asynchronous under pstack. Its description can trigger implicitly. |
| [`grill-me`](../../packs/matty/skills/productivity/grill-me/SKILL.md) | Deliberate interview only, manual | Thin entry point to `grilling`. Install the primitive too if using this wrapper. |
| [`grill-with-docs`](../../packs/matty/skills/engineering/grill-with-docs/SKILL.md) | Deliberate interview only, manual | Combines `grilling` and `domain-modeling`. It is a user-driven design phase, not an autonomous implementation driver. |
| [`improve-codebase-architecture`](../../packs/matty/skills/engineering/improve-codebase-architecture/SKILL.md) | Deliberate design review only, manual | Produces candidates, waits for a choice, and then starts grilling. Needs `codebase-design`, `grilling`, and `domain-modeling`. |
| [`to-spec`](../../packs/matty/skills/engineering/to-spec/SKILL.md) | Deliberate planning phase only, manual | Synthesizes a spec but requires user confirmation of test seams and publishes to the configured tracker. It adds a separate planning process. |
| [`to-tickets`](../../packs/matty/skills/engineering/to-tickets/SKILL.md) | Deliberate planning phase only, manual | Requires approval of ticket granularity and blocking edges before publication. Its expand-contract guidance also needs reconciliation with pstack's same-wave internal API migration policy. |
| [`triage`](../../packs/matty/skills/engineering/triage/SKILL.md) | Separate maintainer-led phase, manual | Owns label state transitions and pauses for maintainer direction. Can prepare issues for pstack, but should not concurrently drive pstack's execution or PR babysitting. Needs tracker/label conventions and, for interviews, `grilling` and `domain-modeling`. |
| [`wayfinder`](../../packs/matty/skills/engineering/wayfinder/SKILL.md) | Separate planning program, manual | Owns decision tickets and normally resolves only one per session. It produces planning decisions before implementation. Overlaps pstack's larger-program coordination. |
| [`loop-me`](../../packs/matty/skills/in-progress/loop-me/SKILL.md) | Separate workflow-design session, manual | Runs a stateful grilling session whose output is workflow specs. Its session and `NOTES.md` ownership should remain separate from a pstack build. Needs `grilling`. |
| [`ask-matt`](../../packs/matty/skills/engineering/ask-matt/SKILL.md) | Exclude as primary router | Routes work into the whole Matty idea-to-ship lifecycle, including its implementation drivers. A partial Matty installation makes many of its routes unavailable. |
| [`implement`](../../packs/matty/skills/engineering/implement/SKILL.md) | Exclude as concurrent driver | Owns implementation, calls `tdd` and `code-review`, and commits to the current branch. Competes with pstack's playbook and worktree ownership. |
| [`implement-spec`](../../packs/matty/skills/engineering/implement-spec/SKILL.md) | Exclude as concurrent driver | Owns task-graph orchestration, integration-branch merges, draft PR creation, and closeout. pstack's PR policy explicitly opens ready PRs. Its unqualified `tdd` lookup can reach the wrong pack if Matty TDD is omitted. |
| [`claude-handoff`](../../packs/matty/skills/in-progress/claude-handoff/SKILL.md) | Exclude from a Codex default | Launches `claude --bg` in the current working directory. This is an explicit handoff to another tool, not Codex-native continuation, and can create a second execution owner. |
| [`tdd`](../../packs/matty/skills/engineering/tdd/SKILL.md) | Keep pstack's version | Exact name collision. Matty requires confirmed test seams and prescribes a broad feature-building loop; pstack's workflow is focused on cheap, practical bug regression checks. |
| [`teach`](../../packs/matty/skills/productivity/teach/SKILL.md) | Keep pstack's version for this installation | Exact name collision. Matty is a stateful multi-session teaching workspace. Use it in a deliberately separate teaching installation if needed. |

## Concrete conflicts behind the exclusions

**Two different PR templates.** Matty `pr` prescribes three sections. pstack's
[Opening a PR playbook](../../packs/pstack/skills/codex/poteto-mode/playbooks/opening-a-pr.md)
prescribes `Why`, `What changed`, mandatory `Scope`, optional `Tradeoffs`,
`Blast Radius`, and `Verification` in that order. Combining the full templates
would violate at least one. pstack also requires PRs to open ready, whereas
Matty `implement-spec` opens a draft after the first integration merge.

**Different prototype locations.** Matty `prototype` puts throwaway code near
its eventual module or page and preserves it on a prototype branch. pstack's
[Prototype playbook](../../packs/pstack/skills/codex/poteto-mode/playbooks/prototype.md)
puts the experiment in an isolated scratch directory, separate from production
source. Both are reasonable policies, but one must own the run.

**Different stopping rules.** Matty `grilling` waits for the user at each frontier
and before action. Matty TDD requires user-confirmed seams before tests.
pstack's [Never Block on the Human principle](../../packs/pstack/skills/codex/principle-never-block-on-the-human/SKILL.md)
asks the agent to proceed with reversible execution. Explicitly requesting an
interactive design session can choose the Matty behavior; installing that
workflow does not make it an appropriate default inside an unattended run.

**Different regression-test thresholds.** Matty `diagnosing-bugs` requires an
already-run, red-capable reproduction before hypotheses. pstack
[TDD](../../packs/pstack/skills/codex/tdd/SKILL.md) allows practical fallback
verification and explicitly prefers no new test over an impractical one.
The choice affects whether the agent keeps moving when a reproducer is costly.

**Different migration defaults.** Matty `to-tickets` permits expand-contract
sequences with intermediate compatibility states for wide refactors. pstack's
[internal API migration principle](../../packs/pstack/skills/codex/principle-migrate-callers-then-delete-legacy-apis/SKILL.md)
applies when there are no external compatibility users and asks for migration
and deletion in the same wave. Resolve this against the project's actual
compatibility contract before using Matty's planner for a pstack migration.

## Partial installations need explicit dependency discipline

Matty's manifest declares no `requires` edges for its skills, even where bodies
call other skills. A custom selection must account for those calls manually.
For example, `grill-with-docs` calls `grilling` and `domain-modeling`, `retro`
calls `writing-for-agents`, and `implement-spec` calls `tdd` and `code-review`.
See the [manifest](../../packs/matty/pack.json) and the linked skill bodies above.

This matters especially for `tdd`: omitting Matty's colliding version and
keeping `implement-spec` would leave its unqualified `tdd` call pointing at a
workflow with different semantics. Renaming a skill alone also does not rewrite
such references. The recommended six-skill selection avoids the Matty
implementation chain entirely.

## This project's existing installation needs a separate migration decision

[packy.json](../../packy.json) currently selects all Matty 4.0.0 for Codex and
does not select pstack. The [README](../../README.md) explicitly says Argote's
Issue Delivery requires Matty's `tdd` and `code-review` at runtime. Its
[bootstrap](../../packs/argote/skills/productivity/issue-delivery/SKILL.md) and
[implementation instructions](../../packs/argote/skills/productivity/issue-delivery/references/implement.md)
also depend on them. Do not remove Matty TDD here and treat pstack TDD as an
equivalent replacement without resolving that existing workflow contract.
An alternative is a custom pstack selection that omits its `tdd` and `teach`;
`poteto-mode`'s declared closure does not require those two resources.
This follows the [pstack manifest](../../packs/pstack/pack.json).

A read-only `packy install pstack --surface codex --dry-run --json` preview
returned `foreign_target` and `projection_collision` at `.agents/skills/tdd`
and `.agents/skills/teach`. Its acquired catalog contained pstack 4.1.0, so this
corroborates the existing installation's name collisions. It does not test the
current 4.5.0 combination. Static review used the checked-in 4.5.0 manifest and
skill bodies. All note links were checked locally. No combined native runtime
execution was performed.

This review changes no pack manifests, installed selections, or activation
policies. Revisit it after either pack changes its instructions or contracts.
