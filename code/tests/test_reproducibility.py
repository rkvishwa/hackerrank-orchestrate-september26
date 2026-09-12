from __future__ import annotations

from pathlib import Path

from buy_or_wait.config import Settings
from buy_or_wait.engine import DecisionEngine
from buy_or_wait.ingest.loader import load_dataset
from buy_or_wait.ingest.loader import _hash_dataset
from buy_or_wait.artifacts.bundle import source_hash, text_sha256

DATASET = Path(__file__).resolve().parents[2] / "dataset"


def test_text_hashes_survive_windows_linux_checkout(tmp_path):
    windows = tmp_path / "windows"
    linux = tmp_path / "linux"
    windows.mkdir()
    linux.mkdir()
    for name in ("events.csv", "main.py", "requirements.txt", "pyproject.toml"):
        (windows / name).write_bytes(b"first\r\nsecond\r\n")
        (linux / name).write_bytes(b"first\nsecond\n")
    assert _hash_dataset([windows / "events.csv"]) == _hash_dataset([linux / "events.csv"])
    assert source_hash(windows) == source_hash(linux)
    assert text_sha256(windows / "events.csv") == text_sha256(linux / "events.csv")
    (linux / "events.csv").write_bytes(b"changed\nsecond\n")
    assert _hash_dataset([windows / "events.csv"]) != _hash_dataset([linux / "events.csv"])


def test_deterministic_decisions_reproducible():
    settings = Settings(dataset_dir=DATASET, deterministic_mode=True, llm_enabled=False)
    dataset = load_dataset(DATASET)
    engine = DecisionEngine(dataset, settings)
    first = [engine.decide(r).payment_plan for r in dataset.requests[:10]]
    second = [engine.decide(r).payment_plan for r in dataset.requests[:10]]
    assert first == second
