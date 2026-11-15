# Operations

Six bounded operations are available as explicit Agent Skills under
`.planner/skills/`. Each operation reads project instructions, governance, the
authority map and only relevant records, then returns a completion envelope.
There is no command router, background process, autonomous loop or execution
launcher.

The normative contracts are
[`references/operation-contracts.md`](../templates/planner-overlay/template/.planner/references/operation-contracts.md)
and
[`references/governance.md`](../templates/planner-overlay/template/.planner/references/governance.md).

## Invocation

No harness configuration is required. Read the skill path and carry out the
operation. Examples:

```text
Read .planner/skills/planner-init/SKILL.md and carry out INIT for this project.
Follow the existing project instructions and retain all existing content
authorities.
```

```text
Read .planner/skills/planner-next/SKILL.md and recommend the next ready task.
Do not execute the prompt or change task state.
```

Replace the path for `planner-status`, `planner-plan`, `planner-change` or
`planner-audit`.

## Completion envelope

```text
operation: INIT | STATUS | PLAN | NEXT | CHANGE | AUDIT
source revision: <commit or working-tree fingerprint>
result: complete | needs_input | blocked | proposed
outputs: ...
changed paths: ... | none
decisions needed: ...
findings/limitations: ...
recommended next operation: ...
```

`complete` never means strategic success or human acceptance. `proposed` means
a concrete proposal awaits a decision. `needs_input` means a consequential
question or approval is missing. `blocked` means authority, source, collision,
schema or required native dependency failure.

## INIT

**Use when:** starting a project, adopting existing planning artifacts, or
resuming an interrupted initialization.

INIT inventories the repository, classifies new/resume/adopt, asks only
consequential questions, optionally uses BMAD product brief/PRD for discovery,
and proposes the authority map, strategy baseline, initial requirements,
verification profile and roles. It creates `planning/**` only after explicit
human approval. It never overwrites an existing path. Repeating INIT resumes.

For existing artifacts it produces a dry-run migration report and exact patch
instead of rewriting sources. See [`migration.md`](migration.md).

## STATUS

**Use when:** asking where the project stands, what is blocked, what evidence is
missing or which decisions are pending.

STATUS is read-only by default and leaves the repository byte-identical. It
reports objectives/outcomes, the active milestone and exit evidence, task
states, blockers, unavailable evidence, pending decisions and one bounded next
action. It separates completed work from achieved outcomes. A saved report is
written only on explicit request under `planning/runs/<run-id>/status.md`.

## PLAN

**Use when:** refining approved strategy into milestones, packages and tasks, or
replanning after an approved change.

PLAN verifies the baseline, uses native BMAD PRD/decomposition for technique,
translates the result into the canonical task contract, applies rolling-wave
detail, runs readiness-only native planning (no sprint ledger), presents an
exact diff and applies only what a human approves. It never implements.

## NEXT

**Use when:** asking what to work on next.

NEXT evaluates the full readiness conjunction, honors the adopted order,
recommends resuming in-progress/review work first, and emits a derived execution
prompt with traceability and a source manifest. Default output is inline; an
explicit save goes to
`planning/prompts/<task-id>-<scope-digest-prefix>.md`.

NEXT does not execute the prompt, reserve the task, change its state, set a
schedule or infer done from a commit.

## CHANGE

**Use when:** a new idea, changed assumption or failed evidence may alter
approved scope or strategy.

CHANGE captures a `CHG-*`, traces impact in both directions, reuses native
BMAD correct-course/PRD update, presents alternatives and an exact proposal,
waits for a human disposition, rechecks source freshness and applies only the
approved diff idempotently. Rejection/defer retains rationale and a revisit
trigger. It never publishes to a tracker or implements.

## AUDIT

**Use when:** before milestone activation/exit, after material change, after
migration, when unauthorized edits or contradictory evidence are suspected, or
as a periodic review.

AUDIT runs the read-only structural checker, optionally native OpenSpec/BMAD
validation, then performs reasoned forward/reverse traceability and strategic
review. Findings have severity, evidence, affected chain, confidence, owner,
repair proposal and required human decision. It saves a report only when asked
and never repairs automatically.

## Structural checker

```bash
uv run --script .planner/scripts/check_planning.py --project . --format text
uv run --script .planner/scripts/check_planning.py --project . --format json
```

Exit `0` means deterministic checks completed without errors; `1` means a
structural/approval invariant failed; `2` means unreadable configuration,
unsupported schema or invalid invocation. Manual-review gaps are always printed.
See [`verification.md`](verification.md).

## Typical first loop

1. Install the overlay and commit it.
2. Run INIT; approve the authority map and strategy baseline.
3. Run PLAN; approve the first milestone and a bounded ready task.
4. Run STATUS to review the outcome and pending decisions.
5. Run NEXT to obtain a prompt; hand it to an execution workflow later.
6. Bring evidence back; use CHANGE for a changed assumption and AUDIT before
   claiming milestone achievement.

## Failure handling

- Missing `planning/planner.yaml`: INIT is required before dependent operations.
- Ambiguous or duplicate authority: stop and report; do not pick a winner.
- Stale approval digest: re-approve the exact current scope through PLAN/CHANGE.
- Missing BMAD: INIT/STATUS/NEXT for sufficient tasks and structural AUDIT still
  work; BMAD-dependent drafting reports the dependency.
- Dirty tree: read-only discovery/reporting is allowed; do not mutate or apply.
- External source unavailable: report the coverage gap; do not pass readiness.
