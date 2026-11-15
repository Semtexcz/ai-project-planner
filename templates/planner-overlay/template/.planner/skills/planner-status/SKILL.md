---
name: planner-status
description: Report current planning state, evidence coverage, blockers and uncertainty without changing the project. Use when the user asks where the project stands, what is blocked, whether a milestone is achieved, or which decisions are pending.
---

# STATUS

Read, in order:

1. the target project's instructions and `AGENTS.md` (if present);
2. `../../references/governance.md`;
3. `../../references/operation-contracts.md` (STATUS);
4. `planning/planner.yaml` and the authoritative records it names;
5. relevant evidence, decisions, changes and recent Git history.

Do not read unrelated private sources or contact external systems.

## Procedure

1. Record the source revision (commit or working-tree fingerprint).
2. State why the project exists and the approved strategic objective/outcome
   chain, citing `VIS`/`OBJ`/`OUT` IDs.
3. Identify the active milestone from its authoritative state, not from
   `current_milestone` alone. Report its outcome, exit criteria and evidence
   status. If no milestone is active, say so.
4. Report the next horizon at the detail actually recorded. Do not invent tasks
   or detail for distant milestones.
5. Summarize task states by ID. Separate draft, ready, in-progress, review,
   done, blocked and cancelled. For done work, show whether reviewed evidence
   exists; do not equate done tasks with an achieved outcome.
6. Report blockers, risks, missing or failed/inconclusive evidence, unresolved
   authority and pending decisions. An unavailable source is `unknown`, never
   assumed healthy.
7. Show criterion coverage as counts with denominators and state the caveat
   that this is not outcome validation. Avoid pseudo-precise percentages.
8. Recommend exactly one bounded next planning or review action.

You may optionally run the read-only structural checker and cite its result:

```bash
uv run --script .planner/scripts/check_planning.py --project . --format json
```

A checker pass is not a strategic PASS. Native BMAD status is used only if its
tracking file is the adopted task authority; otherwise read canonical tasks and
do not create a sprint file.

## Prohibitions

Do not alter priorities, approve or reject scope, mark work done, change task
state, create a summary ledger, start a milestone or select/launch execution.

## Output

Default: inline report only. If and only if the user explicitly asks to save it,
write `planning/runs/<run-id>/status.md` with the source revision and a
derived-artifact header. Otherwise the repository must remain byte-identical.

Return the common envelope. `complete` means the report was produced, not that
the project is healthy.
