#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src"
python -m pytest tests -q
python main.py --deterministic --emit-usage-report
python evaluation/main.py --output ../output.csv --dataset-dir ../dataset
