"""Resumable preparation, independent of prediction and public sample labels."""
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextvars import copy_context

from buy_or_wait.evidence.structured import FactExtractor
from buy_or_wait.llm.usage import UsageTracker
from buy_or_wait.evidence.cache import PROMPT_VERSION


def prepare_evidence(dataset, settings):
    extractor = FactExtractor(dataset, settings)
    records = [("message", m) for items in dataset.messages_by_user.values() for m in items]
    records += [("image", i) for i in dataset.images_by_id.values()]
    completed, failures = [], []
    inventory = UsageTracker(settings.model_prices)
    with UsageTracker.scoped(settings.model_prices) as tracker:
        with ThreadPoolExecutor(max_workers=max(1, min(settings.azure_max_concurrency, 4))) as pool:
            futures = {pool.submit(copy_context().run, getattr(extractor, kind), record): (kind, record)
                       for kind, record in records}
            for future in as_completed(futures):
                kind, record = futures[future]
                identifier = getattr(record, "message_id", getattr(record, "image_id", ""))
                try:
                    data = future.result()
                    if data is None:
                        raise ValueError("No extraction or cached evidence available")
                    completed.append({"kind": kind, "id": identifier, "user_id": record.user_id,
                        "source_hash": data["source_hash"], "rejected_facts": len(data.get("rejected", []))})
                    if data.get("usage"):
                        inventory.record(data["model"], data["usage"]["input_tokens"], data["usage"]["output_tokens"],
                                         deployment=data.get("deployment", ""))
                except Exception as exc:
                    # SDK exception details can contain endpoint/configuration values.
                    failures.append({"kind": kind, "id": identifier, "error_type": type(exc).__name__})
                print(f"Evidence {len(completed) + len(failures)}/{len(records)}: {identifier}", flush=True)
        report = {"dataset_sha256": dataset.version_hash, "completed": sorted(completed, key=lambda x: x["id"]),
                  "failures": failures, "usage": inventory.summary(len(dataset.context_requests_by_id)),
                  "run_usage": tracker.summary(len(dataset.context_requests_by_id)),
                  "accounting_note": "usage counts the original creation of each cached source once; run_usage counts calls during this invocation only"}
        destination = settings.resolved_report_dir
        destination.mkdir(parents=True, exist_ok=True)
        history = destination / "extraction_runs"
        history.mkdir(exist_ok=True)
        previous = destination / "extraction_report.json"
        if previous.exists():
            old = json.loads(previous.read_text(encoding="utf-8"))
            old_id = old.get("run_usage", old["usage"])["run_id"]
            old_path = history / f"{old_id}.json"
            if not old_path.exists():
                old_path.write_text(json.dumps(old, indent=2, sort_keys=True), encoding="utf-8")
        (history / f"{tracker.run_id}.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        (destination / "extraction_report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        if not failures:
            manifest = {"dataset_hash": dataset.version_hash, "prompt_version": PROMPT_VERSION,
                "chat_deployment": settings.azure_chat_deployment,
                "vision_deployment": settings.azure_vision_deployment or settings.azure_chat_deployment,
                "sources": completed}
            path = settings.resolved_evidence_cache_dir / "frozen_manifest.json"
            # A cache-only invocation without deployment settings preserves the
            # original model choices recorded by the preparing environment.
            if not manifest["chat_deployment"] and path.exists():
                old_manifest = json.loads(path.read_text(encoding="utf-8"))
                if old_manifest.get("dataset_hash") == dataset.version_hash:
                    manifest["chat_deployment"] = old_manifest.get("chat_deployment", "")
                    manifest["vision_deployment"] = old_manifest.get("vision_deployment", "")
            path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
        summary = report["usage"]
        (destination / "extraction_report.md").write_text(
            "# Evidence preparation\n\n" + f"Completed: {len(completed)}/{len(records)}. Failures: {len(failures)}.\n\n"
            + "This is upstream extraction usage, separate from the final deterministic prediction run.\n\n"
            + f"Calls made by this preparation invocation: {report['run_usage']['total_calls']}. Source creation usage below is retained on cache-only reruns.\n\n"
            + f"Calls: {summary['total_calls']}; input tokens: {summary['input_tokens']}; output tokens: {summary['output_tokens']}.\n"
            + f"Estimated USD: {summary['estimated_total_cost_usd']} (null means pricing is not configured).\n",
            encoding="utf-8")
    if failures:
        raise RuntimeError(f"{len(failures)} evidence extractions failed; inspect extraction_report.json and retry")
    return report
