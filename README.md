# pytest-ci-harness

Pytest framework with GitHub Actions automation and an AI-inspired helper that
summarises failing test runs.

## Features

- Lightweight "AI" assistant that analyses pytest JSON reports without external
  dependencies.
- CLI tool for generating summaries that can be piped directly into CI logs.
- GitHub Actions workflow that runs unit tests on every push and pull request.

## Getting started

Create a virtual environment and install the project in editable mode:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Run the test-suite locally:

```bash
pytest
```

Generate a JSON report and feed it to the CLI:

```bash
pytest --json-report
python -m pytest_ci_harness.cli .report.json
```

## Continuous integration

The repository includes a GitHub Actions workflow located at
[.github/workflows/ci.yml](.github/workflows/ci.yml) that executes ``pytest`` on
Linux with Python 3.11.
