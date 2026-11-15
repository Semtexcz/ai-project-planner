"""Optional OpenSpec and adopted existing-authority boundaries (I18)."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from support import (
    PLANNER_ROOT,
    CHECKER,
    init_git_repo,
    make_project,
    run_checker,
    tree_hashes,
    write_record,
)


def openspec(npx: str, version: str, *args: str, cwd: Path):
    return subprocess.run(
        [npx, "--yes", f"@fission-ai/openspec@{version}", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )


def test_adopted_bmad_tracking_creates_no_native_mirror(tmp_path):
    project = make_project(tmp_path / "project").write()
    config = yaml.safe_load(
        (project.root / "planning/planner.yaml").read_text(encoding="utf-8")
    )
    config["authorities"] = [
        authority
        for authority in config["authorities"]
        if authority.get("kind") != "task"
    ]
    config["task_order"] = []
    config["authorities"].append(
        {
            "kind": "task",
            "id": "TASK-075",
            "owner": "task_owner",
            "ref": "sprint-status.yaml",
            "locator": "development_status.TASK-075",
            "format": "markdown",
        }
    )
    (project.root / "planning/planner.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
    )
    (project.root / "sprint-status.yaml").write_text(
        "development_status:\n  TASK-075: in-progress\n", encoding="utf-8"
    )
    (project.root / "planning/tasks/TASK-001.md").unlink()
    decision = yaml.safe_load(
        (project.root / "planning/records/DEC-001.md").read_text(encoding="utf-8")
        .split("---\n", 2)[1]
    )
    decision["scope"]["targets"] = [
        target for target in decision["scope"]["targets"] if target["record"] != "TASK-001"
    ]
    write_record(
        project.root / "planning/records/DEC-001.md", decision
    )
    write_record(
        project.root / "planning/records/CHG-001.md",
        {
            "schema_version": 1,
            "kind": "change",
            "id": "CHG-001",
            "owner": "product_owner",
            "scope": {
                "idea": "Reference the adopted BMAD tracking item.",
                "source": "Fixture",
                "affected": ["TASK-075"],
                "impact": "No native mirror is created.",
                "alternatives": ["Create a second task record"],
                "proposed_delta": "Store a pointer only.",
                "required_approvals": ["product_owner"],
            },
            "execution": {
                "state": "captured",
                "disposition_decision": None,
                "applied_revision": None,
                "blockers": [],
                "progress_notes": [],
            },
        },
    )
    report = json.loads(run_checker(project.root).stdout)
    assert report["result"]["errors"] == 0
    assert report["coverage"]["records_by_kind"]["task"] == 0
    assert report["coverage"]["adopted_records"] == 1
    assert ("EXTERNAL_REFERENCE_UNVERIFIED", "manual_review") in {
        (finding["rule"], finding["severity"]) for finding in report["findings"]
    }


def test_planner_has_no_custom_openspec_parser_or_auto_init():
    checker = (PLANNER_ROOT / "scripts/check_planning.py").read_text(encoding="utf-8")
    assert "import subprocess" not in checker
    assert "openspec/specs" not in checker.lower()
    assert "openspec validate" not in checker.lower()
    for skill in (PLANNER_ROOT / "skills").glob("*/SKILL.md"):
        text = skill.read_text(encoding="utf-8").lower()
        assert "openspec apply" not in text
        assert "openspec init" not in text or "never" in text or "do not" in text


@pytest.mark.integration
@pytest.mark.parametrize(
    ("version", "skill_root", "commands_root"),
    [
        ("1.16.0", ".opencode/skills", ".opencode/commands"),
        ("2.0.0", ".agents/skills", None),
    ],
)
def test_native_openspec_versions_generate_expected_paths(
    version, skill_root, commands_root, tmp_path
):
    npx = shutil.which("npx")
    if npx is None:
        pytest.skip("npx is not available")
    from test_template import copy_template, make_tagged_template

    template = make_tagged_template(tmp_path)
    project = tmp_path / "project"
    copied = copy_template(template, project)
    assert copied.returncode == 0, copied.stderr
    planner_before = tree_hashes(project / ".planner")

    init = openspec(
        npx, version, "init", "--tools", "opencode", "--no-animation", ".", cwd=project
    )
    assert init.returncode == 0, (init.stdout, init.stderr)
    assert (project / "openspec/config.yaml").is_file()
    assert (project / skill_root / "openspec-propose/SKILL.md").is_file()
    if commands_root:
        assert (project / commands_root / "opsx-propose.md").is_file()
    else:
        assert not (project / ".opencode/skills").exists()

    validate = openspec(
        npx, version, "validate", "--specs", "--no-interactive", cwd=project
    )
    assert validate.returncode == 0, (validate.stdout, validate.stderr)

    # Framework generation never claims or mutates planner-owned bytes.
    assert tree_hashes(project / ".planner") == planner_before
    assert not (project / ".planner/skills/openspec-propose").exists()


def test_external_issue_authority_is_manual_review_not_a_parser(tmp_path):
    project = tmp_path / "issue-project"
    (project / "planning").mkdir(parents=True)
    config = {
        "schema_version": 1,
        "project_id": "issue-fixture",
        "name": "Issue Fixture",
        "category": "software",
        "content_root": "planning",
        "roles": {"product_owner": "Owner", "task_owner": "Task Owner"},
        "authorities": [
            {
                "kind": "task",
                "id": "TASK-075",
                "owner": "task_owner",
                "ref": "https://github.com/Semtexcz/Bookvoice/issues/75",
                "locator": "body and acceptance section",
                "format": "issue",
            }
        ],
        "aliases": [],
        "current_milestone": None,
        "task_order": [],
        "verification_profiles": ["software"],
        "review_policy": {"periodic_review": "weekly"},
    }
    (project / "planning/planner.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
    )
    report = json.loads(run_checker(project).stdout)
    assert report["result"]["errors"] == 0
    assert report["coverage"]["adopted_records"] == 1
    assert any(
        finding["rule"] == "EXTERNAL_AUTHORITY_UNVERIFIED" for finding in report["findings"]
    )
    assert any("fresh read" in finding["message"] for finding in report["findings"])

    config["authorities"][0]["format"] = "markdown"
    (project / "planning/planner.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
    )
    report = json.loads(run_checker(project).stdout)
    assert report["result"]["errors"] == 1
    assert any(
        finding["rule"] == "UNSAFE_AUTHORITY_REF" for finding in report["findings"]
    )

    config["authorities"][0]["format"] = "issue"
    config["authorities"].append(dict(config["authorities"][0]))
    (project / "planning/planner.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
    )
    report = json.loads(run_checker(project).stdout)
    assert any(
        finding["rule"] == "DUPLICATE_ADOPTED_ID" for finding in report["findings"]
    )
