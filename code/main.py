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
    parser.add_argument("--report-dir", type=Path, default=None, help="Directory for matching usage and evaluation reports")
    parser.add_argument("--evidence-cache-dir", type=Path, default=None, help="Validated evidence cache")
    parser.add_argument("--prepare-evidence", action="store_true", help="Extract all messages/images without running predictions")
    args = parser.parse_args()

    settings = Settings()
    if args.dataset_dir:
        settings.dataset_dir = args.dataset_dir
    if args.output:
        settings.output_path = args.output
    if args.report_dir:
        settings.report_dir = args.report_dir
    if args.evidence_cache_dir:
        settings.evidence_cache_dir = args.evidence_cache_dir
    if args.deterministic:
        settings.deterministic_mode = True
        settings.llm_enabled = False

    if args.prepare_evidence:
        from buy_or_wait.ingest.loader import load_dataset
        from buy_or_wait.evidence.prepare import prepare_evidence
        prepare_evidence(load_dataset(settings.resolved_dataset_dir), settings)
        return 0
    results, output_path = run_pipeline(settings)
    print(f"Wrote {len(results)} predictions to {output_path}")

    print(f"Wrote matching reports to {settings.resolved_report_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
