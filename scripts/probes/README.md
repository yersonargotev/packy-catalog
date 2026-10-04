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
