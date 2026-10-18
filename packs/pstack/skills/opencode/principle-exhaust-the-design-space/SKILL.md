---
name: principle-exhaust-the-design-space
description: "Apply when facing a novel UI interaction or architectural decision with no precedent in the codebase. Build 2-3 competing prototypes and compare side by side before committing."
metadata:
  invocation: explicit-request
---

## OpenCode execution

Apply this workflow when explicitly requested, or read it as a dependency of an explicitly requested pstack workflow. Read sibling pstack skills from this installation, not from another host's roots. Project skills belong under `.opencode/skills`; personal skills under `$XDG_CONFIG_HOME/opencode/skills (default ~/.config/opencode/skills)`.

OpenCode does not enforce Claude's manual-only frontmatter. This explicit-request rule is an instruction, not a native access control. Respect the user's configured skill permissions.

# Exhaust the Design Space

It also applies to product design decisions where user experience depends on feel, not logic.
