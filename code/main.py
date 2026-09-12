#!/usr/bin/env python3
"""Terminal entry point for Buy or Wait batch predictions."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from buy_or_wait.config import Settings
from buy_or_wait.engine import run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Buy or Wait output.csv")
    parser.add_argument("--dataset-dir", type=Path, default=None, help="Path to dataset directory")
    parser.add_argument("--output", type=Path, default=None, help="Output CSV path")
    parser.add_argument("--deterministic", action="store_true", help="Disable Azure LLM calls")
    parser.add_argument("--emit-usage-report", action="store_true", help="Write evaluation/usage_report.md")
    args = parser.parse_args()

    settings = Settings()
    if args.dataset_dir:
        settings.dataset_dir = args.dataset_dir
    if args.output:
        settings.output_path = args.output
    if args.deterministic:
        settings.deterministic_mode = True
        settings.llm_enabled = False

    results, output_path = run_pipeline(settings)
    print(f"Wrote {len(results)} predictions to {output_path}")

    if args.emit_usage_report:
        from buy_or_wait.artifacts.usage_report import write_usage_report

        report_path = ROOT / "evaluation" / "usage_report.md"
        write_usage_report(results, settings, report_path)
        print(f"Wrote usage report to {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
