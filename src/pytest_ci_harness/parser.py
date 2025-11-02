"""Utilities for parsing pytest JSON reports."""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator, Mapping, MutableMapping
from pathlib import Path
from typing import Any

from .ai import PytestCaseResult, PytestRunSummary


def _iter_cases(report: Mapping[str, Any]) -> Iterator[PytestCaseResult]:
    """Yield :class:`PytestCaseResult` objects from a JSON report mapping."""

    tests_obj = report.get("tests", [])
    if not isinstance(tests_obj, Iterable) or isinstance(tests_obj, (str, bytes)):
        tests_iterable: Iterable[Any] = []
    else:
        tests_iterable = tests_obj

    for entry in tests_iterable:
        if not isinstance(entry, MutableMapping):
            continue
        nodeid = str(entry.get("nodeid", "<unknown>"))
        outcome = str(entry.get("outcome", "failed"))
        duration = float(entry.get("duration", 0.0) or 0.0)
        captured = str(entry.get("captured_output", ""))
        yield PytestCaseResult(nodeid=nodeid, outcome=outcome, duration=duration, captured_output=captured)


def parse_pytest_json_report(path: Path | str) -> PytestRunSummary:
    """Parse a pytest JSON report file into a :class:`PytestRunSummary`.

    Parameters
    ----------
    path:
        The file path to the JSON report generated via ``pytest --json-report``.
    """

    report_path = Path(path)
    data = json.loads(report_path.read_text())
    if not isinstance(data, MutableMapping):
        raise ValueError("Pytest JSON report must be a mapping at the top level.")
    return PytestRunSummary.from_iterable(_iter_cases(data))


__all__ = ["parse_pytest_json_report"]
