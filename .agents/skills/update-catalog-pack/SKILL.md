---
name: update-catalog-pack
description: Update an existing Pack in this Packy Catalog Project from a reviewed upstream revision or catalog-authored change. Use for bundle/packs maintenance; not for updating installed Packs in user projects.
---

# Update a Catalog Pack

Read the target manifest and the **Update a Pack** section of
[`README.md`](../../../README.md). Anchor the work on a clean Git baseline.
Resolve any upstream tag or branch to a full commit and inspect the target Pack
contract and declared closure before changing catalog files. Treat maintained
source, the selected commit, and `packy catalog upstream-refresh --help` as
authoritative over remembered commands.

Classify the contract diff using the README's closed **Refresh** rule; every
delta outside that allowance is a **Migration**. For a Refresh, run Packy's
transactional `catalog upstream-refresh` with the explicit Pack, origin, commit,
project, and version values. For a Migration, reconcile the manifest and its
complete declared closure as one reviewed change.

Review every changed file in the Pack closure, including notices and agent
metadata. Validate the finished project against a clean checkout of the target
branch using the repository's validation command. Finish only when all origins
resolve, exact copies match, the complete catalog passes, baseline version
checks pass, unrelated Pack versions remain unchanged, and the Git diff
contains only the intended contract and closure changes.

Report the old and new Pack versions, upstream commit when applicable, chosen
route, changed resources, any intentionally preserved adaptation, and the exact
validation evidence. Leave commit, push, and publication to the user's explicit
request.
