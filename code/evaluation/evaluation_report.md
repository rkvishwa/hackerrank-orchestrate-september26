# Evaluation Report

Run ID: 5c6bc3050bcf4f79b6ab185bfcc11b3b
Output SHA-256: d862ef189924636bb6e86beb72398344f55d7dfd2d1e916975cc8e2d95c20bcb
Requests: 250
Contract violations: 0
Hidden-dataset accuracy: unknown

## Public sample matches
- amount_safe_to_pay: 2/25 (8.0%)
- affordability_status: 19/25 (76.0%)
- recommended_payment_method: 20/25 (80.0%)
- payment_plan: 19/25 (76.0%)
- earliest_date_for_full_payment: 16/25 (64.0%)
- spending_changes_needed: 18/25 (72.0%)

Detailed field differences and the supporting cash-flow forecasts are in evaluation_report.json.
Sample agreement is measured separately from financial contract validation; passing validation does not prove hidden-label accuracy.

## Forecast policy
90 days; confirmed credits available on settlement date before outgoing payments; independent commitments; variable spending upper quartile of latest 12 observed payments; no speculative credits
