# Emil, pstack and Matty upstream review

Reviewed against clean catalog baseline
`168a9a940e80b0b6254fc446cc05edef8cf21805` on November 4, 2026.
[Issue #138](https://github.com/yersonargotev/packy-catalog/issues/138) defines
the approved delivery scope and acceptance criteria.

## Emil 3.1.0 contract migration

Emil moves from 3.0.0 to 3.1.0 and pins
[`emilkowalski/skills@c8a79627b59d72d764d6ab6f2c87c09a48169833`](https://github.com/emilkowalski/skills/commit/c8a79627b59d72d764d6ab6f2c87c09a48169833),
previously `2d228630ba1446365f614a108cb8252f1feda202`.
The two new resources and updated description require a contract migration
under the README's closed Refresh rule. The additive change warrants a minor
version increase.

- `choreograph` coordinates related animations, interruption, reduced motion,
  timing and stillness. Its complete tree includes `RECIPES.md`.
- `remove-animations` removes unnecessary motion, checks removal hazards and
  cleans up orphaned code. Its upstream procedure retains the requirement to
  ask before removing a library dependency.
- `animate`, `animation-performance`, `emil-design-eng`,
  `improve-animations/AUDIT.md`, and `review-animations` incorporate upstream's
  version-specific Motion acceleration guidance. The manifest's
  `animation-performance` description follows its updated entry.

Both new resources are exact copies with native bindings for Agents and Claude
and reviewed exports for Agent Plugins and Claude plugins. Their references to
other skills describe alternative workflows, rather than mandatory invocation
steps. Their frontmatter contains only `name` and `description`; neither needs
a custom role or a new external prerequisite. Recipes remain relative to the
skill root. Export does not establish live client loading or model execution.

All 17 upstream skill trees are represented. The 27 upstream files, including
the MIT notice, retain their exact bytes and modes. The existing catalog-only
`agents/openai.yaml` files for `pick-ui-library`, `prototype`, and
`review-animations` retain `allow_implicit_invocation: false`. Their adapted
provenance and Claude-only export eligibility remain unchanged. The upstream
README and root cheatsheets are outside the declared Pack closure and are not
introduced as resources.

## Unchanged pstack and Matty

The pstack origin remains
`cursor/plugins@1ba91fc25c0977741dd0e267849e6234b037ed0a`. The latest repository
HEAD reviewed was
[`bb68f2365eceafa0cb2d253112f675acf5f144cc`](https://github.com/cursor/plugins/commit/bb68f2365eceafa0cb2d253112f675acf5f144cc).
Both commits have the same complete `pstack/` Git tree,
`4719e1c4b4c43bac85d4206a8b41dd2899769c1c`. There are no upstream pstack changes
to incorporate; its version stays 6.1.0, with its origin pin, originals,
adaptations, statechart inventory and legal closure unchanged.

Matty's pinned commit,
[`mattpocock/skills@4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`](https://github.com/mattpocock/skills/commit/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d),
is still repository HEAD. Its version stays 5.0.0 and its complete Pack remains
unchanged. Every other Pack also retains its version and content.

## Verification

With the declared `requirements-tooling.txt` installed in a disposable virtual
environment, run:

```sh
./scripts/test.sh
./scripts/validate.sh /path/to/clean-baseline --json
```

This is a content-only contract migration with reviewed byte-exact upstream
sources, rather than a change to executable Catalog behavior. A new red/green
implementation test would duplicate the existing provenance and lifecycle
checks. Verification therefore uses the issue's agreed public boundaries:
released catalog validation, the ordinary tooling suite, and disposable native
installation, export and removal through the released candidate CLI.

The complete baseline validation reports `result: valid`, 13 Packs and 434
fitness rows, including provenance, exact-copy closure and independent version
checks. A separate source comparison checks all 27 upstream file bytes and
modes, all 17 skill identities and the three preserved invocation adaptations.

The ordinary tooling suite passes all 74 tests, including the three Pack helper
execution sentinels. `git diff --check` also passes.

A one-off acceptance run uses the checksum-verified released engine to build
the complete working-tree candidate and execute 16 commands in disposable
candidate workspaces. On both Agents and Claude it installs both new skills,
compares native bytes and modes, verifies the installation, exports both skills
with their complete recipes and MIT closure, compares exported bytes, modes and
origin metadata, and removes the installation while preserving unrelated project
documents and personal sentinel files. All checks pass; the authored Pack stays
unchanged. The local snapshot uses the baseline commit as a construction label;
it is not a committed candidate or an official publication. No skill procedure
or model workflow is executed.
