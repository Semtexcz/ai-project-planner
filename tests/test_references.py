"""Read-only structural checker behaviour (I05)."""

from __future__ import annotations

import json
import hashlib
import os
import shutil
import subprocess
import sys

import pytest
import yaml

from support import (
    CHECKER,
    load_frontmatter,
    make_project,
    run_checker,
    tree_hashes,
    write_record,
)


def assert_rule(report, rule, severity="error"):
    rules = {(finding["rule"], finding["severity"]) for finding in report["findings"]}
    assert (rule, severity) in rules, report["findings"]


def test_valid_project_exits_zero_with_manual_review(project):
    result = run_checker(project.root)
    report = json.loads(result.stdout)
    assert result.returncode == 0
    assert report["report_version"] == 1
    assert report["result"]["ok"] is True
    assert report["result"]["errors"] == 0
    assert report["result"]["manual_review_required"] >= 1
    assert report["coverage"]["ready_tasks"] == ["TASK-001"]
    assert report["coverage"]["records_by_kind"]["task"] == 1


def test_dangling_and_type_invalid_references(project):
    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["scope"]["milestone"] = "MS-999"
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    report = json.loads(run_checker(project.root).stdout)
    assert_rule(report, "REFERENCE_DANGLING")

    task["scope"]["milestone"] = "MS-001"
    task["scope"]["requirements"] = ["OBJ-001"]
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    report = json.loads(run_checker(project.root).stdout)
    assert_rule(report, "REFERENCE_TYPE")


def test_missing_and_unsafe_context_paths(project):
    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["scope"]["context"][0]["ref"] = "planning/missing.md"
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    report = json.loads(run_checker(project.root).stdout)
    assert_rule(report, "MISSING_CONTEXT")

    task["scope"]["context"][0]["ref"] = "../outside.md"
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    report = json.loads(run_checker(project.root).stdout)
    assert_rule(report, "UNSAFE_CONTEXT_PATH")


def test_context_content_hash_overrides_older_revision(project):
    from support import scope_digest

    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    context = task["scope"]["context"][0]
    context["revision"] = "old-commit"
    context["sha256"] = hashlib.sha256(
        (project.root / context["ref"]).read_bytes()
    ).hexdigest()
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    decision = load_frontmatter(project.root / "planning/records/DEC-001.md")
    for target in decision["scope"]["targets"]:
        if target["record"] == "TASK-001":
            target["scope_sha256"] = scope_digest(task["scope"])
    write_record(project.root / "planning/records/DEC-001.md", decision)

    report = json.loads(
        run_checker(project.root, "json", "--source-revision", "new-commit").stdout
    )
    rules = {(finding["rule"], finding["severity"]) for finding in report["findings"]}
    assert ("CONTEXT_REVISION_STALE", "warning") not in rules
    assert report["coverage"]["ready_tasks"] == ["TASK-001"]


def test_changed_normative_context_hash_blocks_readiness(project):
    from support import scope_digest

    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    context = task["scope"]["context"][0]
    context["revision"] = "old-commit"
    context["sha256"] = hashlib.sha256(
        (project.root / context["ref"]).read_bytes()
    ).hexdigest()
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    decision = load_frontmatter(project.root / "planning/records/DEC-001.md")
    for target in decision["scope"]["targets"]:
        if target["record"] == "TASK-001":
            target["scope_sha256"] = scope_digest(task["scope"])
    write_record(project.root / "planning/records/DEC-001.md", decision)
    with (project.root / context["ref"]).open("a", encoding="utf-8") as handle:
        handle.write("\nUnapproved appendix.\n")

    report = json.loads(
        run_checker(project.root, "json", "--source-revision", "new-commit").stdout
    )
    assert_rule(report, "CONTEXT_CONTENT_CHANGED")
    assert report["coverage"]["ready_tasks"] == []


def test_background_context_revision_does_not_block_readiness(project):
    from support import scope_digest

    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["scope"]["context"].append(
        {
            "ref": "planning/roadmap.md",
            "authority": "background",
            "revision": "old-commit",
            "purpose": "Historical roadmap view; not an obligation.",
            "normative": False,
        }
    )
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    decision = load_frontmatter(project.root / "planning/records/DEC-001.md")
    for target in decision["scope"]["targets"]:
        if target["record"] == "TASK-001":
            target["scope_sha256"] = scope_digest(task["scope"])
    write_record(project.root / "planning/records/DEC-001.md", decision)

    report = json.loads(
        run_checker(project.root, "json", "--source-revision", "new-commit").stdout
    )
    rules = {(finding["rule"], finding["severity"]) for finding in report["findings"]}
    assert ("CONTEXT_REVISION_STALE", "warning") not in rules
    assert report["coverage"]["ready_tasks"] == ["TASK-001"]


