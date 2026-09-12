#!/usr/bin/env python3
"""Validate exported predictions or score public examples without accessing hidden labels."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from buy_or_wait.config import Settings
from buy_or_wait.engine import DecisionEngine
from buy_or_wait.ingest.loader import load_dataset
from buy_or_wait.artifacts.evaluation import validate_output as _validate_output, score_samples as _score_samples


def score_samples(dataset_dir):
    settings = Settings(dataset_dir=dataset_dir, llm_enabled=False, deterministic_mode=True)
    return _score_samples(dataset_dir, settings).get("accuracy", {})


def validate_output(output_path, dataset_dir, strict=True):
    settings = Settings(dataset_dir=dataset_dir, llm_enabled=False, deterministic_mode=True)
    return _validate_output(output_path, DecisionEngine(load_dataset(dataset_dir), settings))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", type=Path, default=Settings().resolved_dataset_dir)
    parser.add_argument("--output", type=Path, default=Settings().resolved_output_path)
    parser.add_argument("--score-samples", action="store_true")
    parser.add_argument("--strict", action="store_true", default=True)
    parser.add_argument("--baseline-report", type=Path,
                        help="Compare the candidate report with this release baseline")
    parser.add_argument("--candidate-report", type=Path,
                        help="Candidate evaluation_report.json used by the release gate")
    args = parser.parse_args()
    if args.baseline_report:
        if not args.candidate_report:
            parser.error("--baseline-report requires --candidate-report")
        import json
        from buy_or_wait.artifacts.release_gate import assess_release
        assessment = assess_release(json.loads(args.baseline_report.read_text(encoding="utf-8")),
                                    json.loads(args.candidate_report.read_text(encoding="utf-8")))
        print(json.dumps(assessment, indent=2))
        return 0 if assessment["eligible"] else 1
    if args.score_samples:
        for field, value in score_samples(args.dataset_dir.resolve()).items():
            print(f"{field}: {value:.1%}")
        print("Hidden-dataset accuracy: unknown")
        return 0
    errors = validate_output(args.output.resolve(), args.dataset_dir.resolve())
    if errors:
        print("\n".join(errors))
        return 1
    print("Output validation passed (contract and cash-flow replay; hidden accuracy unknown)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
