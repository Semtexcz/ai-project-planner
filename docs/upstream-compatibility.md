# Upstream compatibility and pinned versions

Inspected and exercised 2026-11-15 on Linux x86-64 (Ubuntu-family, kernel
reported by the host), Python 3.14.4 system / 3.12.13 uv-managed, Node
v22.20.0, npm 11.12.1, uv 0.11.28.

This file records observed behaviour, not vendor guarantees. No reference
project was modified and no upstream source is vendored.

## Pinned versions

| Tool | Version | Role | Evidence status |
| --- | --- | --- | --- |
| Copier | 9.19.1 | overlay lineage, copy/update, native conflict handling | exercised |
| BMAD METHOD | 6.12.4 | product brief, PRD, epics/stories, readiness, correct-course | installer/resolver exercised; planning behaviour requires agent acceptance |
| Agent Skills reference validator | `skills-ref@0.1.5` | native SKILL.md format validation | exercised |
| OpenSpec | 1.16.0 and 2.0.0 | optional specification/change authority | init and read-only validate exercised; apply/archive not used |
| ai-devkit overlay | `cc04bcef80b3838cd5956a872717b65949190468` | independent Copier overlay compatibility | copy coexistence in both orders exercised in disposable destinations |
| PyYAML | 6.0.3 | checker/test YAML parsing | exercised |
| jsonschema | 4.25.1 | checker/test JSON Schema 2020-12 | exercised |
| pytest | 8.4.2 | test runner | exercised |
| uv | 0.11.28 | isolated environment and PEP 723 script runner | exercised |

`uv.lock` pins the development dependency graph. The deployed checker's PEP 723
header pins its own runtime dependencies, so it does not resolve against or
edit an application environment.

## Copier 9.19.1

Observed from the pinned CLI:

```text
uvx copier==9.19.1 --version
-> copier 9.19.1

uvx copier==9.19.1 copy --help
uvx copier==9.19.1 update --help
```

Relevant confirmed switches: `copy` and `update` accept `--answers-file/-a`,
`--vcs-ref/-r`, `--pretend/-n`, `--defaults/-l`, `--data/-d`, `--overwrite/-w`;
`update` adds `--conflict {rej,inline}`. `update` requires an answers file with
`_src_path`.

Disposable-template smoke test:

- `_subdirectory: templates/overlay` rendered only that subtree.
- `_answers_file: .copier-selftest-answers.yml` produced that file only.
- The dynamic answers template `{{ _copier_conf.answers_file }}.jinja` used
  `{{ _copier_answers|to_nice_yaml -}}` and recorded `_commit: v0.1.0`,
  `_src_path` and the display-name answer.
- A second tagged revision updated only the managed file and answers file;
  project-owned `planning-note.md` and `app.txt` were unchanged.
- Non-`.jinja` files are copied byte-identically; Copier does not interpolate
  them. Planner therefore keeps only the answers file as a Jinja template.
- `--pretend` produced no destination files.
- Copier does not infer ownership. A non-overlapping unknown file under
  `.planner/` survived, but a matching managed path would be rendered over it.
  The documented preflight (`test ! -e .planner && test ! -e
  .copier-planner-answers.yml`) is mandatory.

## BMAD METHOD 6.12.4

Exact installer commands exercised:

```bash
npx --yes bmad-method@6.12.4 install --help
npx --yes bmad-method@6.12.4 install --list-tools
npx --yes bmad-method@6.12.4 install --list-options
npx --yes bmad-method@6.12.4 install --yes \
  --directory <temp-project> --modules bmm --tools opencode \
  --set bmm.planning_artifacts=planning/runs/bmad/planning-artifacts \
  --set bmm.implementation_artifacts=planning/runs/bmad/implementation-artifacts \
  --set bmm.project_knowledge=planning/runs/bmad/project-knowledge
```

Observed with `opencode`:

```text
_bmad/config.toml                     installer-managed
_bmad/config.user.toml                personal
_bmad/custom/config.toml              team overrides, committed
_bmad/custom/config.user.toml         personal, gitignored
_bmad/custom/.gitignore               *.user.toml
_bmad/_config/{manifest.yaml,skill-manifest.csv,files-manifest.csv}
_bmad/scripts/{config_utils,memlog,render_skill,resolve_config,resolve_customization}.py
.agents/skills/bmad-*/SKILL.md        29 skills for the BMM install
.agents/skills/bmad-*/customize.toml  per-skill merge surface
.opencode/commands/                   29 generated commands
```

Installed inventory includes execution skills (`bmad-build`, `bmad-build-auto`,
`bmad-agent-dev`, etc.). Presence is not authorization to invoke them.

