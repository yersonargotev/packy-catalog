# Warp skill-doctor: reviewed on-demand access

This review records its original Catalog generation. Surface names, Pack
versions, and acceptance evidence below are historical; see the
[current setup guide](../packy-cli.md) for the `agents` and `claude` contract.

[Issue #98](https://github.com/yersonargotev/packy-catalog/issues/98) covers exactly
`warp:skill-doctor` on Codex and Claude Code. Warp advances from 2.4.0 to 2.5.0
against Catalog baseline `cac283b0e829bd9a88233eb1050a4e49a2316019`.
The upstream remains `warpdotdev/common-skills@8792394ff1b655e0af451b8fabb68ef0cfcbd208`.
Other resources, Packs and the central released-engine declaration are unchanged.
Initiative-wide inventory and consolidated operator guidance remain in #99.

## Reviewed contract

The effective `ACCESS.md` retains the original procedure with explicit returned
`resource_root`, intended target directory, history and skill inputs, and separate
writable report/scratch context. All original native files retain their bytes and
modes: collector, Warp decoder, renderer, 37 bundled tests, four rubrics, references,
UI assets (including the diff bundle's embedded notices), and native `SKILL.md`.
The complete tree is now an adaptation because it adds the access entry. Original
origin identity/path, Warp MIT and Catalog adaptation notices, native bindings,
invocation names and requirements remain intact on all three native hosts.
Only Codex and Claude variants declare `skill-tree-v1`; there is no required
skill dependency. Rubrics/references are supporting files, not skill edges.

Retrieval is inert. It does not read histories, ask startup questions, collect,
create output, invoke inference or workers, open a browser, upload, provision
runtimes or edit installed skills. The returned known prerequisites remain
unverified; missing Python or other execution capabilities do not block access.
Native bindings and descriptor surfaces never replace actual runtime harness
identification. The supported-harness reference remains the source of truth,
including the unsupported/unknown stop before reading history or making output.
OpenCode installation remains available; this does not make its executing
harness supported by skill-doctor.

Execution first identifies its actual host, then asks the original conversation
scope question with repository-dependent choices/recommendation, validates any
chosen projects, and asks the original project/global skill question. Both
questions and any project-path question require actual replies using an available
host question control or conversation fallback. Repository detection uses the
intended directory, independently of cache placement. Executing host and history
sources remain distinct: default `--harness auto` scans all available supported
sources; explicit source selectors and home overrides retain their meanings.

After the replies, choose a fresh collision-free directory outside target and
immutable trees. Inventory, sampled transcripts, scoring/report data, proposed
files, rendered HTML and generated Python state stay in this owned destination.
Use absolute `--repo`, `--out` and report-input paths; `--skills-dir` identifies
extra intended inputs. Invoke Python with `-B` or equivalent suppression, and
keep temp/cache state under the report directory. The renderer finds its bundled
UI relative to its prepared script and writes beside the explicit report input.
Render first; browser opening is a separate authorized host capability.

Local-only transcript handling, four scoring rubrics, curved aggregation,
insufficient-evidence rules, empty-session stopping, zero-skill behavior,
failed-conversation-only suggestions and improvement guidance remain intact.
Only proposed files change; applying or sharing remains the user's choice.
Local child scoring is conditional on keeping transcripts on the machine; the
original current-local-process path remains available. Missing local scoring
capability is a prerequisite gap, never simulated success.

Initiating surface and immutable `snapshot_id` travel through any authorized
delegation/nested request. Explicit selection changes affect new independent
requests; old prepared paths remain usable. Missing retained content fails without
latest-revision or modified-installed-copy substitution. No refresh, provisioning
or resource expiry/cleanup is introduced.

## Verification and limits

The pre-agreed acceptance seam is the released Packy public CLI plus the
collector/renderer CLIs. Test-only candidate
`b044bc6c63989f2fd117fd4d4bc2a8f0d5cac5f5` built a complete Catalog Snapshot with
archive SHA-256 `47f0c3cbb0976c2b77c0efcbe6c40e027a751f4913f7f18db0dc5b574584e8cc`.
Its actual Codex retrieval failed with structured `incompatible_resource` before
the adaptation. Run the positive contract from a clean committed candidate:

```sh
python3 -B scripts/probes/content-probes.py --scenario warp-skill-doctor \
  --warp-baseline /path/to/clean-2.4.0-catalog \
  --warp-helpers > /tmp/warp-skill-doctor-evidence.json
```

Without `--warp-helpers`, this only reads reviewed content through the verified
central release. It constructs complete candidate/baseline snapshots and checks
both host descriptors, independent empty dependency closure, every resource and
legal file's bytes/modes, usable relative resources and unverified prerequisites.
Retrieval runs without content runtimes and preserves the target, installation,
activation, locally modified native doctor, snapshot and prepared trees. Explicit
selection transitions check pinned re-entry, prior paths, new independent selection,
and missing-retained-bundle failure. Native regression installs this exact skill
on Codex, Claude and OpenCode while preserving unrelated resources and personal
state. It compares all original native bytes/modes with the clean baseline.

The optional helper fixture executes only the reviewed prepared collector,
renderer and their bundled tests. Its fictional inputs comprise two repositories,
one empty repository, Codex/Claude histories, project/global/extra skills and
predetermined report data. Fifteen collection cases cover individual and mixed
sources, project/all/empty scopes and global/extra skill selection. They check
actual inventory, selected skill usage and sampled transcript contents, including
absence of the unselected conversation. Rendering checks substantive findings,
suggestions, decodable diff, usable proposed file, the complete embedded prepared
UI bundle, preserved input JSON/proposed bytes, and rejection of missing input.

Children have bounded execution with owned HOME/config/data/cache/temp roots.
Python audit hooks prohibit sockets, browser calls, file content reads outside
fixture/resource/runtime roots, writes outside owned output/runtime roots, and
subprocesses other than the reviewed Git repository-root queries. Full byte/mode
observations preserve fictional histories/skills/targets and prepared content;
no bytecode may appear in input/resource trees. Runner-owned execution state is
removed on success, failure and handled interruption. Ordinary tests, validation,
build and publication never execute Catalog content.

These receipts establish retrieval, native projection and safe collection/fixture
rendering. They do not establish actual host startup interaction, native discovery,
all native history formats, model-backed scoring or improvement quality, browser
rendering/PNG export, live-history operation, external uploads or real installed
skill edits. No inference, paid model, live credentials/history, external API,
worker launch or browser participates. Exact candidate/full-suite/review/CI receipts
belong in the delivery PR. Protected integration and successful-main publication
remain authoritative; there is no second manual release.
