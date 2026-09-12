# Financial defect iteration

The three demonstrated defects are corrected, but public-sample accuracy did not improve. This candidate is **not approved for promotion**. The root submission artifacts and remote service remain the control version. Changes were made locally on `codex/financial-correctness`, preserving the existing working tree.

## Reproduced corrections

The frozen control is `artifacts/defect-control-20260912T230232Z/`, based on working-tree HEAD `b0c8c77d9e7afc00c93e0b431adc4c4b429e86cf`. Its manifest preserves source, dataset, evidence-cache and artifact hashes before editing. The source snapshot includes pre-existing uncommitted work; HEAD alone is not the control implementation.

`synthetic_reproductions.json` records actual executions of that control and the candidate on identical constructed inputs:

| Defect | Control forecast | Corrected forecast |
| --- | --- | --- |
| Paid October bill, cancelled November occurrence, paid December bill | No future bill | January, February and March bills of 100; cancelled amount 9,999 does not enter the estimate |
| One historical employer A salary plus employer B's January confirmation | B's 900 repeated for three months | B's confirmed 900 counted once; no unsupported continuation |
| Established employer A payroll plus employer B's same-day confirmation | January contains only B's 900 | January contains A's 500 and B's 900; A continues independently |

Income targeting, recurrence detection and explicit-payment replacement now share one association policy. Ownership, lifecycle links and named employers take precedence; matching amounts alone are insufficient. Ambiguous unnamed confirmations retain their candidate employments and source records, count once and cannot establish recurrence or amend multiple employers. Potential same-occurrence overlap is excluded conservatively.

Effective amendments are applied before cash-state partitioning. An occurrence cancellation can explain an internal cadence gap only with at least two paid observations, including when the cancellation is supplied directly in the CSV without a message patch. Cancellation-only records never select an amount, flexibility or paid anchor. Explicit ongoing cancellations still terminate commitments.

Every request trace records effective history, precise explicit-cash dispositions, employer associations and cancellation-only cadence evidence. Assertions reject duplicate series membership and missing or duplicated explicit cash obligations. The independent capacity calculation and selected-plan replay remain in force. No estimator, reserve, FX, protection, deadline, schedule, CSV or API rule was relaxed.

## Measured sample results

All counts are out of 25. All six fields use decimal/structural comparison; the explanation text is not an accuracy label.

| Version / stage | Amount | Status | Method | Plan | Earliest date | Changes | All six |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Original `3ba63a8` | 3 | 20 | 21 | 21 | 17 | 17 | 3 |
| Frozen local control | 3 | 18 | 19 | 20 | 15 | 17 | 3 |
| Cancellation correction | 3 | 18 | 19 | 20 | 15 | 17 | 3 |
| Employment recurrence correction | 3 | 18 | 19 | 20 | 15 | 17 | 3 |
| Corrected income association / replacement | 3 | 18 | 19 | 20 | 15 | 17 | 3 |
| Final candidate | 3 | 18 | 19 | 20 | 15 | 17 | 3 |
| PR #8 native comparison | 4 | 25 | 25 | 23 | 23 | 25 | 4 |
| PR #8 with reserve fallback removed | 4 | 23 | 23 | 21 | 23 | 23 | 4 |

Mean absolute amount error divided by requested amount is **4.429265%** for both local control and final candidate, compared with **3.550394%** for `3ba63a8`. This is a supplementary diagnostic, not the unknown official scoring formula. The 22 remaining incomplete sample rows are explained individually in [sample_differences.md](sample_differences.md), with the three matching rows included for completeness.

`stage_0_control.json`, `stage_1_cancellation.json`, `stage_2_employment.json`, `stage_3_income_corrected.json` and `stage_4_final.json` retain stage metrics and every field comparison. The superseded `stage_3_income_deduplication.json` is explicitly rejected: an intermediate targeting rule lost valid single-payroll amendments. Its apparent improvements are not accepted results.

## What the external comparison established

