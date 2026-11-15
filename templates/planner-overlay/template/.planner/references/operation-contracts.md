# Operation contracts (runtime reference)

Six operations exist: INIT, STATUS, PLAN, NEXT, CHANGE, AUDIT. Each is a mode of
one explicit Agent Skill invocation, not a command router. The common envelope
and prohibitions are in `governance.md`; this file defines operation-specific
behaviour.

## INIT - discover, establish authority, or propose migration

**Inputs:** project root, stated intention or existing artifacts, optional
category, existing instructions/overlay answers/BMAD/OpenSpec inventory.

**Modes:** new project (default), adopt/migrate (see `migration.md`), resume.

1. Inventory relevant files using native search/Git. Exclude secrets,
   build/vendor directories and private sources outside the authorized project.
   Inspect dirty state and path collisions.
2. Classify new project versus adoption/migration. Identify authors, mandates,
   historical artifacts, derived/proposed material and contradictions. Ask only
   consequential missing product questions.
3. For a new project, use `bmad-product-brief` for discovery and a right-sized
   `bmad-prd` when requirements need development, following
   `bmad-adapter.md`. Create proposed native records from the reviewed result;
   do not duplicate BMAD's elicitation.
4. Propose the authority map, purpose/strategy baseline, initial
   outcome/requirements, verification profile and approval roles. INIT may stop
   at a strategy baseline; PLAN handles roadmap and decomposition.
5. For an existing project, produce the dry-run report defined in
   `migration.md`. Do not change authoritative files or authority designation
   until the exact mapping/change set is approved.
6. Create new project-owned files only after the relevant initialization scope
   is approved. Never overwrite an existing path. Use the blank assets under
   `.planner/assets/` as structure, replacing placeholders with reviewed
   content. Register accepted approvals and provenance. Do not ask again for
   unchanged content the human already approved explicitly.
7. Repeating INIT discovers existing state and resumes. It never reseeds or
   resets content. It may create a new report only when explicitly requested.

**Outputs:** project-owned `planning/planner.yaml`, approved/proposed records as
clearly labelled, or a migration report and exact proposed patch.

**Failure:** ambiguous source owner, collision, unsupported schema, unapproved
adoption. Do not write.

**Stop before:** creating files from unapproved strategy/scope, overwriting an
existing path, switching authority, or applying a migration patch.

## STATUS - read current state and uncertainty

**Inputs:** authority map, strategy/objectives, current milestone, tasks,
evidence and pending decisions.

1. Read authoritative sources only. Record the source revision.
2. Report why the project exists, approved objectives/outcomes, the active
   milestone and its outcome/exit-criterion evidence, next horizon, task states,
   blockers, risks, missing evidence, unresolved authority and pending
   decisions.
3. Clearly separate completed work from achieved outcomes and proposals from
   approved scope. Cite source IDs/paths. Use `unknown` for unavailable
   evidence. Avoid pseudo-precise percentages. Criterion coverage may be shown
   as counts with denominators and the caveat that it is not outcome validation.
4. Use native BMAD status only if its tracking file is the adopted task
   authority. Otherwise read canonical tasks directly; do not create a sprint
   file.
5. Recommend one bounded next planning or review action.

**No files are written** unless the user explicitly requests a saved report
under `planning/runs/<run-id>/status.md`.

**Acceptance:** a blocked active milestone and all pending approvals remain
visible even when every child task is done. An unsaved STATUS leaves the
repository byte-identical. STATUS does not alter priorities, approve scope, mark
work done or select/launch execution.

## PLAN - revise horizons and refine approved milestone work

**Inputs:** approved strategy, outcomes, requirements/constraints, evidence and
approved changes. Read historical decisions before proposing a different
direction.

1. Verify the baseline and current relevance. Unapproved strategy changes become
   CHANGE proposals; do not slip them into a plan.
2. Use native `bmad-prd` create/update/validate for requirements work and
   `bmad-create-epics-and-stories` for decomposition. Supply the approved
   current milestone as the bounded focus and label distant work outcome-only.
   Do not reproduce BMAD's planning procedure in the skill.
3. Translate the result through the canonical task contract: epics can suggest
   packages; stories can suggest tasks. Preserve domain deliverables, actual
   requirements and genuine dependencies. Do not force a software
   architecture/UX document when no output depends on one.
4. Reconcile the proposal with existing owners. Update drafts or produce an
   exact patch; do not overwrite canonical content because BMAD emitted a newer
   draft.
5. Run `bmad-sprint-planning` with readiness-only intent where applicable. Do
   not generate sprint tracking. Apply planner approval/traceability/outcome
   gates in addition to native readiness.
6. Present changed milestone outcomes, scope, dependencies, priorities and
   consequences for approval. Routine decomposition within an explicitly
   delegated approved boundary may be recorded without a new product decision;
   adding obligations, exclusions or consequential reorderings cannot.
7. After approval, apply only the approved plan diff, bind approvals, and
   recheck references/readiness. Record distant unknowns instead of prematurely
   solving them.

**Rolling-wave detail:** the current milestone has outcome/exit criteria,
requirements, constraints, dependencies, packages where useful, bounded ready
tasks, verification/reviewer and open risks. The next milestone has outcome,
candidate packages, major dependencies, evidence gaps and likely decisions;
tasks may remain drafts. Distant milestones have outcomes, rationale,
dependencies and uncertainty only.

