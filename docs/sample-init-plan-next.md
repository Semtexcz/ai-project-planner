# Example INIT → PLAN → NEXT output (synthetic)

**Status: example only.** This is a sanitized, synthetic illustration built from
the offline `Project` fixture in `tests/support.py`, not a live run, not a
recorded human approval and not independent acceptance evidence. It exists so a
reviewer can see the shape and traceability of the outputs without reading the
test code. The checker values quoted at the end were produced by running the
read-only checker against that disposable fixture; no other run is claimed.

All names, roles and identifiers are invented. The fixture was created under
`/tmp/opencode/planner-sample/` and is reproducible from the test helpers.

---

## 1. INIT — project intent

Recorded as the project intent (strategy `VIS-001`) after explicit approval of
the proposed baseline.

| Field | Example value |
| --- | --- |
| Project | Fixture Project (`fixture-project`) |
| Category | software |
| Purpose | Turn an approved intention into verifiable planning work. |
| Beneficiaries | Project maintainers; Product Owner |
| Problem | Planning evidence and approvals are scattered across tools. |
| Key choice | Use one native record model with explicit authority bindings. |
| Exclusions | No autonomous execution or scheduler. |
| Assumption | Git remains the review and history mechanism. |

INIT stops before writing records: the operator approves the exact scope text,
and the approval is bound to a content digest, not to a checkbox.

## 2. PLAN — strategy and requirements

### Objective and outcome (embedded in `planning/strategy.md`)

- `OBJ-001` — Make the planning chain reviewable end to end.
  - `OUT-001` — A reviewer can trace an approved task to a strategic outcome.
  - Baseline: `unknown - no baseline was measured before v0.1`
  - Target/rubric: Every ready task cites an approved requirement and objective.
  - Verification: Review a sample of tasks and their approval records.
  - Horizon: At the first milestone review.

### Requirement (`planning/requirements/REQ-001.md`, state `approved`)

- Statement: The overlay must expose six bounded planning operations.
- Classification: functional
- Objective: `OBJ-001`
- Acceptance `REQ-001:AC-1`: Each operation has one explicit skill entry point
  and no execution launcher.
- Verification: inspect the rendered skill inventory and invoke one operation
  explicitly; expected evidence is a recorded invocation and a skill inventory
  listing six operations; reviewer `domain_reviewer`.

### Milestone and package (`planning/milestones/MS-001.md`, state `active`)

- Outcome: A maintainer completes one planning loop on a disposable project.
- Requirements: `REQ-001`; Objectives: `OBJ-001`; Outcomes: `OUT-001`
- Exit criterion `MS-001:EXIT-1`: The ready task and its derived prompt cite the
  approved chain.
- Package `WP-001`: include strategy/requirement/milestone/task records; exclude
  implementation work.

### Roadmap (`planning/roadmap.md`)

```text
# Roadmap view

1. MS-001 - the current milestone.
```

The roadmap is a view, not an authority; the milestone record and
`current_milestone` bindings remain authoritative.

## 3. First approved task

`planning/tasks/TASK-001.md` — state `ready`, authorized by accepted decision
`DEC-001` (the decision targets the exact `scope_sha256` of each record).

| Field | Example value |
| --- | --- |
| Title | Write the demonstration evidence report |
| Trace | `VIS-001 → OBJ-001/OUT-001 → REQ-001 → MS-001 → WP-001 → TASK-001` |
| Rationale | The report demonstrates that the approved chain is traceable. |
| Include | Write `planning/evidence/demo.md` with cited sources. |
| Exclude | none - no implementation is in scope |
| Deliverable | Reviewable demonstration report at `planning/evidence/demo.md` |
| Criterion | `TASK-001:AC-1` — the report cites `VIS-001`, `OBJ-001` and `REQ-001`. |
| Verification | Read the report and compare each citation with the authoritative record. |
| Expected evidence | The report file at a stated revision. |
| Reviewer | `domain_reviewer` |
| Priority / size | `P1` / `M` |
| Normative context | `planning/strategy.md` (revision `working-tree`) |
| Stop point | Before adding requirements or changing the milestone outcome |

## 4. NEXT — derived execution prompt

NEXT fills the shipped prompt structure from the approved contract. The prompt
below is derived, not authority, and was not executed.

```text
DERIVED EXECUTION PROMPT - TASK-001, not project authority
Sources: Fixture Project (synthetic fixture working tree, no commit),
  planning/tasks/TASK-001.md at scope digest c84f78f22d71...
Recommended model: DeepSeek V4.1 Flash; reasoning HIGH.
Escalation: DeepSeek V4 Pro HIGH only under the recorded escalation policy.

Read existing project/agent instructions first, then these sources:
  planning/tasks/TASK-001.md (normative task contract)
  planning/strategy.md (normative context: objective OBJ-001, outcome OUT-001)
  planning/requirements/REQ-001.md (approved requirement and AC-1)
  planning/milestones/MS-001.md (active milestone, EXIT-1, package WP-001)
  planning/records/DEC-001.md (accepted decision binding the scope digests)
  No background-only sources are in scope for this task.

Objective and rationale: Write the demonstration evidence report that shows the
  approved chain is traceable, so a reviewer can follow task -> requirement ->
  objective -> intent without reconstructing it from memory.
Trace: VIS-001 -> OBJ-001/OUT-001 -> REQ-001 -> MS-001 -> WP-001 -> TASK-001
Deliver: planning/evidence/demo.md, a reviewable report that cites VIS-001,
  OBJ-001 and REQ-001.
Scope includes: Write planning/evidence/demo.md with cited sources.
Scope excludes: none - no implementation is in scope.
Constraints: No new requirements, milestones or decisions; do not change the
  approved scope; use only the cited authoritative records.
Prerequisites: DEC-001 accepted and matching the current record scope digests;
  REQ-001 approved; MS-001 active; no open blockers or dependencies.
Acceptance and verification:
  TASK-001:AC-1 - read the report and compare each citation with the
  authoritative record; expected evidence is the report file at a stated
  revision; reviewer domain_reviewer.

Work only within this contract. Do not infer additional product requirements.
Reread current sources before work; stop if normative scope or approval changed.
Stop before adding requirements or changing the milestone outcome; request a PLAN
or CHANGE step for that.
If a dependency fails, authority conflicts, or requirements are ambiguous,
report evidence and propose a planning change; do not approve it yourself.

Return: changed artifacts; each acceptance criterion's result and evidence;
verification actually performed and subject revision; unrun checks/limitations;
remaining risks; requested review and any human acceptance needed.
Do not claim done/accepted solely because work was produced or checks were planned.
```

## 5. Observed checker output for this fixture

From `uv run --script <checker> --project /tmp/opencode/planner-sample --format json`:

- exit code `0`; `errors = 0`, `warnings = 0`, `manual_review_required = 2`
  (`SEMANTIC_REVIEW_REQUIRED`, `APPROVAL_IDENTITY_UNVERIFIED`);
- `ready_tasks = ["TASK-001"]`;
- `review_required_tasks = []`;
- `task_readiness.TASK-001 = {state: ready, ready: true, blockers: []}`;
- records by kind: strategy 1, requirement 1, milestone 1, task 1, decision 1.

The two manual-review items are deliberately not suppressed: a structural pass
is not a strategic PASS, and a recorded approval is not an authenticated human
identity.

## What this example does not prove

- It is not a live INIT/PLAN/NEXT session and records no human decisions.
- It does not demonstrate prompt quality, strategy quality or requirement
  quality; those remain agent-assisted review items.
- It does not prove that a real project's adopted sources were fresh or
  authoritative.
- The identifiers, roles and text are synthetic fixture data.
