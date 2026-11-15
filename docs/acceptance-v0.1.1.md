# v0.1.1 acceptance evidence

Date: 2026-11-15. Platform: Linux x86-64. Implementation and review model:
DeepSeek V4.1 Flash, reasoning HIGH. No OpenAI model was used. No release tag,
push, merge or reference-repository change was made.

This file records the v0.1.1 hardening pass. It is deliberately separate from
[`acceptance-v0.1.md`](acceptance-v0.1.md), whose v0.1.0 results remain
historical. Deterministic, integration and agent-assisted evidence are kept
separate. A live session run by the implementation agent is labelled as such; it
is not independent human acceptance.

## Environment

| Item | Observed |
| --- | --- |
| OS | Linux x86-64 |
| Python | 3.14.4 system; 3.12.13 used by `uv` |
| uv | 0.11.28 |
| Node / npm | v22.20.0 / 11.12.1 |
| Copier | 9.19.1 |
| BMAD | 6.12.4 (`bmad-method@6.12.4`) |
| Agent Skills validator | `skills-ref@0.1.5` |
| pytest | 8.4.2 |
| PyYAML / jsonschema | 6.0.3 / 4.25.1 |

The live runs used disposable projects under `/tmp/opencode/acceptance/`. None
of `Semtexcz/DeepPlant`, `Semtexcz/Bookvoice` or `Semtexcz/PLOS` was read as a
destination or modified.

## Commands and aggregate results

```bash
uv sync --locked
uv lock --check
uv run --locked pytest -m "not integration"
uv run --locked pytest -m integration
```

At the final recorded run:

- `uv lock --check` passed.
- Offline suite: **146 passed, 6 deselected**.
- Integration suite: **6 passed, 146 deselected**.
- Integration coverage includes the pinned BMAD install/reinstall/resolver, the
  native Agent Skills validator, the OpenSpec boundary checks, the deployed
  PEP 723 checker entry point, and the pinned ai-devkit coexistence check.
- The live runs used a locally tagged snapshot of this repository, not a
  published GitHub tag. Tags existed only in `/tmp` fixture repositories.

## Human interventions in the live runs

The assignment required explicit human approval at concrete gates. These are the
actual interventions, not reconstructed approvals:

| # | Gate | Human decision |
| --- | --- | --- |
| 1 | P1 INIT discovery | Product form = **practice only** (no software); actor = **Daniel Kopecký — Product Owner**; approve each gate explicitly. |
| 2 | P1 INIT baseline | Approved the exact VIS-001, REQ-001..004 and DEC-001 digests. |
| 3 | P1 PLAN | Approved MS-001 activation, TASK-001 ready scope, TASK-002..005 as drafts and the roadmap view (DEC-002). |
| 4 | P2 combined INIT+PLAN | Approved the adopted-authority mapping, native strategy/requirements, MS-001 and TASK-001 (DEC-001/002). Gates were combined to bound the secondary run; P1 had already exercised them separately. |
| 5 | P2 adopted-source check | Confirmed Z mandated, N proposed, D design decision, H unvalidated, I2 not active, and the listed content hashes. |
| 6 | P3 promotion | Approved promoting only the TASK-201 slice to native records after pure adoption produced no ready prompt. |

No approval was invented. The checker can bind content, not identity; every
session approval is recorded with actor, ISO date and approval source, and is
still reported as `APPROVAL_IDENTITY_UNVERIFIED`.

## P1 — Live INIT → PLAN → NEXT from a vague vision

Project: `p1-vague` (disposable Git repository). Starting intention:

> We keep losing the reasoning behind our decisions... I want something
> lightweight that helps a team keep a trustworthy decision history... I am not
> sure whether this should be a tool, a practice, or both.

The human chose **practice only**. The project category is `methodology`.

### What was run

1. Copier 9.19.1 copy of `.planner/**` plus `.copier-planner-answers.yml` from a
   local tagged snapshot.
2. Native `bmad-method@6.12.4` install with `--modules bmm --tools opencode` and
   all BMAD output below `planning/runs/bmad/`.
3. Project-authored sparse `_bmad/custom/*.toml` guardrails for the five reused
   planning skills. The native resolver returned the planner facts and the
   inherited `doc_standards`.
