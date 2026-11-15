"""Content-bound approval and evidence checks (I06)."""

from __future__ import annotations

import json

import pytest
import yaml

from support import load_frontmatter, run_checker, scope_digest, write_record

TASK = "planning/tasks/TASK-001.md"
DECISION = "planning/records/DEC-001.md"


def rewrite(root, rel, data):
    write_record(root / rel, data)


def rules(report):
    return {(finding["rule"], finding["severity"]) for finding in report["findings"]}


def check(project, *extra):
    return json.loads(run_checker(project.root, "json", *extra).stdout)


def test_valid_approvals_pass_but_identity_is_manual_review(project):
    report = check(project)
    assert report["result"]["errors"] == 0
    assert ("APPROVAL_IDENTITY_UNVERIFIED", "manual_review") in rules(report)


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda s: s["include"].append("Also upload to a server"), id="include"),
        pytest.param(lambda s: s["exclude"].clear(), id="exclude"),
        pytest.param(
            lambda s: s["acceptance"][0].__setitem__("statement", "A changed criterion."),
            id="criterion",
        ),
        pytest.param(lambda s: s.__setitem__("size", "L"), id="size"),
        pytest.param(lambda s: s.__setitem__("priority", "P0"), id="priority"),
    ],
)
def test_normative_change_invalidates_prior_approval(project, mutate):
    task = load_frontmatter(project.root / TASK)
    mutate(task["scope"])
    rewrite(project.root, TASK, task)
    report = check(project)
    assert ("APPROVAL_STALE", "error") in rules(report)
    assert ("TASK_NOT_AUTHORIZED", "error") in rules(report)
    assert report["coverage"]["task_readiness"]["TASK-001"]["ready"] is False


def test_execution_and_evidence_changes_preserve_scope_approval(project):
    task = load_frontmatter(project.root / TASK)
    before = scope_digest(task["scope"])
    task["execution"]["state"] = "in_progress"
    task["execution"]["progress_notes"].append("Started.")
    task["execution"]["evidence"].append(
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
    )
    rewrite(project.root, TASK, task)
    report = check(project)
    assert scope_digest(task["scope"]) == before
    assert ("APPROVAL_STALE", "error") not in rules(report)
    assert report["result"]["errors"] == 0


def test_missing_approval_blocks_ready_task(project):
    task = load_frontmatter(project.root / TASK)
    task["scope"]["approvals"] = []
    rewrite(project.root, TASK, task)
    report = check(project)
    assert ("APPROVAL_MISSING", "error") in rules(report)
    assert ("TASK_NOT_AUTHORIZED", "error") in rules(report)
    assert report["coverage"]["task_readiness"]["TASK-001"]["ready"] is False


@pytest.mark.parametrize("state", ["proposed", "rejected", "superseded"])
def test_unaccepted_decision_cannot_authorize(project, state):
    decision = load_frontmatter(project.root / DECISION)
    decision["execution"]["state"] = state
    rewrite(project.root, DECISION, decision)
    report = check(project)
    assert ("APPROVAL_DECISION_NOT_ACCEPTED", "error") in rules(report)


def test_decision_requires_actor_date_and_source(project):
    decision = load_frontmatter(project.root / DECISION)
    decision["execution"]["actor"] = ""
    decision["execution"]["decided_at"] = "not-a-date"
    rewrite(project.root, DECISION, decision)
    report = check(project)
    assert ("APPROVAL_PROVENANCE_INCOMPLETE", "error") in rules(report)
    assert ("APPROVAL_IDENTITY_UNVERIFIED", "manual_review") in rules(report)


def test_forged_accepted_flag_is_structurally_valid_but_not_authenticated(project):
    # A schema-valid accepted record written by an agent still only reaches a
    # manual review item; the checker never proves consent.
    report = check(project)
    assert report["result"]["ok"] is True
    identity = [
        finding
        for finding in report["findings"]
        if finding["rule"] == "APPROVAL_IDENTITY_UNVERIFIED"
    ]
    assert identity
    assert "cannot authenticate identity or consent" in identity[0]["message"]


def delegated_decision(project, covers):
    decision = load_frontmatter(project.root / DECISION)
    decision["scope"]["targets"] = [
        target for target in decision["scope"]["targets"] if target["record"] != "TASK-001"
    ]
    decision["scope"]["delegation"] = {
        "covers": covers,
        "exclusions": ["No new requirement or milestone outcome"],
        "permitted_decisions": ["Decompose approved milestone work into bounded tasks"],
        "stop_conditions": ["Stop before expanding scope or starting a distant milestone"],
    }
    rewrite(project.root, DECISION, decision)


def test_bounded_delegation_authorizes_with_manual_review(project):
    delegated_decision(project, ["TASK-001"])
    report = check(project)
    assert ("APPROVAL_DELEGATED", "manual_review") in rules(report)
    assert ("TASK_NOT_AUTHORIZED", "error") not in rules(report)
    assert report["result"]["errors"] == 0


