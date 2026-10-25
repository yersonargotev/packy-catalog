# pstack engineering and verification: reviewed on-demand access

[Issue #94](https://github.com/yersonargotev/packy-catalog/issues/94) covers exactly
13 logical skills and 26 effective Codex/Claude entries. This Catalog contract
migration advances pstack from 5.0.0 to 5.1.0. The upstream remains
`cursor/plugins@0148b78c56c72a1b8412055913c79f767095b217`; other Packs retain
their versions. It reuses the [reviewed foundations](pstack-foundational-on-demand.md)
and the single released-tooling declaration. It requires no engine checkout.
The separate 5.0.0 prerequisite integrated in #105 before this delivery; the
earlier `e321e44a3b1eef917c5aa5edd44efce45a9eb724` work is reused as source,
with fresh acceptance against integrated baseline
`694b98d7d204b79cb2886388fdfa6504e295f484`.

## Host and resource contracts

Each `ACCESS.md` derives from that host's actual adapted `SKILL.md`, preserving
manual invocation, supported tools, model preferences, limitations, approvals and
workflow evidence gates. Original native bodies, supporting files, notices,
executable modes, bindings, descriptions and `requires` remain unchanged. Common
sources retain their exact-copy originals. OpenCode remains withdrawn under the
[accepted two-host policy](../adr/0003-limit-pstack-host-support.md). All changed
sources retain their existing adapted origin and complete, acyclic
upstream/adaptation legal closure.

The initiating explicit surface and immutable snapshot accompany nested retrieval
and delegated work, along with the target directory, prepared entry/resource
locations and separate writable scratch/output. Missing retained content fails
rather than selecting newer content. New independent requests use the selected
catalog. Native registration, installed siblings and another Pack's similarly
named workflow cannot substitute for the prepared pstack procedure or its gates.

Architect's on-demand runner and rationale copies link prepared entries instead
of native siblings. Its original design red flags remain progressively readable.
TypeScript's on-demand patterns copy retains all examples and links the prepared
principles. The original supporting files remain intact for native use. The
feature-map examples and decision-log template/helper retain their bytes and modes.
Discovery reports metadata and unverified prerequisites, without embedding these
supporting bodies or asserting runtime readiness.

## Reviewed matrix

The required graph is identical on Codex and Claude; their bodies, tool APIs,
preference paths and project skill directories remain host-specific. Required
conditional branches prepare their resources without executing them. Native
`requires` and access dependencies are both prepared by the released engine.
The existing foundational background edges, including minimize-reader-load to
guard-the-context-window, remain in the closure.

| Skill | Direct required pstack dependencies | Preserved workflow and unverified execution prerequisites |
| --- | --- | --- |
| `architect` | `arena`, `how`, `interrogate`, `why`; principles: boundary-discipline, encode-lessons-in-structure, exhaust-the-design-space, fix-root-causes, foundational-thinking, laziness-protocol, make-operations-idempotent, minimize-reader-load, outcome-oriented-execution, redesign-from-first-principles, separate-before-serializing-shared-state, subtract-before-you-add | Ground, sketch, agree, implement, scrap; two structurally distinct independent candidates, confirmed host model preferences, runner prompt, rationale and red flags. Default continuation and explicit sketch/checkpoint requests retain their meaning. Requires target source, authorized subagents and separate writable candidates/outputs. |
| `blast-radius` | `arena`, `unslop`, `why` | Actual downstream/library investigation, one safety fact and real-code proof or an unproven verdict; wide changes retain diverse arena review. `how` is companion advice. Requires target/history/library access and project runtime/harness. |
| `correct` | None | A mistake class needs two real occurrences. Architecture, types, lint, tests, then judgment documentation; prove checks on past mistakes, one commit per class, human-approved exceptions. Requires repository/review history and actual compiler/lint/test/CI tools. |
| `create-formal-verification-skill` | None | Choose a harmful property from real code, fit a reproducible verifier, state bounds/assumptions, report counterexamples without weakening the property or silently changing product code. Execute a real broken variant and restore it. Generated skills belong in the target's host-specific skill directory, with writable scratch and verification tools. |
| `create-verification-skill` | None | Interview the actual app; generate concrete launch/doctor/drive/evidence/cleanup/helpers and feature-map commands, run one real feature, keep evidence after cleanup, report stand-in gaps. Requires a buildable app, harness, seed/auth/instance prerequisites and writable target skill directory. Maintenance is optional routing. |
| `maintain-verification-skill` | None | Explicit target selection, read-only source wave per feature, coordinator-owned live driving of every feature, doctor/recovery/retry rules, evidence survival and final teardown. Only the selected project verification skill is editable; prepared Catalog resources are never targets. Retains `clean`/`changed`/`blocked`, proven corrections and at most one PR. Generation is optional background/routing, not a prerequisite or automatic fallback. |
| `make-bot-ui` | None | Actual authorized provider/connector and webhook response, server-side secret handling, 8-second one-try delivery, harmless proof and distinct wake completion. Network/Tailscale tools, current platform setup and machine approval remain execution requirements. Retrieval does not provision, read secrets, start a server, install tools, change networking or claim a wake. |
| `no-comments` | `architect`, `how`, `why`, `principle-fix-root-causes`, `principle-redesign-from-first-principles` | Comment Sicko or independent brief, disclosed direct-audit fallback, evidence-backed accepted findings, one rejected-report rerun and failure on a second rejection. Explicitly stop architect after its sketch; step 4 implements. Keep scope fences and interactive/caller pre-approval for constraint encodings. |
| `recall` | `unslop`, `why` | Accessible current-workspace history, seven-day default window, actual source identifiers, shared-record source investigation, unavailable-source gaps and live-state checks. Capsule/thread/problem/next-move contract remains. Session pickup is an optional `pstack:poteto-mode` playbook (`playbooks/session-pickup.md`); automation is also an optional route. |
| `show-me-your-work` | `principle-encode-lessons-in-structure`, `unslop` | Canonical append-only TSV, run ownership and transcript audit, evidence pointers, cross-model independent review and Attention output. Missing diverse review remains incomplete. Optional helper requires Bash/date/dirname/mkdir/tr and an explicit writable log outside immutable resources. |
| `teach` | `how`, `unslop`, `why` | Actual how/why investigation, preserved confidence language, paced explanation, progressive diagrams and required image tools where applicable. Requires authorized sources and investigation/delegation capabilities; retrieval itself does no investigation. |
| `technical-writing` | `unslop` | Diátaxis, Google style, STE and Global English, project vocabulary and product-copy boundaries. Propose changes to unslop instead of editing immutable guidance. |
| `typescript-best-practices` | `principle-boundary-discipline`, `principle-type-system-discipline` | Apply type-system discipline first; retain schema-first boundaries, constructive types, narrowing, telemetry, real tests and full patterns. Project schema/compiler/runtime tools are checked during execution. |

## Acceptance and limits

The public CLI is the pre-agreed test seam. Acceptance uses the complete clean
5.0.0 baseline at `694b98d7d204b79cb2886388fdfa6504e295f484`, after protected
integration of the support withdrawal. The earlier candidate is source work;
its receipts do not qualify this delivery. Descriptive policy preservation
additionally requires content review; executing arbitrary app, formal-proof,
external-provider or model-driven workflows is outside retrieval acceptance.

From a clean committed candidate and that complete 5.0.0 baseline:

```sh
python3 -B scripts/probes/content-probes.py --scenario pstack-engineering \
  --pstack-baseline /path/to/pre-change-catalog > /tmp/pstack-engineering-evidence.json
```

The opt-in runner checks all 26 roots for host-qualified identity/version/snapshot,
independently specified required closure, complete source/supporting/legal bytes
and modes, rendered links, invocation restrictions, substantive workflow policies
and unverified prerequisites while content runtimes are absent. A modified active
native architect cannot replace the catalog entry. Representative root and
supporting references retain the initiating snapshot across a controlled selection
transition; old paths stay usable, new independent calls follow the new selection,
and missing retained content fails explicitly.

Only the reviewed decision-log helper executes, with an explicit owned disposable
output. Checks cover one header, append preservation, six columns, formula/tab/
newline/CR escaping, unchanged sources and unrelated targets, and execution-state
cleanup. The source helper is read from its prepared location; its working and
output locations are separate. This does not satisfy its cross-model review gate.

Native regression installs the exact scoped selection and inherited dependencies
on Codex and Claude, compares all original bytes/modes and contracts to
the baseline, and verifies project state. Complete candidate/baseline builds,
ordinary tooling tests and clean-baseline version validation remain required.
All child commands are bounded and HOME/config/data/cache/project state is owned
and disposable. The evidence records exact commits, release identity, archive
digests, command outcomes and cleanup. No live installed selections change.
Ordinary checks and publication do not execute these probes. Protected integration
and the existing successful-main publication workflow retain their authority.
