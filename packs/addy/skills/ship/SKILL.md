---
name: ship
description: "Runs specialist pre-launch checks and synthesizes a go or no-go decision"
---

# Ship

Invoke the shipping-and-launch skill.

`ship` skill is a **fan-out orchestrator**. It runs three specialist personas in parallel against the current change, then merges their reports into a single go/no-go decision with a rollback plan. The personas operate independently — no shared state, no ordering — which is what makes parallel execution safe and useful here.

## Phase A — Parallel fan-out

Unless the narrowly defined skip condition in rule 5 applies, request the three named roles concurrently when the client supports parallel delegation and the roles are available and authorized. Request each role by name; if any required role or delegation is unavailable, stop and report the missing prerequisite. Do not treat a simulated or sequential self-review as independent specialist output.

1. **code-reviewer** — Review correctness, readability, architecture, security and performance on the staged changes or recent commits.
2. **security-auditor** — Check vulnerabilities, threat exposure, authentication, secrets and dependencies.
3. **test-engineer** — Analyze coverage, happy paths, edge cases, errors and concurrency.

The coordinator retains authority to synthesize the three independent reports. Do not infer that configured files prove role availability or authorization.

## Phase B — Merge in main context

Once all three reports are back, the main agent (not a sub-persona) synthesizes them:

1. **Code Quality** — Aggregate Critical/Required findings from `code-reviewer` and any failing tests, lint, or build output. Resolve duplicates between reviewers.
2. **Security** — Promote any Critical/High `security-auditor` findings to launch blockers. Cross-reference with `code-reviewer`'s security axis.
3. **Performance** — Pull from `code-reviewer`'s performance axis; cross-check Core Web Vitals if applicable.
4. **Accessibility** — Verify keyboard nav, screen reader support, contrast (not covered by the three personas — handle directly here, or invoke the accessibility checklist).
5. **Infrastructure** — Env vars, migrations, monitoring, feature flags. Verify directly.
6. **Documentation** — README, ADRs, changelog. Verify directly.

## Phase C — Decision and rollback

Produce a single output:

```markdown
## Ship Decision: GO | NO-GO

### Blockers (must fix before ship)
- [Source persona: Critical finding + file:line]

### Recommended fixes (should fix before ship)
- [Source persona: Important finding + file:line]

### Acknowledged risks (shipping anyway)
- [Risk + mitigation]

### Rollback plan
- Trigger conditions: [what signals would prompt rollback]
- Rollback procedure: [exact steps]
- Recovery time objective: [target]

### Specialist reports (full)
- [code-reviewer report]
- [security-auditor report]
- [test-engineer report]
```

## Rules

1. The three Phase A personas run in parallel — never sequentially.
2. Personas do not call each other. The main agent merges in Phase B.
3. The rollback plan is mandatory before any GO decision.
4. If any persona returns a Critical finding, the default verdict is NO-GO unless the user explicitly accepts the risk.
5. **Skip the fan-out only if all of the following are true:** the change touches 2 files or fewer, the diff is under 50 lines, and it does not touch auth, payments, data access, or config/env. Otherwise, default to fan-out. `ship` skill is designed for production-bound changes — when the blast radius is non-trivial, run the parallel review even if the diff looks small.
