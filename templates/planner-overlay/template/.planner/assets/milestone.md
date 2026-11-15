---
schema_version: 1
kind: milestone
id: MS-000
owner: product_owner
scope:
  outcome: Describe the observable outcome this milestone achieves.
  objectives:
    - OBJ-000
  outcomes:
    - OUT-000
  requirements:
    - REQ-000
  depends_on: []
  exit_criteria:
    - id: MS-000:EXIT-1
      statement: State a demonstrable condition for declaring this milestone achieved.
  verification:
    - criteria:
        - MS-000:EXIT-1
      method: State how the exit criterion will be demonstrated.
      expected_evidence: State the review or demonstration evidence required.
      reviewer: Replace with the accountable reviewer role.
  packages: []
execution:
  state: proposed
  approvals: []
  evidence: []
  blockers: []
  progress_notes: []
---

# Milestone

A milestone is an outcome plus demonstrable exit criteria, not a list of
delivered tasks. At most one milestone is active at a time. Activation and
achievement require the Product Owner's decision.

An optional work package (`WP-*`) can group a coherent bounded deliverable
inside this milestone. Omitting packages is valid for a small milestone.

The body explains context and history; it cannot add exit criteria or approval
that are absent from `scope`.
