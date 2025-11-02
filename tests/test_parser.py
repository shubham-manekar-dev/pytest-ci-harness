import json
from pathlib import Path

import pytest

from pytest_ci_harness.parser import parse_pytest_json_report


@pytest.fixture()
def json_report(tmp_path: Path) -> Path:
    payload = {
        "tests": [
            {
                "nodeid": "tests/test_example.py::test_ok",
                "outcome": "passed",
                "duration": 0.12,
                "captured_output": "",
            },
            {
                "nodeid": "tests/test_example.py::test_fail",
                "outcome": "failed",
                "duration": 0.45,
                "captured_output": "AssertionError: bad",
            },
        ]
    }
    report_path = tmp_path / "report.json"
    report_path.write_text(json.dumps(payload))
    return report_path


def test_parse_pytest_json_report(json_report: Path):
    summary = parse_pytest_json_report(json_report)

    assert len(summary.cases) == 2
    assert summary.has_failures is True
    assert summary.failures[0].nodeid.endswith("test_fail")
    assert summary.failures[0].captured_output == "AssertionError: bad"


def test_parse_invalid_top_level(tmp_path: Path):
    report_path = tmp_path / "invalid.json"
    report_path.write_text("[1, 2, 3]")

    with pytest.raises(ValueError):
        parse_pytest_json_report(report_path)
