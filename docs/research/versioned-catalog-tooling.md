# Versioned Catalog tooling

Date: 2026-10-09 (America/Bogota). Status: research supporting a completed design
review. The nine accepted decisions are recorded in
[ADR 0001](../adr/0001-consume-released-packy-tooling.md), including scope,
distribution, verification, testing, binary identity, and structured output.
The implementation findings below describe the inspected revisions, not an
implementation of that ADR.

The subsequent specification review approved the authoring-only disposable
local-candidate seam and nine implementation/release tickets. Published scopes
and native dependencies are tracked by
[Packy #829](https://github.com/yersonargotev/packy/issues/829) and
[Catalog #53](https://github.com/yersonargotev/packy-catalog/issues/53).

## Evidence scope

Inspected clean local checkouts before writing this note: Catalog Project
`679587d355af659c8b5fdcd45138c9daebf0de3e` and Packy
`b4cf72d892570c1fb26571c434f2407bb0728bd3`. Source links below pin those
revisions. GitHub's official API was queried with `gh api` for the latest
release and its tag; it reported immutable release `v0.2.26`, published
`2026-10-02T18:20:58Z`, and a tag resolving directly to that Packy commit.
This is source/API inspection, not execution of a new artifact or a
cross-platform reproducibility test. [Release API][release-api], [tag API][tag-api].

## Existing architecture and implementation

ADR 0039 separates Catalog Publication from Packy releases and calls for CLI
authoring operations including validation. ADR 0040 explicitly keeps the two
repositories separate, assigns parsing, validation, construction, consumption,
and adapters to Packy, and requires a shared immutable engine pin for validation
and construction. A distributed tool preserves those ownership decisions;
changing distribution does not itself require merging repositories.
[ADR 0039][adr39], [ADR 0040][adr40].

Packy's glossary distinguishes the Catalog Project (authoring), Catalog Snapshot
(complete immutable content), and Catalog Publication (release of a snapshot).
Building bytes and publishing them are separate operations in this note.
[Domain vocabulary][context].

| Current entry point | Inputs and outputs | Source dependency |
| --- | --- | --- |
| `scripts/validate.sh [baseline]` | Validates workflow boundaries, then complete candidate and optional baseline; prints Pack identities, digests, file counts, and fitness count. | Defaults to sibling `../packy`, permits `PACKY_VALIDATOR_ROOT`, and runs `go run ./internal/tools/catalogvalidate`; does not verify checkout HEAD. |
| `internal/tools/catalogsnapshot` | Requires project, source repository/commit, builder identity, and a new output directory; revalidates candidate and produces `catalog-snapshot.tar.gz` plus `SHA256SUMS`. It has no baseline argument. | CI checks out pinned Packy and runs Go source. |
| Publication job | Attests the built archive, then publishes/verifies an immutable GitHub release. | Checks out Packy again to execute `scripts/publish-catalog-snapshot.sh`. |
| Optional lifecycle probes | Exercise installation/lifecycle against a local snapshot through Go tests. | Copy catalog test files into Packy's `internal/cli`, then run `go test`. |

Sources: [local validator wrapper][wrapper], [validator command][validate],
[snapshot command][build], [publication workflow][publish], [probe instructions][probes].

The engine commit is repeated in validation and both publication jobs; the
workflow guard enforces their equality. README also names the version and
commit. The guard currently checks source-command strings, so switching to
an executable also requires updating this contract, not merely the YAML command.
[Validation workflow][ci], [publication workflow][publish], [workflow guard][guard],
[README][readme].

## What the current release can provide

The released CLI exposes `catalog refresh`, `create`, `import`, and
`upstream-refresh`; its command registration has no standalone `catalog
validate` or snapshot-build command. Both required operations exist as internal
tool entry points sharing `internal/cataloglayout`. Downloading today's CLI
alone therefore does not replace current validation/build invocations.
[CLI registration][cli], [validator][validate], [builder][build].

Release assets are four `packy_v0.2.26_<os>_<arch>.tar.gz` files for
Darwin/Linux × amd64/arm64, plus `SHA256SUMS`. Each archive is specified to
contain only `packy`; no validator, builder, or publisher script is packaged.
The API supplies a SHA-256 digest for each asset and reports the release as
immutable. There is no Windows artifact in this release contract.
[Release API][release-api], [release packaging][packaging], [artifact validation][artifact-checks].

Consequently, “same artifact locally and in CI” needs a precise definition.
Different operating systems/architectures consume different bytes. One immutable
release with a verified asset digest per supported platform is feasible within
the existing matrix; literal binary-byte identity across that matrix is not
what those artifacts provide. This is an inference from the packaging contract.
[Release packaging][packaging].

## Network, identity, and reproducibility boundaries

Validation resolves public GitHub origins by cloning repositories with go-git
and checking out exact commits. Temporary checkouts are cached only within one
resolver invocation and removed afterward. A precompiled tool removes the Go
build/source-checkout prerequisite for the tool, but does not remove this
network access or upstream-source dependency. Offline validation would require
an additional explicit contract. [Origin resolver][origins].

Complete validation includes runtime fitness, declared closures, provenance,
and optional baseline version rules. A baseline-free successful snapshot build
does not independently prove the version comparison that PR validation performs.
The current workflow connects publication to successful validation of the
official main-push commit. [Catalog validator][catalog-validation],
[snapshot command][build], [publication workflow][publish].

Snapshot construction sorts file entries, normalizes archive timestamps and
gzip OS metadata, checks validated bytes/modes again, and rejects symlinks or
drift. Tests build twice and compare archive bytes. The index includes the
builder's exact `owner/repository@commit`, so a human release version alone
cannot replace that field under today's format. Source repository/commit and
builder identity are caller-provided labels; the build command does not prove
they match Git HEAD. [Snapshot implementation][snapshot], [snapshot tests][snapshot-tests].

Inference: cross-platform snapshot-byte equivalence is a sensible acceptance
criterion if desired, but the inspected repeated-build test is not evidence
that all four published binaries produce identical archives. Matching Packy
release versions is also not sufficient if input bytes, modes, source labels,
or builder labels differ. [Snapshot implementation][snapshot], [snapshot tests][snapshot-tests].

Catalog Publication adds an attestation and GitHub release operations after
construction. Its retry contract compares the two assets and exact target;
it does not compare the entire GitHub release metadata or attestation envelope
byte-for-byte. “Reproducible snapshot” should therefore specify archive and
checksum bytes separately from official publication provenance.
[Publication workflow][publish], [publisher implementation][publisher].

The existing write-authorized publication job executes pinned Packy code and
never checks out or executes Catalog Project content. A replacement bootstrap
must preserve that boundary: putting a pin in one data file does not authorize
executing candidate-supplied scripts with publication credentials. The current
Packy binary-release workflow does not explicitly issue the same build
attestation used by catalog publication; integrity, immutable-release identity,
and builder provenance should not be treated as interchangeable checks.
[Publication workflow][publish], [workflow guard][guard], [Packy release workflow][release-workflow].

## Options and accepted decisions

The design review selected the main CLI and the broader workflow scope;
the separate-executable alternative is retained here for context:

| Option | Benefit | Required decision/work |
| --- | --- | --- |
| Add supported CLI validation/build/publication commands (accepted) | Reuses the existing binary, version lifecycle, and platform matrix; aligns with ADR 0039's CLI-authoring direction. | Implement the accepted identity and output contracts and preserve existing validation/publication semantics. |
| Publish dedicated executables in a versioned tool bundle | Promotes existing narrow entry points without adding end-user CLI commands. | Define a new asset contract, version relationship, platform testing, and whether publisher tooling belongs in it. |
| Require source-free acceptance and publication too (accepted scope) | Makes the broad “no Packy source checkout” claim true. | Package/replace publisher execution and redesign internal-Go lifecycle probes around supported seams. |

The first two options follow from existing CLI/internal-tool boundaries; the
third follows from actual publisher and probe dependencies. [CLI][cli],
[internal validator][validate], [internal builder][build], [publisher][publisher], [probes][probes].

The design review accepted the complete acceptance/publication scope and
verified per-platform assets from one exact release with functionally equivalent
results. It did not add a cross-platform byte-identical snapshot requirement.
See [ADR 0001](../adr/0001-consume-released-packy-tooling.md).
The review also selected supported commands in the main CLI, Packy ownership
of internal tests, and Catalog content checks through the released binary.
Acquisition will download, verify, and cache the pinned release automatically
using the same mechanism locally and in CI; an unavailable uncached artifact
must fail without falling back to another installed version.
The Catalog will keep one declarative file with release version, source commit,
and per-platform artifact checksums, reviewed through pull requests and consumed
by local execution and CI. Packy must run the same functional contract cases
against all four release binaries before release publication. Catalog content
checks will run against the pinned binary in Linux CI, with local execution
supported on all four platforms.
Released binaries will expose their embedded version and source commit through
a supported structured interface. The Catalog will compare this identity with
its declaration after artifact verification; snapshot construction will use
the executable's identity automatically. The new commands will offer readable
text by default and `--json` with a versioned schema, identifiable results and
errors, exit zero for success, and nonzero for failure.
All nine design questions were accepted by the user. Exact command names,
schemas, declaration format, and cache layout are implementation choices within
those constraints. The research and ADR do not claim that the changes have
been implemented.

## Follow-up evidence: platform execution and binary identity

Packy CI and release preparation run the source tests on `ubuntu-latest`, with
no runtime matrix. Release construction cross-compiles all four targets;
artifact validation checks every archive's contents and digest but executes
only the host binary's `--version`. The later `macos-15` Homebrew smoke also
checks only `--version`. These checks do not establish validation/build/publish
behavior on all four shipped binaries. [Packy CI][packy-ci],
[release workflow][release-workflow], [packaging][packaging], [artifact checks][artifact-checks].

The supported CLI version output contains only `version.Value`, whose default
is `dev` and which release builds override with `-ldflags`. There is no public
revision-reporting field in that command. The current builder separately accepts
`--builder`, rather than deriving a verified revision from its executable.
[Version variable][version-variable], [CLI version command][cli], [builder][build].

Direct inspection of the official Darwin arm64 archive, downloaded into a
temporary directory and removed afterward, found Go build metadata with
`vcs.revision=b4cf72d892570c1fb26571c434f2407bb0728bd3`,
`vcs.modified=true`, and module version `v0.2.26+dirty`.
`go version -m` read the extracted executable without running it. The downloaded
archive SHA-256 was
`b392b994a0775c7d53100e02886013ab10959b40d1ac39620e05c8d7bd941402`,
matching the API's asset digest. This proves embedded revision metadata exists
in that asset; it does not establish why the build was marked dirty, nor a
supported machine interface or equivalent metadata in the other three assets.
[Inspected release asset][inspected-asset], [release API][release-api].

Existing machine interfaces use command-specific `--json` flags and versioned
reports, including `schema_version` and `report`; some lifecycle errors also
emit structured failures. The main executable prints returned errors to stderr
and exits 1, whereas the internal validator distinguishes usage errors (2)
from validation/runtime errors (1). Promoting tools into the main CLI therefore
requires an explicit output/exit-status contract; there is no universal current
error envelope to inherit unchanged. [Doctor report][doctor-report],
[lifecycle error output][lifecycle-output], [main entry point][main], [validator][validate].

## Follow-up: supporting release available

As of 2026-10-10 (America/Bogota), the supporting immutable
[Packy v0.2.27 release](https://github.com/yersonargotev/packy/releases/tag/v0.2.27)
is published from source/tag commit
`1b8d04ddee510b24adcb12906914240bd7063aa6`. GitHub's release API reports
`immutable: true`, `draft: false`, and `prerelease: false`; the tag resolves
directly to that commit. [Release API][supporting-release-api],
[tag API][supporting-tag-api].

[Packy #834 delivery evidence](https://github.com/yersonargotev/packy/issues/834#issuecomment-6104158748)
records the four published archive checksums and the native Darwin/Linux
amd64/arm64 contract results: the same 97 passing tests/subtests on each staged
release binary, with matching version, source commit, and checksum manifests.
The evidence includes the retained per-platform reports and exact tested bundle.
These are the release gate's reported results, not a new four-platform test
performed for this documentation change.

The released [command documentation][released-commands] covers identity,
validation, snapshot construction, publication, and isolated candidate
acceptance. Its [versioned CLI JSON schemas][released-schemas] define the
machine interfaces used for adoption.

This completes the external release prerequisite for
[Catalog #54](https://github.com/yersonargotev/packy-catalog/issues/54).
Catalog adoption remains separate work: its current validator, builder,
publisher, and opt-in probes still use the source-based v0.2.26 workflow.
The earlier sections retain the observations and limitations of the inspected
v0.2.26 revision; they do not describe the newly released implementation.

[supporting-release-api]: https://api.github.com/repos/yersonargotev/packy/releases/tags/v0.2.27
[supporting-tag-api]: https://api.github.com/repos/yersonargotev/packy/git/ref/tags/v0.2.27
[released-commands]: https://github.com/yersonargotev/packy/blob/1b8d04ddee510b24adcb12906914240bd7063aa6/docs/catalog-project.md
[released-schemas]: https://github.com/yersonargotev/packy/tree/1b8d04ddee510b24adcb12906914240bd7063aa6/schemas/cli/v1

[packy-ci]: https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/.github/workflows/ci.yml
[version-variable]: https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/internal/version/version.go
[inspected-asset]: https://github.com/yersonargotev/packy/releases/download/v0.2.26/packy_v0.2.26_darwin_arm64.tar.gz
[doctor-report]: https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/internal/cli/setup_health_adapter.go#L45
[lifecycle-output]: https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/internal/cli/pack.go#L1019
[main]: https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/cmd/packy/main.go#L12
[release-api]: https://api.github.com/repos/yersonargotev/packy/releases/latest
[tag-api]: https://api.github.com/repos/yersonargotev/packy/git/ref/tags/v0.2.26
[adr39]: https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/docs/adr/0039-publish-an-independent-canonical-pack-catalog.md
[adr40]: https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/docs/adr/0040-adopt-pack-local-catalog-layout.md
[context]: https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/CONTEXT.md
[wrapper]: https://github.com/yersonargotev/packy-catalog/blob/679587d355af659c8b5fdcd45138c9daebf0de3e/scripts/validate.sh
[validate]: https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/internal/tools/catalogvalidate/main.go
[build]: https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/internal/tools/catalogsnapshot/main.go
[publish]: https://github.com/yersonargotev/packy-catalog/blob/679587d355af659c8b5fdcd45138c9daebf0de3e/.github/workflows/publish.yml
[probes]: https://github.com/yersonargotev/packy-catalog/blob/679587d355af659c8b5fdcd45138c9daebf0de3e/scripts/probes/README.md
[ci]: https://github.com/yersonargotev/packy-catalog/blob/679587d355af659c8b5fdcd45138c9daebf0de3e/.github/workflows/validate.yml
[guard]: https://github.com/yersonargotev/packy-catalog/blob/679587d355af659c8b5fdcd45138c9daebf0de3e/scripts/validate-publication-workflows.sh
[readme]: https://github.com/yersonargotev/packy-catalog/blob/679587d355af659c8b5fdcd45138c9daebf0de3e/README.md
[cli]: https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/internal/cli/root.go
[packaging]: https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/scripts/build-release-artifacts.sh
[artifact-checks]: https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/scripts/validate-release-artifacts.sh
[origins]: https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/internal/tools/catalogorigin/resolver.go
[catalog-validation]: https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/internal/cataloglayout/catalog_validator.go
[snapshot]: https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/internal/cataloglayout/catalog_snapshot.go
[snapshot-tests]: https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/internal/cataloglayout/catalog_snapshot_test.go
[publisher]: https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/scripts/publish-catalog-snapshot.sh
[release-workflow]: https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/.github/workflows/release.yml