The adapter pins reviewed [PR #8](https://github.com/interviewstreet/hackerrank-orchestrate-september26/pull/8) commit `7c4cc0aa4698be2c558619b577e902bc5f326176` and six source-file hashes. It copies those files into a temporary directory, supplies request inputs without answer fields, clears credentials from the worker environment and blocks network/process calls. Neither its external source nor its forecasts are imported by prediction code. The submission contains only our adapter and diagnostic reports.

The actual offline replay reproduces the published status/method counts, but two recommendations violate the comparator's own reserve:

| Request | Required reserve | Lowest balance after PR plan | Shortfall |
| --- | ---: | ---: | ---: |
| 06, EUR | 800 | 777.695 | 22.305 |
| 11, IDR | 34,140,600 | 30,626,743.635 | 3,513,856.365 |

Removing its tolerance fallback reduces status/method matches to 23/25. This restricted variant is still not a contract-approved solution. Its forecast horizon and evidence/expense policies also differ. In request 11 it misses the Indonesian message confirming base salary of IDR 38,760,000 and uses historical 23,256,000 instead.

For priority requests 06, 08, 11, 12, 13, 21 and 23, `sample_differences.md` identifies the first daily/category ledger divergence, affected records, recurring membership, evidence, reserve calculation and candidate outcome. The complete chronological ledgers and all candidate replays are in `pr8_comparison.json`. Most differences concern expense dates, grouping or estimates; another participant's matching method does not establish a correct underlying ledger. Request 14 instead lacks the amount/date of mandatory childcare. The public answers do not provide their calculation, so unresolved reference assumptions remain unresolved.

## Full-dataset effects and acceptance

The final run produced 250 unique evaluation rows with zero contract errors and 275 request traces, including public samples. Five evaluation decisions changed from the local control; their exact before/after rows and evidence are in `evaluation_changes.json`:

- Requests 97, 124, 196 and 223 contain both previous/new employer histories and an unnamed confirmation. The candidate counts that confirmation once and does not infer ongoing employment from an ambiguous association. This is conservative and may understate actual continuing salary; the supplied confirmation does not identify its employer.
- Request 143's closed prize claim no longer terminates unrelated recurring payroll. The linked non-payroll evidence is scoped to the claim.

Hidden evaluation accuracy is unknown. These changes are not claimed as five correct answers.

The complete suite reports **125 passed, one failed**. The failure is the unchanged original-release sample gate, not a waived or skipped test. Regressions cover all three defects, legitimate confirmations, equal salaries from different employers, unnamed ambiguity, cancellation renewal, user/order isolation, unknown-credit and required-debit monotonicity, and a one-cent reserve breach. Source-accounting tests deliberately inject omitted and duplicate obligations.

Historical validation ran both control and candidate on **825 paired 30/60/90-day folds**, plus the existing **550 timing folds**. Results were identical. The existing historical promotion gates reject the candidate for insufficient changed/scorable forecasts and no cumulative expense accuracy improvement. These folds exclude future confirmations/evidence and cannot demonstrate the synthetic association fixes.

`validation.json` records the unchanged gates:

- No sample field regressed against the current control, but none improved and normalized amount error did not improve.
- Status, method, plan and earliest-date counts still regress against `3ba63a8`; these regressions predate this iteration.
- Eight requests have unquantified mandatory commitments: 14, 83, 87, 119, 127, 147, 155 and 219. Their zero certified capacity is an uncertainty result, not an invented zero-cost liability.
- Historical promotion requirements remain unmet. Dataset and frozen evidence hashes are unchanged.

The candidate output/package stay under `artifacts/defect-candidate-20260912/`. Packaging requires matching source, dataset, output, report and trace hashes and revalidates every CSV recommendation. Frozen-evidence ZIP replay and final control-preservation checks are recorded separately beside those artifacts in `replay_verification.json`.

## Usage and reproduction

No model calls were made during this iteration or the final cached run. The matching `evaluation/usage_report.md` records zero final-run tokens/cost. Prior evidence preparation is reported separately: 231 Azure GPT-4o calls, 188,136 tokens and a USD 0.647040 public-price reference estimate. Azure-specific billing is not assumed.

Normal run commands and setup instructions remain in the code README. The comparison and control/candidate validation commands are documented there as optional development diagnostics. Keep the latest-12 upper-quartile estimator and the frozen evidence cache for reproducing these results. No external participant code is needed to run the packaged financial agent.
