# Matty plugin review

Export eligibility is separate from native installation and on-demand access.
The two plugin formats use the same decisions below. Only
`writing-for-agents` is eligible: its entry and supporting files are
self-contained, do not invoke another skill, and retain the upstream and Catalog
notices. The consuming client still decides whether it supports these files.

The following skills are excluded for both formats. These exclusions are not
claims that the skill cannot work in a particular client; the existing native
instructions have not been adapted to promise a complete plugin workflow.

| Skills | Export limitation |
| --- | --- |
| ask-matt | Native router calls many sibling skills and the Agents binding also contributes project instructions; neither is a standalone plugin closure. |
| claude-handoff | Explicitly uses a Claude CLI background handoff and its environment. |
| code-review, codebase-design, research | Require background-agent delegation; the plugin formats do not establish that the consuming host provides it. |
| diagnosing-bugs | Contains native workflow references and a host-dependent human-loop runtime. |
| domain-modeling | Its workflow invokes other named skills and edits project domain files. |
| grill-me, grill-with-docs, grilling | The wrappers call other named skills and require delegation and interactive user decisions. |
| handoff | Handoff semantics and the receiving agent's skill availability depend on the host. |
| implement, implement-spec | Orchestrate named skills and delegated agents with tracker and worktree requirements; native calls are not portable plugin references. |
| improve-codebase-architecture | Requires named skill vocabulary, delegation, and browser/network assets. |
| loop-me | Workflow depends on host and project execution conventions. |
| pr | Uses project-specific PR templates and source references requiring an independently reviewed package closure. |
| prototype | Includes host and target-project runtime operations that are not portable plugin behavior. |
| retro | Uses session-specific evidence and environment checks, which a plugin package cannot provide. |
| setup-matt-pocock-skills | Configures the target project and tracker for other native skills. |
| setup-ts-deep-modules | Installs target project dependencies and configures the project runtime. |
| tdd | Invokes the native codebase-design skill and requires a confirmed testing seam. |
| teach | Requires an interactive learner, browser, and a persistent teaching workspace. |
| to-questionnaire | Requires a recipient and user-provided knowledge-gap context. |
| to-spec, to-tickets, triage, wayfinder | Depend on configured tracker operations and call other named skills or agents. |
| wait-what | User-only invocation control and session-specific conversation need a reviewed client invocation contract. |
| wizard | Produces human-driven setup and requires a shell and user-confirmed stages. |
| writing-beats, writing-fragments, writing-shape | Interactive writing procedures rely on user choices, current context, and target destinations; client invocation and approval behavior is not established. |

Reconsider an exclusion only with reviewed source, invocation references,
prerequisites and supporting closure for each format. Omission from
`plugin_exports` makes explicit selection fail; it does not silently export a
reduced skill. Native bindings retain their existing behavior and on-demand
`ACCESS.md` remains a distinct, snapshot-pinned procedure.
