---
name: reframe
description: "Teach the expert words for what the operator is building, borrow words from neighboring fields that solved the same problem, then rewrite their description with them. Use for $reframe or /reframe."
disable-model-invocation: true
---

## Host execution

Apply this workflow when explicitly requested, or read it as a dependency of an explicitly requested pstack workflow. Read sibling pstack skills from this installation, not from another host's roots. Project skills belong under `.agents/skills` on Agents and `.claude/skills` on Claude Code; personal skills under `~/.agents/skills` or `~/.claude/skills`.

Delegate through the host's native subagent tool: Codex's advertised subagent API, or Claude Code's Agent tool with an available agent type such as general-purpose. Use only the agent types and parameters it exposes. Delegate only when current instructions permit it. Read `~/.pstack/codex-models.md` on Codex or `~/.pstack/claude-models.md` on Claude Code for confirmed role preferences; otherwise inherit the host model. `inherit-parent` means omit an override, not a model ID. Same-model reviewers are not a multi-model panel. When delegation is unavailable, label sequential work as such; a required independent-review gate remains incomplete.

Use accessible current-workspace history and authorized tools. Missing history, live control, scheduling, or external integrations is a reported limitation. Monitoring lasts only while the session actually runs unless a supported scheduler is verified. Preserve the user's scope and authority for messages, merges, deployments, and destructive actions. Required evidence gates remain blocked until real evidence exists.

On Agents, this workflow assumes Codex capabilities; a shared Agents binding does not provide Codex tools, model choice, or delegation. Use only capabilities authorized and available in the actual client. On Claude Code, read manual-only pstack dependencies as files; do not invoke them through the Skill tool or preload them as model-invoked skills.

Teach the operator the expert words for what they are building. Start from their own files, code and description, not a summary.

If their description could name more than one problem, first list the two or three problems it could be, each with the one term that names it and the sign that would tell it apart from the others. Then teach the words for the most likely one and say why you picked it.

1. Give 8 to 12 terms, ranked by how much each would change what gets built. For each, give the word and its meaning in one plain sentence, the part of their description it names, one real project, paper or system that uses it that way, with a link, and what it lets them ask an agent for.
2. Pick 2 or 3 neighboring fields that solved the same shape of problem under other names. For each, say what carries over, where the analogy breaks, and which terms come back.
3. Name what they didn't mention but should care about.
4. Rewrite their description with the new words.

Open every link and confirm it uses the term that way. Cut any citation you can't confirm. No padding.
