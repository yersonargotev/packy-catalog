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

`catalog_adoption_test.go` now retains only `adoptionRelease`, still imported
by `claude_install_test.go` (#56) and `pstack_lifecycle_test.go` (#57). Remove
that helper when its last consumer migrates. Neither remaining overlay is
executed by the new runner or ordinary CI. Their legacy setup remains
documented until migration. #49 is overlapping prior art; its source-checkout
acquisition model is superseded for these scenarios, and that issue is unchanged.

Controlled runner-boundary fixtures live in
`scripts/tests/test_content_probe_runner.py`. They execute only temporary Python
children and Git/prerequisite fixtures, covering exact and repeated/unexpected
prompts, structured preview, child failure, timeout/descendant cleanup,
interruption cleanup, stripped credentials, dirty candidates and missing
prerequisites. They are safe for the ordinary inert suite.
