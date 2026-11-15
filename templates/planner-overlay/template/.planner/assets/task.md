---
schema_version: 1
kind: task
id: TASK-000
owner: task_owner
scope:
  title: Describe the smallest useful deliverable or review unit.
  objective: OBJ-000
  rationale: Explain how this work contributes to the approved objective and outcome.
  milestone: MS-000
  requirements:
    - REQ-000
  include:
    - State exactly what work is included.
  exclude:
    - State what is deliberately excluded; write "none" with a reason if nothing is excluded.
  depends_on: []
  context:
    - ref: planning/strategy.md
      authority: strategy
      revision: working-tree
      purpose: Explain why this source is required for the work.
      normative: true
  deliverables:
    - description: Describe the concrete artifact or result this task produces.
      path: replace/with/intended/path.md
  acceptance:
    - id: TASK-000:AC-1
      statement: State a pass condition for the deliverable.
  verification:
    - criteria:
        - TASK-000:AC-1
      method: State how the criterion will be verified for this domain.
      expected_evidence: State what recorded evidence must exist.
      reviewer: Replace with the accountable reviewer role.
  approvals: []
  priority: P1
  size: M
execution:
  state: draft
  authorization: []
  evidence: []
  blockers: []
  progress_notes: []
---

# Task

The scope is the contract. `include` and `exclude` bound the work; `depends_on`
means a prerequisite must be satisfied before starting. Use `context` for
references required to do the work, and say whether each is normative or
background.

A draft task may have incomplete approvals. A task is `ready` only when the
approved milestone, objective chain, requirements, complete contract,
authorization, dependencies, context freshness and verification reviewer are
all satisfied. The checker can verify structural parts; an agent must review
the rest.

The body explains context and history; it cannot add scope, permission or
acceptance criteria absent from `scope`.
