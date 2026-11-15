---
id: TASK-075
title: Cloud sync adapter
status: done
priority: P1
depends_on: [TASK-073, TASK-074, TASK-019, TASK-037]
related: [TASK-076]
artifact_gate: docs/contracts/sync-contract.md
---

# TASK-075 - Cloud sync adapter

**Folder state:** ready
**Body state:** in progress
**Frontmatter state:** done

This deliberate three-way mismatch is the duplicate conflict under review.

## Deliverables

- A sync adapter behind the existing storage interface.
- A user-visible conflict report.

## Acceptance criteria

- TASK-075:AC-1 - A sync round trip preserves local content when the remote is
  unavailable.
- TASK-075:AC-2 - A conflict produces a visible report and does not silently
  choose a winner.

## Exclusions

- No background scheduler.
- No automatic account creation.

## Verification

Integration scenario with a simulated unavailable remote, reviewed by the
storage owner.

## Evidence

Manual simulation on 2026-10-02. No automated test was run.
