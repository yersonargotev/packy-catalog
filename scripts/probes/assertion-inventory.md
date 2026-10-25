# Adoption and Ponytail assertion migration (#55)

This inventory precedes removal of `TestCatalogAdoption` and
`ponytail_install_test.go`. `content-probes.py` invokes the actual pin in
`packy-release.json` through the supported `catalog candidate` authoring seam.
Every scenario uses the same complete built snapshot and a separate owned
workspace. Local candidates remain unauthenticated publication inputs.

| Displaced assertion | Equivalent Catalog scenario or Packy-owned fixture |
| --- | --- |
| Acquire the complete Catalog and keep it readable | `adoption`: `list --json` must contain exactly every Pack in the complete build index, before and after rejection |
| Reject incompatible index, preserve selected bytes and prior usability | `adoption`: checksum-correct schema-999 negative fixture fails against both an existing workspace (entire tree unchanged, prior list works) and a new path (no workspace created). Official selection bytes and authenticated acquisition belong to Packy's `internal/catalogstore/store_test.go`, `TestFailedAcquisitionPreservesPreviousSelection`; candidates never create an official selection |
| Install/uninstall Emil common resources on Codex, Claude and OpenCode | `adoption`: real approved install, portable verification, approved uninstall on each surface; no managed contract, notices or skills remain, unrelated guidance/files preserved |
| Ponytail complete, one skill, or instruction-only selection on every surface | `ponytail`: nine cases assert each of the six named skill files, frontmatter, required absences, and guidance presence/absence |
| Read-only preview | `ponytail`: entire already prepared workspace (project, personal roots, retained snapshot, ownership marker and file modes) unchanged after `--dry-run` |
| Preserve existing guidance and include upstream notice | `ponytail`: original guidance retained and copyright attribution required for each selection |
| Portable verification | `ponytail`: `verify --json` must pass after installation and for retained Argote guidance after Ponytail removal |
| Skill-only coexistence with Argote | `ponytail` skill cases install Argote guidance first, retain it after Ponytail install/removal, verify it, then retire Argote separately |
| Shared instruction path ownership conflict | `ponytail` complete/instruction cases reject Argote preview with `projection_collision`; entire workspace unchanged |
| Personal configuration preservation | Every Ponytail case seeds both isolated personal roots, then compares complete bytes/modes through install and uninstall; ambient HOME/config/data remain unchanged across all scenarios |
| Uninstall restores instructions, removes Ponytail skills, retires final contract/notices | Every Ponytail case verifies retained instruction bytes (ignoring the engine's separator newlines), no `ponytail*` roots, unrelated files preserved, and no final `packy.json`, lock, notices or managed skills |
| Injected fake host runner and automatic terminal consent | Replaced with Packy's candidate host-execution prohibition and Catalog's controlled stdin PTY: only one exact prompt bound to the fresh preview observation is answered. No host authentication, model call or activation offer |

Packy engine fixtures at pinned revision
`1b8d04ddee510b24adcb12906914240bd7063aa6` own official acquisition,
attestation, archive integrity, workspace ownership, and consent internals:
`internal/catalogstore/store_test.go`, `internal/cli/catalog_candidate_test.go`,
and the native release scenario `internal/ci/catalog_candidate_test.go`.
Catalog negative fixtures deliberately alter only an index schema and its
archive checksum; they are not a second builder or a publication.

The final `adoptionRelease` shared helper and `pstack_lifecycle_test.go` were
retired after the released-binary pstack scenarios below passed. No copied
Go overlay or engine-source prerequisite remains. #49 is overlapping prior art; its source-checkout
acquisition model is superseded for these scenarios, and that issue is unchanged.

## Claude assertion migration (#56)

This inventory accounts for `TestClaudeProjectInstall` before removing
`claude_install_test.go`. `--scenario claude` shares the verified executable,
one complete snapshot, isolated environment, bounded process, exact-preview
approval and structured evidence contracts established by #55.

| Displaced assertion | Equivalent released-binary behavior |
| --- | --- |
| Complete, eli5-only and html-plan-only on Claude, Codex and OpenCode | Nine `claude` cases install each selection and assert skill frontmatter plus absence of unselected roots |
| Read-only project/home preview | Entire prepared workspace bytes/modes, including project, personal roots, snapshot and ownership marker, unchanged after dry-run |
| Complete HTML runtime closure | Complete/html-plan selections require `runtime/htmlplan.js`, `runtime/htmlplan.css`, `runtime/pack.mjs`, `references/blocks.md` and `examples/scheduled-send.html` in the installed skill |
| Apache license and exactly selected skill metadata notices | Each selection requires Apache attribution text and includes eli5/html-plan metadata iff the corresponding skill was selected |
| Local guidance and Argote coexistence | Install Argote guidance first in every case; project guidance bytes remain equal after Claude install and uninstall |
| Portable verification | `verify --json` passes after Claude installation and again with retained Argote after Claude removal |
| Personal configuration preservation | Both isolated home/config trees compared immediately after install and uninstall; common runner also preserves ambient home/config/data |
| Uninstall removes both Claude skill roots and preserves Argote/local guidance | Each case checks root absence and retained instruction bytes, then removes Argote and checks final contract/notices/skills absence and unrelated files/modes |
| Engine-internal fake host/terminal/source injection | Candidate host prohibition and official trust mechanisms remain Packy-owned; common runner uses single-use exact-preview PTY consent without live hosts/authentication/models |
| Optional HTML packing smoke command | `--html-pack` executes installed packer only in complete/html-plan cases; requires success, no reported errors, exact inlined CSS/JS bytes, no external runtime links and packed digest. Fictional `<doc-calls>` source warnings are recorded separately from other warnings |

Ordinary CLI fixtures use a real pinned binary, inert fictional Pack content
and a controlled Node transport. They cover all nine selections, optional
packing warning classification, missing Node, and checksum-valid content
missing `runtime/htmlplan.js`; they never execute the shipped HTML packer.
Real reviewed content and optional Node execution remain opt-in.

## pstack assertion migration (#57)

This inventory accounts for every `TestPstackCatalogVariants` assertion before
removing `pstack_lifecycle_test.go` and its final `adoptionRelease` caller.
The `pstack` scenario uses one complete candidate and an explicitly supplied
clean committed complete baseline, both built by the same verified release.
The documented baseline is `7a8597e6f0c3867540e342070fed46f97a2e1bfb`
(pstack 3.0.0), preserving the original common-to-host-variant transition.

| Displaced assertion | Equivalent released-binary behavior |
| --- | --- |
| Complete baseline and candidate snapshots in both global/project scope | Full released `catalog build` of both checkouts; install/activate baseline on Codex and Claude in separate owned project/global workspaces |
| Acquire candidate while retaining baseline installations | Supported digest-bound `transition --json`; require candidate/baseline archive identities and local provenance, with home/config/project bytes/modes/links unchanged |
| Targeted Codex update selects Codex definition and preserves Claude | Real `update` (with `--project` for project scope); require `## Codex execution` in installed `reflect`, compare complete Claude tree including link targets and linked file bytes/modes |
| Targeted Claude update selects Claude definition and preserves Codex | Require `## Claude Code execution`; compare complete Codex tree |
| OpenCode divergent coexistence rejection without state changes | Applicable operation's dry-run fails with coexistence diagnostic; entire prepared workspace unchanged, so rejection cannot pass merely because consent is absent |
| Bootstrap helper drift blocks removal | Mutate only disposable installed `bootstrap.ts`; removal preview must fail for projection drift or retained index identity, workspace unchanged; restore exact bytes/mode before removal |
| Remove Codex without affecting Claude, then remove Claude | Exact-preview approved uninstall/deactivate; complete Claude tree unchanged after Codex removal |
| OpenCode installs its own definition after conflicting projections retire | Real install/activate, require `## OpenCode execution`, then approved uninstall/deactivate |
| Architect selection includes variant-only dependencies | Architect-only install/activate requires exhaust-the-design-space, fix-root-causes, prove-it-works, redesign-from-first-principles; unrelated reflect absent |
| Scope isolation, original files and complete retirement | All three skill roots empty/absent; inactive project or personal roots unchanged, sentinel files retained, project final contract/lock/notices absent; ambient state preserved by common runner |
| Injected fake source, host and terminal | Real released candidate route and controlled ordered single-use preview/plan PTY approvals; official trust, no host execution and isolated global roots remain Packy-owned contracts |

Packy v0.2.28 (`eed834cb34dbcc15cdb6164caaa94083392f51f6`) owns
synthetic mechanism coverage in `internal/cli/issue842_candidate_test.go` and
the native `internal/ci/catalog_candidate_transition_test.go` contracts.
Catalog owns the actual pstack content assertions above. Controlled ordinary
fixtures contain inert replacement skill/helper text and no upstream origins;
they exercise both scopes and reject an omitted effective dependency. They
never execute shipped resources. Independent `pstack-update.py`, its opt-in
tests, `pstack-helpers.py` and `pstack-host-loading.py` remain opt-in;
they already require no Packy source and are not part of ordinary CI.

Controlled runner-boundary fixtures live in
`scripts/tests/test_content_probe_runner.py`. They execute only temporary Python
children and Git/prerequisite fixtures, covering exact and repeated/unexpected
prompts, structured preview, child failure, timeout/descendant cleanup,
interruption cleanup, stripped credentials, dirty candidates and missing
prerequisites. They are safe for the ordinary inert suite.

## pstack OpenCode withdrawal (#104)

The `pstack` lifecycle scenario now rejects new OpenCode installation and retains
Codex/Claude coexistence, drift and retirement checks. `pstack-withdrawal` adds
complete two-host preservation and legacy OpenCode project/personal retirement
through the released public CLI. It proves unsupported new requests, failed
updates without mutation, installed/retained ownership, drift, missing personal
retained content, explicit retirement and unrelated-state preservation. Native
foundational coverage follows the accepted two-host policy. Other Packs retain
all their host coverage. No ordinary check executes these real-content probes.
