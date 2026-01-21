def test_help_message(pytester):
    result = pytester.runpytest(
        "--help",
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(
        [
            "artifacts:",
            "*--artifacts-dir=ARTIFACTS_DIR",
        ]
    )
