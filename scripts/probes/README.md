# Opt-in content probes

Adoption, Ponytail, Claude and pstack lifecycle acceptance use the verified
released binary below. Independent pstack content/host checks remain separate
and opt-in. Ordinary validation, construction and publication do not run them.

## pstack update checks

Run these checks after the catalog validator, against reviewed local content.
They are separate from `scripts/validate.sh` and CI's inert-content validation.
The `plans` command executes the shipped common, Claude and Codex plan checkers in
throwaway copies with Node. Temporary copies protect the managed files from
relative writes; they are not a security sandbox for untrusted code.

Requirements: Python 3.9 or newer, plus Node for `plans` and the probe tests.
No packages, credentials or network access are needed. The probe test suite
includes execution of the real Pack plan checkers and remains opt-in after
content review; `scripts/test.sh` and ordinary PR CI do not invoke it.

## Compare surfaces that must remain unchanged

Create a clean checkout of the pre-update commit, then select each surface the
update must preserve:

```sh
python3 scripts/probes/pstack-update.py contracts \
  --baseline /path/to/clean-baseline \
  --preserve-surface claude --preserve-surface codex
```

`--project /path/to/candidate` selects another Catalog Project; it defaults to
this checkout. The comparison covers bound roots and their dependency/notice
closure after applying surface overrides. It checks Pack metadata, effective resource metadata,
source file sets, bytes and executable bits. A shared origin commit or Pack
version may advance; changing those does not imply a host-content update.
Origin identities and repositories must still match.
An optional resource excluded on the preserved surface is not installed there
and does not enter its comparison. Use catalog validation for schema, origins,
exact-copy provenance, cycles, and general runtime fitness.

The command exits 0 only when every selected host is preserved. It exits 1
with the host and failing contract/resource when a difference is found.

## Exercise plan validation

```sh
python3 scripts/probes/pstack-update.py plans
```

The committed `fixtures/pstack-plan.md` is an independently specified fictional
plan, not a template extracted from the implementation under test. For each
checker, the probe requires a valid plan to exit 0 and report zero problems,
an obsolete cadence to exit 1 with its cadence diagnostic, and a missing live
lane to exit 1 with its lane diagnostic. It uses temporary execution directories
and removes them on success, unexpected results, and helper failures. Each
helper invocation has a 15-second timeout. A missing Node executable is a
failure, not a skipped pass. No plan task is executed.

## Test the probes

```sh
python3 -B -m unittest discover -s scripts/probes -p 'test_pstack_update.py'
```

These CLI tests introduce host contract, dependency, resource, byte, executable
mode, and notice drift; verify effective overrides; run the real plan checkers;
and substitute failing and unconditional-success checkers to prove that the
probe rejects bad results and removes temporary execution state. The helper
substitutions are controlled CLI-boundary fixtures in temporary projects.

The other probes in this directory retain their documented requirements in
`docs/research/pstack-surface-variants.md`; this runner does not execute them.

## Released-binary content acceptance

Warp's 15 specification and coordination skills have a focused two-host scenario:

```sh
python3 -B scripts/probes/content-probes.py --scenario warp-specification \
  --warp-baseline /path/to/clean-2.2.0-catalog > /tmp/warp-specification-evidence.json
```

It retrieves every entry on Codex and Claude with full tree/mode/legal and
independent dependency expectations, verifies retained nested spec calls across
a disposable selection change and missing retained content, and checks native
installation on all three hosts. It preserves modified native copies and target
state with content runtimes absent. The retired scanner is only read; no skill
procedure, model, worker, scheduler or external publication runs. See the
[reviewed matrix and limits](../../docs/design/warp-specification-on-demand.md).

After reviewing content, run from a clean committed Catalog checkout:

```sh
python3 -B scripts/probes/content-probes.py --scenario adoption --scenario ponytail > /tmp/catalog-content-evidence.json
```

Select either scenario independently; repeat `--surface codex`, `--surface
claude`, or `--surface opencode` to limit surfaces (default: all three).
Add `--scenario claude` for Claude content acceptance.
`--timeout 30` bounds each lifecycle child. Requirements are Python 3.9+ on
Darwin/Linux (Unix PTYs), curl, Git, uname, and upstream HTTPS access. No Go,
Packy source checkout, globally installed binary, host executable, credentials,
or model is required. The runner acquires and verifies `packy-release.json`
once into owned disposable state and builds one complete candidate snapshot
for all selected scenarios, plus one complete baseline when pstack is selected.
Tool downloads and upstream origin resolution need
network access; the runner removes its private cache when finished.

