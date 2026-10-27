---
name: review
description: "Reviews code for correctness, readability, architecture, security, and performance"
---

# Review

Request the named code-reviewer role when available and authorized, with the code-review-and-quality skill. If that role or delegation is unavailable, report the unmet prerequisite instead of claiming a specialist review.

Review the current changes (staged or recent commits) across all five axes:

1. **Correctness** — Does it match the spec? Edge cases handled? Tests adequate?
2. **Readability** — Clear names? Straightforward logic? Well-organized?
3. **Architecture** — Follows existing patterns? Clean boundaries? Right abstraction level?
4. **Security** — Input validated? Secrets safe? Auth checked? (Use security-and-hardening skill)
5. **Performance** — No N+1 queries? No unbounded ops? (Use performance-optimization skill)

Categorize findings as Critical, Required, Optional, or Nit.
Output a structured review with specific file:line references and fix recommendations.
