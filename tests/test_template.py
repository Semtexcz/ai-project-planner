"""Copier overlay rendering and ownership allowlists (I04)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from support import REPO_ROOT, TEMPLATE_ROOT, tree_hashes

ANSWERS = ".copier-planner-answers.yml"


def make_tagged_template(tmp_path: Path, tag: str = "v0.1.0") -> Path:
    """Create a disposable tagged template repository."""
    from support import git

    repo = tmp_path / "template-repo"
    repo.mkdir()
    shutil.copy2(REPO_ROOT / "copier.yml", repo / "copier.yml")
    shutil.copytree(TEMPLATE_ROOT, repo / "templates/planner-overlay/template")
    git("init", "-q", "-b", "main", cwd=repo)
    git("add", "-A", cwd=repo)
    git("commit", "-q", "-m", "template baseline", cwd=repo)
    git("tag", tag, cwd=repo)
    return repo


def copier(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "copier", *args],
        capture_output=True,
        text=True,
        check=False,
        cwd=cwd or REPO_ROOT,
    )


def copy_template(
    template: Path,
    destination: Path,
    *,
    ref: str = "v0.1.0",
    project_name: str = "Example Project",
    extra: tuple[str, ...] = (),
) -> subprocess.CompletedProcess:
    destination.mkdir(parents=True, exist_ok=True)
    return copier(
        "copy",
        "--defaults",
        "--answers-file",
        ANSWERS,
        "--vcs-ref",
        ref,
        "-d",
        f"project_name={project_name}",
        *extra,
        str(template),
        str(destination),
    )


def assert_only_managed_paths(destination: Path) -> None:
    for path in destination.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(destination).as_posix()
        assert rel == ANSWERS or rel.startswith(".planner/"), rel


def test_copy_emits_only_planner_runtime_and_answers(tmp_path):
    template = make_tagged_template(tmp_path)
    destination = tmp_path / "target project"
    result = copy_template(template, destination, project_name="Účetní projekt")
    assert result.returncode == 0, result.stderr
    assert_only_managed_paths(destination)
    assert (destination / ".planner/schemas/record.schema.json").is_file()
    assert (destination / ".planner/README.md").is_file()
    assert not (destination / "planning").exists()
    assert not (destination / "AGENTS.md").exists()
    assert not (destination / "README.md").exists()
    assert not (destination / "openspec").exists()
    assert not (destination / "_bmad").exists()


def test_answers_own_source_revision_and_display_name(tmp_path):
    template = make_tagged_template(tmp_path)
    destination = tmp_path / "target"
    result = copy_template(template, destination, project_name="Quoted \"name\" – Unicode")
    assert result.returncode == 0, result.stderr
    answers = yaml.safe_load((destination / ANSWERS).read_text(encoding="utf-8"))
    assert answers["_commit"] == "v0.1.0"
    assert answers["_src_path"].endswith("template-repo")
    assert answers["project_name"] == "Quoted \"name\" – Unicode"
    text = (destination / ANSWERS).read_text(encoding="utf-8")
    assert "NEVER EDIT MANUALLY" in text


def test_runtime_files_are_copied_byte_identical(tmp_path):
    template = make_tagged_template(tmp_path)
    destination = tmp_path / "target"
    result = copy_template(template, destination)
    assert result.returncode == 0, result.stderr
    expected = tree_hashes(TEMPLATE_ROOT / ".planner")
    actual = tree_hashes(destination / ".planner")
    assert actual == expected


def test_template_has_no_executable_tasks_or_migrations():
    config = yaml.safe_load((REPO_ROOT / "copier.yml").read_text(encoding="utf-8"))
    for forbidden in ("_tasks", "_migrations", "_jinja_extensions"):
        assert forbidden not in config
    assert config["_subdirectory"] == "templates/planner-overlay/template"
    assert config["_answers_file"] == ANSWERS
    # Only the answers file uses the Jinja suffix.
    jinja_files = [
        p.relative_to(TEMPLATE_ROOT).as_posix()
        for p in TEMPLATE_ROOT.rglob("*.jinja")
    ]
    assert jinja_files == ["{{ _copier_conf.answers_file }}.jinja"]


def test_unknown_planner_files_survive_so_documented_preflight_is_required(tmp_path):
    template = make_tagged_template(tmp_path)
    destination = tmp_path / "target"
    owned = destination / ".planner/owner.txt"
    owned.parent.mkdir(parents=True)
    owned.write_text("another owner\n", encoding="utf-8")
    result = copy_template(template, destination)
    # Copier does not infer ownership. It leaves a non-overlapping unknown file
    # alone, but a matching managed path would be rendered over it. The
    # documented preflight below is therefore mandatory, not advisory.
    assert result.returncode == 0, result.stderr
    assert owned.read_text(encoding="utf-8") == "another owner\n"


def test_documented_preflight_detects_planner_collision(tmp_path):
    (tmp_path / ".planner").mkdir()
    proc = subprocess.run(
        [
            "bash",
            "-c",
            'test ! -e "$1/.planner" && test ! -e "$1/.copier-planner-answers.yml"',
            "preflight",
            str(tmp_path),
        ],
        check=False,
    )
    assert proc.returncode != 0
    fresh = tmp_path / "fresh"
    fresh.mkdir()
    ok = subprocess.run(
        [
            "bash",
            "-c",
            'test ! -e "$1/.planner" && test ! -e "$1/.copier-planner-answers.yml"',
            "preflight",
            str(fresh),
        ],
        check=False,
    )
    assert ok.returncode == 0


def test_pretend_makes_no_changes(tmp_path):
    template = make_tagged_template(tmp_path)
    destination = tmp_path / "target"
    destination.mkdir()
    before = tree_hashes(destination)
    result = copier(
        "copy",
        "--pretend",
        "--defaults",
        "--answers-file",
        ANSWERS,
        "--vcs-ref",
        "v0.1.0",
        "-d",
        "project_name=Preview",
        str(template),
        str(destination),
    )
    assert result.returncode == 0, result.stderr
    assert tree_hashes(destination) == before


def test_no_other_overlay_or_application_path_is_rendered(tmp_path):
    template = make_tagged_template(tmp_path)
    destination = tmp_path / "target"
    (destination / "app").mkdir(parents=True)
    (destination / "app/main.py").write_text("print('keep')\n", encoding="utf-8")
    (destination / "AGENTS.md").write_text("keep me\n", encoding="utf-8")
    (destination / ".copier-answers.yml").write_text(
        "_src_path: gh:example/devkit\n", encoding="utf-8"
    )
    before = tree_hashes(destination)
    result = copy_template(template, destination)
    assert result.returncode == 0, result.stderr
    after = tree_hashes(destination)
    for rel, digest in before.items():
        assert after[rel] == digest, rel
    new_files = set(after) - set(before)
    assert new_files
    assert all(rel == ANSWERS or rel.startswith(".planner/") for rel in new_files)
