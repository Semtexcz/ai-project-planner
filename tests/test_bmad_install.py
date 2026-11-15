"""Native BMAD installer/resolver integration (I01/I07).

These tests need npm registry access and are excluded from the offline suite.
They only use disposable directories and never touch a real project.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

BMAD_VERSION = "6.12.4"


def require_npx() -> str:
    npx = shutil.which("npx")
    if npx is None:
        pytest.skip("npx is not available")
    return npx


def run(cmd: list[str], cwd: Path, env: dict[str, str], timeout: int = 900):
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"command failed ({result.returncode}): {' '.join(cmd)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def sandbox_env(home: Path) -> dict[str, str]:
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["npm_config_cache"] = str(home / ".npm")
    env["npm_config_update_notifier"] = "false"
    return env


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(project: Path, env: dict[str, str], *args: str) -> dict:
    result = run(
        ["uv", "run", "_bmad/scripts/resolve_config.py", "--project-root", ".", *args],
        cwd=project,
        env=env,
    )
    return json.loads(result.stdout)


def resolve_customization(
    project: Path, env: dict[str, str], skill: str, *keys: str
) -> dict:
    args = [
        "uv",
        "run",
        "_bmad/scripts/resolve_customization.py",
        "--skill",
        str(project / ".agents/skills" / skill),
        "--project-root",
        ".",
    ]
    for key in keys:
        args.extend(["--key", key])
    result = run(args, cwd=project, env=env)
    return json.loads(result.stdout)


def test_pinned_install_resolvers_and_reinstall_preserve_project_files(tmp_path):
    npx = require_npx()
    project = tmp_path / "bmad-project"
    project.mkdir()
    home = tmp_path / "home"
    home.mkdir()
    env = sandbox_env(home)

    install = [
        npx,
        "--yes",
        f"bmad-method@{BMAD_VERSION}",
        "install",
        "--yes",
        "--directory",
        str(project),
        "--modules",
        "bmm",
        "--tools",
        "opencode",
        "--set",
        "core.output_folder=planning/runs/bmad",
        "--set",
        "bmm.planning_artifacts=planning/runs/bmad/planning-artifacts",
        "--set",
        "bmm.implementation_artifacts=planning/runs/bmad/implementation-artifacts",
        "--set",
        "bmm.project_knowledge=planning/runs/bmad/project-knowledge",
    ]
    run(install, cwd=project, env=env)

    assert (project / "_bmad/config.toml").is_file()
    assert (project / "_bmad/scripts/resolve_config.py").is_file()
    assert (project / ".agents/skills/bmad-prd/SKILL.md").is_file()
    assert (project / ".agents/skills/bmad-product-brief/SKILL.md").is_file()
    config = resolve(
        project,
        env,
        "--key",
        "modules.bmm.planning_artifacts",
        "--key",
        "modules.bmm.project_knowledge",
        "--key",
        "core.output_folder",
    )
    assert "planning/runs/bmad" in config["core.output_folder"]
    assert "planning/runs/bmad/planning-artifacts" in config[
        "modules.bmm.planning_artifacts"
    ]
    assert "planning/runs/bmad/project-knowledge" in config[
        "modules.bmm.project_knowledge"
    ]

    custom = project / "_bmad/custom/bmad-prd.toml"
    custom.parent.mkdir(parents=True, exist_ok=True)
    custom.write_text(
        "[workflow]\n"
        'persistent_facts = ["PLANNER-PROBE: one agent only"]\n'
        'doc_standards = ["PLANNER-PROBE: appended standard"]\n',
        encoding="utf-8",
    )
    sentinel = project / "_bmad/custom/sentinel.txt"
    sentinel.write_text("keep\n", encoding="utf-8")
    agents = project / "AGENTS.md"
    agents.write_text("# Existing project instructions\nKeep me.\n", encoding="utf-8")
    app = project / "app.txt"
    app.write_text("existing application content\n", encoding="utf-8")
    planning = project / "planning/strategy.md"
    planning.parent.mkdir(parents=True, exist_ok=True)
    planning.write_text("# Project-owned strategy\n", encoding="utf-8")
    before = {path: sha(path) for path in (sentinel, agents, app, planning)}
    custom_bytes = custom.read_bytes()

    merged = resolve_customization(
        project, env, "bmad-prd", "workflow.persistent_facts", "workflow.doc_standards"
    )
    assert merged["workflow.persistent_facts"] == ["PLANNER-PROBE: one agent only"]
    standards = merged["workflow.doc_standards"]
    assert "PLANNER-PROBE: appended standard" in standards
    assert "skill:bmad-review lenses=structure,prose" in standards

    update = [
        npx,
        "--yes",
        f"bmad-method@{BMAD_VERSION}",
        "install",
        "--yes",
        "--action",
        "update",
        "--directory",
        str(project),
        "--modules",
        "bmm",
        "--tools",
        "opencode",
        "--set",
        "core.output_folder=planning/runs/bmad",
        "--set",
        "bmm.planning_artifacts=planning/runs/bmad/planning-artifacts",
        "--set",
        "bmm.implementation_artifacts=planning/runs/bmad/implementation-artifacts",
        "--set",
        "bmm.project_knowledge=planning/runs/bmad/project-knowledge",
    ]
    run(update, cwd=project, env=env)

    assert custom.read_bytes() == custom_bytes
    for path, digest in before.items():
        assert sha(path) == digest, f"{path} changed during BMAD reinstall"
    merged = resolve_customization(
        project, env, "bmad-prd", "workflow.persistent_facts", "workflow.doc_standards"
    )
    assert merged["workflow.persistent_facts"] == ["PLANNER-PROBE: one agent only"]
    assert "PLANNER-PROBE: appended standard" in merged["workflow.doc_standards"]
