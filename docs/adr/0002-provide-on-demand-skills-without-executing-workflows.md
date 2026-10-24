---
status: accepted
---

# Provide on-demand skills without executing workflows

Users need to combine skills from different Packs without changing their project's
installed configuration. Add on-demand access alongside traditional installation:
a single Packy CLI Skill teaches agents to discover catalog skills and obtain
their resources and paths. Packy supplies content; the agent follows the skill's
procedure and executes any required scripts. Permanent instructions retain their
installation model.

File availability alone does not satisfy existing skills that rely on native skill
invocation or installed sibling paths. Maintain explicit, reviewed Catalog
Adaptations and declared dependencies rather than treating arbitrary upstream
skills as automatically compatible. Dependencies may cross Pack boundaries using
explicit Pack-qualified references, rather than requiring users to install each
dependency's Pack. A procedure and its nested dependencies retain one immutable
Catalog Snapshot, so catalog refresh cannot silently mix revisions.
Requests through the Packy CLI Skill use catalog content rather than substituting
an installed, potentially modified copy.

The public access interface is `packy get skill <pack>:<skill>`, with readable and
JSON output containing resource paths and immutable snapshot identity. Retrieval
uses the local catalog, leaves the target project unchanged, and does not require
a Git repository or installed runtimes. Catalog refresh remains explicit. The
agent checks reported prerequisites before executing scripts and uses separate
scratch space for intermediate files and dependencies.

A dedicated official `packy` Pack distributes the `packy-cli` skill using the
existing lifecycle, with personal setup by default and optional project setup.
This reuses catalog review and distribution rather than embedding the skill in
the executable. Initial coverage is all 117 skills in Matty, pstack, and Warp on
Codex and Claude Code. Snapshots and prepared resources have no automatic expiry
or cleanup in the initial delivery, preserving paths across refreshes.

The user confirmed all sixteen design decisions and the final shared understanding
on 2026-10-23. This accepts the architecture; implementation and release remain
separate delivery work. See [the design](../design/on-demand-skills.md).
