# Native BMAD adaptation (runtime reference)

BMAD METHOD 6.12.4 owns elicitation, requirements/PRD development,
decomposition, readiness and course correction. Planner adds authority,
approval, outcome and traceability policy. Planner never edits installed BMAD
skills and never vendors or forks BMAD.

Pin the stable v6.12 line. Do not follow the v7 preview, install `@latest`
implicitly, or enable legacy shims as a dependency.

## 1. Install or reuse

Inspect an existing installation and its version first. Reuse a compatible one;
never copy another project's `_bmad/` directory.

```bash
npx --yes bmad-method@6.12.4 install --help
npx --yes bmad-method@6.12.4 install --list-tools
npx --yes bmad-method@6.12.4 install
```

The interactive install is the documented route: select the BMM module and the
harness the project actually uses. Do not select Automator, preview modules or
execution add-ons as part of planner setup.

For an isolated, non-interactive installation (CI or a disposable test), the
exact flags verified in I01 are:

```bash
npx --yes bmad-method@6.12.4 install --yes \
  --modules bmm --tools opencode \
  --set core.output_folder=planning/runs/bmad \
  --set bmm.planning_artifacts=planning/runs/bmad/planning-artifacts \
  --set bmm.implementation_artifacts=planning/runs/bmad/implementation-artifacts \
  --set bmm.project_knowledge=planning/runs/bmad/project-knowledge
```

Keep every BMAD-writable path below `planning/runs/bmad/`. If the project
already configured `project_knowledge` to an existing read-only knowledge root,
register that choice rather than overwriting it; do not let planner installation
silently redirect or mutate project docs.

Substitute a tool ID from `--list-tools`, not a guessed one. With `opencode`,
BMAD writes skills to `.agents/skills/bmad-*` and commands to
`.opencode/commands`, plus `_bmad/` scripts/config. With another harness the
target directory differs; `--list-tools` is authoritative.

Installed inventory includes execution skills such as `bmad-build`,
`bmad-build-auto` and `bmad-agent-dev`. Their presence does not authorize
planner to invoke them. Planner also does not invoke party mode or autonomous
flows.

### Update/reinstall

Use the native action, for example `install --action update`, and pass the same
`--set` values again. In the I01 fixture an `--yes` update preserved
project-authored `_bmad/custom/**` and project files but did not preserve the
exact previous `--set` scalar values; the resolver returned a normalized path.
Verify the resolved values after every update:

```bash
uv run _bmad/scripts/resolve_config.py --project-root . \
  --key modules.bmm.planning_artifacts \
  --key modules.bmm.implementation_artifacts \
  --key modules.bmm.project_knowledge \
  --key core.output_folder
```

Project-authored `_bmad/custom/config.toml`,
`_bmad/custom/config.user.toml` and `_bmad/custom/<skill>.toml` are never
installer-owned. Never hand-edit `_bmad/config.toml`.

## 2. Sparse project customization

Project overrides live in:

```text
_bmad/custom/bmad-product-brief.toml
_bmad/custom/bmad-prd.toml
_bmad/custom/bmad-create-epics-and-stories.toml
_bmad/custom/bmad-sprint-planning.toml
_bmad/custom/bmad-correct-course.toml
```

Read existing customization first and append a reviewed minimal patch. Do not
replace it wholesale or copy the upstream customization template.

Merge rules (verified with the native resolver):

- scalars override the skill default;
- arrays append to inherited entries;
- an empty array `[]` does **not** erase inherited entries;
- there is no general removal operation.

Example `_bmad/custom/bmad-prd.toml`:

```toml
# Project-owned. Never installed or overwritten by BMAD or planner.
[workflow]
persistent_facts = [
  "PLANNER: Treat file:{project-root}/.planner/references/governance.md as normative operation policy.",
  "PLANNER: Read file:{project-root}/planning/planner.yaml as the authority map when it exists; during first INIT it does not exist yet, so use the discovered authority summary and never infer or overwrite authority.",
  "PLANNER: Use one agent only. Do not spawn research, review or other subagents and do not make paid delegated model calls.",
  "PLANNER: Produce planning drafts only. Do not execute build/dev/apply workflows, publish, or write external trackers.",
  "PLANNER: Stop after the bounded planning result; do not continue into implementation.",
  "PLANNER: Use the project's category and domain vocabulary; do not force software artifacts onto non-software deliverables.",
  "PLANNER: Never mark requirements, milestones or tasks approved. Approval is a separate human decision recorded by planner.",
]
```

Apply the same facts to the other four skills. For `bmad-correct-course`, add a
fact to present a proposal and stop before applying a change. For
`bmad-sprint-planning`, add a fact that only readiness assessment is wanted and
no sprint tracking file may be created.

Use `activation_steps_prepend` / `activation_steps_append` only for further
prose instructions. Do not use them to run shell commands or mutate project
content. Leave `on_complete` empty.

`doc_standards` and `finalize_reviewers` default arrays cannot be removed.
BMAD PRD may therefore offer review subagents or editorial review at Finalize.
The invoking agent must decline optional reviewer/subagent gates (and may run a
sequential, single-agent review when the user explicitly asks). This is a
documented upstream limitation, not a reason to fork BMAD.

Verify merged values:

```bash
uv run _bmad/scripts/resolve_customization.py \
  --skill .agents/skills/bmad-prd --project-root . \
  --key workflow.persistent_facts \
  --key workflow.doc_standards
```

The output must show the planner facts and the inherited defaults. An error
means the customized skill is incompatible: report it and do not substitute a
custom planning workflow.

## 3. Operation recipes

