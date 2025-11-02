from pytest_ci_harness.ai import PytestCaseResult, PytestRunSummary, SimpleAIAgent


def test_summarise_success_run():
    summary = PytestRunSummary(
        [
            PytestCaseResult("tests/test_example.py::test_alpha", "passed", 0.1),
            PytestCaseResult("tests/test_example.py::test_beta", "xfailed", 0.05),
        ]
    )
    agent = SimpleAIAgent()

    message = agent.summarise(summary)

    assert message.startswith("✅ All tests passed"), message
    assert "0.15" in message


def test_summarise_failure_report_includes_history():
    summary = PytestRunSummary(
        [
            PytestCaseResult(
                nodeid="tests/test_example.py::test_gamma",
                outcome="failed",
                duration=0.8,
                captured_output="AssertionError: expected 42 got 0\npossible flake",
            ),
            PytestCaseResult(
                nodeid="tests/test_example.py::test_delta",
                outcome="error",
                duration=0.3,
                captured_output="ValueError: boom",
            ),
        ]
    )

    agent = SimpleAIAgent()
    first = agent.summarise(summary)
    second = agent.summarise(summary)

    assert first.splitlines()[0].startswith("❌ Tests failing: 2")
    assert "Potential flakiness detected" in first
    assert "Failure excerpt" in first
    assert "Last suggestions:" in second
