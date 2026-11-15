#!/usr/bin/env python3
"""Read-only install/update preflight for the planner overlay.

This program does not install, update or modify anything. It inspects a
destination directory and reports whether a native Copier `copy` is safe.

The planner overlay is a Copier template whose managed paths are `.planner/**`
and `.copier-planner-answers.yml`. Copier 9.19.1 refuses to overwrite an
existing conflicting file unless `--overwrite` (or `--force`) is passed, but a
failed copy can still leave a partial destination. This preflight exists so the
operator stops before that partial state, and so an existing `.planner/` of
unknown or foreign ownership is never treated as a fresh target.

Ownership detection is a heuristic, not authentication. It requires the planner
marker files, which makes local checkouts with arbitrary directory names work;
`--expected-source` adds an exact source check when the operator knows it.

Exit codes:
  0  fresh destination: no planner-managed path exists
  1  existing planner installation: use the native `copier update` path
  2  collision: unowned, foreign, partial or unreadable path; stop
  3  invalid invocation or destination
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ANSWERS = ".copier-planner-answers.yml"
MANAGED = ".planner"
MARKERS = (
    Path(".planner/README.md"),
    Path(".planner/skills/planner-init/SKILL.md"),
    Path(".planner/schemas/record.schema.json"),
    Path(".planner/scripts/check_planning.py"),
)
PLANNER_SOURCE_HINTS = ("ai-project-planner", "planner-overlay")


def read_answers_source(path: Path) -> tuple[str | None, str | None]:
    """Return (_src_path, error) without a YAML dependency.

    The answers file is written by Copier and contains a single top-level
    `_src_path:` scalar. We deliberately parse only that line instead of
    treating the file as trusted configuration.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"cannot read {path.name}: {exc}"
    source: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("_src_path:"):
            value = stripped.split(":", 1)[1].strip()
            if value[:1] in {'"', "'"} and value[-1:] == value[:1] and len(value) >= 2:
                value = value[1:-1]
            source = value
            break
    if source is None:
        return None, f"{path.name} has no _src_path entry"
    return source, None


def normalize_source(source: str) -> str:
    return source.rstrip("/").lower()


def source_matches(source: str, expected: str) -> bool:
    left = normalize_source(source)
    right = normalize_source(expected)
    return left == right


def source_has_planner_hint(source: str) -> bool:
    normalized = normalize_source(source)
    return any(hint in normalized for hint in PLANNER_SOURCE_HINTS)


def inspect(destination: Path, expected_source: str | None = None) -> dict:
    planner = destination / MANAGED
    answers = destination / ANSWERS
    result = {
        "destination": str(destination),
        "planner_exists": planner.exists() or planner.is_symlink(),
        "answers_exists": answers.exists() or answers.is_symlink(),
        "status": "fresh",
        "action": "copy",
        "reason": "no planner-managed path exists",
        "source": None,
        "source_hint_matches": None,
    }

    if not result["planner_exists"] and not result["answers_exists"]:
        return result

    if planner.is_symlink():
        result.update(
            status="collision",
            action="stop",
            reason=f"{MANAGED} is a symlink; planner managed paths must be real directories",
        )
        return result
    if answers.is_symlink():
        result.update(
            status="collision",
            action="stop",
            reason=f"{ANSWERS} is a symlink; planner provenance must be a real file",
        )
        return result

    if not result["answers_exists"]:
        result.update(
            status="collision",
            action="stop",
            reason=(
                f"{MANAGED} exists without {ANSWERS}; ownership cannot be established. "
                "Do not copy over it. Inspect it with the project owner first."
            ),
        )
        return result

    source, error = read_answers_source(answers)
    result["source"] = source
    if error:
        result.update(status="collision", action="stop", reason=error)
        return result

    missing = [marker.as_posix() for marker in MARKERS if not (destination / marker).is_file()]
    if missing:
        result.update(
            status="collision",
            action="stop",
            reason=(
                "the answers file is planner-named but planner marker files are missing "
                f"({', '.join(missing)}); treat this as a partial, edited or foreign "
                "installation and inspect it first"
            ),
        )
        return result

    result["source_hint_matches"] = source_has_planner_hint(source or "")
    if expected_source and not source_matches(source or "", expected_source):
        result.update(
            status="collision",
            action="stop",
            reason=(
                f"{ANSWERS} names source {source!r}, which does not match the expected "
                f"source {expected_source!r}"
            ),
        )
        return result

    reason = (
        "a planner installation is present; use `copier update` with this answers "
        "file. Do not run `copier copy` over it."
    )
    if not result["source_hint_matches"]:
        reason += (
            " The source path is a local or alternate checkout; planner markers establish "
            "ownership, not the path name."
        )
    result.update(status="existing", action="update", reason=reason)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only preflight before installing or updating the planner overlay."
    )
    parser.add_argument("--destination", required=True, help="Target project directory")
    parser.add_argument(
        "--expected-source",
        default=None,
        help="Optional exact source path or URL expected in the planner answers file",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Report format (default: text)",
    )
    args = parser.parse_args(argv)

    destination = Path(args.destination).expanduser()
    if not destination.is_dir():
        message = f"destination is not a directory: {destination}"
        if args.format == "json":
            sys.stdout.write(
                json.dumps(
                    {"status": "invalid", "action": "stop", "reason": message},
                    indent=2,
                )
                + "\n"
            )
        else:
            sys.stderr.write(f"error: {message}\n")
        return 3

    result = inspect(destination.resolve(), args.expected_source)
    if args.format == "json":
        sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    else:
        sys.stdout.write(
            f"Planner install preflight\n"
            f"Destination: {result['destination']}\n"
            f"Status: {result['status']}\n"
            f"Action: {result['action']}\n"
            f"Reason: {result['reason']}\n"
        )
    if result["status"] == "fresh":
        return 0
    if result["status"] == "existing":
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
