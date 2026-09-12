"""Compare an evaluated candidate against an immutable public-sample baseline."""
from decimal import Decimal
from buy_or_wait.artifacts.evaluation import SCORED_FIELDS


def assess_release(baseline, candidate):
    reasons = []
    if candidate.get("contract_errors"):
        reasons.append("candidate has contract violations")
    if not candidate.get("full_dataset") or candidate.get("requests") != baseline.get("requests"):
        reasons.append("candidate is not a matching full-dataset run")
    for key in ("dataset_sha256", "sample_dataset_sha256"):
        if candidate.get(key) != baseline.get(key):
            reasons.append(f"{key} differs; baseline comparison is not valid")
    old, new = baseline["samples"], candidate["samples"]
    if old["request_count"] != new["request_count"]:
        reasons.append("sample request count differs")
    comparisons = {}
    improved = False
    for field in SCORED_FIELDS:
        before, after = old["matches"][field], new["matches"][field]
        comparisons[field] = {"baseline": before, "candidate": after, "delta": after - before}
        if after < before:
            reasons.append(f"{field} regressed: {before} -> {after}")
        improved |= after > before
    key = "mean_absolute_error_fraction_of_request"
    old_error = Decimal(old["amount_diagnostics"][key])
    new_error = Decimal(new["amount_diagnostics"][key])
    improved |= new_error < old_error
    if not improved:
        reasons.append("no sample match count or normalized amount error improved")
    return {"eligible": not reasons, "reasons": reasons, "matches": comparisons,
            "baseline_amount_error": str(old_error), "candidate_amount_error": str(new_error)}
