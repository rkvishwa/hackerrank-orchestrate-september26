# Remaining public sample differences

Run: 54ea0642ef314826b98c68f8f4c23cf3
Output SHA-256: b613a3a98215b9bd03c35fff08cac3193e97864b04fa05934cc7e39380131cb3

All six output fields are compared numerically or structurally. These differences do not establish that the public reference is wrong. Estimated future transactions remain assumptions.

## request_02

| Field | Local prediction | Public sample |
| --- | --- | --- |
| amount_safe_to_pay | 17775344.19 | 17229139.2 |

Opening balance: 60383889.2; protected minimum: 29158400. Baseline minimum: 46933744.19. Limiting date/source: 2025-08-13 / series:event_143.

Evidence:
- message_01: scoped income amendment

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / IDR / regular payroll | 33345000 | IDR | calendar month | 5 |
| debit / cloud_storage / IDR / shared storage plan | 369550 | IDR | calendar month | 5 |
| debit / dining / IDR / variable category spending | 1166644.88 | IDR | 21 days | 9 |
| debit / education / IDR / course tuition | 3040000 | IDR | calendar month | 5 |
| debit / entertainment / IDR / cinema and events | 1352563.79 | IDR | calendar month | 5 |
| debit / groceries / IDR / variable category spending | 2192475.45 | IDR | 10 days | 18 |
| debit / healthcare / IDR / clinic payment | 1594883.08 | IDR | calendar month | 5 |
| debit / housing / IDR / home repair reserve | 3534000 | IDR | calendar month | 6 |
| debit / insurance / IDR / household insurance | 1132400 | IDR | calendar month | 5 |
| debit / transport / IDR / variable category spending | 1327886.54 | IDR | 14 days | 13 |
| debit / utilities / IDR / municipal utilities | 2141849.94 | IDR | calendar month | 5 |

[Complete source records, projections, balances and candidate decisions](traces/request_02.json).
Independent arithmetic agrees with the estimated ledger. Its recurrence estimates and cash-flow dates have not been independently established by the public reference; the residual difference remains unresolved.

## request_03

| Field | Local prediction | Public sample |
| --- | --- | --- |
| amount_safe_to_pay | 920743.71 | 873000 |

Opening balance: 5810300; protected minimum: 2668700. Baseline minimum: 3589443.71. Limiting date/source: 2019-09-14 / series:event_252.

Evidence:
- message_02: scoped income amendment
- message_02: one-time income is not recurring salary; retain actual settled cash state

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / IDR / regular payroll | 4365000 | IDR | calendar month | 5 |
| debit / cloud_storage / IDR / shared storage plan | 20900 | IDR | calendar month | 5 |
| debit / dining / IDR / variable category spending | 171191.99 | IDR | 21 days | 9 |
| debit / groceries / IDR / variable category spending | 200238.72 | IDR | 10 days | 18 |
| debit / rent / IDR / landlord standing order | 1140000 | IDR | calendar month | 5 |
| debit / shopping / IDR / clothing and household items | 180395.29 | IDR | calendar month | 5 |
| debit / streaming / IDR / video streaming plan | 117800 | IDR | calendar month | 5 |
| debit / transport / IDR / variable category spending | 106233.46 | IDR | 21 days | 9 |
| debit / utilities / IDR / water and power payment | 295330.29 | IDR | calendar month | 5 |

[Complete source records, projections, balances and candidate decisions](traces/request_03.json).
Independent arithmetic agrees with the estimated ledger. Its recurrence estimates and cash-flow dates have not been independently established by the public reference; the residual difference remains unresolved.

## request_04

| Field | Local prediction | Public sample |
| --- | --- | --- |
| amount_safe_to_pay | 10011485.01 | 8401800 |

Opening balance: 52206950; protected minimum: 30686600. Baseline minimum: 40698085.01. Limiting date/source: 2024-06-13 / series:event_290.

Evidence:
- message_03: one-time income is not recurring salary; retain actual settled cash state

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / IDR / regular payroll | 38190000 | IDR | calendar month | 5 |
| debit / delivery_membership / IDR / food delivery membership | 377150 | IDR | calendar month | 5 |
| debit / dining / IDR / variable category spending | 1931412.81 | IDR | 14 days | 13 |
| debit / entertainment / IDR / local event tickets | 1484369.68 | IDR | calendar month | 5 |
| debit / groceries / IDR / variable category spending | 1698278.31 | IDR | 7 days | 26 |
| debit / gym / IDR / gym membership | 1027900 | IDR | calendar month | 5 |
| debit / music_subscription / IDR / music service subscription | 332500 | IDR | calendar month | 5 |
| debit / rent / IDR / residential rent payment | 12293000 | IDR | calendar month | 6 |
| debit / transport / IDR / variable category spending | 935850.82 | IDR | 7 days | 26 |
| debit / utilities / IDR / municipal utilities | 2017103.37 | IDR | calendar month | 5 |

