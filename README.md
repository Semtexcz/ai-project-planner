# AI Project Planner

A portable, Git-native **project and product planning overlay**. It turns
purpose into approved, verifiable work and feeds evidence back into strategy.
It works for software, engineering research/specification and methodology
development, and it stays useful when execution happens manually, in another
agent, or outside software entirely.

This repository contains the planner overlay only. It is not an execution
system, scheduler, dashboard, database, project-management server or LLM
client.

## What it provides

- Six bounded Agent Skills: `planner-init`, `planner-status`, `planner-plan`,
  `planner-next`, `planner-change`, `planner-audit`.
- A strict native record model with content-bound approvals and evidence.
- A read-only structural checker.
- A Copier overlay that renders only `.planner/**` and its own answers file,
  so project-owned `planning/**` records are never re-rendered or deleted.
- Sparse configuration for BMAD 6.12.4 planning skills, with optional OpenSpec
  coexistence.

## Status

Implementation of the v0.1 plan plus the v0.1.1 hardening pass is present in
this repository. Verification evidence, including unverified capabilities and
platform limits, is recorded in
[`docs/acceptance-v0.1.md`](docs/acceptance-v0.1.md) and
[`docs/acceptance-v0.1.1.md`](docs/acceptance-v0.1.1.md). No release tag has been
published; installation from a tag requires a human to publish that tag first.

## Prerequisites

