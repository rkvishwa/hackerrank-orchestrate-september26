from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("API_KEY", "test-key")

from buy_or_wait.api.app import create_app  # noqa: E402


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready(client):
    response = client.get("/ready")
    assert response.status_code in {200, 503}


def test_sync_decisions_isolate_model_usage(client, monkeypatch):
    from buy_or_wait.api.routes import decisions
    from buy_or_wait.llm.usage import UsageTracker
    monkeypatch.setattr(decisions, "init_db", lambda settings: None)
    original = decisions.DecisionEngine.decide
    def measured_decision(self, request):
        UsageTracker.instance().record("test-model", 10, 5, provider="test")
        return original(self, request)
    monkeypatch.setattr(decisions.DecisionEngine, "decide", measured_decision)
    settings = client.app.state.settings
    settings.llm_enabled = False
    settings.deterministic_mode = True
    dataset = decisions.load_dataset(settings.resolved_dataset_dir)
    results = [client.post("/v1/decisions", json={"request_id": dataset.requests[0].request_id, "sync": True},
                          headers={"x-api-key": settings.api_key}) for _ in range(2)]
    assert all(r.status_code == 200 for r in results)
    first, second = [r.json()["usage"] for r in results]
    assert first["run_id"] != second["run_id"]
    assert first["total_calls"] == second["total_calls"] == 1
    assert first["total_tokens"] == second["total_tokens"] == 15
