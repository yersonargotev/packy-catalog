---
name: automate-me
description: "Use for \"automate me\", \"create/update/refresh my -mode skill\", \"turn/capture my preferences or working style into a skill\", or wanting agents to follow how the user works. Drafts or revises a personal -mode skill via create-skill + unslop, optionally pulling fresh evidence from recent transcripts."
disable-model-invocation: true
---

## Packy host adaptation

This skill originated in Cursor. On Claude Code, Codex, and OpenCode, interpret
Cursor-specific tool names and parameters as examples of the operation, not as
an API contract. Use the host's available tools to achieve the same result.
Delegate only when the host offers subagents and the current instructions permit
it; otherwise perform the steps sequentially. Select a named model only when
that host confirms it is available; otherwise use the parent model or host
default. Never claim a parallel or independent review if it did not occur.
Read `~/.pstack/models.md` only when its `# host` matches the current host;
otherwise use the parent model.

When this skill refers to another pstack skill, read the sibling installed
`SKILL.md` and apply its instructions in the current context. Claude Code's
`disable-model-invocation: true` prevents invoking that skill through its Skill
tool. A user can still invoke each skill explicitly. Replace Cursor transcript,
rule, and cloud-agent paths with the active host's documented equivalents only
when accessible. If required evidence or a capability is unavailable, report the gap and
continue only with independent supported steps. A missing required gate blocks
the action it protects; do not invent a result.

# Automate me

A guided flow for turning the user's working conventions into a skill agents will follow. The output is one `-mode` skill tailored to them (e.g. `jay-mode`, `priya-mode`).

This skill sequences an inline mining pass, a skill-authoring workflow, and
the **unslop** skill. Use Cursor's built-in `create-skill` only on Cursor. On
other hosts use an available skill creator or author the `SKILL.md` directly.

## Flow

### 0. Check for an existing skill

Look in the active host's project and personal skill directories for an
existing `*-mode/SKILL.md` matching the user's handle. On Cursor, include
`.cursor/skills/` and `~/.cursor/skills/`. If one exists, confirm intent with
the host's question tool or a concise question (unless the user already asked
to update it):

- Update the existing skill (default for repeat runs)
- Start fresh (rare, ask why before doing it)

Update mode changes the rest of the flow:
- Step 1 mines only history since the skill was last edited (`git log -1 --format=%cI <path>`).
- Step 2 asks what's changed or missing, not what to capture from zero.
- Step 4 edits the existing file in place. Preserve sections the user hasn't contradicted. Revise ones with new evidence. Add new sections only for genuinely new rules.

### 1. Mine their history

Locate the active workspace's transcript through the host when it exposes
one. On Cursor, use the workspace's `agent-transcripts/` directory. Do not
glob across other projects. If no transcript is accessible, use the current
conversation and ask the user for missing preferences; do not imply that a
history mining pass occurred.

Survey recent agent conversations within that scope for recurring patterns. Run multiple parallel subagents across slices of history (e.g. last 2-4 weeks, split into 3 slices so each has enough material). Each slice mining subagent reads transcripts from the workspace-scoped path the parent provides, looks for the signals below, and returns a short structured list of patterns it saw with evidence pointers. Default signals worth hunting:

- Response preferences (length, tone, format, "dumb it down" corrections)
- Delegation habits (subagents, models, specialized workflows, parallelism)
- Verification posture (what "done" means, unit tests vs live repro, reviewers)
- Code and prose discipline (style, principles cited, lint/format tools)
- Process conventions (worktrees, commits, PRs, review/merge tooling)
- Meta preferences (fixing skills mid-task, proposing new ones)

Cross-check across slices before elevating a signal. Patterns seen in 2+ slices are high-confidence. Lone signals are weak and usually get dropped.

### 2. Ask the user directly

Mining misses intent that hasn't come up yet. Use the `AskQuestion` tool (structured multi-choice) rather than asking the user to type from scratch.

Shape: one or two questions with 4-6 options each, `allow_multiple: true` for category questions. Start broad ("Which areas matter most?"), then follow up on selected areas with specific options. After the structured rounds, one free-form chat question catches anything the options missed.

Don't dump 20 questions.

### 3. Cluster findings

Group the combined signals into sections. Common ones (use only what applies):

- **Response style**: length, tone, format.
- **Autonomy**: how much to do without asking, MCP tool use.
- **Understand first**: which skills to reach for when scoping or investigating a change.
- **Subagents**: default, parallelism, model-to-task, specialized workflows.
- **Prose / code discipline**: principles, lint tools, style guides.
- **Review and verify**: repro posture, verification skills, live-testing tools.
- **Process**: git worktrees, commits, PRs, review/merge tooling.
- **Skills**: skill-authoring habits, fix-the-skill-first, proposing new skills.

The **poteto-mode** skill shows the shape. Read it for granularity. Don't copy its content. The user's rules are not the same as poteto-mode's.

### 4. Draft the skill

Use an available host skill creator to author the skill, or edit `SKILL.md`
directly when none is available. Placement:

- Path: preserve an existing mode skill's category. For a new mode on Cursor,
  use `.cursor/skills/<handle>-mode/SKILL.md` in the project or
  `~/.cursor/skills/<handle>-mode/SKILL.md` personally. On Codex, use
  `.agents/skills/<handle>-mode/SKILL.md` or `~/.agents/skills/`.
  On Claude Code, use `.claude/skills/<handle>-mode/SKILL.md` or
  `~/.claude/skills/`. On OpenCode, use its configured skill directory.
- Handle: the user's first name or chosen identifier.
- Frontmatter `description`: trigger on their name + `/<handle>-mode` + "work in their style", not on generic keywords like "write code" or "review PR".
- Frontmatter formatting: follow `create-skill`'s YAML rules. Keep `description` as one YAML scalar. Quote it or use `description: >-` with indented continuation lines when punctuation or wrapping requires it.
- Frontmatter `disable-model-invocation: true` by default. Opt out only if the user explicitly wants their mode to apply on every turn.

### 5. Iterate on prose

Apply the **unslop** skill and `create-skill`'s writing guidelines to every line.

Show the draft to the user and take feedback. Expect multiple iterations. Cut ruthlessly. A mode skill is not a manual.

### 6. Land it

Work in a worktree off main. Commit and open a PR. Don't push to main directly.

## Guardrails

- **Don't overfit to one conversation.** A preference stated once and contradicted another time is noise. Require multiple instances before codifying it.
- **Don't be clever.** Restating other skills' contents, inventing metaphors, or writing "poetic" prose for an agent reader is cost without benefit. Keep it operational.
- **Reference, don't inline.** Other skills the user relies on should appear as path references, not pasted excerpts. Same for any principle docs they maintain elsewhere.
- **Keep sections minimal.** Only add a section if the user has a specific, non-default rule there. "Communicate clearly" is not a section. "Short paragraphs. Tables when comparing options. Bullets only when items are genuinely parallel." is.
- **Name conventions generic.** Use "the user" or "the human" in imperatives, not the author's first name.
- **Don't force symmetry.** If a user has no process rules worth writing down, skip the Process section entirely.

## Evaluation

A `-mode` skill is subjective output. A `create-skill`-style test/iterate benchmark loop isn't useful here. Vibe-check with the user: does it read like them? Did it miss anything? Then ship.

Run a description-optimization loop only if the skill's trigger accuracy turns out to be a problem in practice.

## When not to use

- User wants a task-specific skill (not working conventions): `create-skill` alone, no mining required.
- User wants to capture one narrow workflow (e.g. "how I write commit messages"). That's a regular skill, not a mode skill.
