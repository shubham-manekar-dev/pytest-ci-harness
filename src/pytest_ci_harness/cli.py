"""Command line interface for producing AI-assisted summaries of pytest runs."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .ai import SimpleAIAgent
from .parser import parse_pytest_json_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="Path to the pytest --json-report output")
    parser.add_argument(
        "--history",
        type=int,
        default=5,
        help="Number of previous summaries to retain for context (default: 5)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    summary = parse_pytest_json_report(args.report)
    agent = SimpleAIAgent(recent_history=args.history)
    message = agent.summarise(summary)
    print(message)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
