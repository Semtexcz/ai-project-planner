# Changelog

All notable changes to AI Project Planner are documented here. The format is
based on Keep a Changelog; versions follow semantic versioning for the overlay.

## [Unreleased]

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
- Documented BMAD 6.12.4, Copier 9.19.1, Agent Skills and optional OpenSpec
  integration boundaries.
- Synthetic Bookvoice-like, DeepPlant-like and PLOS-like fixtures and
  migration/acceptance exercises performed in disposable repositories.
- Offline test suite plus separately marked native integration checks.

### Not included

- Autonomous execution, scheduling, web UI, database, model routing, release
  publication or migration of the reference repositories.
