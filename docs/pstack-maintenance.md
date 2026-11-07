# How pstack is maintained

Packy manages one `pstack` Pack. A qualified identity such as
`pstack:poteto-mode` selects the same logical skill on either supported surface.
The manifest selects the reviewed source for that surface.

## Source layout

- `packs/pstack/skills/<id>` retains the original Cursor skill where the
  resource declares `exact-copy` provenance.
- `packs/pstack/skills/agents/<id>` contains the Agents adaptation.
- `packs/pstack/skills/claude/<id>` contains the Claude adaptation.
- `packs/pstack/skills/shared/<id>` contains one host-neutral adaptation that
  both surface variants select. It is used where the hosts differ only in the
  execution preface: the principles, `blast-radius`, `bro`, `correct`,
  `in-your-own-words`, `ketchup`, `sharpen`, `tdd`, `teach`,
  `technical-writing` and `unslop`.
- `packs/pstack/skills/statechart` contains a shared portable adaptation.

The former `skills/codex` directory is now `skills/agents`. This aligns source
paths with Packy's supported surface name. Some Agents workflows still require
Codex capabilities. Their prerequisites say so. Client settings such as
`~/.pstack/codex-models.md` and `agents/openai.yaml` retain their client meaning.

These directories are Catalog sources. They are not three installations.
Packy installs only the selected surface's effective source. Native use reads
`SKILL.md`; reviewed on-demand access reads `ACCESS.md` and its declared closure.
Each pair preserves the workflow while adapting dependency lookup and writable
output locations. Editing one entry requires checking its counterpart.

A shared tree names each host's roots, delegation tool and preference file in
one `## Host execution` section. Its frontmatter keeps Claude's
`disable-model-invocation`, and `agents/openai.yaml` keeps Codex's manual-only
policy; each host ignores the other's control. Move a skill back to separate
host trees when its workflow needs host-specific steps beyond that section.

## Shared runtime distribution

`statechart` has no host-specific delegation or configuration. Both surfaces
therefore use one adapted tree. Its production TypeScript files, shell launcher,
and render reference come from the pinned upstream revision. The adaptation adds
Packy execution guidance, explicit invocation metadata, and on-demand access.
Its package metadata omits test commands and development dependencies.

The upstream development tests and recorded TLC corpus are not distributed.
The complete original has 407 files, including 376 files under `scripts/test`.
Retaining that tree in addition to the existing original and host adaptations
would exceed the pinned engine's 1,024-entry Pack budget.

This new resource has an explicit exception to the full-original retention
policy recorded in ADR 0003. The original entry is retained as
`references/upstream-SKILL.md`. The complete 407-file upstream inventory is
retained in `references/upstream-files.json`, including paths, hashes and modes.
The manifest's adapted origin points to the entry document. It does not claim
that typed origin validation checks the runtime files. The separate
`pstack-statechart.py` probe verifies every retained production file and the
complete inventory against the pinned upstream checkout.

This distinction also addresses the engine's independent cumulative origin
budget. Indexing the complete statechart origin alongside existing origins
requires 1,051 entries, above its 1,024 limit. The entry-level origin and explicit
runtime inventory make the distribution reviewable without changing the engine
or narrowing existing resources' provenance. Existing original trees stay exact.

## Update boundary

Update common originals, native adaptations, on-demand entries, dependencies,
and legal closure together. A layout or adaptation change is a contract
migration. `catalog upstream-refresh` applies only to the narrower exact-copy
refresh described in the root README.

Run full catalog validation against a clean baseline. Then run the current
[content checks](../scripts/probes/README.md#current-pstack-update-checks).
Historical research and older probe receipts remain evidence for their recorded
revision. They do not establish current host support or current runtime behavior.

Catalog maintenance changes this repository. Publication, local snapshot refresh,
and updates of installed skills are separate operations. A `packy catalog refresh`
selects a snapshot without updating existing installations. On-demand procedures
keep their initiating snapshot throughout a run.
