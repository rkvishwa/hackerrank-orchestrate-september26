from __future__ import annotations

from buy_or_wait.evidence.models import EvidenceContext, EventPatch
from buy_or_wait.ingest.loader import Dataset, FinancialEvent


class ConflictResolver:
    def __init__(self, dataset: Dataset):
        self.dataset = dataset

    def resolve(self, user_id: str, evidence: EvidenceContext) -> EvidenceContext:
        ctx = EvidenceContext(
            amount_overrides=dict(evidence.amount_overrides),
            event_patches=dict(evidence.event_patches),
            suppressed_event_ids=set(evidence.suppressed_event_ids),
            income_patches=list(evidence.income_patches),
            rent_patches=list(evidence.rent_patches),
            notes=list(evidence.notes),
            unresolved_mandatory_debits=set(evidence.unresolved_mandatory_debits),
        )

        events = self.dataset.events_by_user.get(user_id, [])
        by_id = {e.event_id: e for e in events}

        for event in events:
            if event.status == "cancelled":
                ctx.suppressed_event_ids.add(event.event_id)
                if event.linked_event_id:
                    ctx.suppressed_event_ids.add(event.linked_event_id)
            if event.status == "settled" and event.linked_event_id:
                linked = by_id.get(event.linked_event_id)
                if (linked and linked.status in {"scheduled", "pending"}
                        and linked.direction == event.direction and linked.category == event.category
                        and linked.currency == event.currency):
                    ctx.suppressed_event_ids.add(linked.event_id)

        for event in events:
            if event.status == "failed" and event.linked_event_id:
                linked = by_id.get(event.linked_event_id)
                if linked and linked.status in {"scheduled", "pending"}:
                    ctx.suppressed_event_ids.add(event.event_id)

        for event in events:
            if event.event_type == "investment_valuation" or event.status == "unrealized":
                ctx.suppressed_event_ids.add(event.event_id)

        for event_id, patch in list(ctx.event_patches.items()):
            if patch.cancel or patch.suppress:
                ctx.suppressed_event_ids.add(event_id)

        self._dedupe_refund_pairs(events, ctx)
        return ctx

    @staticmethod
    def _dedupe_refund_pairs(events: list[FinancialEvent], ctx: EvidenceContext) -> None:
        by_id = {e.event_id: e for e in events}
        for event in events:
            if event.direction != "credit" or event.status != "pending":
                continue
            if "refund" not in event.description.lower():
                continue
            if event.linked_event_id and event.linked_event_id in by_id:
                ctx.suppressed_event_ids.add(event.event_id)
