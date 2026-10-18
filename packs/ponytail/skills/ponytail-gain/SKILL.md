---
name: ponytail-gain
description: >
  Explain Ponytail 5's published upstream benchmark results and their limits
  when asked about measured impact, savings, or performance. These results
  are not measurements of the current repository or this Packy adaptation.
---

# Ponytail Gain

Report the following published results with their scope and source. This is
a one-shot explanation; it changes no files or conversational modes.

The upstream agentic benchmark dated 2026-10-07 used headless Claude Code with
Opus 5.5 at default effort on 39 tasks, with five runs per task and arm. The
tasks included feature tickets, bug fixes, security and privacy cases, and
small apps. Eighteen tasks had hidden correctness and safety checks. For the
first four metrics below, each figure is the geometric mean of per-task median
ratios against the same agent without the skill:

| Metric | Ponytail 5 share of no-skill baseline | Reported change |
|---|---:|---:|
| Lines of code | 47% | -53% |
| Output tokens | 55% | -45% |
| Cost | 74% | -26% |
| Elapsed time | 59% | -41% |
| Hidden checks passed | 96.7% | no-skill: 95.6% |
| A test where logic needed one | 98% | no-skill: 68% |

Always include the [pinned upstream report](https://github.com/DietrichGebert/ponytail/blob/09c434ab73ca43761c5d8b0c5d341926c2fba710/benchmarks/results/2026-10-07-agentic.md).
These are upstream results, not an independently reproduced Packy benchmark.
The experiment loaded Ponytail as a Claude Code plugin; this Pack ships adapted
skills and guidance without that runtime. Do not transfer its results to this
Pack, other models, or the user's repository as a measured or guaranteed
benefit.

Only the 18 surgical tasks had hidden correctness and safety checks. Ponytail 5
passed 87 of 90 runs and the no-skill arm passed 86 of 90, so the report finds
similar correctness and safety rather than an improvement. The other tasks
measure code size and completeness, not hidden functional quality. The test
rate records whether a test was present where the benchmark's rule required
one; mutation results in the report give the separate evidence about whether
those tests caught injected bugs.

Never invent per-repository lines, tokens, money, or time saved: there is no
measured alternate implementation to subtract. For local evidence, suggest
`ponytail-debt` for a counted shortcut ledger or `ponytail-audit` for proposed
improvements, if those skills are installed.
