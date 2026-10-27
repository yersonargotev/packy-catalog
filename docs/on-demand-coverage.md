# Integrated on-demand coverage

This inventory and its acceptance commands record the previous Catalog
generation. Their Codex/OpenCode support claims, source fingerprints and probe
results are historical, not evidence for the current `agents` and `claude`
generation. The historical probe requires its original checkout and binary;
with v0.2.32 the current runner rejects it. See the
[current setup](packy-cli.md) and [two-surface candidate probe](../scripts/probes/README.md#two-surface-candidate-acceptance).

The [review inventory](on-demand-coverage.json) accounts for exactly **117 unique
qualified logical skills and 234 host cases**: Matty 33, pstack 55, Warp 29, each
on Codex and Claude Code. The scope comes from the approved parent and eight
reviewed slice matrices, not from enumerating whichever resources a future
candidate happens to expose. Each identity occurs once, with both hosts assigned.

Each entry records its review document, required/conditional/optional reference
classification, preserved interaction/approval/stopping rules, supporting content,
independently reviewed direct access edges, and each host's effective source,
prerequisites, explicit rendered-reference files, native requirements and complete
source-tree fingerprint. Pack-level legal expectations retain actual notice bytes
and modes. The frozen content baseline is Catalog
`4593c4a45c0060109ad67ec36e0668008d41653f`; it is a review observation, not a CLI
release pin or a constraint on future Pack versions. Content migrations must
review/update the affected inventory expectations alongside their owning Pack.
Never regenerate expected coverage silently during acceptance.

A source-tree fingerprint is SHA-256 of compact JSON containing ordered
`[relative_path, permission_bits, file_sha256_or_null]` entries, including
directories. The integrated probe additionally compares every prepared file to
its effective authored source, rendering only declared access tokens, and checks
actual relative links, assets, modes, manifests and legal closure. Preparation
covers the union of native skill requirements and access dependencies; a
conditional branch's resource availability does not authorize that branch.
Optional recommendations and external/native capability prerequisites remain
distinct from required Catalog edges.

| Pack | Reviewed slices | Logical identities | Host cases | Native support |
| --- | --- | ---: | ---: | --- |
| Matty | [Design/planning](design/matty-design-on-demand.md), [delivery/writing](design/matty-delivery-on-demand.md) | 33 | 66 | Codex, Claude, OpenCode |
| pstack | [Foundational](design/pstack-foundational-on-demand.md), [engineering](design/pstack-engineering-on-demand.md), [orchestration](design/pstack-orchestration-on-demand.md) | 55 | 110 | Codex, Claude; OpenCode withdrawn under [ADR 0003](adr/0003-limit-pstack-host-support.md) |
| Warp | [Specification](design/warp-specification-on-demand.md), [repository/reporting](design/warp-repository-on-demand.md), [skill-doctor](design/warp-skill-doctor-on-demand.md) | 29 | 58 | Codex, Claude, OpenCode |

Historical matrices describe their own delivery slices and baselines. Their
statements about subsequent work were true at those deliveries; this inventory
is the current consolidated scope. Dated installation research remains
non-normative. No installed selection or procedure policy is merged or migrated.
pstack's withdrawal/legacy-retirement evidence is retained in [its operator
guide](pstack-opencode-retirement.md); integrated retrieval does not change that
contract. Matty/Warp retain native OpenCode installation, without OpenCode
on-demand compatibility.

## Historical integrated contract

After reviewing content, use a clean committed checkout:

```sh
python3 -B scripts/probes/content-probes.py \
  --scenario integrated-on-demand --integrated-helpers \
  > /tmp/integrated-on-demand-evidence.json
```

The single `packy-release.json` declaration, acquisition/embedded-identity
verifier, bounded subprocess runner, exact-preview lifecycle consent, disposable
candidate workspaces, receipts and cleanup are reused. Requirements are Python
3.9+, curl, Git and upstream HTTPS for acquisition/build; reviewed helper execution
also requires Node, Bun and package-network access for disposable dependency
staging. No runtime is provisioned by retrieval. Offline retrieval uses an OS
network boundary: macOS `sandbox-exec`, or Linux `unshare` with permitted user and
network namespaces. A network-denial canary must pass; unavailable isolation fails
rather than reporting offline success. Ordinary tests, validation, construction
and publication never invoke this opt-in scenario or execute Pack content.

The report identifies the exact committed Catalog candidate, release/source
identity, builder, archive digest, inventory digest/baseline, fixture source
commits/archive digests, selected coverage and every bounded command outcome.
Candidate inputs remain unauthenticated authoring data, not official publisher
attestation evidence. The two committed inert fixture revisions are created only
under owned temporary state and never enter official publication inputs.

Coverage includes sequential personal/project bootstrap setup and explicit
retirement for both hosts while preserving unrelated Packs, unmanaged native
skills, the other host and inactive scope; 234 complete qualified root retrievals;
unverified prerequisites with content runtimes absent; deterministic duplicate
TDD discovery and rejection of an unqualified retrieval; actual modified managed
native copies; Matty's pinned nested wrapper with pstack active; non-Git access;
explicit missing-catalog guidance; and same-/cross-Pack fixtures with supporting
references, meaningful assets, scripts and legal closure. A digest-bound selection
transition exercises pinned nested requests and earlier paths, independent new
requests and missing-retained-content rejection without newer/native substitution.
Target/native/activation, authored, retained and prepared trees are observed by
bytes, modes and links. Provider-owned resource preparation is allowed.

`--integrated-helpers` executes both effective pstack temporary bootstraps, their
positive/rejecting plan and bounded success/failure/interruption fixtures, and
the decision-log helper; Warp's explicit target resolver with a meaningful cache
decoy, review validator and reporting fixtures; and fictional skill-doctor
collectors, renderer and bundled tests. Outputs and dependencies stay separate
from immutable resources and target inputs. These checks use no live history,
credentials, paid inference, real forge writes or arbitrary skill workflows.
Without that flag, the report explicitly marks helper evidence unselected; that
run alone is not full acceptance of #99.

The integrated scenario runs independently and reports exactly Codex and Claude;
combining it with historical scenarios or selecting OpenCode access is rejected.
Historical slice transition/native regression scenarios remain independently
runnable with their documented pre-adaptation baselines. Do not pass the current
integrated baseline to every historical scenario: their availability preconditions
differ. This delivery changes no Pack-owned content or versions; the frozen review
and complete prepared-tree checks complement the existing native regression and
pstack withdrawal receipts without relabeling those historical receipts as new
execution evidence.

## Evidence boundaries

Static review and deterministic metadata demonstrate scope and resource access,
not model-driven intent matching. The agent must ask for ambiguous requests.
Helper success and fictional report scores prove only the asserted fixture
behavior, not scoring quality, unattended applicability or semantic completion
of every workflow. Required user interaction, approval, model diversity, external
capabilities and retirement stops remain in the returned procedures. In
particular `warp:scan-new-specs` stays retired.

Real-host loading is optional and is not run by this contract. Any separately
retained evidence must name exact Codex/Claude versions, supported host floors,
selected surfaces and isolated setup, and say whether it proves discovery/loading
only. Native installation or a manifest binding is not such evidence. No fixture
result proves live host interaction, browser rendering or model-backed execution.
Only protected integration and the existing successful-main workflow publish
official Catalog Snapshots; no second release is created here.
