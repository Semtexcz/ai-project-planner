# Architecture and boundaries

AI Project Planner is a portable planning overlay for Git repositories. It
turns purpose into approved, verifiable work and feeds evidence back into
strategy. It is not an execution system, scheduler, dashboard, database or
LLM client.

## Forward chain

```text
vision and strategic choices
  -> objectives and expected outcomes
  -> requirements
  -> outcome-based milestones
  -> optional work packages
  -> approved tasks
  -> derived execution prompts
  -> deliverables and verification evidence
```

Evidence, failed verification, changed assumptions and new ideas flow back
through CHANGE and PLAN. AUDIT tests traceability in both directions. A count
of completed tasks never proves an outcome.

## Components and ownership

| Component | Owner | Boundary |
| --- | --- | --- |
| `.planner/**` | this overlay, managed by Copier | policy, six skills, schemas, checker, blank assets; never project truth |
| `.copier-planner-answers.yml` | Copier lineage | commit it; never hand-edit |
| `planning/**` | the target project | created by INIT, never rendered or deleted by Copier |
| `_bmad/**`, `bmad-*` skills | BMAD native installer | separate install/update transaction |
| `openspec/**` and generated skills | OpenSpec native CLI | optional existing specification authority |
| `AGENTS.md`, README, app manifests, CI, other overlays | existing project owners | planner never writes them |

Copier renders only `.planner/**` and `.copier-planner-answers.yml`. This is
enforced by `_subdirectory` and by tests. Project records are created once by
INIT from reviewed content, so an overlay update cannot delete, recreate or
merge user-owned plans.

## Six bounded operations

`planner-init`, `planner-status`, `planner-plan`, `planner-next`,
`planner-change` and `planner-audit` are explicit Agent Skills. There is no
command router, background process, autonomous loop or execution launcher.
Every operation reads project instructions, governance, the authority map and
only relevant records, then returns a bounded result with a completion
envelope.

The deterministic checker `check_planning.py` is read-only. It validates
records and references, duplicate IDs, dependency cycles, approval digests and
evidence fields. It does not choose work, mutate state, run verification
commands, interpret arbitrary project formats or make strategic judgments.
Unsupported external sources are reported as manual review.

## Upstream reuse

- BMAD METHOD 6.12.4, installed with its official npm installer, owns
  elicitation, requirements/PRD development, decomposition, readiness and
  course correction. Planner configures it sparsely and never edits installed
  skills.
- Copier 9.19.1 owns overlay lineage, updates and native conflict handling.
- Agent Skills format owns portable packaging. Explicit file invocation is the
  baseline; optional discovery links are project-owned.
- OpenSpec is optional and remains authoritative where a project already uses
  it. Planner references native requirement sections rather than creating a
  second specification or task state.
- Git, Markdown and YAML frontmatter own project truth.

## Non-goals for v0.1

Autonomous execution, multi-agent orchestration, scheduling, databases, web
dashboards, custom LLM clients, model routing, generic workflow engines, PM
servers, app scaffolding and replacements for BMAD/OpenSpec. No programming
language or application stack is imposed on target projects.

The implementation also does not authenticate human identity, parse every
external framework, or convert an agent-generated `final` status, Git commit or
checked box into Product Owner approval.

## Verification layers

1. Deterministic offline checks: schemas, references, approvals, cycles,
   template output allowlists, fixture preservation, disposable Git/Copier
   lifecycle.
2. Native integration: pinned BMAD installer/resolver, Agent Skills validator,
   optional OpenSpec native validation.
3. Agent-assisted acceptance: bounded recorded sessions assessed against
   human rubrics. These are never presented as deterministic proof or run in
   CI.

See `docs/verification.md` and `docs/acceptance-v0.1.md`.
