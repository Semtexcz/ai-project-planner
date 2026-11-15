"""Shared test helpers.

The helpers build small synthetic projects in temporary directories. They never
read or write the real DeepPlant, Bookvoice or PLOS repositories.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = REPO_ROOT / "templates" / "planner-overlay" / "template"
PLANNER_ROOT = TEMPLATE_ROOT / ".planner"
CHECKER = PLANNER_ROOT / "scripts" / "check_planning.py"
SCHEMA_DIR = PLANNER_ROOT / "schemas"
ASSET_DIR = PLANNER_ROOT / "assets"


def load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def scope_digest(scope: dict) -> str:
    """Canonical content identity for a native record's scope."""
    payload = json.dumps(scope, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def record_text(frontmatter: dict, body: str = "") -> str:
    header = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True)
    return f"---\n{header}---\n\n{body.strip()}\n"


def write_record(path: Path, frontmatter: dict, body: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(record_text(frontmatter, body), encoding="utf-8")


def load_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"{path} has no frontmatter")
    _, raw, _ = text.split("---\n", 2)
    return yaml.safe_load(raw)


def run_checker(project: Path, fmt: str = "json", *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--project", str(project), "--format", fmt, *extra],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )


def checker_report(project: Path) -> dict:
    proc = run_checker(project)
    if not proc.stdout.strip():
        raise AssertionError(f"checker produced no JSON: {proc.stderr}")
    return json.loads(proc.stdout)


def tree_hashes(root: Path, *, include_git: bool = False) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if not include_git and (rel == ".git" or rel.startswith(".git/")):
            continue
        hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def git(*args: str, cwd: Path) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        env={
            "PATH": "/usr/bin:/bin:/usr/local/bin",
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        },
    )
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {proc.stderr}")
    return proc.stdout


