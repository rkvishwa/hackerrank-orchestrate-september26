from __future__ import annotations

import json
import re
from decimal import Decimal
from pathlib import Path

from buy_or_wait.config import Settings
from buy_or_wait.ingest.loader import Dataset, RequestRow


class EvidenceResolver:
    def __init__(self, dataset: Dataset, settings: Settings | None = None):
        self.dataset = dataset
        self.settings = settings or Settings()
        self.cache_dir = self.settings.resolved_evidence_cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def resolve_amount_overrides(self, request: RequestRow) -> dict[str, Decimal]:
        overrides: dict[str, Decimal] = {}
        user_events = self.dataset.events_by_user.get(request.user_id, [])
        for event in user_events:
            if event.amount is not None:
                continue
            image = self.dataset.images_by_event.get(event.event_id)
            if not image:
                continue
            amount = self._extract_image_amount(image.image_id)
            if amount is not None:
                overrides[event.event_id] = amount
        return overrides

    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def _extract_image_amount(self, image_id: str) -> Decimal | None:
        cache_file = self._cache_path(f"image_{image_id}")
        if cache_file.exists():
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            if data.get("amount") is not None:
                return Decimal(str(data["amount"]))

        image_path = self.dataset.media_dir / f"{image_id}.png"
        if not image_path.exists():
            return None

        amount = self._rule_based_image_amount(image_path)
        if amount is None and self.settings.llm_enabled and not self.settings.deterministic_mode:
            from buy_or_wait.llm.azure_client import AzureEvidenceClient

            client = AzureEvidenceClient(self.settings)
            amount = client.extract_image_amount(image_path, image_id)

        if amount is not None:
            cache_file.write_text(json.dumps({"amount": str(amount)}), encoding="utf-8")
        return amount

    @staticmethod
    def _rule_based_image_amount(image_path: Path) -> Decimal | None:
        # Deterministic fallback without OCR dependencies.
        return None
