# Bounded upstream marketplace inspection

Research date: 2026-10-12. Scope: triage of
[#50](https://github.com/yersonargotev/packy-catalog/issues/50), not implementation
or approval of a new import. Catalog baseline:
`a00729ea5922c51c993942fa393606a754d9b24f`.

## Recommendation

Keep the request as an **enhancement** and recommend **ready-for-agent** after
maintainer agreement. A small Python standard-library CLI is justified: reusable
source classification, checkout containment, and explicit output budgets are
more than a documentation recipe should repeatedly implement. Keep it a local,
read-only inspection tool; do not add download, installation, import, resource
selection, or portability decisions. This follows the existing request rather
than expanding it. [Issue #50](https://github.com/yersonargotev/packy-catalog/issues/50)

The existing focused `jq`/`git` guidance concerns authored Catalog Pack manifests
and update diffs. It does not classify upstream marketplaces or inspect their
local sources. Closed #40 therefore does not make #50 redundant. Repository
inspection found no marketplace inspector in `scripts`, no `.out-of-scope/`
rejection record, and no new-Pack investigation section in the README. Add a
short new-Pack investigation pointer in the README, with detailed usage beside
the tool; do not broaden the existing update skill or always-loaded guidance.
[Update skill](../../.agents/skills/update-catalog-pack/SKILL.md),
[README](../../README.md), [scripts](../../scripts),
[#40](https://github.com/yersonargotev/packy-catalog/issues/40)

Python 3.9+ is already a tooling prerequisite. The proposed inspection needs
only standard-library JSON, argument parsing, and filesystem operations; it does
not require another dependency or changes to released Packy tooling.
[Catalog tooling](../catalog-tooling.md),
[tooling implementation](../../scripts/packy_tool.py)

## Verified upstream evidence

Read the exact pinned marketplace blob and its complete recursive Git tree using
GitHub's API. The tree response reported `truncated: false` and contained 214
entries. No plugin code was executed and no external plugin repository was read.
[Pinned marketplace](https://github.com/anthropics/claude-plugins-community/blob/f60f0454df3045f724c43c6346ec80bdcc3472b2/.claude-plugin/marketplace.json),
[pinned tree API](https://api.github.com/repos/anthropics/claude-plugins-community/git/trees/f60f0454df3045f724c43c6346ec80bdcc3472b2?recursive=1)

| Measurement | Result |
| --- | ---: |
| Raw marketplace bytes | 1,566,683 |
| Plugin entries | 2,284 |
| External `{"source":"url", ...}` | 1,876 |
| External `{"source":"git-subdir", ...}` | 401 |
| Relative string sources | 7 |
| Present local directories | 6 |
| Absent local directories | 1 |
| Duplicate plugin names | 0 |

The six present directories are `quickdesign`, `testdino`,
`tres-finance-plugin`, `eli5`, `next-steps`, and `html-plan`.
`cowork-plugin-management` declares `./cowork-plugin-management`, which is absent
from the pinned tree. These results independently match the existing Claude
scope note. [Pinned tree](https://github.com/anthropics/claude-plugins-community/tree/f60f0454df3045f724c43c6346ec80bdcc3472b2),
[Claude research](claude.md)

Source-object fields are not uniform: five `url` declarations also have a `path`;
three `git-subdir` declarations omit `sha`; one omits `ref`. Preserve these
declarations and avoid treating optional pin fields as required. All entries
have nonempty string names; external entries have nonempty string `url` values,
and `git-subdir` entries have nonempty string `path` values. This is a check of
observed shapes, not certification against the full Claude marketplace schema.
[Pinned marketplace](https://github.com/anthropics/claude-plugins-community/blob/f60f0454df3045f724c43c6346ec80bdcc3472b2/.claude-plugin/marketplace.json)

The research command captured the raw API response in memory and printed only
metadata, source-form counts, one example per form, the seven local names and
their existence, duplicate names, and tree completeness. That JSON summary was
1,718 UTF-8 bytes. This demonstrates that useful evidence can be compact; it is
not an output-bound test of a finished CLI. The reported historical 393,503-token
output was not independently reproduced and concerned a combined file-listing
and manifest-dump command, not necessarily the marketplace alone.
[Original incident report](https://github.com/yersonargotev/packy-catalog/issues/50)

The exact read-only API acquisition used for this analysis was:

```python
import json
import subprocess

revision = "f60f0454df3045f724c43c6346ec80bdcc3472b2"
repository = "repos/anthropics/claude-plugins-community"
raw = subprocess.check_output([
    "gh", "api",
    f"{repository}/contents/.claude-plugin/marketplace.json?ref={revision}",
    "-H", "Accept: application/vnd.github.raw+json",
])
marketplace = json.loads(raw)
tree = json.loads(subprocess.check_output([
    "gh", "api", f"{repository}/git/trees/{revision}?recursive=1",
]))
# Analyze captured data; do not print raw or the complete marketplace/tree.
assert tree["truncated"] is False
print({"manifest_bytes": len(raw), "entries": len(marketplace["plugins"])})
```

This verification uses a pinned blob and complete Git tree, not a local-checkout
execution of the requested tool. Delivery still needs the manual local-checkout
acceptance command and recorded revision required by #50.

## Proposed implementation boundary

The following is a proposed contract for the brief, not implemented behavior:

- Accept a local checkout and inspect only `.claude-plugin/marketplace.json`.
  Summarize metadata and counts by default; support exact named-entry lookup
  and an explicitly requested bounded path inventory.
- Support the three observed source forms. Distinguish present local directory,
  absent local source, external reference, unsupported form, malformed entry,
  and unsafe local path. Do not fetch external references.
- Preserve original source declarations in selected-entry evidence. When a
  declaration exceeds the output budget, visibly mark truncation and identify
  the manifest and entry index for a focused read. Do not present an abbreviated
  value as the complete source. Duplicate-name queries should report ambiguity.
- Enforce a total output byte budget as well as entry/path limits. Include
  totals and omitted counts; long names, metadata, source objects, and diagnostic
  text must not bypass the budget. Choose and document modest fixed defaults.
- Reject absolute paths and traversal. Check the manifest path and all inspected
  source/inventory paths for containment; never follow symlink escapes. Keeping
  symlinks visible without descending through them is a simple conservative
  inventory policy. Treat a reviewed checkout as static during inspection.
- Document exit behavior. Suggested semantics: success for a completed summary
  even when it reports anomalies; nonzero for unreadable/invalid top-level input,
  unsafe manifest access, and absent or ambiguous requested names. Unsupported
  entries remain visible findings rather than silently disappearing.
- Use offline fixtures for at least 2,284 entries and for huge individual fields,
  malformed/unsupported shapes, missing paths, duplicate names, traversal,
  symlink escapes, selected-entry truncation, and inventory omission. Verify the
  input checkout remains unchanged. Preserve ordinary validation/publication
  and shipped Pack contracts.

These details close specification gaps in the existing acceptance criteria;
they do not require a generic plugin framework. Tests should exercise actual
observable output limits and containment, not only mirror classifier branches.
The final flag names, numeric budgets, and documented exit-code numbers are
routine implementation choices. The maintainer decision is whether to approve
this narrow tool rather than reduce the request to documentation only.
[Issue acceptance criteria](https://github.com/yersonargotev/packy-catalog/issues/50)