[Complete source records, projections, balances and candidate decisions](traces/request_04.json).
An independent reconstruction from reviewed raw CSV records agrees with the production ledger; see [forecast diagnostics](forecast_diagnostics.md). The remaining reference discrepancy concerns forecast assumptions.

## request_05

| Field | Local prediction | Public sample |
| --- | --- | --- |
| amount_safe_to_pay | 0 | 737 |

Opening balance: 46475.1; protected minimum: 13100. Baseline minimum: 7641.65. Limiting date/source: 2026-02-03 / series:event_424.

Evidence:
- No additional evidence notes.

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| debit / cloud_storage / ZAR / cloud storage plan | 113.3 | ZAR | calendar month | 5 |
| debit / debt_repayment / ZAR / vehicle loan payment | 968 | ZAR | calendar month | 5 |
| debit / family_support / ZAR / dependent care payment | 840.4 | ZAR | calendar month | 5 |
| debit / groceries / ZAR / variable category spending | 768.64 | ZAR | 7 days | 26 |
| debit / healthcare / ZAR / therapy appointment | 722.37 | ZAR | calendar month | 5 |
| debit / rent / ZAR / apartment rent transfer | 4972 | ZAR | calendar month | 6 |
| debit / shopping / ZAR / personal shopping | 420.31 | ZAR | calendar month | 5 |
| debit / transport / ZAR / variable category spending | 431.81 | ZAR | 14 days | 13 |
| debit / utilities / ZAR / municipal utilities | 713.71 | ZAR | calendar month | 5 |

[Complete source records, projections, balances and candidate decisions](traces/request_05.json).
Independent arithmetic agrees with the estimated ledger. Its recurrence estimates and cash-flow dates have not been independently established by the public reference; the residual difference remains unresolved.

## request_06

Additional expense attribution and the rejected alternative are documented in [the cumulative experiment](expense_experiment/README.md). The figures below remain the default control prediction.

| Field | Local prediction | Public sample |
| --- | --- | --- |
| affordability_status | not_affordable | affordable_with_plan |
| amount_safe_to_pay | 486.48 | 603.3 |
| earliest_date_for_full_payment | 2026-02-15 | 2026-01-15 |
| payment_plan | none | 2026-01-03:620.40 |
| recommended_payment_method | not_recommended | full_payment |
| spending_changes_needed | none | stop:event_476 |

Opening balance: 1942.4; protected minimum: 800. Baseline minimum: 1286.48. Limiting date/source: 2026-01-13 / series:event_531.

Evidence:
- message_04: scoped income amendment

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / EUR / regular payroll | 1441 | EUR | calendar month | 5 |
| debit / cloud_storage / EUR / shared storage plan | 5 | EUR | calendar month | 5 |
| debit / dining / EUR / variable category spending | 54.09 | EUR | 7 days | 25 |
| debit / entertainment / EUR / monthly entertainment spend | 37.36 | EUR | calendar month | 5 |
| debit / groceries / EUR / variable category spending | 51.4 | EUR | 10 days | 18 |
| debit / insurance / EUR / vehicle insurance premium | 26 | EUR | calendar month | 5 |
| debit / rent / EUR / monthly rent | 254.1 | EUR | calendar month | 5 |
| debit / shopping / EUR / household shopping | 41.44 | EUR | calendar month | 5 |
| debit / streaming / EUR / family streaming plan | 19 | EUR | calendar month | 5 |
| debit / transport / EUR / variable category spending | 30.82 | EUR | 5 days | 35 |
| debit / utilities / EUR / water and power payment | 58.34 | EUR | calendar month | 5 |

[Complete source records, projections, balances and candidate decisions](traces/request_06.json).
Independent arithmetic agrees with the estimated ledger. Its recurrence estimates and cash-flow dates have not been independently established by the public reference; the residual difference remains unresolved.

## request_07

Additional expense attribution and the rejected alternative are documented in [the cumulative experiment](expense_experiment/README.md). The figures below remain the default control prediction.

| Field | Local prediction | Public sample |
| --- | --- | --- |
| amount_safe_to_pay | 84037.03 | 87170.56 |
| earliest_date_for_full_payment | 2024-11-23 | 2024-10-23 |
| spending_changes_needed | reduce_to:event_614:2835 | none |

Opening balance: 218945.56; protected minimum: 93000. Baseline minimum: 177037.03. Limiting date/source: 2024-09-20 / series:event_605.

