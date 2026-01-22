import pytest


@pytest.mark.parametrize(
    "addopts,ini,expected",
    [
        pytest.param([], "", ".artifacts/", id="default"),
        pytest.param(
            [],
            """
            [pytest]
            artifacts_dir = .ini_artifacts/
        """,
            ".ini_artifacts/",
            id="ini-only",
        ),
        pytest.param(
            ["--artifacts-dir=.cmdline_artifacts/"],
            "",
            ".cmdline_artifacts/",
            id="cmdline-only",
        ),
        pytest.param(
            ["--artifacts-dir=.cmdline_artifacts/"],
            """
            [pytest]
            artifacts_dir = .ini_artifacts/
        """,
            ".cmdline_artifacts/",
            id="cmdline-overrides-ini",
        ),
    ],
)
def test_fixture_artifacts_dir(pytester, addopts, ini, expected):
    """Test that the artifacts_dir fixture returns the default value."""
    pytester.makeini(ini)

    # create a temporary pytest test module
    pytester.makepyfile(f"""
        def test_sth(request):
            assert request.config.artifacts_dir == '{expected}'
    """)

    # run pytest with the following cmd args
    result = pytester.runpytest("-v", *addopts)

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(
        [
            "*::test_sth PASSED*",
        ]
    )

    # make sure that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_fixture_artifacts(pytester):
    """Test that writing to the artifacts creates a directory named after the
    test case.
    """

    # create a temporary pytest test module
    pytester.makepyfile("""
        def test_sth(artifacts):
            with artifacts.open("file.txt", "w") as f:
                f.write("Hello, World!")

            with artifacts.open("file.txt", "r") as f:
                content = f.read()

            assert content == "Hello, World!"
    """)

    # run pytest with the following cmd args
    result = pytester.runpytest("--artifacts-dir=.pytest_artifacts/", "-v")

    result.stdout.fnmatch_lines(
        [
            "*::test_sth PASSED*",
        ]
    )

    assert result.ret == 0

    # fnmatch_lines does an assertion internally
    pytester.run("ls", "-a").stdout.fnmatch_lines(["*.pytest_artifacts"])
    pytester.run("find", ".pytest_artifacts", "-name", "file.txt").stdout.fnmatch_lines(
        [
            ".pytest_artifacts/test_sth/file.txt",
        ]
    )
