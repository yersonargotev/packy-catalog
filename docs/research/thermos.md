# Thermos upstream and projection requirements

Research date: 2026-09-22. Upstream is pinned to Cursor's `plugins` commit [`53e579f1481697931fc44f5445171397cfa2b24b`](https://github.com/cursor/plugins/tree/53e579f1481697931fc44f5445171397cfa2b24b/thermos), rather than the mutable `main` branch.

## Upstream inventory and license

Thermos 1.0.0 contains exactly three skills and two agents:

| Resource | Upstream purpose |
| --- | --- |
| [`thermo-nuclear-review`](https://github.com/cursor/plugins/blob/53e579f1481697931fc44f5445171397cfa2b24b/thermos/skills/thermo-nuclear-review/SKILL.md) | Diff-scoped correctness, security, breaking-functionality, developer-experience, and feature-gate audit. |
| [`thermo-nuclear-code-quality-review`](https://github.com/cursor/plugins/blob/53e579f1481697931fc44f5445171397cfa2b24b/thermos/skills/thermo-nuclear-code-quality-review/SKILL.md) | Strict maintainability audit emphasizing structural simplification, the 1,000-line threshold, boundary quality, and spaghetti avoidance. |
| [`thermos`](https://github.com/cursor/plugins/blob/53e579f1481697931fc44f5445171397cfa2b24b/thermos/skills/thermos/SKILL.md) | Orchestrates both review passes in parallel and synthesizes prioritized, deduplicated findings. |
| [`thermo-nuclear-review-subagent`](https://github.com/cursor/plugins/blob/53e579f1481697931fc44f5445171397cfa2b24b/thermos/agents/thermo-nuclear-review-subagent.md) | Applies the correctness/security rubric to parent-supplied diff and file context. |
| [`thermo-nuclear-code-quality-review-subagent`](https://github.com/cursor/plugins/blob/53e579f1481697931fc44f5445171397cfa2b24b/thermos/agents/thermo-nuclear-code-quality-review-subagent.md) | Applies the maintainability rubric to the same scoped evidence. |

The plugin metadata declares MIT, and the bundled [`LICENSE`](https://github.com/cursor/plugins/blob/53e579f1481697931fc44f5445171397cfa2b24b/thermos/LICENSE) is the MIT text with `Copyright (c) 2026 Cursor`. Every adapted upstream resource therefore needs an origin relationship of `adapted` and a notice preserving that license and attribution. The upstream [`plugin.json`](https://github.com/cursor/plugins/blob/53e579f1481697931fc44f5445171397cfa2b24b/thermos/.cursor-plugin/plugin.json) and [`CHANGELOG.md`](https://github.com/cursor/plugins/blob/53e579f1481697931fc44f5445171397cfa2b24b/thermos/CHANGELOG.md) corroborate the version and exact resource count.

## Required Packy shape

Packy supports Claude Code, Codex, and OpenCode, and treats a resource as host-independent input to surface adapters ([`CONTEXT.md`](https://github.com/yersonargotev/packy/blob/4b55c845a01feb6544e93174f05d6d94a4259567/CONTEXT.md#L83-L110)). A selectable `thermos` pack should consequently declare all three surfaces, one notice resource, the three skill resources, and the two `mode: subagent` agent resources. Each skill needs a native skill binding on every surface. Each agent needs a native agent binding on every surface and must require its corresponding rubric skill.

The skill bodies should preserve the upstream review scope and approval bars while replacing Cursor-specific `Task` syntax with capability-based instructions. Retain `disable-model-invocation: true` for Claude's manual-only behavior and add `agents/openai.yaml` with `policy.allow_implicit_invocation: false` for Codex. OpenAI documents that this policy blocks implicit selection while keeping explicit `$skill` invocation available ([Build skills](https://developers.openai.com/docs/build-skills)); OpenCode ignores unknown skill frontmatter and loads skills through its native `skill` tool ([OpenCode skills](https://opencode.ai/docs/skills)).

The `thermos` orchestrator must discover and load the installed rubric skills, gather one shared diff/full-file evidence package, send the complete applicable rubric and evidence to each worker, wait for both, then adjudicate and deduplicate. It should prefer the two named native agents when the host exposes them. When named agents are unavailable but generic delegation exists, it should launch two generic review workers with the full role instructions. When no delegation mechanism is available, it should run the two passes sequentially and state that limitation. This preserves the behavior without assuming Cursor's `subagent_type` names or `run_in_background` call shape.

Both adapted agent source files must contain exactly `name` and `description` in frontmatter because Packy's Claude renderer rejects any other source key ([`claude_agent_document.go`](https://github.com/yersonargotev/packy/blob/4b55c845a01feb6544e93174f05d6d94a4259567/internal/claudecode/claude_agent_document.go#L20-L55)). Their bodies must receive the full rubric in the task prompt or explicitly read the installed rubric file. Automatic preloading is not sufficient for Claude: official Claude Code documentation says `disable-model-invocation: true` also prevents a skill from being preloaded into a subagent ([Claude skills](https://code.claude.com/docs/en/skills), [Claude subagents](https://code.claude.com/docs/en/sub-agents)). The adaptation therefore leaves the Claude preload list empty while retaining the manifest dependency, passes complete rubric text from the orchestrator, and gives directly assigned agents a file-read path to that same source. This avoids duplicated rubrics and preserves upstream manual invocation behavior.

## Surface projection constraints

| Surface | Native projection and adaptation |
| --- | --- |
| Claude Code | Use `claude-agent-document`, declare the corresponding skill dependency with an empty preload list, and translate portable authority explicitly. The renderer derives `tools` and `skills` and enforces `permissionMode: default` ([renderer](https://github.com/yersonargotev/packy/blob/4b55c845a01feb6544e93174f05d6d94a4259567/internal/claudecode/claude_agent_document.go#L75-L120), [schema](https://github.com/yersonargotev/packy/blob/4b55c845a01feb6544e93174f05d6d94a4259567/schemas/pack/v2/pack.schema.json#L135-L152)). The review agents need filesystem/read and process/Bash authority to inspect diffs and files; the correctness/security agent additionally needs network authority for PR discussion or documentation checks. No edit authority is required by either rubric. Claude supports concurrent background subagents and synthesis, but permissions and runtime settings can force foreground execution ([Claude subagents](https://code.claude.com/docs/en/sub-agents)). |
| Codex | Packy projects each agent to `~/.codex/agents/<name>.toml` with `name`, `description`, and the adapted prompt as `developer_instructions` ([`surface.go`](https://github.com/yersonargotev/packy/blob/4b55c845a01feb6544e93174f05d6d94a4259567/internal/codex/surface.go#L192-L209), [`codexAgentTOML`](https://github.com/yersonargotev/packy/blob/4b55c845a01feb6544e93174f05d6d94a4259567/internal/codex/surface.go#L562-L572)). Current official Codex documentation supports parallel subagent workflows and project/personal custom agent TOML files ([Codex subagents](https://developers.openai.com/docs/agent-configuration/subagents)). The orchestration skill should request delegation explicitly and carry the full rubric because a worker does not inherit the parent's invoked skill content. |
| OpenCode | Packy projects native Markdown agents with `mode: subagent`, permissions, composition metadata, and the adapted body ([`surface.go`](https://github.com/yersonargotev/packy/blob/4b55c845a01feb6544e93174f05d6d94a4259567/internal/opencode/surface.go#L268-L289), [`openCodeAgentMarkdown`](https://github.com/yersonargotev/packy/blob/4b55c845a01feb6544e93174f05d6d94a4259567/internal/opencode/surface.go#L591-L608)). OpenCode documents primary-to-subagent invocation through the Task tool, parallel child sessions, per-agent permissions, and direct `@agent` invocation ([OpenCode agents](https://opencode.ai/docs/agents)). Its skill docs recognize only `name`, `description`, `license`, `compatibility`, and `metadata`, so Claude's `disable-model-invocation` is ignored there; the orchestrator should explicitly load the rubric and pass it to the worker rather than depend on implicit skill discovery ([OpenCode skills](https://opencode.ai/docs/skills)). |

## Acceptance and unresolved runtime evidence

Catalog validation should prove schema validity, exact pinned origins, notice closure, unique native bindings for all three surfaces, both agent-to-skill requirements, and valid Claude authority translation. Source-level projection tests already establish the adapter formats above, but this research did not run real Claude Code, Codex, OpenCode, ChatGPT Work, or another hosted agent runtime. Therefore parallel scheduling, installed-skill discovery, named-agent selection, and fallback behavior remain runtime-usability obligations to validate separately; documentation support is evidence of capability, not proof that this exact adapted pack executes end to end in every client/version.

## Implementation plan

1. Add `packs/thermos` at version `1.0.0` with the three adapted skills, two
   adapted agents, and byte-exact MIT notice from the pinned upstream commit.
2. Declare native bindings for Claude, Codex, and OpenCode, explicit rubric
   dependencies, and Claude read/process authority (plus network for the deep
   reviewer). Preserve explicit invocation in Claude/Codex metadata and state
   the review trigger in the body for OpenCode.
3. Replace Cursor-only orchestration with available host delegation, full
   rubric/context delivery, and an explicit sequential fallback. Keep reviews
   read-only and distinguish incomplete coverage from a clean verdict.
4. Validate the complete catalog against an unchanged main baseline, exercise
   actual projection/apply/inspection in isolated directories on all three
   adapters, and review standards and requirements independently.
5. Create the issue and PR after local validation/review, wait for required CI,
   and merge only if no unresolved blocking findings remain.
