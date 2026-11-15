# Verification profiles (runtime reference)

Profiles are short reference checklists. They are not executable plugins. A
project selects applicable methods per criterion; mixed projects may use
several. Evidence distinguishes artifact verification from real-world outcome
validation.

| Profile | Appropriate evidence | Insufficient evidence |
| --- | --- | --- |
| software | Relevant automated tests/builds at a commit, integration scenario, reviewed API/package behaviour, reproducible package output. | A checked task, code existing, or test commands listed but not run. |
| engineering / deep-tech | Semantic invariants and counterexamples, stated analysis assumptions, units/dimensions, model or specification review, reproducible calculation or a bounded experiment, named competent reviewer. | Treating code tests as validation of engineering suitability, unstated assumptions, model syntax alone. |
| methodology / systems engineering | Definition and relationship consistency, requirement/decision traceability, scenario walkthroughs, counterexamples, source provenance, accountable human review. Empirical validation only when actually performed. | Assuming a design review proves user benefit, forcing software artifacts, treating hypotheses as mandatory requirements. |

## Evidence entries

```yaml
evidence:
  - id: TASK-001:EV-1
    criteria: [TASK-001:AC-1]
    method: <what was done, not what was planned>
    subject_revision: <commit or working-tree identifier>
    result: pass | fail | inconclusive
    artifact: <path or URI to the substantive report/output>
    reviewer: <accountable role>
    limitations: <what the evidence does not establish; "none known" is allowed>
    observed_at: YYYY-MM-DD
```

Rules:

- Evidence belongs on the task, milestone or strategy item it supports. There is
  no separate evidence database.
- Failed or inconclusive evidence opens a blocker or CHANGE proposal and
  reassesses the requirement/milestone. Never silently weaken acceptance
  criteria or overwrite evidence history.
- Reviewer acceptance of evidence is distinct from authorization of task scope.
- A pass result means the stated criterion was assessed by the stated method at
  the stated revision. It does not establish criteria that were not assessed.
- Reading evidence is not executing verification. Planner never runs the
  method.

## Task-size guidance

Verification must be proportionate to the task contract. A task whose labelled
`size` is larger than the verification can reasonably cover should be split or
re-scoped before it becomes ready. Do not invent a numeric effort estimate to
justify readiness.
