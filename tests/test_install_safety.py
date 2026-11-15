"""Install/update safety: collision preflight and native Copier behaviour."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from support import REPO_ROOT, tree_hashes
from test_template import ANSWERS, copy_template, make_tagged_template

PREFLIGHT = REPO_ROOT / "scripts" / "preflight_planner_install.py"


def preflight(destination: Path, fmt: str = "json") -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(PREFLIGHT),
            "--destination",
            str(destination),
            "--format",
            fmt,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def report(destination: Path) -> tuple[int, dict]:
    result = preflight(destination)
    return result.returncode, json.loads(result.stdout)


def seed_planner_installation(destination: Path, *, source: str | None = None) -> None:
    answers = destination / ANSWERS
    answers.write_text(
        "# Changes here will be overwritten by Copier; NEVER EDIT MANUALLY.\n"
        f"_src_path: {source or 'gh:Semtexcz/ai-project-planner'}\n"
        "project_name: Existing\n",
        encoding="utf-8",
    )
    for rel in (
        ".planner/README.md",
        ".planner/skills/planner-init/SKILL.md",
        ".planner/schemas/record.schema.json",
        ".planner/scripts/check_planning.py",
    ):
        marker = destination / rel
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("# planner marker\n", encoding="utf-8")


def test_preflight_fresh_destination_is_safe_to_copy(tmp_path):
    code, result = report(tmp_path)
    assert code == 0
    assert result["status"] == "fresh"
    assert result["action"] == "copy"


def test_preflight_unowned_planner_directory_stops(tmp_path):
    (tmp_path / ".planner").mkdir()
    (tmp_path / ".planner/README.md").write_text("another owner\n", encoding="utf-8")
    code, result = report(tmp_path)
    assert code == 2
    assert result["status"] == "collision"
    assert result["action"] == "stop"
    assert "ownership cannot be established" in result["reason"]


def test_preflight_existing_planner_installation_requires_update(tmp_path):
    seed_planner_installation(tmp_path)
    code, result = report(tmp_path)
    assert code == 1
    assert result["status"] == "existing"
    assert result["action"] == "update"


def test_preflight_foreign_overlay_answers_stops(tmp_path):
    (tmp_path / ANSWERS).write_text(
        "_src_path: gh:example/devkit\n", encoding="utf-8"
    )
    (tmp_path / ".planner").mkdir()
    code, result = report(tmp_path)
    assert code == 2
    assert "planner marker files are missing" in result["reason"]


def test_preflight_accepts_local_checkout_source(tmp_path):
    seed_planner_installation(tmp_path, source="../planner-source")
    code, result = report(tmp_path)
    assert code == 1
    assert result["status"] == "existing"
    assert result["source_hint_matches"] is False
    assert "local or alternate checkout" in result["reason"]


def test_preflight_expected_source_mismatch_stops(tmp_path):
    seed_planner_installation(tmp_path, source="../planner-source")
    result = subprocess.run(
        [
            sys.executable,
            str(PREFLIGHT),
            "--destination",
            str(tmp_path),
            "--expected-source",
            "gh:Semtexcz/ai-project-planner",
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert "does not match the expected source" in payload["reason"]


def test_preflight_partial_installation_stops(tmp_path):
    (tmp_path / ANSWERS).write_text(
        "_src_path: gh:Semtexcz/ai-project-planner\n", encoding="utf-8"
    )
    (tmp_path / ".planner").mkdir()
    code, result = report(tmp_path)
    assert code == 2
    assert "planner marker files are missing" in result["reason"]


def test_preflight_unreadable_answers_stops(tmp_path):
    seed_planner_installation(tmp_path)
    (tmp_path / ANSWERS).write_text("project_name: no-source\n", encoding="utf-8")
    code, result = report(tmp_path)
    assert code == 2
    assert "no _src_path" in result["reason"]


def test_preflight_symlinked_planner_path_stops(tmp_path):
    target = tmp_path / "elsewhere"
    target.mkdir()
    (tmp_path / ".planner").symlink_to(target)
    code, result = report(tmp_path)
    assert code == 2
    assert "symlink" in result["reason"]


def test_preflight_is_read_only(tmp_path):
    seed_planner_installation(tmp_path)
    before = tree_hashes(tmp_path)
    code, _ = report(tmp_path)
    assert code == 1
    assert tree_hashes(tmp_path) == before


def test_copier_preserves_colliding_managed_file_without_overwrite(tmp_path):
    template = make_tagged_template(tmp_path)
    destination = tmp_path / "target"
    owned = destination / ".planner/README.md"
    owned.parent.mkdir(parents=True)
    owned.write_text("ANOTHER OWNER CONTENT\n", encoding="utf-8")

    # The documented copy command must not pass --overwrite/--force. Native
    # Copier then refuses the conflict instead of silently replacing the file.
    result = copy_template(template, destination)
    assert result.returncode != 0
    assert owned.read_text(encoding="utf-8") == "ANOTHER OWNER CONTENT\n"
    # A failed copy can still leave partial provenance, which is why the
    # read-only preflight is mandatory before the copy, not after it.
    code, preflight_result = report(destination)
    assert code != 0
    assert preflight_result["action"] == "stop"
