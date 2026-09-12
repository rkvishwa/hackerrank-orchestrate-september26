#!/usr/bin/env python3
"""Offline, evaluation-only comparison with reviewed public PR #8.

External source is supplied separately, hash checked, and never packaged. The
worker receives request inputs without answer columns and cannot use a network.
"""
import argparse
from collections import defaultdict
import csv
from dataclasses import asdict
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

COMMIT = "7c4cc0aa4698be2c558619b577e902bc5f326176"
SOURCE_HASHES = {
    "config.py": "ff43bb34fac212a5189812ce9413245d98b09528d36f0e7936deb4f49f907acc",
    "cashflow_engine.py": "1e9a6ad330621ee474c259bb3bc2e94f28bb92c408e877a71080c9d5d12e40aa",
    "decision_engine.py": "b7fece9e774ff1b72dfb8341e1a93f62c2e53627d3995238ab7cb84a0684828d",
    "data_loader.py": "a4794a58a74efb7c1801e13c3ae7227cc258fe272e2e968ed95d74ec5c3e8809",
    "message_analyzer.py": "f0a1878b714aa5c1202f671d15a2a3ced38fcf83a4e2bb5ba2466e98292de4bd",
    "explainer.py": "88fa8059d6147c422870594392671ccf4229ecc713db7fba7665e5a2d5497372",
}
REQUEST_FIELDS = ("request_id", "user_id", "request_date", "request_type", "requested_amount",
                  "desired_completion_date", "allows_partial_payment", "request_text")


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True,
                   default=lambda v: sorted(v) if isinstance(v, set) else str(v)) + "\n", encoding="utf-8")


