# Packy Catalog

This is the canonical Catalog Project for Packy's reviewed Packs. It authors
the manifests, resources, adaptations, provenance, and notices for:

- Addy
- Argote
- Engram
- Issue Delivery
- Matty
- Orchestrate
- pstack

Independent upstream products keep their own repositories and release
lifecycles. A pinned `origin` in a Pack manifest identifies the exact upstream
commit from which reviewed resources were copied or adapted.

## Layout

Pack manifests live at `bundle/packs/<pack-id>/pack.json`. Their resource paths
are relative to `bundle/`. The complete catalog is discovered from those
manifest paths; there is no separately maintained registry.

Catalog content is inert data. Validation reads manifests and files, checks
their declared closures and exact-copy provenance, and evaluates Packy's typed
capability vocabulary without executing catalog content.

## Validate

Use a local Packy checkout containing the Catalog Project validator:

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

## Publish

Every successful validation of a reviewed merge to protected `main`
automatically publishes one complete immutable Catalog Snapshot. No second
release approval or Packy promotion pull request is required.

The release tag is `catalog-<full-source-commit>` and contains exactly:

- `catalog-snapshot.tar.gz`, with the generated `catalog-index.json` and every
  declared Pack closure under `bundle/`; and
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
