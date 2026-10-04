---
name: ponytail-gain
description: >
  Explain Ponytail's published upstream benchmark results and their limits
  when asked about measured impact, savings, or performance. These results
  are not measurements of the current repository or this Packy adaptation.
---

# Ponytail Gain

Report the following published results with their scope and source. This is
a one-shot explanation; it changes no files or conversational modes.

The upstream agentic benchmark dated 2026-06-18 used Claude Code with Haiku 4.5,
12 feature tasks on a FastAPI/React repository, and four runs per task/arm.
The comparison is against the same agent without the skill:

| Metric | Reported mean change |
|---|---:|
| Added lines of code | -54% |
| Tokens | -22% |
| Cost | -20% |
| Elapsed time | -27% |

Always include the [pinned upstream report](https://github.com/DietrichGebert/ponytail/blob/c982cd411abb53323c4baa1baa3c2f020b8d0b08/benchmarks/results/2026-06-18-agentic.md).
These are upstream results, not an independently reproduced Packy benchmark.
The experiment loaded Ponytail as its plugin; this Pack ships adapted skills
and guidance without that runtime. Do not transfer its results to this Pack,
other models, or the user's repository as a measured or guaranteed benefit.

The largest reductions occurred where native controls replaced custom code;
already minimal tasks showed little change. The older 80–94% single-shot
headline is not the overall agentic result. The separate safety checks passed
20/20 runs for Ponytail; passing those checks is not proof of general security.
Four feature-run timeouts were excluded from cost/time but retained for LOC,
so the effective sample count for those metrics was smaller in some cells.

Never invent per-repository lines, tokens, money, or time saved: there is no
measured alternate implementation to subtract. For local evidence, suggest
`ponytail-debt` for a counted shortcut ledger or `ponytail-audit` for proposed
simplifications, if those skills are installed.
