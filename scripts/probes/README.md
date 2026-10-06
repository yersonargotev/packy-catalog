# Opt-in pstack update probes

Run these checks after the catalog validator, against reviewed local content.
They are separate from `scripts/validate.sh` and CI's inert-content validation.
The `plans` command executes the shipped common and Codex plan checkers in
throwaway copies with Node. Temporary copies protect the managed files from
relative writes; they are not a security sandbox for untrusted code.

Requirements: Python 3.9 or newer, plus Node for `plans` and the probe tests.
No packages, credentials or network access are needed.

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

## Ponytail project installation

`ponytail_install_test.go` exercises the real Packy CLI command handlers against
a locally built catalog snapshot. It checks complete, skill-only, and
instruction-only project installation on Codex, Claude, and OpenCode; read-only
preview; notice inclusion; portable verification; and uninstall preservation.
Skill-only installation coexists with Argote. The instruction cases verify
that v0.2.26 rejects cross-Pack ownership of the same instruction file without
changing the project. Personal activation is not accepted: installation uses
JSON output to omit the optional interactive activation offer.

Use a disposable checkout of the pinned Packy engine, with Go installed. Set
`catalog_root` and `probe_engine` to absolute paths. Run from the catalog root:

```sh
catalog_root="$PWD"
probe_engine=/absolute/path/to/disposable-packy-checkout
probe_output="$(mktemp -d)"
probe_commit="$(git rev-parse HEAD)"
cp scripts/probes/catalog_adoption_test.go scripts/probes/ponytail_install_test.go \
  "$probe_engine/internal/cli/"
cd "$probe_engine"
go run ./internal/tools/catalogsnapshot \
  --project "$catalog_root" \
  --source-repository yersonargotev/packy-catalog \
  --source-commit "$probe_commit" \
  --builder yersonargotev/packy@b4cf72d892570c1fb26571c434f2407bb0728bd3 \
  --out-dir "$probe_output/snapshot"
PROBE_SNAPSHOT="$probe_output/snapshot" PROBE_SOURCE_COMMIT="$probe_commit" \
  go test ./internal/cli -run '^TestPonytailProjectInstall$' -count=1 -v
```

The builder resolves upstream origins over the network. The test itself uses
temporary homes and Git projects, a local snapshot source, and fake host
processes. It does not exercise model behavior, host discovery at runtime,
authentication, or remote provenance verification. For an uncommitted candidate,
the source commit above is only a test label; the snapshot is not a publication
or a claim that its bytes match that commit. Remove the disposable engine
checkout and probe output when finished.

## Claude project installation

`claude_install_test.go` uses the same snapshot fixture and pinned engine as the
Ponytail probe. It installs the complete `claude` Pack and each individual skill
on Claude, Codex, and OpenCode, alongside Argote guidance. It checks read-only
preview, notice selection, the complete HTML runtime closure, portable
verification, personal configuration preservation, and uninstall preservation.

Follow the snapshot-build setup above, copying
`scripts/probes/catalog_adoption_test.go` and
`scripts/probes/claude_install_test.go` into the disposable engine's
`internal/cli/`, then run:

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
