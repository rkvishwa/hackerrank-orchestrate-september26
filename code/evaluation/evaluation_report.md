# Evaluation Report

Run ID: b2749129b4984f06a337b03e96510bee
Output SHA-256: fb6a5af2589282a0b3a5730ad45f398b96d3390b90bf2e15889f39a701509347
Requests: 250
Contract violations: 0
Hidden-dataset accuracy: unknown

## Public sample matches

Deployment gate: BLOCKED
- affordability_status regressed: 20 -> 18
- recommended_payment_method regressed: 21 -> 19
- payment_plan regressed: 21 -> 20
- earliest_date_for_full_payment regressed: 17 -> 15

- amount_safe_to_pay: 3/25 (12.0%)
- affordability_status: 18/25 (72.0%)
- recommended_payment_method: 19/25 (76.0%)
- payment_plan: 20/25 (80.0%)
- earliest_date_for_full_payment: 15/25 (60.0%)
- spending_changes_needed: 17/25 (68.0%)

Mean absolute amount error / requested amount: 3.50%.
This supplementary measure describes error size; it does not replace exact matching or establish the official score.

All 25 field comparisons, balance ledgers, limiting cash flows, historical amount ranges and remaining mismatch investigations are in evaluation_report.json.
Sample agreement is measured separately from financial contract validation; passing validation does not prove hidden-label accuracy.

## Forecast policy
90 calendar dates including request date (ending request date + 89 days); confirmed credits available on settlement date before outgoing payments; independent commitments; variable spending upper quartile of latest 12 observed payments; no speculative credits

## Unresolved public-sample differences

These are reference disagreements, not proof that either forecast is correct. The independent capacity check verifies arithmetic on the derived ledger; it does not establish the reference's undocumented estimates.

| Request | Differing fields | Limiting date / flow | Baseline below reserve |
| --- | --- | --- | --- |
| request_02 | amount_safe_to_pay | 2025-08-13 / series:event_143 | False |
| request_03 | amount_safe_to_pay | 2019-09-14 / series:event_252 | False |
| request_04 | amount_safe_to_pay | 2024-06-13 / series:event_290 | False |
| request_05 | amount_safe_to_pay | 2026-02-03 / series:event_424 | True |
| request_06 | amount_safe_to_pay, affordability_status, recommended_payment_method, payment_plan, earliest_date_for_full_payment, spending_changes_needed | 2026-01-13 / series:event_531 | False |
| request_07 | amount_safe_to_pay, earliest_date_for_full_payment, spending_changes_needed | 2024-09-20 / series:event_605 | False |
| request_08 | amount_safe_to_pay, affordability_status, recommended_payment_method, earliest_date_for_full_payment, spending_changes_needed | 2025-02-13 / series:event_716 | False |
| request_10 | amount_safe_to_pay | 2025-03-03 / series:event_840 | True |
| request_11 | amount_safe_to_pay, affordability_status, recommended_payment_method, payment_plan, earliest_date_for_full_payment, spending_changes_needed | 2025-05-14 / series:event_989 | False |
| request_12 | amount_safe_to_pay, affordability_status, recommended_payment_method, payment_plan, earliest_date_for_full_payment | 2026-07-01 / series:event_1018 | False |
| request_13 | amount_safe_to_pay, affordability_status, recommended_payment_method, payment_plan, earliest_date_for_full_payment | 2024-05-14 / series:event_1121 | False |
| request_14 | amount_safe_to_pay | 2025-08-14 / series:event_1197 | False |
| request_15 | amount_safe_to_pay | 2026-01-14 / series:event_1322 | True |
| request_17 | amount_safe_to_pay, earliest_date_for_full_payment, spending_changes_needed | 2026-03-14 / series:event_1529 | False |
| request_18 | amount_safe_to_pay | 2026-07-14 / series:event_1608 | False |
| request_19 | amount_safe_to_pay, payment_plan | 2024-09-14 / series:event_1661 | False |
| request_20 | amount_safe_to_pay | 2026-02-13 / series:event_1739 | False |
| request_21 | amount_safe_to_pay, affordability_status, earliest_date_for_full_payment, spending_changes_needed | 2026-04-12 / series:event_1817 | False |
| request_22 | amount_safe_to_pay, earliest_date_for_full_payment, spending_changes_needed | 2024-12-14 / series:event_1891 | False |
| request_23 | amount_safe_to_pay, affordability_status, recommended_payment_method, earliest_date_for_full_payment, spending_changes_needed | 2025-05-14 / series:event_2027 | False |
| request_24 | amount_safe_to_pay | 2026-01-13 / series:event_2082 | False |
| request_25 | amount_safe_to_pay | 2024-03-14 / series:event_2206 | True |
