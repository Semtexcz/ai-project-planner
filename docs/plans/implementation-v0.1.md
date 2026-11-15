# AI Project Planner v0.1 — implementation plan

Date: 2026-11-15 (Europe/Prague). Repository: `Semtexcz/ai-project-planner`.

This is an architecture and implementation handoff, not an implementation or a release claim. Only this plan was authored during the assignment. No reference repository was changed, no upstream installer was run, and no paid model or implementation agent was invoked. The empty destination repository had no commits at inspection time.

## 1. Product contract and decisions

Build a portable, Git-native **project and product planning overlay**. It turns purpose into approved, verifiable work and feeds evidence back into strategy. It must be useful for software, engineering research/specification, and methodology development. It must remain useful when execution happens manually, in an unrelated agent, or outside software entirely.

The forward chain is:

```text
Vision and strategic choices
  -> objectives and expected outcomes
  -> requirements
  -> outcome-based milestones
  -> optional work packages/slices
  -> approved tasks
  -> derived execution prompts
  -> deliverables and verification evidence
```

Evidence, failed verification, changed assumptions, and new ideas flow back through CHANGE and PLAN. AUDIT tests both directions of traceability. A task count never proves an outcome.

Decisions made for v0.1:

1. Reuse BMAD **6.12.4**, from the stable v6.12 line, through its official npm installer. Do not follow the v7 preview or install `@latest` implicitly. Use native configuration and sparse customization, never edit installed BMAD skills.
2. Use Copier **9.19.1** as the initial compatibility baseline, matching the inspected ai-devkit. Each overlay keeps its own provenance. Planner uses **`.copier-planner-answers.yml`**.
3. Copier renders only `.planner/**` and that answers file. INIT, rather than Copier, creates project-owned records in `planning/`. Updates therefore cannot render, delete, recreate, or merge vision, requirements, roadmap, decisions, or tasks.
4. Provide exactly six portable Agent Skills: `planner-init`, `planner-status`, `planner-plan`, `planner-next`, `planner-change`, `planner-audit`. No planning service, command router, autonomous loop, or execution launcher.
5. Keep skills at `.planner/skills/`. Explicit file invocation is the portable baseline. Optional discovery links are a separate, project-owned convenience, never an excuse to overwrite `.agents/`, `.opencode/`, or `AGENTS.md`.
6. Preserve established authorities through a small project-owned authority map. Native records are the default for new projects, not a mandatory conversion of all existing projects.
7. Use a small read-only structural checker. It validates records and references; the agent performs planning judgment through BMAD. It does not choose work, mutate states, run verification commands, contact models, or interpret arbitrary project formats.
8. OpenSpec is optional. Where already authoritative, it retains detailed behavioral requirements and its change checklists. Planner adds strategic context and references, not competing copies.
9. Approval is an explicit human action with a content-bound record. Agent-generated `final`, Git commits, merged implementation, or checked boxes are not automatically Product Owner approval.
10. Initial verified installation platform: Linux x86-64. Use portable paths and Markdown; do not claim verified macOS/Windows behavior until exercised there. Core reading and explicit skill invocation are independent of an IDE.

Excluded from v0.1: autonomous execution, multi-agent orchestration, scheduling, databases, web dashboards, custom LLM clients, model routing, generic workflow engines, PM servers, and replacements for BMAD/OpenSpec. No app scaffolding or programming-language requirement is imposed on target projects.

### Model and cost policy

This planning assignment uses GPT-6.1 Sol, HIGH, only for architecture/planning. **All implementation tasks below belong to DeepSeek V4.1 Flash, HIGH.** DeepSeek V4 Pro, HIGH, is an escalation for a concrete unresolved failure or architectural ambiguity after two bounded Flash attempts; carry forward the failing evidence and return to Flash afterward. Do not silently substitute any OpenAI implementation model.

Model recommendations in generated prompts are advisory labels. Map them to actual provider/harness IDs in the user's native configuration. The inspected devkit example says `deepseek/deepseek-flash`; that does not establish the provider ID for every model named in this assignment. Do not invent IDs or add an LLM client to resolve them. If the requested model/effort is unavailable, stop the affected model run and report it. Local edits and deterministic checks do not require model calls. CI must never require credentials or make paid inference calls.

## 2. Inspection evidence and upstream responsibilities

### 2.1 Sources inspected

Local reference checkouts were clean when inspected. These are observed snapshots, not a claim that every remote default branch has the same head:

| Repository | Inspected local commit | Relevant findings |
| --- | --- | --- |
| ai-devkit | `cc04bcef80b3838cd5956a872717b65949190468` | `_subdirectory` limits template output; `.copier-answers.yml` tracks lineage; no Copier tasks; native OpenSpec owns its generated integration; update tests use temporary tagged repos, content hashes, conflict evidence, and an unrelated-file allowlist. |
| Bookvoice | `6454ca7917bd55435d3f6cec7c980a3393e11add` | `project/` task cards, folder states, duplicate body/frontmatter metadata, backlog dependency index, and `docs/TASK_SEQUENCE.md` all carry information. A backlog folder does not necessarily mean ready. |
| DeepPlant | `540f2060b36cfa5a17c006596b722ccc1fa4b17b` | `VISION.md`, strategy, product definition, roadmap, current contracts, ADRs, historical gates, and bounded GitHub Issues have separate authority. Directional capabilities are not authorization. |
| PLOS | `3d08fb1e50bf6f0a1d4e282ae0bbf1d2b6e4c81b` | Charter, requirements, domain/glossary, decisions, iteration roadmap and semantic reviews are distinct. Z is explicitly mandated, N proposed, D a design decision, H a hypothesis. The methodology does not presume software. |

