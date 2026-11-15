# Native information model (runtime reference)

This is the normative runtime contract for native planner records. Repository
documentation explains and links here; do not maintain a second copy of this
text.

## Serialization

Native records are Markdown files with YAML frontmatter. Frontmatter has
`schema_version`, `kind`, `id`, `owner`, `scope`, `execution` and optionally
`extensions`. All normative content belongs in `scope`. `execution` holds state,
blockers, evidence and progress notes. Markdown body explains context and
history and cannot add permission or acceptance criteria absent from `scope`.
If prose contradicts scope, AUDIT reports it; nothing is rewritten
automatically.

Schemas: `../schemas/record.schema.json` and `../schemas/project.schema.json`.
Use YAML with unique mapping keys. Arrays have a deliberate order. Dates,
versions and measured targets are strings.

## Identifiers

Default prefixes for new projects:

| Record | Default ID | Where |
| --- | --- | --- |
| Strategy / vision | `VIS-001` | `planning/strategy.md` |
| Objective / outcome | `OBJ-001` / `OUT-001` | embedded in strategy |
| Requirement | `REQ-001` | `planning/requirements/` |
| Milestone | `MS-001` | `planning/milestones/` |
| Work package | `WP-001` | embedded in a milestone |
| Task | `TASK-001` | `planning/tasks/` |
| Decision | `DEC-001` | `planning/records/` |
| Change | `CHG-001` | `planning/records/` |

Criterion IDs use `RECORD-ID:TYPE-N`, for example `TASK-001:AC-1`. Evidence IDs
use `RECORD-ID:EV-N`. Identifiers are stable and unique inside a project; never
reuse or renumber them. Adopted legacy IDs (`FR-01`, `CON-01`, `ADR-07`) are
retained; map an alternative name with `aliases` only when a real collision
needs disambiguation.

## Record shapes

Each criterion is `{id, statement}`. Each verification entry is
`{criteria, method, expected_evidence, reviewer}`. Each evidence entry is
`{id, criteria, method, subject_revision, result, artifact, reviewer,
limitations, observed_at}` where `result` is `pass`, `fail` or `inconclusive`.
A dependency is a record ID or `{gate, criterion, evidence_ref}`. A context
entry is `{ref, authority, revision, purpose, normative}`, with an optional
`sha256` of the local file content. Record `sha256` for normative local context:
a matching hash keeps the source fresh when the repository revision moves, and a
changed hash blocks readiness until the source is reread and the scope
re-approved. Background context (`normative: false`) cannot block readiness on a
revision mismatch.

| Kind | Normative `scope` | Operational `execution` |
| --- | --- | --- |
| strategy | `purpose`, `beneficiaries`, `problem`, `choices`, `exclusions`, `assumptions`, `objectives[]` with `id`, `statement`, `outcomes[]` (`id`, `description`, `baseline`, `target_or_rubric`, `verification`, `review_horizon`) | `state`, `items` keyed by OBJ/OUT ID, `approvals`, `progress_notes` |
| requirement | `statement`, `classification`, `objectives[]`, `sources[]`, `acceptance[]`, `verification[]`, `supersedes[]` | `state`, `approvals`, `evidence`, `blockers`, `progress_notes` |
| milestone | `outcome`, `objectives[]`, `outcomes[]`, `requirements[]`, `depends_on[]`, `exit_criteria[]`, `verification[]`, `packages[]` (`id`, `outcome`, `include`, `exclude`) | `state`, `approvals`, `evidence`, `blockers`, `progress_notes` |
| task | `title`, `objective`, `rationale`, `milestone`, optional `package`, `requirements[]`, `include[]`, `exclude[]`, `depends_on[]`, `context[]`, `deliverables[]`, `acceptance[]`, `verification[]`, `approvals[]`, `priority`, `size` | `state`, `authorization[]`, `evidence`, `blockers`, `progress_notes` |
| decision | `topic`, `rationale`, `options[]`, `choice`, `targets[]`, `authority`, optional `delegation`, `supersedes[]` | `state`, `actor`, `decided_at`, `approval_source`, optional `applied_revision` |
| change | `idea`, `source`, `affected[]`, `impact`, `alternatives[]`, `proposed_delta`, `required_approvals[]`, optional `revisit_trigger` | `state`, `disposition_decision`, `applied_revision`, `blockers`, `progress_notes` |

`deliverables` entries are `{description, path?}`. `targets` entries are
`{record, scope_sha256}`. A delegation is `{covers, exclusions,
permitted_decisions, stop_conditions}`.

## State machines

- Strategy: `proposed` -> `approved` -> `superseded`.
- Objective/outcome items: `proposed` / `active` / `achieved` / `retired`.
- Requirement: `proposed` -> `approved` -> `retired`.
- Milestone: `proposed` -> `approved` -> `active` -> `achieved` -> `retired`.
  At most one milestone is `active` in v0.1.
- Task: `draft` -> `ready` -> `in_progress` -> `review` -> `done`, with
  `blocked` and `cancelled` branches carrying a reason.
- Decision: `proposed` / `accepted` / `rejected` / `superseded`.
- Change: `captured` -> `assessed` -> `approved` / `rejected` / `deferred` ->
  `applied`.

`ready` is a derived conjunction, not merely a word. See
`../../references/governance.md` and `operation-contracts.md`.

## Project configuration

`planning/planner.yaml` conforms to `../schemas/project.schema.json`. It holds
`project_id`, category, roles, content root, authority bindings, aliases,
current milestone index, task order or ordering policy, verification profiles
and review policy. It contains no copies of requirement text, task state,
estimates or roadmap outcomes.

A native collection authority is `{kind, owner, root}`. An explicit adopted
record is `{kind, id, owner, ref, locator?, format}` where format is `native`,
`markdown`, `openspec` or `issue`. Never map one concept to two authoritative
locations; duplicate mappings are errors, not last-writer-wins.

## Content-bound approvals

For native records, compute `scope_sha256` from the UTF-8 JSON serialization of
`scope` with sorted object keys, compact separators (`,` and `:`), and no ASCII
escaping. The same routine is used by the checker, tests and generated
examples. Approval entries on a record reference an accepted decision and its
digest. A decision's `targets` list names the same record and digest. Changing
any normative field invalidates the approval; changing only `execution`
(progress, evidence, blockers) does not.

Approval does not authenticate a human. A schema-valid `accepted` written by an
agent is not proof of consent. Review the actor and approval source, keep the
original provenance, and use Git review as the trust boundary.
