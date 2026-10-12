# Inspect an upstream marketplace

Use Python 3.9+ and a local, reviewed checkout. The Catalog-owned inspector uses
only the standard library and reads `.claude-plugin/marketplace.json`:

```sh
python3 -B scripts/inspect_marketplace.py /path/to/upstream
python3 -B scripts/inspect_marketplace.py /path/to/upstream --entry html-plan
python3 -B scripts/inspect_marketplace.py /path/to/upstream --entry html-plan --inventory
```

`--entry` matches an exact, case-sensitive name. `--inventory` lists paths under
that entry's present local directory, or the whole checkout when no entry is
selected. An external, absent, malformed, unsupported, or unsafe selected source
cannot provide an inventory. External references are never fetched. No hooks,
helpers, skill code, or installation commands are executed; the checkout is
unchanged. The input is assumed static during inspection.

## Output and limits

Normal output and errors are one JSON document on stdout; `--help` is fixed text.
The total UTF-8 output budget is **16,384 bytes**, including the final newline.
There are at most **20 entry summaries** and **100 inventory paths**. Every list
reports `total` and `omitted`; counts reflect the complete manifest or traversed
inventory even when output is shortened. Inventory counts include files,
directories, special files, and symlinks, but exclude descendants of symlinks.
Traversal lists sorted children before visiting their directories in sorted
depth-first order. It includes hidden paths, including `.git`, when present.
Output is bounded, not input size, memory use, or traversal time.

Variable evidence fields use `{"json": "...", "truncated": false}`. `json` is
the original value serialized as JSON, preserving object fields and values, not
original whitespace or key formatting. It is limited to **512 ASCII bytes**
(Unicode uses JSON escapes). `truncated: true` means the preview is incomplete;
never parse it as the complete source declaration. Whole-document JSON remains
valid. To fit the total budget, inventory items and then entry summaries may be
omitted further; their omitted counts include these removals.

`selected.location` is a JSON Pointer such as `/plugins/17` within the reported
manifest. `selected.source` retains the source declaration when it fits; the
entry preview provides additional metadata. The manifest and pointer locate the
authoritative source when a field is truncated. Missing names and duplicate-name
ambiguity fail instead of selecting a guess.

The mutually exclusive classification counts reconcile with `total_entries`:

| Classification | Meaning |
| --- | --- |
| `local_present` | Relative string source naming a present directory |
| `local_absent` | Relative string source naming an absent path |
| `external` | Object with `source: url` and nonempty string `url`, or `source: git-subdir` with nonempty string `url` and `path` |
| `unsupported` | Source object with an unrecognized string discriminator |
| `malformed` | Invalid entry/name/source fields, inaccessible local source, or present non-directory target |
| `unsafe` | Absolute/traversing local path, invalid NUL, or any symlink component |

Extra external fields are retained; `sha` and `ref` are optional. URLs and
external subdirectories are classified as declarations, not validated or read.
This is support for observed source shapes, not the full marketplace schema.
Local paths reject POSIX and Windows absolute/drive paths and `..` components;
both slash styles are recognized. Manifest and local-source access reject all
symlinks, including links that stay within the checkout. Inventory records links
without following them. The explicitly supplied checkout root is resolved once.

Exit codes: **0** for a completed report, even with entry anomalies, or help;
**1** for unreadable/invalid top-level input, unsafe manifest access, missing or
ambiguous entry, or failed inventory; **2** for invalid command arguments.
Diagnostics also obey the output budget. A failed inventory does not present a
partial list as complete.

## Focused follow-up

These summaries do not certify a complete content review, an import, portability,
or license suitability. Read the selected manifest entry and the relevant local
README, notices, and skill files when the review question needs them. For
example, after a result identifies `/plugins/17`, extract only that entry with
`jq '.plugins[17]' /path/to/upstream/.claude-plugin/marketplace.json`. Such an
explicit focused read is outside the inspector's output budget; avoid dumping
the complete marketplace or repository tree by default.

The [triage research](research/marketplace-inspection.md) records the pinned
Anthropic evidence and the distinction between API analysis and CLI acceptance.
Offline public-CLI fixtures run automatically in `./scripts/test.sh`, including
the 2,284-entry fixture, output limits, lookup errors, containment, and unchanged
input checks. They require neither network nor the real upstream checkout.
