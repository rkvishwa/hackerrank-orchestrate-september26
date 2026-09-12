from __future__ import annotations

from celery import Celery

from buy_or_wait.config import Settings

settings = Settings()
celery_app = Celery("buy_or_wait", broker=settings.celery_broker_url, backend=settings.redis_url)
celery_app.conf.update(
    task_default_queue="decisions",
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_retry_delay=5,
    task_routes={"buy_or_wait.worker.tasks.*": {"queue": "decisions"}},
)
celery_app.autodiscover_tasks(["buy_or_wait.worker"])
