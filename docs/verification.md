# Verification

Verification has three layers. They must not be conflated.

1. **Deterministic offline checks** (default): schemas, references, approvals,
   dependency cycles, template output allowlists, fixture preservation,
   disposable Git/Copier lifecycle. No model or paid inference.
2. **Native integration checks** (`-m integration`): exact pinned BMAD
   installer/resolver, Agent Skills validator, optional OpenSpec init/validate
   and overlay compatibility. These use disposable directories and may need
   package registries or network access. A network failure is reported as
   such, not as a product pass.
3. **Agent-assisted acceptance**: bounded DeepSeek V4.1 Flash HIGH sessions
   recorded against a human rubric. These establish behaviour that a file
   search cannot: no invented requirements, useful decomposition, honoring
   stops, strategic coherence and non-software fitness. They are not
   deterministic proof and never run in CI.

## Commands

```bash
uv sync --locked
uv lock --check
uv run --locked pytest -m "not integration"
uv run --locked pytest -m integration
```

The offline command never selects integration tests. The integration marker is
registered in `pyproject.toml`.

The deployed structural checker is a single read-only script with PEP 723
dependencies pinned to the tested versions:

```bash
uv run --script .planner/scripts/check_planning.py --project . --format text
uv run --script .planner/scripts/check_planning.py --project . --format json
uv run --script .planner/scripts/check_planning.py --project . \
  --source-revision "$(git rev-parse HEAD)" --format json
```

`--source-revision` is optional. When supplied, evidence whose
`subject_revision` differs and is not `working-tree` is reported as stale; this
is a warning, not proof that the evidence is ineffective.

A human or agent invokes the checker. No updater hook, installer task or
planning operation runs it implicitly.

## Exit semantics

| Exit | Meaning |
| --- | --- |
| `0` | Deterministic checks completed without errors. Manual-review gaps are still printed. This is not a strategic PASS. |
| `1` | A proven structural or approval invariant failed. |
| `2` | Unreadable configuration, unsupported schema or invalid invocation. |

`report_version: 1` JSON includes a checker version, project identity, result
counts, coverage and findings. Each finding has `rule`, `severity`, `locator`
and `message`. Severities are `error`, `warning` and `manual_review`.

## What the checker validates

- Safe YAML frontmatter loading with duplicate-key rejection.
- JSON Schema 2020-12 validation for `schema_version: 1` project and record
  documents; unsupported versions produce a specific diagnostic.
- Global uniqueness for native IDs, embedded OBJ/OUT IDs, adopted IDs, aliases
  and evidence IDs.
- Authority ownership: native records must live under a configured matching
  authority; duplicate and overlapping authority roots are errors.
- Reference existence and expected type for requirements, objectives,
  outcomes, milestones, packages, decisions, changes, approvals and aliases.
- Exactly one parent milestone per task and valid work-package membership.
- At most one active milestone, agreement with `current_milestone`, and
  `task_order` references.
- Dependency existence, task/milestone prerequisite state, gate evidence and
  cycles (including self-dependencies).
- At least one verification mapping per acceptance/exit criterion, and no
  references to unknown criteria.
- Content-bound approvals: accepted decision, actor/calendar date/source
  present, decision target binding to the exact current `scope_sha256`, stale
  digests, superseded/unaccepted decisions and bounded delegation references.
  Strategy, requirement and milestone approval references live in
  `execution.approvals`; task approval references live in `scope.approvals`,
  matching the approved field grouping.
- Evidence fields, known criteria, observation date, pass/fail/inconclusive
  results, reviewer, limitations and optional stale subject revision.
- Achieved milestones and done tasks cannot rest on failing or missing
  evidence.
- Missing context files, traversal outside the project root, symlinked record
  paths and unsafe authority roots. Normative local context with a recorded
  `sha256` is fresh when the content still matches, even at a newer repository
  revision; a changed hash is an error. Background context is non-normative and
  cannot block readiness on revision distance alone.
- Explicit adopted records and unparsed Markdown are counted and reported for
  manual review, never treated as silently verified. A normative context entry
  that points at a configured adopted authority links that manual finding into
  the task's readiness, so the task becomes `review_required` instead of
  deterministically ready.
- Placeholder `-000` records and placeholder configuration are flagged; a
  placeholder cannot be approved, active or ready.
- Readiness is a per-task conjunction over the task, its objective/strategy,
  parent milestone, cited requirements, approvals, decisions and dependencies.
  Repository-level errors (duplicate IDs/authorities, cycles, multiple active
  milestones, broken task order) block every ready task. `ready_tasks` contains
  only deterministic native readiness; `review_required_tasks` separately lists
  tasks whose adopted/external or delegated authorization needs human review,
  including adopted tasks that have no native record at all (state `adopted`).
  Adopted-only projects therefore require a human freshness/authority
  confirmation or a bounded native promotion before NEXT emits an executable
  prompt.

## What it deliberately does not do

- Authenticate a human identity or prove consent. It verifies a recorded
  binding; Git review and human process supply the trust boundary.
- Prove semantic contradictions, strategic relevance, requirement quality,
  source freshness or that a verification method was appropriate or actually
  executed.
- Choose or rank work, generate prompts or plans, mutate states, write files,
  run commands, contact a model or parse arbitrary external frameworks.
- Treat a schema pass, checked box, Git commit or agent-written `final` as
  approval or outcome achievement.

Those gaps appear as `manual_review` findings and are the AUDIT/agent review
scope.

## Install safety checks

The offline suite covers the distribution boundary separately from the runtime
checker:

- `scripts/preflight_planner_install.py` is read-only and classifies a
  destination as fresh, existing planner installation, or collision. It refuses
  an unowned `.planner/`, a foreign overlay answers file, a partial installation
  and a symlinked managed path.
- Native Copier 9.19.1 is exercised against a colliding managed file without
  `--overwrite`: the copy exits non-zero and the conflicting bytes are
  preserved. A refused copy can still leave partial state, so the preflight is
  mandatory and is not a substitute for reading the diff.
- The template still contains no `_tasks`, `_migrations` or unsafe Jinja
  extensions. The preflight is not a wrapper, hook or install-time command.

## Skill format validation

`SKILL.md` directories are validated with the native Agent Skills reference
validator, pinned during I01:

```bash
npx --yes skills-ref@0.1.5 validate .planner/skills/planner-init
```

It checks name/directory agreement, required frontmatter and format. It does
not judge planning quality. Tests run it only under `-m integration`.

## Fixtures

All migration and domain fixtures are synthetic and live under `tests/fixtures`.
Temporary Git repositories are created in pytest temp directories. The real
DeepPlant, Bookvoice and PLOS repositories are never test destinations and must
remain unchanged.
