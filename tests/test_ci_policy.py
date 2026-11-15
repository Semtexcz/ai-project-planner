"""CI policy and documentation link checks (I20)."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from support import REPO_ROOT, TEMPLATE_ROOT

DOCS = [REPO_ROOT / "README.md", *sorted((REPO_ROOT / "docs").glob("*.md"))]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def test_ci_is_read_only_and_never_runs_paid_inference():
    path = REPO_ROOT / ".github/workflows/verify.yml"
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    assert data["permissions"] == {"contents": "read"}
    assert "pull_request_target" not in text
    assert "secrets." not in text
    assert "git push" not in text
    assert "git tag" not in text
    assert "gh release" not in text
    assert "pytest -m \"not integration\"" in text
    assert "pytest -m integration" in text
    assert "uv sync --locked" in text
    assert "uv lock --check" in text
    jobs = data["jobs"]
    assert set(jobs) == {"offline", "integration"}
    assert jobs["integration"]["if"] == "github.event_name == 'workflow_dispatch'"


def test_documentation_relative_links_resolve():
    failures = []
    for document in DOCS:
        text = document.read_text(encoding="utf-8")
        for target in LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target_path = target.split("#", 1)[0]
            if not target_path:
                continue
            resolved = (document.parent / target_path).resolve()
            if not resolved.exists():
                failures.append((document.relative_to(REPO_ROOT).as_posix(), target))
    assert failures == []


def test_runtime_reference_links_resolve_within_the_planner_tree():
    failures = []
    link_re = re.compile(r"`([^`\n]+\.(?:md|json|py))`")
    for document in list((TEMPLATE_ROOT / ".planner").rglob("*.md")):
        if document.parent == TEMPLATE_ROOT / ".planner":
            # The root README documents installed project-relative paths.
            continue
        text = document.read_text(encoding="utf-8")
        for target in link_re.findall(text):
            if target.startswith(("/", "http://", "https://", "{")):
                continue
            if "/" not in target:
                # Prose also names generic sibling filenames such as SKILL.md.
                continue
            candidate = (document.parent / target).resolve()
            planner_relative = (TEMPLATE_ROOT / ".planner" / target).resolve()
            if candidate.exists() or planner_relative.exists():
                continue
            if document.parent.name == "references" and target.startswith("../../"):
                # Illustrates the path a skill uses, not a link from this file.
                continue
            # Runtime prose also names project paths and BMAD paths.
            if target.startswith(
                (
                    "planning/",
                    "_bmad/",
                    ".agents/",
                    ".opencode/",
                    ".planner/",
                    "openspec/",
                    "docs/",
                )
            ):
                continue
            failures.append((document.name, target))
    assert failures == []


def test_readme_covers_install_activate_update_and_all_operations():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    for phrase in (
        "uvx copier==9.19.1 copy",
        "uvx copier==9.19.1 update",
        "planner-init",
        "planner-status",
        "planner-plan",
        "planner-next",
        "planner-change",
        "planner-audit",
        "uv run --script .planner/scripts/check_planning.py",
        "npx --yes bmad-method@6.12.4",
        "Linux x86-64",
    ):
        assert phrase in text, phrase


def test_no_release_or_push_automation_exists():
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or ".venv" in path.parts:
            continue
        if path.name == "test_ci_policy.py":
            continue
        if path.suffix not in {".yml", ".yaml", ".sh", ".py", ".toml"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        assert "git push" not in text, path
        assert "gh release create" not in text, path