Evidence:
- message_05: scoped income amendment

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / INR / regular payroll | 149000 | INR | calendar month | 5 |
| debit / debt_repayment / INR / personal loan payment | 15650 | INR | calendar month | 5 |
| debit / dining / INR / variable category spending | 6493.86 | INR | 21 days | 9 |
| debit / groceries / INR / variable category spending | 7849.54 | INR | 14 days | 13 |
| debit / music_subscription / INR / music subscription | 1005 | INR | calendar month | 5 |
| debit / rent / INR / monthly rent | 34200 | INR | calendar month | 6 |
| debit / transport / INR / variable category spending | 3690.82 | INR | 21 days | 9 |
| debit / utilities / INR / electricity bill | 7219.31 | INR | calendar month | 5 |

[Complete source records, projections, balances and candidate decisions](traces/request_07.json).
This stage restored omitted purchases on an otherwise regular spending cadence. Current capacity decreased and the earliest full-payment date moved from October 23 to November 23. The source-supported correction reduced reference agreement for the date and spending fields; release remains blocked.

## request_08

| Field | Local prediction | Public sample |
| --- | --- | --- |
| affordability_status | affordable_with_plan | affordable_later |
| amount_safe_to_pay | 274.84 | 284.57 |
| earliest_date_for_full_payment | (empty) | 2025-04-15 |
| recommended_payment_method | full_payment | wait |
| spending_changes_needed | reduce_to:event_716:24.5|stop:event_649|stop:event_648 | none |

Opening balance: 1536.57; protected minimum: 800. Baseline minimum: 1074.84. Limiting date/source: 2025-02-13 / series:event_716.

Evidence:
- message_06: scoped income amendment

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / EUR / regular payroll | 1422.85 | EUR | calendar month | 5 |
| debit / debt_repayment / EUR / personal loan payment | 177 | EUR | calendar month | 5 |
| debit / delivery_membership / EUR / grocery delivery membership | 24 | EUR | calendar month | 5 |
| debit / dining / EUR / variable category spending | 56.05 | EUR | 14 days | 13 |
| debit / education / EUR / school fee payment | 89 | EUR | calendar month | 5 |
| debit / groceries / EUR / variable category spending | 60.11 | EUR | 7 days | 26 |
| debit / music_subscription / EUR / music subscription | 14 | EUR | calendar month | 5 |
| debit / rent / EUR / apartment rent transfer | 467.5 | EUR | calendar month | 6 |
| debit / transport / EUR / variable category spending | 41.57 | EUR | 7 days | 26 |
| debit / utilities / EUR / municipal utilities | 80.9 | EUR | calendar month | 6 |

[Complete source records, projections, balances and candidate decisions](traces/request_08.json).
Independent arithmetic agrees with the estimated ledger. Its recurrence estimates and cash-flow dates have not been independently established by the public reference; the residual difference remains unresolved.

## request_10

| Field | Local prediction | Public sample |
| --- | --- | --- |
| amount_safe_to_pay | 0 | 12700 |

Opening balance: 750155; protected minimum: 225400. Baseline minimum: 161057.93. Limiting date/source: 2025-03-03 / series:event_840.

Evidence:
- message_07: unsettled credit excluded

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / INR / driver platform payout | 47802.51 | INR | 16 days | 4 |
| debit / delivery_membership / INR / delivery service plan | 1895 | INR | calendar month | 5 |
| debit / dining / INR / variable category spending | 9621.2 | INR | 14 days | 13 |
| debit / entertainment / INR / cinema and events | 4770.41 | INR | calendar month | 5 |
| debit / groceries / INR / variable category spending | 12092.24 | INR | 7 days | 26 |
| debit / gym / INR / community fitness plan | 4860 | INR | calendar month | 5 |
| debit / music_subscription / INR / music subscription | 2800 | INR | calendar month | 5 |
| debit / rent / INR / monthly rent | 69100 | INR | calendar month | 6 |
| debit / transport / INR / variable category spending | 6359.49 | INR | 7 days | 25 |
| debit / utilities / INR / electricity and water bill | 17771.13 | INR | calendar month | 5 |

[Complete source records, projections, balances and candidate decisions](traces/request_10.json).
Independent arithmetic agrees with the estimated ledger. Its recurrence estimates and cash-flow dates have not been independently established by the public reference; the residual difference remains unresolved.

## request_11

| Field | Local prediction | Public sample |
| --- | --- | --- |
| affordability_status | affordable_later | affordable_with_plan |
| amount_safe_to_pay | 11527136.55 | 12510645 |
| earliest_date_for_full_payment | 2025-05-15 | 2025-07-15 |
| payment_plan | 2025-05-15:13110000 | 2025-05-03:13110000 |
| recommended_payment_method | wait | full_payment |
| spending_changes_needed | none | reduce_to:event_989:665950 |

