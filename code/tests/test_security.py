from __future__ import annotations

from fastapi.testclient import TestClient

from buy_or_wait.api.app import create_app
from buy_or_wait.config import Settings


def test_missing_api_key_rejected():
    app = create_app(Settings(api_key="secret"))
    client = TestClient(app)
    response = client.post("/v1/decisions", json={"request_id": "request_26", "sync": True})
    assert response.status_code == 401
