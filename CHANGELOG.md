# Changelog

All notable changes to AI Project Planner are documented here. The format is
based on Keep a Changelog; versions follow semantic versioning for the overlay.

## [0.1.1] - 2026-11-15 (candidate, unpublished)

Hardening from live INIT → PLAN → NEXT acceptance runs and an existing-project
adoption trial. No release tag has been published.

### Added

- Copier-distributed planner overlay (`.planner/**` plus
  `.copier-planner-answers.yml`) with an explicit path allowlist.
- Six portable Agent Skills: INIT, STATUS, PLAN, NEXT, CHANGE and AUDIT.
- Native information model, JSON Schemas and blank project-owned assets.
- Read-only structural checker with JSON/text reports, content-bound approval
  verification, evidence checks, dependency-cycle detection and path-safety
  guards. Readiness is computed from the task's full objective/milestone/
  requirement/approval/dependency context; adopted or delegated work is
  reported separately as manual review rather than silently ready.
- Accepted-decision provenance and change-disposition binding checks, calendar
  date validation, alias-cycle diagnosis, gate-criterion matching and explicit
  `ready_tasks`/`review_required_tasks` separation.
- Read-only `scripts/preflight_planner_install.py`. It classifies a destination
  as fresh, an existing planner installation (use `copier update`), or a
  collision (unowned, foreign, partial or symlinked managed path). It never
  installs or mutates, and accepts local checkouts with arbitrary directory
  names while offering `--expected-source` for an exact check.
- Optional `sha256` on a task context entry. Normative local context is now
  content-fresh: a matching hash stays fresh across newer revisions, and a
  changed hash blocks readiness until re-review. Background context can no
  longer block readiness on revision distance alone.
- Adopted tasks are listed in `task_readiness` as `adopted` and
  `review_required`, so NEXT reports a complete blocker set instead of omitting
  work outside the native schema.
- Documented BMAD 6.12.4, Copier 9.19.1, Agent Skills and optional OpenSpec
  integration boundaries.
- Synthetic Bookvoice-like, DeepPlant-like and PLOS-like fixtures and
  migration/acceptance exercises performed in disposable repositories.
- Offline test suite plus separately marked native integration checks, including
  regression tests for the install preflight, native Copier collision behaviour,
  content-hash freshness, background context, adopted-context readiness and
  adopted-task visibility.

### Fixed

- A task could be deterministically ready while `current_milestone` pointed at
  an adopted milestone and a different native milestone was active.
  `CURRENT_MILESTONE_EXTERNAL` is now a project-wide readiness review item, so
  the ambiguous current-milestone authority yields `ready_tasks = []` and the
  affected task moves to `review_required_tasks`. Non-current adopted milestones
  and adopted-only projects keep their existing workflow.
- A task whose normative context pointed at an unparsed Markdown file inside a
  native authority collection could be reported deterministically ready. That
  manual finding now links into task readiness when the context is normative;
  background context remains non-blocking.
- An adopted record that reused a native or embedded ID produced `ID_COLLISION`
  but left the colliding native task deterministically ready. Identity collisions
  now block every ready task while the native record and its scope are preserved;
  the adopted placeholder never replaces it.
- Alias cycles, dangling aliases, a missing adopted source and an explicit native
  authority that does not produce the matching record were errors but did not
  block readiness. They are now project-wide readiness blockers like the other
  identity and authority conflicts.
- A task whose normative context pointed at an unparsed adopted authority could
  be reported deterministically ready. It is now `review_required`, matching the
  documented adopted-source trust boundary.
- A commit-based context revision was reported stale even when the referenced
  file was byte-identical. Content hashes now establish freshness; revision
  strings remain provenance.
- Adopted tasks were invisible to the readiness view; they are now explicitly
  listed as manual review.
- Documented the BMAD epics architecture/UX prerequisite for non-software
  projects and the derived deliverables/verification packet that replaces it
  without inventing software architecture.
- Clarified that project-authored `_bmad/custom/**` is separate operator setup,
  and that `planning/planner.yaml` does not exist during first INIT.
- Documented a one-slice promotion path for an adopted task: preserve IDs, keep
  the source as hashed context, remove only the promoted authority entries, and
  bind a new decision. Historical adoption decisions may show target drift; the
  model has no target-level supersession.
- Stated explicitly that a matching `scope_sha256` proves content identity, not
  consent, and is never cryptographic proof of approval.

### Not included

- Autonomous execution, scheduling, web UI, database, model routing, release
  publication or migration of the reference repositories.