Opening balance: 63531795; protected minimum: 34140600. Baseline minimum: 45667736.55. Limiting date/source: 2025-05-14 / series:event_989.

Evidence:
- message_08: scoped income amendment
- message_08: unsettled credit excluded

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / IDR / regular payroll | 23256000 | IDR | calendar month | 5 |
| debit / cloud_storage / IDR / cloud storage plan | 168150 | IDR | calendar month | 5 |
| debit / dining / IDR / variable category spending | 1503635.49 | IDR | 21 days | 9 |
| debit / education / IDR / child education fee | 2544100 | IDR | calendar month | 5 |
| debit / entertainment / IDR / games and recreation | 1674887.61 | IDR | calendar month | 5 |
| debit / groceries / IDR / variable category spending | 1590529.64 | IDR | 10 days | 18 |
| debit / healthcare / IDR / regular medicine purchase | 3118089.32 | IDR | calendar month | 5 |
| debit / housing / IDR / home association fee | 2954500 | IDR | calendar month | 5 |
| debit / insurance / IDR / vehicle insurance premium | 1881000 | IDR | calendar month | 5 |
| debit / transport / IDR / variable category spending | 1212904.33 | IDR | 14 days | 13 |
| debit / utilities / IDR / municipal utilities | 2891149.67 | IDR | calendar month | 5 |

[Complete source records, projections, balances and candidate decisions](traces/request_11.json).
Independent arithmetic agrees with the estimated ledger. Its recurrence estimates and cash-flow dates have not been independently established by the public reference; the residual difference remains unresolved.

## request_12

Additional expense attribution and the rejected alternative are documented in [the cumulative experiment](expense_experiment/README.md). The figures below remain the default control prediction.

| Field | Local prediction | Public sample |
| --- | --- | --- |
| affordability_status | not_affordable | affordable_with_plan |
| amount_safe_to_pay | 55171.93 | 65164 |
| earliest_date_for_full_payment | (empty) | 2026-04-05 |
| payment_plan | none | 2026-04-19:22590.19|2026-05-20:22590.19|2026-06-20:22590.19 |
| recommended_payment_method | not_recommended | installments |

Opening balance: 193089.89; protected minimum: 43200. Baseline minimum: 98371.93. Limiting date/source: 2026-07-01 / series:event_1018.

Evidence:
- message_09: ambiguous income target; no increase or resumption
- message_09: income is not confirmed

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| debit / cloud_storage / ZAR / shared storage plan | 447.7 | ZAR | calendar month | 5 |
| debit / dining / ZAR / variable category spending | 2452.07 | ZAR | 21 days | 9 |
| debit / groceries / ZAR / variable category spending | 2448 | ZAR | 10 days | 18 |
| debit / rent / ZAR / monthly rent | 11792 | ZAR | calendar month | 6 |
| debit / shopping / ZAR / monthly shopping spend | 1267.67 | ZAR | calendar month | 5 |
| debit / streaming / ZAR / family streaming plan | 1504.8 | ZAR | calendar month | 5 |
| debit / transport / ZAR / variable category spending | 1679.15 | ZAR | 21 days | 9 |
| debit / utilities / ZAR / water and power payment | 3708.19 | ZAR | calendar month | 5 |

[Complete source records, projections, balances and candidate decisions](traces/request_12.json).
Independent arithmetic agrees with the estimated ledger. Its recurrence estimates and cash-flow dates have not been independently established by the public reference; the residual difference remains unresolved.

## request_13

| Field | Local prediction | Public sample |
| --- | --- | --- |
| affordability_status | not_affordable | affordable_later |
| amount_safe_to_pay | 433.54 | 433.4 |
| earliest_date_for_full_payment | (empty) | 2024-05-15 |
| payment_plan | none | 2024-05-15:941.60 |
| recommended_payment_method | not_recommended | wait |

Opening balance: 2789.52; protected minimum: 1300. Baseline minimum: 1733.54. Limiting date/source: 2024-05-14 / series:event_1121.

Evidence:
- No additional evidence notes.

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / EUR / primary household salary | 1343.54 | EUR | calendar month | 5 |
| debit / delivery_membership / EUR / delivery service plan | 21 | EUR | calendar month | 5 |
| debit / dining / EUR / variable category spending | 68.7 | EUR | 14 days | 13 |
| debit / entertainment / EUR / local event tickets | 33.83 | EUR | calendar month | 5 |
| debit / groceries / EUR / variable category spending | 98.36 | EUR | 7 days | 26 |
| debit / gym / EUR / community fitness plan | 61 | EUR | calendar month | 5 |
| debit / music_subscription / EUR / music subscription | 29 | EUR | calendar month | 5 |
| debit / rent / EUR / shared housing rent | 622.6 | EUR | calendar month | 6 |
| debit / transport / EUR / variable category spending | 49.29 | EUR | 7 days | 26 |
| debit / utilities / EUR / water and power payment | 146.33 | EUR | calendar month | 6 |