`adoption` consumes the entire Catalog, rejects a controlled incompatible-index
fixture without changing prior usable state or leaving a new workspace, and
installs/verifies/uninstalls Emil on the selected surfaces. `ponytail` covers
complete, skill-only and instruction-only selection, read-only preview,
notices, portable verification, Argote coexistence for skill-only selection,
shared-instruction ownership conflicts, personal-state preservation, and
uninstall preservation. The [assertion inventory](assertion-inventory.md)
accounts for every displaced Go assertion and the Packy-owned mechanisms.

The supported `catalog candidate` interface owns temporary homes, configuration,
retained snapshots and Git projects. Apply uses a controlled stdin PTY,
answering only the exact ordered approval prompts bound to the freshly
observed preview or plan identity. Each expected prompt is single-use.
Unexpected/repeated prompts, missing approvals,
nonzero children, timeouts and SIGINT/SIGTERM fail visibly. Child groups and
owned state are removed on success, failure and interruption; forced SIGKILL
or machine termination cannot run cleanup. JSON stdout records the committed
candidate, verified Packy identity, builder and archive digests, selected
scenarios, command receipts and outcomes. Progress and failures go to stderr.
The clean commit is rechecked at completion. Save evidence outside the checkout
so redirection does not create an untracked file before the clean-state check.

### Command timing and progress

Each attempted top-level child command has an additive `elapsed_seconds` number
and `context` object in its receipt. Elapsed time uses a monotonic clock, from
immediately before child execution through its result handling and process-group
cleanup, including spawn failure, timeout and interruption. It is finite and
nonnegative; it is not CPU time or an absolute timestamp. Acquisition is timed
at its existing wrapper boundary, not separately for each nested download or
identity-check subprocess. Existing receipt fields and outcome meanings remain
unchanged, as does evidence `schema_version: 1`.

Context always contains `stage`, `scenario`, `surface` and `scope`. Stages are
`candidate-verification`, `baseline-verification` (initial and final clean-commit
checks), `acquisition` (download/verification and reported binary identity),
`candidate-construction`, `baseline-construction`, and `content-acceptance`.
Outside content acceptance, scenario, surface and scope are `null`. Content
acceptance names its scenario and scope (`project` or `disposable-global`).
Single-surface cases carry their surface throughout preparation, lifecycle and
helper commands. In pstack's multi-surface cases, commands with an explicit
surface carry it; shared listing and snapshot transition commands use `null`.
The baseline runner carries the same pstack case context. Historical outcome
records still use `scope: "global"`; only the new context calls this disposable.
Final verification resets case context, so it never inherits the last surface.

