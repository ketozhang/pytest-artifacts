from __future__ import annotations

import logging
import shutil
from contextlib import AbstractContextManager, contextmanager
from pathlib import Path
from typing import Generator

import pytest

log = logging.getLogger(__name__)


def pytest_addoption(parser):
    group = parser.getgroup("artifacts")
    group.addoption(
        "--artifacts-dir",
        action="store",
        type=str,
        help="Directory to store test artifacts. Overrides ini setting.",
    )

    parser.addini(
        "artifacts_dir", "Directory to store test artifacts.", default=".artifacts/"
    )


@pytest.fixture
def _artifacts_dir(request):
    if request.config.option.artifacts_dir is not None:
        return request.config.option.artifacts_dir
    return request.config.getini("artifacts_dir")


@pytest.fixture
def bar(request):
    return request.config.option.dest_foo