**Outputs:** ordered roadmap view, milestone records with outcome gates, limited
packages/tasks, readiness findings and pending decisions. No implementation.

**Stop before:** any new obligation, exclusion, consequential reordering,
milestone activation, approval or implementation.

## NEXT - choose ready work and emit a prompt

**Inputs:** current approved milestone, explicit task order/priorities, complete
task contracts, constraint/dependency/approval records and source freshness.

1. Evaluate readiness per `governance.md`. No write to task state. If work is
   already in progress, recommend resuming or reviewing it before suggesting
   additional starts; do not silently claim new capacity.
2. Respect the project's adopted order (explicit `task_order`, legacy sequence
   authority, or ordering policy). Otherwise order eligible tasks by approved
   priority (`P0` before `P1` before `P2`), then explicit roadmap/package order,
   then stable task ID. Explain dependency-driven skips. No optimization or
   scheduler.
3. If none is ready, report precise blockers and the smallest planning,
   approval or review action that resolves one. Do not manufacture a ready
   task, infer done from a merged PR, or start a future milestone.
4. Generate the prompt in `assets/prompt.md` from the selected approved
   contract. Include traceability and a freshness manifest. Default output is
   inline; an explicit save goes to
   `planning/prompts/<task-id>-<scope-digest-prefix>.md` with source revision
   and a derived-artifact header.
5. End with the prompt and readiness evidence.

**Do not:** run the prompt, invoke an agent, reserve/lock the task, move it to
`in_progress`, set a schedule, or reuse a stale prompt merely because its
filename exists.

Two invocations on identical sources must recommend the same task and a
substantively identical contract. Prose phrasing may vary. The execution agent
must reread sources and stop on a scope/digest change.

## CHANGE - controlled idea intake and replanning proposal

**Inputs:** unexpected idea, changed requirement/assumption, failed evidence or
a proposed strategic pivot; the original source.

1. Create `CHG-*` as `captured`, without modifying approved scope. Dedupe by
   references to earlier ideas; do not delete history.
2. Trace impact upward to requirements/objectives/vision and downward to
   milestones/packages/tasks/dependencies/prompts/evidence. Note constraints,
   trade-offs, completed work affected, invalidated approvals and opportunity
   costs. Estimate qualitatively if evidence does not support a number.
3. Reuse `bmad-correct-course` for a substantial change where a PRD and epics
   exist or a faithful derived packet can supply them. Otherwise use
   `bmad-prd` Update on the relevant requirement proposal. Do not pretend
   correct-course works without its required inputs. All upstream editable
   artifacts are drafts until approved.
4. Present keep/reject/defer/narrow/pivot alternatives, a recommended option,
   exact proposed deltas, unresolved questions, approvers and required
   follow-up verification. A pivot can supersede the original strategy with
   explicit rationale; the old baseline remains historical.
5. Wait for the human disposition. Rejection/defer keeps the existing plan
   intact and retains rationale plus a revisit trigger.
6. Before applying an approved change, recheck the source revision. If it
   changed, refresh the proposal; never apply a stale diff.
7. Apply only approved local planning changes through existing owners. Record a
   DEC, supersession, changed approval digests and affected prompt
   invalidation. Re-run PLAN for affected horizons only. Application is
   idempotent against the recorded change ID and targets; partial application
   is reported and never marked complete.

**Outputs:** retained idea, impact/proposal, explicit disposition and a reviewed
plan diff if approved. No implementation, automatic scope expansion or tracker
publishing.

**Stop before:** approved scope changes, strategy pivots, applying a diff,
changing authority or publishing anywhere.

## AUDIT - structural checks plus strategic review

**Inputs:** approved baseline/decisions, current canonical records, Git diffs
since the last approved baseline, recent evidence, authority map and relevant
new ideas.

1. Run the read-only structural checker:

   ```bash
   uv run --script .planner/scripts/check_planning.py --project . \
     --format json [--source-revision <revision>]
   ```

   Use native OpenSpec validate for OpenSpec-owned artifacts and native BMAD
   validation where its artifacts are authorities. Report unsupported/unread
   sources explicitly.
2. Agent review checks objective -> requirement -> milestone -> task alignment
   and reverse coverage; contradiction, unauthorized normative edits, orphan
   tasks, obsolete milestones, scope excess in delivered work, weak acceptance
   criteria, missing/inconclusive/stale evidence and inappropriate software
   assumptions.
3. Cite exact source IDs/locations and baseline differences. Semantic
   contradictions and strategic relevance require reasoned review; a schema pass
   cannot establish them. Reuse BMAD PRD Validate/readiness where relevant.
4. Findings are `blocking`, `warning` or `information`, with observed evidence,
   affected chain, confidence, owner, proposed repair and required human
   decision. Separate definite violations from suspected semantic conflicts
   needing adjudication.
5. Save only the requested report under `planning/runs/<run-id>/audit.md`. Do
   not auto-repair, approve, retire or expand scope. Offer the corresponding
   CHANGE/PLAN action.

**Triggers:** before a new milestone becomes active, milestone exit, material
requirement/strategy change, contradictory evidence, migration and discovery of
unauthorized edits. Default periodic recommendation: a weekly review while the
project is active, adjustable by the owner. This is a human reminder policy, not
a scheduler or a mandatory time-based block.

At minimum NEXT checks current relevant blockers, scope approvals and source
freshness; it cannot rely on a stale clean audit.