4. Native `bmad-product-brief` (headless/fast path), a right-sized `bmad-prd`,
   sequential single-agent PRD validation, and
   `bmad-create-epics-and-stories`.
5. INIT created VIS-001, REQ-001..004, `planning/planner.yaml` and DEC-001 after
   approval. PLAN created MS-001, five tasks, the roadmap view and DEC-002 after
   approval. NEXT selected TASK-001.

BMAD ran with one agent, no research/review subagents, no external publishing and
no execution. The optional reviewer/subagent gates were declined; the PRD review
was a sequential single-agent critique.

### Results

- INIT checker: 0 errors, 6 warnings (missing milestone/task roots and
  not-yet-decomposed requirements), 2 manual-review items.
- PLAN checker: 0 errors, 0 warnings, 3 manual-review items; `ready_tasks =
  ["TASK-001"]`; TASK-002..005 blocked only by `state is 'draft'`.
- TASK-001 scope digest `18da1fec…` matched DEC-002's target exactly.
- NEXT produced a prompt with the full trace
  `VIS-001 -> OBJ-001/OUT-001 -> REQ-001 -> MS-001 -> WP-001 -> TASK-001`,
  source revision, scope digest, normative/background sources, scope bounds,
  criteria, verification, reviewer, stop points and return evidence.
- The prompt was not executed. No task state changed. Two identical checker runs
  selected the same task.

### Evaluation

**Strategy.** The purpose, beneficiaries, choices and exclusions are usable. The
two objectives have explicit unknown baselines rather than invented numbers. The
exclusion of software and of unproven research-quality claims is concrete.

**Requirements.** Four requirements, each with acceptance criteria, verification
method, expected evidence and a reviewer. They trace to objectives, and the
milestone cites all four. No requirement was silently promoted from the BMAD
draft.

**Roadmap.** One active milestone with three exit gates. The next horizon (one
month of sustained use) is recorded at outcome level only, with no fabricated
exit criteria; this is correct rolling-wave behaviour.

**Tasks.** Five bounded tasks. Only TASK-001 is authorized; the rest are drafts
with dependencies 004→001/002/003 and 005→004. Deliverables are documents, not
software artifacts. The task contract includes boundaries, context, criteria,
verification, reviewer, priority and size.

**Prompt.** It is derived, source-bound, and tells the executor to stop on a
normative change and before scope expansion. It does not invent requirements.

### Confirmed defects and fixes

1. **False stale context (Blocking, fixed).** With a commit-based context
   revision at an older commit and `--source-revision HEAD`, the checker emitted
   three `CONTEXT_REVISION_STALE` warnings and excluded TASK-001 from readiness,
   even though the strategy and requirement files were byte-identical between
   the two commits. Reproduced in `context-probe`.
   Fix: optional `context[].sha256`. A matching hash is fresh across newer
   revisions; a changed normative hash is an error; background context no longer
   blocks on revision distance. `freshness-probe`: matching hashes at older
   revisions → TASK-001 ready; one changed strategy byte → exit 1,
   `CONTEXT_CONTENT_CHANGED`, no ready task.
2. **BMAD epics architecture prerequisite (Major, documented workaround).**
   `bmad-create-epics-and-stories` step 1 expects an architecture document (and
   UX when UI exists). A practice product has neither by design. A derived
   `deliverables-and-verification-design` packet was supplied under
   `planning/runs/plan-1/inputs/`, marked non-authoritative. No software
   architecture was invented. The adapter now documents this substitution and
   requires reporting the gap if decomposition cannot proceed.
3. **Sparse-fact ordering (Minor, fixed).** The documented planner fact told BMAD
   to read `planning/planner.yaml` during first INIT, before that file exists.
   The fact now says "when it exists" and points to the discovered authority
   summary instead.
4. **`_bmad/**` ambiguity (Minor, fixed).** INIT prohibited writing `_bmad/**`
   while the adapter expects project-authored `_bmad/custom/**`. INIT now
   distinguishes installed BMAD files from separate operator setup.

### Limitations

- The brief/PRD/epics were produced by the implementation agent in headless/fast
  mode and approved by the human as a baseline. No independent human rubric
  scored elicitation quality.
