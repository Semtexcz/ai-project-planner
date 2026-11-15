# Migration and adoption

The normative procedure is
[`references/migration.md`](../templates/planner-overlay/template/.planner/references/migration.md);
the report format is
[`assets/migration-report.md`](../templates/planner-overlay/template/.planner/assets/migration-report.md).
This page records how the repository exercises migration without touching real
projects.

## Principle

Migration is a controlled INIT mode performed by an agent with native file and
Git tools. It is not an import engine. Default to adopting existing artifacts by
reference. Normalize in place or create native records only when that materially
improves planning and a human approves the exact patch.

## Procedure summary

1. Discover repository identity, HEAD, dirty state, searched/excluded roots and
   unavailable sources.
2. Inventory every requirement/task/decision ID, occurrence, state, criterion,
   blocking edge, related link and evidence limit, preserving original text.
3. Propose one authority and one location per concept; distinguish current,
   historical, derived, proposed and mandated material.
4. Map IDs and states without renumbering; `related` is not `depends_on`, a
   backlog folder is not ready and done is not verified completion.
5. Report conflicts and duplicates; preserve candidates until adjudicated.
6. Write only a designated dry-run report and proposed patch. No source edits.
7. Obtain separate approval for authority, conflicts, mappings, paths and any
   new scope.
8. Apply on a dedicated branch/worktree after rechecking source hashes.
9. Reconcile before/after manifests with zero unexplained omissions.
10. Commit separately with provenance; re-running is idempotent.

## Reference profiles

Synthetic fixtures reproduce the observed structures without private source:

| Fixture | What it proves |
| --- | --- |
| `tests/fixtures/bookvoice-like/` | task folders, duplicate `TASK-075` occurrences, four blocking prerequisites, related-only link, artifact gate, backlog not ready, evidence limits |
| `tests/fixtures/deepplant-like/` | vision/strategy/product/roadmap separation, semantic-core ADR, process/physical constraint, historical gate, future direction not authorization, unavailable issue detail |
| `tests/fixtures/plos-like/` | Z mandate versus N proposal, D design decision, H hypothesis, I2 complete versus I3 not active, semantic review evidence limits, medium independence |

Tests copy each fixture into a temporary Git repository, snapshot bytes, create
only permissible report/adoption files, rerun, and roll back. The real
DeepPlant, Bookvoice and PLOS repositories are never destinations.

## What is not implemented

- No generic OpenSpec/GitHub/Bookvoice importer.
- No automatic merge of similar requirements or duplicate IDs.
- No external tracker writes.
- No migration of the reference repositories; that remains a separate
  human-approved operation.
- Agent-assisted dry-run quality on the fixtures is not a deterministic test.
  See `docs/acceptance-v0.1.md` for the evidence status.