def test_symlink_escape_is_rejected(project, tmp_path):
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir(exist_ok=True)
    (outside / "secret.md").write_text("secret\n", encoding="utf-8")
    link = project.root / "planning/link.md"
    os.symlink(outside / "secret.md", link)
    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["scope"]["context"][0]["ref"] = "planning/link.md"
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    report = json.loads(run_checker(project.root).stdout)
    assert_rule(report, "UNSAFE_CONTEXT_PATH")

    (project.root / "planning/tasks/linked.md").symlink_to(outside / "secret.md")
    report = json.loads(run_checker(project.root).stdout)
    assert_rule(report, "SYMLINK_SKIPPED", "warning")


def test_context_ref_to_directory_is_reported_without_crash(project):
    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["scope"]["context"][0]["ref"] = "planning"
    task["scope"]["context"][0]["sha256"] = "0" * 64
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    result = run_checker(project.root)
    report = json.loads(result.stdout)
    assert_rule(report, "CONTEXT_NOT_FILE")
    assert result.returncode == 1


def test_duplicate_record_id(project):
    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    write_record(project.root / "planning/tasks/duplicate.md", task)
    report = json.loads(run_checker(project.root).stdout)
    assert_rule(report, "DUPLICATE_ID")


def test_duplicate_yaml_keys_are_rejected(project):
    path = project.root / "planning/tasks/TASK-001.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace("kind: task", "kind: task\nkind: task", 1)
    path.write_text(text, encoding="utf-8")
    result = run_checker(project.root)
    report = json.loads(result.stdout)
    assert result.returncode == 1
    assert_rule(report, "FRONTMATTER_INVALID")


def test_config_duplicate_keys_exit_2(project):
    path = project.root / "planning/planner.yaml"
    text = path.read_text(encoding="utf-8")
    path.write_text(text + "\nschema_version: 1\n", encoding="utf-8")
    result = run_checker(project.root)
    assert result.returncode == 2
    assert_rule(json.loads(result.stdout), "CONFIG_UNREADABLE")


def test_missing_and_invalid_config_exit_2(tmp_path):
    result = run_checker(tmp_path)
    assert result.returncode == 2
    assert_rule(json.loads(result.stdout), "CONFIG_MISSING")

    (tmp_path / "planning").mkdir()
    (tmp_path / "planning/planner.yaml").write_text("schema_version: 1\n", encoding="utf-8")
    result = run_checker(tmp_path)
    assert result.returncode == 2
    assert_rule(json.loads(result.stdout), "CONFIG_SCHEMA")


def test_unsupported_record_schema_exit_2(project):
    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["schema_version"] = 99
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    result = run_checker(project.root)
    assert result.returncode == 2
    assert_rule(json.loads(result.stdout), "UNSUPPORTED_SCHEMA")


def test_dependency_cycles_are_reported(project):
    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["scope"]["depends_on"] = ["TASK-002"]
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    second = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    second["id"] = "TASK-002"
    second["scope"] = dict(second["scope"], title="Second task", depends_on=["TASK-001"])
    second["scope"]["acceptance"] = [
        {"id": "TASK-002:AC-1", "statement": "Second task is complete."}
    ]
    second["scope"]["verification"] = [
        {
            "criteria": ["TASK-002:AC-1"],
            "method": "Review.",
            "expected_evidence": "A report.",
            "reviewer": "domain_reviewer",
        }
    ]
    second["scope"]["approvals"] = []
    second["execution"] = {
        "state": "draft",
        "authorization": [],
        "evidence": [],
        "blockers": [],
        "progress_notes": [],
    }
    write_record(project.root / "planning/tasks/TASK-002.md", second)
    report = json.loads(run_checker(project.root).stdout)
    assert_rule(report, "DEPENDENCY_CYCLE")


