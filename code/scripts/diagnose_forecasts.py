#!/usr/bin/env python3
"""Reproduce reviewed ledgers and historical backtests locally, without API calls."""
import argparse
from collections import defaultdict
from decimal import Decimal
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from buy_or_wait.config import Settings
from buy_or_wait.engine import DecisionEngine
from buy_or_wait.ingest.loader import load_dataset
from buy_or_wait.verification.backtest import historical_backtest
from buy_or_wait.verification.source_ledger import reconstruct_reviewed_case
from buy_or_wait.verification.source_ledger import read_rows
from buy_or_wait.artifacts.evaluation import score_samples


def compare_ledger(reviewed, engine, request):
    def buckets(flows):
        result = defaultdict(lambda: Decimal(0))
        for f in flows:
            result[(f["date"], f["direction"], f["category"])] += Decimal(f["amount"])
        return result
    left = buckets(reviewed["transactions"])
    context = engine.evidence.resolve(request)
    right = buckets([dict(date=str(f.flow_date), direction=f.direction, category=f.category, amount=str(f.amount))
                     for f in engine.forecast.build_cashflows(engine.dataset.profiles[request.user_id], request, evidence=context)])
    differences = [{"date": k[0], "direction": k[1], "category": k[2],
                    "reviewed_amount": str(left.get(k, 0)), "engine_amount": str(right.get(k, 0))}
                   for k in sorted(set(left) | set(right)) if left.get(k, 0) != right.get(k, 0)]
    result = engine.decide(request)
    return {"first_ledger_difference": differences[0] if differences else None,
            "ledger_differences": differences, "engine_amount": str(result.amount_safe_to_pay),
            "engine_earliest": result.earliest_date_for_full_payment,
            "capacity_agrees": Decimal(reviewed["amount_safe"]) == result.amount_safe_to_pay
                               and reviewed["earliest_full"] == result.earliest_date_for_full_payment}


def run(dataset_dir, report_dir, cache_dir):
    settings = Settings(_env_file=None, dataset_dir=dataset_dir, evidence_cache_dir=cache_dir,
                        deterministic_mode=True, llm_enabled=False)
    dataset = load_dataset(dataset_dir)
    engine = DecisionEngine(dataset, settings)
    specs = json.loads((ROOT / "evaluation" / "reviewed_cases.json").read_text(encoding="utf-8"))
    cases = []
    for spec in specs:
        reviewed = reconstruct_reviewed_case(dataset_dir, spec)
        request = dataset.context_requests_by_id[spec["request_id"]]
        reviewed["comparison"] = compare_ledger(reviewed, engine, request)
        # Reference comparison happens only after the independent ledger is frozen.
        label = next(r for r in read_rows(dataset_dir, "sample_requests") if r["request_id"] == spec["request_id"])
        cumulative = Decimal(0)
        payments = {}
        if label["payment_plan"] != "none":
            for leg in label["payment_plan"].split("|"):
                day, amount = leg.split(":")
                payments[day] = payments.get(day, Decimal(0)) + Decimal(amount)
        margins = []
        for row in reviewed["daily"]:
            cumulative += payments.get(row["date"], Decimal(0))
            margins.append({"date": row["date"], "headroom": str(Decimal(row["headroom"]) - cumulative)})
        reviewed["reference_comparison"] = {
            "sample_amount": label["amount_safe_to_pay"], "sample_earliest": label["earliest_date_for_full_payment"],
            "sample_plan": label["payment_plan"],
            "sample_plan_limiting_day": min(margins, key=lambda r: Decimal(r["headroom"])),
            "interpretation": "Safety on the reviewed forecast assumptions only; not proof that the reference is wrong."}
        cases.append(reviewed)
    backtest = historical_backtest(dataset, settings.recurrence)
    samples = score_samples(dataset_dir, settings)
    report_dir.mkdir(parents=True, exist_ok=True)
    for name, data in [("independent_cases", cases), ("historical_backtest", backtest),
                       ("diagnostic_sample_metrics", {k: samples[k] for k in ("matches", "amount_diagnostics", "comparisons")})]:
        (report_dir / (name + ".json")).write_text(json.dumps(data, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"cases": [{"request_id": c["request"]["request_id"], "amount": c["amount_safe"],
                                 "earliest": c["earliest_full"], **c["comparison"]} for c in cases],
                      "historical_backtest": backtest["summary"], "sample_matches": samples["matches"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", type=Path, default=ROOT.parent / "dataset")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "evaluation")
    parser.add_argument("--evidence-cache-dir", type=Path, default=ROOT / "evaluation" / "evidence_cache")
    args = parser.parse_args()
    run(args.dataset_dir.resolve(), args.report_dir.resolve(), args.evidence_cache_dir.resolve())
