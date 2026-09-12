FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY pyproject.toml .
COPY README.md .
COPY src ./src
COPY main.py .
COPY evaluation ./evaluation
COPY scripts ./scripts

RUN pip install -e .

RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser

ENV PYTHONPATH=/app/src \
    DATASET_DIR=/dataset \
    OUTPUT_PATH=/output/output.csv \
    REPORT_DIR=/output/evaluation

CMD ["python", "main.py", "--deterministic", "--emit-usage-report"]
