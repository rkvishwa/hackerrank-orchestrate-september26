from __future__ import annotations

from buy_or_wait.llm.usage import UsageTracker


def test_usage_tracker_summary():
    tracker = UsageTracker.instance()
    tracker.record("gpt-4o", 100, 50)
    summary = tracker.summary(10)
    assert summary["total_calls"] >= 1
    assert summary["total_tokens"] >= 150
