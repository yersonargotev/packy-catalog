# Reviewed pstack surface variants

The sections below record the 4.0.0 rollout. The final section records the
4.1.0 update limited to common sources and Codex.

Date: 2026-10-02. Catalog issue #32 follows the schema v3 rollout in #31.
pstack changes from 3.0.0 to 4.0.0 because its effective host instructions,
invocation behavior, helper execution, and selected dependency contracts change.
Other Pack versions stay unchanged.

## Content and provenance

All 47 logical skill IDs retain their purpose and existing bindings. Each common
source at `skills/<id>` is the original exact copy from
`cursor/plugins@ecc249f1e306fc64ddf83c7bed16cacf7c2239db`. All original helper
files and the MIT notice remain byte-identical. There is no Cursor adapter.

Each skill has three explicit adapted origins at `skills/<surface>/<id>`, with
the original upstream path and MIT notice referenced. Variant descriptions
match their actual frontmatter. There are 141 reviewed adaptations and 536 files
in the complete pstack closure, including retained originals.

PR #24 was reviewed as source material, not merged or modified. Its useful
portable workflow changes and Codex invocation metadata were copied into the
new variant trees. Its replacement of the original common trees, generic host
preface, shared model preferences, residual Cursor APIs, invented model defaults,
and upstream-repository paths were not retained as the final contract.

## Host contracts

| Surface | Invocation | Tools, models, and skill roots |
| --- | --- | --- |
| Codex | 46 manual skills use `agents/openai.yaml`; `setup-pstack` remains implicit. | Use advertised subagent APIs, confirmed models, `.agents/skills`, and `~/.agents/skills`. |
| Claude | Preserve upstream `disable-model-invocation` on 46 skills; setup remains implicit. | Use available Agent types/parameters and native `.claude/skills` roots. Read manual dependencies as files rather than invoking/preloading them through Skill. |
| OpenCode | Explicit-request intent appears in skill instructions/metadata. This is not an enforced manual-only control. | Use available task/skill/read APIs and `.opencode/skills` / XDG native roots. Omitted model overrides use the configured subagent model, which need not be the parent's. |

