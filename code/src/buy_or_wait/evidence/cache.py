from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

PROMPT_VERSION = "v3-content-context-verified"


def content_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_source_hash(path: Path, event) -> str:
    context = json.dumps(asdict(event), sort_keys=True, default=str)
    return hashlib.sha256((content_hash(path) + context + PROMPT_VERSION).encode()).hexdigest()


def cache_key(dataset_hash: str, kind: str, item_id: str, source_hash: str) -> str:
    return f"{dataset_hash}_{kind}_{item_id}_{source_hash}"


class EvidenceCache:
    def __init__(self, cache_dir: Path, dataset_hash: str):
        self.cache_dir = cache_dir
        self.dataset_hash = dataset_hash
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def read(self, kind: str, item_id: str, source_hash: str) -> dict[str, Any] | None:
        key = cache_key(self.dataset_hash, kind, item_id, source_hash)
        path = self._path(key)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return None
        if (not isinstance(data, dict) or data.get("prompt_version") != PROMPT_VERSION
                or data.get("dataset_hash") != self.dataset_hash or data.get("source_hash") != source_hash):
            return None
        return data

    def write(self, kind: str, item_id: str, source_hash: str, payload: dict[str, Any]) -> None:
        key = cache_key(self.dataset_hash, kind, item_id, source_hash)
        payload = {
            **payload,
            "prompt_version": PROMPT_VERSION,
            "dataset_hash": self.dataset_hash,
            "source_hash": source_hash,
        }
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.cache_dir,
                                         suffix=".tmp", delete=False) as fh:
            json.dump(payload, fh, indent=2)
            temp_path = fh.name
        os.replace(temp_path, self._path(key))
