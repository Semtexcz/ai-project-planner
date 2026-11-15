"""Schema and asset contracts for native records (I03)."""

from __future__ import annotations

import hashlib
import json

import jsonschema
import pytest
import yaml

from support import ASSET_DIR, load_schema, run_checker, scope_digest


def validator():
    return jsonschema.Draft202012Validator(load_schema("record.schema.json"))


def project_validator():
    return jsonschema.Draft202012Validator(load_schema("project.schema.json"))


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    _, raw, _ = text.split("---\n", 2)
    return yaml.safe_load(raw)


def test_default_project_records_validate(project):
    schema = validator()
    for path in [
        project.root / "planning/strategy.md",
        project.root / "planning/requirements/REQ-001.md",
        project.root / "planning/milestones/MS-001.md",
        project.root / "planning/tasks/TASK-001.md",
        project.root / "planning/records/DEC-001.md",
    ]:
        schema.validate(frontmatter(path))
    project_validator().validate(yaml.safe_load(
        (project.root / "planning/planner.yaml").read_text(encoding="utf-8")
    ))


def test_representative_methodology_and_engineering_records_validate(tmp_path):
    schema = validator()
    methodology = {
        "schema_version": 1,
        "kind": "task",
        "id": "TASK-201",
        "owner": "task_owner",
        "scope": {
            "title": "Review definition consistency for the conceptual model",
            "objective": "OBJ-001",
            "rationale": "The methodology must not contain contradictory definitions.",
            "milestone": "MS-001",
            "requirements": ["CON-01"],
            "include": ["Compare definition A with definition B"],
            "exclude": ["none - no software artifact is produced"],
            "depends_on": [],
            "context": [
                {
                    "ref": "docs/glossary.md",
                    "authority": "glossary",
                    "revision": "HEAD",
                    "purpose": "The definitions under review.",
                    "normative": True,
                }
            ],
            "deliverables": [{"description": "A reviewed semantic consistency report"}],
            "acceptance": [
                {"id": "TASK-201:AC-1", "statement": "Every contradiction cites both definitions."}
            ],
            "verification": [
                {
                    "criteria": ["TASK-201:AC-1"],
                    "method": "Semantic walkthrough and counterexample review by a domain reviewer.",
                    "expected_evidence": "A signed review report with limitations.",
                    "reviewer": "domain_reviewer",
                }
            ],
            "approvals": [],
            "priority": "P2",
            "size": "S",
        },
        "execution": {
            "state": "draft",
            "authorization": [],
            "evidence": [],
            "blockers": [],
            "progress_notes": [],
        },
    }
    engineering = {
        "schema_version": 1,
        "kind": "requirement",
        "id": "CON-01",
        "owner": "product_owner",
        "scope": {
            "statement": "The model must preserve dimensional consistency for all energy terms.",
            "classification": "constraint",
            "objectives": ["OBJ-001"],
            "sources": ["docs/engineering-constraints.md#semantic-core"],
            "acceptance": [
                {
                    "id": "CON-01:AC-1",
                    "statement": "Each term declares units and a dimensional check passes.",
                }
            ],
            "verification": [
                {
                    "criteria": ["CON-01:AC-1"],
                    "method": "Dimensional analysis and a bounded counterexample review.",
                    "expected_evidence": "A documented analysis with assumptions and limits.",
                    "reviewer": "domain_reviewer",
                }
            ],
            "supersedes": [],
        },
        "execution": {
            "state": "proposed",
            "approvals": [],
            "evidence": [],
            "blockers": [],
            "progress_notes": [],
        },
    }
    schema.validate(methodology)
    schema.validate(engineering)


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda r: r["scope"].pop("exclude"), id="missing-exclude"),
        pytest.param(lambda r: r["scope"].pop("approvals"), id="missing-approvals"),
        pytest.param(lambda r: r["scope"].pop("acceptance"), id="missing-criteria"),
        pytest.param(lambda r: r["scope"].__setitem__("priority", "P9"), id="bad-priority"),
        pytest.param(lambda r: r["scope"].__setitem__("objective", "REQ-1"), id="bad-objective-ref"),
        pytest.param(lambda r: r["execution"].__setitem__("state", "final"), id="bad-state"),
        pytest.param(lambda r: r.__setitem__("schema_version", 2), id="unknown-schema"),
        pytest.param(lambda r: r.__setitem__("unexpected", True), id="unknown-top-level-field"),
    ],
)
def test_invalid_records_fail_schema(project, mutate):
    record = frontmatter(project.root / "planning/tasks/TASK-001.md")
    mutate(record)
    with pytest.raises(jsonschema.ValidationError):
        validator().validate(record)


