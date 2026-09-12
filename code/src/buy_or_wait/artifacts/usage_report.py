from __future__ import annotations

import json
from pathlib import Path
from buy_or_wait.llm.usage import UsageTracker


def usage_markdown(summary, metadata):
    cost = summary["estimated_total_cost_usd"]
    per_cost = summary["estimated_cost_per_request_usd"]
    lines = ["# Token Usage Report", "",
             f"Run ID: {metadata['run_id']}",
             f"Output SHA-256: {metadata.get('output_sha256', 'not supplied')}",
             f"Requests processed: {summary['request_count']}", "",
             "## Overall",
             f"- Total model calls: {summary['total_calls']}",
             f"- Input tokens: {summary['input_tokens']}",
             f"- Output tokens: {summary['output_tokens']}",
             f"- Total tokens: {summary['total_tokens']}",
             f"- Average tokens per request: {summary['avg_tokens_per_request']:.4f}",
             f"- Estimated total cost (USD): {cost if cost is not None else 'unknown (missing model pricing or usage)'}",
             f"- Estimated cost per request (USD): {per_cost if per_cost is not None else 'unknown'}",
             f"- Responses without usage metadata: {summary['missing_usage_responses']}",
             f"- Cache hits by evidence source: {json.dumps(summary['cache_hits'], sort_keys=True)}", "",
             "## Per Model"]
    if not summary["per_model"]:
        lines.append("No provider calls occurred during this run. Rules and validated cached evidence were used.")
    for model, data in summary["per_model"].items():
        lines.extend([f"### {model}", f"- Provider: {data['provider']}",
                      f"- Deployment: {data['deployment']}", f"- Calls: {data['calls']}",
                      f"- Input tokens: {data['input_tokens']}", f"- Output tokens: {data['output_tokens']}",
                      f"- Total tokens: {data['total_tokens']}",
                      f"- Estimated cost (USD): {data['estimated_cost_usd'] if data['estimated_cost_usd'] is not None else 'unknown'}",
                      f"- USD per million input/output tokens: {data['usd_per_million_tokens']}", ""])
    lines.extend(["", "Only this output-producing run is counted. Public-sample audits use separate accounting.",
                  "Reviewed image transcriptions were produced during development. Their development token usage is unavailable and is not reported as final-run model usage.",
                  "A cache hit is not a model call. Missing prices are never assumed to be zero."])
    return "\n".join(lines) + "\n"


def write_usage_report(results, settings, path: Path):
    tracker = UsageTracker.instance()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(usage_markdown(tracker.summary(len(results)), {"run_id": tracker.run_id}), encoding="utf-8")
