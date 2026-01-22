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


def pytest_configure(config):
    artifacts_dir = config.getoption("--artifacts-dir")
    if artifacts_dir is None:
        artifacts_dir = config.getini("artifacts_dir")

    config.artifacts_dir = artifacts_dir


@pytest.fixture
def artifacts(request) -> Generator[ArtifactsRepository, None, None]:  # pylint: disable=invalid-name
    """Provide an artifact repository to store and access test artifacts for the
    particular test case.

    Example:
        Write a file to the artifact repository. Will show up in
        `$PWD/.artifacts/mytest/file.txt`:

        >>> def mytest(artifacts):
        ...     with artifacts.open("file.txt", "w") as f:
        ...         f.write("Hello, World!")

    Yields:
        ArtifactsRepository: The artifacts repository for the specific test
        case.
    """
    artifacts_dir_for_test_case = (
        Path(request.config.artifacts_dir).resolve() / request.node.name
    )
    with ArtifactsRepository(artifacts_dir_for_test_case) as repo:
        yield repo


class ArtifactsRepository(AbstractContextManager):
    """Test artifacts repository. Implemented as a directory located in
    ``$PWD/.artifacts/``.
    """

    dir: Path

    def __init__(self, dirpath: Path) -> None:
        self.dir = dirpath
        super().__init__()

    @contextmanager
    def open(self, name: str, mode: str = "r", **kwargs):
        """Open a file in the artifacts repository for this test case.

        Yield:
            file: Opened file object
        """
        fpath = self.dir / name
        with fpath.open(mode, **kwargs) as f:
            yield f

        if fpath.exists():
            log.debug("Added artifact: %s", fpath)

    def __enter__(self):
        if self.dir.exists():
            shutil.rmtree(self.dir)
        self.dir.mkdir(parents=True)

        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        pass
