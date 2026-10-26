# Packy CLI bootstrap

The official `packy` Pack distributes the `packy-cli` skill and MIT notice,
with effective definitions for Codex and Claude Code. It is Catalog-authored;
it is not an embedded executable skill distribution. Pack versions remain
independent of the engine release selected by `packy-release.json`.

## Set up a host

Install Packy explicitly if unavailable. Use the released CLI supporting the
[on-demand protocol](https://github.com/yersonargotev/packy/blob/v0.2.31/docs/on-demand-skills.md).
Explicitly acquire with `packy init` when there is no local catalog, or update
availability with `packy catalog refresh`. Discovery/retrieval never refresh
implicitly.

Personal activation is the default. Preview, review the plan, then approve its
exact identity through the existing interactive lifecycle:

```sh
packy activate packy --surface codex --resource skill:packy-cli --dry-run
packy activate packy --surface codex --resource skill:packy-cli
```

For Claude Code, independently run the same commands with `--surface claude`.
The personal roots are `~/.agents/skills/packy-cli` and
`~/.claude/skills/packy-cli`. Both hosts can coexist alongside unrelated active
Packs and native skills; ownership conflicts and drift still require resolution.
Claude Code retains the engine's supported host floor (2.1.203 or newer).

For a shared project, run from the intended Git project instead:

```sh
packy install packy --surface codex --resource skill:packy-cli --dry-run
packy install packy --surface codex --resource skill:packy-cli
```

Use `--surface claude` independently for the project's Claude bootstrap.
Project roots are `.agents/skills/packy-cli` and `.claude/skills/packy-cli`.
The real apply command requests consent; JSON output does not grant it. Setting
up the bootstrap does not activate/install the skills later obtained through it.
Update and retire the bootstrap through the existing Pack lifecycle, preserving
normal preview, consent, ownership, and drift checks.

## Discover and obtain

For a complete `<pack>:<skill>` identity, the host's bootstrap retrieves it
directly. `get skill` checks reviewed compatibility; prior discovery is optional.
For an incomplete request, inspect the known Pack with
`packy show <pack> --surface <host> --json`; enumerate `packy list --json` first
only when the Pack is unknown. Capture `show` JSON in writable scratch space,
then display matching rows with a local JSON reader. If the name is unknown or
unmatched, display only qualified identities and descriptions first, then
inspect complete metadata for the matching candidates. The host skill includes
[capture/filter examples](../packs/packy/skills/codex/packy-cli/SKILL.md#select-a-qualified-identity).
There is no embedded Pack list. A unique match resolves directly; several matches
require the user's choice. Keep Pack-qualified identities. Native bindings and installed copies
alone do not establish reviewed on-demand compatibility.

```sh
packy get skill <pack>:<skill> --surface codex --json
packy get skill <dependency-pack>:<dependency-skill> --surface codex --snapshot <returned-snapshot-id> --json
```

Use the initiating host and immutable snapshot for all nested same-Pack and
cross-Pack access. Read the returned `entry_document` and only needed supporting
files under `resource_root`; descriptors also identify the Pack version,
dependencies and known prerequisites. A new independent request follows the
selected local snapshot. Missing retained content fails instead of substituting
a newer revision. There is no automatic expiry or cleanup; explicit manual
removal can invalidate prepared paths.

Packy provides resources; the agent follows the selected procedure, preserving
its approvals, domain assumptions, required tools, stopping rules and retirement
behavior. Missing content runtimes do not block obtaining instructions. Reported
prerequisites remain unverified until the agent checks them before execution.
No runtime provisioning happens automatically. Choose the target project
explicitly and use separate writable scratch/output locations; keep immutable
resources and installed copies unchanged. Native invocation retains its installed
behavior, including local modifications.

Retrieval works outside Git after acquisition and does not execute scripts,
change target projects or install/activate requested Packs. On-demand scope is
Codex and Claude Code. Matty and Warp retain native OpenCode installation;
pstack withdrew OpenCode in 5.0.0 under [ADR 0003](adr/0003-limit-pstack-host-support.md).
Retained pstack installations require [explicit retirement](pstack-opencode-retirement.md);
retrieval never migrates or removes them. All 117 logical Matty/pstack/Warp skills
have reviewed entries for both access hosts; the [coverage inventory](on-demand-coverage.md)
records applicability, dependencies, prerequisites and workflow limits. File/metadata
checks do not prove model-driven matching, native loading, runtime readiness or
semantic workflow success.

## Verify a candidate

After content review, run the [integrated released-binary acceptance](on-demand-coverage.md#run-the-integrated-contract).
It uses owned disposable state for both scopes/hosts, all 234 roots, controlled
same-/cross-Pack selection transitions and optional safe real-content helpers. Ordinary validation, snapshot construction and publication
remain inert. Only the existing successful-main workflow publishes official
Catalog Snapshots; do not manually publish a second release.

## Concrete requests and recovery

For `matty:retro`, obtain the requested skill immediately:

```sh
packy get skill matty:retro --surface codex --json
```

Require a successful versioned `skill-access` report with `result: "prepared"`
and the requested identity and host. The direct route retains all report,
dependency, prerequisite and snapshot checks described above.

For an unspecified “TDD” request, discover the relevant candidates and ask the
user to choose between qualified matches such as `matty:tdd` and `pstack:tdd`.
The CLI does not perform natural-language ranking or resolve that product choice.
Using `jq` to display only exact-name matches:

```sh
packy list --json
packy show matty --surface codex --json > <scratch>/matty.json
packy show pstack --surface codex --json > <scratch>/pstack.json
jq '.skills[] | select(.qualified_skill | endswith(":tdd"))' <scratch>/matty.json <scratch>/pstack.json
# After the user selects matty:tdd:
packy get skill matty:tdd --surface codex --json
```

For a separate `matty:implement` request and its nested TDD procedure:

```sh
packy get skill matty:implement --surface codex --json
packy get skill matty:tdd --surface codex --snapshot <implement-snapshot-id> --json
```

For Claude Code, use `--surface claude` on both discovery and every nested request.
Keep `entry_document`, `resource_root` and `snapshot_id` from the successful
report. Read supporting files relative to their document locations. Tell helpers
the intended target explicitly (for example Warp review's `OZ_REPO_ROOT`), and
choose a different writable scratch/output directory. Do not run commands from
the resource cache merely to infer the target project.

| Observation | Explicit response |
| --- | --- |
| Packy is unavailable | Install the supporting released CLI explicitly; no substitute development binary. |
| No local catalog | Acquire with `packy init` or `packy catalog refresh` after authorization. |
| Several matching names | Ask the user to choose a qualified identity; do not prefer an installed copy. |
| `invalid_identity` or `unknown_skill` | Correct the qualified identity using focused discovery: inspect the named Pack first, using `list` if the Pack is unknown or unresolved. Discovery describes the current selection; preserve the initiating host and `--snapshot` on nested retrieval retries. |
| Incompatible host/resource | Correct the explicit host/identity or request a reviewed adaptation. |
| Missing retained content | Restore that exact retained revision; do not retry against latest or native copies. |
| Missing runtime, tool, model or service | Read resources normally; report/check prerequisites before the relevant procedure, preserving its stop/fallback policy. |
| Modified installed copy | Leave it unchanged; Packy retrieval supplies the selected Catalog Resource and native invocation still uses the installed copy. |

After acquisition, discovery/retrieval use local data offline and outside Git.
They do not refresh, provision runtimes/dependencies, execute scripts or expire/
clean resources. Explicit refresh changes only subsequent independent requests;
carry the earlier snapshot into nested calls and keep earlier paths while their
procedure is active. Manual deletion can invalidate them and yields an error.
