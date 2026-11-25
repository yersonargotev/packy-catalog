# Matty 5.0.2 upstream update

Matty moves from 5.0.1 to 5.0.2 and pins
[`mattpocock/skills@d65391149dbb5fe76478e76fa8d5122b2aa5a70e`](https://github.com/mattpocock/skills/commit/d65391149dbb5fe76478e76fa8d5122b2aa5a70e),
previously `5863806dd4e15c63174bee4e7515a4256792ecfa`.
This is a contract migration rather than an upstream refresh: an adapted entry
changes with its original, a resource description changes, and a retained
original leaves the closure.

## Reviewed changes

Upstream changes nine commits across `chief-of-staff`, `software-factory`,
`skills/in-progress/README.md`, changesets, and frontmatter CI. The README,
changesets, package files, and CI script are outside the Pack closure. No skill
is added, removed, or moved; Matty still contains 35 skills.

`chief-of-staff` now centres on delegating the work to fresh background
subagents briefed with context pointers and remembering what they taught in the
dated, commit-cited wiki. Questions, interviews, and check-ins stay in the main
session; relays lead with the outcome and user decisions. Recurring jobs are
offered only when a task plainly recurs. Environment improvements become
offers after friction, delegated only once the user accepts. The tactical and
strategic tracks, the schedules section, and the strategic view are gone. Its
`SKILL.md` and `agents/openai.yaml` are byte-exact copies. `ACCESS.md`
ports the new procedure and description while keeping the on-demand context and
the qualified `matty:retro`, `matty:to-spec`, `matty:to-tickets`, and
`matty:implement-spec` links in place of sibling paths; its experimental-use
note now says recurring jobs instead of schedules. The nine-skill procedure
closure, native bindings, dependencies, and rejected plugin exports are
unchanged. The Pack description now tracks the delegate-and-remember focus, and
the scheduling prerequisite applies to an accepted recurring job.

`software-factory` now quotes its description upstream, matching the catalog
adaptation byte for byte. The distributed `SKILL.md` is therefore an exact
copy, and the retained `upstream-SKILL.md` original is removed as obsolete.
The source-fidelity probe drops its quoting special case and compares
`SKILL.md` directly. `ACCESS.md`, catalog-authored `agents/openai.yaml`, the
surveys, and the Claude plugin export are unchanged.

The changes are wording and behavioural refinements of explicitly invoked
experimental workflows without new resources, dependencies, or exports, so the
version is a patch. MIT notices and all unrelated Matty resources are
preserved, and every other Pack retains its version and content.

## Verification

```sh
./scripts/test.sh
./scripts/validate.sh /path/to/clean-baseline --json
git diff --check
```

All 74 tooling tests pass. Validation against a clean `98a2675` baseline
reports `valid`, and only Matty's version changes. From the committed
candidate, with a clean checkout of the pinned origin:

```sh
python3 -B scripts/probes/matty-update.py --upstream /path/to/mattpocock-skills
```

It passes on both surfaces with the released Packy v0.2.34: 101 original
files match in bytes and modes, all 35 native and on-demand trees match, the
chief-of-staff closure and retained access hold, chief-of-staff exports are
rejected, software-factory exports to Claude only, and cleanup completes.

The probe neither executes workflows nor establishes client loading or
model-backed success. Commit, push, snapshot publication, and installed-skill
updates remain separate operations.
