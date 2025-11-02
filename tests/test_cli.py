import json
from pathlib import Path

from pytest_ci_harness.cli import main


def test_main_outputs_summary(tmp_path: Path, capsys):
    report = tmp_path / "report.json"
    payload = {
        "tests": [
            {
                "nodeid": "tests/test_cli.py::test_main_outputs_summary",
                "outcome": "passed",
                "duration": 0.2,
            }
        ]
    }
    report.write_text(json.dumps(payload))

    exit_code = main([str(report)])
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert "✅ All tests passed" in captured