[Complete source records, projections, balances and candidate decisions](traces/request_13.json).
An independent reconstruction from reviewed raw CSV records agrees with the production ledger; see [forecast diagnostics](forecast_diagnostics.md). The remaining reference discrepancy concerns forecast assumptions.

## request_14

| Field | Local prediction | Public sample |
| --- | --- | --- |
| amount_safe_to_pay | 0 | 597.74 |

Opening balance: 3931.74; protected minimum: 2200. Baseline minimum: 2779.00. Limiting date/source: 2025-08-14 / series:event_1197.

Evidence:
- message_10: scoped income amendment
- message_10: new mandatory commitment lacks amount/date; positive capacity cannot be certified

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / EUR / regular payroll | 2717 | EUR | calendar month | 3 |
| debit / cloud_storage / EUR / cloud storage plan | 14 | EUR | calendar month | 5 |
| debit / debt_repayment / EUR / credit card repayment | 350 | EUR | calendar month | 5 |
| debit / family_support / EUR / family support payment | 226 | EUR | calendar month | 5 |
| debit / groceries / EUR / variable category spending | 123.41 | EUR | 7 days | 26 |
| debit / healthcare / EUR / family healthcare expense | 92.65 | EUR | calendar month | 5 |
| debit / rent / EUR / monthly rent | 688.6 | EUR | calendar month | 6 |
| debit / shopping / EUR / online retail purchases | 137.03 | EUR | calendar month | 5 |
| debit / transport / EUR / variable category spending | 55.96 | EUR | 14 days | 13 |
| debit / utilities / EUR / energy provider bill | 153.69 | EUR | calendar month | 5 |

[Complete source records, projections, balances and candidate decisions](traces/request_14.json).
A mandatory commitment lacks a supplied amount/date. Zero is uncertified positive capacity, not a zero-cost assumption. The missing input prevents a complete financial calculation.

## request_15

| Field | Local prediction | Public sample |
| --- | --- | --- |
| amount_safe_to_pay | 0 | 83.05 |

Opening balance: 1770.05; protected minimum: 1200. Baseline minimum: 1181.54. Limiting date/source: 2026-01-14 / series:event_1322.

Evidence:
- message_11: scoped income amendment

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / EUR / first job payroll | 1661 | EUR | calendar month | 2 |
| debit / debt_repayment / EUR / credit card repayment | 84 | EUR | calendar month | 5 |
| debit / delivery_membership / EUR / food delivery membership | 27 | EUR | calendar month | 5 |
| debit / dining / EUR / variable category spending | 45.13 | EUR | 14 days | 13 |
| debit / education / EUR / school fee payment | 159 | EUR | calendar month | 5 |
| debit / groceries / EUR / variable category spending | 64.42 | EUR | 7 days | 25 |
| debit / music_subscription / EUR / music subscription | 11 | EUR | calendar month | 5 |
| debit / rent / EUR / landlord standing order | 435.6 | EUR | calendar month | 6 |
| debit / transport / EUR / variable category spending | 36.7 | EUR | 7 days | 25 |
| debit / utilities / EUR / energy provider bill | 87.14 | EUR | calendar month | 5 |

[Complete source records, projections, balances and candidate decisions](traces/request_15.json).
Independent arithmetic agrees with the estimated ledger. Its recurrence estimates and cash-flow dates have not been independently established by the public reference; the residual difference remains unresolved.

## request_17

| Field | Local prediction | Public sample |
| --- | --- | --- |
| amount_safe_to_pay | 237187.90 | 243849.58 |
| earliest_date_for_full_payment | 2026-04-15 | 2026-03-15 |
| spending_changes_needed | reduce_to:event_1542:2935 | none |

Opening balance: 550379.58; protected minimum: 166100. Baseline minimum: 403287.90. Limiting date/source: 2026-03-14 / series:event_1529.