Relevant ai-devkit source: [Copier configuration](https://github.com/Semtexcz/ai-devkit/blob/main/copier.yml), [agent rules](https://github.com/Semtexcz/ai-devkit/blob/main/AGENTS.md), [ownership](https://github.com/Semtexcz/ai-devkit/blob/main/docs/explanation/generated-project-ownership.md), [update procedure](https://github.com/Semtexcz/ai-devkit/blob/main/docs/how-to/update-project-overlay.md), [lifecycle tests](https://github.com/Semtexcz/ai-devkit/blob/main/tests/test_update_lifecycle.py). The remote `copier.yml` was also read and matched the inspected convention. Some devkit documentation contains older release-status wording; use actual files, pinned versions, and test results rather than treating every narrative status claim as current.

Reference authority sources: [Bookvoice task sequence](https://github.com/Semtexcz/Bookvoice/blob/6454ca7917bd55435d3f6cec7c980a3393e11add/docs/TASK_SEQUENCE.md), [Bookvoice task convention](https://github.com/Semtexcz/Bookvoice/blob/6454ca7917bd55435d3f6cec7c980a3393e11add/project/README.md), [DeepPlant governance](https://github.com/Semtexcz/DeepPlant/blob/540f2060b36cfa5a17c006596b722ccc1fa4b17b/docs/dev/planning/index.md), [DeepPlant strategy](https://github.com/Semtexcz/DeepPlant/blob/540f2060b36cfa5a17c006596b722ccc1fa4b17b/docs/dev/planning/strategy.md), [PLOS authority conventions](https://github.com/Semtexcz/PLOS/blob/3d08fb1e50bf6f0a1d4e282ae0bbf1d2b6e4c81b/README.md), [PLOS requirements](https://github.com/Semtexcz/PLOS/blob/3d08fb1e50bf6f0a1d4e282ae0bbf1d2b6e4c81b/02-requirements/high-level-requirements.md).

The reusable-tool catalog at `/mnt/Data/automation/agent-tools/README.md` contains only a mail tool relevant to a different purpose. It supplies no planner implementation to reuse. No mailbox was read. Recheck that catalog before adding a similar reusable script during implementation; the catalog grants no file or network permissions.

### 2.2 Evaluated tools

| Component | Verified capability and responsibility | Boundary / decision |
| --- | --- | --- |
| BMAD v6.12.4 | Product brief and PRD create/update/validate; requirements-to-epics/stories; readiness-only gate; course-correction proposal; native config and customization resolvers. | Owns elicitation, specification development, decomposition and its installed files. Planner adds authority, approval, outcome and traceability policy. Never call build, build-auto, dev-story, party-mode or autonomous flows from planner operations. |
| Copier 9.19.1 baseline | Custom answers file, constrained template subdirectory, tagged copy/update, native conflict handling and multiple templates. | Owns overlay lineage and managed-file updates. No custom updater, hooks, Copier migrations that execute commands, or install-time shell automation. |
| Agent Skills format | A named directory with `SKILL.md` frontmatter and optional references/assets/scripts. | Owns the portable packaging contract. Discovery/invocation syntax is harness-specific; explicit path activation always remains documented. |
| Git + Markdown + YAML frontmatter | Reviewable history, diffs, branches, immutable revisions, readable records. | Own project truth. Git is not an approval identity service. No database/index daemon. |
| OpenSpec | Native specification/change lifecycle, generated skills, validation, update. Current upstream v2 uses different skill names from the devkit's pinned v1.16. | Optional detailed-spec authority. Reuse the installed compatible version; do not upgrade an application's OpenSpec as a side effect of installing planner. Use native validation, not a custom OpenSpec parser. |
| uv + pytest + JSON Schema/PyYAML | Reproducible checker/test dependencies and maintained structural validation. | Tooling for this repository and an isolated checker invocation; no dependencies inserted into target application manifests. |

Primary upstream references, inspected 2026-11-15:

- [BMAD v6.12 releases](https://github.com/bmad-code-org/BMAD-METHOD/releases), [pinned installation guide](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.12.4/docs/start/install-bmad.md), [native customization and merge rules](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.12.4/docs/customize/customize-bmad.md).
- Pinned skills: [product brief](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.12.4/src/bmm-skills/plan/bmad-product-brief/SKILL.md), [PRD](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.12.4/src/bmm-skills/plan/bmad-prd/SKILL.md), [epics/stories](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.12.4/src/bmm-skills/plan/bmad-create-epics-and-stories/SKILL.md), [readiness and status](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.12.4/src/bmm-skills/plan/bmad-sprint-planning/SKILL.md), [course correction](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.12.4/src/bmm-skills/ship/bmad-correct-course/SKILL.md), [planning guide](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.12.4/docs/plan/break-work-into-stories-and-track-it.md).
- [BMAD module configuration keys](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.12.4/src/bmm-skills/module.yaml), [brief customization surface](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.12.4/src/bmm-skills/plan/bmad-product-brief/customize.toml), [PRD customization surface](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.12.4/src/bmm-skills/plan/bmad-prd/customize.toml).
- [Copier configuration and multiple-template guidance](https://copier.readthedocs.io/en/stable/configuring/), [native update behavior](https://copier.readthedocs.io/en/stable/updating/).
- [Agent Skills specification](https://agentskills.io/specification), including `skills-ref validate` as the native format validation route.
- [OpenSpec v2 release changes](https://github.com/Fission-AI/OpenSpec/releases), [v2 README](https://github.com/Fission-AI/OpenSpec/blob/v2.0.0/README.md), [OpenSpec integration in ai-devkit](https://github.com/Semtexcz/ai-devkit/blob/main/docs/explanation/openspec-and-agents.md).

### 2.3 Important capability limits

BMAD is explicitly oriented toward software development. Its brief and PRD support domain-sensitive templates, but cross-domain fitness is an architectural inference that must pass the PLOS and engineering fixtures. Translate story/epic vocabulary to deliverable/slice in invocation context; do not invent APIs or code where the deliverable is a methodology or specification.

BMAD 6.12 is different from older v6 tutorials: use `bmad-prd` and `bmad-product-brief`, and `bmad-sprint-planning` with **readiness-only** intent. Do not depend on opt-in legacy shims. Native sprint tracking already exists; v0.1 does not generate a second `sprint-status.yaml` beside canonical task records. Existing BMAD tracking may remain its project's task authority when adopted.

Customization arrays append; `[]` does not erase inherited entries. There is no general removal operation. Several upstream skills suggest or request research/review subagents, external handoffs, or follow-on skills. V0.1 invocations explicitly require one agent, no paid delegated calls, no external publishing, no execution, and stop after the requested planning result. Add these restrictions through supported persistent facts/hooks and the invocation, not nonexistent disable flags. Run native sequential fallbacks where available. If the pinned workflow cannot obey these restrictions, record a compatibility failure; do not fork it or silently build an alternative planner.

Reading source and documentation established the above surfaces. Installation, merged override behavior, tool discovery, non-software output quality and upgrade preservation remain acceptance gates, not checks already passed.

## 3. Architecture and ownership

```text
Human Product Owner
    | intent, approval, rejection, acceptance
    v
Six planner Agent Skills ---------------> BMAD planning skills (native)
    | policy/context + proposed writes         | draft artifacts
    v                                         v
Project-owned planning/ and adopted existing authorities
    | references, content revisions, evidence
    +--> read-only structural checker
    +--> derived status/audit reports and execution prompts

Copier -> .planner/ + .copier-planner-answers.yml ONLY
BMAD installer -> native BMAD installation ONLY
OpenSpec CLI -> native OpenSpec installation/spec workflow ONLY
Execution -> outside this system; human later brings evidence back
```

There is no background process. An operation is one explicit skill invocation in an agent with repository access. It reads project policy first, resolves authorities, delegates planning technique to BMAD as appropriate, and produces a bounded result. Saved reports and prompts are views of a stated source revision.

### Ownership matrix in target projects

| Paths / concern | Authoritative owner | Creation and updates |
| --- | --- | --- |
| `.planner/**` | Planner overlay | Copier only; contains reusable policy, skills, schemas, checker and blank assets, never project truth. |
| `.copier-planner-answers.yml` | Copier planner lineage | Native Copier only; commit it; never hand-edit. |
| `planning/planner.yaml` | Project Product Owner | INIT creates from blank asset; records local authority and policy. Copier never renders it. |
| `planning/strategy.md`, requirements, milestones, tasks, records | Project's designated owners | INIT/PLAN/CHANGE proposals and human approval; subsequent task evidence updates within authorization. |
| `planning/runs/**`, `planning/prompts/**` | Project, derived artifacts | Explicit operations may create them; never treated as active requirements. |
| Existing vision/roadmap/ADRs/tasks | Existing project owners | Adopt by reference; no write until a specific approved change or migration. |
| `_bmad/**` and installed `bmad-*` skills | BMAD native installer | Separate install/update transaction. Project-authored `_bmad/custom/**` stays project-owned. |
| `openspec/**`, generated OpenSpec skills | OpenSpec / existing project specification authority | Native CLI and workflow; no template rendering or invented parser. |
| `.copier-answers.yml`, devkit template paths | ai-devkit + its native tools | Planner never writes them. |
| `AGENTS.md`, README, app manifests, CI, mise/toolchain config | Existing project/other overlay | Never rendered, patched or automatically extended by planner. |

Future capability overlays get their own namespaces and answers files. Sharing a parent directory does not authorize replacing another capability's leaf files. Planner avoids even that issue by keeping its managed content under `.planner/`.

### Authority resolution

`planning/planner.yaml` contains `schema_version: 1`, a stable `project_id`, category (`software`, `engineering`, `methodology`), named Product Owner/reviewer roles, content root, authority bindings, current milestone reference, explicit task order or ordering policy, verification profile references, and review policy. It contains no copies of requirement text, task state, estimates, or roadmap outcomes.

For a new project, bindings point to the native locations below. For an adopted project, bindings can point to existing files/sections, OpenSpec requirement sections/checklist items, or GitHub Issues with a captured content identity and source timestamp. Issue URLs are mutable; a dated export plus content hash preserves what was reviewed, while a fresh read establishes whether that approval still applies. Native inventories are discovered only inside configured roots. Explicit bindings identify external records by ID, owner, path/URI and locator; aliases retain legacy IDs. Resolve every ID to exactly one owner and one authoritative location. Duplicate mappings are errors, never last-writer-wins. Do not implement a rule language, precedence cascade or automatic source ranking.

For example, an adopted Bookvoice task remains `TASK-075` at its current task card; `docs/TASK_SEQUENCE.md` remains the adopted order/dependency authority until a human approves consolidation. If a card and sequence disagree, report both and block that task. DeepPlant Issues may remain scope authorities while repository documents remain strategy authorities. External tracker writes are out of v0.1's baseline; propose a patch/prompt for the human's existing workflow.

For OpenSpec projects, link to canonical requirement sections and existing checklist items. An incomplete checklist item may be refined **in that same authoritative item** into the task contract through the native agent workflow, or remain unready. Do not create a native task card with a second state or duplicate scope. Add stable inline task identifiers only as an approved project edit. Native OpenSpec `tasks.md` checkboxes retain their meaning; planner readiness is a derived assessment, not a second checkbox list. No automatic two-way sync.

External/adopted Markdown can be understood by the agent without a custom adapter. The deterministic checker checks local existence and explicitly supported references, and reports semantic/unparsed portions as `manual_review_required`. For a GitHub Issue, use the host's existing connector/CLI only if available and authorized; record revision/ETag or export provenance. An inaccessible or changed external source cannot silently pass readiness. Offline reading is possible from a dated snapshot; executing NEXT requires source freshness confirmation. No custom GitHub client is planned.

## 4. Minimal canonical information model

The model is tool-independent. Markdown files below are the default serialization, not new mandatory domain objects. One owner means one authoritative location per concept plus an accountable human role; views and links do not become owners.

| Concept | Semantics, IDs and relationships | Owner / minimal lifecycle |
| --- | --- | --- |
| Vision and strategy | `VIS-001` in `strategy.md`: purpose, intended beneficiaries, problem, choices, exclusions and assumptions. Contains strategic objectives. | Product Owner; proposed -> approved -> superseded. Changes remain legitimate through a new decision, never silent replacement. |
| Objective and expected outcome | `OBJ-001` and nested `OUT-001`: objective explains a strategic choice; outcome describes observable benefit with baseline/target or qualitative rubric, evidence expectation and review horizon. No separate outcome ledger. | Product Owner in strategy; proposed/active/achieved/retired. Achievement needs outcome evidence; unknown baseline is explicit. |
| Requirement | `REQ-001`, classification functional/quality/constraint; an obligation with source and verification criterion, linked to >=1 objective. Links to existing authoritative architecture constraints are valid requirements context. | Product Owner approves obligation; named domain reviewer verifies; proposed/approved/retired, with replacement references. Satisfaction is derived from current evidence. |
| Milestone | `MS-001`: an outcome and demonstrable exit criteria, objective/outcome refs, requirement coverage and genuine dependencies. | Product Owner; proposed/approved/active/achieved/retired. At most one active in v0.1. Achievement requires reviewed milestone evidence. |
| Work package / slice | Optional `WP-001`, embedded in its milestone: a coherent bounded deliverable connecting tasks to milestone outcome. Not a team, sprint, release or extra management hierarchy. | Milestone owner; inherits milestone approval; no separate state machine. Tasks may omit it for a small milestone. |
| Task | `TASK-001`: smallest useful deliverable/review unit, exactly one parent milestone, optional package, >=1 relevant requirement, scope contract, dependencies and evidence expectation. | Accountable task owner; draft -> ready -> in_progress -> review -> done; blocked/cancelled branches with reasons. Ready requires approved scope and satisfied gates. |
| Dependency | Directed `depends_on` reference meaning prerequisite before starting; `context` and `related` mean something else. Task refs, milestone refs, or an explicit external gate with criterion/evidence. | Stored on dependent record; no dependency entity or tracker. Cycles/dangling links invalidate readiness. |
| Decision and approval | `DEC-001`: rationale, options, actor, authority, dated decision, sources, affected records, approved content revisions and any superseded decision. Existing ADRs remain authoritative rationale. | Product Owner for consequence; delegated domain reviewer within named limits. Proposed/accepted/rejected/superseded. Agent can author proposed records, never impersonate an approver. |
| Idea / proposed change | `CHG-001` using the same record structure as decisions with `kind: change`: idea, source, affected chain, alternatives, impact and proposed delta. Does not authorize work. | Product Owner disposition; captured -> assessed -> approved/rejected/deferred -> applied. Rejection/defer retains rationale and revisit trigger. |
| Verification evidence | Embedded `evidence` entries on task/milestone/outcome, or links to a substantive report: unique local label such as `TASK-001:EV-1`, method, criterion refs, subject revision, result, artifact path/URI, reviewer and limitations. | Evidence producer reports; designated reviewer accepts. Results pass/fail/inconclusive; superseded evidence retained. No separate evidence database. |

Assumptions, risks, blockers and open questions are fields/sections on their affected records. Do not add risk, sprint, release, ticket, backlog item, capability, approval-request or agent-run entities for v0.1. Roadmap is an ordered **view** of milestones, not another source of milestone scope. An enabling/research task still needs an explicit approved requirement/objective for its contribution; do not fabricate an alignment link to excuse unrelated work.

### 4.1 Native serialization contract

Native files use YAML frontmatter with `schema_version`, `kind`, `id`, `owner`, `scope`, and `execution`. All normative content goes in `scope`; `execution` contains state, blockers, evidence and progress notes. Markdown body explains context and history and cannot add permission or acceptance criteria absent from scope. If prose contradicts scope, AUDIT reports it; no automated rewriting.

`scope` holds the fields appropriate to each kind: strategic claims/objectives, requirement obligation, milestone outcome/exit criteria, task contract, or decision/change proposal. Stable local identifiers are never reused or renumbered. Criteria use local IDs such as `TASK-001:AC-1`; outcome/evidence references use the same URI-like local-reference convention. Arrays have a deliberate order. Use strings for dates, versions and measured targets. Preserve unknown values explicitly; a ready record cannot contain unknown mandatory fields.

Default identifiers above are conventions for new projects. Migration retains legacy IDs (`FR-01`, `CON-01`, `ADR-07`, etc.) with unique project-local bindings; add a disambiguating alias only on actual collision, preserving both original identities and provenance. IDs are unique within a project, not across the world.

Use JSON Schema Draft 2020-12 with discriminated record definitions and maintained YAML parsing. Reject duplicate YAML keys and malformed documents. Native required fields and enums are strict; support an `extensions` map instead of inventing dozens of optional fields. The checker never parses an arbitrary code expression or executes a value.

Use these concrete native field groupings when implementing I03; optional fields must not conceal missing readiness information:

| Record | Normative `scope` fields | Operational `execution` fields |
| --- | --- | --- |
| strategy | `purpose`, `beneficiaries`, `problem`, `choices`, `exclusions`, `assumptions`, `objectives[]` with `id`, `statement`, `outcomes[]` containing `id`, `description`, `baseline`, `target_or_rubric`, `verification`, `review_horizon` | `state`, `items` keyed by embedded OBJ/OUT ID for state/evidence, `approvals`, `progress_notes` |
| requirement | `statement`, `classification`, `objectives[]`, `sources[]`, `acceptance[]`, `verification[]`, `supersedes[]` | `state`, `approvals`, `evidence`, `blockers`, `progress_notes` |
| milestone | `outcome`, `objectives[]`, `outcomes[]`, `requirements[]`, `depends_on[]`, `exit_criteria[]`, `verification[]`, `packages[]` with `id`, `outcome`, `include[]`, `exclude[]` | `state`, `approvals`, `evidence`, `blockers`, `progress_notes` |
| task | `title`, `objective`, `rationale`, `milestone`, optional `package`, `requirements[]`, `include[]`, `exclude[]`, `depends_on[]`, `context[]`, `deliverables[]`, `acceptance[]`, `verification[]`, `approvals[]`, `priority`, `size` | `state`, `authorization[]` referencing decisions, `evidence`, `blockers`, `progress_notes` |
| decision | `topic`, `rationale`, `options[]`, `choice`, `targets[]`, `authority`, optional bounded `delegation`, `supersedes[]` | `state`, `actor`, `decided_at`, `approval_source`, `applied_revision` where relevant |
| change | `idea`, `source`, `affected[]`, `impact`, `alternatives[]`, `proposed_delta`, `required_approvals[]`, optional `revisit_trigger` | `state`, `disposition_decision`, `applied_revision`, `blockers`, `progress_notes` |

Each criterion is `{id, statement}`. Each verification entry is `{criteria: [IDs], method, expected_evidence, reviewer}`. Each evidence entry is `{id, criteria: [IDs], method, subject_revision, result, artifact, reviewer, limitations}` with a recorded observation/review date. A dependency is either an ID ref or `{gate, criterion, evidence_ref}` for a non-record prerequisite. A context entry identifies `{ref, authority, revision, purpose, normative}`. Fields in these examples denote data shapes, not executable expressions.

Project configuration uses `authorities` entries with `{kind, owner, root}` for a native collection or `{kind, id, owner, ref, locator, format}` for an explicit adopted record; optional `aliases` preserve collisions/legacy names. Formats are `native`, `markdown`, `openspec`, or `issue`. It also has `roles`, `verification_profiles`, `task_order` or the default ordering policy, and `review_policy`. `current_milestone` is an index reference and must agree with the authoritative active milestone selection; it never independently authorizes activation. Do not mirror external task states or dependency lists into this configuration. If relationships are distributed across existing authorities, reference each relationship owner and reconcile conflicts rather than copying a resolved guess.

### 4.2 Content-bound approvals

For native records, approval targets contain record ID and `scope_sha256`. Compute it from the UTF-8 JSON serialization of `scope`, sorted object keys, compact separators, no ASCII escaping. Restrict scope to JSON-compatible types; Unicode and line endings must have defined test vectors. The identical routine is used for checking and examples. This is a small content identity check, not authentication infrastructure.

An accepted DEC records the human actor, timestamp, original approval source (for example a reviewed PR URL or explicit session instruction with retained reference), affected scopes/digests and delegation limits. Prepare the exact proposed records first, then obtain approval for that concrete set. Recording a user's already explicit approval is allowed; inventing it is not. Do not ask again if the same approved content and authority still apply.

Changing task progress/evidence does not change `scope`. Changing a normative field does and invalidates the existing approval until approved through CHANGE/PLAN. References to an approval use the DEC ID, not a digest cycle. Decision acceptance and actor/source are checked against the recorded human decision; a schema-valid agent-written `accepted` is not proof of human consent. Git review/permissions and human review supply that trust boundary.

For adopted records, bind approval to the existing immutable revision plus exact section/item locator and content identity where available. If only a mutable URL or ambiguous section is available, require human/source review and report the limit. Do not pretend a native scope digest validates an unparsed external document. Existing explicit mandates can be adopted with their original approval provenance; do not relabel an entire historical design as approved.

No decision needs recursive self-approval: its accepted state records the human decision and original source. A task is authorized either by approval of its exact scope digest or by an already approved **explicit bounded delegation** covering that decomposition. Delegation identifies allowed objectives/requirements/milestone, exclusions, permitted decisions and stop conditions; the agent records its conformance rationale and the authorizing DEC. Scope/strategy expansion cannot be delegated implicitly by a roadmap label. The checker verifies links and content bindings; conformance to a prose delegation requires review and cannot be advertised as a proved machine authorization. Reviewer acceptance of task evidence is distinct from authorization of its scope.

### 4.3 Rolling-wave detail

| Horizon | Required detail |
| --- | --- |
| Current active milestone | Outcome, exit criteria, requirements, constraints, dependencies, packages where useful, bounded ready tasks, verification/reviewer and open risks. Detail only enough work to make progress; do not pre-decompose all unknowns. |
| Next milestone | Outcome, candidate packages, major dependencies, evidence gaps and likely decisions. Tasks may remain drafts. |
| Distant milestones | Outcomes, strategic rationale, dependencies and uncertainty only. No mandatory task cards, dates or speculative architecture. |

Inspection of all completed tasks can support an outcome claim; it cannot replace the milestone demonstration or the strategic-outcome review. Completed work can reveal that the milestone no longer matters, requiring CHANGE rather than more tasks.

## 5. Repository and installed structures

The following is the intended source layout. Create files incrementally with their owning implementation tasks, not an empty framework scaffold in advance.

```text
ai-project-planner/
  README.md
  LICENSE                         MIT for new original material; retain upstream notices
  CHANGELOG.md
  AGENTS.md                       instructions for developing this repo, never rendered
  copier.yml
  pyproject.toml                  development tools only; not an application package
  uv.lock                         generated by uv
  docs/
    plans/implementation-v0.1.md   this handoff; historical after implementation
    architecture.md               concise maintained decisions and boundaries
    information-model.md
    operations.md
    install-update.md
    migration.md
    verification.md
    upstream-compatibility.md     pinned versions, help/installer and smoke evidence
    acceptance-v0.1.md            actual results and limitations, no invented pass claims
  templates/planner-overlay/template/
    {{ _copier_conf.answers_file }}.jinja
    .planner/
      README.md                   explicit invocation and ownership entry point
      references/
        governance.md
        information-model.md
        operation-contracts.md
        bmad-adapter.md
        migration.md
        verification-profiles.md
      schemas/
        project.schema.json
        record.schema.json
      scripts/
        check_planning.py         bounded read-only structural checks
      assets/
        project-config.yaml       blank project-owned configuration seed
        strategy.md
        requirement.md
        milestone.md
        task.md
        decision.md
        change.md
        prompt.md
        migration-report.md
        audit-report.md
      skills/
        planner-init/SKILL.md
        planner-status/SKILL.md
        planner-plan/SKILL.md
        planner-next/SKILL.md
        planner-change/SKILL.md
        planner-audit/SKILL.md
  tests/
    conftest.py
    test_template.py
    test_native_records.py
    test_references.py
    test_approvals.py
    test_workflow_contracts.py
    test_migration_fixtures.py
    test_overlay_lifecycle.py
    test_bmad_install.py
    test_openspec_boundary.py
    fixtures/
      empty/
      bookvoice-like/
      deepplant-like/
      plos-like/
      change/
      drift/
      overlays/                   small independent overlay with separate answers
  .github/workflows/verify.yml
```

Installed new-project content, created by INIT from assets after reviewing intent:

```text
project/
  .copier-planner-answers.yml      Copier-owned
  .planner/                      Copier-owned reusable capability
  planning/                      entirely PROJECT-owned
    planner.yaml                 authorities, roles, policy and current milestone pointer
    strategy.md                  VIS + embedded OBJ/OUT records
    requirements/REQ-001.md
    roadmap.md                   linked ordered milestone view; no copied exit criteria
    milestones/MS-001.md          optional embedded WP records
    tasks/TASK-001.md
    records/DEC-001.md
    records/CHG-001.md
    evidence/                    substantive review/demonstration reports if needed
    runs/<run-id>/               BMAD drafts, input manifests, migration/audit reports
    prompts/TASK-001-<scope-digest-prefix>.md
  _bmad/                         optional until first BMAD-backed operation; installed natively
```

There is no source-code package or web app. Avoid duplicate maintained copies of planner reference prose: the reference documents under the template are the normative runtime contracts; repository docs explain them and link to them. Schemas express syntax, not a second planning method.

Skills reference their sibling shared resources using documented relative file paths. Validate these paths after rendering; no absolute workstation path is shipped. Host-specific optional discovery links must preserve these paths (resolve links to the canonical skill directory). A host that cannot follow such links uses explicit path invocation.

## 6. Installation, coexistence, upgrades and rollback

### 6.1 Planner overlay

`copier.yml` must set `_subdirectory: templates/planner-overlay/template`, `_answers_file: .copier-planner-answers.yml`, and the tested minimum Copier version. Use the literal dynamic answers template filename shown in the tree and serialize `_copier_answers` through Copier's native YAML filter. Only necessary questions belong here, such as project display name; project strategy and local planning decisions are not Copier answers. Do not store secrets, account model IDs or changing project content there.

Do not add `_tasks`, executable `_migrations`, unsafe extensions, an install script, or an auto-update wrapper. No application file is rendered. A maintained version should not acquire new output paths outside the allowlist without a deliberate compatibility decision.

Document this sequence, using a tagged planner release after a human publishes one:

```bash
# Review the template source and the destination tree first.
uvx copier==9.19.1 copy --pretend --answers-file .copier-planner-answers.yml \
  --vcs-ref v0.1.0 gh:Semtexcz/ai-project-planner "<project>"
uvx copier==9.19.1 copy --answers-file .copier-planner-answers.yml \
  --vcs-ref v0.1.0 gh:Semtexcz/ai-project-planner "<project>"
```

The `uvx` package/version syntax and exact flags must be replayed in task I01 against the pinned CLI. `--pretend` previews native actions, not a security boundary or a substitute for collision inspection. Never use force/overwrite on a pre-existing `.planner/` or planner answers file of unknown origin. If any intended managed path already has another owner, stop before copying and report the conflict. Do not infer ownership from a matching filename alone.

A new empty target can receive a copy before its first commit. Initialize Git and commit the reviewed overlay before attempting upgrades. Existing targets require a clean committed tree for installation/update; read-only discovery/reporting remains possible on a dirty tree, but report it and do not mutate it.

Baseline activation, independent of harness discovery:

> Read `.planner/skills/planner-init/SKILL.md` and carry out INIT for this project. Follow the existing project instructions and retain all existing content authorities.

For the other operations substitute the corresponding skill path. Optional native discovery: a human may configure a supported harness's additional skill directory, or create six project-owned links in a supported directory if it has no ownership conflict. Document only paths verified for the selected harness; do not edit root `AGENTS.md`, shared config, or global agent settings. Updates do not recreate or retarget project-owned links. Explicit invocation is fully supported without them.

### 6.2 Native BMAD setup

When a BMAD-backed operation is first needed, inspect any existing installation and its version. Reuse a compatible installation; do not copy another project's `_bmad/`. For a new installation use:

```bash
npx --yes bmad-method@6.12.4 install --help
npx --yes bmad-method@6.12.4 install --list-tools
npx --yes bmad-method@6.12.4 install
```

The first two commands inspect the exact pinned installer. The last command is the documented interactive installation; select BMM and the actual supported harness, not Automator or preview modules. The installed inventory may include execution skills; their presence does not authorize planner to invoke them. For isolated CI installation tests use the documented `--yes --modules bmm --tools <verified-tool-id>` flags, exact destination flag confirmed by help, and a disposable destination/HOME. Do not assume a guessed tool ID.

Use native settings `[modules.bmm]` for `planning_artifacts`, `implementation_artifacts`, and `project_knowledge`; configure BMAD output below `planning/runs/bmad/`. Native output is draft or derived unless explicitly adopted. A project may retain its already configured BMAD paths; register them rather than overwrite its configuration.

Project-authored sparse overrides under `_bmad/custom/` may add planner facts and hooks to brief, PRD, epics/stories, readiness and correct-course skills. They load `.planner/references/governance.md` and `planning/planner.yaml`, require declared authority, forbid automatic approval/execution/publishing, and constrain domain vocabulary. Use native scalar output-path overrides only where the pinned `customize.toml` exposes them. Verify merged results with the native resolver. Never hand-edit `_bmad/config.toml`, copy a whole customization template, or assume empty arrays suppress defaults. Existing customization is read first; append a reviewed minimal project-owned patch, never replace it wholesale.

The invoking agent may create a **derived input packet** under a run directory when BMAD expects a PRD/epic shape the project does not maintain. It contains faithful requirement/constraint excerpts, stable IDs, source locations, revisions and an explicit non-authoritative notice. This is document preparation, not a new parser or spec engine. BMAD outputs stay in that run directory until review. Missing requirements remain questions rather than fabricated input.

Existing source authorities are not replaced by BMAD `status: final`. Approve either a deliberate adoption of the native BMAD artifact as the owner, or proposed edits to the existing authority; never retain two active texts claiming the same scope. Upon promotion, mark the draft/run result as historical with links to the actual owners. BMAD's memlogs/addenda remain its workshop provenance; planner DEC records own consequential authorization and link to that provenance rather than duplicate every coaching exchange.

BMAD installer changes are a separate reviewed transaction from a Copier update. Test that reinstallation preserves project customizations and canonical planning bytes. If a required BMAD workflow is missing/incompatible, INIT discovery, STATUS, NEXT for already sufficient tasks, and structural AUDIT can still work; BMAD-dependent PLAN/CHANGE drafting must report the missing dependency, never substitute a custom planning workflow.

### 6.3 OpenSpec coexistence

Do not initialize or update OpenSpec automatically. If the project already uses it, inspect its installed version and invoke its native help/validation. The inspected devkit pins 1.16.0; current upstream v2 renames workflow skills and changes generated files. Support both through a small documented version-to-native-invocation table, proven against fixtures. No new generalized adapter interface.

If a user chooses to enable OpenSpec for a new project, perform its official installation and `openspec init` as a separately reviewed project setup step using the chosen supported tools. Preserve its existing configuration and source authority. The planner stops before any OpenSpec apply/execute workflow. OpenSpec validate proves format/consistency within its scope, not strategic approval or milestone achievement.

### 6.4 Independent updates

Run from the target repository with a clean committed tree and reviewed tag:

```bash
uvx copier==9.19.1 update --answers-file .copier-planner-answers.yml \
  --vcs-ref <planner-tag> --pretend .
uvx copier==9.19.1 update --answers-file .copier-planner-answers.yml \
  --vcs-ref <planner-tag> .
```

Always pass the planner answers file to update/check-update; never rely on Copier's default, which could select devkit. Review all diffs and unmerged Git entries, run planner checks and the project's existing checks, then commit the planner-only update separately. Unrelated changed paths fail the lifecycle test. Native conflicts in edited `.planner/` files are resolved visibly; do not take one side automatically. `copier recopy` is not the normal recovery path because it can discard managed-file edits.

Version overlay, native record schema and BMAD compatibility independently. Overlay patch/minor changes cannot rewrite project records. If a future schema changes, recognize the prior supported version or report an explicit migration requirement; do not auto-convert during copy/update. V0.1 needs only schema 1 and a clean unsupported-version diagnostic, not a migration framework.

Rollback is a Git revert of the isolated **planner update commit**, restoring managed files and planner provenance together. Do not hand-edit `_commit`, downgrade another overlay or revert subsequent project work. If later edits touch the same paths, resolve the revert conflicts deliberately. For an uncommitted failed update, restore only reviewed affected tracked paths from the pre-update commit and inspect any newly created untracked paths individually. No `git clean -fd`, global reset or history rewrite. Initial uninstall removes only reviewed planner-owned paths; project-owned plans remain.

## 7. Six operation specifications

### Common operation contract

Every skill reads project instructions, `.planner/references/governance.md`, the project authority map (if present), and only relevant authoritative records. It records its source revision or working-tree fingerprint in saved results. Unknown authority, unresolved contradictions, missing approval or changed sources block dependent work while independent discovery continues.

Modes are explicit within each operation, not additional operations. An invocation authorizes routine bounded planning edits within approved scope; consequential scope/strategy changes require the concrete approval gate below. There is no blanket approval prompt for a read-only report. No operation launches the derived task prompt or runs domain verification commands as a side effect of planning.

Common completion envelope in prose or a saved report: operation, source revision, result (`complete`, `needs_input`, `blocked`, `proposed`), outputs, changed paths if any, decisions needed with reasons, findings/limitations, and recommended next operation. An empty ready set is a valid result. Do not report `complete` for missing approvals or unavailable authority.

### INIT — discover, establish authority, or propose migration

Inputs: project root, initial intention or existing artifacts, optional category, existing instructions/overlay answers/BMAD/OpenSpec inventory. No strategy inference is silently approved.

1. Inventory relevant files with native search/Git; exclude secrets, build/vendor directories and private sources outside the authorized project. Inspect dirty state and path collisions.
2. Classify a new project versus adoption/migration. Identify authors, mandates, historical artifacts, and contradictory sources. Ask only missing consequential product questions.
3. For a new project, use `bmad-product-brief` for discovery and a right-sized `bmad-prd` when requirements need development. Use the single-agent restrictions and domain context. Create proposed native records from the reviewed result; do not duplicate BMAD's elicitation inside INIT.
4. Propose the authority map, purpose/strategy baseline, initial outcome/requirements, verification profile and approval roles. INIT can stop at a strategy baseline; PLAN handles roadmap/decomposition.
5. For an existing project, create the dry-run migration report in section 9. Do not change authoritative files or authority designation until the exact mapping/change set is approved.
6. Create new project-owned files only after the relevant initialization scope is approved; never overwrite an existing path. Register accepted approvals and provenance. Do not require approval again for unchanged content the human already approved explicitly.

Outputs: project-owned `planning/planner.yaml`, approved/proposed records as clearly labeled, or a migration report and exact proposed patch. Repeating INIT discovers existing state and resumes; it never reseeds or resets content. Failure: ambiguous source owner, collision, unsupported schema or unapproved adoption. Repeat invocation must be idempotent aside from an explicitly requested new report.

### STATUS — read current state and uncertainty

Inputs: authority map, vision/objectives, current milestone, task/evidence records and pending decisions. No files are written unless the user requests a saved report under `planning/runs/<run-id>/status.md`.

Report why the project exists, approved objectives/outcomes, active milestone and its outcome/exit-criterion evidence, next horizon, task states, blockers, risks, missing evidence, unresolved authority and pending decisions. Clearly separate completed work from achieved outcomes and proposals from approved scope. Cite sources; use `unknown` for unavailable evidence. Avoid pseudo-precise percentages. Criterion coverage can be shown as counts with denominators and the caveat that it is not outcome validation.

Use native BMAD status only if its tracking file is the adopted task authority; otherwise read canonical tasks directly rather than creating a sprint file. Recommendation is one bounded next planning/review action; STATUS does not alter priorities, approve scope, mark work done, or select/launch execution automatically.

Acceptance: a blocked active milestone and all pending approvals are visible even if every child task is done. The repository remains byte-identical for an unsaved STATUS.

### PLAN — revise horizons and refine approved milestone work

Inputs: approved strategy, outcomes, requirements/constraints, evidence and approved changes. Read historical decisions before proposing a different direction.

1. Verify the baseline and current relevance. Unapproved strategy changes become CHANGE proposals.
2. Use native `bmad-prd` create/update/validate for requirements work, and `bmad-create-epics-and-stories` for decomposition. The agent supplies the approved milestone as the bounded focus and labels distant work outcome-only. Do not reproduce BMAD's full planning procedure in this skill.
3. Translate the result through the canonical task contract: epics can suggest packages; stories can suggest tasks. Preserve domain deliverables, actual requirements and genuine dependencies. Do not force a software architecture/UX document when no output depends on one.
4. Reconcile the proposal with existing owners. Update drafts or produce an exact patch; do not overwrite canonical content merely because BMAD emitted a newer draft.
5. Run `bmad-sprint-planning` with readiness-only intent where applicable. Do not generate sprint tracking. Apply planner approval/traceability/outcome gates in addition to native readiness.
6. Present changed milestone outcomes, scope, dependencies, priorities and consequences for approval. Routine decomposition within an explicitly delegated approved boundary may be recorded without a new product decision; adding obligations, exclusions or consequential reorderings cannot.
7. After approval, apply only the approved plan diff, bind approvals, and recheck references/readiness. Record distant unknowns instead of prematurely solving them.

Outputs: ordered roadmap view, milestone records with outcome gates, limited packages/tasks, readiness findings and pending decisions. No implementation. A missing upstream planning dependency blocks drafting, not unrelated status/discovery.

### NEXT — choose ready work and emit a prompt

Inputs: current approved milestone, explicit task order/priorities, complete task contracts, constraint/dependency/approval records and source freshness.

1. Evaluate readiness using section 8; no write to task state. If work is already in progress, recommend resuming/reviewing it before suggesting additional starts; do not silently claim new capacity.
2. Respect the project's adopted order. Otherwise order eligible tasks by approved priority (`P0` before `P1` before `P2`), then explicit roadmap/package order and stable task ID. Explain dependency-driven skips. No optimization or scheduler.
3. If none is ready, report precise blockers and the smallest planning/approval/review action that resolves one. Do not manufacture a ready task, infer done from a merged PR, or start a future milestone.
4. Generate the section 8 prompt from the selected approved contract. Include traceability and freshness manifest. Default output is inline; explicit save goes to `planning/prompts/<task-id>-<scope-digest-prefix>.md` with source revision and a derived-artifact header.
5. End with the prompt and readiness evidence. Do not run it, invoke an agent, reserve/lock the task, move it to in_progress, or set a schedule.

Two invocations on identical sources must recommend the same task and substantively identical contract. Prose phrasing may vary. The execution agent must reread sources and stop on a scope/digest change.

### CHANGE — controlled idea intake and replanning proposal

Inputs: unexpected idea, changed requirement/assumption, failed evidence, or a proposed strategic pivot; original source recorded.

1. Create `CHG-*` as captured, without modifying approved scope. Dedupe by references to earlier ideas; do not delete history.
2. Trace impact upward to requirements/objectives/vision and downward to milestones/packages/tasks/dependencies/prompts/evidence. Note constraints, trade-offs, completed work affected, invalidated approvals and opportunity costs. Estimate impact qualitatively if evidence does not support a numerical claim.
3. Reuse `bmad-correct-course` for a substantial change where a PRD and epics exist or a faithful derived packet can supply them. Otherwise use native `bmad-prd` Update on the relevant requirement proposal. Do not pretend correct-course works without its required inputs. All upstream editable artifacts are drafts until approved.
4. Present keep/reject/defer/narrow/pivot alternatives, a recommended option, exact proposed deltas, unresolved questions, approvers and required follow-up verification. A pivot can supersede the original strategy with explicit rationale; the old baseline remains historical.
5. Wait for consequential approval. Rejection/defer keeps the existing plan intact. For approval, recheck the source revision; if it changed, refresh the proposal rather than applying a stale diff.
6. Apply approved local planning changes through existing owners; record DEC, supersession, changed approval digests and affected prompt invalidation. Re-run PLAN for affected horizons only. Apply is idempotent against the recorded change ID/targets; partial application is reported and never marked complete.

Outputs: retained idea, impact/proposal, explicit disposition and a reviewed plan diff if approved. No implementation, automatic scope expansion or tracker publishing.

### AUDIT — structural checks plus strategic review

Inputs: approved baseline/decisions, current canonical records, Git diffs since last approved baseline, recent evidence, authority map and relevant new ideas.

1. Run the read-only structural checker for native records and links. Use native OpenSpec validate for OpenSpec-owned artifacts; native BMAD validation where its artifacts are authorities. Report unsupported/unread sources explicitly.
2. Agent review checks objective -> requirement -> milestone -> task alignment and reverse coverage; contradiction, unauthorized normative edits, orphan tasks, obsolete milestones, scope excess in delivered work, weak acceptance criteria, missing/inconclusive/stale evidence and inappropriate software assumptions.
3. Cite exact source IDs/locations and baseline differences. Semantic contradictions and strategic relevance require reasoned review; a schema pass cannot establish them. Use BMAD PRD Validate/readiness to reuse its quality review where relevant.
4. Findings are `blocking`, `warning` or `information`, with observed evidence, affected chain, confidence, owner, proposed repair and required human decision. Separate definite violations from suspected semantic conflicts needing adjudication.
5. Save only the requested report under `planning/runs/<run-id>/audit.md`; do not auto-repair, approve, retire or expand scope. Offer the corresponding CHANGE/PLAN action as a recommendation.

Triggers: before a new milestone becomes active, milestone exit, material requirement/strategy change, contradictory evidence, migration, and discovery of unauthorized edits. Default periodic recommendation: a weekly review while the project is active, adjustable by the owner. This is a human reminder policy, not a scheduler or a mandatory time-based block on every task. At minimum NEXT checks current relevant blockers, scope approvals and sources; it cannot rely on a stale clean audit.

## 8. Task readiness, prompt and evidence contracts

### 8.1 Required ready-task fields

Every field is required in native `scope`, or explicitly present at an adopted task's authoritative location. Empty exclusions or approvals must say `none` with rationale where relevant, rather than disappear.

| Field | Required meaning |
| --- | --- |
| `id`, `title`, `owner` | Unique stable identity and accountable role. |
| `objective`, `rationale` | Concrete result and why it contributes to approved objectives; reference the strategic chain. |
| `milestone`, optional `package` | Exactly one parent milestone, package in that milestone if used. |
| `requirements` | Approved requirement IDs and relevant immutable constraint/ADR references; >=1 obligation justifying the work. |
| `include`, `exclude` | Exact work boundaries, serialized as `scope.include` and `scope.exclude` alongside other task contract fields. |
| `depends_on` | Blocking task/milestone refs, or external gate with explicit criterion and evidence; distinguish informational related/context refs. |
| `context` | Paths/locators and why required; classify normative versus background. Include source authority and revision. |
| `deliverables` | Concrete expected artifacts/results; exact intended paths where known, bounded component areas otherwise. |
| `acceptance` | Criteria with stable local IDs and pass conditions. |
| `verification` | Criterion -> method -> expected evidence -> reviewer mapping, plus known practical limits. No assumption that every method is a test command. |
| `approvals` | Required approver, consequence, stop point, and valid DEC refs or explicitly delegated boundary. |
| `priority`, `size` | Approved relative order and a bounded work/review unit; uncertainty is recorded, not a false precise estimate. |

Use `kind: task`, top-level `id`/`owner`, `scope` for the remaining normative contract, and `execution.state` etc. as defined earlier. The table's field labels refer to semantic fields, not a command interface.

Readiness is a **derived conjunction**, not merely the word `ready`: approved current milestone; active approved objective chain; approved applicable requirements; complete unambiguous contract; valid task authorization; all blocking prerequisites demonstrably satisfied; no dependency cycle; available/fresh context; no blocking audit or unresolved scope decision; suitable verification and reviewer. Draft/rejected/cancelled tasks and distant milestones are excluded. A scoped research task can be ready with an unknown research answer, because its approved deliverable is evidence resolving that uncertainty.

Agents may propose draft tasks or update observed progress under existing authorization. Ready requires the approval gate. In_progress is set by the human/execution workflow outside NEXT. Review means outputs/evidence are available, not accepted. Done requires criteria/evidence review by the delegated reviewer. Blocked retains its prior intent and reason; returning to ready rechecks all gates. Reopening done needs new failed evidence or an approved scope correction with history retained. Milestone activation and achievement always require the Product Owner's decision.

### 8.2 Standard derived execution prompt

The blank `assets/prompt.md` and NEXT use this structure; values are taken from the approved task, never invented:

```text
DERIVED EXECUTION PROMPT — <TASK-ID>, not project authority
Sources: <repository>, <commit/working-tree state>, <task authority + scope digest>
Recommended model: DeepSeek V4.1 Flash; reasoning HIGH.
Escalation: DeepSeek V4 Pro HIGH only under the recorded escalation policy.

Read existing project/agent instructions first, then these sources:
<authoritative task, requirement clauses, parent milestone outcome, relevant ADRs>
<distinguish normative context from historical/background references>

Objective and rationale: <verbatim or faithful approved contract>
Trace: VIS -> OBJ/OUT -> REQ -> MS -> [WP] -> TASK
Deliver: <exact deliverables and intended files/components>
Scope includes: <approved list>
Scope excludes: <approved list>
Constraints: <approved domain/architecture/tool/project constraints>
Prerequisites: <refs, satisfaction evidence, unresolved limits>
Acceptance and verification: <criterion IDs, method, expected evidence, reviewer>

Work only within this contract. Do not infer additional product requirements.
Reread current sources before work; stop if normative scope or approval changed.
Stop before <specific consequential action requiring approval>.
If a dependency fails, authority conflicts, or requirements are ambiguous,
report evidence and propose a planning change; do not approve it yourself.

Return: changed artifacts; each acceptance criterion's result and evidence;
verification actually performed and subject revision; unrun checks/limitations;
remaining risks; requested review and any human acceptance needed.
Do not claim done/accepted solely because work was produced or checks were planned.
```

For a non-software task, replace no verification with code tests unless the task actually demands software. The task determines whether a diagram inspection, semantic counterexample, engineering analysis, experiment, package build or API test is appropriate. A task may legitimately specify human-only work. Model recommendation does not change the approved deliverable or authorize escalation expense.

Prompts are regenerated when source scope or relevant constraints change. A saved prompt records its source manifest and generation date; it is never edited to add requirements. NEXT must not reuse a prompt solely because its filename exists. Concurrent changes require revalidation, not a task lock service.

### 8.3 Domain verification and feedback

| Profile | Appropriate evidence | Insufficient evidence |
| --- | --- | --- |
| Software | Relevant automated tests/builds, integration scenario, reviewed API/package behavior at a commit. | A checked task, code existing, test commands listed but not run. |
| Engineering/deep-tech | Semantic invariants and counterexamples, analysis assumptions, units/dimensions, model/spec review, reproducible calculation or bounded experiment where relevant; named competent reviewer. | Treating code tests as validation of engineering suitability, unstated assumptions, model syntax alone. |
| Methodology/systems engineering | Definition/relationship consistency, requirement and decision traceability, scenario walkthroughs, counterexamples, source provenance, human review; empirical validation only when actually performed. | Assuming a design review proves user benefit, forcing software artifacts, turning hypotheses into mandatory requirements. |

Profiles are short reference checklists and examples, not executable plugins. The project selects applicable methods per criterion; mixed projects can use several. Evidence distinguishes artifact verification from real-world outcome validation. Failed/inconclusive evidence opens a blocker or CHANGE proposal and reassesses the requirement/milestone; it does not silently weaken acceptance criteria. A substantive evidence report can be project-owned outside `planning/evidence/` and linked in place.

## 9. Migration strategy

Migration is a controlled INIT mode, implemented as an agent workflow using maintained file/Git tools and the shared model. Do not build repository-specific import engines. Default to **adopting by reference**; normalize in place or create native replacements only if that materially improves planning and the human approves the exact patch.

### 9.1 Procedure and dry-run contract

1. **Discover.** Record repository identity, HEAD, dirty status, searched/excluded roots, planning paths and any required unavailable sources. Inspect instructions and existing authority declarations before inferring an owner.
2. **Inventory information.** Capture every requirement/task/decision ID and source occurrence, lifecycle meaning, explicit blocking edges, related/context links, criteria, history and evidence. Preserve complete original text in its original committed location; an extract cannot replace it. A manifest may hash source files but does not copy confidential material outside the project.
3. **Identify authority.** Propose owner/location per concept; distinguish current, historical, derived, proposed and mandated material. Neither newest timestamp nor most detailed document automatically wins.
4. **Map.** Map original IDs/locators to the new semantics. Preserve legacy IDs and paths by default. Document state mappings explicitly. `Related` is not automatically `depends_on`; a backlog folder is not automatically ready; closed/done is not automatic evidence of verified completion.
5. **Find conflicts and duplicates.** Compare frontmatter/body/folder state; duplicate IDs; contradictory requirements; disconnected objectives; undocumented dependencies; dependency cycles; proposed-versus-approved scope. Preserve all candidates until adjudicated. Do not auto-merge requirements by similar wording.
6. **Write a dry-run report.** Only an explicitly designated new `planning/runs/<run-id>/migration.md` and proposed patch/manifest may be created. No source edits, moves, deletions, renames, configuration changes or authority switches. On a dirty reference checkout, return the report inline or use a disposable copy rather than writing into it.
7. **Request approval for the concrete result.** Human approves source-authority choices, conflict resolutions, state mappings, precise paths/patch and any new scope separately. Explain unresolved items. Approval to migrate is not approval of proposed product requirements.
8. **Apply on a dedicated branch/disposable worktree of the destination.** Recheck HEAD and all source hashes against the approved report. Apply only the reviewed patch; abort on conflicts/staleness. Keep originals in place or as explicitly marked historical sources; do not move/delete them as a convenience.
9. **Verify losslessness and traceability.** Compare before/after manifests: every original requirement/task identity and blocking edge is either retained, explicitly mapped, or retained unresolved with a reason. Verify decisions, criteria, scope exclusions, evidence links, file history and dependency direction. Zero unexplained omissions is the gate.
10. **Record provenance and review.** Commit the approved migration separately, linking report, approval and original commit. No rebase, squash of historical commits, filter-repo or rewriting the original repo's history. Git log/blame must still reach original artifacts. Re-running the same migration detects mappings and makes no duplicates.

The migration report asset must have: scope/revision; search coverage; artifact inventory; authority table; original -> target IDs/locations/states; dependency edge table with source for each edge; conflicts/duplicates; unmapped/unknown information; proposed new paths and exact patch; byte preservation list; approval requests; verification results to run; rollback procedure; and a coverage reconciliation table. An empty or unavailable source is an explicit gap, not a green migration.

Rollback before committing restores only reviewed migration-created/edited paths. After committing use a revert of that migration commit. A rollback never removes unrelated work or canonical originals. A partially applied migration is not accepted; retain the report and describe recovery.

### 9.2 Reference-specific mapping

| Reference case | Preserve/adopt | Conflicts and review focus |
| --- | --- | --- |
| Bookvoice-like | `docs/ROADMAP.md` direction; task cards in all state folders; backlog index; `docs/TASK_SEQUENCE.md` ordering and explicit dependencies; task text/criteria/exclusions; done evidence and historical dates. | Frontmatter/body/folder mismatches; identical IDs in multiple locations; sequence prerequisites versus merely Related tasks; path prerequisites as artifact gates rather than fake task IDs. Retain the original selection policy until approved otherwise. |
| DeepPlant-like | `VISION.md`; strategy/product/roadmap distinctions; ADR/contract boundaries; direction as context only; historical gate decisions; GitHub Issue scope/revision if available. | Never turn a directional capability into authorization. Preserve the semantic core and semantic/presentation, process/physical boundaries. Current product outcome is more authoritative than an attractive future capability. Missing Issue access makes detailed-task coverage incomplete. |
| PLOS-like | Charter; mandated principles; requirement IDs/statuses; glossary/domain semantics; iteration dependency/exit criteria; decision log; semantic review evidence and its limits. | Z adopts explicit mandate provenance only; N remains proposed; D remains a design decision, not blanket product approval; H stays unvalidated. I3 is not active merely because I2 was completed. Do not import the 36 PLOS domain concepts as planner entities or impose software/storage on the methodology being planned. |

PLOS **project development** can use Git records to plan changes to a medium-independent methodology. That says nothing about whether people applying the resulting methodology must use records, tasks, software or a strategic goal for every daily action. Planner governance must preserve the product's own boundary rather than project its implementation tooling into the domain.

### 9.3 Fixtures and assignment boundaries

Do not run migrations against `Semtexcz/DeepPlant`, `Semtexcz/Bookvoice` or `Semtexcz/PLOS` during this assignment or implementation tests. Create small synthetic fixtures with the observed structures and semantics, containing no credentials or private source dumps. A fixture can include a short cited example such as TASK-075's dependency IDs, but tests must not rely on continued access to the reference repositories.

Create temporary Git repositories from fixtures, commit a baseline, run dry-run/apply/repeat/rollback scenarios there, and compare byte snapshots. These are the only writable migration test destinations. Live project adoption is a later explicit human-approved operation.

## 10. Verification design and release acceptance

### 10.1 Three layers of evidence

1. **Deterministic, offline default checks.** Native record/schema errors, duplicate IDs, missing references, reference type errors, dependency cycles, content-bound approval mismatches, forbidden template outputs, fixture preservation and isolated Git/Copier update behavior. No model, network, shell execution from records or real repository mutation.
2. **Installer/native-tool integration.** Exact pinned BMAD install/reinstall/resolver smoke, native Agent Skills validation and optional OpenSpec validation/init/update compatibility. These use only disposable project/HOME directories and may need package registries. Separate from offline checks, report actual network failures without misclassifying them as product passes.
3. **Agent-assisted acceptance.** One bounded DeepSeek Flash HIGH session per domain/changed workflow with retained input/output and human rubric assessment. This verifies behavior an instruction-file grep cannot establish: no invented requirements, useful decomposition, honoring stops, strategic coherence and non-software fitness. Run through existing native harness configuration; no test LLM client and no paid CI calls. Label real run versus hand-authored example/transcript. Never present a mocked transcript as proof the model obeys the skill.

The checker reports `errors`, `warnings`, `manual_review_required` and checked coverage separately. Exit 1 for a proven structural/approval invariant failure; exit 2 for unreadable config/unsupported schema/invalid invocation; exit 0 only means deterministic checks completed without errors. It must still print manual-review gaps; a skill cannot turn that exit into an overall strategic PASS. JSON output should be versioned (`report_version: 1`) and include rule ID, severity, source locator and message; provide human-readable output without a second data store.

Keep verification entry points explicit. In this repository use `uv sync --locked`, `uv lock --check`, `uv run --locked pytest -m "not integration"`, and separately `uv run --locked pytest -m integration`. Register the marker in I02; integration tests are skipped by the documented offline command and never selected accidentally by that command. The deployed checker interface is `uv run --script .planner/scripts/check_planning.py --project . --format json` (or `--format text`); a human/agent invokes it, never an updater hook. Pin its PEP 723 dependencies so this does not resolve against or edit an application's environment. Skill validation runs the native reference validator against each rendered skill directory as an integration check; record its pinned source/version and exact command established during I01/I02.

Allowed checker behavior: parse native YAML frontmatter with safe loading and duplicate-key rejection; validate JSON Schema; resolve native/explicit local refs; validate global ID uniqueness and parent types; detect dependency cycles; compute content digests and compare recorded approval targets; inspect explicitly supplied baseline Git metadata; check required evidence fields/subject revisions. Reading evidence is not executing verification. Do not infer semantic requirement conflict, prove human identity, select/rank tasks, generate plans/prompts, mutate records, or parse every external framework. Unsupported external portions go to agent review/native validation.

### 10.2 Concrete acceptance scenarios

| ID | Fixture and action | Required observable assertions |
| --- | --- | --- |
| A | Empty Git project. Intention: a small document conversion package. Invoke INIT, approve baseline, PLAN current milestone, approve task, NEXT. | There is an explicit purpose/objective/outcome, requirement, ordered milestone, one complete ready task and a derived prompt referencing the exact chain. Before approval NEXT yields no executable prompt. After approval it selects the task without executing or changing its state. A second run selects the same task. Completing task state alone leaves the milestone unachieved. App files/manifests/AGENTS remain absent/unchanged. |
| B | Bookvoice-like task folders plus `TASK_SEQUENCE.md`, native card/body metadata and a duplicate TASK-075 occurrence. TASK-075 explicitly depends on TASK-073, TASK-074, TASK-019, TASK-037. | Dry-run lists all five unique task identities and both TASK-075 occurrences, all four blocking edges and any other fixture edges; does not turn unrelated links into prerequisites. Conflict is reported and selection blocked until adjudication. Approved adoption retains all source text/criteria and aliases; zero unexplained lost edges/IDs. Rerun is idempotent; rollback restores bytes/history. Backlog is not automatically ready. |
| C | DeepPlant-like intent, strategy, product, current workspace milestone, long-term directions, semantic-core ADR, separate process/physical model constraint and historical gate. Introduce a future simulation task. | Current outcome and constraints survive adoption exactly; historical gates remain historical. The future task is rejected as unapproved current scope or retained as a CHG proposal, never silently made ready. Imported Issue detail is explicitly unavailable if the fixture omits it; audit does not claim full coverage. |
| D | PLOS-like charter, CON-01 software independence, proposed FR/QR in N, mandated Z, D decisions, H hypotheses, I2 complete and I3 proposed. PLAN a bounded conceptual-model consistency review. | No API/database/app artifacts or software requirements appear. Task deliverable is a reviewed semantic specification/diagram/scenario report. N/D/H never become approved requirements by import. Verification uses definitions, counterexamples and review, not task counts. I3 activation waits for owner approval. Project Git records do not become requirements on users of PLOS. |
| E | Active milestone; unexpected cloud-sync idea conflicts with local-only scope. Invoke CHANGE, then reject/defer or approve a narrowed alternative. | CHG captures provenance; proposal identifies affected objective, REQ, milestone, tasks/dependencies, constraints and stale prompts. Before approval all approved scope digests stay unchanged. Reject/defer preserves plan; approved narrow change modifies only approved targets, invalidates affected prompts and retains old decision. A changed source baseline blocks applying the old patch. |
| F | Add one task with no approved objective/requirement chain; alter an approved requirement to permit cloud upload without DEC; add two opposed retention clauses. Invoke AUDIT. | Structural orphan and changed-scope approval mismatch are definite findings with paths/IDs. Opposed clauses are a cited semantic conflict for review, not a fabricated automatic proof. NEXT excludes affected tasks. No source is auto-repaired. A schema-clean state cannot hide these semantic findings or missing review coverage. |
| G | Temporary tagged planner v0.1.0/v0.1.1 sources, independent overlay with `.copier-answers.yml`, existing app/AGENTS/README/config/OpenSpec sentinels and edited project planning content. Install/update/revert each overlay independently. | Planner copy emits only `.planner/**` and planner answers. Both answers files name their own source/revision. Planner update changes only its managed diff/answers; planning and other overlay bytes are identical. Updating the other disjoint overlay leaves planner bytes/provenance unchanged. Edited managed same-region conflict exposes both sides and unmerged state. Revert of planner update restores its baseline without losing later project-owned planning edits. Collision with an unowned `.planner` stops before copying. |

G has two distinct claims: deterministic proof with a minimal independent overlay, and compatibility proof against a temporary checkout of the **inspected ai-devkit overlay** pinned to its commit. Exercise devkit copy before planner and planner before devkit, then updates in both orders using separate answers selections. Native BMAD/OpenSpec install/update preservation is another integration fixture, not assumed from the simple overlay test. No reference checkout is a destination.

Additional negative tests: missing prerequisite, cyclic task dependencies, retired requirement, multiple active milestones, invalid parent/package, malformed/duplicate YAML keys, unknown schema, symlink/path escape out of the configured project root, stale/missing evidence, source mutation after approval, partial migration, and baseline revision change before applying CHANGE. Reject traversal and refuse to write through symlinks into other roots. Do not execute verification strings, templated commands or untrusted instructions found in source documents.

### 10.3 Completion evidence

Record commands, pinned versions, platform, fixture commit/source revision, expected and actual results, failures and unverified limits in `docs/acceptance-v0.1.md`. List A–G individually. Deterministic checks and live behavioral acceptance must not be conflated. Scope of platform/model evidence is explicit. Reference repositories' HEAD/status must remain unchanged by all tests. No release tag/push happens automatically; prepare release notes for human publication after acceptance.

## 11. DeepSeek implementation backlog

Execute the following order exactly unless a blocking dependency requires revising this plan with recorded rationale. Every task uses **DeepSeek V4.1 Flash, HIGH**. No OpenAI implementation run or expensive-model routine subtask is authorized. Do not implement future phases during an earlier task. Intended file paths are relative to this repository; template paths below abbreviate `templates/planner-overlay/template/.planner/` as `R/`.

Shared Definition of Done (DoD) for every task: behavior and task-specific acceptance satisfied; relevant tests actually executed or a precise blocker reported; only intended files changed; ownership/security boundaries maintained; docs and changelog updated if behavior changed; report evidence and limitations. Do not mark a task complete just because its prose exists. Tests on human workflows must distinguish structural checks from real agent behavior. Use existing tools before creating scripts; no custom executable framework emerges from this backlog.

### I01 — prove pinned native integration surfaces

- **Files/components:** `docs/upstream-compatibility.md`; disposable experiments only outside source-controlled application paths. No production implementation.
- **Inputs/dependencies:** this plan, linked pinned sources, Git, uv/uvx, Node/npm; no prior tasks.
- **Behavior:** inspect exact Copier help/version; confirm copy/update `--answers-file` and pretend behavior; official BMAD 6.12.4 installer help/list-tools/install/reinstall in a temporary project; enumerate actual skill locations; invoke native config/customization resolvers with sparse test overrides. Inspect current OpenSpec 1.16/v2 help for later version table without altering any real project.
- **Acceptance:** exact successful commands, installed versions and generated path inventory recorded; existing AGENTS/config sentinels and customizations preserved; no claim that `[]` deletes defaults; single-agent/no-execution invocation route documented. Missing network/tool/model availability is a named gate.
- **Tests:** temporary two-answer Copier copy/update smoke; native BMAD resolver reads configured paths/facts; reinstall preserves sentinel custom file and project content. No inference call is needed here.
- **DoD:** shared DoD plus evidence sufficient to use concrete commands in later tasks. If the pinned upstream cannot meet boundaries, stop dependent integration work and propose the smallest native correction; never patch/fork BMAD.

### I02 — establish minimal repository tooling and policy

- **Files/components:** `README.md`, `LICENSE`, `AGENTS.md`, `CHANGELOG.md`, `pyproject.toml`, generated `uv.lock`, `tests/conftest.py`, `docs/architecture.md`.
- **Inputs/dependencies:** I01 compatibility evidence and model policy.
- **Behavior:** original MIT project material, architecture/non-goals and contribution/model boundaries; development-only uv environment using maintained Copier/pytest/PyYAML/jsonschema plus native skill validation dependencies as needed. Pin exact tested direct versions and generated dependency lock; do not copy devkit's entire toolchain or configure global agents.
- **Acceptance:** independent checkout installs its own dev tools; no ai-devkit runtime dependency; no app package/server or generated lock hand edits; all checks have one documented invocation.
- **Tests:** locked environment synchronization and a minimal pytest collection/configuration smoke; lock consistency. Avoid adding trivial tests that repeat prose.
- **DoD:** shared DoD plus reproducible tool installation documented with observed versions. No target-project toolchain files are introduced.

### I03 — specify native records and blank assets

- **Files/components:** `R/schemas/project.schema.json`, `R/schemas/record.schema.json`, `R/assets/{project-config.yaml,strategy.md,requirement.md,milestone.md,task.md,decision.md,change.md}`, `R/references/information-model.md`, `docs/information-model.md`, `tests/test_native_records.py`.
- **Inputs/dependencies:** I02; sections 3–4 and 8.
- **Behavior:** encode native record types, stable IDs, scope/execution split, objective/outcome/package embedding, approval target and evidence structures. Native schema required fields agree with the task contract. Authority bindings store pointers without mirrored scope/state. Blank assets are marked unapproved; no seeded product scope.
- **Acceptance:** representative software/engineering/methodology records validate; incomplete ready task, duplicate ID, missing mandatory criterion and invalid state/type fail; task evidence changes do not change scope identity. Unknown schema produces a specific diagnostic.
- **Tests:** valid/invalid meaningful record fixtures, Unicode/digest test vectors defined for I06, placeholder assets cannot count as approved/ready. Validate schemas with the maintained library.
- **DoD:** shared DoD plus all fields/enums/examples have a single documented owner and no unnecessary entities.

### I04 — package the isolated Copier overlay

- **Files/components:** `copier.yml`, `templates/planner-overlay/template/{{ _copier_conf.answers_file }}.jinja`, `R/README.md`, `tests/test_template.py`, `docs/install-update.md`.
- **Inputs/dependencies:** I01–I03; confirmed Copier syntax.
- **Behavior:** render only managed runtime content and `.copier-planner-answers.yml`; use `_subdirectory`, native answers serialization and no executable tasks/migrations. Explain explicit skill-path activation and install collision preflight. Project content assets stay inert under `.planner/assets/`.
- **Acceptance:** exact rendered-path allowlist; no `planning/`, AGENTS, README, app/config/OpenSpec/devkit paths in output; own source/tag in answers; paths with spaces and Unicode work. Existing unknown `.planner` is identified before actual copy in the documented workflow.
- **Tests:** tagged disposable template copy, answer provenance, forbidden-output assertions, overlapping-path preflight scenario and render escaping. Nothing copied from reference checkouts into target paths.
- **DoD:** shared DoD plus a clean empty-project install is reproducible and contains no project truth to overwrite later.

### I05 — add a bounded read-only structural checker

- **Files/components:** `R/scripts/check_planning.py`, `tests/test_references.py`, additions to `tests/test_native_records.py`, `docs/verification.md`.
- **Inputs/dependencies:** I03–I04; maintained parsing/schema libraries.
- **Behavior:** safe native frontmatter loading, duplicate-key rejection, schemas, ID inventory, unique authorities, parent/reference type/existence, at-most-one active milestone, prerequisite cycles and incomplete coverage reporting. Reuse one checker; no planning decisions or writes. Use PEP 723 metadata for isolated pinned `uv run --script` dependencies, confirmed on the supported platform.
- **Acceptance:** read-only human/JSON reports and exit semantics in section 10; records/commands are never executed; unsupported external content is explicit manual coverage; out-of-root paths/symlinks rejected.
- **Tests:** dangling/type-invalid references, cycles, duplicate IDs/authorities/keys, traversal, unreadable config and unchanged file hashes before/after checks; meaningful success fixture with no silent gaps.
- **DoD:** shared DoD plus checker remains a validator, not an operation dispatcher, parser framework or planning engine.

### I06 — validate authorization and evidence references

- **Files/components:** `R/scripts/check_planning.py`, `R/references/governance.md`, `tests/test_approvals.py`, evidence fixtures.
- **Inputs/dependencies:** I03/I05; approval and evidence contracts.
- **Behavior:** shared native scope digest; verify target binding to accepted decisions and detect stale scope; inspect evidence criterion/subject/result/reviewer fields and dependency completion claims. Report inability to verify human provenance rather than invent identity verification. Progress-only changes retain scope authorization.
- **Acceptance:** unapproved/stale scopes cannot pass readiness assessment; approval source/actor required; a forged accepted flag is explicitly not authenticated by checker; failed/inconclusive evidence cannot imply achieved milestone. Explicit delegated boundaries are referenced and reviewed, not automatically assumed.
- **Tests:** changed include/exclude/criterion/constraint invalidates prior approval; execution-state/evidence-only changes preserve scope digest; Unicode vectors; missing evidence/reviewer and stale subject warnings/errors by contract. No arbitrary command execution.
- **DoD:** shared DoD plus clear distinction between a machine-checkable binding and the human trust boundary.

### I07 — document native BMAD adaptation and invocation guardrails

- **Files/components:** `R/references/bmad-adapter.md`, `R/references/governance.md`, `R/references/verification-profiles.md`, `tests/test_bmad_install.py`, `docs/upstream-compatibility.md`.
- **Inputs/dependencies:** I01/I03/I06 and actual installed skill/customization paths.
- **Behavior:** write exact invocation recipes and sparse project-owned override examples for the five reused planning skills; no upstream code/template copies. Define draft packet provenance, native config keys, stopped follow-on execution, single-agent behavior and approval semantics. Separate network integration tests from offline tests.
- **Acceptance:** native resolver proves planner facts/paths apply and existing overrides remain; no automatically overwritten application config; no nonexistent disable flags, appended-empty-array assumptions, or silent v7/shim dependency.
- **Tests:** disposable official install/reinstall, sentinel AGENTS/project content/custom config hashes; actual resolver output for sparse settings. Record limitations if a behavior still needs agent acceptance.
- **DoD:** shared DoD plus a small reusable adapter document rather than a BMAD fork or duplicated elicitation workflow.

### I08 — implement new-project INIT skill

- **Files/components:** `R/skills/planner-init/SKILL.md`, INIT part of `R/references/operation-contracts.md`, `tests/test_workflow_contracts.py`, `tests/fixtures/empty/`, `docs/operations.md`.
- **Inputs/dependencies:** I03–I07; blank assets and BMAD discovery recipes.
- **Behavior:** inspect owners/collisions, use native brief/PRD for discovery, prepare proposed strategy/requirements/config, bind actual human approval, create project-owned files once and resume safely. No migration apply yet.
- **Acceptance:** purpose/beneficiary/outcome and authority are explicit; questions only for consequential missing information; draft output never becomes approved implicitly; repeat INIT preserves edited content; no AGENTS/config/app edits.
- **Tests:** native skill format validation and resource links; approval-before-promotion transcript fixture with independent state/diff assertions; idempotent second invocation evaluated in the later live A run. Do not claim a canned transcript proves model behavior.
- **DoD:** shared DoD plus INIT is callable by explicit file path without host configuration.

### I09 — implement bounded PLAN skill

- **Files/components:** `R/skills/planner-plan/SKILL.md`, PLAN contract in `R/references/operation-contracts.md`, roadmap-view asset/example in `R/assets/`, empty/three-domain plan fixtures, workflow tests.
- **Inputs/dependencies:** I07–I08; approved baseline, model and task schemas.
- **Behavior:** native PRD/epics decomposition for approved current milestone, rolling-wave horizons, draft reconciliation, readiness-only native gate, exact approval diff and authoritative promotion.
- **Acceptance:** current work detailed, next moderate, distant outcome-only; new obligations require approval; no second sprint/task ledger; tasks trace to real requirements; no implementation skills invoked.
- **Tests:** representative current/next/distant fixture, unapproved change and missing BMAD dependency outcomes; structural validation of produced review example; live behavior checked in I11/I17.
- **DoD:** shared DoD plus native decomposition is reused and cross-domain vocabulary remains configurable context, not another framework.

### I10 — implement NEXT and the derived prompt contract

- **Files/components:** `R/skills/planner-next/SKILL.md`, `R/assets/prompt.md`, NEXT contract reference, `tests/test_workflow_contracts.py`, task-selection/prompt fixtures.
- **Inputs/dependencies:** I06/I09; task order/readiness and exact contract fields.
- **Behavior:** agent evaluates gates, honors adopted ordering, skips blocked work, explains choice and emits/saves a source-bound prompt. Do not add a custom selection executable.
- **Acceptance:** approved eligible task selected deterministically under defined tie-breaking; no-ready returns blockers; prompt preserves scope/exclusions/constraints/verification/approval stops and requested model policy. No task-state transition or execution.
- **Tests:** blocked-first versus ready-next, already-in-progress, missing approval/requirement, external source inaccessible, stale prompt manifest and changed scope; human checks source-to-prompt completeness. File/diff assertions prove no state mutation in scripted examples.
- **DoD:** shared DoD plus prompt is explicitly derived and sufficient for a separate execution agent without invented decisions.

### I11 — prove the smallest working vertical slice (A)

- **Files/components:** `tests/fixtures/empty/` acceptance inputs, `tests/test_workflow_contracts.py`, `docs/acceptance-v0.1.md` A entry, README quick start.
- **Inputs/dependencies:** I08–I10; native BMAD installation and an available DeepSeek Flash HIGH harness.
- **Behavior:** replay A in a disposable empty Git project: vision -> requirements -> roadmap -> current milestone -> approved ready task -> prompt. Human approves concrete checkpoints; no generated prompt is executed.
- **Acceptance:** all A assertions pass, including pre-approval stop, unchanged application paths, full trace and task-completion-versus-outcome distinction. Explicit-path operation works independent of ai-devkit.
- **Tests:** offline schema/reference/snapshot checks plus one recorded real DeepSeek session and human rubric assessment. Report actual model/version, not an inferred provider alias.
- **DoD:** shared DoD plus first usable documented slice demonstrated before adding the remaining workflows. If paid/native model access is unavailable, leave behavioral acceptance pending and continue independent deterministic work.

### I12 — implement read-only STATUS

- **Files/components:** `R/skills/planner-status/SKILL.md`, STATUS contract reference, status fixtures and workflow tests, operations documentation.
- **Inputs/dependencies:** I06/I11; evidence and pending decision data.
- **Behavior:** concise source-cited objectives, active outcome, criterion/evidence coverage, task progress, uncertainty, risks/blockers and decisions. Optional report only on explicit save; native BMAD status only when adopted.
- **Acceptance:** all-tasks-done/milestone-evidence-missing is visible; pending approval cannot disappear; unavailable source is unknown, not assumed healthy; no unsaved writes or reprioritization.
- **Tests:** before/after repository bytes; missing-evidence and pending-change fixtures; human assessment of source accuracy and useful recommendation.
- **DoD:** shared DoD plus STATUS makes no new canonical summary ledger.

### I13 — implement controlled CHANGE (E)

- **Files/components:** `R/skills/planner-change/SKILL.md`, CHANGE contract, `R/assets/change.md` refinements, `tests/fixtures/change/`, workflow tests, E acceptance report.
- **Inputs/dependencies:** I07/I09/I12; current scopes and explicit source baseline.
- **Behavior:** idea capture, native correct-course/PRD Update, full-chain impact, alternatives, exact diff, human disposition and stale-baseline apply check. Retain approved/rejected/deferred history.
- **Acceptance:** E assertions; plan remains unchanged until approval, narrowed approved change touches only approved targets, valid strategic pivot can supersede prior vision without erasing it. No assumed consent or external publishing.
- **Tests:** reject/defer/approve, incomplete inputs, stale proposal, partial apply and repeated same change. One bounded real Flash CHANGE acceptance validates stopping behavior; CI remains offline.
- **DoD:** shared DoD plus a proposed idea cannot become a ready execution task without the recorded authority chain.

### I14 — implement AUDIT and drift evidence (F)

- **Files/components:** `R/skills/planner-audit/SKILL.md`, `R/assets/audit-report.md`, AUDIT contract, `tests/fixtures/drift/`, workflow/reference tests, F acceptance report.
- **Inputs/dependencies:** I05–I07/I12/I13; approved baseline and Git differences.
- **Behavior:** combine deterministic violations, native validation and semantic/strategic review; bidirectional traces, unauthorized scope, contradictions, stale evidence, obsolete milestones and explicit coverage limitations. No automatic repairs.
- **Acceptance:** F detects both definite orphan/unauthorized edits and cited semantic contradiction; flags uncertainty appropriately; failed evidence can trigger re-evaluation; report distinguishes schema results from strategic judgment.
- **Tests:** injected orphan, approved-scope mutation, opposed requirements, all-tasks-complete/wrong-outcome and no-prompt-repair snapshots. Retain actual Flash audit output and human assessment for semantic coverage.
- **DoD:** shared DoD plus findings have source, owner, severity, repair proposal and approval boundary.

### I15 — extend INIT with dry-run and approved migration

- **Files/components:** `R/skills/planner-init/SKILL.md`, `R/references/migration.md`, `R/assets/migration-report.md`, `docs/migration.md`, `tests/test_migration_fixtures.py`.
- **Inputs/dependencies:** I06/I08/I13/I14; migration procedure and synthetic fixtures.
- **Behavior:** inventory/map/conflict/dry-run with patch, concrete approval, stale-source guard, approved minimal application, losslessness reconciliation and repeat/rollback. No reusable import engine.
- **Acceptance:** dry-run creates only permitted new report artifacts; all source bytes untouched; no apply before actual approval; zero unexplained omitted IDs/edges/criteria and decisions; preserved history; incomplete/unavailable sources explicit.
- **Tests:** dirty tree, conflicting IDs/metadata, denied approval, approved apply, repeated apply, source mutation after report, partial failure and revert in temporary Git repos. No real reference repo destinations.
- **DoD:** shared DoD plus migration can be reviewed before any authority switch and cannot silently approve imported proposals.

### I16 — prove Bookvoice-like adoption (B)

- **Files/components:** `tests/fixtures/bookvoice-like/`, `tests/test_migration_fixtures.py`, Bookvoice migration example in docs, B acceptance entry.
- **Inputs/dependencies:** I15; inspected task/card/sequence conventions.
- **Behavior:** include five unique task IDs, duplicate TASK-075 occurrences, differing folder/body/frontmatter states, four explicit TASK-075 prerequisites, related-only link, deliverables/criteria and an artifact gate. Reconcile by approved mapping, preferably retaining original authority.
- **Acceptance:** every B assertion plus manifest counts and edge sets reconcile exactly; done cards retain evidence limits; selection respects original priority/dependencies and does not equate backlog to ready.
- **Tests:** before/after IDs/occurrences/edges/text/hash manifests, dry-run, approved adoption, idempotence, rollback/history; one bounded Flash migration/report assessment on fixture only.
- **DoD:** shared DoD plus no information omitted for the convenience of the native schema and no Bookvoice checkout changes.

### I17 — prove engineering and methodology applicability (C/D)

- **Files/components:** `tests/fixtures/deepplant-like/`, `tests/fixtures/plos-like/`, migration/workflow tests, profile examples, C/D acceptance entries.
- **Inputs/dependencies:** I09/I14/I15; observed authority and approval distinctions.
- **Behavior:** small representative artifact sets, including historical/future directions and engineering constraints; PLOS Z/N/D/H, glossary/diagram references, iteration outcomes and semantic verification. Plan one engineering analysis/spec task and one methodology review task.
- **Acceptance:** C/D assertions; future direction never authorizes current work; mandates/proposals/hypotheses remain distinct; no invented software deliverables; bounded non-software outcome evidence and accountable review.
- **Tests:** semantic-core/architecture constraint byte preservation, correct normative-state mapping, blocked unapproved iteration, unmet outcome despite done tasks. Retain a real Flash session per domain and human rubric assessment. No source repository writes.
- **DoD:** shared DoD plus universal applicability has demonstrated evidence, not just vocabulary changes in a README.

### I18 — prove optional OpenSpec/existing BMAD authority boundaries

- **Files/components:** `tests/test_openspec_boundary.py`, `tests/test_bmad_install.py`, small synthetic existing-framework fixtures, native invocation version table in `R/references/bmad-adapter.md`, compatibility documentation.
- **Inputs/dependencies:** I01/I07/I10/I15; native installed OpenSpec 1.16.0 and v2 baseline identified in I01.
- **Behavior:** existing requirements/checklists remain authoritative; planner references/refines same items through native workflows, validates natively, detects missing metadata without making duplicate task states. Native BMAD tracking can also be adopted without creating native mirrors.
- **Acceptance:** no OpenSpec auto-init/upgrade, no planner overwrite of generated skills/config; v1/v2 native validation paths proven separately; framework-generated files never Copier-owned; underlying installer updates leave planner bytes and project planning unchanged.
- **Tests:** temporary official init/validate/update, byte sentinels, separate answers/provenance, adopted task -> prompt case, missing detail -> unready, stale source -> stop. No custom OpenSpec parser or client.
- **DoD:** shared DoD plus known compatibility matrix with measured limits; unsupported versions explicitly diagnosed.

### I19 — prove independently versioned overlays and rollback (G)

- **Files/components:** `tests/test_overlay_lifecycle.py`, `tests/fixtures/overlays/`, `docs/install-update.md`, G acceptance entry.
- **Inputs/dependencies:** I04/I11/I15/I18; pinned inspected ai-devkit source copied to a temporary fixture checkout for read-only source use.
- **Behavior:** two temporary tagged planner revisions and disjoint second overlay; install in both orders; update each explicitly by its own answers; planner conflict/revert and planning-content preservation. Repeat compatibility smoke with actual ai-devkit template in disposable destination.
- **Acceptance:** every G assertion; only managed paths/provenance change; both independent histories/revisions remain correct; edited/deleted project planning files are never reseeded; AGENTS/application config/other answers remain untouched. Initial collision handling and edited managed conflict are distinct tests.
- **Tests:** hash whole unrelated tree before/after, allowlist changed files, inspect Git unmerged stages and both conflict texts, resolve and recheck, revert planner-only update after later project planning commit. Assert untracked unrelated sentinels survive recovery instructions.
- **DoD:** shared DoD plus update/rollback demonstrated with native Copier/Git, no custom updater and no reference destinations.

### I20 — complete user docs, CI and v0.1 acceptance handoff

- **Files/components:** `README.md`, `docs/{operations,install-update,migration,verification,upstream-compatibility,acceptance-v0.1}.md`, `.github/workflows/verify.yml`, `CHANGELOG.md`; necessary CI policy test in `tests/`.
- **Inputs/dependencies:** I01–I19 with recorded results.
- **Behavior:** self-contained install/activate/use/update/recover guidance, native dependency version matrix, A–G evidence and limitations, release notes. CI runs offline checks and separate controlled installer integration; caches/locks are native. No dashboard/docs-site framework unless an actual requirement emerges.
- **Acceptance:** new user follows README in a disposable clean supported environment; all six operations documented; A–G results individually attributable; no production code execution/publishing in planner operations; CI is read-only with no secrets, paid inference, `pull_request_target`, release tag creation or push.
- **Tests:** locked dependencies, full offline suite, native skill validator against rendered skills, Markdown/resource links, install/update integration on Linux x86-64 and unchanged tracked tree after verification. A real model session is separately recorded as human-run acceptance, never smuggled into CI.
- **DoD:** shared DoD plus no unresolved release-blocking scenario; incomplete evidence leaves release pending. Prepare a reviewed v0.1.0 release candidate; human publication/tagging is outside automatic implementation completion.

## 12. Exact execution order, gates and unresolved items

Execution order:

```text
I01 native compatibility evidence
I02 repo policy/tooling
I03 model/schema/assets
I04 isolated Copier distribution
I05 read-only structural checks
I06 approval/evidence checks
I07 native BMAD adaptation
I08 INIT (new project)
I09 PLAN
I10 NEXT/prompt
I11 vertical slice A — demonstrate before expansion
I12 STATUS
I13 CHANGE + E
I14 AUDIT + F
I15 migration workflow
I16 Bookvoice-like B
I17 DeepPlant-like C + PLOS-like D
I18 OpenSpec/existing BMAD compatibility
I19 independent overlays G
I20 docs/CI/all-scenario acceptance
```

Acceptance to call v0.1 implementation complete: six bounded operations available; A–G demonstrated with the evidence layers applicable to each; independently updatable planner overlay; project truth and other overlay content preserved; native framework ownership honored; no unauthorized scope or approval inference; both software and non-software task/prompt/evidence flows demonstrated; installed dependencies/versions/platform and remaining limits documented. Do not confuse completing implementation tasks with accepting product outcomes.

No consequential product question is unresolved in this plan. The following are **technical verification gates**, not permission to redesign around a custom engine:

| Gate | Status at planning handoff | Resolution / blocking scope |
| --- | --- | --- |
| Exact pinned installer behavior, generated path ownership and native override resolution | Source/documentation inspected; not installed here. | I01 before dependent integration. If official installer writes conflict with owner boundaries, use native supported choices or record the incompatibility. |
| BMAD obeys single-agent, no-execution, cross-domain planning boundaries | Supported customization surfaces inspected; behavior not run. | I07/I11/I17 demonstrate; block affected workflow/release if it cannot comply. Do not fork or duplicate BMAD without a separately demonstrated requirement and approved revision of this architecture. |
| Actual DeepSeek V4.1 Flash / V4 Pro provider IDs and HIGH availability in the execution environment | User requested these model labels; no API availability claim. | Operator selects through native harness config before model runs. Unavailable Flash blocks implementation model runs; deterministic/read-only work can continue. No OpenAI substitution. |
| Existing OpenSpec 1.16 versus current v2 integration | Version difference observed; compatibility not executed. | I18 tests both native paths; no automatic host upgrade. |
| Real agent behavior and supported clean-machine installation | No runtime tests in this architecture-only assignment. | I11–I20 supply actual evidence; do not publish unsupported platform/model claims. |

No implementation was begun by the planning agent. DeepSeek must start at I01, respect each approval boundary during live fixture sessions, and stop when this bounded v0.1 is accepted or a documented blocker requires human judgment. This handoff does not authorize migration of the three real reference repositories or release publication.

**PLANNING COMPLETE — READY FOR DEEPSEEK IMPLEMENTATION**
