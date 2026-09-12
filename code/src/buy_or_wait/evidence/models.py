from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Literal

AmountRole = Literal[
    "net_pay",
    "balance_due",
    "amount_due",
    "invoice_total",
    "total_paid",
    "total_fare",
    "unknown",
]


@dataclass
class ExtractedAmount:
    amount: Decimal
    currency: str
    amount_role: AmountRole = "unknown"
    confidence: float = 1.0
    source: str = "rule"
    warnings: list[str] = field(default_factory=list)


@dataclass
class EventPatch:
    event_id: str
    amount: Decimal | None = None
    currency: str | None = None
    settlement_date: date | None = None
    status: str | None = None
    cancel: bool = False
    suppress: bool = False
    source: str = ""
    observed_at: str = ""
    explicit: bool = True


@dataclass
class IncomeSchedulePatch:
    category: str = "salary"
    amount: Decimal | None = None
    effective_from: date | None = None
    stop_after: date | None = None
    effective_until: date | None = None
    resume_from: date | None = None
    currency: str | None = None


@dataclass
class RentPatch:
    multiplier: Decimal
    effective_from: date


@dataclass
class EvidenceContext:
    amount_overrides: dict[str, Decimal] = field(default_factory=dict)
    event_patches: dict[str, EventPatch] = field(default_factory=dict)
    suppressed_event_ids: set[str] = field(default_factory=set)
    income_patches: list[IncomeSchedulePatch] = field(default_factory=list)
    rent_patches: list[RentPatch] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    unresolved_mandatory_debits: set[str] = field(default_factory=set)

    def merge(self, other: EvidenceContext) -> EvidenceContext:
        patches = dict(self.event_patches)
        for event_id, incoming in other.event_patches.items():
            current = patches.get(event_id)
            if current is None:
                patches[event_id] = incoming
                continue
            if current.explicit != incoming.explicit:
                winner = incoming if incoming.explicit else current
            elif current.source == incoming.source and current.observed_at != incoming.observed_at:
                winner = max((current, incoming), key=lambda p: p.observed_at)
            elif current.status == "settled" or incoming.status == "settled":
                winner = current if current.status == "settled" else incoming
            elif current.cancel or incoming.cancel:
                winner = current if current.cancel else incoming
            else:
                winner = incoming
            patches[event_id] = winner
        suppressed = self.suppressed_event_ids | other.suppressed_event_ids
        for event_id, patch in patches.items():
            if patch.status == "settled" and not patch.cancel and not patch.suppress:
                suppressed.discard(event_id)
        merged = EvidenceContext(
            amount_overrides={**self.amount_overrides, **other.amount_overrides},
            event_patches=patches,
            suppressed_event_ids=suppressed,
            income_patches=[*self.income_patches, *other.income_patches],
            rent_patches=[*self.rent_patches, *other.rent_patches],
            notes=[*self.notes, *other.notes],
            unresolved_mandatory_debits=self.unresolved_mandatory_debits | other.unresolved_mandatory_debits,
        )
        return merged