- Linux x86-64 is the verified platform for v0.1.
- Git.
- Python 3.11+ and [uv](https://docs.astral.sh/uv/) for the isolated checker.
- Node.js/npm only when using native BMAD or optional OpenSpec integration.
- A harness that can read an explicit `SKILL.md` path. Discovery is optional.

## Install the overlay

Review the template source and destination first. Replace `<project>` with the
target directory and `v0.1.1` with a tag a human has actually published.

Before any copy, run the read-only preflight. It stops on an existing `.planner/`
or answers file that is not confirmed planner-owned:

```bash
# From a local checkout of the planner repository:
uv run --script scripts/preflight_planner_install.py --destination <project>

# Without a checkout, a basic existence check (it cannot distinguish owners):
test ! -e <project>/.planner && test ! -e <project>/.copier-planner-answers.yml
```

Exit `0` is a fresh destination; `1` means a planner installation already exists
and must be updated, not copied; `2` means an unowned, foreign, partial or
symlinked collision and you must stop; `3` is an invalid destination or
invocation. Then preview and copy:

```bash
uvx copier==9.19.1 copy --pretend \
  --answers-file .copier-planner-answers.yml \
  --vcs-ref v0.1.1 gh:Semtexcz/ai-project-planner "<project>"

uvx copier==9.19.1 copy \
  --answers-file .copier-planner-answers.yml \
  --vcs-ref v0.1.1 gh:Semtexcz/ai-project-planner "<project>"
```

For a local checkout used during development, pass the repository path instead
of the GitHub source:

```bash
uvx copier==9.19.1 copy --pretend --defaults \
  --answers-file .copier-planner-answers.yml \
  . "<project>"
```

A local checkout with an arbitrary directory name is accepted by the preflight;
pass `--expected-source <path-or-url>` when the exact source must match.

`--pretend` previews native Copier actions. It is not a security boundary.
Never pass `--overwrite` or `--force` when `.planner/` or
`.copier-planner-answers.yml` already exists. Native Copier 9.19.1 refuses a
conflicting file without those flags, but a refused copy can still leave a
partial destination; that is why the preflight comes first. With `--overwrite`
Copier replaces matching managed files, so that flag is prohibited on an
existing unowned path.

A new empty target may receive the copy before its first commit. Initialize
Git and commit the reviewed overlay before attempting upgrades. Existing
targets require a clean committed tree for install/update.

## First use

Activate INIT explicitly; no harness configuration is required:

> Read `.planner/skills/planner-init/SKILL.md` and carry out INIT for this
> project. Follow the existing project instructions and retain all existing
> content authorities.

INIT inspects the repository, proposes an authority map and a strategy
baseline, and creates project-owned files under `planning/` only after the
relevant scope is explicitly approved. It never overwrites an existing path,
and repeating INIT resumes rather than reseeding.

For later operations, substitute the skill path:

```text
.planner/skills/planner-status/SKILL.md
.planner/skills/planner-plan/SKILL.md
.planner/skills/planner-next/SKILL.md
.planner/skills/planner-change/SKILL.md
.planner/skills/planner-audit/SKILL.md
```

Optional native discovery is project-owned convenience only. Do not edit root
`AGENTS.md`, shared configuration or global agent settings to add it. Updates
do not recreate project-owned links.

## Check planning structure

```bash
uv run --script .planner/scripts/check_planning.py --project . --format text
uv run --script .planner/scripts/check_planning.py --project . --format json
```

Exit `0` means deterministic checks completed without errors. It does not mean
the plan is strategically sound. Exit `1` means a structural/approval invariant
failed. Exit `2` means unreadable configuration, an unsupported schema or an
invalid invocation. Manual-review gaps are printed in every mode.

## Approval is content identity, not consent

A matching `scope_sha256` proves that the approved content is byte-identical to
the content being checked. It does **not** prove who approved it, that a human
approved it, or that the approval was informed. The checker reports
`APPROVAL_IDENTITY_UNVERIFIED` as a manual-review item; Git review, human
process and repository access control are the trust boundary. Never describe a
digest match as cryptographic proof of consent.

## Native BMAD planning

BMAD is installed separately with its official installer when a BMAD-backed
operation is first needed:

```bash
npx --yes bmad-method@6.12.4 install --list-tools
npx --yes bmad-method@6.12.4 install
```

Select the BMM module and the harness you actually use. Do not install v7
preview, Automator, or execution modules as part of planner setup. Configure
BMAD's `planning_artifacts` below `planning/runs/bmad/` through native settings,
and add sparse project overrides under `_bmad/custom/` as documented in
[`.planner/references/bmad-adapter.md`](templates/planner-overlay/template/.planner/references/bmad-adapter.md).
Installed BMAD skills are never edited by planner.

If BMAD is unavailable, INIT discovery, STATUS, NEXT for already sufficient
tasks and structural AUDIT still work. BMAD-dependent PLAN/CHANGE drafting
reports the missing dependency instead of replacing BMAD with a custom
workflow.

## Update the overlay

Run from the target repository with a clean committed tree and a reviewed tag:

```bash
uvx copier==9.19.1 update --answers-file .copier-planner-answers.yml \
  --vcs-ref <planner-tag> --pretend .

uvx copier==9.19.1 update --answers-file .copier-planner-answers.yml \
  --vcs-ref <planner-tag> .
```

Always pass the planner answers file. Never rely on Copier's default answers
file, which may belong to another overlay. Review diffs and unmerged paths, run
planner checks and the project's own checks, then commit the planner-only
update separately. Resolve managed-file conflicts visibly; do not take one side
automatically.

Rollback is a Git revert of the isolated planner update commit. Do not
hand-edit `_commit`, downgrade another overlay, run `git clean -fd` or rewrite
history.

See [`docs/install-update.md`](docs/install-update.md) for details and
[`docs/operations.md`](docs/operations.md) for the six operations.

## Repository layout

```text
copier.yml
templates/planner-overlay/template/.planner/   installed runtime
scripts/preflight_planner_install.py           read-only install/update preflight
docs/                                          architecture, operations, evidence
tests/                                         offline + integration checks
```

## Development

```bash
uv sync --locked
uv lock --check
uv run --locked pytest -m "not integration"
uv run --locked pytest -m integration
```

## License

MIT. Upstream tools remain the property of their authors; no upstream source is
vendored here.
