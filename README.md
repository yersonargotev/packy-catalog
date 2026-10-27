# Packy Catalog

This is the canonical Catalog Project for Packy's reviewed Packs. It authors
the manifests, resources, adaptations, provenance, and notices for:

- Addy
- Argote
- Claude
- Emil
- HumanLayer
- Matty
- Orchestrate
- Packy
- Ponytail
- pstack
- Thermos
- Warp
- Web

Argote includes the `issue-delivery` skill, adapted from Matt
Pocock's implementation workflow. It requires the `tdd` and `code-review`
skills from Matty at runtime. The standalone Engram and Issue Delivery Packs
are no longer part of this catalog.

Independent upstream products keep their own repositories and release
lifecycles. A pinned `origin` in a Pack manifest identifies the exact upstream
commit from which reviewed resources were copied or adapted.

[Resource ownership terminology](GLOSSARY.md) distinguishes Catalog Resources,
Catalog Adaptations, Upstream Resources, and Installed Resources.

## Layout

Each Pack is a self-contained module under `packs/<pack-id>/`. Its `pack.json`
and every declared resource path are relative to that Pack root. The complete
catalog is discovered from those directories; there is no separately
maintained registry and Packs cannot reference files owned by another Pack.

Catalog content is inert data. Validation reads manifests and files, checks
their declared closures and exact-copy provenance, and evaluates Packy's typed
capability vocabulary without executing catalog content.

## Validate

Use Python 3.9+, `curl`, Git, and the workflow parser installed with
`python3 -m pip install -r requirements-tooling.txt`. Validate with:

```sh
./scripts/validate.sh
```

The entry point automatically acquires the exact immutable Packy release in
[`packy-release.json`](packy-release.json), verifies its archive checksum and
embedded identity, and reuses verified archives from a local cache. It needs
neither Go, a neighboring Packy checkout, nor a global Packy installation.
GitHub access is needed on first acquisition and for upstream origin validation;
a warm tool cache does not make content validation offline.

To enforce independent Pack version changes against another Catalog Project
checkout, pass that checkout as the baseline. Add `--json` for the versioned
validation report:

```sh
./scripts/validate.sh ../packy-catalog-main --json
```

[Catalog tooling](docs/catalog-tooling.md) describes cache recovery, prerequisites,
contract tests, snapshot commands, and reviewed release upgrades.
The [schema v3 adoption record](docs/schema-v3-adoption.md) describes an earlier
generation; follow the current handoff below for this incompatible transition.

When a Pack's manifest contract or referenced bytes change, its version must
increase. Packs whose content is unchanged must retain their versions. A new
Pack may start at any valid SemVer. Pull-request CI applies the same rules
against the exact base commit.

## Use the catalog

The compatible engine provides two surface conventions: `agents` for shared
Agents instructions and skills, and `claude` for Claude instructions and skills.
Agents is a convention, not a promise that every client supports a workflow's
runtime assumptions. Custom roles require an explicitly reviewed client and
scope; select `--client codex` when a supported Agents workflow requires Codex
roles. The retired `codex` and `opencode` surface values are rejected.

