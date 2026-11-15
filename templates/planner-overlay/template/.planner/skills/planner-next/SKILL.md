---
name: planner-next
description: Select one ready approved task and emit a derived execution prompt with full traceability, or explain precise blockers when nothing is ready. Use when the user asks what to work on next. Never executes the prompt or changes task state.
---

# NEXT

Read, in order:

1. the target project's instructions and `AGENTS.md` (if present);
2. `../../references/governance.md`;
3. `../../references/operation-contracts.md` (NEXT);
4. `../../assets/prompt.md`;
5. `planning/planner.yaml`, the active milestone, task contracts, dependencies,
   approvals, constraints, context sources and recent evidence;
6. any adopted order authority (for example a task sequence file) named by the
   project.

Also run the read-only checker:

```bash
uv run --script .planner/scripts/check_planning.py --project . \
  --format json --source-revision <current-revision>
```

A checker error blocks an affected task. A checker pass does not by itself make
a task ready.

## Procedure

### 1. Evaluate readiness

Apply the full readiness conjunction in `governance.md`. Do not rely on the
word `ready`. Exclude drafts, cancelled tasks, distant milestones, unauthorized
scopes, unsatisfied dependencies, stale context, unresolved approvals and
blocking audit findings.

If work is already `in_progress` or `review`, recommend resuming or reviewing it
before suggesting an additional start. Do not silently claim new capacity.

External/adopted sources must be accessible and fresh enough for the decision.
If freshness cannot be established, report the task as not ready rather than
guessing.

### 2. Choose deterministically

Respect the project's adopted order:

1. explicit task order / legacy sequence authority;
2. otherwise approved priority `P0` before `P1` before `P2`;
3. then roadmap/package order;
4. then stable task ID.

Explain every dependency-driven skip. This is bounded selection, not an
optimizer or scheduler.

If no task is ready, report each blocker and the smallest planning, approval or
review action that resolves one. Do not manufacture a ready task, infer done
from a merged PR, start a future milestone or relax a gate.

### 3. Build the derived prompt

Use the structure in `../../assets/prompt.md` and fill it only from
authoritative approved content. Include:

- task ID and the statement that the prompt is derived, not authority;
- repository/source revision, task authority path and current scope digest;
- recommended model: DeepSeek V4.1 Flash, reasoning HIGH; escalation to
  DeepSeek V4 Pro HIGH only under the recorded policy (advisory labels);
- authoritative sources to reread, with normative versus background context;
- verbatim/faithful objective, rationale and trace
  `VIS -> OBJ/OUT -> REQ -> MS -> [WP] -> TASK`;
- exact deliverables, includes, excludes, constraints and prerequisites;
- each criterion ID, verification method, expected evidence and reviewer;
- the specific stop point requiring approval;
- required return evidence and the reminder that producing work does not prove
  acceptance.

Do not invent requirements, files or decisions. If a value is missing, the task
is not ready.

### 4. Save only when asked

Default: return the prompt inline. If the user explicitly asks to save it, write
`planning/prompts/<task-id>-<scope-digest-prefix>.md` with a derived-artifact
header and source manifest. Never edit an existing prompt to add scope; generate
a new one when normative scope or relevant constraints change.

## Prohibitions

Do not run the prompt, invoke an agent, reserve or lock the task, move it to
`in_progress`, mark it ready/done, set a schedule, alter priorities or publish
anything. Two invocations on identical sources must select the same task and a
substantively identical contract.

## Output

Return the common envelope followed by the prompt and readiness evidence.
`complete` means a prompt was produced, not that work was executed or accepted.
