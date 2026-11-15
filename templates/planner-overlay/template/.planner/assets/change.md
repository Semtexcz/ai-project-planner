---
schema_version: 1
kind: change
id: CHG-000
owner: product_owner
scope:
  idea: State the new idea, changed assumption or failed evidence.
  source: Record where the idea came from and when.
  affected: []
  impact: Describe the upward and downward impact on objectives, requirements, milestones, tasks and evidence.
  alternatives:
    - Describe keep, reject, defer, narrow or pivot alternatives.
  proposed_delta: Describe the exact proposed change, without claiming approval.
  required_approvals: []
execution:
  state: captured
  disposition_decision: null
  applied_revision: null
  blockers: []
  progress_notes: []
---

# Change proposal

A change captures an idea or changed assumption without modifying approved
scope. It traces impact upward to objectives and requirements and downward to
milestones, tasks, dependencies, prompts and evidence. It states alternatives
and the exact proposed delta.

Only an explicit human disposition moves a change to `approved`, `rejected` or
`deferred`. Applying an approved change rechecks the source revision first and
must be idempotent against the recorded change ID and targets. A partial apply
is reported and is not complete.