Before replacing an older binary, follow the released engine's
[adoption and previous-binary handoff guide](https://github.com/yersonargotev/packy/blob/v0.2.32/docs/catalog-adoption.md).
Wait for a complete compatible catalog snapshot, inventory every affected
receipt, and remove old projections using the previous binary. Preserve
unrelated files, credentials, client settings, and retained content referenced
by receipts. There is no automatic migration.

Acquire the catalog explicitly with `packy init`, or select a newer complete
snapshot with `packy catalog refresh`. Refresh does not update installations;
existing receipts retain their snapshot. A failed refresh leaves the previous
valid selection usable. Preview each desired installation before applying it:

```sh
packy catalog refresh
packy install ponytail --surface agents --dry-run
packy install ponytail --surface agents
```

Select specific resource roots with `--resource` when the whole Pack is not
wanted. For example, Ponytail's persistent `instruction:ponytail-guidance` is
independent of its skills. Agents instructions apply at project scope; Claude
uses its native instruction convention. Ownership and drift checks protect
existing content. Consult the Pack's metadata and preview for supported
surfaces, scopes, dependencies, and prerequisites.

The catalog-authored Packy CLI skill supports [on-demand access](docs/packy-cli.md)
without installation of the retrieved Pack. Qualified identities and the
initiating surface and snapshot carry through nested access; acquisition and
refresh are never implicit.

## Export a plugin

Export is separate from installation and reads a retained local snapshot:

```sh
packy export ponytail --surface agents --output ./ponytail-plugin --json
packy export ponytail --surface claude --skill ponytail --output ./ponytail-claude
```

Agents exports Agent Plugins and Claude exports a Claude plugin. The default
selects skills explicitly reviewed for the chosen format; an explicit selection
and its required closure must all be compatible or the whole export fails. The
output parent must exist and the destination must be new or empty. Reports
identify the snapshot, selection, closure, and unverified prerequisites.
Export does not install or enable a plugin, register custom roles, change client
settings, or execute its content. A valid package does not establish client
loading, authorization, or model-backed usability. See the released engine's
[plugin export guide](https://github.com/yersonargotev/packy/blob/v0.2.32/docs/plugin-export.md)
for format and prerequisite details.

## Investigate a new Pack

For a reviewed local Claude plugin marketplace checkout, use the
[bounded marketplace inspector](docs/marketplace-inspection.md) to classify
sources and locate focused follow-up evidence. Summaries do not replace source
review or decide which resources belong in a Pack.

## Update a Pack

Select an immutable upstream release or full commit and record its full commit
ID. Treat the Pack manifest and its declared resource closure as the reviewed
contract; compare them completely before changing catalog files.

Use Packy's transactional Upstream Refresh only when the complete comparison
changes no manifest data except the Pack version and the selected origin's
commit or optional revision, and changes no closure topology except resource
bytes at already declared `exact-copy` paths:

```sh
packy catalog upstream-refresh <pack-id> \
  --project . \
  --origin-id <origin-id> \
  --commit <full-commit> \
  --version <new-pack-version>
```

Treat every other manifest or closure change as a contract migration. Reconcile
the manifest and closure together, including additions, removals, moved paths,
adaptations, and catalog-authored changes. Preserve the upstream author's
declared provenance unless the catalog resource is a byte-exact copy of a newly
pinned path. Pack versions are catalog-owned: choose a strictly greater SemVer
that represents the reviewed compatibility change; matching the upstream
version is useful but not required. The full commit is authoritative;
`upstream-refresh` clears the optional human-readable `revision` label.

Finish either route by reviewing the complete Pack closure, validating against
a clean baseline checkout, and confirming that unrelated Pack versions remain
unchanged. The update is complete only when the provenance resolves, exact-copy
resources match byte-for-byte, the baseline validation passes, and the Git diff
contains only the intended contract and closure changes.

## Publish

Every successful validation of a reviewed merge to protected `main`
automatically publishes one complete immutable Catalog Snapshot. No second
release approval or Packy promotion pull request is required.

The release tag is `catalog-<full-source-commit>` and contains exactly:

- `catalog-snapshot.tar.gz`, with the generated `catalog-index.json` and every
  declared Pack closure under `packs/<pack-id>/`; and
- `SHA256SUMS`, with the archive's SHA-256 digest.

The index identifies the exact Catalog Project and Packy builder commits, the
catalog digest, and each Pack's version, manifest digest, closure digest, and
ordered path/mode/content-digest index. Publication also records GitHub build
provenance for the archive. Verify downloaded bytes with:

```sh
shasum -a 256 -c SHA256SUMS
gh attestation verify catalog-snapshot.tar.gz \
  --repo yersonargotev/packy-catalog
gh release verify catalog-<full-source-commit> \
  --repo yersonargotev/packy-catalog
```

Pull-request validation has read-only repository permission and no publication
credentials. The publication workflow starts only after the separate
validation workflow succeeds for an official `main` push. Its read-only job
builds and retains the validated artifact; only the final job can attest and
publish it, and that job reads the reviewed release declaration at the validated commit,
independently acquires and verifies the released publisher, and never executes
Catalog Project scripts or resources.

Repository settings enable native release immutability. The publisher creates a
draft, uploads and verifies the complete asset set, publishes it, and requires
GitHub to report the result as immutable. Retrying the same commit accepts only
the same target and byte-identical assets. An interrupted draft can upload
missing expected assets; a published mutable release, unexpected asset, or
changed byte is rejected.
