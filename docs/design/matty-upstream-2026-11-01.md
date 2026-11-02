# Matty 5.0.0 upstream migration

[Issue #134](https://github.com/yersonargotev/packy-catalog/issues/134) records the
maintainer-approved scope and acceptance criteria.

Matty moves from 4.4.0 to 5.0.0 and pins
[`mattpocock/skills@4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`](https://github.com/mattpocock/skills/commit/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d),
previously `a496f5513d4a4cf889bc48e189e579f4b0bdf6aa`.
This is a contract migration: a new resource and adapted procedure dependencies
fall outside the README's closed upstream-refresh allowance.

## Reviewed changes

`software-factory` adds experimental, explicitly invoked design vocabulary,
example tasks, and surveys of ticket trackers, git hosts, runners, and
observability platforms. All six upstream files retain their bytes and modes;
the original entry is retained as `upstream-SKILL.md`. Upstream's description
contains an unquoted colon, which the released plugin exporter rejects as invalid
YAML. The distributed `SKILL.md` and `ACCESS.md` quote that description without
changing its value or the procedure. The source-fidelity probe checks this exact
one-line adaptation as well as the retained original.
Catalog-authored `agents/openai.yaml` preserves explicit invocation on Codex
with `allow_implicit_invocation: false`. The on-demand entry reads the corrected
procedure and preserves its relative
references. Surveys identify their October 2026 research date and require fresh
primary-source research before product selection. Retrieval and design do not
provision services or authorize automated runs. Agents and Claude native use and
on-demand access are available; Claude plugin export includes all supporting
files. Agent Plugins export remains undeclared because of user-only frontmatter.
Matty now contains 35 skills; frozen `skills/misc` resources remain excluded.

`chief-of-staff` first looks for an existing shared wiki and follows its
conventions. A new wiki still requires an agreed location. It runs retrospectives
on roughly one in five delegated sessions, prioritizes failures, and pursues
selected retrospective improvements itself. Large work follows the existing
specification, ticket decomposition, and implementation procedures.

The original native procedure stays byte-exact. Native installation retains its
existing sibling-skill convention. The inline on-demand procedure replaces the
four sibling paths with qualified links to `matty:retro`, `matty:to-spec`,
`matty:to-tickets`, and `matty:implement-spec`. Their transitive closure adds
`code-review`, `tdd`, `codebase-design`, and `writing-for-agents`. All nine entries retain the
initiating surface, snapshot, project, writable output, and delegated context.
Preparation does not execute conditional procedures or replace their user
decisions, test-seam confirmation, and runtime prerequisites.

The new sibling procedure calls invalidate chief-of-staff's previous standalone
Claude plugin review: the referenced skills have no reviewed plugin export
closure. Its export declaration is removed, and explicit export must fail
without output on both surfaces. This compatibility change warrants 5.0.0.
Native and on-demand access remain available. MIT notices, native bindings,
native dependency semantics, and all unrelated Matty resources are preserved.

## pstack comparison

The complete `pstack` tree at reviewed catalog origin
`cursor/plugins@1ba91fc25c0977741dd0e267849e6234b037ed0a` and repository HEAD
[`ae5650febf4320793844c12c4adaa937f417f8da`](https://github.com/cursor/plugins/commit/ae5650febf4320793844c12c4adaa937f417f8da)
has the same Git tree ID, `4719e1c4b4c43bac85d4206a8b41dd2899769c1c`.
There are no upstream pstack changes to incorporate. Its version stays 6.1.0;
its origin pin, originals, adaptations, statechart inventory, and legal closure
stay unchanged. Every other Pack also retains its version and content.

## Verification

Run tooling tests and complete catalog validation against the clean pre-change
checkout, including independent Pack version checks:

```sh
./scripts/test.sh
./scripts/validate.sh /path/to/clean-baseline --json
```

From a clean committed candidate, with a clean checkout of the pinned Matty
origin, run:

```sh
python3 -B scripts/probes/matty-update.py --upstream /path/to/mattpocock-skills
```

The probe checks all original bytes/modes, 35 native and on-demand trees on both
surfaces, complete notices, chief-of-staff's retained nine-skill closure,
software-factory's complete Claude export, rejected unsupported plugin
selections, and uninstall cleanup with unchanged ambient and authored state.
It neither executes workflows nor establishes client loading or model-backed
success. Commit, push, snapshot publication, and installed-skill updates remain
separate operations.
