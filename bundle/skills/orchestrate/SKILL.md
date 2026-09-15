---
name: orchestrate
description: Coordinate agents when work benefits from delegation, parallel workstreams, or independent review.
---

# Orchestrate

Keep direction, integration, and user communication with the coordinator. Delegate bounded work when it saves time or improves quality; handle small, tightly coupled work locally. Launch independent assignments together and keep dependent work in order.

Choose among the runtime's available models and configured roles, respecting user choices. Prefer a fast, lower-cost model for narrow discovery and well-specified execution; use a stronger model for ambiguity, difficult implementation, or consequential review. With Astra coordinating, routine workers need not inherit Astra. Use low effort for narrow scouts, medium for routine work, and high for difficult work when supported. Escalate when evidence shows the assignment needs it.

Give each worker an outcome, relevant context, file or module ownership, constraints, and a checkable completion criterion. Prefer fresh context for self-contained assignments (`fork_turns: "none"` where supported); follow the runtime's inheritance rules when overriding model or effort. Keep scouts read-only, assign one writer per scope, and tell workers to preserve others' edits and return to the coordinator for further delegation.

Ask workers to return results, verification evidence, and unresolved issues on completion, or report a blocker when coordinator input is needed. Rely on completion notifications instead of polling for status. While workers run, do useful independent work. When only delegated work remains, end the turn only if the runtime explicitly supports worker completion waking the coordinator; leave a brief handoff with pending work and the next integration step. Otherwise use the runtime's blocking wait mechanism. A handoff is pending work, not task completion.

Resume with the returned evidence, resolve conflicting findings, integrate changes, and verify the combined result proportionately. Resolve or reassign blocked work and reuse workers for focused follow-ups. Finish when the requested outcome is met or further progress requires unavailable input or access; keep any required user approval with the coordinator and honor authorization already given.