def test_delegation_must_cover_the_task(project):
    delegated_decision(project, ["TASK-999"])
    report = check(project)
    assert ("APPROVAL_TARGET_MISSING", "error") in rules(report)
    assert ("TASK_NOT_AUTHORIZED", "error") in rules(report)


def milestone_evidence(project, result):
    milestone = load_frontmatter(project.root / "planning/milestones/MS-001.md")
    milestone["execution"]["state"] = "achieved"
    milestone["execution"]["evidence"] = [
        {
            "id": "MS-001:EV-1",
            "criteria": ["MS-001:EXIT-1"],
            "method": "Demonstration review.",
            "subject_revision": "working-tree",
            "result": result,
            "artifact": "planning/evidence/demo-report.md",
            "reviewer": "product_owner",
            "limitations": "One reviewer.",
            "observed_at": "2026-11-15",
        }
    ]
    rewrite(project.root, "planning/milestones/MS-001.md", milestone)
    # Avoid an unrelated ready-task-under-achieved-milestone error so the
    # milestone evidence rule is exercised on its own.
    task = load_frontmatter(project.root / TASK)
    task["execution"]["state"] = "cancelled"
    task["execution"]["blockers"] = [{"description": "Evidence fixture isolation"}]
    rewrite(project.root, TASK, task)
    return check(project)


def test_failed_evidence_cannot_imply_achieved_milestone(project):
    report = milestone_evidence(project, "fail")
    assert ("MILESTONE_EVIDENCE_FAILED", "error") in rules(report)


def test_inconclusive_evidence_does_not_imply_achieved_milestone(project):
    report = milestone_evidence(project, "inconclusive")
    assert ("MILESTONE_EVIDENCE_INCONCLUSIVE", "error") in rules(report)
    assert not [
        finding
        for finding in report["findings"]
        if finding["rule"].startswith("TASK_")
    ]


def test_achieved_milestone_without_evidence_fails(project):
    milestone = load_frontmatter(project.root / "planning/milestones/MS-001.md")
    milestone["execution"]["state"] = "achieved"
    rewrite(project.root, "planning/milestones/MS-001.md", milestone)
    report = check(project)
    assert ("MILESTONE_EVIDENCE_MISSING", "error") in rules(report)


def test_done_task_with_failed_evidence(project):
    task = load_frontmatter(project.root / TASK)
    task["execution"]["state"] = "done"
    task["execution"]["evidence"] = [
        {
            "id": "TASK-001:EV-1",
            "criteria": ["TASK-001:AC-1"],
            "method": "Read the report.",
            "subject_revision": "working-tree",
            "result": "fail",
            "artifact": "planning/evidence/demo.md",
            "reviewer": "domain_reviewer",
            "limitations": "Single reviewer.",
            "observed_at": "2026-11-15",
        }
    ]
    rewrite(project.root, TASK, task)
    report = check(project)
    assert ("TASK_DONE_EVIDENCE_FAILED", "error") in rules(report)


def test_evidence_requires_reviewer_and_known_criterion(project):
    task = load_frontmatter(project.root / TASK)
    task["execution"]["evidence"] = [
        {
            "id": "TASK-001:EV-1",
            "criteria": ["TASK-001:AC-999"],
            "method": "Read.",
            "subject_revision": "working-tree",
            "result": "pass",
            "artifact": "planning/evidence/demo.md",
            "reviewer": "",
            "limitations": "None.",
            "observed_at": "2026-11-15",
        }
    ]
    rewrite(project.root, TASK, task)
    report = check(project)
    assert ("RECORD_SCHEMA", "error") in rules(report)
    assert ("EVIDENCE_UNKNOWN_CRITERION", "error") in rules(report)


def test_stale_evidence_subject_revision_is_reported(project):
    task = load_frontmatter(project.root / TASK)
    task["execution"]["evidence"] = [
        {
            "id": "TASK-001:EV-1",
            "criteria": ["TASK-001:AC-1"],
            "method": "Read.",
            "subject_revision": "old-revision",
            "result": "pass",
            "artifact": "planning/evidence/demo.md",
            "reviewer": "domain_reviewer",
            "limitations": "None.",
            "observed_at": "2026-11-15",
        }
    ]
    rewrite(project.root, TASK, task)
    report = check(project, "--source-revision", "new-revision")
    assert ("EVIDENCE_REVISION_STALE", "warning") in rules(report)
    assert ("EVIDENCE_EFFECTIVENESS", "manual_review") in rules(report)


def test_decision_target_drift_is_visible(project):
    requirement = load_frontmatter(project.root / "planning/requirements/REQ-001.md")
    requirement["scope"]["statement"] = "A changed obligation."
    rewrite(project.root, "planning/requirements/REQ-001.md", requirement)
    report = check(project)
    assert ("DECISION_TARGET_DRIFT", "warning") in rules(report)
    assert ("APPROVAL_STALE", "error") in rules(report)


