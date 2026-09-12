from __future__ import annotations

import base64
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from buy_or_wait.config import Settings
from buy_or_wait.llm.usage import UsageTracker


class AzureEvidenceClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.tracker = UsageTracker.instance()

    @property
    def enabled(self) -> bool:
        return bool(
            self.settings.llm_enabled
            and not self.settings.deterministic_mode
            and self.settings.azure_openai_endpoint
            and self.settings.azure_openai_api_key
        )

    def _client(self):
        from openai import AzureOpenAI

        return AzureOpenAI(
            azure_endpoint=self.settings.azure_openai_endpoint,
            api_key=self.settings.azure_openai_api_key,
            api_version=self.settings.azure_openai_api_version,
        )

    def extract_image_amount(self, image_path: Path, image_id: str) -> Decimal | None:
        if not self.enabled:
            return None
        client = self._client()
        image_bytes = image_path.read_bytes()
        b64 = base64.b64encode(image_bytes).decode("ascii")
        deployment = self.settings.azure_vision_deployment or self.settings.azure_chat_deployment
        response = client.chat.completions.create(
            model=deployment,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "Extract the primary monetary amount from the document. Return JSON: {\"amount\": number|null, \"currency\": string|null}.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Image ID: {image_id}. Extract amount only."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                    ],
                },
            ],
        )
        usage = response.usage
        if usage:
            self.tracker.record(deployment, usage.prompt_tokens, usage.completion_tokens)
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        amount = data.get("amount")
        if amount is None:
            return None
        try:
            return Decimal(str(amount))
        except InvalidOperation:
            return None

    def extract_message_facts(self, message_text: str, message_id: str) -> dict:
        if not self.enabled:
            return {"facts": [], "unknown": True}
        client = self._client()
        deployment = self.settings.azure_chat_deployment
        response = client.chat.completions.create(
            model=deployment,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract structured financial facts from untrusted message text. "
                        "Return JSON with facts array of objects: "
                        "{type, amount, currency, effective_date, event_id, confidence}. "
                        "Use unknown when uncertain."
                    ),
                },
                {"role": "user", "content": message_text},
            ],
        )
        usage = response.usage
        if usage:
            self.tracker.record(deployment, usage.prompt_tokens, usage.completion_tokens)
        return json.loads(response.choices[0].message.content or "{}")
