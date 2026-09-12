# Requirements and checks

| Requirement | Implementation / validation |
| --- | --- |
| User, request and event ownership; multiple documents | Loader ownership validation; cross-user regression tests; all documents retained |
| Current balance, home currency and reserve | Opening-balance anchor; dated currency converter; capacity property tests |
| Historical and future cash-state distinctions | Lifecycle resolver; pending-debit, pending-credit, refund and investment tests |
| Financial priorities, protected and adjustable categories | Full profile retained in each trace; explicit category permissions govern changes; protected-spending tests |
| Methods, partial permission and maximum installment duration | Plan enumerator and verifier; eligibility reasons recorded for supplied offers |
| Request amount/type/date/deadline/text | Exact input case; schema/date checks; amount bounds and deadline replay |
| Dated FX direction | Exact settlement-date lookup; currency forecast tests |
| Recurrence supported by history | Membership and cadence traces; independent employer, invoice, airline, new-merchant and cancellation tests |
| Shared salary association and occurrence replacement | `test_income_association.py`: named/equal/independent employers, legitimate confirmation, ambiguous confirmation, explicit evidence targeting |
| Occurrence cancellation retains supported recurrence | Internal cancelled-date gap, renewal by settlement, cancelled amount/flexibility/anchor exclusion, at least two paid observations |
| Complete explicit and recurring accounting | Duplicate recurring membership and omitted/duplicate explicit obligation regressions; exact source dispositions in every request trace |
| Capacity invariants | Required debit cannot increase capacity; unknown credit cannot increase capacity; one-cent reserve breach rejected; shuffled inputs and unrelated users |
| Conservative variable spending | Upper quartile over latest 12 cycles; small-variation utility/healthcare/shopping tests |
| Multilingual and unlinked messages | All-source preparation; quoted fact validation; Indonesian salary regression |
| Image amounts and date conditions | All-source preparation; role/condition selection; due-date regression; source-bound reviewed fallback |
| Unsupported dates, currencies, directives | Deterministic fact validation; unsupported-date and injection tests |
| Missing mandatory commitment | Explicit uncertainty and zero certified capacity; no invented expense; release blocked |
| 90-day safety and maximum current capacity | Independent cumulative balances/suffix minima; property tests; selected-plan replay |
| Independently justified forecast membership and dates | Three reviewed CSV-based ledgers; 90-day brute-force payment replay; first ledger difference report |
| Recurrence validation without public answers | 550 historical folds across 275 users; future-confirmation exclusion test; timing and matched-amount metrics |
| Full-horizon expense and cash-flow validation | 825 paired 30/60/90-day folds; unmatched cash flows included; unknown amounts/FX explicitly unscorable; no invented historical balances |
| Forecast changes require accuracy and risk evidence | Frozen alternative and user partition; separate validation users; underprediction gate; rejected estimator stays outside default prediction |
| Alternating merchants on a regular cadence | Fortnightly dining regression; exceptional on-cadence basket remains excluded |
| Missing-commitment explanation reaches the output row | End-to-end regression checks zero certified amount and explicit missing-data explanation |
| Partial legs / supplied installment schedules | CSV verifier checks exact two-part sum or supplied offer; ranking regressions |
| At most three distinct spending actions | Action eligibility and mutual-exclusion verifier; below-half reduction regression |
| Six sample output fields | Decimal/structural comparison for every sample; immutable baseline gate |
| No cross-user/order effects | User isolation and shuffled-history regression; deterministic full-output replay |
| Explain every request end to end | Source accounting coverage; 275 hashed request traces; mismatch ledger reports |
| Output/schema/run commands | Full batch contract validation; API tests; package replay and artifact hashes |
| Usage and credentials | Scoped final-run usage; separate extraction usage; environment-only secrets; ZIP exclusions |

Future expense estimates, date-only intraday ordering and unresolved reference assumptions are disclosed policies, not claims about the hidden evaluator. Sample answers are used only by evaluation code.
