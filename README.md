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
- Ponytail
- pstack
- Thermos
- Warp
- Web

Argote includes the Codex-only `issue-delivery` skill, adapted from Matt
Pocock's implementation workflow. It requires the `tdd` and `code-review`
skills from Matty at runtime. The standalone Engram and Issue Delivery Packs
are no longer part of this catalog.

Independent upstream products keep their own repositories and release
lifecycles. A pinned `origin` in a Pack manifest identifies the exact upstream
commit from which reviewed resources were copied or adapted.

## Layout

Each Pack is a self-contained module under `packs/<pack-id>/`. Its `pack.json`
and every declared resource path are relative to that Pack root. The complete
catalog is discovered from those directories; there is no separately
maintained registry and Packs cannot reference files owned by another Pack.

Catalog content is inert data. Validation reads manifests and files, checks
their declared closures and exact-copy provenance, and evaluates Packy's typed
capability vocabulary without executing catalog content.

## Validate

Use the released Packy v0.2.26 checkout at
`b4cf72d892570c1fb26571c434f2407bb0728bd3`, matching CI and publication.
See [schema v3 adoption](docs/schema-v3-adoption.md) before upgrading existing
installations. Validate with:

```sh
PACKY_VALIDATOR_ROOT=../packy ./scripts/validate.sh
```

To enforce independent Pack version changes against another Catalog Project
checkout, pass that checkout as the only argument:

```sh
PACKY_VALIDATOR_ROOT=../packy ./scripts/validate.sh ../packy-catalog-main
```

When a Pack's manifest contract or referenced bytes change, its version must
increase. Packs whose content is unchanged must retain their versions. A new
Pack may start at any valid SemVer. Pull-request CI applies the same rules
against the exact base commit.

## Claude

Claude 1.0.0 provides `eli5` and `html-plan` for Claude Code, Codex, and
OpenCode, adapted from the community repository at
`f60f0454df3045f724c43c6346ec80bdcc3472b2`. `html-plan` includes its HTML
runtime and requires Node.js. This edition includes the two self-contained
skills, with their notices; the upstream marketplace and service-dependent
plugins are outside its scope. See [scope, adaptations, and installation](docs/research/claude.md).
No Packy engine changes are required.

## Ponytail

Ponytail 1.0.0 provides six skills and an independently selectable persistent
instruction, adapted from upstream commit
`c982cd411abb53323c4baa1baa3c2f020b8d0b08` (plugin version 4.10.3).
It supports Codex, Claude Code, and OpenCode project installation using the
existing Packy v0.2.26 engine. No engine changes are required.

After this catalog revision is published, refresh catalog availability and
install from the target Git project. The complete Pack is suitable when no
other Pack owns the host's instruction file:

```sh
packy catalog refresh
packy install ponytail --surface codex --dry-run
packy install ponytail --surface codex
```

The complete Pack installs all six skills and permanent guidance. For skills
without permanent guidance, repeat `--resource` for the desired skill roots:

```sh
packy install ponytail --surface codex \
  --resource skill:ponytail --resource skill:ponytail-review --dry-run
```

Remove `--dry-run` after reviewing the preview. The standalone instruction is
`instruction:ponytail-guidance`; it contributes to `AGENTS.md` on Codex/OpenCode
and `CLAUDE.md` on Claude. It remains in effect when a conversational skill mode
ends. Packy v0.2.26 blocks two different Packs from owning the same instruction
file, even with distinct block identifiers. If Argote or another Pack already
manages that file, select only Ponytail skills. Existing unmanaged instruction
text is preserved. Supporting independent Pack blocks in the same file would
require a separate engine change.

This edition does not include lifecycle hooks, statusline integration, MCP,
or mode configuration files. Skill levels are conversational. The main skill,
help, benchmark summary, and persistent instruction are maintained adaptations;
review, audit, debt, and the MIT notice retain exact upstream bytes. The benchmark
skill reports the newer upstream agentic results with their limitations, not
claimed savings for the Packy adaptation or the current project.

The [Ponytail installation probe](scripts/probes/README.md#ponytail-project-installation)
checks resource selection, notices, preservation, and the shared-file limit on
all three hosts.

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
publish it, and that job never checks out or executes Catalog Project content.

Repository settings enable native release immutability. The publisher creates a
draft, uploads and verifies the complete asset set, publishes it, and requires
GitHub to report the result as immutable. Retrying the same commit accepts only
the same target and byte-identical assets. An interrupted draft can upload
missing expected assets; a published mutable release, unexpected asset, or
changed byte is rejected.
