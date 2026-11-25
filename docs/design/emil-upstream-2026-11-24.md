# Emil upstream review

Reviewed against clean catalog baseline
`98a26757d6ce780bd6f0c17c0690662031ea8f07` on November 24, 2026.

## Emil 4.0.0 contract migration

Emil moves from 3.1.0 to 4.0.0 and pins
[`emilkowalski/skills@64eb3deb9a5fbfa041faf783e0bc3fd635872e9c`](https://github.com/emilkowalski/skills/commit/64eb3deb9a5fbfa041faf783e0bc3fd635872e9c),
previously `c8a79627b59d72d764d6ab6f2c87c09a48169833`.
Three new skills, new native dependency edges, updated descriptions and a
narrower Agent Plugins export require a contract migration under the README's
closed Refresh rule. The removed export eligibility warrants a major version
increase, following the Matty 5.0.0 precedent.

Upstream rewrites all 26 previously declared skill files. The changes tighten
wording and descriptions, and replace several named skill references with
literal sibling paths:

- `animate/SKILL.md` now reads `../pick-ui-library/SKILL.md` instead of
  invoking `pick-ui-library`; `animate/RECIPES.md` follows
  `../choreograph/SKILL.md` for group entrances.
- `emil-design-eng`, `find-animation-opportunities`,
  `improve-animations/AUDIT.md`, and `review-animations` (`SKILL.md` and
  `STANDARDS.md`) follow `../choreograph/SKILL.md` for staggered entrances.
- `apple-design` points to `../animation-performance/SKILL.md`.
- `improve-animations execute <plan>` reviews the executor's diff against
  `../review-animations/STANDARDS.md`.

These paths resolve only when the sibling is installed or bundled beside the
skill. Each referencing skill therefore declares the sibling as a native
`requires` edge, which native installation and plugin export both follow:
`animate` requires `choreograph` and `pick-ui-library`; `apple-design`
requires `animation-performance`; `emil-design-eng`,
`find-animation-opportunities`, and `review-animations` require
`choreograph`; `improve-animations` requires `choreograph` and
`review-animations`. The manifest descriptions of `animation-performance`,
`choreograph`, `emil-design-eng`, `pick-ui-library`, and `prototype`
follow their updated upstream entries.

`review-animations` is eligible only for Claude plugins because of its
user-only invocation metadata. `improve-animations` now requires it, so its
Agent Plugins export is removed: an explicit selection must fail rather than
ship an unresolved sibling path. Its Claude plugin export, with its subagent
prerequisite, remains. `animate` stays unexported; upstream's path reference
resolves its earlier invocation concern, but enabling its export is a separate
review.

## New skills

- `gestures` builds drag, swipe and sheet interactions. It is an exact copy
  with native Agents and Claude bindings. Its `../pick-ui-library/SKILL.md`
  reference adds a `requires` edge, so it is eligible only for Claude plugins,
  the formats that `pick-ui-library` supports.
- `learn-taste` turns a session's design corrections into approved rules. It
  keeps upstream `disable-model-invocation: true`, adds catalog-only
  `agents/openai.yaml` with `allow_implicit_invocation: false`, and has
  adapted provenance and Claude-only export eligibility, like `prototype`.
  Its optional transcript reading is conditional on the host and the user's
  request.
- `ask-emil` routes a situation to one skill or flow. It receives the same
  user-only invocation adaptation as `learn-taste` and native bindings on both
  surfaces. Like `matty:ask-matt`, it declares no required edges: the user
  chooses a route and it reads the chosen skill's `SKILL.md` before
  recommending it. It is not exported, because its routes name many sibling
  skills with unqualified slash syntax that has no reviewed plugin invocation.

All 20 upstream skill trees are represented. The 30 upstream skill files and
the MIT notice retain their exact bytes and modes. The catalog-only
`agents/openai.yaml` files for `pick-ui-library`, `prototype`, and
`review-animations` retain `allow_implicit_invocation: false`. The upstream
README, root cheatsheets and repository metadata remain outside the declared
Pack closure.

## Verification

With the declared `requirements-tooling.txt` installed in a disposable virtual
environment, run:

```sh
./scripts/test.sh
./scripts/validate.sh /path/to/clean-baseline --json
```

The complete baseline validation reports `result: valid`, 14 Packs and 452
fitness rows, including provenance, exact-copy closure and independent version
checks. Every other Pack retains its baseline version. A separate source
comparison checks every upstream skill file and the notice against the new
commit; only the five catalog-only `agents/openai.yaml` files differ.

The ordinary tooling suite passes all 74 tests, including the three Pack helper
execution sentinels. `git diff --check` also passes.

A local candidate built from the working tree exports Emil in both formats
through the released engine. Claude plugins select 18 skills and Agent Plugins
12; every exported file matches its upstream bytes, and every literal sibling
path resolves inside each package. A single `emil-design-eng` Agent Plugins
export bundles `choreograph`. Explicit Agent Plugins exports of
`improve-animations` and `gestures`, and a Claude plugin export of
`ask-emil`, fail without output. The opt-in generation probe,
`scripts/probes/generation.py --pack emil --skill emil-design-eng`, passes on
the committed candidate: it installs, verifies and removes the skill on Agents
and Claude and exports it in both formats with matching bytes and modes. The
historical `content-probes.py` adoption scenario requires its v0.2.31
checkout and does not apply. No skill procedure or model workflow is executed.
