# Matty plugin compatibility review

Plugin compatibility is independent of native bindings and the standalone
on-demand `ACCESS.md` procedure. The reviewed exports retain complete skill
folders and notices; the reports disclose external runtime and user
prerequisites without asserting that a client satisfies them.

Both formats export `codebase-design`, `diagnosing-bugs`, `domain-modeling`,
`grilling`, `prototype`, `research`, `wizard`, and `writing-for-agents`. Their
relative support files remain within each skill tree. Their use of an interactive
user, target project, browser, shell, or background agent is a disclosed
prerequisite, not a reason to treat the files as automatically unusable.

Claude additionally exports experimental `chief-of-staff`, `handoff`, `setup-matt-pocock-skills`, `teach`,
`to-questionnaire`, `wait-what`, `writing-beats`, `writing-fragments`, and
`writing-shape`. Their user-only invocation metadata is preserved. The Agent
Plugins export excludes these nine: their `disable-model-invocation` or
`argument-hint` fields are rejected by the released engine's Agent Skills
frontmatter validation. Removing the user-only control would change the
workflow's invocation policy. A format adaptation must preserve that policy
before it can be declared compatible.

The following candidates are omitted from both formats:

| Skills | Concrete unresolved contract |
| --- | --- |
| ask-matt | Router instructions invoke many sibling skills with unqualified slash syntax; the Agents binding also carries project instruction content, which plugins do not package. |
| claude-handoff | Launches the Claude CLI and directs the next agent to invoke arbitrary suggested skills through the Skill tool; a portable invocation contract is not established. |
| code-review | Calls `/setup-matt-pocock-skills` without a declared native dependency or reviewed format-specific invocation. |
| grill-me, grill-with-docs | Call the Skill tool for named sibling skills, but the native manifest does not declare that dependency closure or plugin invocation references. |
| implement, implement-spec | Call named sibling skills using slash syntax or the Skill tool, without declared native dependencies and reviewed per-format invocation references. |
| improve-codebase-architecture | Calls named sibling skills and uses `/codebase-design` without declared native dependencies or reviewed per-format references. |
| loop-me | Calls `/grilling` without a native dependency and reviewed per-format invocation. |
| pr | Its frontmatter `metadata.credits` is a nested mapping; the released exporter requires metadata values to be strings in both formats. |
| retro | Calls the Skill tool for `writing-for-agents` without a native dependency and reviewed invocation. |
| setup-ts-deep-modules | Calls the Skill tool for `codebase-design` without a native dependency and reviewed invocation. |
| tdd | Calls the Skill tool for `codebase-design` without a native dependency and reviewed invocation. |
| to-spec, to-tickets | Refer to `/setup-matt-pocock-skills` without a native dependency or reviewed per-format invocation. |
| triage, wayfinder | Call multiple sibling skills through the Skill tool and refer to setup without native dependencies or reviewed per-format invocation. |

Omission from `plugin_exports` makes an explicit selection fail rather than
silently omit the selected skill. Eligibility does not prove plugin installation,
client authorization, delegation, or model-backed execution. Additional
candidates require reviewed native dependency closure and reference contexts or
a format-specific adaptation; on-demand edges are not native plugin dependencies.

`chief-of-staff` remains an experimental, explicitly invoked workflow. Its
Claude export preserves original invocation metadata and discloses fresh-context
background agents, a user-agreed writable wiki, and host support and user
authorization for any selected recurring schedule. Its Agents native binding
and on-demand entry remain available; no Agent Plugins export is declared.