def test_scope_digest_ignores_execution_changes(project):
    record = frontmatter(project.root / "planning/tasks/TASK-001.md")
    before = scope_digest(record["scope"])
    record["execution"]["state"] = "in_progress"
    record["execution"]["progress_notes"].append("Started review.")
    record["execution"]["evidence"].append(
        {
            "id": "TASK-001:EV-1",
            "criteria": ["TASK-001:AC-1"],
            "method": "Read the report",
            "subject_revision": "abc123",
            "result": "pass",
            "artifact": "planning/evidence/demo.md",
            "reviewer": "domain_reviewer",
            "limitations": "Single reviewer.",
            "observed_at": "2026-11-15",
        }
    )
    assert scope_digest(record["scope"]) == before


def test_scope_digest_unicode_vector_is_defined():
    scope = {"purpose": "Příliš žluťoučký kůň – „quotes“", "n": 1}
    expected = "99088f24e35949834108813271b970e5aaca571fe81217175181271d7bee084d"
    assert scope_digest(scope) == expected
    # The digest is over a JSON value, not file bytes: CRLF and ASCII escaping
    # cannot change it.
    payload = json.dumps(scope, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    assert hashlib.sha256(payload.encode("utf-8")).hexdigest() == expected


def test_blank_assets_validate_but_are_not_approved_or_ready():
    schema = validator()
    assets = [
        "strategy.md",
        "requirement.md",
        "milestone.md",
        "task.md",
        "decision.md",
        "change.md",
    ]
    for name in assets:
        record = frontmatter(ASSET_DIR / name)
        schema.validate(record)
        assert record["id"].endswith("-000"), name
        state = record["execution"]["state"]
        assert state in {"proposed", "draft", "captured"}, name
        assert record["id"] != "VIS-001"  # never a real seeded identity


def test_blank_project_config_validates():
    config = yaml.safe_load((ASSET_DIR / "project-config.yaml").read_text(encoding="utf-8"))
    project_validator().validate(config)
    assert config["project_id"] == "replace-me"
    assert config["current_milestone"] is None


def test_project_config_rejects_mirrored_scope_or_unknown_state():
    config = yaml.safe_load((ASSET_DIR / "project-config.yaml").read_text(encoding="utf-8"))
    config["requirements"] = [{"id": "REQ-001", "state": "done"}]
    with pytest.raises(jsonschema.ValidationError):
        project_validator().validate(config)


def test_file_line_endings_do_not_change_scope_identity(project):
    path = project.root / "planning/tasks/TASK-001.md"
    before = scope_digest(frontmatter(path)["scope"])
    path.write_bytes(path.read_text(encoding="utf-8").replace("\n", "\r\n").encode("utf-8"))
    after = scope_digest(frontmatter(path)["scope"])
    assert before == after
    result = run_checker(project.root)
    assert result.returncode == 0, result.stdout


def test_retired_requirement_cannot_satisfy_a_ready_task(project):
    from support import load_frontmatter, write_record

    requirement = load_frontmatter(project.root / "planning/requirements/REQ-001.md")
    requirement["execution"]["state"] = "retired"
    write_record(project.root / "planning/requirements/REQ-001.md", requirement)
    import json

    report = json.loads(run_checker(project.root).stdout)
    assert any(
        finding["rule"] == "TASK_REQUIREMENT_NOT_APPROVED"
        for finding in report["findings"]
    )
    assert report["coverage"]["ready_tasks"] == []