def test_multiple_active_milestones_and_current_mismatch(project):
    milestone = load_frontmatter(project.root / "planning/milestones/MS-001.md")
    second = yaml.safe_load(yaml.safe_dump(milestone))
    second["id"] = "MS-002"
    second["scope"]["outcome"] = "A second active milestone."
    second["execution"]["approvals"] = []
    second["scope"]["exit_criteria"] = [
        {"id": "MS-002:EXIT-1", "statement": "Second milestone exits."}
    ]
    second["scope"]["verification"] = [
        {
            "criteria": ["MS-002:EXIT-1"],
            "method": "Review.",
            "expected_evidence": "A report.",
            "reviewer": "product_owner",
        }
    ]
    second["execution"]["evidence"] = []
    write_record(project.root / "planning/milestones/MS-002.md", second)
    report = json.loads(run_checker(project.root).stdout)
    assert_rule(report, "MULTIPLE_ACTIVE_MILESTONES")
    assert_rule(report, "APPROVAL_MISSING")


def test_unknown_owner_invalid_package_and_unknown_task_order(project):
    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["owner"] = "nobody"
    task["scope"]["package"] = "WP-999"
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    config = yaml.safe_load((project.root / "planning/planner.yaml").read_text(encoding="utf-8"))
    config["task_order"] = ["TASK-999"]
    (project.root / "planning/planner.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
    )
    report = json.loads(run_checker(project.root).stdout)
    assert_rule(report, "UNKNOWN_OWNER")
    assert_rule(report, "INVALID_PACKAGE")
    assert_rule(report, "TASK_ORDER_UNKNOWN")


def test_unsafe_authority_root_is_rejected(project):
    config = yaml.safe_load((project.root / "planning/planner.yaml").read_text(encoding="utf-8"))
    config["authorities"][0]["root"] = "../outside"
    (project.root / "planning/planner.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
    )
    report = json.loads(run_checker(project.root).stdout)
    assert_rule(report, "UNSAFE_AUTHORITY_ROOT")


def test_aliases_resolve_and_dangling_alias_fails(project):
    config = yaml.safe_load((project.root / "planning/planner.yaml").read_text(encoding="utf-8"))
    config["aliases"] = [{"id": "FR-01", "target": "REQ-001", "note": "Legacy ID"}]
    (project.root / "planning/planner.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
    )
    change = {
        "schema_version": 1,
        "kind": "change",
        "id": "CHG-001",
        "owner": "product_owner",
        "scope": {
            "idea": "Use the legacy requirement identifier.",
            "source": "Alias fixture",
            "affected": ["FR-01"],
            "impact": "No normative change.",
            "alternatives": ["Keep the canonical ID."],
            "proposed_delta": "Record only.",
            "required_approvals": ["product_owner"],
        },
        "execution": {
            "state": "captured",
            "disposition_decision": None,
            "applied_revision": None,
            "blockers": [],
            "progress_notes": [],
        },
    }
    write_record(project.root / "planning/records/CHG-001.md", change)
    report = json.loads(run_checker(project.root).stdout)
    assert not [f for f in report["findings"] if f["rule"] == "REFERENCE_DANGLING"]

    config["aliases"].append({"id": "FR-02", "target": "REQ-999"})
    (project.root / "planning/planner.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
    )
    report = json.loads(run_checker(project.root).stdout)
    assert_rule(report, "DANGLING_ALIAS")
    assert report["coverage"]["ready_tasks"] == []
    assert (
        "global: DANGLING_ALIAS"
        in report["coverage"]["task_readiness"]["TASK-001"]["blockers"]
    )


def test_checker_is_read_only_and_does_not_execute_values(project):
    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["scope"]["verification"][0]["method"] = "Run `touch pwned` now"
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    before = tree_hashes(project.root)
    run_checker(project.root)
    after = tree_hashes(project.root)
    assert before == after
    assert not (project.root / "pwned").exists()
    from support import REPO_ROOT

    assert not (REPO_ROOT / "pwned").exists()


def test_text_output_keeps_manual_review_visible(project):
    result = run_checker(project.root, "text")
    assert result.returncode == 0
    assert "SEMANTIC_REVIEW_REQUIRED" in result.stdout
    assert "not a strategic PASS" in result.stdout


