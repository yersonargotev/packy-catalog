# Foundation Pack surface and export review

This review accompanies the two-surface migration of claude 2.0.0, emil
3.0.0, humanlayer 4.0.0, ponytail 3.0.0, and web 4.0.0. It records format
eligibility separately from direct skill installation. No plugin declaration
claims that a client installed, authorized, or executed a skill.

Ponytail 3.0.1 corrects the invocation review in
[Catalog #120](https://github.com/yersonargotev/packy-catalog/issues/120).
`ponytail:ponytail` uses the explicit reviewed `plugins/ponytail` source in both
formats, with adapted provenance from the unchanged pinned upstream
`skills/ponytail`. Its invocation reference renders
`/ponytail:ponytail lite|full|ultra` for Claude plugins. Agent Plugins delegates
invocation to the consuming client, retaining the same level arguments without
inventing shared command syntax. Native installation keeps its separately scoped
Codex and Claude commands and client-dependent Agents guidance. Retired OpenCode
workflow guidance is removed. Metadata, full behavior, conversational stop rules,
supporting content and MIT attribution/notices are preserved. The opt-in
generation probe checks actual installed and exported instructions, unchanged
behavior outside invocation guidance, provenance/legal closure, deterministic
bytes/modes and isolated installation/client state. Other skills' eligibility
below is unchanged.

The manifests explicitly declare eligible formats. Omitted formats are not
eligible. The following exceptions apply to both plugin formats unless a format
is named:

- `emil:animate`: its mandatory instruction to invoke `pick-ui-library` needs
  a reviewed format-specific invocation adaptation. Native installations now
  include that dependency. The skill is not exported until that adaptation is
  reviewed; no universal invocation syntax is assumed.
- `emil:pick-ui-library`, `emil:prototype`, `emil:review-animations`, and
  `humanlayer:show-me`: eligible for Claude only. Their authored
  `disable-model-invocation` control is supported by Claude but is not Agent
  Skills metadata. Removing it would change their invocation policy.
- `ponytail:ponytail-help`, `ponytail:ponytail-audit`,
  `ponytail:ponytail-review`, and `ponytail:ponytail-debt`: excluded from both
  formats pending review of their user-facing direct installation guidance or
  literal slash command examples in plugin contexts. The ordinary skills remain
  directly available; the separately selected instruction is not bundled.
- `web:agent-browser`: excluded from both formats pending a reviewed source
  adaptation for its `hidden` and client-specific `allowed-tools` metadata and
  the separately installed browser CLI. The full native source is retained.

The remaining declared exports retain their same-Pack skill trees and notices;
references to files within those trees remain relative to their skill directory.
`claude:html-plan` discloses Node.js, and `emil:improve-animations` discloses
its host delegation prerequisite. References to other skills in descriptive
text are alternatives rather than required invocation steps. No custom roles are
required by these declared exports. GitHub Actions and agent credentials are
chosen by users of the Humanlayer loop-building workflows; generating a plugin
neither provisions nor authorizes those services.

The Humanlayer show-me and visual-pr adaptations replace host-specific tool or
skill-directory syntax with instructions relative to the skill tree. The loop
builder chooses the skill root for the explicitly selected client rather than
hard-coding Claude's root. Ponytail help uses the new surface names and preserves
the separation between project instruction and skill selections. These
adaptations retain their upstream origins and legal notices.
