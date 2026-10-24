# Matty delivery and writing: reviewed on-demand access

This is the exact 14-skill slice in [issue #92](https://github.com/yersonargotev/packy-catalog/issues/92).
Together with [the 19 design/planning skills](matty-design-on-demand.md), it
accounts for all 33 Matty skills on Codex and Claude Code. Matty advances from
4.1.0 to 4.2.0. Upstream remains
`mattpocock/skills@d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.
This is a Catalog contract migration, not an upstream refresh.

## Access and execution

Each added `ACCESS.md` preserves source frontmatter, including user-only
invocation and credits. Calling procedures have reviewed qualified
`packy.access` references; procedures without installation-dependent calls read
their unchanged `SKILL.md`. The router and handoff qualify recommendations without
making them mandatory graph edges. Every nested request, delegated agent and
handoff retains the initiating explicit host, immutable snapshot, target
repository, returned entry/resource locations and writable scratch/output.
Missing retained content requires restoring that revision. Another Pack or a
modified native copy cannot substitute for the selected Catalog Resource.

Required dependencies prepare resource availability, including conditional
branches; they do not authorize execution. Matty TDD requires confirmed public
test seams, vertical red/green slices and review-stage refactoring. Its policy,
Matty's PR template, prototype, diagnosis and execution procedures remain distinct
from pstack's. The bootstrap follows the user's chosen workflow.

All original procedures, supporting references, templates, scripts, assets,
metadata and modes remain unchanged. `ask-matt` has a separate qualified phase
reference; its original decision tree remains intact. Changed resource trees are
adaptations with the existing upstream provenance, MIT notice and Catalog
adaptation notice. The prior 19 adaptations and all other Packs remain unchanged.
Native installation on Codex, Claude and OpenCode retains its existing bindings,
dependency semantics and original source content; OpenCode gains no on-demand
contract. No live selection is migrated.

## Reviewed matrix

Both hosts use these entries. Discovery reports known prerequisites as
unverified; later execution must check them. R = required invocation; C =
conditional invocation; S = recommendation or descriptive route with no automatic
invocation. Every relative supporting resource stays within the returned tree.

| Skill | Qualified references and graph | Supporting content | Preserved workflow and execution prerequisites |
| --- | --- | --- | --- |
| `ask-matt` | S: all Matty routes named in the source; no required edges | Original `PHASE-BOUNDARIES.md` and qualified `ACCESS-PHASE-BOUNDARIES.md` | Main flow, on-ramps, standalone/vocabulary map, session/context hygiene and ordered phase tree. User chooses a route; user-only skills remain user-only. Host context commands require actual host support. |
| `claude-handoff` | S: selected `matty:<skill>` suggestions, no required edges | Original source and metadata | Explicit user invocation; redacted prompt with artifact pointers; external `claude --bg --name` in the target directory and `claude agents` management. Requires that Claude CLI capability on either host; no Codex-native continuation or launch during retrieval. |
| `code-review` | S: `matty:setup-matt-pocock-skills` if tracker configuration is absent | Complete fixed-point, standards baseline and two-axis procedure | Valid nonempty fixed-base diff, configured tracker/spec discovery, two independent parallel background review agents, repository overrides baseline, separate Standards/Spec reports. |
| `diagnosing-bugs` | None | `scripts/hitl-loop.template.sh`, copied to writable scratch for a selected human-loop branch | Secret redaction; demonstrate a tight red-capable command before hypotheses; reproduce/minimize, rank hypotheses, instrument, regress at an appropriate seam and clean up. Runtime/human access depends on the bug. |
| `implement` | C: `matty:tdd` where possible; R: final `matty:code-review` | Reviewed complete implementation body; transitive TDD support | Pre-agreed seams, prescribed incremental checks and full suite, final review, commit on the current branch. Requires target Git/check commands and review-agent/tracker capabilities. |
| `implement-spec` | R: `matty:tdd` in implementers and final `matty:code-review`; S: setup when tracker is missing | Complete task-graph procedure and explicit delegation context | Configured tracker/spec/tickets, frontier, integration branch, isolated implementer worktrees, merger agents, draft PR after first merge, final review/repair, closeout and cleanup. Every delegate receives qualified entry pointers and the same host/snapshot. |
| `pr` | None | Original template, examples, metadata and `CREDITS.md` | Matty Summary/Evidence/Merge Danger, smallest appropriate visual, before/after proof and door/blast-radius judgment. Retains original credits; no pstack template merge. |
| `retro` | R: `matty:writing-for-agents` | Full retrospective body; authoring mechanics through dependency | Primary session evidence, environment recommendations ordered by severity, existing checks first, deterministic checks for mechanical mistakes, judgment standards for nonmechanical ones. Retrieval edits no environment or steering file. |
| `setup-ts-deep-modules` | R: `matty:codebase-design` | Original `dependency-cruiser.config.cjs` | User-only setup; detect package manager/root/config, merge existing config, install dependency-cruiser, preserve four boundary principles/no cycles, example package, observed pass/fail/pass and documentation/context pointer. Installs and project changes occur only in the selected procedure. |
| `tdd` | C: `matty:codebase-design` when interface shape is in question | Original `tests.md` and `mocking.md` | User-confirmed public seams before tests, behavioral assertions, one vertical red/green slice at a time, refactoring reserved for review. Target runtime/checks remain prerequisites. |
| `teach` | None | `MISSION-FORMAT.md`, `RESOURCES-FORMAT.md`, `LEARNING-RECORD-FORMAT.md`, `GLOSSARY-FORMAT.md` | Stateful target teaching workspace, mission confirmation, cited trusted sources, interactive learning/feedback and reusable assets; browser for lessons. Format inputs come from resources; outputs go to the user's workspace. |
| `writing-beats` | None | Complete original procedure | User-selected output, audience prerequisites/grounded concepts, user choice among candidates before every write, one beat at a time, re-read/preserve edits. |
| `writing-fragments` | None; its exploratory interview is in the procedure | Complete original procedure and fragment format | User-selected destination, explore without structure, capture initial material, append/re-read discipline and user edits. No implicit grilling dependency is added. |
| `writing-shape` | None; its shaping interview is in the procedure | Complete original procedure | Read full raw input, keep it read-only, separate article, grounded concepts, user-selected opening, agreed incremental blocks, re-read edits and user-controlled completion. |

## Acceptance

Run from a clean committed candidate with the clean complete 4.1.0 baseline:

```sh
python3 -B scripts/probes/content-probes.py --scenario matty-delivery \
  --matty-baseline /path/to/clean-4.1.0-catalog > /tmp/matty-delivery-evidence.json
```

This extends the existing isolated released-binary runner and central immutable
release declaration. It builds both complete snapshots and records exact commits,
identities/digests and bounded child receipts. Neither candidate is an official
publication; no fixture is published. Ordinary validation, tests and publication
remain inert.

Coverage includes all 66 roots, reviewed direct declarations and transitive
closure, full prepared source/supporting/legal bytes and modes, meaningful
relative targets and unverified known prerequisites with content runtimes absent.
Representative implementation, delegated TDD/review, retrospective and setup
references are followed on both hosts. Qualified Matty TDD is checked separately
with pstack TDD active and with a modified native TDD in isolated state, respecting
native name-conflict rules. No workflow is executed.

The controlled selection transition reuses the existing digest-bound mechanism:
nested retrievals keep the initiating snapshot while independent requests see the
baseline; prior prepared resources remain usable; missing retained content fails
explicitly. Target/native state, ambient HOME/config/data/cache and immutable
resources are observed. Native regression installs all 33 selected skills on
Codex, Claude and OpenCode and checks original bytes/modes/contracts against the
baseline. Runner-owned temporary state is removed on success or failure.

These checks prove resource access and preservation, not model-driven workflow
success, runtime readiness or unattended applicability. In particular, they
obtain Claude handoff instructions without launching Claude and setup templates
without changing a target project's configuration or dependencies.
