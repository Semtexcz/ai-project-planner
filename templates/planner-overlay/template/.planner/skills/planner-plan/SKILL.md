---
name: planner-plan
description: Refine approved strategy into outcome-based milestones, bounded work packages and approved tasks for the current horizon. Use when the user asks to plan, replan, decompose an approved milestone, or produce a roadmap. Reuses native BMAD PRD and decomposition skills; does not implement work.
---

# PLAN

Read, in order:

1. the target project's instructions and `AGENTS.md` (if present);
2. `../../references/governance.md`;
3. `../../references/operation-contracts.md` (PLAN) and
   `../../references/verification-profiles.md`;
4. `../../references/bmad-adapter.md`;
5. `planning/planner.yaml`, approved strategy/objectives/outcomes,
   requirements/constraints, current milestone, evidence and decisions;
6. relevant Git history and approved changes.

Do not plan from an unapproved idea. If the requested direction changes approved
strategy, stop and recommend CHANGE.

## Procedure

### 1. Verify the baseline

Confirm the strategy and active milestone are approved and that cited
requirements are still approved and relevant. Record the source revision. Look
for failed/inconclusive evidence, contradictory decisions or stale context. If
the baseline is missing, return `blocked` with the smallest required action.

### 2. Reuse native BMAD for technique

Follow `../../references/bmad-adapter.md`. Use `bmad-prd` create/update/validate
for requirements work and `bmad-create-epics-and-stories` for decomposition,
bounded to the approved current milestone. One agent only: no subagents, no paid
delegated calls, no publishing, no execution.

Write BMAD drafts under `planning/runs/bmad/...` or the configured artifacts
root. They are drafts, not authority. If BMAD is unavailable, report the missing
dependency; do not invent a replacement planning workflow.

### 3. Translate into the canonical model

- Epic-like groups may become optional embedded work packages (`WP-*`).
- Story-like units may become tasks (`TASK-*`).
- Preserve the real domain deliverable: specification, analysis, experiment,
  review report or software artifact. Do not force software architecture or UX
  documents when no deliverable needs them.
- Every task needs exactly one milestone, at least one approved requirement, an
  objective/outcome trace, boundaries, dependencies, context, deliverables,
  criteria, verification, reviewer, priority and size.
- Do not fabricate an alignment link for unrelated work.

### 4. Apply rolling-wave detail

- Current milestone: full outcome, exit criteria, requirements, constraints,
  dependencies, packages where useful and bounded ready tasks.
- Next milestone: outcome, candidate packages, major dependencies, evidence gaps
  and likely decisions. Tasks may remain drafts.
- Distant milestones: outcome, strategic rationale, dependencies and uncertainty
  only.

Do not pre-decompose unknown work or fabricate dates.

### 5. Run readiness-only native planning

Use `bmad-sprint-planning` for readiness assessment only. Do not create a
sprint-status file or a second task ledger. Planner's approval, traceability and
outcome gates apply in addition to native readiness.

### 6. Reconcile and present the exact diff

Compare the proposal with existing owners. Update drafts or produce an exact
patch. Present changed milestone outcomes, scope, dependencies, priorities,
new obligations/exclusions and consequences for human approval. Routine
decomposition inside an explicitly delegated approved boundary may be recorded
without a new product decision; adding obligations, exclusions or consequential
reordering cannot.

### 7. Apply only what was approved

After explicit approval:

- apply only the approved diff at the approved paths;
- create/update records using the schemas and blank asset structure;
- for each normative local context source, record the file's SHA-256 in the
  context entry alongside the revision and purpose;
- bind approvals to exact final `scope_sha256` values and accepted decisions;
- invalidate affected prompts and reread references;
- run the read-only checker and report findings;
- recheck readiness and record remaining unknowns.

Never overwrite unrelated canonical content because BMAD produced a newer
draft.

## Milestone and task gates

A milestone becomes active only by explicit Product Owner decision. At most one
milestone is active. A task becomes ready only through the full readiness
conjunction in `governance.md`; `ready` is not a label an agent may assign
without approval and satisfied gates.

Do not invoke build, build-auto, dev-story, apply or any execution skill.

## Output

Recommend a roadmap view (ordered milestones, no copied exit criteria),
milestone/package/task records, readiness findings and pending decisions. Run:

```bash
uv run --script .planner/scripts/check_planning.py --project . --format json
```

Return the common envelope. `proposed` means the diff awaits approval. `blocked`
means an upstream planning dependency is missing. `complete` only after the
approved diff is applied and checks pass.
