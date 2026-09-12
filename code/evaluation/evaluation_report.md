# Evaluation Report

Run ID: a1aeab6db9f3487ebc3745bee39bfa12
Output SHA-256: e5fe914636d8a042c246cd8239f1c86e46ddeac02e552ecad10d7a58521bf919
Requests: 250
Contract violations: 0
Hidden-dataset accuracy: unknown

## Public sample matches
- amount_safe_to_pay: 3/25 (12.0%)
- affordability_status: 20/25 (80.0%)
- recommended_payment_method: 21/25 (84.0%)
- payment_plan: 21/25 (84.0%)
- earliest_date_for_full_payment: 17/25 (68.0%)
- spending_changes_needed: 17/25 (68.0%)

Mean absolute amount error / requested amount: 3.55%.
This supplementary measure describes error size; it does not replace exact matching or establish the official score.

All 25 field comparisons, balance ledgers, limiting cash flows, historical amount ranges and remaining mismatch investigations are in evaluation_report.json.
Sample agreement is measured separately from financial contract validation; passing validation does not prove hidden-label accuracy.

## Forecast policy
90 calendar dates including request date (ending request date + 89 days); confirmed credits available on settlement date before outgoing payments; independent commitments; variable spending upper quartile of latest 12 observed payments; no speculative credits
