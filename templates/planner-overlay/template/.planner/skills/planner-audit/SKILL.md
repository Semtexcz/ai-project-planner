---
name: planner-audit
description: Audit planning structure and strategy for traceability, unauthorized scope changes, contradictions, stale evidence and outcome gaps. Use before milestone activation or exit, after material change, or when planning drift is suspected. Reports findings; never auto-repairs.
---

# AUDIT

Read, in order:

1. the target project's instructions and `AGENTS.md` (if present);
2. `../../references/governance.md`;
3. `../../references/operation-contracts.md` (AUDIT);
4. `../../references/information-model.md`,
   `../../references/verification-profiles.md` and, when relevant,
   `../../references/bmad-adapter.md`;
5. `planning/planner.yaml`, the approved baseline and decisions, all current
   canonical records, evidence and Git diffs since the last approved baseline.

## Procedure

### 1. Deterministic layer

Run the read-only checker and retain its JSON output:

```bash
uv run --script .planner/scripts/check_planning.py --project . \
  --format json --source-revision <revision>
```

Use native OpenSpec validate for OpenSpec-owned artifacts and native BMAD
validation where its artifacts are authorities. Report unsupported, unread or
unavailable sources explicitly. Do not claim full coverage over an external
source you could not read.

The checker reports errors, warnings and manual-review items. Its exit `0` is
not a strategic PASS.

### 2. Semantic and strategic layer

Review both directions:

- Forward: `VIS -> OBJ/OUT -> REQ -> MS -> [WP] -> TASK -> evidence`.
- Reverse: delivered work -> task -> requirement -> objective -> strategy.

Look for:

- orphan or unaligned tasks, requirements or milestones;
- approved-scope edits without a decision;
- contradictory requirements, objectives or decisions;
- obsolete or superseded milestones still presented as active;
- tasks whose delivered scope exceeds their approved contract;
- weak, ambiguous or unverifiable acceptance criteria;
- missing, failed, inconclusive, stale or mismatched evidence;
- done tasks with no achieved outcome;
- hypothesis, proposal, mandate and approval conflated;
- software assumptions imposed on non-software deliverables;
- authority conflicts, mutable external sources and unavailable locators.

Cite exact IDs and paths. Distinguish a definite structural violation from a
suspected semantic conflict that a human must adjudicate.

### 3. Classify findings

For each finding record:

- severity: `blocking`, `warning` or `information`;
- observed evidence and source revision;
- affected chain;
- confidence;
- accountable owner;
- proposed repair;
- required human decision;
- whether a CHANGE or PLAN action is needed.

Do not repair automatically. Do not approve, retire, expand or mark anything
done.

### 4. Save only when requested

If the user explicitly asks for a saved report, write
`planning/runs/<run-id>/audit.md` using `../../assets/audit-report.md`. Include
the source revision, scope of review, commands/results actually obtained,
unverified coverage and the distinction between schema results and reasoned
judgment. Otherwise return the report inline and leave the repository
byte-identical.

## Triggers

Before a new milestone becomes active, at milestone exit, after a material
requirement/strategy change, after contradictory evidence, after migration and
when unauthorized edits are suspected. A weekly review while the project is
active is a human reminder policy, not a scheduler.

## Output

Return the common envelope with findings, limitations and one recommended next
operation. `complete` means the audit was performed; it never means the plan
passed or the project is healthy. A blocking finding must remain visible even
when every child task is done.
