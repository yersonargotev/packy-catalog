# On-demand skill access

Status: accepted design. The user confirmed all sixteen decisions and the final
shared understanding on 2026-10-23. This document records agreed requirements and
constraints from the dated interview. The engine is now released; Catalog delivery
proceeds through [#90](https://github.com/yersonargotev/packy-catalog/issues/90)
and its follow-up adaptations, rather than claiming the whole initiative is complete.

## Agreed requirements

- A single Packy CLI Skill teaches an agent how to discover and obtain skills.
  It describes discovery rather than embedding a static package inventory.
- On-demand Skill Access coexists with traditional skill installation.
- Permanent instructions retain their installation model. The initial on-demand
  scope is skills.
- Packy provides resources and the paths needed to use them. The agent reads
  instructions and follows the procedure; Packy does not execute skill workflows.
- A skill includes its supporting files, such as references and scripts, rather
  than only its entry document.
- Discovery resolves a unique match automatically. Multiple matching skills
  require the agent to ask the user which one to use.
- Pack-qualified identifiers distinguish skills from different Packs. The command
  interface is `packy get skill <pack>:<skill>`, with human-readable output and a
  `--json` option.
- Catalog skills may receive explicit, reviewed adaptations for on-demand use,
  including declared dependencies rather than inference from arbitrary prose.
- Access through the Packy CLI Skill resolves catalog content, even if the project
  has an installed or locally modified copy of the same skill. Native invocation
  continues to use the installed copy.
- A skill procedure and its nested skill dependencies use the same immutable
  Catalog Snapshot. Refreshing the catalog does not change that procedure's
  resources; a new independent request may use the newly selected snapshot.
- Dependencies may cross Pack boundaries through explicit Pack-qualified
  references. Obtaining a skill prepares its dependencies without installing
  their Packs.
- Initial compatibility coverage includes the skills in Matty, pstack, and Warp.
  This is the selected initial scope, rather than an arbitrary sample of skills.
  Reviewed adaptations must address supporting files, scripts, and nested calls.
- Initial host coverage is Codex (`.agents/skills`) and Claude Code
  (`.claude/skills`). OpenCode is outside the initial on-demand delivery scope;
  its existing installation behavior remains supported.
- The Packy CLI Skill is personal/user-scoped by default, with project-scoped
  installation available for shared project configuration. Personal roots are
  `~/.agents/skills` for Codex and `~/.claude/skills` for Claude Code.
- Each host's Packy CLI Skill passes its host identity explicitly, so retrieval
  selects the appropriate host-specific body.
- Retrieval uses the local catalog without automatically checking the network.
  `packy catalog refresh` remains an explicit action. If no local catalog exists,
  retrieval explains how to acquire one.
- Catalog resources remain immutable. Scripts operate on the intended target
  directory, with separate scratch space for dependencies and intermediate files.
  Retrieval itself does not modify the target project; subsequent agent actions
  follow the selected skill's procedure.
- Retrieval and skills that do not require Git must work outside Git repositories.
- Missing runtimes do not prevent obtaining skill resources. Packy reports known
  prerequisites; the agent checks them before running a script. Packy does not
  automatically install runtimes or script dependencies.
- The retrieval result provides the qualified identity, selected host, immutable
  snapshot identity, entry-document path, resource root, and prepared dependencies.
  The agent reads the files it needs instead of loading all resource contents into
  the conversation at once.
- A dedicated official Pack named `packy` distributes only the `packy-cli` skill
  and its required supporting files and notices. The CLI executable does not
  embed a separate distribution of the skill. Existing Pack lifecycle commands
  handle its installation and updates.
- The bootstrap skill is set up once per selected host and does not embed a static
  inventory. New catalog skills do not require reinstalling it solely to update
  the list of available skills.
- Snapshots and prepared resource paths have no automatic expiry or cleanup in the
  initial delivery. Explicit user removal can invalidate those paths; future
  cleanup must account for resources still in use.

The architectural direction is recorded in
[ADR 0002](../adr/0002-provide-on-demand-skills-without-executing-workflows.md).

## Historical constraints (2026-10-23)

The following observations describe the pre-release checkout inspected during the
interview. They are retained as dated evidence. Packy v0.2.31 now provides
`get skill`, explicit cross-Pack access dependencies, and retained snapshot
propagation; see [released tooling](../catalog-tooling.md). The real-skill
adaptations and complete-inventory acceptance remain Catalog follow-up work.

- The engine already exposes `packy list --json` and `packy show <pack> --json`.
  There is no on-demand `get` command in the inspected engine checkout.
- Catalog refresh already retains a complete immutable snapshot locally.
  Obtaining a skill need not imply downloading it separately.
- Some skills have distinct bodies for Codex, Claude Code, and OpenCode.
  Resolving a Pack and skill alone does not determine the applicable body.
- A skill's file tree and its dependencies on other skills are distinct concerns.
  For example, [Matty grill-with-docs](../../packs/matty/skills/engineering/grill-with-docs/SKILL.md)
  invokes `grilling` and `domain-modeling`, while its resource currently declares
  an empty `requires` list in [the manifest](../../packs/matty/pack.json).
- Existing skills may assume native host invocation or installed sibling paths.
  Access to their files alone does not establish compatibility with on-demand use.
- Personal/user and project skill locations already exist for Codex, Claude Code,
  and OpenCode. The engine currently uses `activate` without `--project` for
  personal scope and `install` for project scope; there is no `install --global`.
- Current installation and activation commands require an explicit `--surface`.
- Declared resource dependencies currently resolve within one Pack only. The
  agreed cross-Pack dependency contract requires engine and catalog work.
- Snapshot storage can resolve a retained snapshot by its immutable identifier,
  independently of the selected catalog. The new interface must carry that
  identifier through nested retrievals to preserve the agreed consistency.
- The selected Packs contain 117 logical skills: Matty 33, pstack 55, and Warp 29.
  These counts describe manifest inventory, not verified working procedures.
- Warp `review-pr` has a script that derives the target repository from its own
  location unless `OZ_REPO_ROOT` is set. Snapshot-based access must provide the
  intended project context rather than rely on that installed-layout assumption.
- The effective pstack `poteto-mode` host variants already copy their scripts into
  temporary working space before installing script dependencies. They preserve
  the target project's working directory rather than modifying catalog sources.
- Official snapshots currently have no automatic eviction or Packy cleanup command.
  Refresh retains earlier immutable snapshots. Upstream authoring-cache eviction
  is a separate mechanism and must not be confused with snapshot retention.
- There is not yet a distributed Packy CLI Skill or a built-in command to install
  one. The agreed dedicated Pack will use the existing lifecycle instead.
- Personal activation maintains multiple Pack-and-host intents. A dedicated
  bootstrap Pack can coexist with other Packs and be active for Codex and Claude
  simultaneously, provided its resource names and paths do not conflict.

## Bootstrap usage

The official `packy` Pack is authored by this Catalog slice. After its protected
main publication, use the [setup instructions](../packy-cli.md). Each host is
optional; personal activation is the default:

```sh
packy catalog refresh
packy activate packy --surface codex --resource skill:packy-cli
packy activate packy --surface claude --resource skill:packy-cli
```

Each host is optional and configured independently. Project-scoped setup uses
`packy install packy --surface <host> --resource skill:packy-cli` instead.

After setup, the agent uses the local catalog to discover a requested skill and
invokes `packy get skill <pack>:<skill> --surface <host>` for its host. The result identifies a
fixed snapshot and resource paths. The agent reads the entry document and any
needed supporting files, and retains that snapshot for nested skill retrievals.

## Product decision status

Q1–Q16 and final shared understanding have been confirmed. There are no remaining
product questions in this interview. The details below are engineering work within
the agreed boundaries, rather than additional unresolved product alternatives.

## Engineering delivery within the agreed contract

The released engine implements the first five items below. Catalog compatibility
review and acceptance of all 117 logical skills (33 Matty, 55 pstack, 29 Warp)
on both hosts remain the initiative scope; this bootstrap slice does not claim
those adaptations are complete.

- Exact discovery metadata and the versioned JSON result and error schemas.
- Resource preparation layout and preservation of relative references.
- How nested retrieval explicitly carries immutable snapshot identity.
- How callers pass target-directory context to scripts that need it.
- Manifest/schema evolution for cross-Pack skill dependencies, including validation
  of missing dependencies and cycles.
- Compatibility verification and reviewed adaptations for every in-scope skill
  on Codex and Claude Code.

## Delivery ownership

The Packy engine owns discovery/retrieval commands, structured output, cross-Pack
dependency resolution, immutable snapshot propagation, and resource preparation.
The Catalog Project owns the new `packy` Pack and reviewed Matty, pstack, and Warp
adaptations, declared dependencies, provenance, notices, and compatibility coverage.
Publishing catalog resources that require the new engine behavior must follow
availability of a supporting released Packy version.

The existing installed-resource contract remains supported. Catalog changes follow
the project's existing Pack versioning and validation rules.

## Acceptance scenarios

- A user can obtain a Matty skill while using pstack skills, without changing
  project installation or activation state.
- An installed, modified skill remains unchanged; retrieval through Packy returns
  the catalog version, while native invocation still uses the installed version.
- An unqualified request with multiple matches causes the agent to ask the user;
  a qualified request resolves the named Pack and skill.
- Entry documents, relative references, executable scripts, and required dependency
  resources remain usable from the returned locations for the selected host.
- Nested retrieval across Pack boundaries retains the starting snapshot even if
  a catalog refresh occurs between calls.
- Retrieval works offline after catalog acquisition, outside Git repositories,
  and without the skill's script runtimes installed.
- Retrieval does not execute catalog scripts or alter target-project files.
- Host-specific scripts use the intended target directory and writable scratch
  space, rather than inferring the project from the resource-cache location.
- Both human-readable and machine-readable results identify the resources and
  immutable snapshot used. Missing catalogs or unsupported requests produce
  actionable errors rather than silently substituting installed content.
- Matty, pstack, and Warp are reviewed for on-demand use on both Codex and Claude
  Code. A manifest binding alone is not evidence that a procedure works.
- Setting up the official `packy` Pack preserves existing Pack activations, and
  setting up one host does not replace the other's integration.
- A refresh does not remove earlier snapshots or prepared resource paths. Missing
  retained content must not silently resolve to a newer snapshot.

The design interview is complete. The implementation plan and tracker tickets
must preserve these boundaries and distinguish accepted requirements from
reversible engineering choices.
