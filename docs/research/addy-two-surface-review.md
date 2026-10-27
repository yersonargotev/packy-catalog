# Addy two-surface review

Addy 5.0.0 retains the original skill trees, supporting assets, MIT notice, and
four named specialists. The source revision is unchanged. Codex role files are
explicitly selected only at global scope on `agents`; Claude role documents
are supported at global and project scope. Neither files nor a preview prove
that a client loaded, authorized, or used a role. Browser and network tools
remain external prerequisites and are never configured by this Pack.

The nine former command resources are reviewed adaptations, not runtime command
projections. Each keeps its original upstream `commands/*.toml` provenance.
`build` keeps the single-task and approved autonomous modes; `constraints`,
`plan`, and `spec` keep their interview and planning gates; `code-simplify`
keeps behavior-preserving verification; `test` keeps the test-first loop and
conditional browser prerequisite; `review` retains five-axis review; `webperf`
keeps measured/deep versus source-only modes; and `ship` keeps its parallel
specialist fan-out, narrow skip condition, report synthesis, decision and
rollback. `ship` and `webperf` now explicitly stop when required named roles
or authorization are unavailable, rather than treating self-review as a
successful specialist delegation. Configured files do not establish runtime
access. Each derived skill declares its selected native dependencies; the four
specialist documents retain their dependency on `using-agent-skills` and the
owned asset/legal closure.

## Plugin review

Plugin export is reviewed separately for Agent Plugins and Claude plugins.
Only `api-and-interface-design` and `documentation-and-adrs` are eligible in
both formats: each is self-contained and has no required role, host-specific
invocation, relative support link, or installer-side state. The MIT notice is
included. The following skills are excluded from **both** formats; an explicit
selection fails, rather than silently dropping them or their dependencies.
The list identifies the principal reason; exclusion is not a claim that all
other aspects are portable.

| Skill | Reason for exclusion |
| --- | --- |
| browser-testing-with-devtools | Requires an independently configured and authorized Chrome DevTools MCP runtime and host-specific setup. |
| build | Nested workflow invocations and runtime/approval-sensitive autonomous execution need reviewed plugin invocation contracts. |
| ci-cd-and-automation | Assumes CI runtime, credentials, and project configuration; plugin execution context is not reviewed. |
| code-review-and-quality | Nested skill references and review support closure require plugin-context review. |
| code-simplification | Nested review and testing workflow references require plugin-context review. |
| code-simplify | Depends on native workflow skills and owned assets with unreviewed plugin references. |
| constraint-driven-development | Refers to native workflow invocations, project instructions, and external tools. |
| constraints | Depends on native workflow skills and owned assets with unreviewed plugin references. |
| context-engineering | Contains runtime-specific integrations and workflow references. |
| debugging-and-error-recovery | Refers to other workflow skills and external execution contexts. |
| deprecation-and-migration | Refers to related workflow skills and project-specific migration procedures. |
| doubt-driven-development | Assumes host-specific subagent and invocation behavior and includes orchestration reference material. |
| frontend-ui-engineering | Browser and accessibility support, related workflows, and reference contexts require review. |
| git-workflow-and-versioning | Refers to related skill invocations and release workflows. |
| idea-refine | Uses host argument interpolation and bundled script execution. |
| incremental-implementation | Refers to related workflow skills, test execution, and task state. |
| interview-me | Refers to downstream skill workflows and requires a responsive user. |
| observability-and-instrumentation | Refers to project runtime and monitoring integrations. |
| performance-optimization | Requires measurement tools, external runtime context, and reviewed related workflow references. |
| plan | Depends on native workflow skills and owned assets with unreviewed plugin references. |
| planning-and-task-breakdown | Refers to downstream workflow invocation and task-state paths. |
| review | Requires the native code-reviewer role and multiple skills; no plugin role adaptation was reviewed. |
| security-and-hardening | Refers to runtime security tooling and related workflow references. |
| ship | Requires three native specialist roles and parallel delegation; no plugin role adaptation was reviewed. |
| shipping-and-launch | Refers to project deployment operations, support files, and related workflow references. |
| source-driven-development | Relies on source-access tools and related runtime workflow assumptions. |
| spec | Depends on native workflow skills and owned assets with unreviewed plugin references. |
| spec-driven-development | Refers to other native skill paths and downstream workflow invocations. |
| test | Requires native test-engineer and browser/tool workflows; no plugin role adaptation was reviewed. |
| test-driven-development | References browser MCP and subagent execution, plus support files. |
| using-agent-skills | Routes among many native skills and owned assets; a standalone plugin closure was not reviewed. |
| webperf | Requires the native web-performance-auditor role and optional external measurement tools. |

These decisions describe package eligibility, not client installation, tool
authorization, host loading, or model-backed execution. Addy does not declare
on-demand access; this is distinct from native installation and plugin export.
