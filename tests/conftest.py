"""Pytest configuration for the planner repository."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))


@pytest.fixture()
def project(tmp_path):
    from support import make_project

    return make_project(tmp_path).write()


@pytest.fixture()
def empty_project(tmp_path):
    root = tmp_path
    root.mkdir(parents=True, exist_ok=True)
    return root
