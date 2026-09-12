from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ModelUsage:
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def estimated_cost_usd(self) -> float:
        return (self.input_tokens * 2.5 + self.output_tokens * 10.0) / 1_000_000


class UsageTracker:
    _instance: "UsageTracker | None" = None

    def __init__(self) -> None:
        self.per_model: dict[str, ModelUsage] = {}

    @classmethod
    def instance(cls) -> "UsageTracker":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def record(self, model: str, input_tokens: int, output_tokens: int) -> None:
        usage = self.per_model.setdefault(model, ModelUsage())
        usage.calls += 1
        usage.input_tokens += input_tokens
        usage.output_tokens += output_tokens

    def summary(self, request_count: int) -> dict:
        total_calls = sum(u.calls for u in self.per_model.values())
        input_tokens = sum(u.input_tokens for u in self.per_model.values())
        output_tokens = sum(u.output_tokens for u in self.per_model.values())
        total_tokens = input_tokens + output_tokens
        per_model = {
            model: {
                "calls": usage.calls,
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "total_tokens": usage.total_tokens,
                "estimated_cost_usd": usage.estimated_cost_usd,
            }
            for model, usage in self.per_model.items()
        }
        estimated_total = sum(u.estimated_cost_usd for u in self.per_model.values())
        return {
            "total_calls": total_calls,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "avg_tokens_per_request": total_tokens / request_count if request_count else 0.0,
            "estimated_total_cost_usd": estimated_total,
            "estimated_cost_per_request_usd": estimated_total / request_count if request_count else 0.0,
            "per_model": per_model,
        }
