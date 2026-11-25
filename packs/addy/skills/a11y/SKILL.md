---
name: a11y
description: "Runs an accessibility audit through the accessibility-auditor persona"
---

# A11y

Invoke the accessibility-engineering skill.

This workflow runs a dedicated accessibility audit. It checks keyboard navigation, screen reader support, color contrast, form labeling, and structural WCAG 2.2 AA compliance.

## Determine the mode

**Deep mode** — activate when any of these is available:
- An axe-core or pa11y JSON report file (generate a combined report using the audit-script path instructions in the loaded `accessibility-engineering` skill)
- A live URL — the agent can instruct the user to run the audit script above
- Chrome DevTools MCP (for live DOM inspection, contrast checking, and rendering analysis)

**Quick mode** — default when no tool output is available. Scan source code for structural anti-patterns (missing labels, div-as-button, no alt text, skipped heading levels).

## Run the audit

Request the `accessibility-auditor` native role only when the selected client exposes it and delegation is authorized. If unavailable, stop and report the missing prerequisite; a configured definition is not evidence of a successful delegation. Pass it explicitly:

- The files, components, or diff under review
- Any artifact paths (axe-core JSON, pa11y JSON, audit script output)
- The target URL or component when known
- A note on which mode you expect (Quick or Deep), so the agent surfaces missing inputs if Deep was intended

The subagent returns a WCAG scorecard, a ranked list of findings by severity, positive observations, and remediation guidance with code examples.

## Output

Return the full audit report to the user. No synthesis or merge step is needed — this is a single-persona workflow.
