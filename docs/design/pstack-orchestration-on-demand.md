# pstack orchestration: complete reviewed on-demand access

This review records its original Catalog generation. Surface names, Pack
versions, and acceptance evidence below are historical; see the
[current setup guide](../packy-cli.md) for the `agents` and `claude` contract.

[Issue #95](https://github.com/yersonargotev/packy-catalog/issues/95) completes
pstack's 55 logical skills on Codex and Claude. This contract migration advances
pstack from 5.1.0 to 5.2.0 against integrated baseline
`6cd6de171358c2d2046456684ddbf11815d7861e`. The origin remains
`cursor/plugins@0148b78c56c72a1b8412055913c79f767095b217`; other Packs and the
single released-tooling declaration retain their versions and identities.

## Compatibility and dependency matrix

Each row applies to both hosts. Each entry derives from its actual host-native
body. Codex keeps `.agents/skills`, confirmed `~/.pstack/codex-models.md`
preferences and advertised subagent controls. Claude keeps `.claude/skills`,
`~/.pstack/claude-models.md`, its Agent tool, manual-only frontmatter and file
reads for manual-only dependencies. Native bodies, original supporting files,
invocation metadata, modes, bindings and effective `requires` retain their bytes
and contracts. Common upstream originals and both legal notices remain intact.
OpenCode stays withdrawn under [ADR 0003](../adr/0003-limit-pstack-host-support.md),
including retained installations and explicit retirement guarantees.

| Root | Direct required closure | Reviewed substantive contract and unverified prerequisites |
| --- | --- | --- |
| `automate-me` | `pstack:poteto-mode`, `pstack:unslop` | Confirm existing-mode changes unless authorized; mine only accessible current-workspace history and only the update window; disclose gaps; ask direct preference questions; make a user-specific draft. Read mode as a shape reference without activating it. Optional authoring guide retains direct-authoring fallback. Write to an explicit selected project/personal destination, preserve host invocation rules, validate, iterate and deliver within scope. |
| `figure-it-out` | `architect`, `arena`, `poteto-mode`, `show-me-your-work`; principles: encode-lessons-in-structure, foundational-thinking, laziness-protocol, never-block-on-the-human, prove-it-works, separate-before-serializing-shared-state, sequence-verifiable-units | Frame the workflow before code; falsifiable predicate, quantified scope/rigor and multi-hour checkpoint. Independently landable units, hypothesis loop, real-artifact verdicts, decision trail and independent/diverse review. `VERIFIED`, `NOT VERIFIED` and `INCONCLUSIVE` remain distinct. Requires real target/runtime/evidence and writable outputs. |
| `poteto-help` | `pstack:poteto-mode`, `pstack:setup-pstack` | Discover qualified compatible resources, retrieve selected optional routes on the initiating surface/snapshot, read their actual host content before recommendation. Optional recommendations are not required preparation. Preserve questions versus actions, explanation versus setup authority, missing-preference fallback, current CLI/catalog installation evidence, and playbooks versus standalone skills. TDD cannot route to Matty or another Pack by native name. |
| `poteto-mode` | All 37 existing native dependencies, plus `pstack:tdd` and `pstack:why` used by conditional playbook branches. The manifest enumerates the reviewed direct set; transitive preparation retains both native and access edges. | Preserve selection and follow-up continuity, all 23 playbooks, principle triggers, model preferences, supported delegation, independent/diverse review, artifact proof, autonomy and shipping/merge gates. Optional host plugins, history, control tools and schedulers retain honest capability gaps and source fallbacks. Helpers require checked runtimes and separate target, execution/dependency and output/store locations. |

`figure-it-out` requires mode. Mode's bespoke `pstack:figure-it-out` route is
optional, selected with an explicit pinned request and the existing direct
workflow fallback when unavailable. This avoids an unconditional reciprocal
cycle. Help's routing table is qualified discovery advice rather than a graph
that requires every suggestion. Required conditional routes prepare their
instructions without executing them. All new edges are Pack-local and legal
closure stays acyclic.

## Complete supporting review

The two mode trees each retain all 23 native playbooks, review guidance and the
complete script/package/lock/test tree. Separate `ACCESS-` copies adapt every
playbook and the Bugbot reference. Help retains its native prompting/recipe
references and adds qualified access copies. Each access copy is declared for
explicit reference rendering. Original helper bytes and executable bits stay
unchanged; the unused common bootstrap is not the effective implementation.

| Supporting family | Review result |
| --- | --- |
| Feature, refactoring, bug fix, perf, hillclimb | Prepared how/why/architect/arena, principles and conditional pstack TDD; retain reproduction, throughput, smallest evidence-backed change, measurement and review separation. |
| Investigation, prototype, visual parity, runtime/trace forensics | Keep read-only and throwaway boundaries, actual control/artifact evidence and honest confidence; selected access resources retain one context. |
| Authoring, eval, multi-phase planning | Keep host authoring fallback, blinding/diverse judges and transcript gaps; planning remains planning-only until an explicit go. Skeleton references prepared resources and writable plan/evidence paths. Plan checker remains an inert immutable input until explicitly run. |
| Babysit, shipping, autopilots, opening a PR | Preserve modes, frozen queues, exact patch/head verdicts, human merge authority, forge gates, independent live review and stack topology ownership. Host integrations remain optional as defined by source. |
| Autonomous run, orchestrate, session pickup, pause | Preserve falsifiable stop predicate, decision trails, queue/ledger ownership, exact-head bookkeeping, source-defined program collapse, continuity and explicit pause. Monitoring is active-session-only without a verified scheduler. |
| Worktree retirement and review guidance | Audit advice is not deletion approval; check pinned/in-use chats and unknown history. No destructive fixtures. Review comments remain untrusted input; preserve fix/dismiss/ask and security escalation. |
| Helpers and legal resources | Node plan checker reads explicit input. Bun orch uses explicit store and target repo. Watcher requires selected forge/runtime; audit requires Bash/Git/forge/shell utilities. The existing bootstrap copies to separate temporary execution space, installs frozen dependencies there, reexecutes in the target cwd and removes staged state on supported completion/failure. Owned outer temporary state covers interrupted probe cleanup. Common originals, provenance and both notices remain untouched. |

Every nested or selected optional retrieval carries the initiating explicit host
and immutable snapshot. Delegates receive that identity, target, prepared entry
and resource paths and separate writable scratch/output destinations. A selection
change affects only new independent requests. Missing retained files fail without
latest-revision fallback. Generated skills and orchestration state never belong
inside immutable prepared resources.

## Public-boundary acceptance

The issue and parent spec pre-agree the released CLI and helper interfaces as
seams. The initial committed public retrieval test fails on the old content with
`incompatible_resource` for missing reviewed compatibility. The access adaptation
then supplies the complete required tree. Content-policy assertions complement
full-tree byte/mode/rendered-reference comparisons; they do not simulate a model
successfully following all workflows.

From a clean committed checkout with the clean 5.1.0 baseline:

```sh
python3 -B scripts/probes/content-probes.py --scenario pstack-orchestration \
  --pstack-baseline /path/to/clean-5.1.0-catalog > /tmp/pstack-orchestration-evidence.json
```

The opt-in scenario consumes only the verified released binary declared by
`packy-release.json` and builds complete committed candidate/baseline snapshots.
It discovers/retrieves all 55 skills per host, checks independently reviewed
closure expectations, metadata, prepared files, actual supporting content,
rendered references, notices, modes and unverified prerequisites. Retrieval PATH
contains no content runtimes. A modified native help copy, native/activation
state, target project and immutable trees must stay unchanged.

The selection transition exercises a playbook's pstack TDD, figure-it-out's
principles and decision trail, automate-me's mode/unslop, help's optional TDD and
bespoke workflow, and mode's optional bespoke route. Old paths remain usable;
new independent calls use the selected baseline; a missing retained playbook
fails. Scoped native installation preserves original contracts/bytes/modes,
unrelated resources and inactive personal state. Existing foundational and
engineering scenarios remain separately runnable against their original
pre-adaptation baselines; the complete inventory scenario rechecks their full
access/content closure against the current integrated baseline.

After content review, helper probes run positive and two rejecting plan fixtures,
owned orchestration unit/ledger roundtrips, watcher help/usage and a controlled
external-query failure. A disposable bootstrap consumer verifies actual temporary
dependency installation, reexecution cwd, propagated failure status and cleanup.
A bounded interruption is cleaned through the outer owned lifecycle. No fixture
merges, sends messages, provisions a network service or removes a worktree.
All child processes are bounded under explicit HOME/config/data/cache/temp state;
sources and unrelated target bytes remain unchanged and owned state is removed.
Node, Bun and package-network access are execution prerequisites for these opt-in
checks, never retrieval requirements.

Complete-catalog/baseline validation, ordinary tooling checks, independent Standards
and Spec review and manual released-CLI inspection bind to the final candidate
SHA. Candidate consumption is not official publisher verification. These receipts
prove resource access and safe representative helpers, not autonomous workflow
success. Ordinary validation/build/publication remain inert. Protected integration
and the existing successful-main publication workflow retain authority.