def test_invalid_invocation_exits_2(tmp_path):
    bad_format = subprocess.run(
        [sys.executable, str(CHECKER), "--project", str(tmp_path), "--format", "yaml"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert bad_format.returncode == 2
    missing = subprocess.run(
        [sys.executable, str(CHECKER), "--project", str(tmp_path / "missing")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert missing.returncode == 2


def test_unparsed_markdown_is_manual_review_not_silence(project):
    (project.root / "planning/tasks/NOTES.md").write_text("# free notes\n", encoding="utf-8")
    report = json.loads(run_checker(project.root).stdout)
    assert report["coverage"]["unparsed_markdown"] == 1
    assert_rule(report, "UNPARSED_MARKDOWN", "manual_review")


@pytest.mark.integration
def test_deployed_pep723_checker_entrypoint(project):
    import shutil

    uv = shutil.which("uv")
    if uv is None:
        pytest.skip("uv is not available")
    result = subprocess.run(
        [
            uv,
            "run",
            "--script",
            str(CHECKER),
            "--project",
            str(project.root),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    assert result.returncode == 0, (result.stdout, result.stderr)
    report = json.loads(result.stdout)
    assert report["report_version"] == 1
    assert report["result"]["errors"] == 0


def test_alias_canonicalization_avoids_false_orphans(project):
    config = yaml.safe_load(
        (project.root / "planning/planner.yaml").read_text(encoding="utf-8")
    )
    config["aliases"] = [
        {"id": "FR-01", "target": "REQ-001", "note": "Legacy requirement ID"},
        {"id": "MS-LEGACY", "target": "MS-001", "note": "Legacy milestone ID"},
    ]
    (project.root / "planning/planner.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
    )
    task = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    task["scope"]["requirements"] = ["FR-01"]
    task["scope"]["milestone"] = "MS-LEGACY"
    write_record(project.root / "planning/tasks/TASK-001.md", task)
    milestone = load_frontmatter(project.root / "planning/milestones/MS-001.md")
    milestone["scope"]["requirements"] = ["FR-01"]
    write_record(project.root / "planning/milestones/MS-001.md", milestone)
    report = json.loads(run_checker(project.root).stdout)
    rules = {finding["rule"] for finding in report["findings"]}
    assert "REFERENCE_DANGLING" not in rules
    assert "REFERENCE_TYPE" not in rules
    assert "REQUIREMENT_NOT_DECOMPOSED" not in rules
    assert "TASK_REQUIREMENT_OUTSIDE_MILESTONE" not in rules


def test_project_path_with_spaces_and_unicode(tmp_path):
    root = tmp_path / "projekt s mezerou – žluťoučký kůň"
    make_project(root).write()
    result = run_checker(root)
    assert result.returncode == 0, result.stdout
    assert json.loads(result.stdout)["coverage"]["ready_tasks"] == ["TASK-001"]


def test_alias_cycles_are_diagnosed_without_crashing(project):
    config = yaml.safe_load(
        (project.root / "planning/planner.yaml").read_text(encoding="utf-8")
    )
    config["aliases"] = [
        {"id": "FR-01", "target": "FR-02"},
        {"id": "FR-02", "target": "FR-01"},
    ]
    (project.root / "planning/planner.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
    )
    result = run_checker(project.root)
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert_rule(report, "ALIAS_CYCLE")
    assert report["coverage"]["ready_tasks"] == []
    assert (
        "global: ALIAS_CYCLE"
        in report["coverage"]["task_readiness"]["TASK-001"]["blockers"]
    )


def test_duplicate_and_overlapping_authority_roots(project):
    config = yaml.safe_load(
        (project.root / "planning/planner.yaml").read_text(encoding="utf-8")
    )
    strategy_authority = {
        "kind": "strategy",
        "owner": "product_owner",
        "root": "planning/strategy.md",
    }
    config["authorities"].append(strategy_authority)
    (project.root / "planning/planner.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
    )
    report = json.loads(run_checker(project.root).stdout)
    assert_rule(report, "DUPLICATE_AUTHORITY")

    # Remove the duplicate, then add a broad task root that contains the
    # requirement root.
    seen_strategy = False
    deduped = []
    for authority in config["authorities"]:
        if authority == strategy_authority:
            if seen_strategy:
                continue
            seen_strategy = True
        deduped.append(authority)
    deduped.append({"kind": "task", "owner": "task_owner", "root": "planning"})
    config["authorities"] = deduped
    (project.root / "planning/planner.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
    )
    report = json.loads(run_checker(project.root).stdout)
    assert_rule(report, "OVERLAPPING_AUTHORITY_ROOTS")


def test_unhashable_yaml_keys_are_reported_without_crashing(project):
    (project.root / "planning/planner.yaml").write_text(
        "schema_version: 1\n? [a, b]\n: value\n", encoding="utf-8"
    )
    result = run_checker(project.root)
    assert result.returncode == 2
    assert_rule(json.loads(result.stdout), "CONFIG_UNREADABLE")