def test_applied_change_requires_an_applied_revision(project):
    change = {
        "schema_version": 1,
        "kind": "change",
        "id": "CHG-001",
        "owner": "product_owner",
        "scope": {
            "idea": "A recorded change.",
            "source": "Fixture",
            "affected": ["TASK-001"],
            "impact": "Bounded.",
            "alternatives": ["Do nothing."],
            "proposed_delta": "No scope change in this fixture.",
            "required_approvals": ["product_owner"],
        },
        "execution": {
            "state": "applied",
            "disposition_decision": "DEC-001",
            "applied_revision": None,
            "blockers": [],
            "progress_notes": [],
        },
    }
    write_record(project.root / "planning/records/CHG-001.md", change)
    report = check(project)
    assert ("CHANGE_APPLIED_REVISION_MISSING", "error") in rules(report)


def test_change_disposition_requires_an_accepted_provenanced_decision(project):
    change = {
        "schema_version": 1,
        "kind": "change",
        "id": "CHG-001",
        "owner": "product_owner",
        "scope": {
            "idea": "A rejected idea.",
            "source": "Fixture",
            "affected": ["TASK-001"],
            "impact": "None.",
            "alternatives": ["Do nothing."],
            "proposed_delta": "No change.",
            "required_approvals": ["product_owner"],
            "revisit_trigger": "If priorities change.",
        },
        "execution": {
            "state": "rejected",
            "disposition_decision": "DEC-002",
            "applied_revision": None,
            "blockers": [],
            "progress_notes": [],
        },
    }
    digest = scope_digest(change["scope"])
    decision = {
        "schema_version": 1,
        "kind": "decision",
        "id": "DEC-002",
        "owner": "product_owner",
        "scope": {
            "topic": "Reject the idea",
            "rationale": "Out of scope.",
            "options": ["Reject", "Defer"],
            "choice": "Reject",
            "targets": [{"record": "CHG-001", "scope_sha256": digest}],
            "authority": "Product Owner",
            "supersedes": [],
        },
        "execution": {
            "state": "proposed",
            "actor": "",
            "decided_at": "",
            "approval_source": "",
            "applied_revision": None,
        },
    }
    write_record(project.root / "planning/records/CHG-001.md", change)
    write_record(project.root / "planning/records/DEC-002.md", decision)
    report = check(project)
    assert ("CHANGE_DISPOSITION_NOT_ACCEPTED", "error") in rules(report)

    decision["execution"] = {
        "state": "accepted",
        "actor": "",
        "decided_at": "2026-11-15",
        "approval_source": "",
        "applied_revision": None,
    }
    write_record(project.root / "planning/records/DEC-002.md", decision)
    report = check(project)
    assert ("CHANGE_DISPOSITION_PROVENANCE_INCOMPLETE", "error") in rules(report)


def test_strategy_approved_without_approval_is_rejected(project):
    strategy = load_frontmatter(project.root / "planning/strategy.md")
    strategy["execution"]["approvals"] = []
    write_record(project.root / "planning/strategy.md", strategy)
    report = check(project)
    assert ("APPROVAL_MISSING", "error") in rules(report)
    assert report["coverage"]["ready_tasks"] == []


def test_unreferenced_accepted_decision_requires_provenance(project):
    decision = {
        "schema_version": 1,
        "kind": "decision",
        "id": "DEC-002",
        "owner": "product_owner",
        "scope": {
            "topic": "An accepted decision with no provenance",
            "rationale": "Fixture.",
            "options": ["Accept"],
            "choice": "Accept",
            "targets": [],
            "authority": "Product Owner",
            "supersedes": [],
        },
        "execution": {
            "state": "accepted",
            "actor": "",
            "decided_at": "2026-99-99",
            "approval_source": "",
            "applied_revision": None,
        },
    }
    write_record(project.root / "planning/records/DEC-002.md", decision)
    report = check(project)
    assert ("APPROVAL_PROVENANCE_INCOMPLETE", "error") in rules(report)


def test_inconclusive_done_task_is_not_done(project):
    task = load_frontmatter(project.root / TASK)
    task["execution"]["state"] = "done"
    task["execution"]["evidence"] = [
        {
            "id": "TASK-001:EV-1",
            "criteria": ["TASK-001:AC-1"],
            "method": "Read.",
            "subject_revision": "working-tree",
            "result": "inconclusive",
            "artifact": "planning/evidence/demo.md",
            "reviewer": "domain_reviewer",
            "limitations": "Single reviewer.",
            "observed_at": "2026-11-15",
        }
    ]
    rewrite(project.root, TASK, task)
    report = check(project)
    assert ("TASK_DONE_EVIDENCE_INCONCLUSIVE", "error") in rules(report)


def test_impossible_calendar_date_is_rejected(project):
    task = load_frontmatter(project.root / TASK)
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
            "observed_at": "2026-99-99",
        }
    ]
    rewrite(project.root, TASK, task)
    report = check(project)
    assert ("EVIDENCE_DATE_INVALID", "error") in rules(report)
