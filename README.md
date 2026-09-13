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

Catalog Snapshot publication is intentionally separate from this validation
flow.