Stderr emits flushed lines prefixed `Content probe: ` followed by a JSON object.
Each command has a `started` event containing its argument vector and a terminal
`passed`, `expected-rejection` or `failed` event containing `elapsed_seconds`.
Both include `context` and a one-based `command_id` indexing the final report's
`commands` array. Start events arrive while the child is still running, including
during acquisition and builds. A passed child can still be followed by a failed
scenario assertion; the final report and existing failure message describe that
run-level failure. Forced SIGKILL/machine termination cannot emit a final event
or report. Other human-readable scenario/failure lines remain on stderr; stdout
contains only the final JSON evidence for supported run outcomes (argument
validation errors still use argparse's stderr/exit behavior).

To inspect the commands that consumed the most observed time:

```sh
python3 - <<'PY'
import json
from pathlib import Path
report = json.loads(Path('/tmp/catalog-content-evidence.json').read_text())
for receipt in sorted(report['commands'], key=lambda item: item['elapsed_seconds'], reverse=True)[:10]:
    print(receipt['elapsed_seconds'], receipt['context'], receipt['command'])
PY
```

These measurements describe that run, including I/O and network waits. They do
not establish a performance improvement or replace exact-candidate acceptance.

The evidence describes **local authoring candidates**, not attested Catalog
Publications. Global activation is confined to pstack's owned disposable
workspace. No publication, host authentication, model calls or live user-state
changes occur. Ordinary `scripts/test.sh`, validation and PR CI
do not invoke real-content scenarios. Controlled runner-boundary tests use inert
fixture content and fake external transports in the ordinary suite.
[#49](https://github.com/yersonargotev/packy-catalog/issues/49) is overlapping
prior art; this runner does not adopt its source-checkout acquisition design
or modify/close that issue.

## Claude content acceptance

After reviewing the Claude content, run from a clean committed checkout:

```sh
python3 -B scripts/probes/content-probes.py --scenario claude > /tmp/claude-content-evidence.json
```

This runs complete, eli5-only and html-plan-only selections on Claude, Codex
and OpenCode. It checks read-only preview, notice selection, full HTML runtime
closure, Argote coexistence, portable verification, personal configuration
preservation and uninstall preservation. It shares the acquisition, one-build,
isolation, exact-preview PTY, deadlines, cleanup and JSON evidence contracts
above. Repeat `--scenario` to combine it with adoption or Ponytail in one build;
repeat `--surface` to limit hosts. No Go or Packy source is needed. The
[assertion inventory](assertion-inventory.md#claude-assertion-migration-56)
accounts for the removed Claude Go overlay.

HTML packing is explicitly optional and additionally requires Node:

```sh
python3 -B scripts/probes/content-probes.py --scenario claude --html-pack > /tmp/claude-html-evidence.json
```

This executes the reviewed packer from each installed complete/html-plan skill,
using the installed fictional example and disposable output. It requires exit
zero, no reported errors, exact CSS/JavaScript bytes inside the packed document,
and no remaining external runtime links. Evidence records the packed digest,
expected fictional-source warnings (missing application code under
`<doc-calls>`) and other warnings separately. Warnings do not count as errors;
missing assets or a nonzero packer fail visibly and clean all owned state.
Without `--html-pack`, lifecycle checks only inspect the HTML files as data and
Node is not required. Neither command proves skill discovery, authentication
or model behavior in a live host session. Ordinary tests use only an inert
controlled Node fixture and never execute the shipped packer.

## pstack lifecycle acceptance

From a clean committed Catalog candidate, use the complete schema-v3 baseline
that preceded the host variants (pstack 3.0.0):

```sh
git worktree add --detach /tmp/pstack-baseline 7a8597e6f0c3867540e342070fed46f97a2e1bfb
python3 -B scripts/probes/content-probes.py --scenario pstack \
  --pstack-baseline /tmp/pstack-baseline > /tmp/pstack-content-evidence.json
git worktree remove /tmp/pstack-baseline
```

The baseline must be a clean committed complete Catalog Project. Both checkouts
are rechecked at completion. The runner uses the candidate's single verified
release to build both snapshots, recording their commits, builders, full Pack
inventories and archive digests. Another reviewed baseline can be supplied
explicitly; it must support an actual update to this candidate. Builds validate
every Pack and provenance; neither snapshot is an attested publication.

Every invocation exercises project and isolated global scope with Codex and
Claude; both hosts are required for coexistence checks. The separate withdrawal
scenario covers legacy OpenCode retirement. The lifecycle scenario installs
baseline Codex and Claude, transitions snapshot availability without
changing installed state, then updates each surface while preserving the
other's complete bytes, modes and links. Drifting an installed bootstrap helper
blocks removal: the project copy fails projection checks; the global link exposes retained-source
integrity failure. The helper is restored before successful retirement.

Codex removal preserves Claude, then both retire. OpenCode legacy retirement is
covered separately by the withdrawal scenario below. Architect-only selection
must include the four surface-effective principle dependencies and exclude unrelated `reflect`.
Final checks require no managed skill roots, preservation of unrelated files
and the inactive scope, and project contract/lock/notices retirement. Ambient
home/config/data state and both source checkouts remain unchanged. All writes,
global links and deliberate drift stay beneath runner-owned disposable state.

This uses the common deadlines, exact ordered PTY approvals, command receipts,
JSON evidence and process/state cleanup. It requires no Go, Packy source,
host executable, authentication or model execution. The
[pstack assertion inventory](assertion-inventory.md#pstack-assertion-migration-57)
accounts for the removed Go probe and its final shared helper. The plan checks,
helper checks and host-loading probes remain independent opt-in commands; this
lifecycle run does not claim native skill discovery or model behavior.

## Packy bootstrap acceptance

After reviewing content, run from a clean committed candidate:

```sh
python3 -B scripts/probes/content-probes.py --scenario packy-bootstrap > /tmp/packy-bootstrap-evidence.json
```

This uses the single verified released-tooling declaration and complete Catalog
candidate. Both Codex and Claude are required. Each personal and project case
sets up the hosts sequentially through exact-preview consent, compares actual
bootstrap bytes/modes with the authored effective definition, and preserves the
other host, an unrelated active Pack, unmanaged native skills, and inactive scope.
It then retires only its disposable setup. Global operations are confined to the
owned candidate HOME/config/data environment; live selections are unchanged.

An inert complete two-Pack authoring fixture exercises deterministic host-effective
discovery and qualified cross-Pack retrieval through the same released binary.
Assertions cover the structured contract, identities/versions/host/snapshot,
usable entry/resource paths, supporting/legal closure, executable bytes/modes,
rendered dependency references, nested snapshot reuse, an absent declared runtime,
inert scripts, and unchanged authored resources and target project. Fixture Packs
are never added to the official catalog or published. These metadata checks do
not establish natural-language matching or semantic model-backed workflow success.
The fixture does not depend on pending real-skill adaptations.

The shared runner owns explicit HOME/config/data/cache/project roots, bounded
child processes, command receipts, progress, clean-candidate checks and cleanup.
No host credentials, model calls, live activation, runtime provisioning or manual
publication occurs. Ordinary tests/validation/publication do not run this scenario.
The initial 117-skill compatibility and complete-inventory acceptance remain
separate follow-up deliveries.

## Matty design and planning acceptance

Run the focused, opt-in `matty-design` scenario with a clean pre-adaptation
complete Catalog baseline:

```sh
python3 -B scripts/probes/content-probes.py --scenario matty-design \
  --matty-baseline /path/to/pre-change-catalog > /tmp/matty-design-evidence.json
```

Both Codex and Claude are required; native regression also covers OpenCode.
The [reviewed matrix](../../docs/design/matty-design-on-demand.md) records all 19
entries, required/conditional edges, approvals, output contracts and execution
prerequisites. The scenario compares all 38 root resources and full supporting/legal
closure, follows wrapper/wayfinder references across a controlled snapshot
transition, rejects missing retained content, preserves modified native copies,
and checks native installation on all three hosts. Content runtimes are absent
during retrieval. It obtains instructions without executing any Matty procedure,
script or template. Ordinary checks and publication do not invoke this scenario.


## Matty delivery and writing acceptance

```sh
python3 -B scripts/probes/content-probes.py --scenario matty-delivery \
  --matty-baseline /path/to/clean-4.1.0-catalog > /tmp/matty-delivery-evidence.json
```

The [reviewed 14-skill matrix](../../docs/design/matty-delivery-on-demand.md)
completes the prior 19-skill slice. This scenario checks all 66 roots, full
supporting/legal bytes and modes, explicit implementation/delegation references,
retained-snapshot transitions and missing-content failures, qualified Matty TDD
with pstack TDD active and separately with a modified installed native copy,
absent runtimes, and unchanged target/active/immutable/ambient state. Native
regression covers all 33 skills on Codex, Claude and OpenCode. Both access hosts
are required. The existing isolated runner, central release pin and bounded
process/cleanup receipts apply; no Matty workflow or template is executed and no
live installation changes. Ordinary checks and publication remain inert.

## pstack principles and foundational acceptance

```sh
python3 -B scripts/probes/content-probes.py --scenario pstack-foundational \
  --pstack-baseline /path/to/clean-4.5.0-catalog > /tmp/pstack-foundational-evidence.json
```

The [reviewed 38-skill matrix](../../docs/design/pstack-foundational-on-demand.md)
accounts for 24 principles and 14 utilities on Codex and Claude Code. The opt-in
runner checks all 76 effective roots, required qualified closure, complete
supporting/legal bytes and modes, progressive why references, distinct qualified
pstack/Matty TDD with a modified active native copy, inert setup and absent content
runtimes. Representative nested links retain the initiating host/snapshot across
a controlled selection transition; independent requests follow the new selection
and missing retained content fails. Native regression preserves the scoped
selection, original content and contracts on Codex and Claude. Existing isolated
state, bounded commands, central released binary, complete candidate/baseline
builds, receipts and cleanup apply. No agent workflow is executed; ordinary tests,
validation and publication do not run this scenario.

## pstack 5.0.0 support withdrawal

```sh
python3 -B scripts/probes/content-probes.py --scenario pstack-withdrawal \
  --pstack-baseline /path/to/clean-4.6.0-catalog > /tmp/pstack-withdrawal-evidence.json
```

Use the complete pre-withdrawal baseline at
`52ce7cc0bb4f0657d20dd92123c95e8ac0de3ca9`. This scenario is specific to the
4.6.0 → 5.0.0 migration. It compares the complete declared contract, all existing
Codex/Claude access content and native bytes/modes in both scopes. Identical
personal projections may yield a converged update with no action phases or
approvals; the runner applies that no-op without answering prompts. New OpenCode
requests fail without mutation. Existing OpenCode project installations and
personal activations survive selecting the new snapshot and failed updates.
Explicit uninstall/deactivation then use installed or retained old evidence.
Drift blocks both paths; missing retained content blocks personal retirement.
The old content is restored before successful retirement. Unrelated files and
the inactive scope survive. Acquisition, complete builds, receipts, bounded
children and cleanup use the shared released-binary runner. No workflow runs.

`pstack-helpers.py` now executes only Codex/Claude helpers, from disposable copies
with owned HOME, configuration, data, temporary files and Bun cache, using the
shared bounded child runner.
`pstack-host-loading.py claude [global|project]` checks the supported Claude
transport with a deterministic localhost provider and removes its temporary
state after emitting the result. It does not establish model inference.
See [retirement instructions](../../docs/pstack-opencode-retirement.md).

## pstack engineering and verification acceptance

```sh
python3 -B scripts/probes/content-probes.py --scenario pstack-engineering \
  --pstack-baseline /path/to/clean-5.0.0-catalog > /tmp/pstack-engineering-evidence.json
```

The [reviewed 13-skill matrix](../../docs/design/pstack-engineering-on-demand.md)
accounts for all 26 effective Codex/Claude roots and their foundational closure.
Checks cover actual supporting/legal content and modes, host workflow policies,
rendered nested and runner references, absent content runtimes, a modified active
native architect, retained-snapshot selection transitions and explicit missing-
content failure. Native regression preserves the scoped selection and inherited
contracts/original content on Codex and Claude under the accepted two-host policy. Both access hosts are required.

After content review, this scenario executes only the decision-log helper, using
an explicit disposable output path. It verifies header, append, six-column and
escaping behavior, source/target preservation and cleanup. Bash and the helper's
standard Unix tools are needed for that opt-in execution. This is not proof of
cross-model review, app/formal verification or provider/network workflow success.
The shared central release pin, clean candidate/baseline requirements, isolated
HOME/config/data/cache/project roots, bounded commands, receipts and cleanup apply.
Ordinary validation, tests and publication never run this scenario.

## Complete pstack orchestration access

After reviewing both effective host bodies and their complete supporting trees,
run from a clean committed candidate with the integrated pre-change 5.1.0 baseline:

```sh
python3 -B scripts/probes/content-probes.py --scenario pstack-orchestration \
  --pstack-baseline /path/to/clean-5.1.0-catalog > /tmp/pstack-orchestration-evidence.json
```

This opt-in scenario verifies all 55 skills on Codex and Claude through the same
pinned released CLI, including the four new roots, complete closure/content,
qualified optional routes, retained snapshots and native regressions. Retrieval
runs without content runtimes. Separate reviewed helper execution requires Node,
Bun and package-network access; it uses disposable targets, outputs, stores,
HOME/config/data/cache/temp state and bounded children. It checks plan acceptance
and rejection, orchestration bookkeeping, safe watcher failures and the actual
bootstrap's temporary dependency staging, cwd, failure propagation and cleanup.
No real forge mutation, message, scheduler, worktree deletion or model execution
participates. See the [review matrix](../../docs/design/pstack-orchestration-on-demand.md).

## Warp repository and reporting acceptance

After reviewing the exact 13-skill repository/reporting slice, run from a clean
committed candidate with its clean Warp 2.3.0 baseline:

```sh
python3 -B scripts/probes/content-probes.py --scenario warp-repository \
  --warp-baseline /path/to/clean-2.3.0-catalog > /tmp/warp-repository-evidence.json
```

This retrieves all 13 entries on Codex and Claude, verifies complete effective
resources/legal closure and independent dependencies, preserves native copies
and installed state, checks retained nested calls across a selection transition,
and installs the exact inventory on all three native hosts. Content runtimes
are absent during retrieval. The preceding specification slice stays unchanged.

Add `--warp-helpers` only after reviewing the bundled helpers. This executes the
cached review resolver with explicit fictional repository context and a fake HTTP
transport, validates positive/invalid annotated review locations, embeds fictional
pinned source and regenerates an index in explicit disposable output. Meaningful
decoy/missing-input negatives and full byte/mode observations detect cache lookup,
input/resource mutation and personal-output regressions. Python networking is
prohibited; no submission, credential store, real API, browser, hosting, cloud
repro, live Factory, worker or model workflow runs. Without the flag, helper
content is read only. Ordinary tests/validation/build/publication remain inert.
See the [review matrix and limits](../../docs/design/warp-repository-on-demand.md).
