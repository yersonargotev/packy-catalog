# Matty 4.4.0 upstream migration

[Issue #130](https://github.com/yersonargotev/packy-catalog/issues/130) updates
Matty from 4.3.0 to 4.4.0. The reviewed origin moves from
`mattpocock/skills@d81f3a183412e71a5b1e84ca21bc1a35eea03a60` to
`mattpocock/skills@a496f5513d4a4cf889bc48e189e579f4b0bdf6aa`.
This is a contract migration: it adds a resource and reconciles Catalog
Adaptations, beyond the closed upstream-refresh allowance.

## Updated resources

The selected upstream revision changes 20 original files across 17 included
skills: `ask-matt`, `code-review`, `codebase-design`, `diagnosing-bugs`,
`implement`, `implement-spec`, `improve-codebase-architecture`, `research`,
`setup-matt-pocock-skills`, `tdd`, `to-tickets`, `wayfinder`, `wizard`,
`claude-handoff`, `grilling`, `handoff`, and `teach`.

All original files, including templates and agent metadata, retain their exact
upstream bytes and executable modes. Inline `ACCESS.md` procedures incorporate
the applicable changes while keeping qualified Matty references and the
initiating host, snapshot, target project and delegated resource pointers.
Entries that already delegate to `SKILL.md` use the updated original procedure.
The existing MIT legal closure, native bindings, and dependency identities
remain intact. Other Packs retain their versions and content.

The migration includes wizard input/environment-file fixes, tracker CLI and
relationship corrections, fresh subagent contexts, a fresh implementer for
each ticket and final repairs, foreground parallel review, ticket lookup before
implementation, mutation evidence and explicit test-seam coverage notes.
Readiness declarations reflect the changed review, implementation and setup
requirements. Handoff summaries use an OS temporary file and the upstream
quoted file-read launch form.

## Experimental chief-of-staff

The new resource brings Matty to 34 skills. Its original `SKILL.md` retains
`disable-model-invocation: true`, and `agents/openai.yaml` retains
`allow_implicit_invocation: false`. The manifest description and on-demand
entry identify it as experimental. Agents and Claude native bindings are
available; acquisition alone never invokes it.

The workflow requires background subagents with fresh contexts and a writable
persistent wiki, with the location agreed before the first write. Wiki claims
are dated and code claims cite repository commits. Scheduling is a suggestion
contingent on host support and user authorization. Delegates retain the
initiating on-demand host, snapshot and resource pointers.

The Claude plugin export preserves its complete source and invocation metadata.
Agent Plugins export remains undeclared because that format rejects its
user-only frontmatter; explicit selection must fail without creating output.
The four `skills/misc/` resources remain excluded, consistent with upstream's
frozen, unmaintained policy.

## Verification

Run ordinary tooling tests and complete catalog validation against the clean
pre-change baseline:

```sh
./scripts/test.sh
./scripts/validate.sh /path/to/clean-baseline --json
```

From a clean committed candidate, check source fidelity and native/on-demand
behavior against a clean checkout of the selected upstream commit:

```sh
python3 -B scripts/probes/matty-update.py --upstream /path/to/mattpocock-skills \
  > /tmp/matty-update-evidence.json
```

The opt-in probe compares every original file and executable mode, installs and
verifies all 34 skills on both surfaces, compares complete native trees and
notices, retrieves each on-demand entry and its supporting/legal closure,
checks explicit retained access for chief-of-staff, exports its Claude plugin,
rejects its unsupported Agent Plugins export, and removes native installations
while preserving unrelated project files. It observes installation, ambient
client and authored-resource state and removes its disposable workspace.

These checks establish packaging and access behavior. They do not launch
agents, execute a wizard, create a wiki, schedule work, or establish
model-backed workflow success. PR evidence records the candidate and actual
validation results; official publication belongs to the main-push workflow.
