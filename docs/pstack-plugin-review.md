# pstack plugin compatibility review

The `agents` variant is written for Codex and the `claude` variant for Claude Code. An Agents binding by itself does not establish model availability, delegation, authorization, or client support. Format prerequisites disclose the respective compatible client; delegation and evidence-dependent skills disclose additional requirements. A package validates configuration, not execution.

The per-skill decisions below apply independently to Agent Plugins and Claude plugins. `Eligible` means the respective surface variant is explicitly declared for that format. Names remain their skill IDs, there are no authored cross-skill export substitutions in eligible entries, and support trees, optional metadata, and MIT notices remain in the exported closure. For the standalone skills the native installation-root preamble was removed; `tdd` uses separately authored plugin trees. The other format decisions are exclusions, not promises that adaptation is impossible. Explicit selection of an excluded skill fails the complete export.

| Skill | Agent Plugins | Claude plugin | Review evidence |
| --- | --- | --- | --- |
| `architect` | Excluded | Excluded | Calls `how`, `arena`, `interrogate` and principles and passes runner files; native sibling references and the required dependency closure need plugin-context mapping. |
| `arena` | Excluded | Excluded | Requires four principle skills and native sibling links; its subagent/model selection requires a supported, authorized client. |
| `automate-me` | Excluded | Excluded | Calls `poteto-mode` and `unslop` and locates native host skill roots; plugin namespace and dependency paths have not been adapted. |
| `benchmark-checklist` | Eligible | Eligible | Standalone measurement checklist; representative data and measurement tools are disclosed. |
| `blast-radius` | Excluded | Excluded | Depends on `arena`, `unslop`, and `why` and must map their native invocations into plugin contexts. |
| `bro` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `correct` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `create-formal-verification-skill` | Eligible | Eligible | Standalone verification workflow; appropriate verification tools and permission are disclosed. |
| `create-verification-skill` | Excluded | Excluded | Recommends `/maintain-verification-skill` and writes host-specific skill roots; the recommendation is not namespace-adapted. |
| `figure-it-out` | Excluded | Excluded | Requires `architect`, `poteto-mode`, principles, and `show-me-your-work`; those native invocation references need a complete plugin closure. |
| `how` | Eligible | Eligible | Includes relative explainer/explorer prompts; authorized delegation and lookup tools are prerequisites. |
| `in-your-own-words` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `interrogate` | Eligible | Eligible | Includes reviewer templates; authorized delegation and actual model diversity are prerequisites. |
| `ketchup` | Excluded | Excluded | Reads `../bro/SKILL.md` and invokes optional host tooling; a partial plugin with only ketchup would need reviewed cross-skill path handling. |
| `maintain-verification-skill` | Excluded | Excluded | Refers to `/create-verification-skill`, native project skill roots and required per-feature subagents; the invocation is not namespace-adapted. |
| `make-bot-ui` | Eligible | Eligible | Webhook routine, provisioning access and server runtime are explicit external prerequisites. |
| `no-comments` | Excluded | Excluded | Requires `architect`, `how`, `why` and principles, and names a delegated review procedure; plugin dependency invocation has not been mapped. |
| `poteto-help` | Excluded | Excluded | Reads installed sibling skills, references setup and poteto-mode, and directs users to host-local paths; those assumptions do not hold for an isolated plugin. |
| `poteto-mode` | Excluded | Excluded | Requires 37 native skills and uses `../<name>/SKILL.md`, playbooks and host-specific invocations; no complete plugin reference adaptation has been reviewed. |
| `principle-attack-the-premise` | Excluded | Excluded | Links four sibling principle skills by `../.../SKILL.md`; selected dependency paths have not been reviewed as plugin references. |
| `principle-boundary-discipline` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `principle-build-the-lever` | Excluded | Excluded | Links sibling principles by `../.../SKILL.md` and requires their closure; plugin path references are not declared. |
| `principle-encode-lessons-in-structure` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `principle-exhaust-the-design-space` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `principle-experience-first` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `principle-explain-the-number` | Excluded | Excluded | Requires `benchmark-checklist` through `../benchmark-checklist/SKILL.md`; that native sibling path lacks a reviewed plugin reference. |
| `principle-fix-root-causes` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `principle-foundational-thinking` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `principle-guard-the-context-window` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `principle-laziness-protocol` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `principle-make-operations-idempotent` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `principle-migrate-callers-then-delete-legacy-apis` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `principle-minimize-reader-load` | Excluded | Excluded | Requires `principle-guard-the-context-window`; the relationship and cross-skill references need a plugin-context review. |
| `principle-model-the-domain` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `principle-never-block-on-the-human` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `principle-outcome-oriented-execution` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `principle-prove-it-works` | Excluded | Excluded | Names `show-me-your-work` for an audit trail; that external workflow has no compatible plugin export. |
| `principle-redesign-from-first-principles` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `principle-separate-before-serializing-shared-state` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `principle-sequence-verifiable-units` | Excluded | Excluded | Names `principle-prove-it-works` and `principle-build-the-lever`, neither currently exportable; their relationship is not reviewed for plugins. |
| `principle-subtract-before-you-add` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `principle-test-behavior-not-implementation` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `principle-type-system-discipline` | Excluded | Excluded | Names `typescript-best-practices`, boundary discipline and encode-lessons workflows; its references are not yet a reviewed plugin closure. |
| `recall` | Excluded | Excluded | Requires `unslop` and `why` and routes to host-specific skills and history; plugin invocation/reference handling has not been mapped. |
| `reflect` | Excluded | Excluded | Requires a principle skill, native sibling links and separate host delegates; the plugin dependency path is not declared. |
| `setup-pstack` | Eligible | Eligible | Writes an explicitly approved pstack preference file; supported client model controls are prerequisites. |
| `sharpen` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `show-me-your-work` | Excluded | Excluded | Requires `unslop`, copies a local template and requests an independent subagent; dependency invocation and support paths require a plugin review. |
| `swarm` | Eligible | Eligible | Requires authorized host delegation and isolated worker outputs; no named custom role is registered. |
| `tdd` | Eligible | Eligible | No native skill dependencies; explicit plugin trees remove native install roots. |
| `teach` | Excluded | Excluded | Invokes `how`, `why`, and `unslop`; the dependency invocation syntax and namespace have not been adapted. |
| `technical-writing` | Excluded | Excluded | Requires the `unslop` skill for its prose pass; the native invocation has not been mapped to plugin contexts. |
| `typescript-best-practices` | Excluded | Excluded | Requires boundary-discipline and type-system-discipline, including the currently excluded type-system workflow; dependency mapping is incomplete. |
| `unslop` | Eligible | Eligible | Standalone workflow with no required native skill dependency or cross-skill path; host-specific execution requirements remain explicit. |
| `why` | Eligible | Eligible | Includes evidence playbooks and templates; authorized delegation and available evidence connectors are prerequisites. |
