# pstack plugin compatibility review

The pstack variants retain their separately authored Codex and Claude workflows.
The Agents projection of the Codex variant does not establish Codex execution,
model availability, delegation, or authorization in another Agents client.
On-demand procedures retain the initiating surface and immutable snapshot and
are independent of native plugin invocation.

`tdd` is eligible for both Agent Plugins and Claude plugins using explicit
format-specific sources. These remove the native installation-root assumption;
they retain the respective host prerequisite, skill metadata and MIT notice.
The procedure itself has no native skill or custom-agent dependencies. Plugin
creation does not establish runtime authorization or that a test was run.

The following skills are excluded from **both formats**. Their native variants
instruct readers to use pstack siblings from the native installation and fixed
host discovery roots. A skills-only plugin does not establish those locations;
for dependent workflows their host-specific invocation, supporting paths and
delegation assumptions also need a format-specific review. Omission from
`plugin_exports` is deliberate: explicit selection fails rather than exporting
an incomplete or misleading workflow. On-demand availability is a separate
contract and is not evidence of plugin compatibility.

- `architect`
- `arena`
- `automate-me`
- `benchmark-checklist`
- `blast-radius`
- `bro`
- `correct`
- `create-formal-verification-skill`
- `create-verification-skill`
- `figure-it-out`
- `how`
- `in-your-own-words`
- `interrogate`
- `ketchup`
- `maintain-verification-skill`
- `make-bot-ui`
- `no-comments`
- `poteto-help`
- `poteto-mode`
- `principle-attack-the-premise`
- `principle-boundary-discipline`
- `principle-build-the-lever`
- `principle-encode-lessons-in-structure`
- `principle-exhaust-the-design-space`
- `principle-experience-first`
- `principle-explain-the-number`
- `principle-fix-root-causes`
- `principle-foundational-thinking`
- `principle-guard-the-context-window`
- `principle-laziness-protocol`
- `principle-make-operations-idempotent`
- `principle-migrate-callers-then-delete-legacy-apis`
- `principle-minimize-reader-load`
- `principle-model-the-domain`
- `principle-never-block-on-the-human`
- `principle-outcome-oriented-execution`
- `principle-prove-it-works`
- `principle-redesign-from-first-principles`
- `principle-separate-before-serializing-shared-state`
- `principle-sequence-verifiable-units`
- `principle-subtract-before-you-add`
- `principle-test-behavior-not-implementation`
- `principle-type-system-discipline`
- `recall`
- `reflect`
- `setup-pstack`
- `sharpen`
- `show-me-your-work`
- `swarm`
- `teach`
- `technical-writing`
- `typescript-best-practices`
- `unslop`
- `why`
