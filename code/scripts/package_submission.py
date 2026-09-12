#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def package(repo_root: Path) -> tuple[Path, Path]:
    code_dir = repo_root / "code"
    zip_path = repo_root / "code.zip"
    manifest_path = repo_root / "run_manifest.json"

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in code_dir.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and path.name != ".env":
                arcname = path.relative_to(code_dir).as_posix()
                zf.write(path, arcname)

    output_path = repo_root / "output.csv"
    output_checksum = ""
    if output_path.exists():
        output_checksum = hashlib.sha256(output_path.read_bytes()).hexdigest()

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "output_checksum": output_checksum,
        "code_zip": str(zip_path),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return zip_path, manifest_path


if __name__ == "__main__":
    repo = Path(__file__).resolve().parents[2]
    zpath, mpath = package(repo)
    print(f"Created {zpath}")
    print(f"Created {mpath}")
