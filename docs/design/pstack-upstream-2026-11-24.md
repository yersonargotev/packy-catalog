# pstack 6.3.0 upstream update

pstack moves from 6.2.0 to 6.3.0 and pins
[`cursor/plugins@41e400932eca14f289e7db717a70455256b6d388`](https://github.com/cursor/plugins/tree/41e400932eca14f289e7db717a70455256b6d388/pstack),
upstream plugin version 0.15.48. The previous pin was
`1ba91fc25c0977741dd0e267849e6234b037ed0a` (0.15.36). This is a contract
migration. The update adds a skill and a file, removes upstream files, and
changes adaptations, so it falls outside the README's exact-copy
upstream-refresh allowance.

The reviewed range contains seven upstream pstack commits. They shorten skill
texts, add `worker.md`, route Cursor delegation through Opus first with an
`xhigh` cap, turn `how` and `why` into single files, add `/reframe`, and fix
statechart on native Windows and with TLC's `\r\n` line endings. The Claude
Code harness copies under `harness/pstack/claude-code` differ from the Cursor
originals only by their adapter preface line. The Catalog's Claude
adaptations therefore track the same content change. Upstream `docs/`,
`agents/`, `automations/` and plugin metadata are not in the Pack closure.

## Reviewed changes

- **New skill.** `reframe` teaches the expert vocabulary for what the operator
  is building and rewrites their description with it. Its hosts differ only in
  the execution preface. It therefore uses one host-neutral
  `skills/shared/reframe` tree for both surfaces, with explicit invocation on
  both hosts and no pstack dependencies. The original is retained byte-exact.
  The Pack now has 59 skills on each surface and 61 logical resources.
- **Collapsed skills.** `architect`, `how`, `why` and `reflect` are now
  single files. Their 21 upstream reference files are removed from the
  originals, together with every Agents and Claude counterpart and `ACCESS-`
  twin. `architect` now depends only on `arena`. `why` and `reflect` no
  longer delegate. Their on-demand prerequisites drop the subagent and
  model-preference requirements. `reflect` reads the transcript directly, and
  its catalog-only digest and backlog-filing steps have no upstream anchor left,
  so they are removed. The `why` and `reflect` descriptions follow upstream.
- **poteto-mode.** Triggers, Subagents, Writing the reply and Playbooks follow
  upstream's shorter text. The Comments section is removed. Upstream's new
  `worker.md` is added to both adaptations. Every delegated agent reads it
  first. The catalog copy adds one rule: host and user authorization still
  govern external actions. It has no skill references, so the on-demand entry
  reads it directly and `reference_files` lists it. Upstream deleted the
  Orchestrate playbook and `scripts/check-plan.mjs` with its test. Both are
  removed from the originals and both adaptations. The on-demand playbook
  index still links each `ACCESS-` playbook explicitly. The watcher package
  drops the removed test from its test script.
- **Playbooks.** Eighteen playbooks follow upstream. Multi-phase plan becomes a
  five-step outline with no checker. Babysit keeps the catalog's read-only
  `observe` mode and its explicit-repair rule. Shipping uses the new
  `--queued-stack` and `--stack-prs` watcher wording.
- **Principles and writing skills.** Fourteen principles, `blast-radius`,
  `sharpen`, `teach`, `technical-writing` and `unslop` follow upstream's
  shorter bodies. Shared host-execution and on-demand sections are unchanged.
- **Setup and routing.** `setup-pstack` adds the `# defaults: 3` marker and the
  three budget tiers capped at `xhigh`. It drops the retired role lines and
  selects the cross-judge by vendor. `poteto-help` lists `reframe`.
  `recall` sends one investigator to each source, so it no longer depends on
  `why`. `arena`, `swarm`, `show-me-your-work`, `figure-it-out`,
  `automate-me`, `no-comments` and `benchmark-checklist` follow their upstream
  edits.
- **Statechart.** The shared runtime retains the updated `mermaid.ts`,
  `dot.ts`, `run.ts`, `statechart.ts` and the new `janitor.ts` and `kill.ts`.
  `references/upstream-SKILL.md` matches the new entry. The adapted entry and
  on-demand access carry upstream's native Windows runtime guidance.
  `references/upstream-files.json` records all 410 upstream files at the new
  commit. Of those, 377 are development tests and 32 are retained originals.

## Adaptation decisions

Upstream now names concrete Cursor model slugs, Opus `-fast` rules, a Fable
exception and a Gemini panel seat. Both adaptations keep confirmed host
preferences with `inherit-parent` defaults and never invent model IDs. A
diverse panel uses distinct confirmed models only. On Agents, a speed setting
applies only when the confirmed preference names it. The former urgency-based
fast-mode sentence is removed everywhere, following upstream's removal of
per-subagent speed choice. On Claude Code, fast mode remains a session setting.
Upstream's `AskQuestion`, `Task`, `run_in_background`, `readonly`, `/loop`,
`~/.cursor` paths and Cursor built-in skills keep their existing host
replacements.

Native `requires` and on-demand `dependencies` follow the new references. On
every on-demand variant, the dependencies are exactly the prepared qualified
links in its reference files, as they were at the baseline. Native requirements
drop skills that no longer appear in the procedure:

- `architect` drops `how`, `why`, `interrogate` and its principle requirements.
- `poteto-mode` drops `how` and `reflect`.
- `no-comments` drops `how`.
- `recall` drops `why`.
- `reflect` drops `principle-encode-lessons-in-structure`.
- `principle-attack-the-premise`, `principle-build-the-lever` and
  `principle-minimize-reader-load` no longer reference other principles.

The original-resource descriptions of `interrogate`, `principle-explain-the-number`
and `sharpen` had drifted from their retained originals before this
revision. They now match the originals. No upstream skill is excluded.

## Tooling changes

Upstream removed the plan checker, so the opt-in `pstack-update.py plans`
command and its three plan-checker probe tests are retired. Its contract
comparison and 13 remaining tests are unchanged. The ordinary suite's
inertness sentinel now replaces each pstack `worktree-audit.sh` helper,
which is still distributed in the original and both adaptations. The suite
still reports three Pack helper execution sentinels. The historical
integrated on-demand scenario in `content-probes.py` already referenced
retired `orch` scripts. It is left unchanged, together with the plan fixture
that scenario reads.

## Verification

Validation used a clean baseline at `98a2675` and the pinned Packy v0.2.34
release. No installed user Pack or selected user snapshot was changed.

- `./scripts/validate.sh <baseline> --json` returned `valid` for 14 Packs and
  448 fitness rows. pstack 6.3.0 has 518 closure files. Every other Pack
  version is unchanged, and no file outside `packs/pstack` changed in any
  Pack.
- `./scripts/test.sh` passed 74 ordinary tests with three Pack helper
  execution sentinels. The opt-in probe suite passed 13 tests.
- `pstack-helpers.py` ran the watcher help and decision-log checks on both
  adaptations. Authored and installed bytes were unchanged. Both watcher
  suites passed 54 tests with 154 assertions and strict type checking in
  disposable copies.
- `pstack-statechart.py --upstream <checkout at 41e4009>` passed for all 410
  upstream records, 32 retained files and 37 distributed files. Upstream's
  complete statechart suite passed 304 tests in a disposable copy. Seventy TLC
  tests were skipped because `TLA2TOOLS` was unavailable.
- `pstack-native.py` passed on the committed candidate for both surfaces. It
  installed and verified all 59 skills per surface, recovered six access roots
  with pinned dependencies, and uninstalled the Pack with temporary state
  removed.
- No conflict markers or unresolved Cursor-only mechanics remain in the
  adapted trees. Every relative and prepared link resolves. Each on-demand
  entry's dependencies equal its prepared qualified links. `git diff --check`
  passed.

These checks do not establish client loading, model-backed workflow execution,
persistent monitoring or the skipped TLC checks. The update does not publish
a snapshot or update user installations.
