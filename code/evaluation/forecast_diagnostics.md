# Independent forecast investigation

Latest work: [Cumulative expense experiment](expense_experiment/README.md). The results below record the preceding recurrence investigation.

The local recurrence correction improves historical date coverage and sample amount error, but does not pass the release gate. No remote changes were made.

## Changes and their evidence

The recurrence detector used repeated merchant names to establish a spending schedule. If a favourite takeaway appeared every other fortnight, the detector could discard the intervening purchases at other merchants and project dining monthly. A complete regular sequence now takes precedence over merchant repetition. Exceptional baskets still remain excluded, and variable amounts still use the latest-12 upper quartile.

The historical example for user_217 contains purchases every 14 days from September 12 through January 2. At the January 5 cutoff, the old detector retained four observations and incorrectly projected January 19. The correction projects January 16 and January 30; both appear in the held-out records. The regression uses synthetic alternating merchants and does not depend on public answers.

A separate output bug created a missing-commitment explanation in a local variable after the result object had been built. The explanation now reaches the CSV row. An end-to-end test checks the missing source ID, zero certified capacity and the explicit explanation.

## Independent reconstruction

The three reviewed cases use original CSV records, manually reviewed membership/cadence rules, independently calculated expense quantiles and a daily ledger. They do not call the production evidence interpreter, recurrence detector, currency converter, simulator or capacity checker. Public labels are consulted only afterward. Reviewed message text is hash-bound, and unreviewed historical records cause an error.

All projected date/category amounts agree with production for these three cases. This narrows the disagreement to financial assumptions; it does not establish the reference forecast.

| Case | Independently calculated capacity | Public amount | Finding |
| --- | ---: | ---: | --- |
| request_13 | EUR 433.54 | EUR 433.40 | Minimum occurs May 14. Paying EUR 941.60 on May 15 leaves EUR 1,001.23 on June 4, below the EUR 1,300 reserve by EUR 298.77 under these expense estimates. A near-identical current capacity does not establish the same future payment date. |
| request_04 | IDR 10,011,485.01 | IDR 8,401,800 | Both forecasts permit full payment June 15. The reviewed ledger includes the IDR 1,704,300 school fee, regular payroll and recurring expenses. The historical bonus is already in opening balance; an unapproved future bonus is excluded. The IDR 1,609,685.81 capacity difference remains unresolved. |
| request_25 | IDR 0 certified | IDR 1,425,000 | All three USD 1,800 salary payments are present and use dated IDR rates. The limitation occurs before payday: IDR 8,683,950 opening headroom minus IDR 8,838,420.38 expenses leaves a IDR 154,470.38 shortfall on March 14. Salary continuation is not the cause. |

Second household income in request_13 was paid October–January, with no February payment or confirmed resumption before the March request. It is not silently projected. These cases contain no images; additional image extraction would not resolve their differences.

See [reviewed rules](reviewed_cases.json) and [independent ledgers](independent_cases.json) for every observation, exclusion, estimated amount, transaction and daily balance.

## Historical validation

Two disjoint 30-day windows per user produce 550 folds across all 275 users. Training includes only earlier settled observations; future messages, images, salary confirmations and public answers are excluded. The transaction statuses are final snapshot values, so this is a recurrence backtest, not historical decision validation. Unpredicted one-off transactions count as misses; unknown image amounts are not assumed zero.

| Metric | Before this correction | After |
| --- | ---: | ---: |
| Observed date/category/currency buckets | 8,860 | 8,860 |
| Correctly predicted buckets | 8,432 | 8,598 |
| Timing precision | 99.6808% | 99.6985% |
| Timing recall | 95.1693% | 97.0429% |
| Mean relative amount error on matched known buckets | 12.3065% | 12.4703% |

The added 166 correct dates improve coverage. Matched-amount error did not improve, and the matched population changed, so this result is not evidence for replacing the expense estimator. Future debit estimates cover 6,288 of 8,129 matched observed debit buckets (77.35%); that coverage is descriptive, not a guarantee of safety.

## Public samples and release status

| Field | Original 3ba63a8 | Before this iteration | After |
| --- | ---: | ---: | ---: |
| Safe amount | 3/25 | 3/25 | 3/25 |
| Status | 20/25 | 18/25 | 18/25 |
| Method | 21/25 | 19/25 | 19/25 |
| Plan | 21/25 | 20/25 | 20/25 |
| Earliest date | 17/25 | 16/25 | 15/25 |
| Spending changes | 17/25 | 18/25 | 17/25 |
| Mean absolute amount error / request | 3.5504% | 4.5236% | 4.4293% |

request_07 now includes previously omitted routine spending: capacity moves from 91,886.57 to 84,037.03 (reference 87,170.56), and the earliest date moves from October 23 to November 23. It loses the date and spending-field matches. request_18 improves from 557.83 to 507.26 against reference 462.00. All other sample structured outputs remain unchanged in this iteration.

The full suite has 101 passing tests and one failing, unchanged sample release-gate test. All 250 evaluation rows pass contract validation. Eight missing mandatory commitments still block release. Extraction was reused; this iteration makes zero model calls. Existing source extraction usage remains separately reported in usage_report.md.

The candidate remains local and is not release-approved. The next justified investigation is the expense projection policy and its treatment of routine cycles, using historical validation and explicit requirement support. The current upper-quartile rule has not been changed merely to match answers. Every remaining sample disagreement is recorded in [sample_differences.md](sample_differences.md).
