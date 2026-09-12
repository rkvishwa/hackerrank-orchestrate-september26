from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from buy_or_wait.config import CODE_ROOT
from buy_or_wait.artifacts.evaluation import validate_output, score_samples
from buy_or_wait.artifacts.usage_report import usage_markdown


def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha256(path: Path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def source_hash(code_root: Path = CODE_ROOT):
    paths = list(code_root.rglob("*.py")) + [code_root / "requirements.txt", code_root / "pyproject.toml"]
    digest = hashlib.sha256()
    for path in sorted(paths):
        if not path.is_file() or any(p in {".venv", "build", "dist"} for p in path.parts):
            continue
        digest.update(path.relative_to(code_root).as_posix().encode())
        digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
    return digest.hexdigest()


def evidence_hash(results):
    evidence = {r.request_id: r.trace for r in results}
    def encode(value):
        return sorted(value) if isinstance(value, set) else str(value)
    return hashlib.sha256(json.dumps(evidence, sort_keys=True, default=encode).encode()).hexdigest()


def publish(engine, results, settings, tracker, expected_ids):
    output = settings.resolved_output_path.resolve()
    report_dir = settings.resolved_report_dir.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    # One writer per report bundle; worker runs use separate directories.
    lock_path = report_dir / ".publication.lock"
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise RuntimeError(f"Artifact writer already active; inspect {lock_path} before retrying") from exc
    os.close(fd)
    try:
        with tempfile.TemporaryDirectory(prefix=".run-", dir=output.parent) as temp:
            stage = Path(temp)
            staged_output = stage / "output.csv"
            engine.write_output(results, staged_output)
            errors = validate_output(staged_output, engine, expected_ids)
            if errors:
                raise ValueError("Output validation failed: " + "; ".join(errors))
            metadata = {
                "run_id": tracker.run_id, "generated_at": datetime.now(timezone.utc).isoformat(),
                "dataset_sha256": engine.dataset.version_hash, "source_sha256": source_hash(),
                "evidence_sha256": evidence_hash(results), "output_sha256": sha256(staged_output),
                "evidence_source_hashes": sorted(tracker.evidence_hashes),
                "requests": len(results), "full_dataset": set(expected_ids) == set(engine.dataset.requests_by_id),
                "contract_errors": [], "hidden_dataset_accuracy": "unknown",
                "forecast_policy": "90 days; confirmed credits available on settlement date before outgoing payments; independent commitments; variable spending upper quartile of latest 12 observed payments; no speculative credits",
                "usage": tracker.summary(len(results)),
            }
            audit_settings = settings.model_copy(update={"deterministic_mode": True, "llm_enabled": False})
            metadata["samples"] = score_samples(settings.resolved_dataset_dir, audit_settings)
            metadata["text_hash_policy"] = "Dataset, source and sample text use LF-normalized bytes; artifacts and images use exact bytes."
            metadata["sample_dataset_sha256"] = text_sha256(settings.resolved_dataset_dir / "sample_requests.csv") if (settings.resolved_dataset_dir / "sample_requests.csv").exists() else None
            markdown = ["# Evaluation Report", "", f"Run ID: {tracker.run_id}",
                        f"Output SHA-256: {metadata['output_sha256']}",
                        f"Requests: {len(results)}", "Contract violations: 0",
                        "Hidden-dataset accuracy: unknown", "", "## Public sample matches"]
            samples = metadata["samples"]
            for field, count in samples.get("matches", {}).items():
                markdown.append(f"- {field}: {count}/{samples['request_count']} ({samples['accuracy'][field]:.1%})")
            markdown.extend(["", "Detailed field differences and the supporting cash-flow forecasts are in evaluation_report.json.",
                "Sample agreement is measured separately from financial contract validation; passing validation does not prove hidden-label accuracy.",
                "", "## Forecast policy", metadata["forecast_policy"]])
            documents = {
                "usage_report.md": usage_markdown(metadata["usage"], metadata),
                "evaluation_report.md": "\n".join(markdown) + "\n",
            }
            metadata["report_sha256"] = {name: hashlib.sha256(body.encode()).hexdigest()
                                          for name, body in documents.items()}
            documents["evaluation_report.json"] = json.dumps(metadata, indent=2, sort_keys=True)
            # Prepare files on each destination filesystem, replace manifest last.
            pending = []
            for name, body in documents.items():
                target = report_dir / name
                with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                                  dir=report_dir, suffix=".tmp", delete=False) as fh:
                    fh.write(body)
                    pending.append((Path(fh.name), target))
                # NamedTemporaryFile defaults to 0600; published reports must
                # also be readable by the host account on a Docker bind mount.
                os.chmod(fh.name, 0o644)
            pending.insert(0, (staged_output, output))
            old = {target: target.read_bytes() if target.exists() else None for _, target in pending}
            changed = []
            try:
                for src, target in pending:
                    os.replace(src, target)
                    changed.append(target)
            except BaseException:
                for target in reversed(changed):
                    if old[target] is None:
                        target.unlink(missing_ok=True)
                    else:
                        target.write_bytes(old[target])
                raise
            finally:
                for src, _ in pending:
                    src.unlink(missing_ok=True)
    finally:
        lock_path.unlink(missing_ok=True)
    return output
