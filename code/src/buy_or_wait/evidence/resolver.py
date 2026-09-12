from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from buy_or_wait.config import Settings
from buy_or_wait.evidence.cache import EvidenceCache, image_source_hash
from buy_or_wait.evidence.conflicts import ConflictResolver
from buy_or_wait.evidence.image_catalog import infer_amount_role
from buy_or_wait.evidence.messages import MessageResolver
from buy_or_wait.evidence.models import EvidenceContext, EventPatch, ExtractedAmount
from buy_or_wait.ingest.loader import Dataset, FinancialEvent, RequestRow


class EvidenceResolver:
    def __init__(self, dataset: Dataset, settings: Settings | None = None):
        self.dataset = dataset
        self.settings = settings or Settings()
        self.cache_dir = self.settings.resolved_evidence_cache_dir
        self.cache = EvidenceCache(self.cache_dir, self.dataset.version_hash)
        self.messages = MessageResolver(dataset, self.settings)
        self.conflicts = ConflictResolver(dataset)
        self._resolved = {}

    def resolve(self, request: RequestRow) -> EvidenceContext:
        key = (request.user_id, request.request_id, request.request_date)
        if key in self._resolved:
            return self._resolved[key]
        ctx = EvidenceContext()
        user_events = self.dataset.events_by_user.get(request.user_id, [])

        for event in user_events:
            images = self.dataset.image_records_by_event.get(event.event_id, [])
            if not images and self.dataset.images_by_event.get(event.event_id):
                images = [self.dataset.images_by_event[event.event_id]]
            images = [i for i in images if i.user_id == request.user_id
                      and (not i.request_id or i.request_id == request.request_id)]
            if not images:
                if event.amount is not None:
                    continue
                if event.direction == "debit" and event.status in {"pending", "scheduled"}:
                    ctx.unresolved_mandatory_debits.add(event.event_id)
                continue
            from buy_or_wait.evidence.structured import FactExtractor, select_document_amount
            amounts = []
            for image in images:
                prepared = FactExtractor(self.dataset, self.settings).image(image)
                reviewed = self.cache.read("image", image.image_id, image_source_hash(
                    self.dataset.media_dir / f"{image.image_id}.png", event)) if (self.dataset.media_dir / f"{image.image_id}.png").exists() else None
                selected = select_document_amount(prepared, event) if prepared else None
                if selected:
                    amount, selection = selected
                    resolution = "document role and settlement-date conditions"
                    if reviewed and reviewed.get("source") == "reviewed_image" and Decimal(str(reviewed["amount"])) != amount:
                        resolution = "vision disagrees with source-bound reviewed image; retained reviewed amount"
                        amount = Decimal(str(reviewed["amount"]))
                    amounts.append(amount)
                    ctx.fact_audit.append({"source_id": image.image_id, "user_id": request.user_id,
                        "event_id": event.event_id, "extraction": prepared["extraction"],
                        "selection": selection, "selected_amount": str(amount), "resolution": resolution})
                elif event.amount is None:
                    old = self._extract_image_amount(event, image.image_id)
                    if old:
                        amounts.append(old.amount)
            if len(set(amounts)) > 1:
                raise ValueError(f"Conflicting image evidence requires review: {event.event_id}")
            extracted = ExtractedAmount(amounts[0], event.currency) if amounts else None
            if extracted is None:
                if event.direction == "debit" and event.status in {"pending", "scheduled"}:
                    ctx.unresolved_mandatory_debits.add(event.event_id)
                continue
            if extracted.currency and extracted.currency != event.currency:
                raise ValueError(f"Image currency mismatch for {event.event_id}")
            ctx.amount_overrides[event.event_id] = extracted.amount
            ctx.event_patches[event.event_id] = EventPatch(
                event_id=event.event_id,
                amount=extracted.amount,
                currency=extracted.currency or event.currency,
                source="verified_image", explicit=False,
            )

        message_ctx = self.messages.resolve_for_user(
            request.user_id, request.request_date, request.request_id
        )
        ctx = ctx.merge(message_ctx)
        ctx = self.conflicts.resolve(request.user_id, ctx)
        self._resolved[key] = ctx
        return ctx

    def resolve_amount_overrides(self, request: RequestRow) -> dict[str, Decimal]:
        return self.resolve(request).amount_overrides

    def _extract_image_amount(self, event: FinancialEvent, image_id: str) -> ExtractedAmount | None:
        image_path = self.dataset.media_dir / f"{image_id}.png"
        if not image_path.exists():
            return None

        source_hash = image_source_hash(image_path, event)
        cached = self.cache.read("image", image_id, source_hash)
        if cached and cached.get("amount") is not None:
            amount = Decimal(str(cached["amount"]))
            if not amount.is_finite() or amount < 0 or cached.get("event_id") != event.event_id:
                raise ValueError(f"Invalid cached evidence for {event.event_id}")
            from buy_or_wait.llm.usage import UsageTracker
            UsageTracker.instance().cache_hit(cached.get("source", "cache"), source_hash)
            return ExtractedAmount(
                amount,
                cached.get("currency", event.currency),
                cached.get("amount_role", "unknown"),
                cached.get("confidence", 1.0),
                cached.get("source", "cache"),
            )

        extracted = None
        if self.settings.llm_enabled and not self.settings.deterministic_mode:
            extracted = self._llm_image_amount(event, image_id, image_path)

        if extracted is not None:
            if (not extracted.amount.is_finite() or extracted.amount < 0 or extracted.confidence < 0.8
                    or extracted.currency != event.currency):
                raise ValueError(f"Uncertain or inconsistent image evidence for {event.event_id}")
            from buy_or_wait.llm.usage import UsageTracker
            UsageTracker.instance().evidence_hashes.add(source_hash)
            self.cache.write(
                "image",
                image_id,
                source_hash,
                {
                    "amount": str(extracted.amount),
                    "currency": extracted.currency,
                    "amount_role": extracted.amount_role,
                    "confidence": extracted.confidence,
                    "source": extracted.source,
                    "event_id": event.event_id,
                },
            )
        return extracted

    def _rule_based_image_amount(self, event: FinancialEvent, image_id: str) -> ExtractedAmount | None:
        # IDs are identifiers, never evidence of an amount.
        return None

    def _llm_image_amount(
        self, event: FinancialEvent, image_id: str, image_path: Path
    ) -> ExtractedAmount | None:
        from buy_or_wait.llm.azure_client import AzureEvidenceClient

        role = infer_amount_role(event.description, event.direction, event.status)
        client = AzureEvidenceClient(self.settings)
        result = client.extract_image_amount(
            image_path,
            image_id,
            event_description=event.description,
            direction=event.direction,
            category=event.category,
            status=event.status,
            currency=event.currency,
            settlement_date=event.settlement_date.isoformat(),
            amount_role=role,
        )
        if result is None:
            return None
        return ExtractedAmount(
            result["amount"],
            result.get("currency") or event.currency,
            result.get("amount_role", role),
            float(result.get("confidence", 0.8)),
            "azure",
        )
