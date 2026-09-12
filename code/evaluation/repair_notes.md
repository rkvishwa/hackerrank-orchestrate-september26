# Financial repair candidate — deployment blocked

The candidate fixes four general financial behaviors: income amendments are scoped to their income stream, occurrence cancellations preserve ongoing commitments, reductions can reach the permitted minimum without silently stopping an expense, and all fluctuating expenses use the stated conservative estimator. Synthetic regression tests reproduce the original defects. An independent cumulative-balance calculation checks capacity and its first safe date.

These fixes do not establish the undocumented forecast behind the public examples. The stricter expense estimator increases some projected obligations and changes several recommendations. The accepted release gate rejects this candidate, so the running release must remain on `3ba63a8`.

| Public sample metric | Baseline | Candidate |
| --- | ---: | ---: |
| Exact safe amount | 3/25 | 3/25 |
| Status | 20/25 | 18/25 |
| Payment method | 21/25 | 19/25 |
| Payment plan | 21/25 | 20/25 |
| Earliest full-payment date | 17/25 | 15/25 |
| Spending changes | 17/25 | 17/25 |
| Mean absolute amount error / requested amount | 3.5504% | 3.4961% |

The modest amount-error improvement does not override the four regressed match counts. `test_sample_release_gate` deliberately fails on those regressions; it must not be marked xfail, skipped, or weakened. All other tests should pass. Candidate artifacts are review artifacts, not an approved replacement for the current service.

## Remaining differences

`evaluation_report.md` lists all 22 requests with differences and the limiting cash flow. `evaluation_report.json` contains every expected/predicted field, dated ledger, observed expense amounts, estimator, and independent capacity cross-check. The classifications remain `unresolved_reference_difference`; replaying an example under our own forecast is not evidence that the example itself is wrong.

In particular, the candidate loses agreement for requests 12 and 23 after reserving the upper-quartile variable expenses. Requests 7 and 17 obtain later capacity dates. Request 11's current payroll message confirms a different amount from the historical base-salary rows; the prediction follows that supplied evidence rather than substituting the example's July date. No sample answers or organizer-only records enter predictions.

## Reproduction

From the repository root:

```text
python -B -m pytest code/tests -q -p no:cacheprovider
python -B code/main.py --deterministic --emit-usage-report
python -B code/evaluation/main.py --baseline-report code/evaluation/reference_baseline.json --candidate-report code/evaluation/evaluation_report.json
python -B code/scripts/package_submission.py
```

The suite and release-check commands are expected to exit nonzero until the accuracy gate is met. A full-dataset run and contract replay can succeed while this deployment gate remains blocked.
