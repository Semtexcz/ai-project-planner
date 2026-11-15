# Planner overlay (installed capability)

This directory is managed by the Copier planner overlay. It contains reusable
capability, not project truth:

- `references/` - normative runtime contracts.
- `schemas/` - JSON Schemas for project configuration and native records.
- `scripts/check_planning.py` - read-only structural checker.
- `assets/` - blank project-owned records and report/prompt templates.
- `skills/` - six portable Agent Skills.

Project truth lives in the project's own `planning/` directory (or in existing
authorities registered by `planning/planner.yaml`). It is created by INIT and is
never rendered, deleted or merged by an overlay update.

## Explicit invocation

No harness configuration is required. Read the skill file and carry out the
operation. Baseline activation:

> Read `.planner/skills/planner-init/SKILL.md` and carry out INIT for this
> project. Follow the existing project instructions and retain all existing
> content authorities.

Substitute the corresponding path for other operations:

| Operation | Skill path |
| --- | --- |
| INIT | `.planner/skills/planner-init/SKILL.md` |
| STATUS | `.planner/skills/planner-status/SKILL.md` |
| PLAN | `.planner/skills/planner-plan/SKILL.md` |
| NEXT | `.planner/skills/planner-next/SKILL.md` |
| CHANGE | `.planner/skills/planner-change/SKILL.md` |
| AUDIT | `.planner/skills/planner-audit/SKILL.md` |

Skills refer to shared resources with paths relative to their own directory,
for example `../../references/governance.md`. Do not move or retarget these
files.

## Optional discovery

A human may configure a supported harness's additional skill directory, or
create six project-owned links in a supported directory that has no ownership
conflict. Links must resolve to the canonical skill directories so relative
references keep working. Do not edit root `AGENTS.md`, shared configuration or
global agent settings. Overlay updates do not recreate or retarget
project-owned links. Explicit invocation remains fully supported without them.

## Structural checks

```bash
uv run --script .planner/scripts/check_planning.py --project . --format text
```

The checker is read-only. Exit `0` means deterministic checks completed without
errors, not that the plan is strategically sound. Exit `1` is a structural or
approval invariant failure. Exit `2` is unreadable configuration, an
unsupported schema or an invalid invocation.

## Ownership and updates

- `.planner/**` and `.copier-planner-answers.yml` are managed by Copier.
- `planning/**` belongs to the project. Copier never touches it.
- BMAD (`_bmad/**`, installed `bmad-*` skills) is owned by the BMAD native
  installer.
- OpenSpec (`openspec/**`, generated skills) is owned by the OpenSpec native
  CLI.
- `AGENTS.md`, README, application manifests, CI and other overlays are never
  written by planner.

Update with Copier and this overlay's answers file (see the repository
`docs/install-update.md`). Review conflicts visibly; never take one side
automatically. Rollback is a Git revert of the isolated planner update commit.

## Model policy in generated prompts

Derived execution prompts recommend DeepSeek V4.1 Flash with reasoning HIGH.
DeepSeek V4 Pro HIGH is an escalation only under the recorded policy. Model
labels are advisory and must be mapped to the user's native harness
configuration. Planner never makes inference calls itself.