Evidence:
- No additional evidence notes.

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / INR / regular payroll | 206000 | INR | calendar month | 5 |
| debit / debt_repayment / INR / credit card repayment | 30200 | INR | calendar month | 5 |
| debit / delivery_membership / INR / food delivery membership | 1675 | INR | calendar month | 5 |
| debit / dining / INR / variable category spending | 6688.81 | INR | 14 days | 13 |
| debit / education / INR / course tuition | 13660 | INR | calendar month | 5 |
| debit / groceries / INR / variable category spending | 10873.47 | INR | 7 days | 26 |
| debit / music_subscription / INR / music subscription | 2055 | INR | calendar month | 5 |
| debit / rent / INR / apartment rent transfer | 49600 | INR | calendar month | 5 |
| debit / transport / INR / variable category spending | 5758.89 | INR | 7 days | 26 |
| debit / utilities / INR / municipal utilities | 9948.15 | INR | calendar month | 5 |

[Complete source records, projections, balances and candidate decisions](traces/request_17.json).
Independent arithmetic agrees with the estimated ledger. Its recurrence estimates and cash-flow dates have not been independently established by the public reference; the residual difference remains unresolved.

## request_18

| Field | Local prediction | Public sample |
| --- | --- | --- |
| amount_safe_to_pay | 507.26 | 462 |

Opening balance: 2486; protected minimum: 1400. Baseline minimum: 1907.26. Limiting date/source: 2026-07-14 / series:event_1608.

Evidence:
- message_13: internal transfer pair ambiguous; no unrelated records suppressed

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / EUR / regular payroll | 2310 | EUR | calendar month | 5 |
| debit / dining / EUR / variable category spending | 101.82 | EUR | 14 days | 13 |
| debit / groceries / EUR / variable category spending | 108.09 | EUR | 10 days | 18 |
| debit / healthcare / EUR / clinic payment | 162.41 | EUR | calendar month | 5 |
| debit / housing / EUR / building maintenance payment | 167 | EUR | calendar month | 6 |
| debit / insurance / EUR / household insurance | 68 | EUR | calendar month | 5 |
| debit / streaming / EUR / family streaming plan | 68 | EUR | calendar month | 5 |
| debit / transport / EUR / variable category spending | 50.57 | EUR | 14 days | 13 |
| debit / utilities / EUR / energy provider bill | 121.67 | EUR | calendar month | 5 |

[Complete source records, projections, balances and candidate decisions](traces/request_18.json).
Restoring all purchases on the regular cadence reduced capacity from 557.83 to 507.26, closer to the public 462.00. The residual forecast difference is unresolved.

## request_19

Additional expense attribution and the rejected alternative are documented in [the cumulative experiment](expense_experiment/README.md). The figures below remain the default control prediction.

| Field | Local prediction | Public sample |
| --- | --- | --- |
| amount_safe_to_pay | 23528.45 | 28820 |
| payment_plan | 2024-09-04:23528.45|2024-09-15:16131.55 | 2024-09-04:28820|2024-09-15:10840 |

Opening balance: 199545; protected minimum: 92800. Baseline minimum: 116328.45. Limiting date/source: 2024-09-14 / series:event_1661.

Evidence:
- No additional evidence notes.

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / INR / regular payroll | 131000 | INR | calendar month | 5 |
| debit / cloud_storage / INR / online backup subscription | 395 | INR | calendar month | 5 |
| debit / debt_repayment / INR / loan repayment | 11850 | INR | calendar month | 5 |
| debit / family_support / INR / childcare contribution | 12650 | INR | calendar month | 5 |
| debit / groceries / INR / variable category spending | 5146.94 | INR | 7 days | 25 |
| debit / healthcare / INR / clinic payment | 8946.09 | INR | calendar month | 5 |
| debit / rent / INR / residential rent payment | 36100 | INR | calendar month | 5 |
| debit / shopping / INR / clothing and household items | 6069.58 | INR | calendar month | 5 |
| debit / transport / INR / variable category spending | 3432.81 | INR | 14 days | 13 |
| debit / utilities / INR / municipal utilities | 6129.19 | INR | calendar month | 5 |

[Complete source records, projections, balances and candidate decisions](traces/request_19.json).
Independent arithmetic agrees with the estimated ledger. Its recurrence estimates and cash-flow dates have not been independently established by the public reference; the residual difference remains unresolved.

## request_20

| Field | Local prediction | Public sample |
| --- | --- | --- |
| amount_safe_to_pay | 7924.25 | 5400 |

Opening balance: 102609.05; protected minimum: 64500. Baseline minimum: 72424.25. Limiting date/source: 2026-02-13 / series:event_1739.

