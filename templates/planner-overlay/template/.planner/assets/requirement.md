---
schema_version: 1
kind: requirement
id: REQ-000
owner: product_owner
scope:
  statement: Describe one obligation the product or project must satisfy.
  classification: functional # functional | quality | constraint
  objectives:
    - OBJ-000
  sources:
    - Describe the human source, document or observed need behind this obligation.
  acceptance:
    - id: REQ-000:AC-1
      statement: State a pass condition that can be assessed.
  verification:
    - criteria:
        - REQ-000:AC-1
      method: State how the criterion will be assessed.
      expected_evidence: State what evidence must exist.
      reviewer: Replace with the accountable reviewer role.
  supersedes: []
execution:
  state: proposed
  approvals: []
  evidence: []
  blockers: []
  progress_notes: []
---

# Requirement

A requirement is an obligation with a source and a verification criterion. It
links to at least one objective so the strategic chain is visible. A
`constraint` may reference an existing authoritative architecture decision or
contract rather than restating it.

Satisfaction is derived from current evidence, never from this document's
existence. The body explains context and history; it cannot add acceptance
criteria absent from `scope`.
