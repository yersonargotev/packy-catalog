---
name: ponytail-help
description: >
  Explain Ponytail's Packy edition, available skills, conversational levels,
  and project installation choices when the user asks how to use Ponytail.
  Read-only help; does not install resources or change modes.
---

# Ponytail Help

Explain only the relevant entries below. This Pack contains skills and an
independently selectable project instruction. It does not install the upstream
plugin's hooks, statusline, MCP server, or persistent mode tracker.

## Skills and levels

| Skill | Purpose |
|---|---|
| `ponytail` | Choose the simplest correct implementation. |
| `ponytail-review` | Review a diff for unnecessary complexity. |
| `ponytail-audit` | Audit the whole repository for unnecessary complexity. |
| `ponytail-debt` | Collect deliberate shortcuts marked with `ponytail:` comments. |
| `ponytail-gain` | Explain upstream benchmark results and limitations. |
| `ponytail-help` | Explain this Packy edition. |

In Codex invoke `$ponytail` or `$ponytail-review`; in Claude Code use
`/ponytail` or `/ponytail-review`. In OpenCode ask the agent to load the named
skill. Skills omitted from a selected installation are not available there.

The `ponytail` skill accepts `lite`, `full` (default), or `ultra`:

- `lite`: implement the request and point out a simpler alternative.
- `full`: prefer reuse, standard libraries, and native platform features.
- `ultra`: challenge unnecessary scope while preserving explicit requirements.

Levels last within the conversation until changed. "Stop ponytail" or
"normal mode" ends the conversational mode. There is no cross-session mode
file or `PONYTAIL_DEFAULT_MODE` support in this Pack.

## Project installation

From the target Git project, preview before applying. These commands are
instructions for the user, not authorization to run them during help:

```sh
packy install ponytail --surface codex --dry-run
packy install ponytail --surface codex
```

The complete Pack includes all six skills **and persistent guidance**. Packy
v0.2.26 blocks installation if another Pack, such as Argote, already owns the
host's instruction file. In that case select only skills. For just the
conversational coding skill, select it explicitly:

```sh
packy install ponytail --surface codex --resource skill:ponytail --dry-run
packy install ponytail --surface codex --resource skill:ponytail
```

Repeat `--resource skill:<name>` to include other skills. Persistent guidance is
`instruction:ponytail-guidance`; it is not a dependency of any skill. Use
`--surface claude` or `--surface opencode` for those hosts.

Project guidance is installed into `AGENTS.md` for Codex/OpenCode and
`CLAUDE.md` for Claude. Stopping a conversational mode leaves that guidance
in effect. Existing unmanaged text is preserved, but separate Packs cannot
share ownership of this file in the pinned engine. To switch an existing
complete installation to skills only, preview
and uninstall that Pack surface, then reinstall with the desired skill roots.
Preserve local edits and resolve any drift before removal.

```sh
packy uninstall ponytail --surface codex --dry-run
packy uninstall ponytail --surface codex
```

## Updates and verification

```sh
packy catalog refresh
packy update ponytail --surface codex --project --dry-run
packy update ponytail --surface codex --project
packy verify --json
```

Refresh changes catalog availability; it does not update installed content.
Packy owns installation and removal. Do not edit its managed instruction
markers, receipts, or copied skills as a way to change conversation modes.
Interactive installation may offer a separate personal activation or host
trust step; accepting that step changes personal configuration independently
of the shared project installation.
