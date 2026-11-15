# Migration report template

Derived artifact proposed by INIT. It is not authority and does not itself
approve a migration, adoption or product requirement. Fill every section; an
unavailable source is an explicit gap, never a green result.

```markdown
# Migration / adoption report - <project> - <date>

## Scope and revision

- Destination repository and HEAD:
- Working-tree state (clean/dirty; dirty means no in-place apply):
- Source repositories/paths, commits/tags and dirty state:
- Authorized roots searched:
- Roots excluded and why:
- Unavailable/private sources:
- Requested outcome: adopt by reference | normalize in place | native replacement

## Artifact inventory

| Source path | Commit | Artifact type | IDs found | Authority candidate | Notes |
| --- | --- | --- | --- | --- | --- |

Every requirement, task, milestone, decision, criterion, dependency, evidence
entry and original ID must appear at least once. Preserve complete original
text in its committed location; this report is not a replacement.

## Authority table

| Concept | Current owner | Current location | Proposed authority | Format | Rationale |
| --- | --- | --- | --- | --- | --- |

Distinguish current, historical, derived, proposed and mandated material.
Explain why an existing authority is retained or, exceptionally, replaced.

## ID and state mapping

| Original ID | Original location | Original state/lifecycle | Target ID | Target location | Target state | Alias/legacy note |
| --- | --- | --- | --- | --- | --- | --- |

Rules:

- preserve original IDs and locations by default;
- `related` is not automatically `depends_on`;
- a backlog folder is not automatically ready;
- closed/done is not automatically verified completion;
- `proposed`, `hypothesis`, `mandate` and `approved` keep their distinct
  meanings and provenance;
- duplicate IDs remain conflicts until adjudicated.

## Dependency edge table

| Dependent | Prerequisite | Edge type (blocking/context/related) | Source evidence | Preserved target |
| --- | --- | --- | --- | --- |

Every original blocking edge must be retained, explicitly mapped or retained
unresolved with a reason.

## Conflicts, duplicates and contradictions

| Conflict | Occurrences | Impact | Proposed resolution | Needs human decision |
| --- | --- | --- | --- | --- |

Compare frontmatter, body, folder state and sequence/order documents. Do not
auto-merge requirements by similar wording.

## Unmapped and unknown information

| Item | Why unmapped | Risk | Proposed follow-up |
| --- | --- | --- | --- |

An empty table is valid only if every inventory item is accounted for in the
coverage reconciliation.

## Proposed new paths and exact patch

<Exact patch or file list with content; no source edits are included before approval.>

## Byte-preservation list

| Path | Commit | SHA-256 | Reason preserved |
| --- | --- | --- | --- |

## Approval requests

1. Authority choices:
2. Conflict resolutions:
3. State mappings:
4. Proposed paths/patch:
5. Any new product scope (separate approval):
6. Unresolved items accepted for follow-up:

Approval of migration is not approval of imported product requirements.

## Verification to run after apply

- [ ] Source hashes still match this report.
- [ ] `uv run --script .planner/scripts/check_planning.py --project . --format json`
- [ ] ID/occurrence/edge manifests reconcile exactly.
- [ ] Original files still reachable in Git history/blame.
- [ ] No unexplained omission of criteria, decisions, exclusions or evidence.
- [ ] Project's existing checks.

## Rollback

<Restore only reviewed migration-created/edited paths before commit; after commit use a revert of the isolated migration commit. Do not remove canonical originals or unrelated work.>

## Coverage reconciliation

| Original artifact/ID/edge | Preserved | Explicitly mapped | Unresolved with reason | Unexplained omission |
| --- | --- | --- | --- | --- |
| <counts and IDs> | | | | 0 |

Zero unexplained omissions is the gate. Partial application is not accepted.
```
