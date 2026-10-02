---
name: principle-redesign-from-first-principles
description: "Apply when integrating a new requirement into an existing design. Redesign as if the requirement had been a foundational assumption from day one, instead of bolting it on."
metadata:
  invocation: explicit-request
---

## OpenCode execution

Apply this workflow when explicitly requested, or read it as a dependency of an explicitly requested pstack workflow. Read sibling pstack skills from this installation, not from another host's roots. Project skills belong under `.opencode/skills`; personal skills under `$XDG_CONFIG_HOME/opencode/skills (default ~/.config/opencode/skills)`.

OpenCode does not enforce Claude's manual-only frontmatter. This explicit-request rule is an instruction, not a native access control. Respect the user's configured skill permissions.

# Redesign From First Principles

When integrating a change, don't bolt it onto the existing design. Redesign as if the requirement had been there from the start.

- Read all affected files and understand the current design
- Ask: "if we were writing this from scratch with this new requirement, what would we build?"
- Propagate the change through every reference: types, docs, examples, rationale sections
- Think about the whole redesign, then deliver it incrementally

This is the method for preserving option value when integrating changes into an existing design.
