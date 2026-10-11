---
status: accepted
---

# Consume released Packy tooling throughout the Catalog workflow

The Catalog Project must be able to complete its acceptance and publication
workflow using released Packy tooling without a Packy source checkout or a
sibling repository. This includes addressing the publisher and lifecycle
probes that currently depend on Packy source, because distributing validation
and snapshot construction alone would leave that dependency in the workflow.

Local execution and CI must use the same exact Packy release, with verified
artifact checksums for each supported platform and functionally equivalent
results for equivalent inputs. Cross-platform byte identity of snapshots is
not an additional acceptance requirement for this change; existing snapshot
determinism and publication integrity requirements remain in force.

Packy will expose validation, snapshot construction, and publication as
supported commands in its main CLI, reusing the existing binary distribution
and release version. Separate executables would introduce an additional
distribution contract without a demonstrated need.

Tests requiring access to Packy internals belong in Packy. The Catalog Project
will verify its content by invoking the released binary through supported
interfaces. This preserves coverage at the appropriate ownership boundary
without copying Catalog tests into a Packy source checkout.

The confirmed acceptance seam includes an explicit, supported authoring-only
route for the real released binary to exercise a local candidate snapshot in
a disposable workspace. Candidate input must remain distinct from an official
Catalog Publication, preserve normal publisher verification, and avoid
personal/global state mutation. This does not introduce general custom catalog
sources or let JSON output substitute for required user consent.

Catalog entry points will automatically download, verify, and cache the exact
required CLI release, using the same acquisition mechanism locally and in CI.
If the required artifact is unavailable in the cache and cannot be downloaded,
execution must fail clearly; it must not substitute another installed version.

A single declarative file in the Catalog Project will pin the exact Packy
release version, source commit, and artifact checksums for each supported
platform. Local execution and CI will consume that file; workflows must not
duplicate the tool version. Changes to this declaration are reviewed through
pull requests.

Packy must run the same functional contract cases against each of the four
release binaries (Darwin/Linux, amd64/arm64) before publishing a release.
Cross-compilation and version smoke checks alone do not satisfy this gate.
The Catalog Project will check its content with the pinned binary in Linux CI
while retaining local execution on all four platforms. This places evidence
for the tools' cross-platform behavior with Packy and content verification
with the Catalog Project.

Released binaries will embed their Packy version and source commit and expose
that identity through a supported structured interface. After verifying the
artifact checksum, the Catalog will check this identity against its declaration.
Snapshot construction will derive the builder identity from the executable
rather than accept an independently supplied builder label, preventing the
caller from misidentifying the tool used to build a snapshot.

The new commands will provide human-readable output by default and a supported
`--json` interface with a versioned schema and identifiable results and errors.
Success returns exit code zero; failures return a nonzero exit code. Catalog
automation and contract tests can inspect structured results without depending
on the wording of human-facing messages.

Existing validation semantics, baseline version checks, snapshot format and
integrity guarantees, and publication trust boundaries remain requirements.
In particular, the write-authorized publication job must not execute Catalog
Project content. Removing the Packy source prerequisite does not promise
offline validation of upstream origins.

The design review is complete. Detailed command names, JSON schemas, and
declaration/cache layout are implementation choices within these constraints.
Packy must publish the supporting CLI release before the Catalog can migrate
to it. As of 2026-10-10 (America/Bogota), immutable
[Packy v0.2.27](https://github.com/yersonargotev/packy/releases/tag/v0.2.27)
has satisfied that prerequisite through
[Packy #834](https://github.com/yersonargotev/packy/issues/834#issuecomment-6104158748).
[Catalog #54](https://github.com/yersonargotev/packy-catalog/issues/54) tracks
adoption; the Catalog validation and publication workflows still use v0.2.26.

Evidence and alternatives: [Versioned Catalog tooling research](../research/versioned-catalog-tooling.md).

Approved specifications and child tickets are published under
[Packy #829](https://github.com/yersonargotev/packy/issues/829) and
[Catalog #53](https://github.com/yersonargotev/packy-catalog/issues/53).
The Catalog adoption ticket declares the Packy release ticket as its
prerequisite; that ticket is now completed. Release availability does not
itself migrate Catalog entry points or lifecycle probes.
