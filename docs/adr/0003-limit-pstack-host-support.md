---
status: accepted
---

# Keep pstack identity while withdrawing OpenCode support

Retain one pstack Pack with reviewed surface variants for Codex and Claude.
Withdraw OpenCode support in pstack's next major version, preserve existing
installations, and document explicit retirement. Retain the common exact-copy
upstream bodies and their immutable provenance and legal closure. The user
selected these decisions to both unblock Catalog issue #94 and reduce recurring
adaptation maintenance. This support change applies only to pstack.

The original upstream pstack bodies target Cursor. Replacing the reviewed
Codex and Claude variants with those originals would restore wrong project and
preference paths, host-specific tool assumptions, inaccessible transcript
assumptions, and runtime writes inside managed resources. Separate host Packs
would retain the adaptation work while fragmenting public identities, versions,
provenance, installation ownership, and updates. Keeping variants retains
qualified identities such as `pstack:architect`.

The immediate blocker is a bounded engine index budget: pstack uses 1,015
entries on Catalog main, and the #94 candidate uses 1,047, exceeding pinned
Packy v0.2.31's limit of 1,024. Removing OpenCode's 55 variant roots saves 133
files and 72 directories. The corresponding counts become 810 and 842 while
retaining both notices and all common originals. These are source-tree counts;
released-binary validation and candidate acceptance remain required.

Increasing the engine budget remains a separate capacity option. It would not
itself reduce adaptation maintenance. Removing the shipped common originals
would also save space, but would change the existing original-retention policy
without being necessary for this withdrawal. A single portable authored body
would still be a Catalog Adaptation requiring reviewed host behavior; it is
not equivalent to the upstream original.

## Existing installations

The withdrawal does not authorize automatic deletion, replacement, or migration
of any installed OpenCode resources. Document explicit project uninstall and
personal deactivation, preserve drift and ownership guards, and retain the old
installation/snapshot evidence needed for retirement. New OpenCode installation
is unsupported after withdrawal. Do not promise that an update automatically
retires an unsupported host.

Source inspection of the pinned engine shows that project update rejects an
unsupported host before planning retirement. Personal update produces a
non-actionable plan; its preview can contain proposed actions, but applying it
fails before native-content or activation-state writes. Project uninstall reads
installed ownership data, and personal deactivation resolves its exact old
version and retained snapshot. Missing retained content fails explicitly.
Released-binary acceptance must prove these transitions and drift preservation;
source inspection is not execution evidence. All other Packs retain their
existing support contracts.

## Delivery sequence

Deliver the withdrawal first as a separate prerequisite, advancing pstack from
4.6.0 to 5.0.0. Then resume #94 against that clean baseline, with its own
appropriate independent Pack version increase. Preserve the existing #94
candidate as source work, not proof for the new baseline. No engine-budget
change is required by the reviewed source-tree counts.

Issue #94 currently requires OpenCode preservation. Its tracker specification,
dependency and affected acceptance coverage must explicitly reflect the selected
withdrawal before implementation. The prerequisite must prove Codex/Claude
preservation, unsupported new OpenCode requests, unchanged legacy installations
on failed updates, explicit project/personal retirement, drift guards, complete
catalog validation and owned-state cleanup. Then #94 must rerun its own exact-
candidate access acceptance. Do not silently broaden the approved issue or reuse
old candidate receipts for a changed migration.

The user confirmed the complete shared understanding. This ADR records the
accepted target contract; implementation and publication remain separate delivery
work in the sequence above.

Related decisions: [on-demand access](0002-provide-on-demand-skills-without-executing-workflows.md)
and the engine's [logical resource identity across surface variants](https://github.com/yersonargotev/packy/blob/c7f08bcfa639488f412a67d80176398aebe93868/docs/adr/0041-keep-logical-resource-identity-across-surface-variants.md).