- PRD validation was sequential and single-agent, not independent reviewer
  subagents (the governance restriction forbids them).
- OUT-002 (one-month sustainability) is not verified; it remains active.
- The prompt was not executed, so it is not evidence of task acceptance.
- The human supplied the product form and approval identity; INIT's discovery
  round was not fully autonomous.

## P2 — Live methodology scenario (PLOS-inspired)

Project: `p2-plos` (disposable, fictional). Charter Z-01/Z-02, proposed N-01/N-02,
design decision D-01, unvalidated H-01, six-concept glossary, iterations I1
complete and I2 proposed, and a prior semantic review with limitations.

### What was run

- Existing authorities were adopted **by reference**; no method content was
  copied into planner entities.
- Native VIS-001, REQ-001 (software/storage/vendor independence) and REQ-002
  (concept trace, citations, status distinction) were approved by DEC-001;
  MS-001 and TASK-001 by DEC-002.
- TASK-001 is a semantic consistency review producing
  `06-reviews/semantic-consistency-review.md`, verified by definition comparison,
  counterexamples and independent document review. No code tests, schema,
  database or UI.
- NEXT required human confirmation of adopted statuses and hashes before it
  emitted a prompt.

### Results and evaluation

- Checker: 0 errors; 7 manual-review items (four unparsed adopted authorities,
  two approval identities, one semantic-review notice).
- After the adopted-context fix, TASK-001 is `review_required` with
  `EXTERNAL_AUTHORITY_UNPARSED`, not deterministically ready. This is the
  intended trust boundary and was previously a false green.
- Requirements traceability holds: every task requirement resolves to an
  approved native requirement; the adopted Z/N/D/H statuses are stated in the
  task and prompt and remain unpromoted.
- I2 remains proposed and is not activated by planning its review.
- The prompt states the source hashes, the status of each adopted item, the
  semantic verification methods, and the stop points (no promotion, no software,
  no glossary rewrite).
- No software artifact appears in the task, milestone, verification or prompt.

### Limitations

- The checker cannot verify that N-01/N-02 remain proposed; that is enforced by
  the task acceptance criteria and human review, not by parsing the adopted
  document.
- Adopted sources require human freshness confirmation before a prompt; this is
  deliberate but costs a manual round.
- The INIT and PLAN gates were combined for this secondary scenario. Recorded as
  an acceptance-process limitation, not a product pass.

## P3 — Existing-project adoption and NEXT reconciliation

Project: `p3-existing` (disposable). Existing TypeScript ledger application with
`docs/VISION.md`, M2/M3 roadmap, two requirements, three task cards and a
`TASK_SEQUENCE.md`, plus `AGENTS.md` and application sentinels.

### Pure adoption (the realistic first step)

- Eight adopted records (strategy, two requirements, milestone, three tasks,
  roadmap) registered by reference with content hashes in DEC-201.
- Checker: 0 errors, 19 manual-review items; **0 native tasks and 0 ready
  prompts**. The original checker did not list adopted tasks in readiness at all,
  so NEXT saw no task set rather than precise blockers. This was a **Blocking
  usability defect** for existing projects.
- Fix: adopted tasks are now listed in `task_readiness` with state `adopted`,
  `ready: false`, `review_required: true` and the
  `EXTERNAL_AUTHORITY_UNPARSED` reason. NEXT can explain a complete blocker set.

### One-slice promotion (the smallest usable correction)

Promoted only `TASK-201` plus the chain it needs: VIS-001, REQ-SYNC-01,
REQ-SYNC-02, MS-201 and TASK-201. Legacy IDs were preserved; the original files
remain normative context with SHA-256 hashes. TASK-202/203 and the roadmap remain
adopted.

- Checker after promotion: `ready_tasks = ["TASK-201"]`,
  `review_required_tasks = ["TASK-202", "TASK-203"]`, 0 errors.
- NEXT produced a source-bound prompt for TASK-201 with the trace
  `VIS-001 -> OBJ-001/OUT-001 -> REQ-SYNC-01 -> MS-201 -> WP-201 -> TASK-201`,
  TypeScript/pnpm constraints, test-based acceptance, a manual restart scenario
  and explicit exclusions.
