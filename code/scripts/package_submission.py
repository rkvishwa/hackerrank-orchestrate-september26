#!/usr/bin/env python3
"""Package only a validated, matching full-dataset artifact bundle."""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
import sys
import tempfile
import zipfile

CODE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE_ROOT / "src"))

from buy_or_wait.artifacts.bundle import sha256, source_hash, text_sha256
from buy_or_wait.config import Settings
from buy_or_wait.engine import DecisionEngine
from buy_or_wait.ingest.loader import load_dataset
from buy_or_wait.artifacts.evaluation import validate_output
from buy_or_wait.evidence.cache import PROMPT_VERSION

EXCLUDE_PARTS = {"__pycache__", ".pytest_cache", ".ruff_cache", ".venv", ".env", ".git", "build", "dist"}
REPORTS = {"usage_report.md", "evaluation_report.md", "evaluation_report.json"}


def package(repo_root: Path, output_path: Path | None = None, report_dir: Path | None = None):
    code_dir = repo_root / "code"
    if not code_dir.exists():
        code_dir = CODE_ROOT
    output_path = output_path or repo_root / "output.csv"
    report_dir = report_dir or code_dir / "evaluation"
    report = report_dir / "evaluation_report.json"
    if not report.exists() or any(not (report_dir / n).is_file() for n in REPORTS):
        raise ValueError("Generate output and all matching reports before packaging")
    metadata = json.loads(report.read_text(encoding="utf-8"))
    if not output_path.exists() or metadata["output_sha256"] != sha256(output_path):
        raise ValueError("Output hash does not match evaluation report")
    if metadata["source_sha256"] != source_hash(code_dir):
        raise ValueError("Source changed after the run; regenerate output and reports")
    if not metadata.get("full_dataset") or metadata.get("contract_errors"):
        raise ValueError("Only a successful full-dataset run can be packaged")
    for name in ("usage_report.md", "evaluation_report.md"):
        if metadata.get("report_sha256", {}).get(name) != sha256(report_dir / name):
            raise ValueError(f"Report hash does not match run metadata: {name}")
    usage_text = (report_dir / "usage_report.md").read_text(encoding="utf-8")
    if metadata["run_id"] not in usage_text or metadata["output_sha256"] not in usage_text:
        raise ValueError("Usage report belongs to a different run")
    settings = Settings()
    dataset_dir = settings.dataset_dir or repo_root / "dataset"
    dataset = load_dataset(dataset_dir)
    if metadata["dataset_sha256"] != dataset.version_hash:
        raise ValueError("Dataset changed after the run")
    sample_path = dataset_dir / "sample_requests.csv"
    if sample_path.exists() and metadata.get("sample_dataset_sha256") != text_sha256(sample_path):
        raise ValueError("Public samples changed after the audit")
    settings.dataset_dir = dataset_dir
    settings.llm_enabled = False
    settings.deterministic_mode = True
    errors = validate_output(output_path, DecisionEngine(dataset, settings))
    if errors:
        raise ValueError("Output failed replay validation: " + "; ".join(errors))
    with output_path.open(encoding="utf-8", newline="") as fh:
        row_count = len(list(csv.DictReader(fh)))
    if row_count != metadata["requests"]:
        raise ValueError("Output row count differs from run report")

    zip_path = repo_root / "code.zip"
    with tempfile.NamedTemporaryFile(dir=repo_root, suffix=".zip", delete=False) as fh:
        staged = Path(fh.name)
    try:
        with zipfile.ZipFile(staged, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(code_dir.rglob("*")):
                if not path.is_file():
                    continue
                relative = path.relative_to(code_dir)
                if any(part in EXCLUDE_PARTS or part.endswith(".egg-info") for part in relative.parts):
                    continue
                if path.suffix in {".pyc", ".tmp", ".lock"} or (path.name.startswith(".env") and path.name != ".env.example"):
                    continue
                if relative.as_posix() in {f"evaluation/{n}" for n in REPORTS}:
                    continue
                if "evidence_cache" in relative.parts and path.suffix == ".json":
                    data = json.loads(path.read_text(encoding="utf-8"))
                    if data.get("prompt_version") != PROMPT_VERSION or data.get("dataset_hash") != dataset.version_hash:
                        continue
                zf.write(path, relative.as_posix())
            for name in sorted(REPORTS):
                zf.write(report_dir / name, f"evaluation/{name}")
        os.replace(staged, zip_path)
    finally:
        staged.unlink(missing_ok=True)
    manifest = {k: metadata[k] for k in ("run_id", "output_sha256", "dataset_sha256", "source_sha256", "evidence_sha256", "requests")}
    manifest["code_zip_sha256"] = sha256(zip_path)
    manifest["reports"] = {name: sha256(report_dir / name) for name in sorted(REPORTS)}
    manifest_path = repo_root / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return zip_path, manifest_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=CODE_ROOT.parent)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report-dir", type=Path)
    args = parser.parse_args()
    for path in package(args.repo_root.resolve(), args.output, args.report_dir):
        print(f"Created {path}")