def init_git_repo(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    git("init", "-q", "-b", "main", cwd=root)
    git("add", "-A", cwd=root)
    git("commit", "-q", "-m", "baseline", cwd=root)


DEFAULT_STRATEGY_SCOPE = {
    "purpose": "Turn an approved intention into verifiable planning work.",
    "beneficiaries": ["Project maintainers", "Product Owner"],
    "problem": "Planning evidence and approvals are scattered across tools.",
    "choices": ["Use one native record model with explicit authority bindings."],
    "exclusions": ["No autonomous execution or scheduler."],
    "assumptions": ["Git remains the review and history mechanism."],
    "objectives": [
        {
            "id": "OBJ-001",
            "statement": "Make the planning chain reviewable end to end.",
            "outcomes": [
                {
                    "id": "OUT-001",
                    "description": "A reviewer can trace an approved task to a strategic outcome.",
                    "baseline": "unknown - no baseline was measured before v0.1",
                    "target_or_rubric": "Every ready task cites an approved requirement and objective.",
                    "verification": "Review a sample of tasks and their approval records.",
                    "review_horizon": "At the first milestone review.",
                }
            ],
        }
    ],
}

DEFAULT_REQUIREMENT_SCOPE = {
    "statement": "The overlay must expose six bounded planning operations.",
    "classification": "functional",
    "objectives": ["OBJ-001"],
    "sources": ["Approved v0.1 implementation plan"],
    "acceptance": [
        {
            "id": "REQ-001:AC-1",
            "statement": "Each operation has one explicit skill entry point and no execution launcher.",
        }
    ],
    "verification": [
        {
            "criteria": ["REQ-001:AC-1"],
            "method": "Inspect the rendered skill inventory and invoke one operation explicitly.",
            "expected_evidence": "A recorded invocation and a skill inventory listing six operations.",
            "reviewer": "domain_reviewer",
        }
    ],
    "supersedes": [],
}

DEFAULT_MILESTONE_SCOPE = {
    "outcome": "A maintainer completes one planning loop on a disposable project.",
    "objectives": ["OBJ-001"],
    "outcomes": ["OUT-001"],
    "requirements": ["REQ-001"],
    "depends_on": [],
    "exit_criteria": [
        {
            "id": "MS-001:EXIT-1",
            "statement": "The ready task and its derived prompt cite the approved chain.",
        }
    ],
    "verification": [
        {
            "criteria": ["MS-001:EXIT-1"],
            "method": "Review the task record and regenerated prompt against the strategy.",
            "expected_evidence": "A reviewed demonstration report with source revisions.",
            "reviewer": "product_owner",
        }
    ],
    "packages": [
        {
            "id": "WP-001",
            "outcome": "A complete planning record set for one small deliverable.",
            "include": ["Strategy, requirement, milestone and task records"],
            "exclude": ["Implementation work"],
        }
    ],
}

DEFAULT_TASK_SCOPE = {
    "title": "Write the demonstration evidence report",
    "objective": "OBJ-001",
    "rationale": "The report demonstrates that the approved chain is traceable.",
    "milestone": "MS-001",
    "package": "WP-001",
    "requirements": ["REQ-001"],
    "include": ["Write planning/evidence/demo.md with cited sources"],
    "exclude": ["none - no implementation is in scope"],
    "depends_on": [],
    "context": [
        {
            "ref": "planning/strategy.md",
            "authority": "strategy",
            "revision": "working-tree",
            "purpose": "The objective and outcome this work serves.",
            "normative": True,
        }
    ],
    "deliverables": [
        {"description": "A reviewable demonstration report", "path": "planning/evidence/demo.md"}
    ],
    "acceptance": [
        {"id": "TASK-001:AC-1", "statement": "The report cites VIS-001, OBJ-001 and REQ-001."}
    ],
    "verification": [
        {
            "criteria": ["TASK-001:AC-1"],
            "method": "Read the report and compare each citation with the authoritative record.",
            "expected_evidence": "The report file at a stated revision.",
            "reviewer": "domain_reviewer",
        }
    ],
    "approvals": [
        {
            "decision": "DEC-001",
            "required_by": "product_owner",
            "consequence": "Normative task scope",
            "stop_point": "Before adding requirements or changing the milestone outcome",
        }
    ],
    "priority": "P1",
    "size": "M",
}


class Project:
    """A mutable synthetic native planning project."""

    def __init__(self, root: Path):
        self.root = root
        self.scopes: dict[str, dict] = {
            "VIS-001": deepcopy(DEFAULT_STRATEGY_SCOPE),
            "REQ-001": deepcopy(DEFAULT_REQUIREMENT_SCOPE),
            "MS-001": deepcopy(DEFAULT_MILESTONE_SCOPE),
            "TASK-001": deepcopy(DEFAULT_TASK_SCOPE),
        }
        self.states = {
            "VIS-001": "approved",
            "REQ-001": "approved",
            "MS-001": "active",
            "TASK-001": "ready",
            "DEC-001": "accepted",
        }
        self.items = {"OBJ-001": "active", "OUT-001": "active"}
        self.decision_state = "accepted"
        self.decision_targets: list[dict] = []
        self.category = "software"
        self.profiles = [self.category]
        self.config: dict = {}
        self.extra_records: dict[str, dict] = {}
        self.extra_files: dict[str, str] = {}
        self.current_milestone: str | None = "MS-001"
        self.approval_refs = ["DEC-001"]
        self.approval_overrides: dict[str, list[str]] = {}

    def change_scope(self, record_id: str, **updates) -> dict:
        scope = self.scopes[record_id]
        for key, value in updates.items():
            if isinstance(value, list) and isinstance(scope.get(key), list):
                scope[key] = value
            elif isinstance(value, dict) and isinstance(scope.get(key), dict):
                scope[key].update(value)
            else:
                scope[key] = value
        return scope

    def set_state(self, record_id: str, state: str) -> None:
        self.states[record_id] = state

    def build_config(self) -> dict:
        return {
            "schema_version": 1,
            "project_id": "fixture-project",
            "name": "Fixture Project",
            "category": self.category,
            "content_root": "planning",
            "roles": {
                "product_owner": "Product Owner",
                "task_owner": "Task Owner",
                "domain_reviewer": "Domain Reviewer",
            },
            "authorities": [
                {"kind": "strategy", "owner": "product_owner", "root": "planning/strategy.md"},
                {
                    "kind": "requirement",
                    "owner": "product_owner",
                    "root": "planning/requirements",
                },
                {"kind": "milestone", "owner": "product_owner", "root": "planning/milestones"},
                {"kind": "task", "owner": "task_owner", "root": "planning/tasks"},
                {"kind": "decision", "owner": "product_owner", "root": "planning/records"},
                {"kind": "change", "owner": "product_owner", "root": "planning/records"},
                {"kind": "roadmap", "owner": "product_owner", "root": "planning/roadmap.md"},
            ],
            "aliases": [],
            "current_milestone": self.current_milestone,
            "task_order": ["TASK-001"],
            "ordering_policy": "priority,roadmap,id",
            "verification_profiles": self.profiles,
            "review_policy": {
                "periodic_review": "weekly",
                "milestone_activation_requires_product_owner": True,
            },
        }

    def record_paths(self) -> dict[str, Path]:
        return {
            "VIS-001": self.root / "planning/strategy.md",
            "REQ-001": self.root / "planning/requirements/REQ-001.md",
            "MS-001": self.root / "planning/milestones/MS-001.md",
            "TASK-001": self.root / "planning/tasks/TASK-001.md",
            "DEC-001": self.root / "planning/records/DEC-001.md",
        }

    def record(self, record_id: str) -> dict:
        kind = {
            "VIS": "strategy",
            "REQ": "requirement",
            "MS": "milestone",
            "TASK": "task",
            "DEC": "decision",
            "CHG": "change",
        }[record_id.split("-")[0]]
        owner = "product_owner" if kind != "task" else "task_owner"
        return {
            "schema_version": 1,
            "kind": kind,
            "id": record_id,
            "owner": owner,
            "scope": self.scopes[record_id],
            "execution": self.execution(record_id),
        }

    def execution(self, record_id: str) -> dict:
        kind = record_id.split("-")[0]
        state = self.states[record_id]
        if kind == "VIS":
            return {
                "state": state,
                "items": {
                    key: {"state": value, "evidence": []} for key, value in self.items.items()
                },
                "approvals": [
                    {"decision": d}
                    for d in self.approval_overrides.get(record_id, self.approval_refs)
                ],
                "progress_notes": [],
            }
        if kind == "TASK":
            return {
                "state": state,
                "authorization": [d for d in self.approval_refs if d.startswith("DEC")],
                "evidence": [],
                "blockers": [],
                "progress_notes": [],
            }
        if kind == "DEC":
            accepted = state == "accepted"
            return {
                "state": state,
                "actor": "Daniel Kopecký" if accepted else "",
                "decided_at": "2026-11-15" if accepted else "",
                "approval_source": "Explicit approval recorded in a reviewed session"
                if accepted
                else "",
                "applied_revision": None,
            }
        return {
            "state": state,
            "approvals": [
                {"decision": d}
                for d in self.approval_overrides.get(record_id, self.approval_refs)
            ],
            "evidence": [],
            "blockers": [],
            "progress_notes": [],
        }

    def decision_record(self, *, recompute: bool = True) -> dict:
        if recompute:
            self.decision_targets = [
                {"record": rid, "scope_sha256": scope_digest(scope)}
                for rid, scope in self.scopes.items()
            ]
        return {
            "schema_version": 1,
            "kind": "decision",
            "id": "DEC-001",
            "owner": "product_owner",
            "scope": {
                "topic": "Approve the initial planning baseline and ready task scope",
                "rationale": "The baseline is internally traceable and the task is bounded.",
                "options": ["Approve the exact proposed scopes", "Request changes"],
                "choice": "Approve the exact proposed scopes",
                "targets": deepcopy(self.decision_targets),
                "authority": "Product Owner",
                "supersedes": [],
            },
            "execution": self.execution("DEC-001"),
        }

    def write(self, *, recompute_digests: bool = True) -> "Project":
        self.root.mkdir(parents=True, exist_ok=True)
        self.config = self.build_config()
        (self.root / "planning").mkdir(parents=True, exist_ok=True)
        (self.root / "planning/planner.yaml").write_text(
            yaml.safe_dump(self.config, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )
        paths = self.record_paths()
        for record_id in ["VIS-001", "REQ-001", "MS-001", "TASK-001"]:
            write_record(paths[record_id], self.record(record_id), f"# {record_id}\n")
        write_record(
            paths["DEC-001"],
            self.decision_record(recompute=recompute_digests),
            "# DEC-001\n",
        )
        (self.root / "planning/roadmap.md").write_text(
            "# Roadmap view\n\n1. MS-001 - the current milestone.\n", encoding="utf-8"
        )
        (self.root / "planning/evidence").mkdir(exist_ok=True)
        for rel, text in self.extra_files.items():
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        for rel, frontmatter in self.extra_records.items():
            write_record(self.root / rel, frontmatter, f"# {frontmatter.get('id', rel)}\n")
        return self


def make_project(root: Path, **kwargs) -> Project:
    project = Project(root)
    for key, value in kwargs.items():
        setattr(project, key, value)
    return project