- Manual cost: five native records, one decision, one config edit, with
  field-by-field mapping from the existing card and requirements. Bounded but
  not trivial. Promoting one task at a time avoids converting the whole backlog.

### Smallest safe improvement adopted

- Adopted tasks are visible to NEXT as `review_required` (checker change).
- `references/migration.md` now documents a one-slice promotion recipe: preserve
  IDs, keep the source as hashed context, remove only the promoted authority
  entries, bind a new decision, and do not rewrite the historical adoption
  decision.
- `planner-next` explains the reconciliation/promotion action instead of
  treating an adopted task as ready.

### Remaining limitations

- `DEC-201` now shows `DECISION_TARGET_DRIFT` for the promoted records. The model
  has no target-level supersession; the warnings are historical and do not block
  TASK-201. This is recorded, not hidden.
- `REQ-SYNC-02` is approved but not decomposed in M2 (`REQUIREMENT_NOT_DECOMPOSED`
  warning); it belongs to M3, which is not active.
- Pure adoption still cannot produce a deterministic ready prompt. A human must
  confirm one task's contract/freshness or approve a one-slice promotion.

## P4 — Safety: install, overlays and approval boundaries

### Unwanted overwrite

Native Copier 9.19.1 behaviour was verified, not assumed:

- Without `--overwrite`/`--force`, Copier refuses a colliding managed file and
  exits non-zero; the existing bytes are preserved.
- A refused copy can still create other files and the answers file before it
  stops. The destination is therefore not guaranteed clean after a failure.
- With `--overwrite`, Copier replaces matching managed files. That flag is
  prohibited for an existing unowned path.

The read-only `scripts/preflight_planner_install.py` now classifies a destination
as `fresh` (exit 0), `existing` planner installation (exit 1, use update), or
`collision` (exit 2: unowned, foreign, partial or symlinked). The first version
misclassified a legitimate local checkout (`_src_path: ../planner-source`) as
foreign; critical review caught it against P3. It now requires the planner marker
files, accepts local/alternate checkouts, and offers `--expected-source` for an
exact check. Regression tests cover both paths. It is not a wrapper and does not
make Copier safe by itself. **A user who ignores it and passes
`--overwrite` can still overwrite an unowned `.planner/`.** Closing that fully
would require Copier `_tasks`/hooks, which the architecture forbids. This is a
**Major residual limitation**, mitigated by the preflight, documentation and a
regression test.

### Independent overlays and update

- The offline lifecycle suite passes: two overlays in either order, separate
  answers files, planner-only updates, conflict markers, rollback and preserved
  project planning content.
- Live: `p2-plos` was updated from overlay v0.1.0 to v0.1.1 with native Copier.
  Only `.planner/**` and `.copier-planner-answers.yml` changed; all
  `planning/**` and adopted domain sources were byte-identical.
- Harness note: the first local tag used a non-PEP-440 suffix (`v0.1.0-local`),
  and Copier update refused it. The disposable source was re-tagged with PEP 440
  tags and the answers `_commit` was corrected in the fixture. Real releases must
  use PEP 440 tags.

### Approval boundaries

- A matching `scope_sha256` proves content identity only. It does not prove who
  approved, that a human approved, or that consent was informed.
- The checker reports `APPROVAL_IDENTITY_UNVERIFIED` for every accepted
  decision. A structurally valid forged `accepted` flag is not authenticated;
  the existing regression test asserts the manual-review finding.
- README, governance and this evidence state explicitly that a digest is not
  cryptographic proof of consent. No such claim is made anywhere.
- Git review, repository access control and human process remain the trust
  boundary.

## P5 — Regression and verification coverage

New offline tests (18 total) cover:

- preflight fresh / existing / unowned / foreign / partial / symlink / read-only;
- native Copier preserving a colliding managed file without `--overwrite`;
- content-hash freshness across an older revision;
- changed normative context hash blocking readiness;
- background context not blocking on revision distance;
- adopted normative context making a task `review_required`;
- pure adoption listing adopted tasks as `review_required`.

The full offline suite is 146 passed. The integration suite is 6 passed. The
native Agent Skills validator accepts all six skills. The BMAD installer,
reinstall and resolver checks pass. No test or live run modified a reference
repository.

## Critical review findings

### Blocking (fixed in this pass)

