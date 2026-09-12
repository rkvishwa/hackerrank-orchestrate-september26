from __future__ import annotations

import json
from dataclasses import asdict

from buy_or_wait.config import Settings
from buy_or_wait.db.models import BatchRun, DecisionJob
from buy_or_wait.db.session import get_session, init_db
from buy_or_wait.engine import DecisionEngine, run_pipeline
from buy_or_wait.ingest.loader import load_dataset
from buy_or_wait.worker.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3)
def decide_request_task(self, job_id: str, request_id: str) -> None:
    settings = Settings()
    init_db(settings)
    session = get_session(settings)
    try:
        job = session.get(DecisionJob, job_id)
        if job is None:
            return
        job.status = "running"
        session.commit()
        dataset = load_dataset(settings.resolved_dataset_dir)
        engine = DecisionEngine(dataset, settings)
        result = engine.decide(dataset.requests_by_id[request_id])
        job.result_json = json.dumps(
            {
                "request_id": result.request_id,
                "amount_safe_to_pay": str(result.amount_safe_to_pay),
                "affordability_status": result.affordability_status,
                "recommended_payment_method": result.recommended_payment_method,
                "payment_plan": result.payment_plan,
                "earliest_date_for_full_payment": result.earliest_date_for_full_payment,
                "spending_changes_needed": result.spending_changes_needed,
                "decision_explanation": result.decision_explanation,
            }
        )
        job.status = "completed"
        session.commit()
    except Exception as exc:  # noqa: BLE001
        if job:
            job.status = "failed"
            job.error = str(exc)
            session.commit()
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    finally:
        session.close()


@celery_app.task(bind=True, max_retries=3)
def run_batch_task(self, run_id: str) -> None:
    settings = Settings()
    init_db(settings)
    session = get_session(settings)
    try:
        run = session.get(BatchRun, run_id)
        if run is None:
            return
        run.status = "running"
        session.commit()
        results, output_path = run_pipeline(settings)
        run.completed = len(results)
        run.failed = 0
        run.status = "completed"
        run.artifact_path = str(output_path)
        session.commit()
    except Exception as exc:  # noqa: BLE001
        if run:
            run.status = "failed"
            session.commit()
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    finally:
        session.close()
