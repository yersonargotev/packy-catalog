---
name: principle-attack-the-premise
description: "Apply when two or more fixes that share one premise have failed the same gate. Take a census of which actors hold the imbalance before the next fix, then question the premise instead of writing another fix that assumes it."
metadata:
  invocation: explicit-request
---

## OpenCode execution

Apply this workflow when explicitly requested, or read it as a dependency of an explicitly requested pstack workflow. Read sibling pstack skills from this installation, not from another host's roots. Project skills belong under `.opencode/skills`; personal skills under `$XDG_CONFIG_HOME/opencode/skills (default ~/.config/opencode/skills)`.

Delegate through the task tool with an available subagent type; model selection follows that agent configuration unless the live tool exposes an override. Delegate only when current instructions permit it. Read `~/.pstack/opencode-models.md` for confirmed role preferences; otherwise use the host-selected subagent model. `inherit-parent` is a portable preference meaning omit an override, not a model ID. OpenCode may choose a different configured subagent model; report only model identities actually confirmed. Same-model reviewers are not a multi-model panel. When delegation is unavailable, label sequential work as such; a required independent-review gate remains incomplete.

Use accessible current-workspace history and authorized tools. Missing history, live control, scheduling, or external integrations is a reported limitation. Monitoring lasts only while the session actually runs unless a supported scheduler is verified. Preserve the user's scope and authority for messages, merges, deployments, and destructive actions. Required evidence gates remain blocked until real evidence exists.

OpenCode does not enforce Claude's manual-only frontmatter. This explicit-request rule is an instruction, not a native access control. Respect the user's configured skill permissions.

# Attack the Premise

When two or more fixes that share one premise have failed the same gate, suspect the premise, not the fixes.

**Why:** Each failure under a shared premise is evidence about the premise.

**Pattern:**
- **Write the premise down.** The premise is the one sentence that every failed fix assumed.
- **Take a census before the next fix.** Count the imbalance per actor. The census shows which actors hold the imbalance, not how large it is. Write the census as a rerunnable script per [Build the Lever](../principle-build-the-lever/SKILL.md).
- **Read the skew.** If the same few actors hold most of the imbalance on every run, something assigns them that role. Find what assigns the role. That assignment is the next "why" per [Fix Root Causes](../principle-fix-root-causes/SKILL.md).
- **Remove the asymmetry instead of compensating for it**, per the [Laziness Protocol](../principle-laziness-protocol/SKILL.md). Rotate the role between actors, randomize the assignment, or move the role, so that no actor holds it on every run. A return path, a shared pool, a batched hand-off, or a periodic rebalance leaves the assignment in place and adds work on every run.

**Stop:**
- Do not start the next fix before the premise is written down and the census exists.
- If the census is even across actors, the premise is not the cause. Look for the cause elsewhere and keep the census as evidence.

This principle is distinct from [Redesign from First Principles](../principle-redesign-from-first-principles/SKILL.md), which rebuilds a design around a new requirement. It questions a fact the current design assumes.
