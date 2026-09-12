#!/usr/bin/env python3
"""Evaluate one frozen expense alternative; never change the production default."""
import argparse
from collections import defaultdict
from dataclasses import asdict
from decimal import Decimal
import json
from pathlib import Path
import sys

CODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE / "src"))

from buy_or_wait.config import Settings
from buy_or_wait.engine import DecisionEngine
from buy_or_wait.ingest.loader import load_dataset
from buy_or_wait.artifacts.evaluation import forecast_audit, score_samples, SCORED_FIELDS, validate_output
from buy_or_wait.llm.usage import UsageTracker
from buy_or_wait.verification.expense_candidate import calendar_window_engine, calendar_window_estimate
from buy_or_wait.verification.horizon_backtest import evaluate_horizons


def attribution(engine, request):
    evidence = engine.evidence.resolve(request)
    audit = forecast_audit(engine, request, evidence)
    binding = audit["binding_cashflow"]
    groups = defaultdict(lambda: {"credit": Decimal(0), "debit": Decimal(0), "sources": []})
    for flow in audit["ledger"]:
        if binding["source"] == "opening_balance":
            break
        group = groups[flow["category"]]
        group[flow["direction"]] += Decimal(flow["amount"])
        group["sources"].append(flow["source"])
        if flow == binding:
            break
    result = engine.decide(request)
    changes = []
    for change in engine.enumerator._eligible_spending_changes(engine.dataset.profiles[request.user_id], request, evidence):
        changes.append({"action": asdict(change), "capacity_with_this_change": str(engine.forecast.max_safe_payment(
            engine.dataset.profiles[request.user_id], request, spending_changes=[change], evidence=evidence))})
    return {"request": asdict(request), "opening_balance": audit["opening_balance"],
            "reserve": str(engine.dataset.profiles[request.user_id].minimum_balance_to_keep),
            "binding_transaction": binding, "contributions_through_binding": dict(groups),
            "evidence": asdict(evidence), "single_spending_change_checks": changes,
            "prediction": {field: str(getattr(result, field)) for field in SCORED_FIELDS}, "forecast": audit}


def run(dataset_dir, report_dir, cache_dir):
    settings = Settings(_env_file=None, dataset_dir=dataset_dir, evidence_cache_dir=cache_dir,
                        llm_enabled=False, deterministic_mode=True)
    dataset = load_dataset(dataset_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    specification = {
        "models": ["occurrence_q75", "calendar_window_q75"],
        "window_days": 30, "windows": 3, "minimum_occurrences_per_window": 2,
        "quantile": "0.75 nearest rank", "rounding": "upward to cent",
        "categories": ["groceries", "transport", "dining"],
        "fallback": "existing estimator for sparse, constant or incomplete series",
        "split": "SHA-256(expense-horizon-v1: + user_id) mod 10; 0..2 validation, others development; sample users audit only",
        "historical_gate": "No worsening at any horizon in cumulative amount error, total/prefix underprediction, "
                           "net-cash overstatement or underpredicted fold count; at least one accuracy improvement",
        "sample_gate": "No count regression in any of the six fields against current local control and lower amount error",
        "release_gate": "Existing 3ba63a8 release gate is additionally required; experiment never deploys",
        "dataset_sha256": dataset.version_hash,
    }
    def write(name, value):
        (report_dir / name).write_text(json.dumps(value, indent=2, default=lambda v: sorted(v) if isinstance(v, set) else str(v)) + "\n", encoding="utf-8")
    # Persist the complete alternative and gates before examining any outcomes.
    write("specification.json", specification)
    historical = evaluate_horizons(dataset, settings.recurrence)
    write("historical_horizons.json", historical)
    print(json.dumps({"historical_selection": historical["selection"], "summary": historical["summary"]}, indent=2), flush=True)

    control_engine = DecisionEngine(dataset, settings)
    alternative_engine = calendar_window_engine(dataset, settings)
    traces = []
    for rid in ("request_06", "request_12", "request_19", "request_07"):
        request = dataset.context_requests_by_id[rid]
        traces.append({"request_id": rid, "control": attribution(control_engine, request),
                       "alternative": attribution(alternative_engine, request)})
    write("request_attribution.json", traces)
    # Public labels enter only after the alternative and historical decision are frozen.
    samples = {}
    for name, factory in (("control", None), ("alternative", calendar_window_engine)):
        result = score_samples(dataset_dir, settings, engine_factory=factory)
        samples[name] = {key: result[key] for key in ("matches", "amount_diagnostics", "comparisons")}
    regressions = [field for field in SCORED_FIELDS if samples["alternative"]["matches"][field] < samples["control"]["matches"][field]]
    amount_improved = Decimal(samples["alternative"]["amount_diagnostics"]["mean_absolute_error_fraction_of_request"]) < Decimal(samples["control"]["amount_diagnostics"]["mean_absolute_error_fraction_of_request"])
    samples["promotion"] = {"count_regressions": regressions, "amount_error_improved": amount_improved,
                            "eligible": not regressions and amount_improved and historical["selection"]["promote"]}
    with UsageTracker.scoped(settings.model_prices) as tracker:
        results = alternative_engine.run_batch()
        output = report_dir / "experimental_output.csv"
        alternative_engine.write_output(results, output)
        errors = validate_output(output, alternative_engine)
    samples["experimental_full_run"] = {"requests": len(results), "contract_errors": errors,
                                        "usage": tracker.summary(len(results)),
                                        "output": output.name, "production_default": False}
    if errors:
        samples["promotion"]["eligible"] = False
    write("sample_comparison.json", samples)
    print(json.dumps({"sample_matches": {name: samples[name]["matches"] for name in ("control", "alternative")},
                      "promotion": samples["promotion"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", type=Path, default=CODE.parent / "dataset")
    parser.add_argument("--report-dir", type=Path, default=CODE / "evaluation" / "expense_experiment")
    parser.add_argument("--evidence-cache-dir", type=Path, default=CODE / "evaluation" / "evidence_cache")
    args = parser.parse_args()
    run(args.dataset_dir.resolve(), args.report_dir.resolve(), args.evidence_cache_dir.resolve())
