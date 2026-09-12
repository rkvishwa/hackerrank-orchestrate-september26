# Buy or Wait — Solution Package

## Requirements

- Python 3.11+
- Optional: Docker Engine + Compose plugin for production deployment

## Quick Start (Submission Path)

From the repository root:

```bash
pip install -r code/requirements.txt
python code/main.py --deterministic --emit-usage-report
```

This reads `dataset/`, writes root-level `output.csv`, and generates `code/evaluation/usage_report.md`.

## Environment Variables

Copy `code/.env.example` to `code/.env` for Azure OpenAI and API deployment settings.

Key variables:

- `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`
- `AZURE_CHAT_DEPLOYMENT`, `AZURE_VISION_DEPLOYMENT`
- `LLM_ENABLED`, `DETERMINISTIC_MODE`, `RETRIEVAL_MODE`
- `DATABASE_URL`, `REDIS_URL`, `CELERY_BROKER_URL`, `API_KEY`

When Azure is unavailable, run with `--deterministic` to use cached/deterministic fallbacks and still emit all 250 rows.

## Evaluation

```bash
python code/evaluation/main.py --output output.csv --dataset-dir dataset
python code/evaluation/main.py --score-samples --dataset-dir dataset
```

## Tests

```bash
cd code
export PYTHONPATH=src
pytest tests -q
bash scripts/test_all.sh
```

## Docker Deployment

```bash
cd code
cp .env.example .env
docker compose up -d --build
```

Production one-command deploy on Ubuntu VM:

```bash
REPO_URL=https://github.com/your-org/hackerrank-orchestrate-september26.git bash code/scripts/deploy.sh install
```

Domain: `https://financeagent.knurdz.org`

## API

- `GET /health`
- `GET /ready`
- `POST /v1/runs`
- `GET /v1/runs/{run_id}`
- `GET /v1/runs/{run_id}/output`
- `POST /v1/decisions`
- `GET /v1/jobs/{job_id}`

All `/v1/*` routes require `X-API-Key`.

## Submission Artifacts

```bash
python code/scripts/package_submission.py
```

Produces:

- `code.zip`
- `run_manifest.json`
- root `output.csv`
- `code/evaluation/usage_report.md`
- `log.txt` as chat transcript
