# Check evidence before cleanup

Before deleting run-owned temporary state, inventory every exact cleanup target,
trail and retained handoff for the run. Stop owned writers. Use Python 3 and the
standard library to run this resource's read-only helper immediately before the
separate cleanup decision:

```sh
python3 -B "$SHOW_WORK_RESOURCE/scripts/check-retention.py" \
  --base "$RUN_ROOT" --trail "$EVIDENCE/decisions.tsv" \
  --handoff "$EVIDENCE/handoff.md" --target "$OWNED_SCRATCH"
```

All arguments must be absolute. Repeat `--trail`, `--handoff`, and `--target` to
supply the complete inventory. Use `--no-trail` or `--no-handoff` only after
confirming that kind is absent. `--base` resolves relative trail paths; handoff
paths resolve relative to their document. Documents must survive every target.
A nonzero exit blocks cleanup. Zero checks the supplied inventory only; it does
not establish ownership or authorize deletion. Rerun after any change to evidence,
paths, targets, or filesystem topology. This is a snapshot, not a lock.

Copy each affected local artifact outside all targets and append an ordinary
six-column TSV row with phase `relocation`. Its evidence cell must be exactly
`[/old/absolute/path](/new/absolute/path)`. Keep the original rows and files.
The helper hashes both live regular files with SHA-256. It checks every relocation,
including unreferenced ones, rejects conflicting or chained mappings, and requires
all destinations to survive all targets. A later test or unrelated HTTPS link is
not a replacement for the original. If an original is already missing, this
checker cannot verify a new copy claim, even when an earlier check was reported.
Report that gap; do not claim reconstruction. Do not retain credentials as evidence.

## Supported citations

A trail uses the exact `ts`, `phase`, `decision`, `why`, `evidence`, `result` TSV
header. Normal evidence cells contain pointers separated by commas or semicolons.
Supported pointers are absolute paths, relative paths with a slash, simple filenames
with an extension, an optional numeric `:line` suffix, ordinary inline Markdown
links, HTTPS URLs, `commit <hex>`, a 7-to-64-digit hexadecimal commit, `PR #N`,
and `#N`. Link destinations follow the same local path rules. Relocation links
require absolute local paths on both sides. Whitespace, escapes, shell variables,
globs, URL relocations and paths with Markdown delimiters are unsupported.
Directories and special files are not evidence files; cite their individual files.
Symlink paths and ancestors are rejected, including symlinks encountered before
`..`. An absent cleanup target can pass only when all citations still resolve.

In handoffs, express local citations as ordinary inline links or inline code paths.
Links resolve relative to the handoff. Plain HTTPS URLs are independent citations.
Reference-style links, nested or escaped Markdown, malformed constructs and
path-like prose and inline code that is neither a supported path nor an external citation block the check. The helper is not a general Markdown parser and
cannot discover implicit references in free-form prose or documents omitted from
the inventory. Rewrite mutable handoff citations into the supported form, and
record any append-only trail correction without erasing history. Unknown trail
cells block visibly; do not omit them to obtain a pass.
