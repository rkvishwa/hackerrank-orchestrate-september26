from __future__ import annotations

from buy_or_wait.api.routes import batch, decisions, health
from buy_or_wait.config import Settings
from fastapi import FastAPI


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title="Buy or Wait API", version="1.0.0")
    app.state.settings = settings
    app.include_router(health.router)
    app.include_router(batch.router, prefix="/v1")
    app.include_router(decisions.router, prefix="/v1")
    return app
