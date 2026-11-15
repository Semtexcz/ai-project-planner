# v0.1 acceptance evidence

Date: 2026-11-15. Platform: Linux x86-64. Implementation model: DeepSeek V4.1
Flash, reasoning HIGH. No OpenAI model was used for implementation, tests,
reviews or repairs. No release tag was published.

This file records actual results, not intended results. Deterministic,
integration and agent-assisted evidence are kept separate.

## Environment

| Item | Observed |
| --- | --- |
| OS | Linux x86-64 |
| Python | 3.14.4 system; 3.12.13 used by `uv` |
| uv | 0.11.28 |
| Node / npm | v22.20.0 / 11.12.1 |
| Copier | 9.19.1 |
| BMAD | 6.12.4 |
| Agent Skills validator | `skills-ref@0.1.5` |
| OpenSpec | 1.16.0 and 2.0.0 (disposable installs) |
| pytest | 8.4.2 |
| PyYAML / jsonschema | 6.0.3 / 4.25.1 |

## Commands and aggregate results

```bash
uv sync --locked
uv lock --check
uv run --locked pytest -m "not integration"
uv run --locked pytest -m integration
```

At the final recorded run:

- `uv lock --check` passed.
- Offline suite: **128 passed, 6 deselected**.
- Integration suite: **6 passed, 128 deselected**.
- Integration tests used disposable directories/HOME and network access to npm
  and GitHub. They did not modify any reference repository.
- The checker was also exercised through its PEP 723 entry point with
  `uv run --script`.

Exact pass counts are a snapshot of this commit and environment; rerun the
commands to reproduce.

## Independent critical review

A separate read-only reviewer context using DeepSeek V4.1 Flash (HIGH) inspected
the implementation against the approved plan. Findings that were fixed and
covered by tests:

- readiness is now computed from the task's objective/strategy, milestone,
  requirements, approvals, decisions and dependencies, and repository-level
  errors block all ready tasks;
- `rel#field` schema errors and cross-record errors block the affected task;
- change dispositions require an accepted, provenanced decision bound to the
  exact change scope;
- an approved strategy without approval, and an unreferenced accepted decision
  without provenance, are errors;
- inconclusive evidence cannot support `done` or `achieved`;
- external gate evidence must cite the gate criterion;
- requirement/milestone approvals were restored to `execution.approvals` and
  task approvals remain in `scope.approvals`, matching the approved field
  grouping;
- active/approved milestones and ready-task include/exclude boundaries cannot be
  empty;
- alias cycles, unhashable YAML keys, invalid calendar dates, unknown
  authorization references and missing revisit triggers are diagnosed.

Remaining findings are recorded below as limitations: Copier cannot enforce the
unowned-`.planner` collision stop itself, and adopted/delegated authorization
remains a human-review boundary instead of deterministic readiness.

## A - Empty project vertical slice

Status: **deterministic structure verified; live human-scored session pending.**

Observed:

- `tests/fixtures/empty/INTENT.md` supplies a document-conversion intention.
- The test constructs one strategy, objective/outcome, approved requirement,
  active milestone, approved ready task and accepted decision in a disposable
  project.
- Exactly one task is ready. Its contract contains every required field,
  objective/milestone/requirement trace, criteria, verification and approval.
- Removing the authorization removes readiness and produces
  `TASK_NOT_AUTHORIZED`; no prompt should be emitted in that state.
- Two checker runs on identical sources produce identical JSON and select the
  same ready task.
- The checker leaves the tree byte-identical; no application, `AGENTS.md` or
  prompt file is created.
- A done task with passing task evidence does not change the milestone from
  `active` to `achieved`; only reviewed milestone evidence plus a human decision
  can do that.

Not verified here: an independent DeepSeek session scored by a human rubric.
The prompt structure is covered by `assets/prompt.md` assertions, not by a live
execution.

## B - Bookvoice-like adoption

Status: **deterministic fixture verified. Both TASK-075 occurrences are reported;
adoption by reference retains IDs and edges.**

Observed:

- `tests/fixtures/bookvoice-like/` has six unique task IDs in five state
  folders, two `TASK-075` occurrences with conflicting folder/frontmatter/body
  states, four explicit `TASK-075` blocking prerequisites, related-only links,
  an artifact gate (`docs/contracts/sync-contract.md`), a backlog card that is
  not ready, and cards whose evidence is explicitly limited.
- Tests reconcile every unique ID, occurrence count, blocking edge, related
  edge and artifact gate against `manifest.json`.
- A contract-level dry-run test creates only
  `planning/runs/run-1/migration.md`; source bytes are unchanged. It does not
  drive the INIT skill. A dirty tree is not an in-place apply target.
