# Claude community Pack

The `claude` Pack 1.0.0 contains the portable, self-contained `eli5` and
`html-plan` skills from
[`anthropics/claude-plugins-community` at `f60f0454df3045f724c43c6346ec80bdcc3472b2`](https://github.com/anthropics/claude-plugins-community/tree/f60f0454df3045f724c43c6346ec80bdcc3472b2).
Both have native skill bindings for Claude Code, Codex, and OpenCode. The name
identifies the source collection; these are community contributions by Thariq
Shihipar, rather than a claim of Anthropic authorship.

## Scope

This upstream revision is a marketplace with 2,284 entries, mostly pointers to
independent repositories. It is not a single portable plugin bundle. The Pack
reviews the resources stored in this repository, rather than recursively
importing the marketplace.

| Local plugin | Decision |
| --- | --- |
| `eli5` | Include the picture-explanation skill, with portable input and artifact delivery. |
| `html-plan` | Include the planning skill and its complete runtime, reference, and example closure. |
| `next-steps` | Exclude: depends on Claude's function-hook runtime, session forks, composer widgets, and draft insertion. A conversational skill would change its behavior. |
| `quickdesign` | Exclude from this self-contained edition: requires the QuickDesign CLI and hosted media service. |
| `testdino` | Exclude from this edition: requires its hosted MCP service and authentication. |
| `tres-finance-plugin` | Exclude from this edition: requires its hosted finance MCP service and organization access. |
| `cowork-plugin-management` | Listed with a relative source, but no directory is present at the pinned revision. |

Importing an external marketplace entry would require reviewing and pinning its
own upstream origin, license, resource closure, and host requirements. It is
outside this Pack's reviewed contract.

## Adaptations and requirements

Both entrypoints use the topic or change in the invocation/conversation instead
of assuming Claude expands `$ARGUMENTS`. `eli5` explicitly writes a standalone
HTML file and returns its path or an available artifact link. `html-plan`
retains the upstream claim tree, packing workflow, and user-response gate.
Its runtime's comments and copy-response UI address the current agent rather
than Claude. Runtime code, CSS, references, and examples otherwise retain
upstream behavior. The skill roots are consequently declared `adapted`.

`html-plan` needs `node` to lint and pack a portable HTML file. The Pack declares
that executable as an external requirement; it does not install it. `eli5`
itself needs only file-writing capability. No lifecycle hooks, MCP servers,
instruction files, or personal host settings are installed by this Pack.

The repository supplies an Apache-2.0 `LICENSE`, while both included plugins'
metadata declares MIT and names Thariq Shihipar as author. No separate MIT
license text is present for these two plugins at this revision. The Pack
preserves the repository license and both original metadata files byte-for-byte
as notice resources, retaining both declarations without inventing a copyright
statement or replacing the upstream license text.

## Installation and validation

After publication, run from a target Git project:

```sh
packy catalog refresh
packy install claude --surface codex --dry-run
packy install claude --surface codex
```

Use `--surface claude` or `--surface opencode` for the other hosts. Select just
one skill with `--resource skill:eli5` or `--resource skill:html-plan`.

Packy v0.2.26 already discovers Pack directories and projects native skills on
all three hosts. This addition needs only Catalog Project changes, with no
engine or registry update. Validate the catalog against an unchanged checkout
and run the [project installation probe](../../scripts/probes/README.md#claude-project-installation).
The probe checks actual CLI projection, selection, notice closure, preservation,
and removal. A separate packing smoke check uses the shipped HTML example.
These checks do not establish model behavior or discovery in live host sessions.
