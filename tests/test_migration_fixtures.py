"""Synthetic migration and domain-profile fixtures (I15-I17).

Nothing here reads or writes the real DeepPlant, Bookvoice or PLOS
repositories. Fixtures are copied into disposable temporary repositories.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from support import (
    git,
    init_git_repo,
    load_frontmatter,
    make_project,
    run_checker,
    scope_digest,
    tree_hashes,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"


# ----------------------------------------------------------------- helpers
def parse_bookvoice(root: Path) -> list[dict]:
    cards = []
    for path in sorted((root / "project").glob("*/TASK-*.md")):
        data = load_frontmatter(path)
        text = path.read_text(encoding="utf-8")
        cards.append(
            {
                "path": path.relative_to(root).as_posix(),
                "folder": path.parent.name,
                "id": data["id"],
                "status": data.get("status"),
                "priority": data.get("priority"),
                "depends_on": data.get("depends_on") or [],
                "related": data.get("related") or [],
                "artifact_gate": data.get("artifact_gate"),
                "body": text,
            }
        )
    return cards


def bookvoice_edges(cards: list[dict]) -> tuple[set, set]:
    blocking = set()
    related = set()
    for card in cards:
        for dependency in card["depends_on"]:
            blocking.add((card["id"], dependency))
        for other in card["related"]:
            related.add((card["id"], other))
    return blocking, related


def source_hashes(root: Path, manifest: dict) -> dict[str, str]:
    hashes = tree_hashes(root)
    return {path: hashes[path] for path in manifest["must_preserve"]}


def adoption_config(tasks: list[str], paths: dict[str, str]) -> dict:
    authorities = [
        {"kind": "strategy", "id": "VIS-001", "owner": "product_owner",
         "ref": "docs/ROADMAP.md", "locator": "#roadmap", "format": "markdown"},
        {"kind": "requirement", "id": "REQ-001", "owner": "product_owner",
         "ref": "docs/contracts/sync-contract.md", "locator": "whole document",
         "format": "markdown"},
        {"kind": "decision", "owner": "product_owner", "root": "planning/records"},
        {"kind": "change", "owner": "product_owner", "root": "planning/records"},
    ]
    for task_id in tasks:
        authorities.append(
            {
                "kind": "task",
                "id": task_id,
                "owner": "task_owner",
                "ref": paths[task_id],
                "locator": "frontmatter and body",
                "format": "markdown",
            }
        )
    return {
        "schema_version": 1,
        "project_id": "bookvoice-fixture",
        "name": "Bookvoice-like Fixture",
        "category": "software",
        "content_root": "planning",
        "roles": {
            "product_owner": "Fixture Product Owner",
            "task_owner": "Fixture task owner",
            "domain_reviewer": "Fixture reviewer",
        },
        "authorities": authorities,
        "aliases": [],
        "current_milestone": None,
        "task_order": [],
        "ordering_policy": "priority,roadmap,id",
        "verification_profiles": ["software"],
        "review_policy": {"periodic_review": "weekly"},
    }


def change_record(affected: list[str]) -> dict:
    return {
        "schema_version": 1,
        "kind": "change",
        "id": "CHG-001",
        "owner": "product_owner",
        "scope": {
            "idea": "Adopt the existing Bookvoice-like task authority by reference.",
            "source": "Synthetic fixture dry run",
            "affected": affected,
            "impact": "No source text is rewritten; IDs and edges are retained.",
            "alternatives": ["Create native replacements", "Adopt by reference"],
            "proposed_delta": "Register pointers in the authority map only.",
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


def can_apply_in_place(root: Path) -> bool:
    return not git("status", "--porcelain", cwd=root).strip()


class DuplicateAuthorityError(Exception):
    """Raised when a migration would silently choose between duplicate IDs."""


def bookvoice_authority_paths(
    cards: list[dict], adjudicated: dict[str, str] | None = None
) -> dict[str, str]:
    adjudicated = adjudicated or {}
    paths: dict[str, str] = {}
    duplicates: set[str] = set()
    for card in cards:
        task_id = card["id"]
        if task_id in paths:
            duplicates.add(task_id)
            if task_id not in adjudicated:
                raise DuplicateAuthorityError(
                    f"{task_id} occurs at {paths[task_id]} and {card['path']}; "
                    "adjudicate one authoritative occurrence before adoption"
                )
        if task_id in adjudicated:
            paths[task_id] = adjudicated[task_id]
        elif task_id not in paths:
            paths[task_id] = card["path"]
    missing = set(duplicates) - set(paths)
    if missing:
        raise DuplicateAuthorityError(f"unresolved duplicate IDs: {sorted(missing)}")
    return paths


def adopt_by_reference(
    root: Path, tasks: list[str], adjudicated: dict[str, str] | None = None
) -> None:
    cards = parse_bookvoice(root)
    paths = bookvoice_authority_paths(cards, adjudicated)
    (root / "planning").mkdir(exist_ok=True)
    (root / "planning/planner.yaml").write_text(
        yaml.safe_dump(adoption_config(tasks, paths), sort_keys=False), encoding="utf-8"
    )
    from support import write_record

    write_record(root / "planning/records/CHG-001.md", change_record(tasks))


def reconciliation(manifest: dict, adopted: list[str]) -> dict:
    expected = set(manifest["unique_task_ids"])
    actual = set(adopted)
    return {
        "missing": sorted(expected - actual),
        "extra": sorted(actual - expected),
        "complete": expected == actual,
    }


# --------------------------------------------------------------- Bookvoice
def test_bookvoice_fixture_inventory_and_edges_reconcile(tmp_path):
    fixture = FIXTURES / "bookvoice-like"
    manifest = json.loads((fixture / "manifest.json").read_text(encoding="utf-8"))
    root = tmp_path / "bookvoice"
    shutil.copytree(fixture, root)
    cards = parse_bookvoice(root)
    ids = sorted({card["id"] for card in cards})
    assert ids == manifest["unique_task_ids"]
    occurrences = {task_id: sum(card["id"] == task_id for card in cards) for task_id in ids}
    assert occurrences == manifest["occurrences"]
    assert occurrences["TASK-075"] == 2

    blocking, related = bookvoice_edges(cards)
    assert blocking == {tuple(edge) for edge in manifest["blocking_edges"]}
    assert related == {tuple(edge) for edge in manifest["related_edges"]}
    assert ("TASK-076", "TASK-075") in related
    assert ("TASK-076", "TASK-075") not in blocking
    gates = {
        (card["id"], card["artifact_gate"])
        for card in cards
        if card.get("artifact_gate")
    }
    assert gates == {tuple(edge) for edge in manifest["artifact_gates"]}

    ready_occurrence = next(
        card for card in cards if card["path"] == "project/ready/TASK-075.md"
    )
    assert ready_occurrence["folder"] == "ready"
    assert ready_occurrence["status"] == "done"
    assert "**Body state:** in progress" in ready_occurrence["body"]
    backlog = next(card for card in cards if card["id"] == "TASK-076")
    assert backlog["folder"] == "backlog"
    assert backlog["id"] in manifest["not_ready"]


def test_dry_run_creates_only_the_permitted_report(tmp_path):
    fixture = FIXTURES / "bookvoice-like"
    root = tmp_path / "bookvoice"
    shutil.copytree(fixture, root)
    init_git_repo(root)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    cards = parse_bookvoice(root)
    before = tree_hashes(root)

    report = root / "planning/runs/run-1/migration.md"
    report.parent.mkdir(parents=True)
    template = Path(__file__).resolve().parents[1] / (
        "templates/planner-overlay/template/.planner/assets/migration-report.md"
    )
    body = template.read_text(encoding="utf-8")
    body += "\n\n## Fixture inventory\n\n"
    for card in cards:
        body += f"- {card['id']} at {card['path']} (folder {card['folder']})\n"
    body += f"\nExpected unique IDs: {', '.join(manifest['unique_task_ids'])}\n"
    body += "Coverage: 0 unexplained omissions.\n"
    report.write_text(body, encoding="utf-8")

    after = tree_hashes(root)
    added = set(after) - set(before)
    assert added == {"planning/runs/run-1/migration.md"}
    for path, digest in before.items():
        assert after[path] == digest

    # A dirty source tree is reported inline and is not an in-place apply target.
    (root / "docs/ROADMAP.md").write_text("changed\n", encoding="utf-8")
    assert can_apply_in_place(root) is False


def test_adoption_by_reference_retains_ids_edges_and_source_bytes(tmp_path):
    fixture = FIXTURES / "bookvoice-like"
    root = tmp_path / "bookvoice"
    shutil.copytree(fixture, root)
    manifest = json.loads((fixture / "manifest.json").read_text(encoding="utf-8"))
    before = source_hashes(root, manifest)
    init_git_repo(root)
    adopt_by_reference(
        root,
        manifest["unique_task_ids"],
        {"TASK-075": "project/ready/TASK-075.md"},
    )

    report = json.loads(run_checker(root).stdout)
    assert report["result"]["errors"] == 0, report["findings"]
    assert report["coverage"]["adopted_records"] >= 7
    dangling = [f for f in report["findings"] if f["rule"] == "REFERENCE_DANGLING"]
    assert dangling == []
    external = [f for f in report["findings"] if f["rule"] == "EXTERNAL_REFERENCE_UNVERIFIED"]
    assert len(external) == len(manifest["unique_task_ids"])

    after = source_hashes(root, manifest)
    assert after == before

    cards = parse_bookvoice(root)
    blocking, related = bookvoice_edges(cards)
    assert blocking == {tuple(edge) for edge in manifest["blocking_edges"]}
    assert related == {tuple(edge) for edge in manifest["related_edges"]}


def test_repeated_adoption_is_idempotent(tmp_path):
    fixture = FIXTURES / "bookvoice-like"
    root = tmp_path / "bookvoice"
    shutil.copytree(fixture, root)
    manifest = json.loads((fixture / "manifest.json").read_text(encoding="utf-8"))
    adjudicated = {"TASK-075": "project/ready/TASK-075.md"}
    adopt_by_reference(root, manifest["unique_task_ids"], adjudicated)
    first = tree_hashes(root)
    adopt_by_reference(root, manifest["unique_task_ids"], adjudicated)
    assert tree_hashes(root) == first


def test_bookvoice_adoption_refuses_ambiguous_duplicate(tmp_path):
    fixture = FIXTURES / "bookvoice-like"
    manifest = json.loads((fixture / "manifest.json").read_text(encoding="utf-8"))
    root = tmp_path / "bookvoice"
    shutil.copytree(fixture, root)
    with pytest.raises(DuplicateAuthorityError):
        adopt_by_reference(root, manifest["unique_task_ids"])
    assert not (root / "planning/planner.yaml").exists()


def test_partial_adoption_is_reported_not_accepted(tmp_path):
    fixture = FIXTURES / "bookvoice-like"
    manifest = json.loads((fixture / "manifest.json").read_text(encoding="utf-8"))
    result = reconciliation(manifest, manifest["unique_task_ids"][:-1])
    assert result["complete"] is False
    assert result["missing"] == [manifest["unique_task_ids"][-1]]


def test_source_mutation_after_report_is_detected(tmp_path):
    fixture = FIXTURES / "bookvoice-like"
    root = tmp_path / "bookvoice"
    shutil.copytree(fixture, root)
    manifest = json.loads((fixture / "manifest.json").read_text(encoding="utf-8"))
    before = source_hashes(root, manifest)
    (root / "docs/TASK_SEQUENCE.md").write_text("mutated\n", encoding="utf-8")
    after = source_hashes(root, manifest)
    assert any(before[path] != after.get(path) for path in before)


def test_rollback_restores_baseline_without_touching_source(tmp_path):
    fixture = FIXTURES / "bookvoice-like"
    root = tmp_path / "bookvoice"
    shutil.copytree(fixture, root)
    manifest = json.loads((fixture / "manifest.json").read_text(encoding="utf-8"))
    init_git_repo(root)
    baseline = tree_hashes(root)
    adopt_by_reference(
        root,
        manifest["unique_task_ids"],
        {"TASK-075": "project/ready/TASK-075.md"},
    )
    git("add", "-A", cwd=root)
    git("commit", "-q", "-m", "adopt fixture", cwd=root)
    adoption_commit = git("rev-parse", "HEAD", cwd=root).strip()
    git("revert", "--no-edit", adoption_commit, cwd=root)
    assert tree_hashes(root) == baseline


# --------------------------------------------------------------- DeepPlant
def test_deepplant_fixture_preserves_authority_bytes_and_boundaries(tmp_path):
    fixture = FIXTURES / "deepplant-like"
    manifest = json.loads((fixture / "manifest.json").read_text(encoding="utf-8"))
    root = tmp_path / "deepplant"
    shutil.copytree(fixture, root)
    before = source_hashes(root, manifest)
    for path in manifest["must_preserve"]:
        assert (root / path).is_file()
    assert "simulation" in " ".join(manifest["future_directions"]).lower()
    assert manifest["historical_gates"] == ["GATE-2025-01"]
    assert manifest["issue_coverage"]["unavailable"] == ["ISSUE-102"]
    assert source_hashes(root, manifest) == before


def test_future_direction_does_not_authorize_current_work(tmp_path):
    fixture = FIXTURES / "deepplant-like"
    manifest = json.loads((fixture / "manifest.json").read_text(encoding="utf-8"))
    root = tmp_path / "deepplant"
    shutil.copytree(fixture, root)
    before = source_hashes(root, manifest)

    project = make_project(tmp_path / "engineering-project", category="engineering")
    project.scopes["VIS-001"]["purpose"] = (
        "Give engineers a trustworthy model of the current process."
    )
    project.scopes["REQ-001"]["statement"] = (
        "The current workspace must document semantic invariants and units."
    )
    project.scopes["REQ-001"]["classification"] = "quality"
    project.scopes["REQ-001"]["verification"][0]["method"] = (
        "Semantic invariant and dimensional review by a competent engineer."
    )
    project.scopes["MS-001"]["outcome"] = (
        "A reviewed process model for one bounded subsystem."
    )
    project.scopes["MS-001"]["exit_criteria"][0]["statement"] = (
        "Invariants, units and limitations are reviewed and signed."
    )
    project.scopes["TASK-001"]["title"] = "Review the bounded process model"
    project.scopes["TASK-001"]["deliverables"] = [
        {"description": "A reviewed process-model report with invariants and units"}
    ]
    project.scopes["TASK-001"]["verification"][0]["method"] = (
        "Semantic invariant analysis, unit check and a counterexample."
    )
    project.write()
    config = yaml.safe_load(
        (project.root / "planning/planner.yaml").read_text(encoding="utf-8")
    )
    assert config["category"] == "engineering"
    assert config["current_milestone"] == "MS-001"

    # A simulation idea is retained as a captured change, not a ready task.
    from support import write_record

    simulation = {
        "schema_version": 1,
        "kind": "change",
        "id": "CHG-001",
        "owner": "product_owner",
        "scope": {
            "idea": "Add whole-process simulation.",
            "source": "Future direction in docs/dev/planning/roadmap.md",
            "affected": ["MS-001"],
            "impact": "Would expand beyond the current bounded review.",
            "alternatives": ["Keep simulation as directional context"],
            "proposed_delta": "No change; retain as an idea.",
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
    write_record(project.root / "planning/records/CHG-001.md", simulation)
    report = json.loads(run_checker(project.root).stdout)
    assert report["result"]["errors"] == 0
    assert report["coverage"]["ready_tasks"] == ["TASK-001"]
    assert report["coverage"]["records_by_kind"]["task"] == 1
    assert source_hashes(root, manifest) == before


# -------------------------------------------------------------------- PLOS
def test_plos_fixture_preserves_z_n_d_h_and_iteration_boundaries():
    fixture = FIXTURES / "plos-like"
    manifest = json.loads((fixture / "manifest.json").read_text(encoding="utf-8"))
    classification = manifest["classification"]
    assert classification["Z-01"] == "mandated"
    assert classification["N-FR-01"] == "proposed"
    assert classification["N-FR-02"] == "proposed"
    assert classification["D-01"] == "design_decision"
    assert classification["H-01"] == "hypothesis"
    assert classification["CON-01"] == "constraint"
    assert manifest["iterations"] == {"I1": "complete", "I2": "complete", "I3": "proposed"}
    assert manifest["i3_active"] is False
    assert manifest["software_artifacts_required"] is False

    requirements = (fixture / "02-requirements/high-level-requirements.md").read_text(
        encoding="utf-8"
    )
    assert "software, storage" in requirements
    assert "N-FR-01" in requirements and "Proposed" in requirements
    review = (fixture / "07-reviews/semantic-review.md").read_text(encoding="utf-8")
    assert "not proof of user benefit" in review
    assert "No software was used" in review


def test_plos_like_methodology_task_uses_semantic_evidence(tmp_path):
    project = make_project(
        tmp_path / "plos-project",
        category="methodology",
        profiles=["methodology"],
    )
    project.set_state("VIS-001", "approved")
    project.set_state("MS-001", "proposed")
    project.set_state("TASK-001", "draft")
    project.current_milestone = None
    project.change_scope(
        "VIS-001",
        purpose="Help teams reason about complex systems without confusing model and system.",
        beneficiaries=["Engineering teams applying the methodology"],
        problem="Teams confuse a model with the system it describes.",
        choices=["Keep the methodology medium-independent."],
        exclusions=["No mandatory software, storage or task tool."],
        assumptions=["Human reviewers can assess definition consistency."],
    )
    project.change_scope(
        "REQ-001",
        statement="CON-01 - The methodology must remain independent of software and storage.",
        classification="constraint",
        sources=["01-charter/charter.md", "02-requirements/high-level-requirements.md"],
        acceptance=[
            {
                "id": "REQ-001:AC-1",
                "statement": "No software artifact is required to apply the method.",
            }
        ],
        verification=[
            {
                "criteria": ["REQ-001:AC-1"],
                "method": "Scenario walkthrough on paper.",
                "expected_evidence": "A reviewed walkthrough with limitations.",
                "reviewer": "domain_reviewer",
            }
        ],
    )
    project.change_scope(
        "MS-001",
        outcome="A reviewed conceptual model consistency report for one subsystem.",
        exit_criteria=[
            {
                "id": "MS-001:EXIT-1",
                "statement": "Definitions are consistent and two counterexamples assessed.",
            }
        ],
        verification=[
            {
                "criteria": ["MS-001:EXIT-1"],
                "method": "Semantic review and counterexample walkthrough.",
                "expected_evidence": "A reviewed report with a named reviewer.",
                "reviewer": "domain_reviewer",
            }
        ],
    )
    project.approval_overrides["MS-001"] = []
    project.change_scope(
        "TASK-001",
        title="Review conceptual-model definition consistency",
        rationale="I3 must not activate merely because I2 completed.",
        deliverables=[
            {"description": "A reviewed semantic specification and scenario report"}
        ],
        acceptance=[
            {
                "id": "TASK-001:AC-1",
                "statement": "Each contradiction cites both definitions and a counterexample.",
            }
        ],
        verification=[
            {
                "criteria": ["TASK-001:AC-1"],
                "method": "Definition comparison, counterexample and scenario walkthrough.",
                "expected_evidence": "A reviewed report with limitations.",
                "reviewer": "domain_reviewer",
            }
        ],
        approvals=[],
    )
    project.write()
    config = yaml.safe_load(
        (project.root / "planning/planner.yaml").read_text(encoding="utf-8")
    )
    config["current_milestone"] = None
    (project.root / "planning/planner.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
    )
    report = json.loads(run_checker(project.root).stdout)
    assert report["result"]["errors"] == 0, report["findings"]
    assert report["coverage"]["ready_tasks"] == []
    assert report["project"]["category"] == "methodology"
    assert report["coverage"]["records_by_kind"]["task"] == 1

    record = load_frontmatter(project.root / "planning/tasks/TASK-001.md")
    serialized = json.dumps(record["scope"]).lower()
    for forbidden in ("api endpoint", "database", "web app", "mobile app"):
        assert forbidden not in serialized
    assert "semantic" in serialized
    assert "counterexample" in serialized
    assert record["execution"]["state"] == "draft"


def test_plos_adoption_does_not_copy_domain_concepts_or_impose_software(tmp_path):
    fixture = FIXTURES / "plos-like"
    manifest = json.loads((fixture / "manifest.json").read_text(encoding="utf-8"))
    root = tmp_path / "plos"
    shutil.copytree(fixture, root)
    before = source_hashes(root, manifest)
    config = adoption_config([], {})
    config["project_id"] = "plos-fixture"
    config["category"] = "methodology"
    config["verification_profiles"] = ["methodology"]
    config["authorities"] = [
        {
            "kind": "strategy",
            "id": "VIS-001",
            "owner": "product_owner",
            "ref": "01-charter/charter.md",
            "locator": "Purpose and mandated principles",
            "format": "markdown",
        },
        {
            "kind": "requirement",
            "id": "CON-01",
            "owner": "product_owner",
            "ref": "02-requirements/high-level-requirements.md",
            "locator": "Constraints",
            "format": "markdown",
        },
    ]
    (root / "planning").mkdir()
    (root / "planning/planner.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
    )
    from support import write_record

    write_record(
        root / "planning/records/CHG-001.md",
        change_record(["VIS-001", "CON-01"]),
    )
    planner_bytes = (root / "planning/planner.yaml").read_text(encoding="utf-8")
    assert "software, storage" not in planner_bytes
    assert "36 observed domain concepts" not in planner_bytes
    report = json.loads(run_checker(root).stdout)
    assert report["result"]["errors"] == 0
    assert source_hashes(root, manifest) == before