- Approved adoption by reference registers one authority per ID, leaves source
  bytes untouched, resolves every reference, and reports external content for
  manual review.
- Repeated adoption is byte-idempotent. Partial adoption reports the missing ID.
  Source mutation after a report changes the recorded hash and is detected.
  Rollback with a revert commit in a disposable Git repository restores the
  baseline.
- Duplicate authority is refused, not last-writer-wins: the test helper raises
  until an explicit occurrence is adjudicated. With the ready-folder occurrence
  chosen, the duplicate remains in the manifest conflict list and the source
  bytes are preserved. This is a test-harness contract, not a live INIT
  session.

Not verified here: a live Bookvoice checkout or a human-scored migration
session. The real repository was not read or written.

## C - DeepPlant-like engineering applicability

Status: **deterministic fixture verified; no current-work authorization from a
future direction.**

Observed:

- `tests/fixtures/deepplant-like/` preserves vision, strategy, product, roadmap,
  governance index, semantic-core ADR, process/physical model constraint and a
  historical gate as separate authorities.
- Byte hashes of all preserved sources remain unchanged.
- The fixture classifies simulation as a future direction. A bounded generic
  engineering project represents the current outcome and retains the simulation
  idea only as a captured `CHG`, never as a ready task. This does not automate
  reading the actual DeepPlant authority files; it tests the classification and
  structural rule.
- The current outcome is represented by a bounded engineering task with
  semantic-invariant, unit and counterexample verification; no software
  assumptions are forced.
- Issue coverage explicitly lists `ISSUE-102` as unavailable, so full
  detailed-task coverage is not claimed.
- The historical gate remains historical and does not authorize presentation
  work.

Not verified here: live GitHub Issue reading or a human-scored engineering
review session.

## D - PLOS-like methodology applicability

Status: **deterministic fixture verified; no software artifacts imposed.**

Observed:

- `tests/fixtures/plos-like/` keeps Z mandates, N proposals, D design decisions
  and H hypotheses distinct. `CON-01` keeps software/storage independence.
- I2 is complete; I3 is proposed and is **not** active. A methodology task for a
  conceptual-model consistency review remains `draft` until owner approval; the
  ready set is empty.
- The task deliverable is a reviewed semantic specification/diagram/scenario
  report. Verification uses definition comparison, counterexamples and semantic
  walkthroughs, not task counts or code tests.
- No API/database/app/mobile artifact appears in the task contract.
- Adoption registers references only; it does not copy the 36 domain concepts
  into planner entities or impose records/software on method users.
- The semantic review evidence states its limitations and does not claim user
  benefit.

Not verified here: a human-scored methodology session or empirical validation
of the methodology. None was performed or claimed.

## E - Controlled CHANGE

Status: **deterministic state/diff behaviour verified; proposal quality is not
human-scored.**

Observed:

- A captured cloud-sync idea leaves every approved scope byte unchanged.
- Impact is recorded against objective/requirement/milestone/task and calls out
  invalidated approval, prompt and evidence assumptions.
- Rejection is recorded through an accepted decision and retains a revisit
  trigger; the plan stays unchanged.
- A narrowed approved alternative changes only the target task scope, adds a new
  decision and retains the old decision. Unrelated records remain byte-identical.
- At the primitive gate level, a changed source baseline produces a different
  scope digest, so an old patch cannot be treated as current. The test does not
  execute a live CHANGE apply or a model-driven staleness check.
- No tracker publishing or implementation occurs.

Not verified here: BMAD correct-course execution and a human-scored proposal
session. The test environment has no provider-backed BMAD run.

## F - AUDIT and drift

Status: **deterministic findings verified; semantic contradiction detection is
reserved for reasoned review.**

Observed:

- An orphan task with unknown objective/requirement produces
  `REFERENCE_DANGLING`.
- Changing an approved requirement without a decision produces
  `APPROVAL_STALE`, `DECISION_TARGET_DRIFT` and
  `TASK_REQUIREMENT_NOT_AUTHORIZED`; the affected task is excluded from the ready
  set.
- Checker runs leave all bytes unchanged; no source is auto-repaired.
- Two opposed retention clauses are preserved and cited from the drift fixture.
  The checker does **not** fabricate a semantic-contradiction proof; the audit
  report template requires a cited semantic finding and a human decision.
- A done-task/active-milestone state remains visibly distinct from achieved
  outcome.

Not verified here: a live Flash audit transcript and human assessment of
semantic coverage.

## G - Independent overlays, update and rollback

Status: **minimal independent overlay fully verified offline; real ai-devkit
coexistence verified for installation in disposable destinations.**

Observed:

- Two tagged planner revisions and an independent second overlay install in
  either order. Answers files are separate and name their own source/revision.
