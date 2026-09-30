# pstack host compatibility proposal

Research date: 2026-09-26. Catalog baseline: `pstack@2.2.0`, pinned to
`cursor/plugins@ecc249f1e306fc64ddf83c7bed16cacf7c2239db`.

## Recommendation

Keep all 47 skills and their existing Packy dependencies. Adapt the source
instructions for Claude Code, Codex, and OpenCode where Cursor-specific tools
and paths would otherwise prevent execution. Keep the original Cursor plugin
as the Cursor installation route; Packy has no Cursor surface. Preserve manual
invocation policy across hosts, upstream attribution, and the MIT notice.

This is a Catalog contract migration rather than an upstream refresh. The
origin commit remains pinned. Every skill directory changes, so each origin
relationship becomes `adapted` and the Pack version increases to `3.0.0`.

## Implemented adaptation

- The 46 skills with upstream `disable-model-invocation: true` gain
  `agents/openai.yaml` with `allow_implicit_invocation: false`. `setup-pstack`
  retains implicit invocation because upstream does not disable it. This
  preserves the opt-in behavior in [Claude Code](https://code.claude.com/docs/en/skills)
  and [Codex](https://learn.chatgpt.com/docs/build-skills).
- Routed workflow skills identify Cursor tool names, subagent parameters,
  model slugs, and transcript paths as host-specific. They use available host
  capabilities, read sibling pstack skills directly, and report missing
  independent or live verification. Claude cannot internally invoke a skill
  marked `disable-model-invocation: true`, so reading the installed file is
  required for skill composition.
- `setup-pstack` writes `~/.pstack/models.md`, a file that pstack skills read
  explicitly. It records only confirmed host models; `inherit-parent` is the
  fallback. The file is not presented as an automatically applied host rule.
- `no-comments` supplies its review brief when the Cursor `Comment Sicko`
  agent is absent. Transcript workflows use only history the active host
  exposes. Verification-skill authoring uses each host's project skill path.
- `poteto-mode` and its playbooks treat Cursor cloud agents, `/goal`, `/loop`,
  and `cursor-team-kit` as optional integrations. An unavailable verification
  capability is reported, never counted as a successful check.

The [Cursor skills](https://cursor.com/docs/skills) and
[Cursor subagents](https://cursor.com/docs/subagents) remain the source for
Cursor-specific behavior. Codex supports native skills and subagents, but its
agent tool and model selection differ from Cursor's
[Task parameters](https://learn.chatgpt.com/docs/agent-configuration/subagents).

## Verification and remaining limit

Catalog validation checks the schema, declared dependencies, origin, notices,
and full file closure. It does not execute the 47 workflows. Confirm installed
skill discovery, manual invocation, configuration, and representative routed
workflows in real Claude Code and Codex sessions before claiming full runtime
parity. In particular, a host without background execution cannot perform a
continuous `/loop` workflow; the adapted skill reports that limit instead of
claiming continuous monitoring.
