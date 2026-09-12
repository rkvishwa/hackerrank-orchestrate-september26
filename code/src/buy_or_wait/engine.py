from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from buy_or_wait.config import Settings
from buy_or_wait.domain import OUTPUT_COLUMNS, DecisionResult, PlanCandidate, SpendingChange
from buy_or_wait.evidence.resolver import EvidenceResolver
from buy_or_wait.explanation.templates import build_explanation
from buy_or_wait.finance.forecast import ForecastEngine
from buy_or_wait.ingest.loader import Dataset, RequestRow, load_dataset
from buy_or_wait.plans.enumerator import PlanEnumerator
from buy_or_wait.verification.verifier import OutputVerifier


def _format_plan(plan: PlanCandidate) -> str:
    if not plan.legs:
        return "none"
    return "|".join(f"{leg.payment_date.isoformat()}:{leg.amount}" for leg in plan.legs)


def _format_spending(changes: list[SpendingChange]) -> str:
    if not changes:
        return "none"
    parts: list[str] = []
    for change in changes:
        if change.action == "stop":
            parts.append(f"stop:{change.event_id}")
        else:
            parts.append(f"reduce_to:{change.event_id}:{change.new_amount}")
    return "|".join(parts)


def _map_status(plan: PlanCandidate, request: RequestRow, profile, amount_safe: Decimal, earliest_full: date | None) -> tuple[str, str]:
    if plan.method == "not_recommended":
        if earliest_full is None and amount_safe < request.requested_amount:
            return "not_affordable", plan.method
        if plan.method == "not_recommended":
            return "not_affordable", "not_recommended"
    if plan.method == "wait":
        return "affordable_later", plan.method
    if plan.method == "full_payment" and amount_safe >= request.requested_amount and not plan.spending_changes:
        if "full_payment" in profile.payment_methods_user_will_consider:
            return "affordable_now", plan.method
    if plan.method in {"full_payment", "partial_payment", "installments"}:
        return "affordable_with_plan", plan.method
    if plan.method == "not_recommended":
        return "not_affordable", plan.method
    return "not_affordable", plan.method


class DecisionEngine:
    def __init__(self, dataset: Dataset, settings: Settings | None = None):
        self.dataset = dataset
        self.settings = settings or Settings()
        self.forecast = ForecastEngine(dataset, self.settings)
        self.enumerator = PlanEnumerator(self.forecast)
        self.evidence = EvidenceResolver(dataset, self.settings)
        self.verifier = OutputVerifier()

    def decide(self, request: RequestRow) -> DecisionResult:
        profile = self.dataset.profiles[request.user_id]
        options = self.dataset.payment_options_by_request.get(request.request_id, [])
        amount_overrides = self.evidence.resolve_amount_overrides(request)

        amount_safe = self.forecast.max_safe_payment(
            profile, request, spending_changes=None, amount_overrides=amount_overrides
        )
        earliest = self.forecast.earliest_full_payment_date(
            profile, request, spending_changes=None, amount_overrides=amount_overrides
        )

        candidates = self.enumerator.enumerate(
            profile, request, options, amount_safe, earliest, amount_overrides
        )
        ranked = PlanEnumerator.rank(candidates)

        selected: PlanCandidate | None = ranked[0] if ranked else None
        if selected is None:
            selected = PlanCandidate(
                method="not_recommended",
                legs=[],
                total_paid=Decimal("0"),
                safe=False,
            )

        for candidate in ranked + [selected]:
            errors = self.verifier.verify_plan(request, candidate)
            if not errors and candidate.safe:
                selected = candidate
                break

        if not selected.safe:
            selected = PlanCandidate(method="not_recommended", legs=[], total_paid=Decimal("0"), safe=False)

        status, method = _map_status(selected, request, profile, amount_safe, earliest)
        earliest_str = ""
        if status == "affordable_now":
            earliest_str = request.request_date.isoformat()
        elif earliest is not None:
            earliest_str = earliest.isoformat()

        explanation = build_explanation(profile, request, selected, amount_safe, earliest_str, status)
        result = DecisionResult(
            request_id=request.request_id,
            amount_safe_to_pay=amount_safe,
            affordability_status=status,  # type: ignore[arg-type]
            recommended_payment_method=method,  # type: ignore[arg-type]
            payment_plan=_format_plan(selected),
            earliest_date_for_full_payment=earliest_str,
            spending_changes_needed=_format_spending(selected.spending_changes),
            decision_explanation=explanation,
            trace={"amount_overrides": {k: str(v) for k, v in amount_overrides.items()}},
        )
        self.verifier.verify_request_row(request, result)
        return result

    def run_batch(self, request_ids: list[str] | None = None) -> list[DecisionResult]:
        targets = (
            [self.dataset.requests_by_id[rid] for rid in request_ids]
            if request_ids
            else self.dataset.requests
        )
        return [self.decide(request) for request in targets]

    def write_output(self, results: list[DecisionResult], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=OUTPUT_COLUMNS)
            writer.writeheader()
            for result in results:
                writer.writerow(
                    {
                        "request_id": result.request_id,
                        "amount_safe_to_pay": str(result.amount_safe_to_pay),
                        "affordability_status": result.affordability_status,
                        "recommended_payment_method": result.recommended_payment_method,
                        "payment_plan": result.payment_plan,
                        "earliest_date_for_full_payment": result.earliest_date_for_full_payment,
                        "spending_changes_needed": result.spending_changes_needed,
                        "decision_explanation": result.decision_explanation,
                    }
                )


def run_pipeline(settings: Settings | None = None, request_ids: list[str] | None = None) -> tuple[list[DecisionResult], Path]:
    settings = settings or Settings()
    dataset = load_dataset(settings.resolved_dataset_dir)
    engine = DecisionEngine(dataset, settings)
    results = engine.run_batch(request_ids)
    engine.write_output(results, settings.resolved_output_path)
    return results, settings.resolved_output_path
