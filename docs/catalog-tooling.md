# Released Catalog tooling

`packy-release.json` is the single release declaration for local validation,
CI validation, construction, and publication. It contains one exact stable
release version, its full embedded source commit, and the four archive SHA-256
checksums for Darwin/Linux amd64/arm64. It is strictly parsed data; unknown,
duplicate, missing, or malformed fields fail before acquisition.

## Reviewed engine adoption

The current pin adopts [Packy v0.2.30](https://github.com/yersonargotev/packy/releases/tag/v0.2.30),
source `65992143121fe33f65d5ac3c98e6a1ed14484874`, to fix immutable-source
handoff for byte-identical global Claude skills. The previous engine was
v0.2.28. This change keeps the existing ordinary skill contracts; the optional
skill-template capability introduced in v0.2.29 is not requested by these Packs.

The [release execution](https://github.com/yersonargotev/packy/actions/runs/39175836256)
passed the complete native executable Catalog contract on Darwin/Linux
amd64/arm64 before publication. Its four retained `contract-v0.2.30-<platform>`
artifacts contain matching source/version identities, artifact validation,
functional test events, and the same `SHA256SUMS` as the published archives.
All four published archive digests and the local native executable identity were
verified before changing the pin. Candidate/baseline validation, construction,
and released-binary lifecycle acceptance must also pass for this Catalog candidate.

## Local commands and prerequisites

Install Python 3.9 or newer, curl, Git, and the workflow parser:

```sh
python3 -m pip install -r requirements-tooling.txt
./scripts/validate.sh [baseline-catalog-project] [--json]
./scripts/packy.sh version --json
./scripts/packy.sh catalog build --project . \
  --source-repository yersonargotev/packy-catalog \
  --source-commit "$(git rev-parse HEAD)" --out-dir /path/to/new-dist --json
```

`packy.sh` forwards arguments to the verified released CLI. Its
[command documentation](https://github.com/yersonargotev/packy/blob/65992143121fe33f65d5ac3c98e6a1ed14484874/docs/catalog-project.md)
explains versioned JSON reports, optional build baselines, and publication.
Local construction labels do not certify a clean reviewed commit and do not
create an attestation or official Catalog Publication. The main-push workflow
owns official publication; do not manually publish a second release.

No Go runtime, Packy source checkout, global installation, or alternative
binary on PATH participates. Validation and construction read Pack resources
as inert data. Adoption, Ponytail, Claude and pstack lifecycle acceptance use the opt-in released-binary
runner documented in [`scripts/probes/README.md`](../scripts/probes/README.md).
Independent pstack content and host-loading checks retain their own prerequisites.
Ordinary validation never invokes these probes.

## Acquisition, cache, and network

Every call chooses the native platform, downloads only the declared official
GitHub release archive when absent, checks SHA-256 before execution, extracts
only its sole regular `packy` member into a disposable private directory, and
compares `packy version --json` with the complete declaration. Extraction uses
the same sealed bytes that were hashed. No workstation catalog or host
configuration is initialized by acquisition.

Only a checksum- and identity-verified archive is atomically exposed in the
cache. Its key includes version, source commit, platform, and checksum. Every
warm invocation repeats checksum, safe extraction, and embedded identity
verification; cached executables are never reused. The default directory is
`${XDG_CACHE_HOME:-$HOME/.cache}/packy-catalog/tooling`. `PACKY_CACHE_DIR` selects
an explicit cache directory, including disposable test/CI caches.

Corrupt, incomplete, or symlinked entries fail without silently redownloading or
using another release. Remove only the cache entry named in the diagnostic and
retry. Download failures clean staging directories and leave no usable entry.
Interrupted acquisition may leave `.acquiring-*` staging directories; those
are never cache hits and can be removed. Concurrent cold acquisitions can
return a retryable cache-conflict error rather than replace an existing entry.

Cold acquisition needs HTTPS access to GitHub release assets, including its
redirected asset hosts. curl retains normal TLS verification and proxy settings.
A verified warm archive needs no artifact download. Content validation still
resolves declared public upstream origins over the network; this change does
not provide offline origin caching. Packy's origin transport supports
`HTTPS_PROXY` and `SSL_CERT_FILE` without disabling certificate verification.
Publication additionally requires authenticated GitHub CLI (`gh`), release
access, and native release immutability, supplied by the official workflow.

## CI and publication trust

PR validation has read-only permissions, checks the exact base commit, and
invokes the same local entry point and release declaration. Contract tests use
the actual native release binary and controlled external download/GitHub
transports. They execute fixture data only, never Pack scripts or hosts.

After a successful official main-push validation, read-only preparation checks
its clean checkout against the exact validated commit and runs the declared
`catalog build`. Only the two snapshot assets cross the job boundary.

The credentialed job downloads those assets, reads release declaration data
again from that exact commit, and independently downloads and verifies Packy.
It uses a fresh job-local cache, not executable bytes supplied by preparation.
Its acquisition implementation is inline trusted workflow orchestration;
`scripts/validate-publication-workflows.sh` requires it to equal the local
acquisition implementation exactly. This checked mirror keeps the same contract
without executing Catalog Project scripts in the credentialed job. The job
attests the prepared archive and invokes only the verified released publisher,
preserving immutable publication, byte checks, matching-draft recovery, and
idempotent retries.

## Tests and reviewed upgrades

The [delivery guard](delivery.md) verifies GitHub-recognized closing references
before protected integration and requalifies delivery issues after prerequisites.
Its tracker-boundary tests run with the ordinary suite below.

Run the complete ordinary tooling suite with the local Python prerequisites:

```sh
./scripts/test.sh
```

This command checks Catalog-owned Python and shell syntax, including workflow
shell blocks, before acquiring the native test archive. Syntax checks read
opt-in probe scripts as data. The ordinary suite then runs once in a disposable
copy with every pstack `check-plan.mjs` helper replaced by an execution sentinel.
Any sentinel execution fails the command even if a test ignores the helper's
exit status. The source checkout is untouched, temporary state is cleaned up,
and no Node runtime is needed. This scenario protects the inert ordinary-CI
boundary; it does not execute or replace the opt-in lifecycle probes.

The pstack probe tests remain explicitly opt-in under
[`scripts/probes/README.md`](../scripts/probes/README.md), including their Node
prerequisite. They execute reviewed Pack helpers and are excluded from this
suite and ordinary CI.

The tooling suite acquires the declared native archive once; cases then use controlled
transports and disposable state, without live GitHub publication, Go, host
services, or model execution. `PACKY_TEST_ARCHIVE=/path/to/native-archive`
reuses an already downloaded fixture; the cases still verify its declared
checksum and identity. Real full-catalog provenance validation remains
`./scripts/validate.sh [baseline] --json` and needs upstream network access.

The ordinary runner establishes one strict Git environment before discovering
tests. It removes inherited `GIT_*` variables and `EMAIL`, disables global and
system Git configuration, and sets `user.useConfigOnly=true`. Its HOME and XDG
configuration directory belong to the disposable run and are removed on both
success and failure. The existing Python/YAML prerequisite remains available
when installed in the caller's user site; no caller Git configuration is written.
All fixture subprocesses inherit this profile, including the content, pstack,
negative mutation, and publication-preparation commit paths. Each commit must
still declare `Fixture <fixture@example.invalid>` through invocation-scoped
configuration (or repository-local configuration inside its owned fixture).
An earlier command's `-c` identity does not configure later commands. Direct
`unittest` invocations bypass the runner and are not proof of this contract.

Public-command regressions check repeated missing-identity failures, conflicting
ambient author/committer and configuration injection, preserved caller state,
and cleanup after success and failure. Delivery evidence must record the full
ordinary command on required Linux CI and available local Darwin execution;
focused tests or one platform do not establish the other platform's result.

### Fixture preparation failures

Ordinary fixture preparation uses `scripts.fixture_commands.prepare`. It returns
captured stdout on success and raises a test error on failure, for example:

```text
fixture command git commit: exit status 128
fatal: author identity unknown
```

Callers supply a static, non-sensitive command `label` (such as `git commit`),
the argument list, and their existing `env`/`cwd`. Arguments and child
environments are not dumped. The default deadline is 30 seconds per command;
an explicit `timeout` must be finite and positive. Spawn errors report
`spawn failed` with the OS reason; deadlines report `deadline expired` and any
stderr captured before expiry. Invalid UTF-8 is replaced rather than hiding the
failure. Diagnostics are limited to 8,192 characters after redaction, with a
truncation marker when necessary.

The helper reuses the content-probe runner's bounded capture (16 MB combined
stdout/stderr) and isolated process session. Fixture input is closed; text
containing `[y/N]` is data, not an approval request. Content probes retain their
existing strict approval handling. The runner kills the owned process group
when its leader exits, on timeout, or on failure, and waits for its direct child
before returning. Normal descendants cannot retain its pipes or write after
fixture removal; orphan reaping belongs to the OS. Children that deliberately
escape the session are outside this test-fixture contract. Fixture directories
remain owned by the caller's `TemporaryDirectory`/`addCleanup` lifecycle. Register
cleanup before preparing commands; `unittest` reports an additional fixture
cleanup failure separately without hiding the primary command failure.

Failure diagnostics redact exact nonempty values passed through `redact` and
environment values whose names contain `TOKEN`, `PASSWORD`, `SECRET`,
`CREDENTIAL`, or a `KEY` component. Redaction runs before truncation and applies
to both nonzero-exit and timeout diagnostics. Other sensitive argument or child
data values must be declared through `redact`; this is not a detector for
unknown secrets or encoded/transformed values. Do not embed secrets in labels
or Python source: the test runner may show source lines in a traceback.
Successful returned stdout remains data for the caller, not a sanitized log.

The migrated callers cover ordinary Git initialization, staging, commits and
revision reads for content, pstack, negative fixtures, publication preparation,
and probe/identity regressions. Subprocesses exercising commands under test
(including intentional missing-identity rejection) remain observable test
subjects, not preparation commands. Public-command regressions exercise success,
exit 128, spawn failure, timeout, sensitive diagnostics, descendant cleanup,
secondary fixture-cleanup errors and preservation of unrelated state.

Upgrade the pin only through a reviewed PR after the immutable stable release
is published and its four native functional contract results are available.
Verify the release tag's source commit, published archive digests, embedded
identities, and released command/schema compatibility. Change all pin fields
together, then run contract tests, full candidate/baseline validation, and
snapshot construction. Workflows do not declare an independent tool version.

When changing acquisition code, update its marked inline mirror in
`.github/workflows/publish.yml` in the same PR. The workflow guard rejects drift
and changes to the publication authority or exact-source boundaries. Review
that mirror as executable workflow orchestration, and the release pin as data.