- Planner copy emits only `.planner/**` and `.copier-planner-answers.yml`.
  Application, `AGENTS.md`, README, OpenSpec, planning content and the other
  overlay are unchanged.
- Planner update changes only its managed diff and answers file. Project
  planning edits, other-overlay bytes and deleted project planning files are
  preserved.
- Second-overlay update leaves planner bytes and provenance unchanged.
- A same-region edited managed conflict exposes both sides with inline markers;
  the user must review it. Copier writes conflict markers rather than silently
  choosing a side.
- Reverting the isolated planner update commit restores planner v0.1.0 while a
  later project planning edit survives.
- A preflight collision test proves the documented check detects an existing
  `.planner` or planner answers file. **Plan G's stronger assertion that an
  unowned `.planner` collision "stops before copying" is not enforced by Copier
  itself**; only the mandatory human preflight detects it. A user who bypasses
  the preflight can have matching managed paths overwritten. No install wrapper
  was added because the approved architecture forbids one. This is a remaining
  defect against plan G, mitigated by documentation and the preflight test.
- Integration: the inspected ai-devkit commit
  `cc04bcef80b3838cd5956a872717b65949190468` was cloned into a temporary
  directory. Planner and devkit were copied in **both orders** into disposable
  destinations. Both answers files named their own source; planner bytes and
  provenance were unchanged by devkit in the planner-first order, and devkit's
  generated `AGENTS.md` was unchanged by planner in the devkit-first order.
  Devkit owns `AGENTS.md`; in planner-first order its copy requires an explicit
  overwrite decision, which the test exercises only in a disposable directory.
- Integration: the deployed PEP 723 checker entry point
  (`uv run --script .planner/scripts/check_planning.py`) was executed against a
  fixture project.

Not verified here: a **newer** ai-devkit revision update in both order
combinations. The pinned inspected revision was used; update ordering is proven
with the minimal independent overlay. No reference repository was a
destination.

## Negative and safety checks

Executed by the offline suite:

- dangling references and wrong reference types;
- missing/multiple active milestones and current-milestone disagreement;
- dependency cycles and self-dependency;
- duplicate IDs, duplicate authority roots, overlapping authority roots and
  dangling aliases;
- malformed YAML, duplicate YAML keys, unsupported schema version and unreadable
  configuration;
- unknown owner, invalid package and unknown task order;
- missing/inconclusive/failing evidence and stale subject revision;
- stale approval digest, unaccepted decision, incomplete provenance and missing
  approval target;
- missing context, traversal outside the project root and symlink escape;
- `-000` placeholder records, explicit TBD/TODO/replace-me values, and blank
  project identity cannot be approved or ready;
- checker read-only byte equality and refusal to execute record commands;
- Copier forbidden-output allowlist and unknown-path preservation.

## Unverified capabilities and limits

- No independent human rubric assessment of live DeepSeek planning sessions.
  The implementation agent performed the deterministic fixture work, but that is
  not a substitute for separate-agent and human review.
- Deterministic `ready_tasks` excludes tasks whose objective, milestone,
  requirement, dependency or approval comes from an adopted/external source, or
  whose authorization relies on bounded delegation. They appear in
  `review_required_tasks` with the manual rule; NEXT must obtain human
  confirmation before emitting an executable prompt. This is a deliberate trust
  boundary, not a claim that adopted-only projects are deterministically ready.
- No live BMAD product-brief/PRD/epics/readiness/correct-course planning run was
  executed. Installer, generated paths, resolver merges and reinstall
  preservation were verified.
- No macOS or Windows verification. Linux x86-64 only.
- No real GitHub Issue connector, ETag/revision capture or external freshness
  check. Unavailable external sources are manual-review gaps.
- No real OpenSpec apply/archive workflow. Init paths and read-only validation
  were verified for 1.16.0 and 2.0.0.
- Copier conflict markers are not a Git unmerged index state. Human review is
  still required; the test asserts both sides and a changed working tree.
- No publication, tag, push, external repository change or release notes
  publication. The commit remains local.
- The checker cannot authenticate identity/consent, prove semantic
  contradictions, judge strategic relevance or prove a verification method was
  appropriate or executed.

## Reference repository safety

No test or command in this repository used `Semtexcz/DeepPlant`,
`Semtexcz/Bookvoice` or `Semtexcz/PLOS` as a destination. The only external
clone was public ai-devkit in a pytest temporary directory, read-only apart from
its own checkout. No reference repository was modified.

## Release readiness

The implementation is a v0.1.0 release candidate, not a published release.
Human acceptance of the agent-assisted items above, publication of a tag and
release notes are outside automatic completion.
