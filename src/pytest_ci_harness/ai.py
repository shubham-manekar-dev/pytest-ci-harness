"""Simple heuristics to reason about pytest results.

The goal of this module is to provide a small, deterministic "AI" helper that can
summarise pytest runs in continuous integration (CI) environments.  Instead of
relying on remote services, we implement a few light-weight heuristics that make
context-aware suggestions for failing tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List


@dataclass(frozen=True)
class PytestCaseResult:
    """Represents a single pytest test case result.

    Attributes
    ----------
    nodeid:
        Fully qualified test identifier reported by pytest (e.g. ``tests/test_example.py::test_pass``).
    outcome:
        Raw outcome string from pytest.  Typically one of ``passed``, ``failed``, ``skipped`` or
        ``xfailed`` / ``xpassed`` when xfail markers are involved.
    duration:
        Execution time in seconds as reported by pytest.  The duration is stored as a ``float`` to
        simplify arithmetic during analysis.
    captured_output:
        Optional stdout/stderr output captured for the test.  Including a snippet of the failure
        output helps the assistant provide actionable hints.
    """

    nodeid: str
    outcome: str
    duration: float
    captured_output: str = ""

    def is_success(self) -> bool:
        """Return ``True`` if the test should be considered successful."""

        return self.outcome in {"passed", "xfailed", "skipped"}

    def is_failure(self) -> bool:
        """Return ``True`` if the test run indicates a failure or error."""

        return not self.is_success()


@dataclass
class PytestRunSummary:
    """Aggregated information for an entire pytest run."""

    cases: List[PytestCaseResult] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.cases = list(self.cases)

    @property
    def failures(self) -> List[PytestCaseResult]:
        """Return a list with only the failing cases."""

        return [case for case in self.cases if case.is_failure()]

    @property
    def total_duration(self) -> float:
        """Return the total duration of the test run."""

        return sum(case.duration for case in self.cases)

    @property
    def has_failures(self) -> bool:
        """Whether any case in the summary indicates a failure."""

        return any(case.is_failure() for case in self.cases)

    def add_case(self, case: PytestCaseResult) -> None:
        """Add a case to the summary."""

        self.cases.append(case)

    @classmethod
    def from_iterable(cls, cases: Iterable[PytestCaseResult]) -> "PytestRunSummary":
        """Create a summary from an iterable of cases."""

        return cls(list(cases))


class SimpleAIAgent:
    """A small deterministic helper that summarises pytest outcomes."""

    success_prefix = "✅ All tests passed"
    failure_prefix = "❌ Tests failing"

    def __init__(self, recent_history: int = 5) -> None:
        self.recent_history = recent_history
        self.history: List[str] = []

    def _remember(self, message: str) -> None:
        self.history.append(message)
        if len(self.history) > self.recent_history:
            self.history = self.history[-self.recent_history :]

    def summarise(self, summary: PytestRunSummary) -> str:
        """Produce a short summary for the CI logs."""

        if not summary.cases:
            message = "ℹ️ No tests were collected. Ensure pytest discovered your test suite."
            self._remember(message)
            return message

        if summary.has_failures:
            failing = summary.failures
            headline = f"{self.failure_prefix}: {len(failing)} failing of {len(summary.cases)}"
            suggestions = self._suggestions(failing)
            message = "\n".join([headline, *suggestions])
            self._remember(message)
            return message

        message = f"{self.success_prefix} in {summary.total_duration:.2f}s."
        self._remember(message)
        return message

    def _suggestions(self, failures: List[PytestCaseResult]) -> List[str]:
        """Generate deterministic hints based on failing tests."""

        hints: List[str] = []
        longest = max(failures, key=lambda case: case.duration)
        hints.append(
            "Longest failing test: ``{node}`` ({duration:.2f}s).".format(
                node=longest.nodeid, duration=longest.duration
            )
        )
        flaky = [case for case in failures if "flake" in case.captured_output.lower()]
        if flaky:
            hints.append(
                "Potential flakiness detected in: {nodes}.".format(
                    nodes=", ".join(case.nodeid for case in flaky)
                )
            )
        first = failures[0]
        excerpt = first.captured_output.strip().splitlines()[:3]
        if excerpt:
            hints.append("Failure excerpt (first 3 lines):")
            hints.extend(f"> {line}" for line in excerpt)
        else:
            hints.append("No captured output available for the first failing test.")

        if self.history:
            hints.append("Last suggestions:")
            hints.extend(f"- {entry}" for entry in self.history)

        return hints


__all__ = ["PytestCaseResult", "PytestRunSummary", "SimpleAIAgent"]
