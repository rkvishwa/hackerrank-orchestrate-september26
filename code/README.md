# Buy or Wait

Python 3.11+ financial decision engine. It reads only participant data, constructs a 90-day forecast, checks eligible payment plans, and publishes a CSV with matching usage and evaluation reports.

## Local or VM terminal run

Run from the repository root in PowerShell or a Linux shell:

```text
python -m pip install -r code/requirements.txt
python code/main.py --deterministic --emit-usage-report
python code/evaluation/main.py --output output.csv --dataset-dir dataset
python code/evaluation/main.py --score-samples --dataset-dir dataset
python code/scripts/package_submission.py
```

Outputs are root `output.csv`, `code/evaluation/usage_report.md`, `code/evaluation/evaluation_report.md`, and `code/evaluation/evaluation_report.json`. Reports are always generated together; the existing `--emit-usage-report` flag remains accepted. Packaging creates `code.zip` and `run_manifest.json` only after checking source, dataset and output hashes and replaying the CSV. A changed source or dataset requires a new run before packaging.

For explicit locations (recommended on a VM):

```text
python code/main.py --dataset-dir dataset --output artifacts/output.csv --report-dir artifacts/evaluation --deterministic --emit-usage-report
python code/evaluation/main.py --dataset-dir dataset --output artifacts/output.csv
python code/scripts/package_submission.py --output artifacts/output.csv --report-dir artifacts/evaluation
```

Relative arguments resolve from the working directory. Defaults resolve from the code location. The code directory may also be extracted from the ZIP; invoke `python main.py` with explicit dataset, output and report paths in that layout.

## Evidence and financial assumptions

Messages and images are untrusted financial evidence. The engine ignores future messages, scopes facts to their linked user/event, reserves pending debits, excludes speculative unsettled credits and non-cash investments, and applies explicit amendments before forecasting.

Independent subscriptions and bills retain separate series. Rotating grocery, transport and dining merchants are aggregated within their category. Regularity requires multiple distinct dates and consistent intervals. Variable outgoings use the upper quartile of the latest 12 observations. Irregular recurring income uses a lower observed amount; missed pay cycles, final payroll and termination evidence prevent unsupported continuation. These are explicit forecasting assumptions, not hidden-label rules.

Dates have no intraday timestamps. Confirmed credits are available on their settlement date before outgoing payments on that date. Every subsequent expense and plan payment must retain the minimum balance. Forecasts end 90 days after the request; all recommended payments must also meet the requested deadline.

Image extraction requires the actual PNG. The included reviewed transcriptions were visually checked against the supplied images, contain only financial fields, and are bound to the complete dataset hash, image bytes, event context and extraction version. They are evidence caches, not request predictions. A changed document or event invalidates the cache. In deterministic mode, unresolved mandatory amounts fail the run without overwriting the prior output. Development transcription tokens are unavailable and are not counted as final-run provider usage.

Public samples are scored separately, with numeric and structural comparisons. The JSON report includes every field mismatch and its forecast for investigation. Zero contract violations does not establish hidden-dataset accuracy; that accuracy is unknown.

## Optional Azure extraction

PowerShell: `Copy-Item code/.env.example code/.env`

Linux: `cp code/.env.example code/.env`

Set Azure credentials through environment variables or the ignored `code/.env`, then omit `--deterministic`. Process environment values override that file. Do not package credentials.

`AZURE_CHAT_DEPLOYMENT` and `AZURE_VISION_DEPLOYMENT` select existing deployments. Actual response model names and deployments are recorded. Configure `MODEL_PRICES` as a JSON mapping of model name (or deployment fallback) to USD per million input/output tokens, using your provider's applicable rates. Missing pricing is reported as unknown. Cached extraction is not counted as a provider call, and public-sample audit usage is isolated from the output-producing run.

## Tests

```text
python -B -m pytest code/tests -q -p no:cacheprovider
```

Tests cover financial invariants, image invalidation, exported-plan replay, run accounting, failed-publication preservation, and public sample regression. The full batch test uses a temporary output/report directory.

## Docker on Linux

From `code/`:

```sh
cp .env.example .env
docker compose up -d --build
docker compose exec -T api python main.py --deterministic --emit-usage-report
```

Dataset mount: `../dataset:/dataset:ro`. Persistent artifact directory: `../artifacts:/output`. The initialization service gives the container user write access to that artifact directory. Evidence caches inside the image include the reviewed transcriptions; new extraction caches remain in the container and should be exported if needed for reuse.

CLI output appears in host `artifacts/output.csv` and `artifacts/evaluation/`. API batch jobs use `artifacts/runs/<run_id>/`, so concurrent jobs cannot overwrite each other. Deploy readiness is checked inside the API container; port 8000 need not be exposed on the host.

Existing endpoints remain unchanged: `/health`, `/ready`, and authenticated `/v1/runs`, `/v1/runs/{run_id}`, `/v1/runs/{run_id}/output`, `/v1/decisions`, `/v1/jobs/{job_id}`.

## Submission contents

Package includes runnable source, tests, prompts/configuration, reviewed evidence caches and the required `evaluation/usage_report.md`, alongside evaluation reports. Supply the matching external `output.csv` and your development chat transcript separately. `log.txt` is append-only, ignored by Git, and excluded from the ZIP.

If a run is interrupted during publication, packaging detects a mismatched bundle. A leftover `.publication.lock` must only be removed after confirming that no writer is running; then rerun the command.

Dataset, source and public-sample text hashes normalize CRLF to LF so identical Git checkouts work on Windows and Linux. Image and generated artifact hashes always cover exact bytes.

The forecast covers 90 calendar dates including the request date, ending 89 days later. Salary resumption and revised payday messages affect supported payroll series. Generic next-salary confirmations replace one matching payroll occurrence and do not create an additional employer; a lone confirmed future payment without supporting history is counted once. An issued rent balance from image evidence is not increased again by a general lease amendment. Pending platform earnings are excluded when the provider says they are unconfirmed or unavailable.

The public audit retains exact comparisons across all six fields. Each mismatch includes the complete balance ledger, the cash flow that limits payment capacity, historical ranges behind recurring estimates, and replay of the sample's proposed safe amount. A supplementary mean absolute error divided by requested amount helps measure error size across currencies; it is not the official score. Future variable expenses require assumptions, and the examples do not provide their internal forecasts, so residual discrepancies remain explicitly unresolved.
