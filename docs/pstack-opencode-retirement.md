# Retire an existing pstack OpenCode installation

pstack 5.0.0 supports Codex and Claude Code. New OpenCode discovery, retrieval,
installation and activation are unsupported. Existing OpenCode installations are
not automatically deleted, replaced or migrated by this support withdrawal.
Other Packs retain their declared support.

A project update rejects the unsupported host. A personal update can preview
proposed actions but produces a non-actionable plan: applying it fails before
native-content or activation-state writes. Neither path retires OpenCode.

## Project uninstall

From the project containing the existing installation, preview and explicitly
approve its removal using the public CLI:

```sh
packy uninstall pstack --surface opencode --dry-run
packy uninstall pstack --surface opencode
```

Project uninstall uses installed ownership evidence. Keep `.packy` metadata and
owned native resources until it completes. Drift blocks removal; inspect and
back up intentional local changes, then restore the owned content before retrying.
Do not bypass the ownership guard or delete another Pack's resources manually.

## Personal deactivation

```sh
packy deactivate pstack --surface opencode --dry-run
packy deactivate pstack --surface opencode
```

Deactivation resolves the exact active old version and its retained snapshot.
Keep the activation state and retained catalog content until deactivation
completes. Do not clear the catalog cache or remove retained snapshots first.
Drift or missing retained content fails explicitly; restore the exact original
content from the same snapshot rather than substituting the current two-host
Pack or another revision. Review and back up intentional modifications first.

After either operation, inspect the reported removal and confirm that only the
owned pstack OpenCode selection retired and unrelated resources remain. No
command above authorizes changing live installations without the owner's intent.
The opt-in withdrawal probe performs these operations only in disposable state.

The [accepted decision](adr/0003-limit-pstack-host-support.md) records the support
contract and delivery order; [probe instructions](../scripts/probes/README.md#pstack-500-support-withdrawal)
describe the released-binary acceptance boundary.
