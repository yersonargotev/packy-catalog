---
name: setup-pstack
description: Configure the models and reasoning budget used by pstack roles on the active agent host. Use for /setup-pstack, "configure pstack models", or "pstack budget".
---

# Setup pstack

Write the portable pstack preference file at `~/.pstack/models.md`. Other
pstack workflows read it when they choose a worker model. It is not a host rule
and does not change the host's own model configuration.

## Steps

1. Detect the current host and the models its subagent tool actually accepts.
   A model shown in a picker is not proof that its subagent tool accepts it.
   If no model list is available, use `inherit-parent`; do not guess slugs.
2. Read an existing `~/.pstack/models.md` if present. Preserve role choices
   still supported by this host. Drop retired role names.
3. Ask the user for a budget: unlimited, large, medium, or small. Show the
   resulting model for each role. Let the user change individual roles. A
   reasoning tier is a preference, not a guarantee: use only a model the host
   confirms at that tier. Otherwise use the nearest confirmed lower tier, or
   `inherit-parent`.
4. Write the complete file atomically. Use the role names below. A panel value
   can list multiple models; each entry represents one candidate or reviewer.
   Use `inherit-parent` for a role when the host cannot select a model for it.
5. Read the file back and report the active choices and any host limitation.

```text
# pstack model preferences for the current host. This file is read by pstack
# skills; it is not automatically loaded by the host.
# host: codex
# budget: medium
feature, refactoring: inherit-parent
bug-fix: inherit-parent
perf-issue: inherit-parent
hillclimb: inherit-parent
judgment and prose: inherit-parent
hardest tasks: inherit-parent
how explorer: inherit-parent
how explainer: inherit-parent
why investigators: inherit-parent
why synthesizer: inherit-parent
reflect tooling: inherit-parent
reflect judgment, divergent, synthesizer: inherit-parent
arena runners: inherit-parent, inherit-parent, inherit-parent
arena cross-judge pool: inherit-parent
swarm workers: inherit-parent
architect runners: inherit-parent, inherit-parent
interrogate reviewers: inherit-parent, inherit-parent, inherit-parent
```

Read this file only when `# host` matches the current host. On another host,
ignore its model values and use `inherit-parent` until the user configures that
host. If no subagent facility exists, run a role in the current context and
report that the review was not independent.
