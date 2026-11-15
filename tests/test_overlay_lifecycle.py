"""Independently versioned overlay lifecycle and rollback (I19)."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from support import REPO_ROOT, TEMPLATE_ROOT, git, init_git_repo, tree_hashes
from test_template import ANSWERS, make_tagged_template

SECOND_ANSWERS = ".copier-second-answers.yml"
PLANNER_ANSWERS = ANSWERS


def copier(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "copier", *args],
        capture_output=True,
        text=True,
        cwd=cwd or REPO_ROOT,
        check=False,
    )


def install(
    source: Path,
    destination: Path,
    answers: str,
    ref: str,
    *data: str,
) -> subprocess.CompletedProcess:
    destination.mkdir(parents=True, exist_ok=True)
    return copier(
        "copy",
        "--defaults",
        "--answers-file",
        answers,
        "--vcs-ref",
        ref,
        *data,
        str(source),
        str(destination),
    )


def update(destination: Path, answers: str, ref: str, *extra: str):
    return copier(
        "update",
        "--defaults",
        "--answers-file",
        answers,
        "--vcs-ref",
        ref,
        *extra,
        str(destination),
    )


def make_second_overlay(tmp_path: Path, tag: str = "v1.0.0") -> Path:
    repo = tmp_path / f"second-overlay-{tag}"
    shutil.copytree(
        Path(__file__).resolve().parent / "fixtures/overlays/minimal-overlay", repo
    )
    git("init", "-q", "-b", "main", cwd=repo)
    git("add", "-A", cwd=repo)
    git("commit", "-q", "-m", "second baseline", cwd=repo)
    git("tag", tag, cwd=repo)
    return repo


def bump_second_overlay(repo: Path, tag: str) -> None:
    (repo / "templates/overlay/.second/README.md").write_text(
        f"# Second overlay {tag}\n", encoding="utf-8"
    )
    git("add", "-A", cwd=repo)
    git("commit", "-q", "-m", tag, cwd=repo)
    git("tag", tag, cwd=repo)


def bump_planner(template: Path, tag: str, *, conflict_line: str | None = None) -> None:
    readme = template / "templates/planner-overlay/template/.planner/README.md"
    text = readme.read_text(encoding="utf-8")
    if conflict_line:
        text = text.replace("## Explicit invocation", conflict_line)
    else:
        text += f"\nManaged update {tag}.\n"
    readme.write_text(text, encoding="utf-8")
    git("add", "-A", cwd=template)
    git("commit", "-q", "-m", tag, cwd=template)
    git("tag", tag, cwd=template)


def seed_project(root: Path) -> dict[str, str]:
    root.mkdir(parents=True, exist_ok=True)
    files = {
        "app/main.py": "print('keep')\n",
        "AGENTS.md": "# Existing agent instructions\nKeep these.\n",
        "README.md": "# Existing project readme\n",
        ".copier-answers.yml": "_src_path: gh:example/devkit\n",
        "openspec/config.yaml": "schema: spec-driven\n",
        "planning/strategy.md": "# Project-owned strategy\n",
    }
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return {rel: (root / rel).read_text(encoding="utf-8") for rel in files}


def changed_tracked(root: Path) -> set[str]:
    return set(git("diff", "--name-only", cwd=root).splitlines())


def test_two_overlays_install_in_either_order_without_cross_changes(tmp_path):
    planner = make_tagged_template(tmp_path)
    second = make_second_overlay(tmp_path)
    for order in ("planner-first", "second-first"):
        root = tmp_path / order
        seeded = seed_project(root)
        planner_before = None
        if order == "second-first":
            result = install(second, root, SECOND_ANSWERS, "v1.0.0")
            assert result.returncode == 0, result.stderr
            planner_before = tree_hashes(root)
        result = install(
            planner, root, PLANNER_ANSWERS, "v0.1.0", "-d", "project_name=Order Test"
        )
        assert result.returncode == 0, result.stderr
        if order == "planner-first":
            result = install(second, root, SECOND_ANSWERS, "v1.0.0")
            assert result.returncode == 0, result.stderr
            planner_before = tree_hashes(root)
        assert (root / PLANNER_ANSWERS).is_file()
        assert (root / SECOND_ANSWERS).is_file()
        planner_answers = yaml.safe_load((root / PLANNER_ANSWERS).read_text(encoding="utf-8"))
        second_answers = yaml.safe_load((root / SECOND_ANSWERS).read_text(encoding="utf-8"))
        assert planner_answers["_commit"] == "v0.1.0"
        assert second_answers["_commit"] == "v1.0.0"
        assert planner_answers["_src_path"] != second_answers["_src_path"]
        assert (root / ".planner/README.md").is_file()
        assert (root / ".second/README.md").is_file()
        for rel, text in seeded.items():
            assert (root / rel).read_text(encoding="utf-8") == text, rel
        assert planner_before is not None


def test_planner_update_changes_only_its_managed_diff(tmp_path):
    planner = make_tagged_template(tmp_path)
    second = make_second_overlay(tmp_path)
    bump_planner(planner, "v0.1.1")
    root = tmp_path / "target"
    seed_project(root)
    assert install(planner, root, PLANNER_ANSWERS, "v0.1.0").returncode == 0
    assert install(second, root, SECOND_ANSWERS, "v1.0.0").returncode == 0
    (root / "planning/strategy.md").write_text("# Project strategy edited\n", encoding="utf-8")
    init_git_repo(root)
    before_second = tree_hashes(root / ".second")
    before_planning = (root / "planning/strategy.md").read_text(encoding="utf-8")

    result = update(root, PLANNER_ANSWERS, "v0.1.1")
    assert result.returncode == 0, result.stderr
    changed = changed_tracked(root) | {
        path for path in git("ls-files", "--others", "--exclude-standard", cwd=root).splitlines()
    }
    assert changed == {".planner/README.md", PLANNER_ANSWERS}
    assert "Managed update v0.1.1" in (root / ".planner/README.md").read_text(encoding="utf-8")
    assert (root / "planning/strategy.md").read_text(encoding="utf-8") == before_planning
    assert tree_hashes(root / ".second") == before_second
    answers = yaml.safe_load((root / PLANNER_ANSWERS).read_text(encoding="utf-8"))
    assert answers["_commit"] == "v0.1.1"


def test_second_overlay_update_leaves_planner_bytes_and_provenance(tmp_path):
    planner = make_tagged_template(tmp_path)
    second = make_second_overlay(tmp_path)
    bump_second_overlay(second, "v1.0.1")
    root = tmp_path / "target"
    seed_project(root)
    assert install(planner, root, PLANNER_ANSWERS, "v0.1.0").returncode == 0
    assert install(second, root, SECOND_ANSWERS, "v1.0.0").returncode == 0
    init_git_repo(root)
    before_planner = tree_hashes(root / ".planner")
    before_answers = (root / PLANNER_ANSWERS).read_bytes()

    result = update(root, SECOND_ANSWERS, "v1.0.1")
    assert result.returncode == 0, result.stderr
    assert tree_hashes(root / ".planner") == before_planner
    assert (root / PLANNER_ANSWERS).read_bytes() == before_answers
    assert "Second overlay v1.0.1" in (root / ".second/README.md").read_text(encoding="utf-8")


def test_edited_managed_conflict_exposes_both_sides(tmp_path):
    planner = make_tagged_template(tmp_path)
    bump_planner(planner, "v0.1.1", conflict_line="## Explicit invocation (v0.1.1)")
    root = tmp_path / "target"
    seed_project(root)
    assert install(planner, root, PLANNER_ANSWERS, "v0.1.0").returncode == 0
    readme = root / ".planner/README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8").replace(
            "## Explicit invocation", "## Explicit invocation (local edit)"
        ),
        encoding="utf-8",
    )
    init_git_repo(root)
    result = update(root, PLANNER_ANSWERS, "v0.1.1", "--conflict", "inline")
    assert result.returncode == 0, result.stderr
    text = readme.read_text(encoding="utf-8")
    assert "<<<<<<<" in text and "=======" in text and ">>>>>>>" in text
    assert "local edit" in text
    assert "v0.1.1" in text
    # Copier writes conflict markers into a normal working-tree file; the user
    # must review them. It does not silently pick one side.
    assert len(changed_tracked(root)) >= 1


def test_deleted_project_planning_file_is_not_reseeded(tmp_path):
    planner = make_tagged_template(tmp_path)
    bump_planner(planner, "v0.1.1")
    root = tmp_path / "target"
    seed_project(root)
    assert install(planner, root, PLANNER_ANSWERS, "v0.1.0").returncode == 0
    init_git_repo(root)
    (root / "planning/strategy.md").unlink()
    git("add", "-A", cwd=root)
    git("commit", "-q", "-m", "remove project strategy", cwd=root)
    assert update(root, PLANNER_ANSWERS, "v0.1.1").returncode == 0
    assert not (root / "planning/strategy.md").exists()


def test_revert_of_planner_update_preserves_later_planning_edit(tmp_path):
    planner = make_tagged_template(tmp_path)
    bump_planner(planner, "v0.1.1")
    root = tmp_path / "target"
    seed_project(root)
    assert install(planner, root, PLANNER_ANSWERS, "v0.1.0").returncode == 0
    init_git_repo(root)
    assert update(root, PLANNER_ANSWERS, "v0.1.1").returncode == 0
    git("add", "-A", cwd=root)
    git("commit", "-q", "-m", "planner update", cwd=root)
    update_commit = git("rev-parse", "HEAD", cwd=root).strip()

    (root / "planning/strategy.md").write_text(
        "# Later project-owned strategy edit\n", encoding="utf-8"
    )
    git("add", "-A", cwd=root)
    git("commit", "-q", "-m", "project planning edit", cwd=root)

    git("revert", "--no-edit", update_commit, cwd=root)
    assert "Managed update v0.1.1" not in (root / ".planner/README.md").read_text(
        encoding="utf-8"
    )
    assert "Later project-owned strategy edit" in (
        root / "planning/strategy.md"
    ).read_text(encoding="utf-8")
    answers = yaml.safe_load((root / PLANNER_ANSWERS).read_text(encoding="utf-8"))
    assert answers["_commit"] == "v0.1.0"


DEVKIT_COMMIT = "cc04bcef80b3838cd5956a872717b65949190468"


@pytest.mark.integration
def test_inspected_ai_devkit_overlay_coexists_in_both_orders(tmp_path):
    clone = tmp_path / "ai-devkit"
    result = subprocess.run(
        [
            "git",
            "clone",
            "--quiet",
            "https://github.com/Semtexcz/ai-devkit",
            str(clone),
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
    )
    if result.returncode != 0:
        pytest.skip(f"integration gate: ai-devkit clone unavailable: {result.stderr}")
    try:
        git("checkout", "--quiet", DEVKIT_COMMIT, cwd=clone)
    except AssertionError as exc:
        pytest.skip(f"integration gate: inspected ai-devkit commit unavailable: {exc}")

    planner = make_tagged_template(tmp_path)

    def devkit_copy(destination: Path, *, overwrite: bool = False):
        destination.mkdir(parents=True, exist_ok=True)
        args = [
            sys.executable,
            "-m",
            "copier",
            "copy",
            "--defaults",
        ]
        if overwrite:
            args.append("--overwrite")
        args.extend(
            [
                "--vcs-ref",
                DEVKIT_COMMIT,
                str(clone),
                str(destination),
            ]
        )
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=False,
            timeout=300,
        )

    for order in ("planner-first", "devkit-first"):
        dest = tmp_path / order
        dest.mkdir()
        sentinels = {
            "app/main.py": "print('keep')\n",
            "planning/strategy.md": "# project-owned strategy\n",
            "docs/keep.md": "# existing project knowledge\n",
        }
        for rel, text in sentinels.items():
            path = dest / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

        if order == "devkit-first":
            devkit = devkit_copy(dest)
            assert devkit.returncode == 0, (devkit.stdout, devkit.stderr)
            assert (dest / ".copier-answers.yml").is_file()
            # Devkit owns its generated AGENTS.md. Planner must not touch it.
            agents_hash = tree_hashes(dest).get("AGENTS.md")
            planner_copy = install(
                planner, dest, PLANNER_ANSWERS, "v0.1.0", "-d", "project_name=Coexist"
            )
            assert planner_copy.returncode == 0, planner_copy.stderr
            assert tree_hashes(dest).get("AGENTS.md") == agents_hash
        else:
            planner_copy = install(
                planner, dest, PLANNER_ANSWERS, "v0.1.0", "-d", "project_name=Coexist"
            )
            assert planner_copy.returncode == 0, planner_copy.stderr
            planner_before = tree_hashes(dest / ".planner")
            planner_answers_before = (dest / PLANNER_ANSWERS).read_bytes()
            # Devkit owns AGENTS.md and may ask to overwrite an existing one;
            # --overwrite is acceptable only in this disposable test and only
            # for devkit's own template paths. Planner paths must not change.
            devkit = devkit_copy(dest, overwrite=True)
            assert devkit.returncode == 0, (devkit.stdout, devkit.stderr)
            assert (dest / ".copier-answers.yml").is_file()
            assert tree_hashes(dest / ".planner") == planner_before
            assert (dest / PLANNER_ANSWERS).read_bytes() == planner_answers_before

        assert (dest / ".planner/README.md").is_file()
        assert (dest / PLANNER_ANSWERS).is_file()
        assert (dest / ".copier-answers.yml").is_file()
        planner_answers = yaml.safe_load(
            (dest / PLANNER_ANSWERS).read_text(encoding="utf-8")
        )
        devkit_answers = yaml.safe_load(
            (dest / ".copier-answers.yml").read_text(encoding="utf-8")
        )
        assert planner_answers["_commit"] == "v0.1.0"
        assert planner_answers["_src_path"].endswith("template-repo")
        assert devkit_answers["_src_path"].endswith("ai-devkit")
        for rel, text in sentinels.items():
            assert (dest / rel).read_text(encoding="utf-8") == text, (order, rel)
