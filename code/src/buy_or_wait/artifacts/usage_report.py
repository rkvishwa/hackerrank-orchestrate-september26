from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from buy_or_wait.config import Settings
from buy_or_wait.domain import DecisionResult
from buy_or_wait.llm.usage import UsageTracker


def write_usage_report(results: list[DecisionResult], settings: Settings, path: Path) -> None:
    tracker = UsageTracker.instance()
    summary = tracker.summary(len(results))
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Token Usage Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Dataset directory: {settings.resolved_dataset_dir}",
        f"Retrieval mode: {settings.retrieval_mode}",
        f"LLM enabled: {settings.llm_enabled}",
        f"Requests processed: {len(results)}",
        "",
        "## Overall",
        f"- Total model calls: {summary['total_calls']}",
        f"- Input tokens: {summary['input_tokens']}",
        f"- Output tokens: {summary['output_tokens']}",
        f"- Total tokens: {summary['total_tokens']}",
        f"- Average tokens per request: {summary['avg_tokens_per_request']:.2f}",
        f"- Estimated total cost (USD): {summary['estimated_total_cost_usd']:.4f}",
        f"- Estimated cost per request (USD): {summary['estimated_cost_per_request_usd']:.6f}",
        "",
        "## Per Model",
    ]
    for model, data in summary["per_model"].items():
        lines.extend(
            [
                f"### {model}",
                f"- Calls: {data['calls']}",
                f"- Input tokens: {data['input_tokens']}",
                f"- Output tokens: {data['output_tokens']}",
                f"- Total tokens: {data['total_tokens']}",
                f"- Estimated cost (USD): {data['estimated_cost_usd']:.4f}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")