Resolvers:

```bash
uv run _bmad/scripts/resolve_config.py --project-root .
uv run _bmad/scripts/resolve_customization.py \
  --skill .agents/skills/bmad-prd --project-root . --key workflow
```

Verified merge behaviour with a sparse `_bmad/custom/bmad-prd.toml`:

- `workflow.persistent_facts` returned the planner probe facts.
- `workflow.doc_standards` returned the inherited
  `skill:bmad-review lenses=structure,prose` plus the appended probe, proving
  arrays append.
- `workflow.prd_output_path` defaults to
  `{planning_artifacts}/prds` and `run_folder_pattern` to
  `prd-{project_name}-{date}`.

Reinstall/update evidence:

- `_bmad/custom/bmad-prd.toml` and a sentinel `_bmad/custom/sentinel.txt`
  survived `install --action update`.
- An `AGENTS.md`/application sentinel is outside the installer and is not
  touched; the integration test asserts hashes.
- An `--yes` update did not preserve the exact previous `--set` scalar value
  verbatim: the resolved path became
  `{project-root}/planning/runs/bmad/planning-artifacts`. The recipe therefore
  re-passes `--set` and verifies the resolver output. The installer-managed
  `_bmad/config.toml` must not be hand-edited.
- Empty arrays do not remove inherited entries; there is no removal operation.
  Planner uses appended persistent facts rather than assuming deletion.
- PRD defaults include `doc_standards` and `finalize_reviewers` that can offer
  review subagents. Planner invocations decline those optional gates to honour
  the single-agent/no-paid-delegation boundary. This is recorded as an
  upstream limitation, not worked around by forking.

## Agent Skills

`skills-ref@0.1.5` observed behaviour:

```text
npx --yes skills-ref@0.1.5 validate <skill-dir>
Valid skill: <path>                    exit 0
Validation failed for <path>:
  - Directory name 'bad-skill' must match skill name 'wrong-name'
                                       exit 1
```

Planner validates each rendered skill directory with this native validator as
an integration check. The format validator does not judge planning quality.

## OpenSpec

`@fission-ai/openspec` versions 1.16.0 and 2.0.0 were installed only in
disposable directories with `--tools opencode --no-animation`.

| Version | Observed generated integration | Notes |
| --- | --- | --- |
| 1.16.0 | `.opencode/skills/openspec-*`, `.opencode/commands/opsx-*`, `openspec/config.yaml`, `openspec/specs`, `openspec/changes` | devkit's inspected pin |
| 2.0.0 | `.agents/skills/openspec-*`, `openspec/config.yaml`, `openspec/specs`, `openspec/changes` | current upstream v2 baseline |

Both expose the same six skill names (`openspec-propose`, `-apply-change`,
`-archive-change`, `-explore`, `-sync-specs`, `-update-change`) and the same
read-only validation switches (`validate --changes|--specs --strict
--no-interactive`). Generated skill frontmatter includes
`allowed-tools: Bash(openspec:*)`; planner does not use that as permission to
apply or archive.

Planner never initializes or upgrades OpenSpec as a side effect and never
creates a competing requirement or task state.

## ai-devkit coexistence

The reviewed ai-devkit commit
`cc04bcef80b3838cd5956a872717b65949190468` was cloned to a pytest temporary
directory. Planner and devkit were copied into disposable destinations in both
orders.

Observed:

- Each answers file names its own source and revision
  (`.copier-planner-answers.yml` vs `.copier-answers.yml`).
- Planner output remained only `.planner/**` plus its answers file.
- Devkit generated `AGENTS.md`. In planner-first order, devkit's copy asked to
  overwrite that devkit-owned path and refused to continue without
  `--overwrite` in a non-interactive session. The integration test uses
  `--overwrite` only in a disposable directory and asserts planner bytes and
  planner provenance are unchanged. This is a devkit ownership decision, not a
  planner write.
- In devkit-first order, planner left the generated `AGENTS.md` byte-identical.
- Project application, planning and knowledge sentinels remained unchanged in
  both orders.

Not exercised: a newer devkit revision update in both order combinations. Update
independence is proven with the minimal independent overlay fixture.

## Platform and availability limits

- Only Linux x86-64 is verified. macOS/Windows behaviour is unverified.
- npm registry access and package integrity were required for BMAD, OpenSpec
  and `skills-ref`; transient npm tarball retry warnings were observed and did
  not change the pinned versions.
- Real BMAD planning quality, single-agent compliance, cross-domain fitness and
  model-provider availability are agent/human acceptance gates, not
  deterministic passes.
- No OpenAI model was used for implementation, tests, reviews or repairs.
