# Opt-in content probes

The source-overlay lifecycle probes in this directory remain separate from
released-tooling adoption (#54). Their remaining migration is tracked by #56–#57; they
are not prerequisites for source-free validation, construction, or publication.
Their explicitly documented Go/Packy-source requirements still apply.

## pstack update checks

Run these checks after the catalog validator, against reviewed local content.
They are separate from `scripts/validate.sh` and CI's inert-content validation.
The `plans` command executes the shipped common and Codex plan checkers in
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
  --preserve-surface claude --preserve-surface opencode
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

## Adoption and Ponytail acceptance

After reviewing content, run from a clean committed Catalog checkout:

```sh
python3 -B scripts/probes/content-probes.py --scenario adoption --scenario ponytail > /tmp/catalog-content-evidence.json
```

Select either scenario independently; repeat `--surface codex`, `--surface
claude`, or `--surface opencode` to limit surfaces (default: all three).
`--timeout 30` bounds each lifecycle child. Requirements are Python 3.9+ on
Darwin/Linux (Unix PTYs), curl, Git, uname, and upstream HTTPS access. No Go,
Packy source checkout, globally installed binary, host executable, credentials,
or model is required. The runner acquires and verifies `packy-release.json`
once into owned disposable state and builds one complete candidate snapshot
for all selected scenarios. Tool downloads and upstream origin resolution need
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
retained snapshot and Git projects. Install/uninstall uses a controlled stdin
PTY, answering only the exact project approval prompt bound to the freshly
observed preview digest. Unexpected/repeated prompts, missing approvals,
nonzero children, timeouts and SIGINT/SIGTERM fail visibly. Child groups and
owned state are removed on success, failure and interruption; forced SIGKILL
or machine termination cannot run cleanup. JSON stdout records the committed
candidate, verified Packy identity, builder and archive digests, selected
scenarios, command receipts and outcomes. Progress and failures go to stderr.
The clean commit is rechecked at completion. Save evidence outside the checkout
so redirection does not create an untracked file before the clean-state check.

The evidence describes **local authoring candidates**, not attested Catalog
Publications. No publication, host authentication, activation, model calls or
live user-state changes occur. Ordinary `scripts/test.sh`, validation and PR CI
do not invoke real-content scenarios. Controlled runner-boundary tests use inert
fixture content and fake external transports in the ordinary suite.
[#49](https://github.com/yersonargotev/packy-catalog/issues/49) is overlapping
prior art; this runner does not adopt its source-checkout acquisition design
or modify/close that issue.

## Claude project installation

`claude_install_test.go` retains the legacy snapshot fixture and engine overlay
until #56. It installs the complete `claude` Pack and each individual skill
on Claude, Codex, and OpenCode, alongside Argote guidance. It checks read-only
preview, notice selection, the complete HTML runtime closure, portable
verification, personal configuration preservation, and uninstall preservation.

This unmigrated overlay requires Go and a disposable Packy v0.2.26 checkout
at `b4cf72d892570c1fb26571c434f2407bb0728bd3`. The shared
`catalog_adoption_test.go` contains only its still-needed `adoptionRelease`
fixture. It no longer runs adoption acceptance. For this legacy probe only:

```sh
catalog_root="$PWD"
probe_engine=/absolute/path/to/disposable-packy-checkout
probe_output="$(mktemp -d)"
probe_commit="$(git rev-parse HEAD)"
cp scripts/probes/catalog_adoption_test.go scripts/probes/claude_install_test.go \
  "$probe_engine/internal/cli/"
cd "$probe_engine"
go run ./internal/tools/catalogsnapshot \
  --project "$catalog_root" \
  --source-repository yersonargotev/packy-catalog \
  --source-commit "$probe_commit" \
  --builder yersonargotev/packy@b4cf72d892570c1fb26571c434f2407bb0728bd3 \
  --out-dir "$probe_output/snapshot"
```

Construction resolves public upstream origins over the network. The overlay
uses temporary projects/homes and fake hosts; it does not prove authentication,
model behavior or remote attestation. An uncommitted source label is not proof
of publication bytes. Remove the owned engine checkout and output afterward.
Then run:

```sh
PROBE_SNAPSHOT="$probe_output/snapshot" PROBE_SOURCE_COMMIT="$probe_commit" \
  go test ./internal/cli -run '^TestClaudeProjectInstall$' -count=1 -v
```

For the HTML packing smoke check, run from the catalog root with Node installed:

```sh
probe_html="$(mktemp -d)"
cp packs/claude/skills/html-plan/examples/scheduled-send.html "$probe_html/plan.html"
node packs/claude/skills/html-plan/runtime/pack.mjs "$probe_html/plan.html" \
  --root "$PWD/packs/claude/skills/html-plan"
```

The upstream example refers to a fictional app, so missing source-file excerpts
produce warnings. Packing must still succeed, inline the two runtime assets,
and write `plan.packed.html` in the temporary directory. Remove `probe_html`
when finished. Neither check proves skill discovery or model behavior in a
live host session.
