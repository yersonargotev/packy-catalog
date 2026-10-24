# Packy CLI bootstrap

The official `packy` Pack distributes the `packy-cli` skill and MIT notice,
with effective definitions for Codex and Claude Code. It is Catalog-authored;
it is not an embedded executable skill distribution. Pack versions remain
independent of the engine release selected by `packy-release.json`.

## Set up a host

Install Packy explicitly if unavailable. Use the released CLI supporting the
[on-demand protocol](https://github.com/yersonargotev/packy/blob/v0.2.31/docs/on-demand-skills.md).
After this Catalog revision is published by the existing protected-main workflow,
explicitly acquire with `packy init` when there is no local catalog, or update
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

The host's bootstrap enumerates live local inventory using `packy list --json`
and `packy show <pack> --surface <host> --json`, with no embedded Pack list.
A unique match resolves directly; several matches require the user's choice.
Keep Pack-qualified identities. Native bindings and installed copies alone do
not establish reviewed on-demand compatibility.

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
Codex and Claude Code; OpenCode's existing native installation remains supported.
The approved initiative covers all 117 logical Matty/pstack/Warp skills. This
slice supplies the bootstrap and controlled retrieval acceptance; #91–#98 own
real-skill adaptations and #99 owns complete-inventory acceptance. File/metadata
checks do not prove model-driven matching, native loading, runtime readiness or
semantic workflow success.

## Verify a candidate

After content review, run the [opt-in released-binary acceptance](../scripts/probes/README.md#packy-bootstrap-acceptance).
It uses owned disposable state for both scopes/hosts and a controlled reviewed
cross-Pack fixture. Ordinary validation, snapshot construction and publication
remain inert. Only the existing successful-main workflow publishes official
Catalog Snapshots; do not manually publish a second release.
