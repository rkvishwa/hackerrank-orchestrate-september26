#!/usr/bin/env python3
"""Compare frozen-control and corrected code with unchanged acceptance gates."""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def historical_worker(code, dataset_dir, output):
    sys.path.insert(0, str(code / "src"))
    from buy_or_wait.config import Settings
    from buy_or_wait.ingest.loader import load_dataset
    from buy_or_wait.verification.horizon_backtest import evaluate_horizons
    from buy_or_wait.verification.backtest import historical_backtest
    data = load_dataset(dataset_dir)
    policy = Settings(_env_file=None, llm_enabled=False, deterministic_mode=True).recurrence
    write(output / "horizons.json", evaluate_horizons(data, policy))
    write(output / "timing.json", historical_backtest(data, policy))


def run(root, control, candidate, report_dir):
    history_dir = root / "artifacts" / "defect-history"
    environment = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP") if key in os.environ}
    for name, code in (("control", control / "code"), ("candidate", root / "code")):
        subprocess.run([sys.executable, "-I", "-B", str(Path(__file__).resolve()), "--history-worker",
            "--code", str(code), "--dataset-dir", str(root / "dataset"), "--output", str(history_dir / name)],
            check=True, env=environment)
    before = json.loads((history_dir / "control/horizons.json").read_text())
    after = json.loads((history_dir / "candidate/horizons.json").read_text())
    timing_before = json.loads((history_dir / "control/timing.json").read_text())
    timing_after = json.loads((history_dir / "candidate/timing.json").read_text())
    paired = deepcopy(after["summary"])
    changes = []
    for a, b in zip(before["folds"], after["folds"]):
        assert (a["user_id"], a["horizon"]) == (b["user_id"], b["horizon"])
        if a["models"].get("occurrence_q75") != b["models"].get("occurrence_q75"):
            changes.append({"user_id": b["user_id"], "horizon": b["horizon"], "split": b["split"]})
    for split, horizons in paired.items():
        for horizon, row in horizons.items():
            row["models"] = {"control": before["summary"][split][horizon]["models"]["occurrence_q75"],
                             "candidate": after["summary"][split][horizon]["models"]["occurrence_q75"]}
            row["folds_with_changed_estimates"] = sum(c["split"] == split and str(c["horizon"]) == horizon for c in changes)
    sys.path.insert(0, str(root / "code/src"))
    from buy_or_wait.verification.horizon_backtest import promotion_check
    from buy_or_wait.artifacts.release_gate import assess_release
    gates = {split: promotion_check(paired, split, models=("control", "candidate")) for split in ("development", "validation")}
    baseline = json.loads((control / "code/evaluation/evaluation_report.json").read_text())
    original = json.loads((root / "code/evaluation/reference_baseline.json").read_text())
    current = json.loads((candidate / "evaluation/evaluation_report.json").read_text())
    dataset_manifest = json.loads((control / "manifest.json").read_text())
    mismatches = []
    for relative, digest in dataset_manifest["dataset"].items():
        if hashlib.sha256((root / "dataset" / relative).read_bytes()).hexdigest() != digest:
            mismatches.append("dataset/" + relative)
    for relative, digest in dataset_manifest["evidence_cache"].items():
        if hashlib.sha256((root / "code/evaluation/evidence_cache" / relative).read_bytes()).hexdigest() != digest:
            mismatches.append("evidence_cache/" + relative)
    result = {"historical": {"paired_summary": paired, "gates": gates, "changed_folds": changes,
                 "total_folds": len(after["folds"]), "timing_folds": len(timing_after["folds"]),
                 "timing_results_identical": timing_before == timing_after,
                 "timing_summary": timing_after["summary"],
                 "limitations": after["method"]},
              "against_local_control": assess_release(baseline, current),
              "against_original_release": assess_release(original, current),
              "frozen_input_mismatches": mismatches,
              "candidate_rows": current["requests"], "contract_errors": current["contract_errors"],
              "candidate_output_identical_to_control": (candidate / "output.csv").read_bytes() == (control / "output.csv").read_bytes(),
              "promotion_eligible": False}
    result["promotion_eligible"] = (not mismatches and not current["contract_errors"] and
        all(g["eligible"] for g in gates.values()) and result["against_local_control"]["eligible"] and
        result["against_original_release"]["eligible"])
    write(report_dir / "validation.json", result)
    print(json.dumps({k: result[k] for k in ("against_local_control", "against_original_release", "candidate_rows",
                      "contract_errors", "candidate_output_identical_to_control", "promotion_eligible")}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--history-worker", action="store_true")
    parser.add_argument("--code", type=Path)
    parser.add_argument("--dataset-dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--control", type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--report-dir", type=Path)
    args = parser.parse_args()
    if args.history_worker:
        historical_worker(args.code, args.dataset_dir, args.output)
    else:
        run(args.root.resolve(), args.control.resolve(), args.candidate.resolve(), args.report_dir.resolve())
