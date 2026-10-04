# Triage labels

GitHub's existing `status:approved` label is the repository's `ready-for-agent`
state. An open issue bearing it is eligible only when its scope, acceptance
criteria, and dependencies are also ready. Approval alone does not bypass
protected integration.

| Canonical role | Repository representation |
| --- | --- |
| `needs-triage` | Open issue without `status:approved`; no dedicated label configured |
| `needs-info` | Explain the missing information in the issue and remove `status:approved`; no dedicated label configured |
| `ready-for-agent` | `status:approved` |
| `ready-for-human` | Explicit human ownership in the issue without `status:approved`; no dedicated label configured |
| `wontfix` | `wontfix` |

Only `status:approved` is a configured readiness label. Do not invent or create
additional triage labels during delivery. Closing an issue is GitHub's state
transition; historical approved labels may remain on closed issues.
