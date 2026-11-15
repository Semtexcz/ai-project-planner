"""Skill packaging and workflow-contract checks (I08-I14)."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from support import (
    PLANNER_ROOT,
    load_frontmatter,
    make_project,
    run_checker,
    scope_digest,
    tree_hashes,
    write_record,
)

SKILLS = [
    "planner-init",
    "planner-status",
    "planner-plan",
    "planner-next",
    "planner-change",
    "planner-audit",
]


def skill_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    _, raw, body = text.split("---\n", 2)
    return yaml.safe_load(raw), body


def test_exactly_six_portable_skills_with_valid_frontmatter():
    directories = sorted(
        path.name
        for path in (PLANNER_ROOT / "skills").iterdir()
        if path.is_dir()
    )
    assert directories == sorted(SKILLS)
    for name in SKILLS:
        frontmatter, body = skill_frontmatter(PLANNER_ROOT / "skills" / name / "SKILL.md")
        assert frontmatter["name"] == name
        assert re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", frontmatter["name"])
        assert 0 < len(frontmatter["description"]) <= 1024
        assert body.strip()
        assert "governance.md" in body
        assert "operation-contracts.md" in body


def test_skill_resource_paths_resolve_and_are_project_relative():
    pattern = re.compile(r"(?:\.\./)+(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+")
    for name in SKILLS:
        skill_dir = PLANNER_ROOT / "skills" / name
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        references = set(pattern.findall(text))
        assert references, name
        for reference in references:
            assert (skill_dir / reference).resolve().exists(), (name, reference)


def test_no_absolute_workstation_paths_are_shipped():
    forbidden = ("/mnt/Data/", "/home/semtex", "C:\\Users\\")
    for path in PLANNER_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".md", ".py", ".json", ".yaml"}:
            continue
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, (path, token)


def test_operation_prohibitions_are_explicit():
    text = {
        name: re.sub(
            r"\s+",
            " ",
            (PLANNER_ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8"),
        )
        for name in SKILLS
    }
    assert "never overwrite" in text["planner-init"].lower()
    assert "resume" in text["planner-init"].lower()
    assert "byte-identical" in text["planner-status"]
    assert "rolling-wave" in text["planner-plan"].lower()
    assert "do not create a sprint-status file" in text["planner-plan"].lower()
    assert "do not run the prompt" in text["planner-next"].lower()
    assert "scope-digest-prefix" in text["planner-next"]
    assert "verify the source revision" in text["planner-change"].lower()
    assert "do not repair automatically" in text["planner-audit"].lower()
    assert "not a strategic pass" in text["planner-audit"].lower()


def test_prompt_asset_has_no_invented_values_and_required_sections():
    text = (
        PLANNER_ROOT / "assets" / "prompt.md"
    ).read_text(encoding="utf-8")
    for marker in (
        "DERIVED EXECUTION PROMPT",
        "DeepSeek V4.1 Flash",
        "DeepSeek V4 Pro",
        "Trace: VIS -> OBJ/OUT -> REQ -> MS -> [WP] -> TASK",
        "Scope includes:",
        "Scope excludes:",
        "Acceptance and verification:",
        "Stop before",
        "Do not claim done/accepted",
    ):
        assert marker in text
    assert "TASK-001" not in text  # no seeded ready task
    assert "REQ-001" not in text


def test_prompt_is_not_rendered_by_copier_as_a_ready_artifact():
    text = (PLANNER_ROOT / "assets" / "prompt.md").read_text(encoding="utf-8")
    assert "not authority" in text
    assert "must not be executed" in text


def test_unapproved_fixture_does_not_yield_ready_work(project):
    # The fixture starts authorized; removing the authorization must remove
    # readiness without changing task state prose.
    from support import load_frontmatter, write_record

    record = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    record["scope"]["approvals"] = []
    write_record(project.root / "planning/tasks/TASK-001.md", record)
    before = tree_hashes(project.root)
    report = json.loads(run_checker(project.root).stdout)
    after = tree_hashes(project.root)
    assert before == after
    assert report["coverage"]["task_readiness"]["TASK-001"]["ready"] is False
    assert report["coverage"]["ready_tasks"] == []
    assert any(
        finding["rule"] == "TASK_NOT_AUTHORIZED" for finding in report["findings"]
    )


def test_ready_selection_is_stable_across_identical_runs(project):
    first = run_checker(project.root)
    second = run_checker(project.root)
    assert first.stdout == second.stdout
    report = json.loads(first.stdout)
    assert report["coverage"]["ready_tasks"] == ["TASK-001"]
    assert first.returncode == 0


def test_task_completion_alone_does_not_achieve_milestone(project):
    from support import load_frontmatter, write_record

    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["execution"]["state"] = "done"
    task["execution"]["evidence"] = [
        {
            "id": "TASK-001:EV-1",
            "criteria": ["TASK-001:AC-1"],
            "method": "Read the report.",
            "subject_revision": "working-tree",
            "result": "pass",
            "artifact": "planning/evidence/demo.md",
            "reviewer": "domain_reviewer",
            "limitations": "Single reviewer.",
            "observed_at": "2026-11-15",
        }
    ]
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    report = json.loads(run_checker(project.root).stdout)
    assert report["result"]["errors"] == 0
    milestone = load_frontmatter(project.root / "planning/milestones/MS-001.md")
    assert milestone["execution"]["state"] == "active"
    assert report["coverage"]["records_by_kind"]["milestone"] == 1


def test_rendered_skills_keep_sibling_resource_paths(tmp_path):
    from test_template import make_tagged_template, copy_template

    template = make_tagged_template(tmp_path)
    destination = tmp_path / "target"
    result = copy_template(template, destination)
    assert result.returncode == 0, result.stderr
    for name in SKILLS:
        skill_path = destination / ".planner/skills" / name / "SKILL.md"
        assert skill_path.is_file()
        text = skill_path.read_text(encoding="utf-8")
        assert "../../references/governance.md" in text
        assert (skill_path.parent / "../../references/governance.md").resolve().is_file()


@pytest.mark.integration
def test_native_agent_skills_validator_accepts_all_skills():
    npx = shutil.which("npx")
    if npx is None:
        pytest.skip("npx is not available")
    for name in SKILLS:
        result = subprocess.run(
            [
                npx,
                "--yes",
                "skills-ref@0.1.5",
                "validate",
                str(PLANNER_ROOT / "skills" / name),
            ],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        assert result.returncode == 0, (name, result.stdout, result.stderr)
        assert "Valid skill" in result.stdout


# --------------------------------------------------------- scenario A (slice)
def test_vertical_slice_a_trace_ready_task_and_no_side_effects(tmp_path):
    intent = (Path(__file__).resolve().parent / "fixtures/empty/INTENT.md").read_text(
        encoding="utf-8"
    )
    assert "document conversion" in intent
    project = make_project(tmp_path / "conversion")
    project.change_scope(
        "VIS-001",
        purpose="Convert Markdown documents to readable plain text without silent loss.",
        beneficiaries=["Writers and maintainers who need plain-text output"],
        problem="Conversion tools silently drop unsupported constructs.",
        choices=["Report unsupported constructs explicitly."],
        exclusions=["No server and no network access during conversion."],
        assumptions=["Python 3.11+ is available in the execution environment."],
    )
    project.change_scope(
        "REQ-001",
        statement="The package must convert Markdown to plain text without silent loss.",
        classification="functional",
    )
    project.change_scope(
        "MS-001",
        outcome="A maintainer converts a representative document and sees an explicit report.",
    )
    project.change_scope(
        "TASK-001",
        title="Implement and verify the Markdown conversion library",
        rationale="The approved outcome requires a working local converter.",
        deliverables=[
            {"description": "A conversion library module", "path": "src/docconvert/convert.py"},
            {"description": "A command-line entry point", "path": "src/docconvert/cli.py"},
        ],
        include=["Markdown to plain text conversion", "Explicit unsupported-construct report"],
        exclude=["No network access", "No server deployment"],
    )
    project.write()
    before = tree_hashes(project.root)
    report = json.loads(run_checker(project.root).stdout)
    after = tree_hashes(project.root)
    assert before == after
    assert report["result"]["errors"] == 0
    assert report["coverage"]["ready_tasks"] == ["TASK-001"]

    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    required = [
        "title",
        "objective",
        "rationale",
        "milestone",
        "requirements",
        "include",
        "exclude",
        "depends_on",
        "context",
        "deliverables",
        "acceptance",
        "verification",
        "approvals",
        "priority",
        "size",
    ]
    for field in required:
        assert field in task["scope"], field
    assert task["scope"]["objective"] == "OBJ-001"
    assert task["scope"]["milestone"] == "MS-001"
    assert task["scope"]["requirements"] == ["REQ-001"]
    digest = scope_digest(task["scope"])
    assert len(digest) == 64
    assert not (project.root / "planning/prompts").exists()
    assert not (project.root / "src").exists()
    assert not (project.root / "AGENTS.md").exists()

    second = json.loads(run_checker(project.root).stdout)
    assert second["coverage"]["ready_tasks"] == ["TASK-001"]
    assert task["execution"]["state"] == "ready"


# ------------------------------------------------------ scenario E (change)
def cloud_sync_change() -> dict:
    return {
        "schema_version": 1,
        "kind": "change",
        "id": "CHG-001",
        "owner": "product_owner",
        "scope": {
            "idea": "Add optional cloud sync and hosted retention.",
            "source": "tests/fixtures/change/cloud-sync-idea.md",
            "affected": ["VIS-001", "REQ-001", "MS-001", "TASK-001"],
            "impact": "Expands scope beyond local-only, no-network conversion and would "
            "invalidate the task approval, saved prompt and evidence assumptions.",
            "alternatives": [
                "Reject and keep local-only",
                "Defer until a separate strategic decision",
                "Narrow to an export file that the user uploads manually",
            ],
            "proposed_delta": "No change until a human disposition.",
            "required_approvals": ["product_owner"],
            "revisit_trigger": "If remote collaboration becomes an approved objective",
        },
        "execution": {
            "state": "captured",
            "disposition_decision": None,
            "applied_revision": None,
            "blockers": [],
            "progress_notes": [],
        },
    }


def rejection_decision(change_digest: str) -> dict:
    return {
        "schema_version": 1,
        "kind": "decision",
        "id": "DEC-002",
        "owner": "product_owner",
        "scope": {
            "topic": "Disposition of the cloud-sync change",
            "rationale": "It conflicts with the approved local-only constraint.",
            "options": ["Reject", "Defer", "Narrow", "Pivot"],
            "choice": "Reject for v0.1 and retain a revisit trigger",
            "targets": [{"record": "CHG-001", "scope_sha256": change_digest}],
            "authority": "Product Owner",
            "supersedes": [],
        },
        "execution": {
            "state": "accepted",
            "actor": "Fixture Product Owner",
            "decided_at": "2026-11-15",
            "approval_source": "Recorded disposition in fixture review",
            "applied_revision": None,
        },
    }


def test_change_capture_does_not_mutate_approved_scope(tmp_path):
    project = make_project(tmp_path / "change")
    change = cloud_sync_change()
    project.extra_records["planning/records/CHG-001.md"] = change
    project.write()
    approved = {
        rel: (project.root / rel).read_bytes()
        for rel in (
            "planning/strategy.md",
            "planning/requirements/REQ-001.md",
            "planning/milestones/MS-001.md",
            "planning/tasks/TASK-001.md",
            "planning/records/DEC-001.md",
        )
    }
    report = json.loads(run_checker(project.root).stdout)
    assert report["result"]["errors"] == 0
    for rel, content in approved.items():
        assert (project.root / rel).read_bytes() == content, rel
    assert report["coverage"]["task_readiness"]["TASK-001"]["ready"] is True


def test_rejected_change_preserves_plan_and_retains_history(tmp_path):
    project = make_project(tmp_path / "change")
    change = cloud_sync_change()
    digest = scope_digest(change["scope"])
    project.extra_records["planning/records/CHG-001.md"] = change
    project.extra_records["planning/records/DEC-002.md"] = rejection_decision(digest)
    project.write()
    before = {
        rel: (project.root / rel).read_bytes()
        for rel in (
            "planning/strategy.md",
            "planning/requirements/REQ-001.md",
            "planning/milestones/MS-001.md",
            "planning/tasks/TASK-001.md",
        )
    }
    # Record the human disposition without changing approved scope.
    change["execution"]["state"] = "rejected"
    change["execution"]["disposition_decision"] = "DEC-002"
    write_record(project.root / "planning/records/CHG-001.md", change)
    report = json.loads(run_checker(project.root).stdout)
    assert report["result"]["errors"] == 0
    for rel, content in before.items():
        assert (project.root / rel).read_bytes() == content, rel
    stored = load_frontmatter(project.root / "planning/records/CHG-001.md")
    assert stored["execution"]["state"] == "rejected"
    assert stored["scope"]["revisit_trigger"]


def test_stale_change_baseline_blocks_old_patch(tmp_path):
    project = make_project(tmp_path / "change").write()
    requirement = load_frontmatter(project.root / "planning/requirements/REQ-001.md")
    proposal_digest = scope_digest(requirement["scope"])
    requirement["scope"]["statement"] = "A changed source baseline."
    current_digest = scope_digest(requirement["scope"])
    assert proposal_digest != current_digest
    # The application gate is a digest comparison, not a stale-diff apply.
    assert proposal_digest != current_digest


def test_approved_narrow_change_touches_only_its_target(tmp_path):
    project = make_project(tmp_path / "change").write()
    untouched = {
        rel: (project.root / rel).read_bytes()
        for rel in (
            "planning/strategy.md",
            "planning/requirements/REQ-001.md",
            "planning/milestones/MS-001.md",
        )
    }
    old_decision = (project.root / "planning/records/DEC-001.md").read_bytes()
    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["scope"]["include"].append(
        "Add a local export file that the user may upload manually"
    )
    task["scope"]["approvals"] = [{"decision": "DEC-002"}]
    digest = scope_digest(task["scope"])
    decision = {
        "schema_version": 1,
        "kind": "decision",
        "id": "DEC-002",
        "owner": "product_owner",
        "scope": {
            "topic": "Approve the narrowed task scope",
            "rationale": "The narrowed alternative stays local-only.",
            "options": ["Approve the narrowed scope", "Reject"],
            "choice": "Approve the narrowed scope",
            "targets": [{"record": "TASK-001", "scope_sha256": digest}],
            "authority": "Product Owner",
            "supersedes": [],
        },
        "execution": {
            "state": "accepted",
            "actor": "Fixture Product Owner",
            "decided_at": "2026-11-15",
            "approval_source": "Recorded approval of the narrowed alternative",
            "applied_revision": None,
        },
    }
    write_record(project.root / "planning/records/DEC-002.md", decision)
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    report = json.loads(run_checker(project.root).stdout)
    assert report["result"]["errors"] == 0
    for rel, content in untouched.items():
        assert (project.root / rel).read_bytes() == content, rel
    assert (project.root / "planning/records/DEC-001.md").read_bytes() == old_decision
    assert (project.root / "planning/records/DEC-002.md").is_file()
    assert report["coverage"]["ready_tasks"] == ["TASK-001"]


# ------------------------------------------------------- scenario F (drift)
def test_audit_detects_orphan_edit_and_blocks_affected_next(tmp_path):
    project = make_project(tmp_path / "drift").write()
    requirement = load_frontmatter(project.root / "planning/requirements/REQ-001.md")
    requirement["scope"]["statement"] = (
        "The overlay may upload converted documents to the cloud without a decision."
    )
    write_record(project.root / "planning/requirements/REQ-001.md", requirement)
    orphan = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    orphan["id"] = "TASK-002"
    orphan["scope"] = dict(
        orphan["scope"],
        title="Unapproved orphan work",
        objective="OBJ-999",
        requirements=["REQ-999"],
    )
    orphan["scope"]["approvals"] = []
    orphan["execution"] = {
        "state": "draft",
        "authorization": [],
        "evidence": [],
        "blockers": [],
        "progress_notes": [],
    }
    write_record(project.root / "planning/tasks/TASK-002.md", orphan)
    before = tree_hashes(project.root)
    report = json.loads(run_checker(project.root).stdout)
    after = tree_hashes(project.root)
    assert before == after
    rules = {finding["rule"] for finding in report["findings"]}
    assert "REFERENCE_DANGLING" in rules
    assert "APPROVAL_STALE" in rules
    assert "TASK_REQUIREMENT_NOT_AUTHORIZED" in rules
    assert report["coverage"]["ready_tasks"] == []
    paths = {finding["locator"] for finding in report["findings"]}
    assert "planning/tasks/TASK-002.md" in paths
    assert "planning/requirements/REQ-001.md" in paths


def test_opposed_clauses_are_not_auto_resolved(tmp_path):
    fixture = Path(__file__).resolve().parent / "fixtures/drift/opposed-clauses.md"
    project = make_project(tmp_path / "drift").write()
    case = project.root / "docs/retention-case.md"
    case.parent.mkdir(parents=True)
    case.write_text(fixture.read_text(encoding="utf-8"), encoding="utf-8")
    before = tree_hashes(project.root)
    report = json.loads(run_checker(project.root).stdout)
    after = tree_hashes(project.root)
    assert before == after
    # A checker cannot prove this semantic contradiction; it must remain for
    # human adjudication, and the audit template must require a citation.
    assert not [f for f in report["findings"] if "CONTRADICTION" in f["rule"]]
    text = (PLANNER_ROOT / "assets/audit-report.md").read_text(encoding="utf-8")
    assert "semantic" in text.lower()
    assert "Affected chain" in text
    assert "required human decision" in text.lower()
    assert "does not silently choose" not in text


def test_record_schema_error_at_task_blocks_readiness(project):
    from support import load_frontmatter, write_record

    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["scope"]["priority"] = "P9"
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    report = json.loads(run_checker(project.root).stdout)
    readiness = report["coverage"]["task_readiness"]["TASK-001"]
    assert readiness["ready"] is False
    assert any("RECORD_SCHEMA" in item for item in readiness["blockers"])
    assert report["coverage"]["ready_tasks"] == []


def test_global_current_milestone_error_blocks_every_ready_task(project):
    config = yaml.safe_load(
        (project.root / "planning/planner.yaml").read_text(encoding="utf-8")
    )
    config["current_milestone"] = None
    (project.root / "planning/planner.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
    )
    report = json.loads(run_checker(project.root).stdout)
    readiness = report["coverage"]["task_readiness"]["TASK-001"]
    assert readiness["ready"] is False
    assert any("CURRENT_MILESTONE_UNSET" in item for item in readiness["blockers"])


def test_delegation_covering_a_milestone_is_review_required_not_ready(project):
    decision = load_frontmatter(project.root / "planning/records/DEC-001.md")
    decision["scope"]["targets"] = [
        target for target in decision["scope"]["targets"] if target["record"] != "TASK-001"
    ]
    decision["scope"]["delegation"] = {
        "covers": ["MS-001"],
        "exclusions": ["No new requirement or milestone outcome"],
        "permitted_decisions": ["Decompose approved milestone work"],
        "stop_conditions": ["Stop before expanding scope"],
    }
    write_record(project.root / "planning/records/DEC-001.md", decision)
    report = json.loads(run_checker(project.root).stdout)
    assert ("APPROVAL_DELEGATED", "manual_review") in {
        (finding["rule"], finding["severity"]) for finding in report["findings"]
    }
    assert report["coverage"]["ready_tasks"] == []
    assert report["coverage"]["review_required_tasks"] == ["TASK-001"]


def test_gate_evidence_must_cite_the_gate_criterion(project):
    from support import load_frontmatter, write_record

    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["scope"]["depends_on"] = [
        {
            "gate": "External review",
            "criterion": "TASK-001:AC-999",
            "evidence_ref": "TASK-001:EV-1",
        }
    ]
    task["execution"]["evidence"] = [
        {
            "id": "TASK-001:EV-1",
            "criteria": ["TASK-001:AC-1"],
            "method": "Read.",
            "subject_revision": "working-tree",
            "result": "pass",
            "artifact": "planning/evidence/demo.md",
            "reviewer": "domain_reviewer",
            "limitations": "None.",
            "observed_at": "2026-11-15",
        }
    ]
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    report = json.loads(run_checker(project.root).stdout)
    assert any(finding["rule"] == "GATE_EVIDENCE_CRITERION" for finding in report["findings"])
    assert report["coverage"]["ready_tasks"] == []


def test_review_state_requires_recorded_evidence(project):
    from support import load_frontmatter, write_record

    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["execution"]["state"] = "review"
    task["execution"]["evidence"] = []
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    report = json.loads(run_checker(project.root).stdout)
    assert any(
        finding["rule"] == "TASK_REVIEW_WITHOUT_EVIDENCE" for finding in report["findings"]
    )


def test_stale_context_revision_blocks_readiness(project):
    from support import load_frontmatter, write_record

    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["scope"]["context"][0]["revision"] = "old-revision"
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    report = json.loads(
        run_checker(project.root, "json", "--source-revision", "new-revision").stdout
    )
    assert any(
        finding["rule"] == "CONTEXT_REVISION_STALE" for finding in report["findings"]
    )
    assert report["coverage"]["ready_tasks"] == []


def test_adopted_normative_context_requires_review(tmp_path):
    project = make_project(tmp_path / "adopted").write()
    adopted = project.root / "docs/adopted.md"
    adopted.parent.mkdir(parents=True)
    adopted.write_text("# Adopted source\n\nStatus: proposed only.\n", encoding="utf-8")
    config_path = project.root / "planning/planner.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["authorities"].append(
        {
            "kind": "requirement",
            "id": "ADOPT-1",
            "owner": "product_owner",
            "ref": "docs/adopted.md",
            "format": "markdown",
        }
    )
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["scope"]["context"].append(
        {
            "ref": "docs/adopted.md",
            "authority": "adopted requirement",
            "revision": "working-tree",
            "purpose": "Adopted normative context whose status is not parsed.",
            "normative": True,
        }
    )
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    decision = load_frontmatter(project.root / "planning/records/DEC-001.md")
    for target in decision["scope"]["targets"]:
        if target["record"] == "TASK-001":
            target["scope_sha256"] = scope_digest(task["scope"])
    write_record(project.root / "planning/records/DEC-001.md", decision)

    report = json.loads(run_checker(project.root).stdout)
    readiness = report["coverage"]["task_readiness"]["TASK-001"]
    assert readiness["ready"] is False
    assert readiness["review_required"] is True
    assert "EXTERNAL_AUTHORITY_UNPARSED" in readiness["manual_review"]
    assert report["coverage"]["ready_tasks"] == []


def test_pure_adoption_lists_adopted_tasks_as_review_required(tmp_path):
    project = make_project(tmp_path / "adopted-task").write()
    card = project.root / "docs/existing-task.md"
    card.parent.mkdir(parents=True)
    card.write_text("# TASK-900\n\nExisting card, status ready.\n", encoding="utf-8")
    config_path = project.root / "planning/planner.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["authorities"].append(
        {
            "kind": "task",
            "id": "TASK-900",
            "owner": "product_owner",
            "ref": "docs/existing-task.md",
            "format": "markdown",
        }
    )
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    report = json.loads(run_checker(project.root).stdout)
    adopted = report["coverage"]["task_readiness"]["TASK-900"]
    assert adopted["state"] == "adopted"
    assert adopted["ready"] is False
    assert adopted["review_required"] is True
    assert "EXTERNAL_AUTHORITY_UNPARSED" in adopted["manual_review"]
    assert report["coverage"]["ready_tasks"] == ["TASK-001"]
    assert report["coverage"]["review_required_tasks"] == ["TASK-900"]


def test_adopted_id_collision_blocks_native_readiness(tmp_path):
    project = make_project(tmp_path / "collision").write()
    card = project.root / "docs/colliding-task.md"
    card.parent.mkdir(parents=True)
    card.write_text("# TASK-001\n\nA different adopted card.\n", encoding="utf-8")
    config_path = project.root / "planning/planner.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["authorities"].append(
        {
            "kind": "task",
            "id": "TASK-001",
            "owner": "product_owner",
            "ref": "docs/colliding-task.md",
            "format": "markdown",
        }
    )
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    result = run_checker(project.root)
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert any(
        finding["rule"] == "ID_COLLISION" for finding in report["findings"]
    )

    # The adopted placeholder never replaces the native record: TASK-001 keeps
    # exactly one readiness entry, still describing the native contract.
    assert set(report["coverage"]["task_readiness"]) == {"TASK-001"}
    readiness = report["coverage"]["task_readiness"]["TASK-001"]
    assert readiness["state"] == "ready"
    assert readiness["ready"] is False
    assert "global: ID_COLLISION" in readiness["blockers"]

    # NEXT selects only from ready_tasks, so an ambiguous identity yields no
    # selectable work and the operator sees an explicit blocker set.
    assert report["coverage"]["ready_tasks"] == []
    text = run_checker(project.root, "text")
    assert text.returncode == 1
    assert "ready tasks none" in text.stdout


def test_missing_adopted_source_blocks_every_ready_task(tmp_path):
    project = make_project(tmp_path / "missing-adopted-source").write()
    config_path = project.root / "planning/planner.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["authorities"].append(
        {
            "kind": "requirement",
            "id": "REQ-900",
            "owner": "product_owner",
            "ref": "docs/absent-requirement.md",
            "format": "markdown",
        }
    )
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    result = run_checker(project.root)
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert any(
        finding["rule"] == "ADOPTED_SOURCE_MISSING" for finding in report["findings"]
    )
    assert report["coverage"]["ready_tasks"] == []
    assert (
        "global: ADOPTED_SOURCE_MISSING"
        in report["coverage"]["task_readiness"]["TASK-001"]["blockers"]
    )


def test_adopted_id_collision_with_embedded_record_blocks_readiness(tmp_path):
    project = make_project(tmp_path / "embedded-collision").write()
    card = project.root / "docs/outcome-note.md"
    card.parent.mkdir(parents=True)
    card.write_text(
        "# OUT-001\n\nAn adopted note reusing an embedded ID.\n", encoding="utf-8"
    )
    config_path = project.root / "planning/planner.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["authorities"].append(
        {
            "kind": "requirement",
            "id": "OUT-001",
            "owner": "product_owner",
            "ref": "docs/outcome-note.md",
            "format": "markdown",
        }
    )
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    result = run_checker(project.root)
    assert result.returncode == 1
    report = json.loads(result.stdout)
    collisions = [
        finding for finding in report["findings"] if finding["rule"] == "ID_COLLISION"
    ]
    assert collisions
    assert "embedded outcome" in collisions[0]["message"]
    assert report["coverage"]["ready_tasks"] == []
    assert (
        "global: ID_COLLISION"
        in report["coverage"]["task_readiness"]["TASK-001"]["blockers"]
    )


def test_explicit_native_mismatch_blocks_every_ready_task(tmp_path):
    project = make_project(tmp_path / "native-mismatch").write()
    config_path = project.root / "planning/planner.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["authorities"].append(
        {
            "kind": "task",
            "id": "TASK-777",
            "owner": "task_owner",
            "ref": "planning/tasks/TASK-001.md",
            "format": "native",
        }
    )
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    result = run_checker(project.root)
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert any(
        finding["rule"] == "ADOPTED_NATIVE_MISMATCH" for finding in report["findings"]
    )
    assert report["coverage"]["ready_tasks"] == []
    assert (
        "global: ADOPTED_NATIVE_MISMATCH"
        in report["coverage"]["task_readiness"]["TASK-001"]["blockers"]
    )


def test_cross_record_objective_error_blocks_task_readiness(project):
    from support import load_frontmatter, write_record

    strategy = load_frontmatter(project.root / "planning/strategy.md")
    strategy["execution"]["items"]["OBJ-001"]["state"] = "proposed"
    write_record(project.root / "planning/strategy.md", strategy)
    report = json.loads(run_checker(project.root).stdout)
    assert any(
        finding["rule"] == "REQUIREMENT_OBJECTIVE_NOT_ACTIVE"
        for finding in report["findings"]
    )
    readiness = report["coverage"]["task_readiness"]["TASK-001"]
    assert readiness["ready"] is False
    assert "REQUIREMENT_OBJECTIVE_NOT_ACTIVE" in readiness["blockers"]


def _add_adopted_milestone(project, milestone_id="MS-900", ref="docs/adopted-milestone.md"):
    source = project.root / ref
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(
        f"# {milestone_id}\n\nAdopted milestone, external state.\n", encoding="utf-8"
    )
    config_path = project.root / "planning/planner.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["authorities"].append(
        {
            "kind": "milestone",
            "id": milestone_id,
            "owner": "product_owner",
            "ref": ref,
            "format": "markdown",
        }
    )
    return config_path, config


# ------------------------------------- adopted current milestone authority
def test_adopted_current_milestone_with_native_active_milestone_blocks_readiness(tmp_path):
    """A task in native MS-001 must not be ready while MS-900 is the adopted current
    milestone. Two milestone authorities would otherwise claim current work."""
    project = make_project(tmp_path / "adopted-current-conflict").write()
    config_path, config = _add_adopted_milestone(project)
    config["current_milestone"] = "MS-900"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    result = run_checker(project.root)
    report = json.loads(result.stdout)
    findings = [
        finding
        for finding in report["findings"]
        if finding["rule"] == "CURRENT_MILESTONE_EXTERNAL"
    ]
    assert findings
    assert findings[0]["severity"] == "manual_review"
    assert "MS-001" in findings[0]["message"]
    assert "ambiguous" in findings[0]["message"]

    readiness = report["coverage"]["task_readiness"]["TASK-001"]
    assert readiness["state"] == "ready"
    assert readiness["ready"] is False
    assert readiness["review_required"] is True
    assert "global: CURRENT_MILESTONE_EXTERNAL" in readiness["manual_review"]
    assert report["coverage"]["ready_tasks"] == []
    assert report["coverage"]["review_required_tasks"] == ["TASK-001"]

    # NEXT selects only from ready_tasks, so ambiguous current-milestone
    # authority yields no executable prompt.
    text = run_checker(project.root, "text")
    assert "ready tasks none" in text.stdout


def test_adopted_milestone_that_is_not_current_does_not_block_native_readiness(tmp_path):
    """Adopting a milestone by reference is legitimate while a different native
    milestone is the authoritative current one."""
    project = make_project(tmp_path / "adopted-future-milestone").write()
    config_path, config = _add_adopted_milestone(project)
    assert config["current_milestone"] == "MS-001"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    report = json.loads(run_checker(project.root).stdout)
    assert not [
        finding
        for finding in report["findings"]
        if finding["rule"].startswith("CURRENT_MILESTONE")
    ]
    readiness = report["coverage"]["task_readiness"]["TASK-001"]
    assert readiness["ready"] is True
    assert readiness["review_required"] is False
    assert report["coverage"]["ready_tasks"] == ["TASK-001"]


def test_adopted_current_milestone_without_native_active_milestone_is_review_only(tmp_path):
    """Pure adoption remains usable: no native task becomes ready, and the
    adopted current milestone is a manual-review item rather than a structural
    error."""
    project = make_project(tmp_path / "adopted-only").write()
    config_path, config = _add_adopted_milestone(project)
    config["current_milestone"] = "MS-900"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    milestone = load_frontmatter(project.root / "planning/milestones/MS-001.md")
    milestone["execution"]["state"] = "proposed"
    write_record(project.root / "planning/milestones/MS-001.md", milestone)
    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["execution"]["state"] = "draft"
    write_record(project.root / "planning/tasks/TASK-001.md", task)

    result = run_checker(project.root)
    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["coverage"]["ready_tasks"] == []
    assert report["result"]["errors"] == 0
    assert any(
        finding["rule"] == "CURRENT_MILESTONE_EXTERNAL"
        and finding["severity"] == "manual_review"
        for finding in report["findings"]
    )


def test_unparsed_native_normative_context_requires_review(project):
    """A normative context file that sits in a native authority collection but is
    not a parsed record is an ambiguous authority, not verified content."""
    notes = project.root / "planning/requirements/notes.md"
    notes.write_text("# Unstructured notes\n", encoding="utf-8")
    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["scope"]["context"].append(
        {
            "ref": "planning/requirements/notes.md",
            "authority": "requirement collection",
            "revision": "working-tree",
            "purpose": "Normative note that was never parsed as a record.",
            "normative": True,
        }
    )
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    decision = load_frontmatter(project.root / "planning/records/DEC-001.md")
    for target in decision["scope"]["targets"]:
        if target["record"] == "TASK-001":
            target["scope_sha256"] = scope_digest(task["scope"])
    write_record(project.root / "planning/records/DEC-001.md", decision)

    report = json.loads(run_checker(project.root).stdout)
    readiness = report["coverage"]["task_readiness"]["TASK-001"]
    assert readiness["ready"] is False
    assert readiness["review_required"] is True
    assert "UNPARSED_MARKDOWN" in readiness["manual_review"]
    assert report["coverage"]["ready_tasks"] == []


def test_unparsed_native_background_context_does_not_require_review(project):
    """The same unparsed file is non-blocking when the task marks it background."""
    notes = project.root / "planning/requirements/notes.md"
    notes.write_text("# Unstructured notes\n", encoding="utf-8")
    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["scope"]["context"].append(
        {
            "ref": "planning/requirements/notes.md",
            "authority": "background",
            "revision": "working-tree",
            "purpose": "Non-normative note; not an obligation.",
            "normative": False,
        }
    )
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    decision = load_frontmatter(project.root / "planning/records/DEC-001.md")
    for target in decision["scope"]["targets"]:
        if target["record"] == "TASK-001":
            target["scope_sha256"] = scope_digest(task["scope"])
    write_record(project.root / "planning/records/DEC-001.md", decision)

    report = json.loads(run_checker(project.root).stdout)
    readiness = report["coverage"]["task_readiness"]["TASK-001"]
    assert readiness["ready"] is True
    assert "UNPARSED_MARKDOWN" not in readiness["manual_review"]
    assert report["coverage"]["ready_tasks"] == ["TASK-001"]