Before any BMAD call, read `.planner/references/governance.md`,
`planning/planner.yaml`, relevant approved records and the installed skill's
`SKILL.md`. Give the skill a bounded focus, the applicable domain category, and
the output run directory. Do not let it roam over unrelated authorities.

### INIT discovery: product brief and PRD

```text
Read .agents/skills/bmad-product-brief/SKILL.md and run Create intent for this
project. Use one agent, no subagents, no external publishing, no execution.
The bounded input is <project intention and discovered authority summary>.
Write only under planning/runs/bmad/planning-artifacts/. Return draft content
and source provenance; do not mark anything approved.
```

Use `bmad-prd` Create/Update only when requirements need development. Both
outputs are drafts. INIT creates native `planning/**` records only from reviewed
content and explicit human approval.

### PLAN: requirements and decomposition

```text
Read .agents/skills/bmad-prd/SKILL.md and run Update/Validate intent for the
approved current milestone only. Use one agent, no subagents, no publishing,
no execution. Distant milestones are outcome-only. Do not create sprint
tracking. Treat the result as a draft proposal.
```

```text
Read .agents/skills/bmad-create-epics-and-stories/SKILL.md and decompose only
the approved current milestone. Use the approved requirement IDs and the
project's domain deliverables. Do not invent requirements, architecture or
software artifacts. Stop after the decomposition proposal.
```

Translate the result through planner's canonical task contract: epics may
suggest work packages, stories may suggest tasks. Preserve real deliverables,
requirement references and dependencies. Do not force a software
architecture/UX document when no deliverable depends on one.

`bmad-create-epics-and-stories` step 1 expects a PRD, an architecture document
and, when UI exists, a UX contract. Non-software projects have neither
architecture nor UX by design. Do not fabricate them. Prepare a derived packet
under `planning/runs/<run-id>/inputs/` that states why those inputs do not exist
and supplies the deliverable and verification design the decomposition actually
needs, marked `DERIVED INPUT - NOT AUTHORITATIVE`. Record the substitution as a
compatibility observation. If the decomposition cannot proceed without a real
architecture document, report the gap instead of inventing one.

### Readiness-only gate

```text
Read .agents/skills/bmad-sprint-planning/SKILL.md and perform readiness
assessment only for <bounded set of draft tasks>. Do not create or update a
sprint status file and do not start execution. Report readiness gaps.
```

Planner applies its own approval, traceability and outcome gates in addition to
native readiness. Do not create a second `sprint-status.yaml` beside canonical
task records. If an existing BMAD tracking file is the project's adopted task
authority, read it directly; otherwise read native tasks.

### CHANGE: course correction

```text
Read .agents/skills/bmad-correct-course/SKILL.md and assess this bounded change
against <PRD/epic inputs or a faithful derived packet>. Use one agent, no
subagents, no publishing, no execution. Present alternatives and an exact
proposal; stop before applying it.
```

If the required PRD/epic input does not exist and cannot be faithfully derived,
use `bmad-prd` Update on the relevant requirement proposal instead. Do not
pretend correct-course works without its inputs.

## 4. Derived input packets

When BMAD expects a PRD/epic shape the project does not maintain, create a
derived packet under the run directory:

```text
planning/runs/<run-id>/inputs/
  manifest.md          source paths, revisions, hashes, coverage and gaps
  requirements.md      faithful excerpts with stable IDs and source locators
  notice.md            DERIVED INPUT - NOT AUTHORITATIVE
```

It contains faithful excerpts, stable IDs, source locations, revisions and an
explicit non-authoritative notice. Missing requirements remain questions, never
fabricated input. This is document preparation, not a parser or specification
engine.

## 5. Promotion and provenance

BMAD output is draft or derived unless a human explicitly adopts it. Never keep
two active texts claiming the same scope. On promotion either:

- deliberately adopt the BMAD artifact as the owner and register it in the
  authority map, or
- apply an approved exact patch to the existing authority and mark the run
  output historical with links to the real owner.

BMAD memlogs and addenda remain workshop provenance. Planner decisions own
consequential authorization and link to that provenance; do not duplicate every
coaching exchange.

BMAD `status: final`, a completed run, a Git commit or a merged implementation
are not Product Owner approval.

## 6. Optional OpenSpec coexistence

Do not initialize or upgrade OpenSpec automatically. Reuse the installed
version and native validation. Planner references canonical requirement
sections and checklist items; it does not create a second state list or parse
OpenSpec itself.

Verified native paths for the two inspected baselines (`--tools opencode`):

| Version | Generated integration | Native validation |
| --- | --- | --- |
| 1.16.0 | `.opencode/skills/openspec-*`, `.opencode/commands/opsx-*` | `npx --yes @fission-ai/openspec@1.16.0 validate --changes --strict --no-interactive` (and `--specs`) |
| 2.0.0 | `.agents/skills/openspec-*` | `npx --yes @fission-ai/openspec@2.0.0 validate --changes --strict --no-interactive` (and `--specs`) |

Both expose skills named `openspec-propose`, `openspec-apply-change`,
`openspec-archive-change`, `openspec-explore`, `openspec-sync-specs` and
`openspec-update-change`. Planner may read/propose/update requirements through
the native workflow and run read-only `validate`. It never invokes apply or
archive automatically and never upgrades OpenSpec as a side effect. OpenSpec
validation proves format/consistency within OpenSpec's scope, not strategic
approval or milestone achievement.

If a version or generated path differs, record it in
`docs/upstream-compatibility.md` and treat unsupported versions as an explicit
compatibility gap rather than guessing an invocation.
