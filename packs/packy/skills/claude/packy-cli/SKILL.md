---
name: packy-cli
description: Discover and obtain a requested Catalog skill through Packy, including Pack-qualified requests and ambiguous skill names.
---

# Packy CLI

Use the Packy CLI as a resource provider. You read the returned instructions and
follow the selected procedure; retrieval itself does not execute that procedure.
This definition is for Claude Code. Pass `--surface claude` explicitly on every
host-specific inspection and retrieval, including nested calls.

## Select a qualified identity

1. If the request already identifies `<pack>:<skill>` (for example `matty:retro`),
   proceed directly to **Obtain and read** with that identity. Retrieval checks
   reviewed compatibility; no prior `list` or `show` is needed.
2. Otherwise, discover only what is missing. If the Pack is unknown, first run
   `packy list --json`. Capture each relevant Pack's inspection in writable
   scratch space, then filter it before displaying results. With a known skill
   name, for example using `jq`:

   ```sh
   packy show <pack> --surface claude --json > <scratch>/pack.json
   jq --arg name "<skill>" '.skills[] | select(.qualified_skill | endswith(":" + $name))' <scratch>/pack.json
   ```

   If no exact name matches or the request needs description matching, display
   only identity/description summaries with
   `jq '.skills[] | {qualified_skill, description}' <scratch>/pack.json`, then
   inspect complete metadata for the matching candidates. Expand to other Packs
   when the known Pack is unresolved or has no match. Use another local JSON
   reader if `jq` is unavailable; keep the full captured report out of context.
   Match the request against qualified identities, effective descriptions,
   reviewed compatibility, dependencies, and known prerequisites. Preserve each
   `<pack>:<skill>` identity throughout selection.
3. Select a unique match directly. When multiple skills match, ask the user to
   choose among the qualified candidates and explain their relevant differences.
   Installed state, native aliases, and modified installed copies do not rank or
   replace Catalog Resources.

Complete when one qualified identity is ready for retrieval, or report the
unresolved ambiguity.

## Obtain and read

Run:

```sh
packy get skill <pack>:<skill> --surface claude --json
```

Require a successful versioned `skill-access` report with `result: "prepared"`
and the requested `qualified_skill` and `surface`. Retrieval must confirm reviewed
on-demand compatibility for this host; a native binding alone is insufficient.
If incompatible, explain the reported reason and request a reviewed adaptation.
Retain `qualified_skill`, `pack_version`, `surface`, `snapshot_id`,
`entry_document`, `resource_root`,
`dependencies`, and `prerequisites`. Read the returned entry document first, then
only the supporting files needed by the procedure, resolving relative references
from their document locations within the prepared resource tree. Prepared
same-Pack and cross-Pack dependencies retain their qualified owners and versions;
reviewed access references point to their usable entry documents.

For every nested request, keep the initiating host and snapshot:

```sh
packy get skill <dependency-pack>:<dependency-skill> --surface claude --snapshot <snapshot_id> --json
```

A new independent request uses the selected local snapshot. Explicit refresh does
not change an active procedure's snapshot. Missing retained content must fail;
restore that exact retained revision instead of substituting a newer one.
Snapshots and prepared paths have no automatic expiry or cleanup. Manual removal
can invalidate them; preserve them while a procedure is using them.

Complete when the entry and needed supporting/dependency documents are readable
and the initiating immutable identity is available for nested calls.

## Follow the procedure

Check reported prerequisites before execution: declarations remain unverified,
and an empty list does not prove runtime readiness. Missing content runtimes do
not prevent obtaining instructions. Preserve the selected skill's approvals,
domain assumptions, tool requirements, stopping rules, and retirement behavior.
Resource availability does not authorize external effects or prove workflow success.

Choose the user's intended target directory explicitly. Keep immutable resource
locations separate from that target and from writable scratch/output locations.
Run helpers with their documented target argument or environment, and place
intermediate files and script dependencies in separate writable scratch space.
Preserve Catalog sources and installed copies. Native invocation continues using
its installed definition, including local modifications.

## Acquisition and errors

Discovery and retrieval use local content, work outside Git after acquisition,
and do not implicitly refresh, download, activate/install requested Packs, modify
target projects, execute scripts, or install runtimes/dependencies. If no local
catalog exists, explain explicit acquisition with `packy init` or
`packy catalog refresh`; perform acquisition only when authorized. Surface or
identity errors require correcting the selection, not guessing another host or
revision. Read `get skill` structured errors and discovery's stderr/nonzero exit.
For `invalid_identity` or `unknown_skill`, return to focused discovery: inspect
the named Pack first, using `list` only if the Pack is unknown or unresolved.
Preserve the initiating host and `--snapshot` on any nested retrieval retry;
discovery describes the currently selected catalog, not an older pinned snapshot.
If Packy itself is unavailable, explain that the CLI must be installed explicitly;
do not automatically provision it or any content runtime.