def worker(source, dataset_dir, requests_path, output):
    def offline(event, args):
        if event.startswith("socket.") or event in {"subprocess.Popen", "os.system"}:
            raise RuntimeError("Comparison worker is offline")
        if event == "open" and isinstance(args[0], (str, bytes)):
            name = Path(os.fsdecode(args[0])).name.lower()
            if name.startswith(".env") or name in {"sample_requests.csv", "log.txt"}:
                raise RuntimeError("Comparison worker cannot read labels, credentials or conversation logs")
    sys.addaudithook(offline)
    sys.path.insert(0, str(source))
    import data_loader as loader
    from cashflow_engine import CashflowEngine
    from decision_engine import DecisionEngine
    from message_analyzer import analyze_messages_for_user
    loader.DATASET_DIR = dataset_dir
    profiles = loader.load_financial_profiles()
    events = loader.load_financial_events(profiles, loader.load_exchange_rates())
    options = loader.load_request_payment_options()
    messages = defaultdict(list)
    for item in loader.load_messages():
        messages[item["user_id"]].append(item)
    cash = CashflowEngine(profiles, events, messages)
    replays = []
    original_simulate = cash.simulate_balance

    def capture(*args, **kwargs):
        result = original_simulate(*args, **kwargs)
        payments = kwargs.get("extra_payments", args[5] if len(args) > 5 else [])
        if payments:
            replays.append({"payments": payments, "minimum_balance": result[0], "safe": result[2]})
        return result
    cash.simulate_balance = capture

    class StrictDecisionEngine(DecisionEngine):
        def find_spending_changes_for_full_payment(self, uid, day, amount, facts, profile):
            result = super().find_spending_changes_for_full_payment(uid, day, amount, facts, profile)
            if not result:
                return None
            changes = parse_changes(result[0])
            flows = cash.generate_projected_cashflows(uid, day, facts, changes)
            _, _, safe = original_simulate(uid, day, profile["current_available_balance"],
                profile["minimum_balance_to_keep"], flows, [(day, amount)])
            return result if safe else None

    def parse_changes(text):
        if text == "none":
            return {}
        parts = [part.split(":") for part in text.split("|")]
        return {p[1]: (p[0], float(p[2]) if len(p) == 3 else None) for p in parts}

    cases = []
    for request in json.loads(requests_path.read_text(encoding="utf-8")):
        assert set(request) == set(REQUEST_FIELDS)
        request["requested_amount"] = float(request["requested_amount"])
        request["allows_partial_payment"] = str(request["allows_partial_payment"]).lower() == "true"
        uid, day = request["user_id"], request["request_date"]
        profile = profiles[uid]
        facts = analyze_messages_for_user(uid, messages[uid], day)
        flows = cash.generate_projected_cashflows(uid, day, facts)
        baseline_minimum, baseline_daily, _ = original_simulate(uid, day, profile["current_available_balance"],
            profile["minimum_balance_to_keep"], flows, [])
        recurrence = cash.analyze_user_recurring(uid, day, facts)
        # Add membership provenance without changing the external estimate.
        flexible = {"dining", "streaming", "cloud_storage", "delivery_membership", "music_subscription",
                    "gym", "shopping", "entertainment"}
        for series in recurrence["monthly_expenses"] + recurrence["weekly_expenses"]:
            series["member_event_ids"] = [e["event_id"] for e in events[uid]
                if e["status"] == "settled" and e["settlement_date"] <= day and e["direction"] == "debit"
                and e["category"] == series["category"]
                and (e["category"] in flexible or e["description"] == series["description"])]
        replays.clear()
        prediction = DecisionEngine(cash).evaluate_request(request, profile, options.get(request["request_id"], []), messages[uid])
        unique_replays = list({json.dumps(r, sort_keys=True): r for r in replays}.values())
        strict = StrictDecisionEngine(cash).evaluate_request(request, profile, options.get(request["request_id"], []), messages[uid])
        selected_flows = cash.generate_projected_cashflows(uid, day, facts, parse_changes(prediction["spending_changes_needed"]))
        payments = [] if prediction["payment_plan"] == "none" else [
            (part.split(":")[0], float(part.split(":")[1])) for part in prediction["payment_plan"].split("|")]
        minimum, daily, safe = original_simulate(uid, day, profile["current_available_balance"],
            profile["minimum_balance_to_keep"], selected_flows, payments)
        cases.append({"request_id": request["request_id"], "prediction": prediction, "strict_prediction": strict,
            "baseline_flows": flows, "recurrence": recurrence, "interpreted_messages": facts,
            "baseline_minimum": baseline_minimum,
            "baseline_limiting_date": next((d for d, balance in baseline_daily if balance == baseline_minimum), day),
            "baseline_daily": baseline_daily,
            "candidate_replays": unique_replays, "selected_plan_strict_safe": safe,
            "selected_plan_minimum": minimum, "selected_plan_daily": daily,
            "minimum_required": profile["minimum_balance_to_keep"]})
    write(output, {"commit": COMMIT, "source_hashes": SOURCE_HASHES, "cases": cases,
                   "model_calls": 0, "request_labels_supplied_to_worker": False})


