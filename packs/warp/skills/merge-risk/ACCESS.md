---
name: "merge-risk"
description: "Use when assessing the risk of merging a PR"
metadata:
  credits:
    skill: pr
    author: Matt Pocock
    url: "https://github.com/mattpocock/skills/blob/main/skills/engineering/pr/SKILL.md"
---

## On-demand context

Use the initiating descriptor's `surface` and `snapshot_id` for this procedure
and every nested request, including requests made by a delegate:

```sh
packy get skill warp:<skill> --surface <initiating-surface> --snapshot <initiating-snapshot-id> --json
```

Read and follow prepared Warp entries at the authored links below. Native skill
registrations and installed sibling copies are unnecessary. Carry the same host,
snapshot, target project, and writable scratch/output context in delegate briefs.
Selection changes affect new independent requests only. Keep previously returned
paths; if retained content is missing, stop and restore that exact revision.
Never substitute a newer revision or another Pack's similarly named workflow.

Resolve supporting files relative to this entry and `resource_root`, reading
only the active branch's references. Resolve repository paths, specs, review
inputs and generated files against the intended target project. Select writable
scratch/output separately from immutable resource trees. Retrieval supplies
instructions only: model, worker, MCP, credential, repository, scheduler, runtime
and validation prerequisites remain unverified until checked in the active host.
Honor the source's approvals, domain boundaries, stopping rules and fallbacks.

Use only controls actually exposed by the initiating host. On Codex, use its
available local subagent launch, message/resume and wait controls; on Claude Code,
use its available Agent control and supported original-author follow-up. Check
available model identifiers and whether model selection is per child or per run.
Use separate launches when only run-wide model selection exists. If a required
control is absent, report the limitation and stop that branch unless its source
explicitly provides a fallback. A lifecycle success is not validation evidence.
Use the host's question control (with the source's choices and free-text option),
or ask in conversation and wait for the actual reply when no question tool exists.
Use available host file, shell, search and computer-use controls where applicable;
access does not provision Warp/Oz tools or remote execution. Remote-only checks
require an actual authorized remote capability; otherwise report the gap and use
only the source-defined fallback. Obtaining these instructions grants no approval
to launch workers, post external content, commit, push or schedule anything.

Output format:

```
**Merge risk: <low-medium-high>**

**<category>:** <verdict>
<list gaps that increase risk. Use bullets, keep succinct. Include links to relevant files as needed>

<...list all categories>
```

These are the **categories** and **verdicts** that affect risk, with descriptions of what "low risk" means:

- **Alignment (poor ⚠️ / decent 👀 / good ✅):** Code aligns with the description and source issue, when present. Behavior assumptions and drive-bys must be documented.
- **Impact (large ⚠️ / medium 👀 / small ✅):** Scope is contained and away from sensitive code paths.
  - Consider blast radius: potential impact or scope of the changes introduced by this PR. Consider all possibilities. Examples are layout shift, breakages for consumers, mobile responsiveness, etc.
  - Sensitive areas carry outsized risk regardless of diff size: auth, permissions, payments, PII, secrets, data migrations, dependency bumps, and infra or config changes. Flag any that are touched, and call out anything that widens access, weakens validation, or logs sensitive data.
- **Verification (poor ⚠️ / decent 👀 / good ✅):** Behavior is verified, where applicable.
  - Changes to the user experience **need** end-to-end proof as screenshots or recordings. Changes that could meaningfully affect performance **need** profiling. Prefer before-and-after evidence to standalone proof. When this coverage is lacking, it's a failure.
  - Edge cases must be tested, or documented when they aren't; review the code closely and link the user to relevant code when only documentation is present.
- **Rollback cost (high ⚠️ / medium 👀 / low ✅):** The code is reversible once merged. Consider one-way vs. two-way doors. You can walk back through two-way doors, but not one-way doors. A PR that is cheap to roll back is lower risk. Changes that involve destructive actions or hard-to-reverse decisions are one-way doors.
- **Error detection (poor ⚠️ / decent 👀 / good ✅ / N/A ✅):** If applicable, critical flows should be monitored; If this breaks in production, someone should find out before users report it. Look for swallowed errors or fallbacks that hide breakage.

Generate a risk score for merging this PR on a scale of low - medium - high.

Verdicts:

- ⚠️ = 3
- 👀 = 2
- ✅ = 1

Weights:

- Impact = 2x
- Verification = 2x
- Rollback cost = 1.5x
- Error detection = 1x
- Alignment = 1x

Score = Σ(score × weight) / Σ(weights).

- low: < 1.5
- medium: 1.5 – < 2.25
- high: ≥ 2.25

Keep the numerical score and its calculations internal; do not include them in the output.
