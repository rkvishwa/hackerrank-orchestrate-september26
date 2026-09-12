from __future__ import annotations

from contextvars import ContextVar
from contextlib import contextmanager
from dataclasses import dataclass
import uuid

_current: ContextVar["UsageTracker | None"] = ContextVar("model_usage", default=None)


@dataclass
class ModelUsage:
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    provider: str = ""
    deployment: str = ""
    price: tuple[float, float] | None = None

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def estimated_cost_usd(self) -> float | None:
        if self.price is None:
            return None
        return (self.input_tokens * self.price[0] + self.output_tokens * self.price[1]) / 1_000_000


class UsageTracker:
    def __init__(self, prices=None, run_id: str | None = None):
        self.run_id = run_id or uuid.uuid4().hex
        self.per_model: dict[str, ModelUsage] = {}
        self.prices = prices or {}
        self.cache_hits: dict[str, int] = {}
        self.evidence_hashes: set[str] = set()
        self.missing_usage_responses = 0

    @classmethod
    def instance(cls):
        tracker = _current.get()
        if tracker is None:
            tracker = cls()
            _current.set(tracker)
        return tracker

    @classmethod
    def reset(cls):
        _current.set(cls())

    @classmethod
    @contextmanager
    def scoped(cls, prices=None, run_id=None):
        tracker = cls(prices, run_id)
        token = _current.set(tracker)
        try:
            yield tracker
        finally:
            _current.reset(token)

    def record(self, model: str, input_tokens: int, output_tokens: int,
               provider: str = "Azure OpenAI", deployment: str = ""):
        if min(input_tokens, output_tokens) < 0:
            raise ValueError("Token counts cannot be negative")
        key = f"{provider}/{model}"
        usage = self.per_model.setdefault(key, ModelUsage(
            provider=provider, deployment=deployment,
            price=self.prices.get(model) or self.prices.get(deployment)))
        usage.calls += 1
        usage.input_tokens += input_tokens
        usage.output_tokens += output_tokens

    def cache_hit(self, source: str, evidence_hash: str):
        self.cache_hits[source] = self.cache_hits.get(source, 0) + 1
        self.evidence_hashes.add(evidence_hash)

    def summary(self, request_count: int):
        inputs = sum(u.input_tokens for u in self.per_model.values())
        outputs = sum(u.output_tokens for u in self.per_model.values())
        costs = [u.estimated_cost_usd for u in self.per_model.values()]
        total_cost = None if any(c is None for c in costs) or self.missing_usage_responses else sum(costs)
        return {
            "run_id": self.run_id, "request_count": request_count,
            "total_calls": sum(u.calls for u in self.per_model.values()) + self.missing_usage_responses,
            "input_tokens": inputs, "output_tokens": outputs, "total_tokens": inputs + outputs,
            "avg_tokens_per_request": (inputs + outputs) / request_count if request_count else 0,
            "estimated_total_cost_usd": total_cost,
            "estimated_cost_per_request_usd": total_cost / request_count if total_cost is not None and request_count else total_cost,
            "cache_hits": dict(self.cache_hits), "missing_usage_responses": self.missing_usage_responses,
            "per_model": {m: {
                "provider": u.provider, "deployment": u.deployment, "calls": u.calls,
                "input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
                "total_tokens": u.total_tokens, "estimated_cost_usd": u.estimated_cost_usd,
                "usd_per_million_tokens": u.price,
            } for m, u in sorted(self.per_model.items())},
        }