1. **A task with unchanged normative context was excluded by a false stale
   revision.** Evidence: `context-probe` produced three
   `CONTEXT_REVISION_STALE` warnings and no ready task while
   `git diff 816ae8c -- planning/strategy.md planning/requirements/` was empty.
   Fixed by content hashes; regression tests added.
2. **A task citing an unparsed adopted authority could be deterministically
   ready.** Evidence: P2 before the fix showed `ready_tasks = ["TASK-001"]`
   despite `EXTERNAL_AUTHORITY_UNPARSED` on four adopted sources. Fixed by
   linking normative context paths into task readiness; P2 now shows
   `review_required`.
3. **Adopted tasks were invisible to the readiness view.** Evidence: P3 pure
   adoption showed `records_by_kind.task = 0`, `ready_tasks = []` and no
   per-task blockers for TASK-201..203. Fixed by explicit adopted-task readiness
   entries; regression test added.

### Major (residual, accepted, or fixed during this pass)

1. **Copier can still overwrite an unowned `.planner/` if the operator passes
   `--overwrite`.** The documented path and preflight prevent it; the native
   tool cannot be made to refuse without forbidden hooks. This remains a
   documented limitation against the strongest reading of the v0.1 plan G claim.
2. **Non-software decomposition needs a derived design packet.** BMAD's epics
   workflow expects architecture/UX. The adapter now documents the substitution,
   but the manual step remains for methodology/engineering projects.
3. **Pure adoption cannot produce a deterministic ready prompt.** One-slice
   promotion works and is documented, but the cost is five records per slice.
   This is a deliberate trust boundary, not a silent pass.
4. **Consent cannot be authenticated.** A digest binds content, not a human.
   This is inherent and explicitly documented; real acceptance must rely on Git
   and human review.
5. **Live acceptance was performed by the implementation agent.** The human
   approved concrete gates, but no independent human rubric scored strategy or
   prompt quality. This is agent-assisted acceptance, not independent review.
6. **The first preflight implementation rejected legitimate local checkouts.**
   Evidence: it returned exit 2 for `p3-existing` with
   `_src_path: ../planner-source`. Fixed by requiring planner marker files,
   accepting local/alternate sources, and adding `--expected-source` plus
   regression tests. This was caught by critical review, not by the initial
   tests.

### Minor

1. `DEC-201` shows historical `DECISION_TARGET_DRIFT` after partial promotion;
   target-level supersession is not modeled.
2. The P2 INIT+PLAN gates were combined to bound the secondary run.
3. A non-PEP-440 local tag blocks `copier update`; real release tags must be
   PEP-440.
4. `REQ-SYNC-02` is approved but not decomposed in M2; an expected planning
   warning, not a defect.
5. A context reference that resolves to a directory and carries a `sha256` could
   reach an unguarded read. It now produces `CONTEXT_NOT_FILE`; a regression test
   covers it. No live occurrence was observed.
6. Adding `sha256` to an already approved task changes its `scope` digest and
   therefore requires re-approval. Records created before v0.1.1 should use
   `working-tree` or be re-approved when a content hash is added.

## Unverified capabilities

- No independent human rubric of the live P1/P2/P3 sessions.
- No execution of any derived prompt; no task evidence was produced.
- No one-month sustainability evidence for OUT-002.
- No macOS or Windows verification; Linux x86-64 only.
- No live GitHub Issue/ETag connector; adopted issue sources remain manual.
- No real OpenSpec apply/archive workflow; only the boundary and validation paths
  are covered.
- No cryptographic or identity-provider proof of approval, by design.
- No release tag, push, merge or publication.

## Release readiness

The v0.1.1 candidate is **ready for human product acceptance, with the Major
limitations above explicitly accepted**. The three Blocking defects found by the
live runs are fixed and regression-tested, and the preflight local-checkout
defect found in critical review is fixed and tested. The residual risks are the
`--overwrite` bypass (mitigated by preflight and documentation), the BMAD
non-software design-packet step, the cost of one-slice promotion, and the
inherent inability to authenticate consent.

It is **not** ready for an unconditional release claim: a human must accept the
Major limitations, decide whether the `--overwrite` bypass is acceptable for
v0.1.1, and publish any tag. No tag, push, merge or release was created by this
work.
