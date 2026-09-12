# Cumulative expense experiment — alternative rejected

This experiment completed the planned attribution review and 30-, 60- and 90-day historical validation. The calendar-window alternative improved average errors and some public sample fields, but increased historical underprediction risk. It was not promoted. The default output remains the occurrence-based upper-quartile model, with 3/25 exact safe amounts and 4.4293% normalized amount error. The remote service was not changed.

## Frozen alternative

For groceries, transport and dining only, calculate the average amount per occurrence in each of three complete 30-day historical windows, then take their nearest-rank upper quartile and round upward to a cent. Every window must contain at least two observations and every date expected from the supported cadence. Sparse, incomplete and constant series retain the control estimate. Explicit bills and credits retain their supplied amounts and dates.

The alternative, user partition and promotion rules are saved in [specification.json](specification.json) before outcomes are evaluated. No coefficients were selected using public answers. Public sample users form a separate audit group. Evaluation users are split deterministically by user ID into development and reserved validation groups; a user's records never cross those groups.

## Full-horizon historical results

There are 825 folds: one 30-, 60- and 90-day window for each of 275 users. Of these, 789 have complete amounts and dated FX for both models. Thirty-six folds are explicitly unscorable; missing amounts are not substituted with zero in reported metrics. The windows overlap, so they are not independent trials.

All settled cash outflows, including unmatched one-offs, enter the error calculation. Credits and debits are replayed from a relative balance of zero. This measures cumulative cash-flow and drawdown error without inventing historical bank balances. Final snapshot transaction states and absent historical messages limit the backtest; these are not observed bank-overdraft counts.

| Reserved validation horizon | Control mean absolute outflow error | Alternative | Control underpredicted total outflows | Alternative |
| --- | ---: | ---: | ---: | ---: |
| 30 days | 5.0924% | 3.8705% | 5/78 | 9/78 |
| 60 days | 4.8809% | 3.8510% | 5/78 | 10/78 |
| 90 days | 5.1061% | 3.9790% | 3/78 | 7/78 |

At 90 days, the mean largest cumulative outflow underestimate rises from 0.1854% to 0.2781% of actual total outflows. Development data shows the same tradeoff. The alternative fails the predeclared requirement that amount improvement must not worsen total/prefix underprediction or cash-flow overstatement. Lower average error alone is insufficient.

Every fold retains its cutoff, training/observed IDs, included series, window estimates, unmatched transactions, exclusions, daily cash changes and model metrics in [historical_horizons.json](historical_horizons.json).

## Public sample results

| Field | Current default | Rejected alternative |
| --- | ---: | ---: |
| Exact safe amount | 3/25 | 3/25 |
| Status | 18/25 | 19/25 |
| Payment method | 19/25 | 20/25 |
| Payment plan | 20/25 | 20/25 |
| Earliest full-payment date | 15/25 | 17/25 |
| Spending changes | 17/25 | 17/25 |
| Mean absolute amount error / requested amount | 4.4293% | 4.1415% |

These improvements meet the sample criteria relative to the local control but do not override the failed historical risk gate. Both models also remain below the original release's status/method/plan match counts and its 3.5504% normalized amount error. Neither the experimental nor original release gate has been weakened.

All 250 evaluation requests were run under both models and have zero contract errors on their respective projected ledgers. That does not establish hidden-dataset accuracy. The rejected run is stored as `experimental_output.csv` for reproducibility; it is not the root submission output or the API default. Full comparison and zero-call usage records are in [sample_comparison.json](sample_comparison.json).

## Attribution findings

| Request | Control capacity | Alternative capacity | Source-grounded limitation |
| --- | ---: | ---: | --- |
| request_06 | EUR 486.48 | EUR 510.83 | EUR 1,142.40 initial headroom minus EUR 655.92 expenses through January 13. Stopping streaming adds only EUR 19, giving EUR 505.48 under the control, still below the EUR 620.40 request. Changing salary paid January 15 cannot remove this earlier limit. |
| request_12 | ZAR 55,171.93 | ZAR 57,025.66 | No confirmed seasonal-income renewal. ZAR 149,889.89 initial headroom minus ZAR 94,717.96 spending through July 1. The alternative permits the supplied installments only with three spending changes; the public sample needs none. |
| request_19 | INR 23,528.45 | INR 24,094.84 | INR 106,745 initial headroom minus INR 83,216.55 expenses through September 14. The settled INR 2,854 receipt is already in opening balance and is not deducted again. Two weekly grocery forecasts total INR 10,293.88 before payday. |
| request_07 | INR 84,037.03 | INR 84,457.44 | Restoring a supported September 12 grocery occurrence explains the previous INR 7,849.54 decrease in capacity. The alternative restores the October 23 earliest-date match but still requires the dining reduction. |

[request_attribution.json](request_attribution.json) contains evidence, every contribution through the limiting transaction, full forecasts and each permitted individual spending-change check. The estimator used is identified explicitly in experimental traces. These calculations establish the consequences of the documented assumptions; they do not establish the reference's internal forecast.

## Verification and delivery

The complete suite has 108 passing tests and one unchanged failing sample release-gate test. Seven new tests cover complete-window requirements, missing cycles, authoritative bills, hand-calculated drawdowns, unknown amounts, user partitions and rejection when average accuracy improves but underprediction worsens. All execution uses frozen evidence and makes zero model calls.

The default full-dataset output is byte-identical to the control saved before this experiment. The refreshed code package includes the experiment and reports for review, while its normal run command continues using the control model. Further forecasting work needs an evidence-based allowance for cumulative prediction error; unconditional reductions in estimated spending did not meet the accepted safety criterion.