def run(source, dataset_dir, report_dir, evidence_cache):
    report_dir.mkdir(parents=True, exist_ok=True)
    with (dataset_dir / "sample_requests.csv").open(encoding="utf-8-sig", newline="") as handle:
        labels = list(csv.DictReader(handle))
    for name, expected in SOURCE_HASHES.items():
        if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"PR source differs from reviewed commit: {name}")
    with tempfile.TemporaryDirectory(prefix="buy-or-wait-pr8-") as temp:
        directory = Path(temp)
        external = directory / "external"
        external.mkdir()
        for name in SOURCE_HASHES:
            shutil.copy2(source / name, external / name)
        inputs = directory / "request_inputs.json"
        write(inputs, [{key: row[key] for key in REQUEST_FIELDS} for row in labels])
        result = directory / "result.json"
        environment = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP") if key in os.environ}
        subprocess.run([sys.executable, "-I", "-B", str(Path(__file__).resolve()), "--worker", "--pr-source", str(external),
            "--dataset-dir", str(dataset_dir), "--requests", str(inputs), "--worker-output", str(result)],
            env=environment, cwd=directory, check=True)
        comparison = json.loads(result.read_text(encoding="utf-8"))

    code = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(code / "src"))
    from buy_or_wait.config import Settings
    from buy_or_wait.engine import DecisionEngine
    from buy_or_wait.ingest.loader import load_dataset
    from buy_or_wait.artifacts.evaluation import normalize, SCORED_FIELDS
    engine = DecisionEngine(load_dataset(dataset_dir), Settings(_env_file=None, llm_enabled=False,
        deterministic_mode=True, evidence_cache_dir=evidence_cache))
    counts = {model: dict.fromkeys(SCORED_FIELDS, 0) for model in ("ours", "pr8", "pr8_strict")}
    complete = dict.fromkeys(counts, 0)
    for label, case in zip(labels, comparison["cases"]):
        assert label["request_id"] == case["request_id"]
        request = engine.dataset.context_requests_by_id[case["request_id"]]
        result = engine.decide(request)
        case["ours"] = {field: str(getattr(result, field)) for field in SCORED_FIELDS}
        case["our_trace"] = result.trace["case"]
        for name, row in [("ours", case["ours"]), ("pr8", case["prediction"]), ("pr8_strict", case["strict_prediction"])]:
            flags = {f: normalize(f, row[f]) == normalize(f, label[f]) for f in SCORED_FIELDS}
            for f, flag in flags.items():
                counts[name][f] += flag
            complete[name] += all(flags.values())
        ours, theirs = defaultdict(Decimal), defaultdict(Decimal)
        for flow in case["our_trace"]["baseline"]["ledger"]:
            ours[(flow["date"], flow["direction"], flow["category"])] += Decimal(flow["amount"])
        for flow in case["baseline_flows"]:
            value = Decimal(str(flow["amount"]))
            theirs[(flow["date"], "credit" if value >= 0 else "debit", flow["category"])] += abs(value)
        differences = [{"date": key[0], "direction": key[1], "category": key[2],
                        "ours": str(ours[key]), "pr8": str(theirs[key])}
                       for key in sorted(ours.keys() | theirs.keys()) if ours[key] != theirs[key]]
        case["ledger_differences"] = differences
        case["first_ledger_difference"] = differences[0] if differences else None
        case["classifications"] = []
        if case["prediction"]["payment_plan"] != "none" and not case["selected_plan_strict_safe"]:
            case["classifications"].append("comparison_implementation_reserve_violation")
        if case["our_trace"]["accounting_coverage"]["unquantified_commitments"]:
            case["classifications"].append("missing_mandatory_evidence")
        if differences:
            case["classifications"].append("recurrence_membership_timing_or_estimator_assumptions")
        case["reference"] = {f: label[f] for f in SCORED_FIELDS}
    comparison["matches"] = counts
    comparison["complete_row_matches"] = complete
    comparison["limitations"] = ["PR predictions use its own evidence interpretation and recurrence assumptions.",
        "The strict variant removes its reserve-breach fallback only; it is not a contract-approved solution.",
        "PR horizon includes day +90; our existing horizon ends on day +89.",
        "A difference from another participant does not establish an error in our implementation."]
    write(report_dir / "pr8_comparison.json", comparison)
    print(json.dumps({"matches": counts, "complete_rows": complete,
                      "unsafe_pr_recommendations": [c["request_id"] for c in comparison["cases"]
                         if c["prediction"]["payment_plan"] != "none" and not c["selected_plan_strict_safe"]]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr-source", type=Path, required=True)
    parser.add_argument("--dataset-dir", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path)
    parser.add_argument("--evidence-cache-dir", type=Path)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--requests", type=Path)
    parser.add_argument("--worker-output", type=Path)
    args = parser.parse_args()
    if args.worker:
        worker(args.pr_source.resolve(), args.dataset_dir.resolve(), args.requests, args.worker_output)
    else:
        run(args.pr_source.resolve(), args.dataset_dir.resolve(), args.report_dir.resolve(), args.evidence_cache_dir.resolve())
