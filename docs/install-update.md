# Install, update and rollback

The planner is a Copier overlay. It renders only two managed surfaces:

```text
.planner/**                    reusable capability (references, schemas, checker, assets, skills)
.copier-planner-answers.yml    Copier lineage for this overlay
```

It never renders `planning/**`, `AGENTS.md`, `README.md`, application files,
`_bmad/**`, `openspec/**`, `.copier-answers.yml` (another overlay) or CI.

## Prerequisites

- Verified platform for v0.1: Linux x86-64.
- Git, Python 3.11+ and `uv` for the checker.
- Copier 9.19.1 (the tested baseline), invoked with `uvx copier==9.19.1`.
- Node.js/npm only for native BMAD or optional OpenSpec integration.

## Preflight (mandatory)

Run from the target project. This is the ownership check; `--pretend` is only a
native-action preview, not a security boundary.

```bash
test ! -e .planner && test ! -e .copier-planner-answers.yml \
  || { echo "STOP: .planner or planner answers already exists; inspect its owner"; exit 1; }
git status --short
```

If either path exists, stop. Do not assume a matching filename means planner
owns it. Do not use `--force` or `--overwrite` on an existing `.planner/` or
planner answers file of unknown origin. An existing `.planner/` may belong to a
different capability overlay or to hand-written work.

The destination must either be a new empty project or an existing project with
a clean committed tree. Read-only discovery is possible on a dirty tree; an
actual copy/update is not.

## Install

Review the template and destination first:

```bash
uvx copier==9.19.1 copy --pretend \
  --answers-file .copier-planner-answers.yml \
  --vcs-ref v0.1.0 gh:Semtexcz/ai-project-planner .

uvx copier==9.19.1 copy \
  --answers-file .copier-planner-answers.yml \
  --vcs-ref v0.1.0 gh:Semtexcz/ai-project-planner .
```

`v0.1.0` must be a tag a human has published. For a local development checkout,
replace the GitHub source with the repository path. Local templates are copied
without a tag unless `--vcs-ref` names one; the answers file records the
resolved `_src_path` and `_commit`.

Then:

```bash
git add .planner .copier-planner-answers.yml
git commit -m "chore: install planner overlay v0.1.0"
```

Commit the reviewed overlay before any update attempt.

## First use

INIT is explicit and needs no host configuration:

> Read `.planner/skills/planner-init/SKILL.md` and carry out INIT for this
> project. Follow the existing project instructions and retain all existing
> content authorities.

INIT creates `planning/**` only after the relevant scope is explicitly
approved. It never overwrites an existing path and repeating it resumes.

Optional discovery: a human may configure a supported harness's additional
skill directory, or create six project-owned links in a directory with no
ownership conflict. Links must resolve to the canonical skill directories so
relative references work. Do not edit root `AGENTS.md`, shared configuration or
global agent settings. Updates never recreate project-owned links.

## Update

Run from the target repository with a clean committed tree and a reviewed tag:

```bash
uvx copier==9.19.1 update --answers-file .copier-planner-answers.yml \
  --vcs-ref <planner-tag> --pretend .

uvx copier==9.19.1 update --answers-file .copier-planner-answers.yml \
  --vcs-ref <planner-tag> .
```

Always pass the planner answers file. Never rely on Copier's default
`.copier-answers.yml`, which may select ai-devkit or another overlay. Review:

1. `git status --short` and the full diff; only `.planner/**` and the planner
   answers file may change.
2. Any unmerged Git entries and both sides of a managed-file conflict.
3. `uv run --script .planner/scripts/check_planning.py --project . --format text`.
4. The project's own checks.

Commit the planner-only update separately:

```bash
git add .planner .copier-planner-answers.yml
git commit -m "chore: update planner overlay to <planner-tag>"
```

If an edited `.planner/` file conflicts, resolve it visibly with both sides
reviewed. Do not run `copier recopy` as routine recovery: it can discard
managed-file edits.

## Rollback

Revert only the planner update commit:

```bash
git revert --no-edit <planner-update-commit>
```

This restores managed files and planner provenance together. If later project
work touched the same paths, resolve the revert conflicts deliberately. Never
hand-edit `_commit`, downgrade another overlay, run `git clean -fd`, reset
shared history or rewrite commits.

For an uncommitted failed update, restore only the reviewed affected tracked
paths from the pre-update commit and inspect newly created untracked paths
individually.

## Uninstall

Remove only the reviewed planner-owned paths:

```text
.planner/
.copier-planner-answers.yml
```

`planning/**` is project-owned and remains. Remove `_bmad/**` or `openspec/**`
only through their own native tools and only if the project intends to drop
those capabilities.

## Versioning and compatibility

The overlay version, the native record schema and BMAD compatibility are
independent:

- Overlay patch/minor updates cannot rewrite project records.
- `schema_version: 1` is the only supported native record schema in v0.1.
  An unsupported version is diagnosed; it is not auto-converted.
- Reinstalling BMAD is a separate reviewed transaction. It must preserve
  project-authored `_bmad/custom/**` and canonical planning bytes.
- Updating another overlay must leave `.planner/**` and planner answers bytes
  unchanged.
