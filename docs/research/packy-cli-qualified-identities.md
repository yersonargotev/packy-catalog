# Direct retrieval for qualified Packy skill identities

## Question

Should the `packy-cli` skill run broad `list` and `show` discovery before
obtaining a request that already supplies a complete identity such as
`matty:retro`?

## Evidence

The Catalog pins Packy `v0.2.31` at source commit
`c7f08bcfa639488f412a67d80176398aebe93868`; this report treats that release,
rather than the adjacent engine checkout's newer `HEAD`, as the executable
contract ([`packy-release.json`](../../packy-release.json)).

At that revision, `get skill` accepts exactly one `<pack>:<skill>` argument and
requires an explicit Codex or Claude surface. It validates those inputs before
resolving the selected Catalog Snapshot, then prepares the resource directly.
It does not depend on a preceding discovery command
([`internal/cli/skill_get.go`](https://github.com/yersonargotev/packy/blob/c7f08bcfa639488f412a67d80176398aebe93868/internal/cli/skill_get.go#L40-L83),
[`internal/skillaccess/skillaccess.go`](https://github.com/yersonargotev/packy/blob/c7f08bcfa639488f412a67d80176398aebe93868/internal/skillaccess/skillaccess.go#L54-L83)).
The release documentation likewise presents direct `get skill
example:guide --surface ...` as the retrieval operation, while `list` and
`show` are inspection commands for discovering current candidates
([`docs/on-demand-skills.md`](https://github.com/yersonargotev/packy/blob/c7f08bcfa639488f412a67d80176398aebe93868/docs/on-demand-skills.md#L3-L15),
[`docs/on-demand-skills.md`](https://github.com/yersonargotev/packy/blob/c7f08bcfa639488f412a67d80176398aebe93868/docs/on-demand-skills.md#L44-L56)).

At Catalog baseline `bbf3eecfd7afb85d36586e6f4e18801d2eef47b6`, the skill
makes discovery unconditional in step 1 even though step 2 says a
user-qualified request should use that identity. This creates the reported
redundant `list -> show -> get` path in both host variants
([Codex `SKILL.md`](https://github.com/yersonargotev/packy-catalog/blob/bbf3eecfd7afb85d36586e6f4e18801d2eef47b6/packs/packy/skills/codex/packy-cli/SKILL.md#L15-L23),
[Claude `SKILL.md`](https://github.com/yersonargotev/packy-catalog/blob/bbf3eecfd7afb85d36586e6f4e18801d2eef47b6/packs/packy/skills/claude/packy-cli/SKILL.md#L15-L23)).

Direct retrieval preserves the safeguards currently attached to `get`. JSON
success is a versioned `skill-access` report and includes `qualified_skill`,
`pack_version`, `surface`, `snapshot_id`, `entry_document`, `resource_root`,
`prerequisites`, and the transitive `dependencies`; all dependency entries keep
the initiating surface and snapshot
([release documentation](https://github.com/yersonargotev/packy/blob/c7f08bcfa639488f412a67d80176398aebe93868/docs/on-demand-skills.md#L162-L177)).
The existing Catalog skill already requires checking and retaining these fields
before reading the returned entry document
([Codex `SKILL.md`](../../packs/packy/skills/codex/packy-cli/SKILL.md#obtain-and-read)).

Error handling can be focused rather than speculative:

- An unqualified or malformed value returns `invalid_identity`; the remedy is a
  lowercase kebab-case `<pack>:<skill>` identity. If the request itself is
  ambiguous or unqualified, `list` and focused `show` calls supply the candidates.
- A valid qualified identity whose Pack or skill is absent returns
  `unknown_skill`; its messages direct the caller to `list` or to `show` for the
  named Pack. This is the appropriate recovery point for discovery.
- `catalog_unavailable`, `unsupported_surface`, `incompatible_resource`, and
  `preparation_failed` each have their own corrective action; broad discovery
  does not resolve them.
- An explicit `--snapshot` is resolved as that exact retained identity. Missing
  content returns `snapshot_unavailable`; the implementation does not fall back
  to the selected or a newer snapshot
  ([`skill_get.go`](https://github.com/yersonargotev/packy/blob/c7f08bcfa639488f412a67d80176398aebe93868/internal/cli/skill_get.go#L53-L80),
  [error contract](https://github.com/yersonargotev/packy/blob/c7f08bcfa639488f412a67d80176398aebe93868/docs/on-demand-skills.md#L179-L192)).

These facts support a documentation-only change. The CLI already implements the
desired fast path and structured recovery; changing the engine would add no
needed capability.

## Recommended change

Make selection branch on the input in both Packy skill variants:

1. When the request contains a complete `<pack>:<skill>` identity, run `packy
   get skill` for that identity and explicit host immediately.
2. When the skill is unqualified but its Pack is known, inspect only that Pack
   with `show <pack> --surface <host> --json`. Use `list --json` when the Pack is
   also unknown, then inspect only relevant Packs. Ask the user to choose if
   several qualified candidates remain.
3. After a direct attempt returns `invalid_identity` or `unknown_skill`, use
   focused discovery to correct the identity. Preserve the specific recovery for
   every other structured error, especially exact snapshot restoration for
   `snapshot_unavailable`.
4. Keep the existing success-report field checks, entry-document reading order,
   prerequisite checks, and nested `--snapshot <snapshot_id>` rule unchanged.

Align the concrete `matty:tdd` example in [`docs/packy-cli.md`](../packy-cli.md)
with the same branching rule so the public walkthrough does not reintroduce an
unconditional discovery sequence.

## Acceptance criteria

- A request explicitly naming `matty:retro` directs Codex to one initial
  `packy get skill matty:retro --surface codex --json` call; Claude uses the same
  command with `--surface claude`.
- An unqualified `retro` request still discovers candidates and asks the user to
  choose when more than one qualified match remains.
- A direct `invalid_identity` or `unknown_skill` failure routes to focused
  `list`/`show` discovery, while `snapshot_unavailable` requires restoration of
  the exact retained snapshot and never retries against the selected revision.
- Successful retrieval still validates and retains every documented
  `skill-access` field, reads `entry_document` first, and passes the returned
  surface and `snapshot_id` to nested retrievals.
- Codex and Claude skill definitions remain behaviorally parallel, the Pack
  closure/version changes according to Catalog policy, and the repository's full
  validation succeeds against the pinned released Packy archive.
