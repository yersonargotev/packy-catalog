# Catalog schema v3 adoption

The original schema v3 cut pinned its validator, snapshot builder, and trusted
publisher to Packy v0.2.26, commit `b4cf72d892570c1fb26571c434f2407bb0728bd3`.
The engine release is immutable (GitHub release 402053995). This catalog cut
requires that engine or a compatible later release; earlier engines cannot
consume schema v3 snapshots. Current authoring and publication tooling is
declared in [`packy-release.json`](../packy-release.json).

## Version decisions

All ten manifests change their incompatible schema contract. Each advances to
the next major version, with resource bytes, modes, bindings, dependencies,
origins, and notices preserved:

| Pack | Before | After |
| --- | --- | --- |
| Addy | 3.0.0 | 4.0.0 |
| Argote | 3.0.0 | 4.0.0 |
| Emil | 1.0.0 | 2.0.0 |
| HumanLayer | 2.0.0 | 3.0.0 |
| Matty | 3.0.0 | 4.0.0 |
| Orchestrate | 2.0.0 | 3.0.0 |
| pstack | 2.2.0 | 3.0.0 |
| Thermos | 1.0.0 | 2.0.0 |
| Warp | 1.0.0 | 2.0.0 |
| Web | 2.0.0 | 3.0.0 |

The v3 engine deliberately has no v2 reader. For the first v3 transition (PR #33), a temporary validation check
compared the clean v2 baseline's entire Pack inventory with the candidate,
requiring identical file paths, modes, and bytes except for manifest schema and
exact next-major versions. It requires every other manifest field to match.
The complete candidate also passed the released engine's schema, origin,
closure, fitness, and legal validation. This check does not convert or install
old content. The temporary cut check was removed after that merge. All subsequent baselines
use the engine's normal v3 version validator.

## Operator handoff

Keep the previous engine binary, immutable snapshots, and referenced source
content. With that previous engine, inventory global activations and each Git
worktree's project installations. Preview and deactivate global and personal
project activations, then preview and uninstall affected project installations.
Resolve drift through the old engine before proceeding. Preserve personal data,
credentials, Memory, unmanaged files, and installations belonging to other hosts.
Do not move or delete `.agents/skills` wholesale.

Once the compatible engine and catalog snapshot have both been published,
upgrade Packy, run `packy init`, inspect `packy list`, and explicitly preview and
reinstall/reactivate the desired Packs and surfaces. There is no automatic
conversion or old-root cleanup. Retain old content until no receipt references
it. Follow the pinned engine's [complete adoption procedure](https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/docs/catalog-adoption.md).

OpenCode now uses its native skill roots, but compatibility discovery can still
prevent divergent same-name skills coexisting with Codex or Claude. An
environment flag on one launch does not bypass Packy's discovery guard. See the
[verified discovery limits](https://github.com/yersonargotev/packy/blob/b4cf72d892570c1fb26571c434f2407bb0728bd3/docs/skill-discovery.md).

## Reproducible acceptance probes

`scripts/probes/catalog_adoption_test.go` is a test-only overlay for the pinned
engine's `internal/cli` package, run in disposable engine worktrees. It consumes
complete snapshot assets through an injected local Source and uses disposable
homes and projects. It does not modify the user's installations or test remote
attestation verification. The production publication workflow retains its
separate attestation and immutable-release checks.

Set `PROBE_SNAPSHOT` to an asset directory and `PROBE_SOURCE_COMMIT` to its
index source commit, then run `go test ./internal/cli -run '^TestCatalogAdoption$'
-v -count=1`. Under v0.2.26 it acquires the full catalog and installs/uninstalls
common Emil resources for Codex, Claude, and OpenCode. Under v0.2.25, start with
the published v2 snapshot, additionally set `PROBE_REJECT_SNAPSHOT` and
`PROBE_REJECT_COMMIT` to the v3 candidate, and verify rejection preserves the
selection bytes and leaves the prior catalog readable.

### Executed evidence (2026-10-02)

- Full v0.2.26 validation: 10 Packs, 552 fitness rows; all origins and exact
  copies passed. PR validation also passed against the clean v2 base.
- Strict cut comparison passed. Independent negative cases rejected resource
  drift, identity changes, wrong schema, and a non-major version increase.
- Two independent complete builds were byte-identical, including `SHA256SUMS`.
  Archive SHA-256: `9c977bae05bf1a1b565a06c856166a4e10c12d47ec9364519a33399d64277cc3`.
  These local prepublication probes used source label
  `76b8b8a3013cf95850ba18d433fbe16b60f77e4f`; they are not official releases.
  Publication rebuilds from the actual reviewed merge SHA.
- The v0.2.26 CLI probe acquired the complete v3 snapshot and successfully
  installed/uninstalled Emil's common resources on all three project surfaces.
- The v0.2.25 CLI probe acquired the published v2 baseline, rejected the v3
  snapshot with `Catalog Snapshot index schema_version must be 2`, preserved
  the previous selection byte for byte, and could still list the old catalog.
- The read-only PR / isolated write-authorized publisher boundary check passed.

These tests establish catalog acquisition and lifecycle behavior, not model-backed
execution of all skills. pstack host adaptations and runtime evidence belong to
catalog issue #32.
