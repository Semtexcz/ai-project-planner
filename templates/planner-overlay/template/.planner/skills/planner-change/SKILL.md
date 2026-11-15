---
name: planner-change
description: Capture an idea, changed assumption or failed evidence as a change proposal and present its full impact and disposition options. Use when scope, strategy or requirements may need to change. Does not modify approved scope without explicit human approval.
---

# CHANGE

Read, in order:

1. the target project's instructions and `AGENTS.md` (if present);
2. `../../references/governance.md`;
3. `../../references/operation-contracts.md` (CHANGE);
4. `../../references/bmad-adapter.md`;
5. `planning/planner.yaml`, the approved strategy/requirements/milestones/tasks
   affected by the idea, decisions, evidence and any saved prompts;
6. the original source of the idea (message, review, failure report or
   observation) and its revision.

## Procedure

### 1. Capture without changing scope

Create a `CHG-*` record in state `captured` at the project's change authority.
Preserve the source, date and original wording. Link earlier related ideas
instead of deleting or duplicating history. Creating this proposal does not
authorize any change.

### 2. Trace impact in both directions

Upward: affected outcomes/objectives/requirements/strategy choices.
Downward: milestones, packages, tasks, dependencies, prompts, evidence and
completed work. Note:

- constraints and trade-offs;
- invalidated approvals and content digests;
- affected saved prompts that must be regenerated;
- opportunity costs and work that would be wasted;
- unresolved questions and required follow-up verification.

Estimate impact qualitatively when evidence does not support a number.

### 3. Reuse native BMAD for analysis

For a substantial change where a PRD and epics exist, or a faithful derived
packet can supply them, use `bmad-correct-course` per
`../../references/bmad-adapter.md`. Otherwise use `bmad-prd` Update on the
relevant requirement proposal. Never pretend correct-course works without its
required inputs. Use one agent, no subagents, no publishing, no execution. All
upstream editable artifacts remain drafts until approved.

### 4. Present alternatives and an exact proposal

State keep / reject / defer / narrow / pivot alternatives with consequences, a
recommendation, exact proposed deltas, unresolved questions, approvers and
required verification. A pivot may supersede the original strategy only with
explicit rationale; the old baseline remains historical. Never delete the old
decision.

### 5. Wait for a human disposition

Record the decision as `DEC-*` with actor, ISO date, source and exact target
digests. Reject/defer keeps the existing plan intact and records a revisit
trigger. Do not infer consent from silence, a generic "looks good", a merged PR
or an agent-written `approved` state.

### 6. Apply only after approval and freshness check

Verify the source revision has not changed since the proposal. If it has,
refresh the proposal instead of applying a stale diff.

After approval:

- apply only the approved local planning changes through their existing owners;
- record the decision and supersession;
- update approval digests and invalidate affected prompts;
- re-run PLAN for affected horizons only;
- run the read-only checker;
- report partial application explicitly and never mark it complete.

Application must be idempotent against the recorded change ID and targets.

## Prohibitions

No implementation, automatic scope expansion, external tracker publishing,
deletion of history, or overwrite of another owner's text. Do not change
approved scope while merely capturing or assessing an idea.

## Output

Return the retained `CHG` record, impact/proposal, explicit disposition, reviewed
plan diff if approved, and invalidated prompt list. Use `proposed` until a human
disposition; `complete` only after an approved change is fully applied and
verified. Recommend the next ACTION (PLAN, NEXT, AUDIT or a targeted review).
