# Information model

The normative runtime contract is
[`templates/planner-overlay/template/.planner/references/information-model.md`](../templates/planner-overlay/template/.planner/references/information-model.md),
shipped to installed projects as `.planner/references/information-model.md`.
This page is a short orientation; do not maintain divergent field lists here.

## Core idea

One concept has one authoritative location and one accountable human role.
Views, links, prompts and reports do not become owners. Native records use
YAML frontmatter with a strict `scope`/`execution` split:

- `scope` is normative: purpose, obligations, outcomes, boundaries, criteria,
  verification and the task's approval references.
- `execution` is operational: state, blockers, evidence, progress notes and the
  approval references for strategy, requirement and milestone records. Task
  approvals stay in `scope` because they are part of the task contract.

Markdown body explains context and history. It cannot add permission or
acceptance criteria absent from `scope`.

## Entities

Vision/strategy (`VIS`) contains objectives (`OBJ`) and expected outcomes
(`OUT`). Requirements (`REQ`) link to objectives and carry acceptance and
verification criteria. Milestones (`MS`) state an outcome and exit criteria and
may embed work packages (`WP`). Tasks (`TASK`) are the smallest useful
deliverable or review unit and link to one milestone and at least one
requirement. Decisions (`DEC`) record human dispositions and content-bound
approvals. Changes (`CHG`) capture ideas without modifying approved scope.
Evidence is embedded on the record it supports.

There is deliberately no risk, sprint, release, ticket, backlog-item,
capability, approval-request or agent-run entity. Roadmap is an ordered view of
milestones. Assumptions, risks, blockers and open questions live on affected
records.

## Approvals

Approval is an explicit human action bound to a content digest of `scope`:
SHA-256 over UTF-8 JSON with sorted keys, compact separators and no ASCII
escaping. Progress and evidence changes do not alter the digest; normative
changes do. A decision accepted by an agent without a recorded human actor and
source is not proof of approval. The checker verifies the binding, not identity.

## Domain neutrality

Software, engineering research and methodology projects share the model but not
the evidence methods. Verification can be an automated test, an engineering
counterexample, a semantic review, a scenario walkthrough, a package build or
human-only work. A task determines what evidence is appropriate; the model does
not force software artifacts onto non-software deliverables.

See `docs/verification.md` for the three verification profiles.
