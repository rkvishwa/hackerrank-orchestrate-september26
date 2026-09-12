# Buy or Wait

Python 3.11+ financial decision engine. It reads only participant data, constructs a 90-day forecast, checks eligible payment plans, and publishes a CSV with matching usage and evaluation reports.

## Local or VM terminal run

Run from the repository root in PowerShell or a Linux shell:

```text
python -m pip install -r code/requirements.txt
python code/main.py --dataset-dir dataset --output output.csv --report-dir code/evaluation --evidence-cache-dir code/evaluation/evidence_cache --deterministic
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

Independent subscriptions and bills retain separate series. Routine grocery, transport and dining merchants can share a series. Documentary invoices, airline tickets and wallet transactions retain distinct identities. Repeated descriptions establish the routine cadence; a new description must fit that cadence and not be an exceptional basket. Regularity requires multiple distinct dates and consistent intervals. Variable outgoings use the upper quartile of the latest 12 observed cycles. Irregular recurring income uses a lower observed amount; missed pay cycles, final payroll and termination evidence prevent unsupported continuation. These are explicit forecasting assumptions, not hidden-label rules.

Dates have no intraday timestamps. Confirmed credits are available on their settlement date before outgoing payments on that date. Every subsequent expense and plan payment must retain the minimum balance. Forecasts cover 90 calendar dates ending on request date + 89 days; all recommended payments must also meet the requested deadline.

Image extraction requires the actual PNG. The included reviewed transcriptions were visually checked against the supplied images, contain only financial fields, and are bound to the complete dataset hash, image bytes, event context and extraction version. They are evidence caches, not request predictions. A changed document or event invalidates the cache. In deterministic mode, unresolved mandatory amounts fail the run without overwriting the prior output. Development transcription tokens are unavailable and are not counted as final-run provider usage.

Public samples are scored separately, with numeric and structural comparisons. The JSON report includes every field mismatch and its forecast for investigation. Zero contract violations does not establish hidden-dataset accuracy; that accuracy is unknown.

Payroll amendments target the linked or uniquely identified income stream. Ambiguous amendments cannot increase income or restart it, and cancellation of one payment does not cancel the ongoing commitment. Only explicit subscription/commitment cancellation suppresses future charges from its effective date. Reductions use the permitted minimum; when no positive floor is stated, a one-cent budget preserves the distinction from stopping.

Every varying expense series uses the upper quartile of its latest 12 observations, including small variations in utilities, healthcare and shopping. An independent cumulative-balance check validates baseline capacity and its first safe date without calling the payment simulator. This checks arithmetic on the estimated ledger, not the hidden reference forecast.

## Release gate

The frozen `evaluation/reference_baseline.json` records the sample metrics from commit `3ba63a8`. Prediction code never reads it. Run the release check after producing a candidate full-dataset report:

```text
python code/evaluation/main.py --baseline-report code/evaluation/reference_baseline.json --candidate-report artifacts/candidate/evaluation/evaluation_report.json
```

The command exits nonzero if any of the six sample match counts falls, the dataset differs, contract validation fails, or there is no improvement in match counts or normalized amount error. The sample regression test enforces the same accuracy expectations. A failed gate means the candidate must not replace the running service, even when its financial invariant tests pass. Candidate artifacts are for review until that gate passes.

## Optional Azure extraction

PowerShell: `Copy-Item code/.env.example code/.env`

Linux: `cp code/.env.example code/.env`

Set Azure credentials through environment variables or the ignored `code/.env`, then omit `--deterministic`. Process environment values override that file. Do not package credentials.

`AZURE_CHAT_DEPLOYMENT` and `AZURE_VISION_DEPLOYMENT` select existing deployments. Actual response model names and deployments are recorded. Configure `MODEL_PRICES` as a JSON mapping of model name (or deployment fallback) to USD per million input/output tokens, using your provider's applicable rates. Missing pricing is reported as unknown. Cached extraction is not counted as a provider call, and public-sample audit usage is isolated from the output-producing run.

## Tests

When `code/.env` contains Docker paths, set explicit local paths before tests in PowerShell:

```powershell
$env:DATASET_DIR = (Resolve-Path dataset).Path
$env:EVIDENCE_CACHE_DIR = (Resolve-Path code/evaluation/evidence_cache).Path
```

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

The forecast covers 90 calendar dates including the request date, ending 89 days later. Salary resumption and revised payday messages affect supported payroll series. Income association is shared by evidence targeting, recurrence and occurrence replacement. Lifecycle links and named employers take precedence over generic descriptions; equal amounts alone do not identify an employer. An unnamed confirmation is counted once. When several employments remain possible, overlapping projected occurrences are excluded conservatively and independently identified income is retained. Such ambiguity cannot establish new recurrence or amend multiple employers. An issued rent balance from image evidence is not increased again by a general lease amendment. Pending platform earnings are excluded when the provider says they are unconfirmed or unavailable.

The public audit retains exact comparisons across all six fields. Each mismatch includes the complete balance ledger, the cash flow that limits payment capacity, historical ranges behind recurring estimates, and replay of the sample's proposed safe amount. A supplementary mean absolute error divided by requested amount helps measure error size across currencies; it is not the official score. Future variable expenses require assumptions, and the examples do not provide their internal forecasts, so residual discrepancies remain explicitly unresolved.

## Prepare evidence once, then test locally

```text
python code/main.py --dataset-dir dataset --report-dir code/evaluation --evidence-cache-dir code/evaluation/evidence_cache --prepare-evidence
python code/main.py --dataset-dir dataset --output output.csv --report-dir code/evaluation --evidence-cache-dir code/evaluation/evidence_cache --deterministic
python code/scripts/package_submission.py --dataset-dir dataset --evidence-cache-dir code/evaluation/evidence_cache
```

Preparation uses the configured Azure model, at most four concurrent requests, bounded retries, and source-bound caches. Every message is considered, including unlinked messages. Image extraction preserves totals, payment state and date-dependent amounts. Strict schema responses still undergo quotation, number, date and ownership validation. Model responses never select affordability or calculate balances. Extraction usage is reported separately from the output-producing cached replay.

The current dataset has one request for each of 275 distinct users. Every case is independent. Historical settled transactions are already represented in the opening balance and are not subtracted again. A `linked_event_id` alone does not erase a real debit, credit or repayment.

Each run writes `evaluation/traces/<request_id>.json` for 250 evaluation requests and 25 samples. Traces include original/effective history, evidence interpretations and rejections, recurring membership, baseline and selected-plan ledgers, offer eligibility, candidate ranking and unresolved commitments. The report hashes every trace; packaging checks these hashes.

A supplied pending/scheduled event with no recoverable amount remains an error. A message announcing an additional mandatory commitment without enough details produces a conservative `not_recommended` result with zero certified capacity and an explicit uncertainty explanation. Such cases block the release gate; zero means no positive payment was certified, not that the unknown liability was assumed to cost zero. Missing reference calculations and missing input facts are reported separately from demonstrated code defects.

## Independent forecast diagnostics

```text
python -B code/scripts/diagnose_forecasts.py --dataset-dir dataset --report-dir code/evaluation --evidence-cache-dir code/evaluation/evidence_cache
```

This command makes no API calls. It reconstructs three reviewed cases directly from the CSV records using the membership and schedules in `evaluation/reviewed_cases.json`. It calculates amounts from historical observations and replays all 90 days without importing the production recurrence, evidence or capacity implementation. Every historical record must belong to a reviewed series or have an explicit exclusion. Public answers enter only the subsequent comparison. These reviewed cases are evaluation fixtures; prediction never reads their specifications.

The same command tests recurrence across two historical 30-day windows for each user, training only on earlier settled records. It reports date/category/currency precision and recall separately from error on matched amounts. Future messages, images, salary confirmations and sample answers cannot influence this backtest. The dataset supplies final transaction states, so this validates patterns in settled history rather than reconstructing historical bank snapshots.

A complete regular spending pattern takes precedence over the frequency of repeated merchant names. Alternating a favourite restaurant with other merchants must not halve the frequency of dining expenses. The exceptional-basket filter and latest-12 upper-quartile estimator still apply. Current measured results and unresolved assumptions are in `evaluation/forecast_diagnostics.md`; the original release gate remains authoritative.

## Cumulative expense experiment

```text
python -B code/scripts/experiment_expenses.py --dataset-dir dataset --report-dir code/evaluation/expense_experiment --evidence-cache-dir code/evaluation/evidence_cache
```

This evaluation command compares the default estimator with a fixed calendar-window alternative. It evaluates cumulative cash flows and drawdowns over 30, 60 and 90 days, reserves validation users, keeps public sample users outside model selection, and includes unmatched observed transactions. Missing amounts or unavailable dated FX make a fold unscorable. Historical balances are not invented. Both models also run all 250 evaluation requests with frozen evidence and no model calls.

The alternative is experimental and does not change the normal CLI or API forecast. It reduced average errors but increased historical underprediction, so the promotion gate rejected it. Its output is explicitly named `experimental_output.csv` inside the experiment report directory. See `evaluation/expense_experiment/README.md` for results and the distinction between experimental and submission outputs.

## Defect comparison and candidate artifacts

The cancellation and employer-association corrections, per-fix results, and remaining differences are documented in `evaluation/defect_iteration/README.md`. Amendments are applied before cash-state filtering. A cancelled internal occurrence can explain a cadence gap only between at least two paid observations; its amount, flexibility and date cannot become the paid anchor. Traces separately record cancellation calendar evidence, income associations and explicit cash inclusion/exclusion reasons. Accounting checks reject duplicate recurring membership and missing or duplicated explicit obligations.

The comparison adapter requires separately obtained, reviewed PR #8 source at commit `7c4cc0aa4698be2c558619b577e902bc5f326176`. It verifies file hashes and runs the external functions in a temporary offline worker without credentials or sample answers. External source is not included in this package and is never imported by prediction code.

```text
python -B code/scripts/compare_pr8.py --pr-source <reviewed-pr8-code-directory> --dataset-dir dataset --report-dir code/evaluation/defect_iteration --evidence-cache-dir code/evaluation/evidence_cache
python -B code/scripts/validate_defects.py --control artifacts/defect-control-20260912T230232Z --candidate artifacts/defect-candidate-20260912 --report-dir code/evaluation/defect_iteration
```

Keep candidate artifacts separate until all release gates pass. The current defect iteration did not improve sample scores and must not replace the control submission or remote deployment. Its full run, package and 275 request traces live under `artifacts/defect-candidate-20260912/` in the development checkout. Frozen controls and external comparison source are development inputs and are not required for a normal packaged run.