Evidence:
- message_14: unsettled credit excluded

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / INR / regular payroll | 108000 | INR | calendar month | 5 |
| debit / cloud_storage / INR / shared storage plan | 365 | INR | calendar month | 5 |
| debit / dining / INR / variable category spending | 3803.95 | INR | 21 days | 9 |
| debit / education / INR / school fee payment | 8740 | INR | calendar month | 5 |
| debit / entertainment / INR / cinema and events | 2279.67 | INR | calendar month | 5 |
| debit / groceries / INR / variable category spending | 3796.24 | INR | 10 days | 18 |
| debit / healthcare / INR / family healthcare expense | 6648.5 | INR | calendar month | 5 |
| debit / housing / INR / home association fee | 7950 | INR | calendar month | 6 |
| debit / insurance / INR / household insurance | 3290 | INR | calendar month | 6 |
| debit / transport / INR / variable category spending | 3063.34 | INR | 14 days | 13 |
| debit / utilities / INR / municipal utilities | 7977.68 | INR | calendar month | 6 |

[Complete source records, projections, balances and candidate decisions](traces/request_20.json).
Independent arithmetic agrees with the estimated ledger. Its recurrence estimates and cash-flow dates have not been independently established by the public reference; the residual difference remains unresolved.

## request_21

| Field | Local prediction | Public sample |
| --- | --- | --- |
| affordability_status | affordable_now | affordable_with_plan |
| amount_safe_to_pay | 1574.40 | 1543.35 |
| earliest_date_for_full_payment | 2026-04-03 | 2026-04-15 |
| spending_changes_needed | none | stop:event_1815|reduce_to:event_1816:23.50 |

Opening balance: 3911.35; protected minimum: 1800. Baseline minimum: 3464.35. Limiting date/source: 2026-04-12 / series:event_1817.

Evidence:
- No additional evidence notes.

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / USD / regular payroll | 2256 | USD | calendar month | 5 |
| debit / cloud_storage / USD / online backup subscription | 11 | USD | calendar month | 5 |
| debit / dining / USD / variable category spending | 97.67 | USD | 21 days | 9 |
| debit / groceries / USD / variable category spending | 85.9 | USD | 10 days | 18 |
| debit / rent / USD / residential rent payment | 718.8 | USD | calendar month | 6 |
| debit / shopping / USD / monthly shopping spend | 126.38 | USD | calendar month | 5 |
| debit / streaming / USD / streaming subscription | 47 | USD | calendar month | 5 |
| debit / transport / USD / variable category spending | 47.84 | USD | 21 days | 9 |
| debit / utilities / USD / municipal utilities | 123.72 | USD | calendar month | 5 |

[Complete source records, projections, balances and candidate decisions](traces/request_21.json).
Independent arithmetic agrees with the estimated ledger. Its recurrence estimates and cash-flow dates have not been independently established by the public reference; the residual difference remains unresolved.

## request_22

| Field | Local prediction | Public sample |
| --- | --- | --- |
| amount_safe_to_pay | 451.89 | 475.46 |
| earliest_date_for_full_payment | 2025-02-15 | 2025-01-15 |
| spending_changes_needed | stop:event_1890|stop:event_1892 | none |

Opening balance: 1132.46; protected minimum: 500. Baseline minimum: 951.89. Limiting date/source: 2024-12-14 / series:event_1891.

Evidence:
- message_15: informational; no additional cash

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / EUR / regular payroll | 616 | EUR | calendar month | 5 |
| debit / delivery_membership / EUR / food delivery membership | 5 | EUR | calendar month | 5 |
| debit / dining / EUR / variable category spending | 18.41 | EUR | 14 days | 13 |
| debit / entertainment / EUR / weekend entertainment | 22.03 | EUR | calendar month | 5 |
| debit / groceries / EUR / variable category spending | 27.33 | EUR | 7 days | 26 |
| debit / gym / EUR / gym membership | 17 | EUR | calendar month | 5 |
| debit / music_subscription / EUR / music service subscription | 6 | EUR | calendar month | 5 |
| debit / rent / EUR / apartment rent transfer | 178.2 | EUR | calendar month | 6 |
| debit / transport / EUR / variable category spending | 15.65 | EUR | 7 days | 25 |
| debit / utilities / EUR / electricity and water bill | 32.53 | EUR | calendar month | 5 |

[Complete source records, projections, balances and candidate decisions](traces/request_22.json).
Independent arithmetic agrees with the estimated ledger. Its recurrence estimates and cash-flow dates have not been independently established by the public reference; the residual difference remains unresolved.

## request_23

| Field | Local prediction | Public sample |
| --- | --- | --- |
| affordability_status | affordable_with_plan | affordable_later |
| amount_safe_to_pay | 8022.15 | 9152 |
| earliest_date_for_full_payment | (empty) | 2025-07-15 |
| recommended_payment_method | full_payment | wait |
| spending_changes_needed | stop:event_2000 | none |

Opening balance: 51957.9; protected minimum: 27000. Baseline minimum: 35022.15. Limiting date/source: 2025-05-14 / series:event_2027.

