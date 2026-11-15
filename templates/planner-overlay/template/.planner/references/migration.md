# Migration and adoption (runtime reference)

Migration is a controlled INIT mode performed by the agent with maintained file
and Git tools. There is no repository-specific import engine, parser framework
or executable migration tool. Default to **adopting by reference**; normalize in
place or create native replacements only when that materially improves planning
and the human approves the exact patch.

Never run a migration against a reference checkout during development or tests.
Use synthetic fixtures in disposable temporary Git repositories. Live adoption
is a separate explicit human-approved operation.

## 1. Discover

Record repository identity, HEAD, dirty status, searched and excluded roots,
planning paths and unavailable sources. Read project instructions and existing
authority declarations before inferring an owner. Never read secrets or private
sources outside the authorized project.

## 2. Inventory information

For every requirement, task, milestone, decision and criterion, capture the ID,
source occurrence, lifecycle meaning, explicit blocking edges, related/context
links, criteria, history and evidence.

Preserve complete original text in its original committed location. An extract
cannot replace it. A manifest may hash source files but must not copy
confidential material outside the project.

## 3. Identify authority

Propose one owner and one location per concept. Distinguish current, historical,
derived, proposed and mandated material. Neither the newest timestamp nor the
most detailed document automatically wins. An issue URL is mutable; a dated
export plus content hash preserves what was reviewed, and a fresh read
establishes whether an approval still applies.

## 4. Map

Map original IDs and locators to planner semantics while preserving legacy IDs
and paths by default. Document every state mapping explicitly.

- `related` does not become `depends_on`.
- A backlog folder does not become `ready`.
- Closed/done is not verified completion.
- A historical gate remains historical.
- A mandate keeps its original approval provenance; a proposal remains proposed;
  a design decision is not blanket product approval; a hypothesis stays
  unvalidated.
- Do not renumber an ID because a native prefix would be prettier.

## 5. Find conflicts and duplicates

Compare frontmatter, body and folder state. Detect duplicate IDs, contradictory
requirements, disconnected objectives, undocumented dependencies, dependency
cycles, and proposed-versus-approved scope. Preserve all candidates until
adjudicated. Never auto-merge requirements by similar wording.

## 6. Write the dry-run report

The only permitted new artifacts in dry-run are an explicitly designated
`planning/runs/<run-id>/migration.md` and the proposed patch/manifest. Use
`assets/migration-report.md`. Make no source edits, moves, deletions, renames,
configuration changes or authority switches.

On a dirty reference checkout, return the report inline or use a disposable
copy; do not write into the reference checkout.

## 7. Request approval for the concrete result

The human separately approves source-authority choices, conflict resolutions,
state mappings, exact paths/patch and any new scope. Explain unresolved items.
Approval to migrate is not approval of proposed product requirements.

## 8. Apply on a dedicated branch or disposable worktree

Recheck HEAD and all source hashes against the approved report. Apply only the
reviewed patch. Abort on conflicts or staleness. Keep originals in place or mark
them explicitly historical; do not move or delete them as a convenience.

## 9. Verify losslessness and traceability

Compare before/after manifests. Every original requirement/task identity,
blocking edge, criterion, exclusion and decision is retained, explicitly mapped,
or retained unresolved with a reason. Verify dependency direction, evidence
links, file history and state mappings. Zero unexplained omissions is the gate.

## 10. Record provenance and review

Commit the approved migration separately, linking the report, approval and
original commit. Do not rebase, squash historical commits, use filter-repo or
rewrite the original repository's history. Git log/blame must still reach the
original artifacts. Re-running the same migration detects existing mappings and
creates no duplicates.

## State mapping examples

| Original meaning | Native state | Caution |
| --- | --- | --- |
| idea / backlog item | absent or `CHG-*`/draft task | A backlog folder is not ready. |
| proposal marked "N" | `proposed` | Never becomes approved by import. |
| mandate marked "Z" | approved with original provenance | Preserve the mandating decision. |
| design decision "D" | `DEC-*` or context requirement | Not blanket product approval. |
| hypothesis "H" | assumption/hypothesis field | Stays unvalidated. |
| task folder "done" | `done` only with reviewed evidence | Otherwise retain with an evidence gap. |
| historical gate | historical decision/context | Does not authorize current work. |
| directional capability | strategy context only | Never current authorization. |

## Reference-specific mapping

### Bookvoice-like

Preserve `docs/ROADMAP.md` direction; task cards in all state folders; backlog
index; `docs/TASK_SEQUENCE.md` ordering and explicit dependencies; task text,
criteria and exclusions; done evidence and dates.

Review frontmatter/body/folder mismatches, identical IDs in multiple locations,
sequence prerequisites versus merely related tasks, and path prerequisites as
artifact gates rather than fake task IDs. Retain the original selection policy
until approved otherwise.

### DeepPlant-like

Preserve `VISION.md`; strategy/product/roadmap distinctions; ADR and contract
boundaries; direction as context only; historical gate decisions; GitHub Issue
scope/revision if available.

Never turn a directional capability into authorization. Preserve semantic core,
semantic/presentation and process/physical boundaries. The current product
outcome is more authoritative than an attractive future capability. Missing
Issue access makes detailed-task coverage explicitly incomplete.

### PLOS-like

Preserve the charter; mandated principles; requirement IDs/statuses;
glossary/domain semantics; iteration dependencies and exit criteria; decision
log; semantic review evidence and its limits.

Z adopts explicit mandate provenance only. N remains proposed. D remains a design
decision. H stays a hypothesis. I3 is not active merely because I2 completed. Do
not import 36 domain concepts as planner entities and do not impose
software/storage on the methodology being planned.

PLOS *project development* can use Git records to plan changes to a
medium-independent methodology. That does not require users of the resulting
methodology to use records, tasks, software or a strategic goal for every daily
action.

## Rollback

Before commit: restore only reviewed migration-created/edited paths. After
commit: revert the isolated migration commit. A rollback never removes unrelated
work or canonical originals. A partially applied migration is not accepted;
retain the report and describe recovery.
