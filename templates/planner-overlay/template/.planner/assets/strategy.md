---
schema_version: 1
kind: strategy
id: VIS-000
owner: product_owner
scope:
  purpose: Describe the purpose this project exists to serve.
  beneficiaries:
    - Describe who benefits and in what situation.
  problem: Describe the problem or opportunity, without proposing a solution.
  choices:
    - Describe a deliberate strategic choice and its consequence.
  exclusions:
    - Describe what this project deliberately does not pursue.
  assumptions:
    - Describe an assumption that could invalidate the strategy if false.
  objectives:
    - id: OBJ-000
      statement: Describe a strategic objective that explains a choice above.
      outcomes:
        - id: OUT-000
          description: Describe an observable benefit, not a task or output.
          baseline: State a measured baseline, or say that the baseline is unknown and why.
          target_or_rubric: State a target or a qualitative rubric.
          verification: State what evidence would demonstrate the outcome.
          review_horizon: State when the outcome will be reviewed.
execution:
  state: proposed
  items:
    OBJ-000:
      state: proposed
    OUT-000:
      state: proposed
  approvals: []
  progress_notes: []
---

# Strategy

This record holds the vision, strategic choices, objectives (`OBJ-*`) and
expected outcomes (`OUT-*`). Objectives explain why a choice matters. Outcomes
describe observable benefit with a baseline, a target or rubric, an evidence
expectation and a review horizon.

Nothing here authorizes work by itself. Requirements must link to an objective,
milestones must state exit criteria, and tasks need an approved scope.

Markdown body text explains context and history. It cannot add permission or
acceptance criteria that are absent from `scope`. Replace the `-000` placeholder
identifiers with stable project-local identifiers; never renumber identifiers
that already exist.
