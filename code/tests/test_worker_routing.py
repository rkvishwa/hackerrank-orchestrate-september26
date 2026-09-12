from buy_or_wait.worker.celery_app import celery_app


def test_api_tasks_are_routed_to_a_queue_the_default_worker_consumes():
    consumed = set(celery_app.amqp.queues.consume_from)
    for task in ("decide_request_task", "run_batch_task"):
        route = celery_app.amqp.router.route({}, f"buy_or_wait.worker.tasks.{task}")
        assert route["queue"].name in consumed
