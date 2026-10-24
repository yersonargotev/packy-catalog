# Matty design and planning: reviewed on-demand access

This review covers exactly the 19 logical skills in [issue #91](https://github.com/yersonargotev/packy-catalog/issues/91)
on Codex and Claude Code. Matty advances from 4.0.0 to 4.1.0; its upstream remains
`mattpocock/skills@d81f3a183412e71a5b1e84ca21bc1a35eea03a60`.
This is a Catalog contract migration, not an upstream refresh.

## Resource access and native behavior

Each reviewed resource has an alternate `ACCESS.md` entry under `skill-tree-v1`.
It preserves source frontmatter and routes to the original procedure where no
installation-dependent calls need adaptation. The seven calling/suggestion
procedures use reviewed bodies with explicit qualified `packy.access` links or
qualified next-session guidance. Every nested request carries
the initiating explicit host and immutable snapshot. Missing retained content
requires restoring that revision. An installed or foreign same-name skill cannot
replace the named Matty resource.

The small on-demand context is repeated at standalone entries so each root has
its own retrieval context without adding a synthetic skill dependency. All original
`SKILL.md`, references, metadata, templates, and modes remain byte-identical.
Prototype keeps its original logic/UI guides and capture backlinks; both return
to the same preserved procedure within the returned resource tree.
Origins mark the complete changed trees as adaptations, retaining upstream paths
and the original MIT notice. The other 14 Matty skill definitions and every other Pack remain
unchanged; the shared legal closure gains the Catalog adaptation notice. OpenCode receives its existing native procedure, without new on-demand
support. No live installation is updated. The imported MIT notice points to a terminal,
Catalog-authored MIT notice for these adaptations instead of referencing itself.
The released contract requires imported notices to retain a legal reference and
rejects cycles during on-demand graph validation. Every skill still includes the
unchanged upstream MIT notice, now with the additional Catalog adaptation notice;
native skill selection and original source bytes remain intact.

Native `requires` edges retain their original installation semantics. The reviewed
`on_demand.dependencies` graph below supplies required resource availability;
conditional edges prepare instructions but do not execute the conditional branch.
No unqualified native Skill-tool call is needed to follow the adapted procedures.

## Reviewed matrix

Both hosts use the same reviewed entry. The manifest records sorted known
prerequisites; discovery explicitly reports that they are unverified. Requirements
below concern subsequent execution, never permission to execute during retrieval.

| Skill | Direct on-demand dependencies | Preserved interaction/output and execution requirements |
| --- | --- | --- |
| `codebase-design` | None | Exact module/interface/depth/seam/adapter/leverage/locality vocabulary; DEEPENING and DESIGN-IT-TWICE references. Alternative interfaces require background agents. |
| `domain-modeling` | None | Challenge terminology, record resolved terms lazily in the target glossary, offer ADRs only under its three conditions; both format documents preserved. Target write access when recording. |
| `grilling` | None | Numbered frontier rounds with recommendations; wait for answers each round and final shared-understanding confirmation before acting. Background agents find environmental facts. |
| `grill-me` | `grilling` | User-only wrapper follows Matty's own primitive, preserving its rounds and final confirmation. |
| `grill-with-docs` | `domain-modeling`, `grilling` | User-only wrapper follows both Matty primitives; domain writes stay in the target project. |
| `improve-codebase-architecture` | `codebase-design`, `domain-modeling`, `grilling` | Repository/background exploration, OS-temp HTML report with original CDN assets/scaffold, candidate choice before interviewing, inline resolved terms and offered ADRs; alternative-interface branch stays conditional. |
| `to-questionnaire` | None | Interview the send/recipient and knowledge gap in separate exchanges; write the original questionnaire shape to the target current directory. This is its own interview, not an implicit grilling dependency. |
| `to-spec` | None | Synthesize existing conversation without a new interview; confirm test seams with the user; configured tracker and role mapping; preserve full spec template. |
| `to-tickets` | None | Vertical slices, dependency edges, user-approved breakdown before publishing, original local/remote templates; preserve parent issue. |
| `triage` | `domain-modeling`, `grilling` (if clarification is needed) | Maintainer recommendation/direction, verification before conditional interview, configured canonical-role mapping, AI disclaimer on every tracker post, original agent-brief/rejection guidance. |
| `wayfinder` | `domain-modeling`, `grilling`, `prototype`, `research` | Qualified access in research/prototype/interview branches; target tracker map/child/blocking operations, claim-first discipline, human answers for HITL, one ticket per session except research; research uses background agents. Notes may request additional qualified skills, resolved in the same snapshot with invocation policies preserved. |
| `loop-me` | `grilling` | Stateful grilling discipline, source loop/workflow vocabulary, target `workflows/*.md` specs and `NOTES.md`; no mandated structural AI/checkpoint/schedule. |
| `setup-matt-pocock-skills` | None | Prompt-driven exploration, one section/answer at a time, draft configuration/instruction confirmation before writes, original file-selection rules and all five seed templates. Triage's installed/available status remains a fact to inspect, not an automatic dependency installation. |
| `wizard` | None | Genuinely human-only steps; confirm ordered stages and captured values; copy the immutable Bash template to writable target/scratch, preserve its library, verify statically and hand off; human confirms irreversible actions. No template execution during retrieval. |
| `writing-for-agents` | None | Original context pointers, hierarchy, completion criteria, invocation/router mechanics; SKILL-MECHANICS preserved. |
| `wait-what` | None | User-only re-explanation in source-defined ASD-STE100 Simplified Technical English with target glossary terminology. |
| `handoff` | None | User-only, redacted handoff in the OS temporary directory; reference existing artifacts. Suggested next-session skills are qualified recommendations with host/snapshot context, not mandatory dependencies or automatic invocations. |
| `research` | None | Requires an available background-agent capability, primary sources and cited Markdown in the target repository's existing notes convention. Retrieval does not run research. |
| `prototype` | None | Logic HTML versus UI variants chosen by the design question; target-local throwaway code, no default persistence, capture validated answer and full prototype on a throwaway Git branch with issue pointer, keep only the decision on main. Browser and UI runtime readiness remain execution checks. |

Setup reminders in planning skills, descriptive references in setup/domain
consumer templates, and handoff suggestions remain recommendations, not mandatory
graph edges. Preparation is not a model-driven interview, runtime readiness,
tracker setup, document generation, research result, prototype, or provisioning.

## Acceptance

Run from a clean committed candidate and clean pre-change complete baseline:

```sh
python3 -B scripts/probes/content-probes.py --scenario matty-design \
  --matty-baseline /path/to/pre-change-catalog > /tmp/matty-design-evidence.json
```

The existing runner acquires only `packy-release.json`, builds both complete
catalogs and records exact commits/digests. Its existing candidate route, isolated
HOME/config/data/cache/project roots, bounded process runner, receipts and cleanup
remain authoritative. The baseline must predate this on-demand adaptation so a
controlled availability transition can distinguish new requests from retained ones.
No fixture catalog is published.

Acceptance covers all 38 roots; qualified identities, version, explicit host,
snapshot, direct reviewed declarations and complete dependency closure; all source,
supporting-resource, notice and mode comparisons; real relative Markdown targets;
modified installed-copy preservation; and absent content runtimes. Wrapper and
wayfinder nested requests retain the original snapshot after a digest-bound
transition to the baseline, while independent requests see baseline incompatibility.
Missing original retained content fails explicitly, including when the candidate
integrity guard rejects the altered retained tree before access dispatch. Native installation of all 19
skills on Codex, Claude and OpenCode preserves original selection, contracts,
source bytes/modes and project verification. Target/installation and authored
immutable trees are observed throughout. HOME comparison permits only the
candidate provider's skill-access preparation data, while preserving native
roots, configuration, and every other HOME entry. Nested preparation may return
a different location for the same qualified resource; both copies must retain
identical snapshot/content, and prior references must remain usable. Ordinary validation/publication remain
inert and never invoke this scenario.

The first public wrapper check was recorded red on committed candidate
`19986c190c1205a580f47c8c38ce18556f713dc4`, before any resource adaptation.
The final delivery evidence binds successful acceptance to its final candidate SHA;
these checks establish resource access, not semantic execution of the procedures.
