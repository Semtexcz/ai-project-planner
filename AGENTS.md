# Repository development instructions

These instructions apply to developing **AI Project Planner itself**. They are
not rendered into target projects and are not part of the installed overlay.

## Model policy

- Implementation, tests, reviews and repairs use **DeepSeek V4.1 Flash, HIGH**.
- **DeepSeek V4 Pro, HIGH**, is an escalation only for a concrete unresolved
  failure or architectural ambiguity after two bounded Flash attempts. Carry
  the failing evidence forward and return to Flash afterwards.
- Do not invoke OpenAI models and do not delegate coding, testing, reviews or
  repairs to them.
- Model labels in generated execution prompts are advisory. CI must never
  require credentials or make paid inference calls.

## Boundaries

- Keep the product a portable planning overlay. Do not add an execution
  launcher, scheduler, background service, database, dashboard, custom LLM
  client, model router or generic workflow engine.
- Never edit installed BMAD or OpenSpec skills. Use their native configuration
  and sparse project-owned customization.
- Copier may render only `templates/planner-overlay/template/.planner/**` and
  the planner answers file. Never render `planning/**`, `AGENTS.md`, `README`,
  application files or another overlay's paths.
- Never overwrite user-owned planning content. INIT creates records once and
  resumes without reseeding.
- Do not migrate the real DeepPlant, Bookvoice or PLOS repositories. Use
  synthetic fixtures in disposable temporary Git repositories.
- Do not push, tag, publish releases or modify external repositories without
  explicit human permission.

## Layout

- `templates/planner-overlay/template/.planner/` is the installed runtime:
  normative references, schemas, checker, blank assets and six skills.
- `docs/` explains the runtime and records evidence. Avoid duplicating
  normative runtime prose in repository docs; link to it.
- `tests/` contains offline deterministic checks and separately marked native
  integration checks.
- `planning/` in this repository is development example data only, never
  shipped by Copier.

## Verification

```bash
uv sync --locked
uv lock --check
uv run --locked pytest -m "not integration"
uv run --locked pytest -m integration          # native tools/network; separate
uv run --script templates/planner-overlay/template/.planner/scripts/check_planning.py \
  --project <project> --format text
```

`uv run --locked pytest -m "not integration"` must never select integration
tests. Native skill validation uses `npx --yes skills-ref@0.1.5 validate
<skill-dir>`; record the exact pinned version when evidence is captured.

## Change discipline

Work one bounded task at a time from
`docs/plans/implementation-v0.1.md`. Run the relevant tests after each change,
fix failures before moving on, and keep `CHANGELOG.md`, runtime references and
user documentation synchronized. Structural checks are not strategic proof;
label agent-assisted acceptance as such.
