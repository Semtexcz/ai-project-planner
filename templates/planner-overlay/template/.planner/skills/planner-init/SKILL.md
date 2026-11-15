---
name: planner-init
description: Initialize a project's planning authority or resume an interrupted initialization. Use when a project has no planning/planner.yaml, when the user asks to start planning, or when existing planning artifacts need an approved adoption proposal. Creates project-owned planning content only after explicit human approval.
---

# INIT

Read, in order:

1. the target project's instructions and `AGENTS.md` (if present);
2. `../../references/governance.md`;
3. `../../references/operation-contracts.md` (INIT);
4. `../../references/bmad-adapter.md`;
5. `../../references/information-model.md` and `../../references/migration.md`
   when existing artifacts are present;
6. `../../assets/project-config.yaml`, `strategy.md`, `requirement.md`,
   `milestone.md`, `task.md`, `decision.md` and `change.md` as structural
   guides only.

Also read any existing `planning/planner.yaml`, `.planner/README.md`, BMAD or
OpenSpec inventory, and the project's real authority files.

## Procedure

### 1. Inventory and classify

Use native file search and Git. Record repository identity, HEAD, dirty status,
searched roots, exclusions and unavailable sources. Never read secrets,
credentials, private mail or files outside the authorized project.

Classify the request as:

- **new** - no planning authority exists;
- **resume** - planner files exist; continue without reseeding;
- **adopt/migrate** - existing vision, requirements, roadmap, ADRs, tasks,
  OpenSpec or issues carry authority.

Do not infer product strategy from a directory name, and do not treat a
backlog, a `final` status, a closed issue or a merged PR as approval.

### 2. Ask only consequential questions

Ask for missing purpose, beneficiaries, problem, strategic choices, exclusions,
category (`software`, `engineering`, `methodology`), accountable roles and
existing authority ownership. Do not ask the human to restate information
already present in an authoritative source. Ask one bounded round where
possible.

### 3. Develop planning content

For a new project, use the native `bmad-product-brief` skill for discovery and
a right-sized `bmad-prd` when requirements need development, following
`../../references/bmad-adapter.md`. Use one agent, no subagents, no publishing
and no execution.

For an existing project, do not rewrite its content. Build a dry-run adoption
proposal per `../../references/migration.md`; every original ID, dependency,
criterion and decision stays accounted for.

### 4. Prepare the exact proposal

Present:

- the authority map with one owner and one location per concept;
- roles and approval authority;
- purpose, strategic choices, exclusions and assumptions;
- objectives (`OBJ-*`) with outcome baselines/targets (`OUT-*`);
- initial requirements (`REQ-*`) with sources and verification;
- verification profile(s) and reviewer roles;
- for adoption, the migration report and exact patch.

Separate what is already explicitly approved from what is proposed. An existing
explicit mandate retains its original provenance; do not relabel an entire
historical design as approved.

### 5. Approval gate

Stop and obtain explicit human approval for the concrete proposal, including
the exact paths to be created and, for adoption, the authority changes and
conflicts. Approval to initialize is not approval of every proposed product
requirement unless the human approves that exact content.

Prepare records first, then record the approval as a `DEC-*` with the human
actor, ISO date, original approval source and exact `scope_sha256` targets per
`governance.md`. Never invent approval.

### 6. Create once, never overwrite

After approval:

- create `planning/planner.yaml` from the reviewed configuration;
- create only approved/proposed records at the proposed paths;
- create directories, `planning/roadmap.md` if a roadmap view was approved,
  and `planning/evidence/` as needed;
- replace every `-000` placeholder and placeholder text with reviewed values;
- bind approvals to the exact final scopes;
- record the source revision in `planning/runs/<run-id>/init.md` if a report was
  requested.

Before each write, check that the path does not exist. If it does, stop and
report the collision. Never overwrite, reseed, delete or silently merge
user-owned planning files.

Do not write `AGENTS.md`, `README`, application manifests, CI, `_bmad/**`,
`openspec/**` or another overlay's configuration.

### 7. Resume safely

A repeated INIT reads existing state and continues from the first incomplete
step. If `planning/planner.yaml` exists, do not replace it. Report what is
present, what is still proposed and what needs a human decision. Create a new
report only when explicitly requested.

## Completion

Return the common envelope from `governance.md`. Use `needs_input` when a
consequential product question or approval is missing, `proposed` when a
reviewable proposal exists, `blocked` for an owner/collision/schema conflict,
and `complete` only after the approved files exist and structural checks pass.

Recommended next operation after a strategy baseline: PLAN.
