# Released Catalog tooling

`packy-release.json` is the single release declaration for local validation,
CI validation, construction, and publication. It contains one exact stable
release version, its full embedded source commit, and the four archive SHA-256
checksums for Darwin/Linux amd64/arm64. It is strictly parsed data; unknown,
duplicate, missing, or malformed fields fail before acquisition.

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
[command documentation](https://github.com/yersonargotev/packy/blob/1b8d04ddee510b24adcb12906914240bd7063aa6/docs/catalog-project.md)
explains versioned JSON reports, optional build baselines, and publication.
Local construction labels do not certify a clean reviewed commit and do not
create an attestation or official Catalog Publication. The main-push workflow
owns official publication; do not manually publish a second release.

No Go runtime, Packy source checkout, global installation, or alternative
binary on PATH participates. Validation and construction read Pack resources
as inert data. The existing opt-in lifecycle probes remain separate until
migration under #55–#57; their existing prerequisites are not removed by #54.

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

Run the complete automated suite with Python and Node available:

```sh
./scripts/test.sh
```

It acquires the declared native archive once; cases then use controlled
transports and disposable state, without live GitHub publication, Go, host
services, or model execution. `PACKY_TEST_ARCHIVE=/path/to/native-archive`
reuses an already downloaded fixture; the cases still verify its declared
checksum and identity. Real full-catalog provenance validation remains
`./scripts/validate.sh [baseline] --json` and needs upstream network access.

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
