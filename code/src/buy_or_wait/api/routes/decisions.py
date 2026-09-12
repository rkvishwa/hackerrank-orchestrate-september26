from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from buy_or_wait.api.deps import require_api_key
from buy_or_wait.db.models import DecisionJob
from buy_or_wait.db.session import get_session, init_db
from buy_or_wait.engine import DecisionEngine
from buy_or_wait.ingest.loader import load_dataset
from buy_or_wait.worker.tasks import decide_request_task

router = APIRouter(tags=["decisions"])


class DecisionRequest(BaseModel):
    request_id: str
    sync: bool = False


@router.post("/decisions")
def create_decision(payload: DecisionRequest, request: Request, _: str = Depends(require_api_key)):
    settings = request.app.state.settings
    init_db(settings)
    dataset = load_dataset(settings.resolved_dataset_dir)
    if payload.request_id not in dataset.requests_by_id:
        raise HTTPException(status_code=404, detail="Unknown request_id")

    if payload.sync:
        engine = DecisionEngine(dataset, settings)
        result = engine.decide(dataset.requests_by_id[payload.request_id])
        return {
            "request_id": result.request_id,
            "amount_safe_to_pay": str(result.amount_safe_to_pay),
            "affordability_status": result.affordability_status,
            "recommended_payment_method": result.recommended_payment_method,
            "payment_plan": result.payment_plan,
            "earliest_date_for_full_payment": result.earliest_date_for_full_payment,
            "spending_changes_needed": result.spending_changes_needed,
            "decision_explanation": result.decision_explanation,
        }

    job_id = uuid.uuid4().hex
    session = get_session(settings)
    try:
        job = DecisionJob(id=job_id, request_id=payload.request_id, status="queued")
        session.add(job)
        session.commit()
    finally:
        session.close()
    decide_request_task.delay(job_id, payload.request_id)
    return {"job_id": job_id, "status": "queued"}


@router.get("/jobs/{job_id}")
def get_job(job_id: str, request: Request, _: str = Depends(require_api_key)):
    settings = request.app.state.settings
    session = get_session(settings)
    try:
        job = session.get(DecisionJob, job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        result = json.loads(job.result_json) if job.result_json else None
        return {"job_id": job.id, "status": job.status, "result": result, "error": job.error}
    finally:
        session.close()