Evidence:
- message_16: unsettled credit excluded

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / ZAR / regular payroll | 45760 | ZAR | calendar month | 5 |
| debit / cloud_storage / ZAR / cloud storage plan | 295.9 | ZAR | calendar month | 5 |
| debit / debt_repayment / ZAR / education loan instalment | 5852 | ZAR | calendar month | 5 |
| debit / family_support / ZAR / childcare contribution | 4270.2 | ZAR | calendar month | 5 |
| debit / groceries / ZAR / variable category spending | 1794.76 | ZAR | 7 days | 25 |
| debit / healthcare / ZAR / clinic payment | 1377.89 | ZAR | calendar month | 5 |
| debit / rent / ZAR / shared housing rent | 15312 | ZAR | calendar month | 6 |
| debit / shopping / ZAR / personal shopping | 1389.39 | ZAR | calendar month | 5 |
| debit / transport / ZAR / variable category spending | 968.71 | ZAR | 14 days | 13 |
| debit / utilities / ZAR / electricity bill | 2877.85 | ZAR | calendar month | 5 |

[Complete source records, projections, balances and candidate decisions](traces/request_23.json).
Independent arithmetic agrees with the estimated ledger. Its recurrence estimates and cash-flow dates have not been independently established by the public reference; the residual difference remains unresolved.

## request_24

| Field | Local prediction | Public sample |
| --- | --- | --- |
| amount_safe_to_pay | 12960.25 | 13420 |

Opening balance: 85045; protected minimum: 51000. Baseline minimum: 63960.25. Limiting date/source: 2026-01-13 / series:event_2082.

Evidence:
- message_17: one-time income is not recurring salary; retain actual settled cash state

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / INR / regular payroll | 61000 | INR | calendar month | 5 |
| debit / cloud_storage / INR / online backup subscription | 355 | INR | calendar month | 5 |
| debit / dining / INR / variable category spending | 1942.46 | INR | 7 days | 26 |
| debit / entertainment / INR / local event tickets | 1916.16 | INR | calendar month | 5 |
| debit / groceries / INR / variable category spending | 2321.31 | INR | 10 days | 18 |
| debit / insurance / INR / insurance policy payment | 2510 | INR | calendar month | 5 |
| debit / rent / INR / landlord standing order | 18600 | INR | calendar month | 6 |
| debit / shopping / INR / monthly shopping spend | 2564 | INR | calendar month | 5 |
| debit / streaming / INR / family streaming plan | 1200 | INR | calendar month | 5 |
| debit / transport / INR / variable category spending | 1514.06 | INR | 5 days | 36 |
| debit / utilities / INR / household utility payment | 3417.7 | INR | calendar month | 5 |

[Complete source records, projections, balances and candidate decisions](traces/request_24.json).
Independent arithmetic agrees with the estimated ledger. Its recurrence estimates and cash-flow dates have not been independently established by the public reference; the residual difference remains unresolved.

## request_25

| Field | Local prediction | Public sample |
| --- | --- | --- |
| amount_safe_to_pay | 0 | 1425000 |

Opening balance: 32063050; protected minimum: 23379100. Baseline minimum: 23224629.62. Limiting date/source: 2024-03-14 / series:event_2206.

Evidence:
- No additional evidence notes.

| Recurring series | Native amount | Currency | Cadence | Members |
| --- | ---: | --- | --- | ---: |
| credit / salary / USD / international employer payroll | 1800 | USD | calendar month | 5 |
| debit / cloud_storage / IDR / cloud storage plan | 126350 | IDR | calendar month | 5 |
| debit / dining / IDR / variable category spending | 1128974.93 | IDR | 7 days | 25 |
| debit / entertainment / IDR / games and recreation | 499510.22 | IDR | calendar month | 5 |
| debit / groceries / IDR / variable category spending | 1369082.68 | IDR | 10 days | 18 |
| debit / insurance / IDR / insurance policy payment | 904400 | IDR | calendar month | 5 |
| debit / rent / IDR / monthly rent | 6954000 | IDR | calendar month | 6 |
| debit / shopping / IDR / monthly shopping spend | 1102784.74 | IDR | calendar month | 5 |
| debit / streaming / IDR / video streaming plan | 573800 | IDR | calendar month | 5 |
| debit / transport / IDR / variable category spending | 663001.49 | IDR | 5 days | 36 |
| debit / utilities / IDR / household utility payment | 1341541.39 | IDR | calendar month | 5 |

[Complete source records, projections, balances and candidate decisions](traces/request_25.json).
An independent reconstruction from reviewed raw CSV records agrees with the production ledger; see [forecast diagnostics](forecast_diagnostics.md). The remaining reference discrepancy concerns forecast assumptions.