The OpenCode distinction follows its [documented frontmatter and skill
permissions](https://opencode.ai/docs/skills/). Claude's distinction follows its
[invocation controls](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill)
and [subagent contract](https://code.claude.com/docs/en/sub-agents).
Unsupported Cursor presentation/frontmatter fields are removed from adaptations;
originals remain intact. Names normalize to the logical kebab-case IDs.

Preferences are isolated as `~/.pstack/<surface>-models.md`; setup writes only
confirmed selections, defaulting to `inherit-parent` as an instruction to omit
an override. It does not change host configuration. Model diversity, independent
review, live verification, background execution, and persistent scheduling are
reported only when they actually occurred. Missing required evidence blocks its
gate. Accessible current-workspace history or an explicitly labeled conversation
digest replaces assumptions about Cursor's private transcript layout.

`arena`, `architect`, and `reflect` declare their additional mandatory principle
dependencies in each effective variant. Optional routing from `poteto-mode` to
`figure-it-out` has an explicit direct-workflow fallback, avoiding a dependency
cycle. External authoring, control, routine, and tracker integrations are checked
before use. A personal skill need not produce an unrelated PR; reflection keeps
unpublished backlog local; monitoring alone grants no repair/publication authority.

## Helpers

The orchestration and PR watcher helpers retain their reviewed source and locked
dependencies. Their adapted bootstrap copies scripts into a per-run temporary
workspace before installing dependencies, preserving Packy-owned trees. The
staged path is canonicalized to avoid macOS `/var` / `/private/var` recursion.
The child keeps the working directory, arguments, and environment; the wrapper
propagates its result and removes scratch files. Helper dependencies require Bun
and package access; failure is reported rather than counted as verification.

The worktree audit no longer searches Cursor transcripts. It reports history
unknown and requires history verification before cleanup. Plan checks use the
installed playbook and recorded objective. The decision-log helper retains its
append-only, tab/newline, and spreadsheet-formula escaping behavior.

## Acceptance evidence and limits

- Complete engine validation passes: 10 Packs, 552 fitness rows, including exact
  original trees, adapted origin closure, notices, and baseline version rules.
- All 141 frontmatters parse; names match logical IDs. The Codex/OpenCode skills
  pass the installed skill-creator validator; Claude's supported manual-only
  field is validated separately rather than rejected by that Codex-only checker.
- An independent read-only forward test covered no delegation, no model catalog,
  no transcript, and no scheduler, then reviewed every skill and helper. Its
  concrete host, scope, dependency, and path findings were corrected and reviewed.
- Real Codex 0.160.0 executed `$bro` with model inference in a disposable project:
  “Sending the same request again won’t create a second record.” The isolated
  run reused existing authentication only for that request, then removed the copy.
- Real Claude Code 2.1.220 expanded `/reflect` and executed a Read of its judgment
  reviewer reference in both global and project installations. Both exited zero
  through a localhost deterministic Anthropic provider. A separate attempt at
  model inference reported `Not logged in`; model-backed Claude behavior remains
  runtime-unknown.
- Real OpenCode 1.18.15 loaded `reflect` through its skill tool and read the same
  reference in both scopes, exiting zero through a localhost deterministic
  OpenAI-compatible provider. No inference occurred. No OpenCode model credential
  was available in the isolated fixture; model-backed workflows remain unknown.
- `scripts/probes/pstack-host-loading.py` reproduces those native Claude/OpenCode
  tool calls. It uses fake local-only keys, disposable roots, no external plugins,
  and OpenCode's process-local external-skill discovery disabling flag. This flag
  is not persistent isolation and does not bypass Packy's coexistence guard.
- `scripts/probes/pstack-helpers.py` runs the shipped helpers for all three hosts,
  checks log behavior, and compares the installed file/mode/content inventory
  before and after. The upstream helper suite also passes: 52 tests, 206 assertions.

Native transport/tool probes establish discovery and file consumption, not an
independent review or execution of all 47 workflows. No inference or background
completion is claimed where it did not occur. Cursor original preservation does
not advertise Cursor installation support.

For lifecycle and snapshot reproduction, copy `scripts/probes/pstack_lifecycle_test.go`
and `catalog_adoption_test.go` into a disposable v0.2.26 engine's `internal/cli`.
Set `PROBE_OLD_SNAPSHOT` / `PROBE_OLD_COMMIT` to the complete #31 snapshot and
`PROBE_SNAPSHOT` / `PROBE_SOURCE_COMMIT` to the complete #32 candidate. Run
`go test ./internal/cli -run '^TestPstackCatalogVariants$' -v -count=1`.
These test-only local sources do not verify remote attestations; the official
publication workflow retains that separate check.

The full acquired-catalog lifecycle probe passed for both global and project
scope. It installed pstack 3.0.0 simultaneously on Codex and Claude, acquired
the complete 4.0.0 candidate, and updated each surface while proving the other
host's skill tree stayed byte-identical. Removal of Codex preserved Claude;
helper drift blocked removal. OpenCode's divergent simultaneous activation was
rejected without state changes; after removing the conflicting installations,
OpenCode installed and removed its own variant. Selecting only `architect`
installed the additional effective principle dependencies.

Two independent complete snapshot builds were byte-identical (archive and
`SHA256SUMS`), with archive SHA-256
`7420b9a76954fe6fb926b872a551e14bc07bd1aa5d77e9ddad987ec1925c8bf8`.
The probe source label was `7a8597e6f0c3867540e342070fed46f97a2e1bfb`; these are
local prepublication artifacts, not official releases. The publisher rebuilds
from the actual reviewed merge SHA. Every archived Pack file was compared with
the final candidate and matched. PR #24's reviewed source head was
`62b19451f697091443b174fd1a10660168474554`.

## 4.1.0 common and Codex update

The 2026-10-03 contract migration advances the shared `cursor-plugins` origin
from `ecc249f1e306fc64ddf83c7bed16cacf7c2239db` to
`e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`. It adds `benchmark-checklist`,
`correct`, and `principle-explain-the-number`, bringing the common and Codex
inventories to 50 skills each. All common trees and the MIT notice match the
new upstream revision byte-for-byte, including file modes.

Packy v0.2.26 allows only one origin per repository, so the origin pin is shared.
The Claude and OpenCode trees, their 47 variant records per host, bindings,
descriptions, invocation policies, and effective dependencies remain unchanged
from 4.0.0. Their adaptations still derive from the earlier revision and
intentionally omit these upstream changes. The three new resources have explicit
exclusions on those hosts. No new Claude or OpenCode variants were added.

Codex receives the upstream architecture checks, performance measurement
guidance, schema-first TypeScript examples, fresh-worker rules, hourly autopilot
audits, and revised PR workflow. It retains native invocation metadata, confirmed
model preferences, installed-skill paths, and capability checks. Hourly audits
use active-session monitoring or a verified scheduler rather than assuming
Cursor's `/loop`. The benchmark checklist supports Linux and macOS core counts.

The Codex `poteto-mode` dependency list adds both measurement skills.
`principle-explain-the-number` requires `benchmark-checklist` only in its Codex
variant. Keeping this dependency out of the common contract avoids traversing an
unavailable dependency when the excluded root is evaluated on another host.
The checklist's link back to the principle is optional background, avoiding a
dependency cycle while allowing standalone checklist selection.

Validation against the clean catalog baseline
`da96c291a2325e96e15e702c75588b1290da5d58` passed with the pinned v0.2.26 engine:
`PACKY_VALIDATOR_ROOT=../packy ./scripts/validate.sh <baseline-checkout>` reported
10 Packs and 561 fitness rows. All 50 Codex skills passed skill-creator
validation. The common and Codex plan checkers accepted filled versions of their
shipped skeletons and rejected an obsolete audit cadence and a missing live
verification lane. Byte/mode inventories and manifest comparisons proved the
other hosts unchanged. Unrelated Pack versions remain unchanged. These checks
do not claim model execution of all workflows or persistent scheduler execution.
