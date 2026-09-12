from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/ready")
def ready(request: Request):
    settings = request.app.state.settings
    degraded = []
    if settings.llm_enabled and not settings.azure_openai_api_key:
        degraded.append("azure_unconfigured")
    status = "ready" if not degraded else "degraded"
    code = 200
    return {"status": status, "degraded": degraded}
