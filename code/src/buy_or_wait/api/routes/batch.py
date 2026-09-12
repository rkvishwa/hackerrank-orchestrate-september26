from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse

from buy_or_wait.api.deps import require_api_key
from buy_or_wait.config import Settings
from buy_or_wait.db.models import BatchRun
from buy_or_wait.db.session import get_session, init_db
from buy_or_wait.worker.tasks import run_batch_task

router = APIRouter(tags=["batch"])


@router.post("/runs")
def create_run(request: Request, _: str = Depends(require_api_key)):
    settings: Settings = request.app.state.settings
    init_db(settings)
    run_id = uuid.uuid4().hex
    session = get_session(settings)
    try:
        from buy_or_wait.ingest.loader import load_dataset

        dataset = load_dataset(settings.resolved_dataset_dir)
        run = BatchRun(
            id=run_id,
            dataset_hash=dataset.version_hash,
            status="queued",
            total=len(dataset.requests),
        )
        session.add(run)
        session.commit()
    finally:
        session.close()
    run_batch_task.delay(run_id)
    return {"run_id": run_id, "status": "queued"}


@router.get("/runs/{run_id}")
def get_run(run_id: str, request: Request, _: str = Depends(require_api_key)):
    settings: Settings = request.app.state.settings
    session = get_session(settings)
    try:
        run = session.get(BatchRun, run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="Run not found")
        return {
            "run_id": run.id,
            "status": run.status,
            "total": run.total,
            "completed": run.completed,
            "failed": run.failed,
            "artifact_path": run.artifact_path,
        }
    finally:
        session.close()


@router.get("/runs/{run_id}/output")
def download_output(run_id: str, request: Request, _: str = Depends(require_api_key)):
    settings: Settings = request.app.state.settings
    session = get_session(settings)
    try:
        run = session.get(BatchRun, run_id)
        if run is None or not run.artifact_path:
            raise HTTPException(status_code=404, detail="Output not ready")
        path = Path(run.artifact_path)
        if not path.exists():
            raise HTTPException(status_code=404, detail="Artifact missing")
        return FileResponse(path, filename="output.csv")
    finally:
        session.close()
