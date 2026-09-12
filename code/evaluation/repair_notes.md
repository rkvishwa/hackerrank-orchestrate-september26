# Current local result: expense alternative rejected

The latest cumulative expense experiment is documented in [expense_experiment/README.md](expense_experiment/README.md). It evaluates all 275 users over 30, 60 and 90 days and runs all 250 evaluation requests under both models. The alternative improves sample status/method/date counts and normalized amount error to 4.1415%, but increases historical underprediction risk and was not promoted. The production default and root output remain byte-identical to the prior local control: 3/25 exact amounts, 4.4293% normalized amount error, and the original release gate still blocked.

The complete suite now has 108 passing tests and one unchanged failing sample gate. Both full-dataset runs have zero contract errors and zero model calls. Source datasets and the remote deployment remain unchanged. The normal code.zip run uses the control estimator; the rejected experimental output is labeled separately inside its report directory.

## Previous local iteration

The independent forecast investigation and current results are documented in [forecast_diagnostics.md](forecast_diagnostics.md). The original reconstruction, evidence extraction, user isolation and request tracing remain in place. The new correction preserves a complete regular spending cadence when merchants alternate, and the missing-commitment warning now reaches the output row.

Exact amounts remain 3/25. Relative to the previous local iteration, normalized amount error improves from 4.5236% to 4.4293%, while earliest-date matches fall from 16 to 15 and spending-change matches fall from 18 to 17. Relative to the original release, the candidate remains worse on status, method, plan, date and normalized amount error. It is not a validated release improvement.

All 250 evaluation rows pass output contracts. There are 275 request traces and 25,342 accounted financial events. The full suite has 101 passing tests and one failed sample release gate; it was not weakened or skipped. Historical backtesting covers 550 windows across all 275 users. Independent raw-record ledgers agree with the engine for request_13, request_04 and request_25, but do not explain the public reference's different forecast assumptions.

Eight unquantified childcare commitments remain: request_119, request_127, request_14, request_147, request_155, request_219, request_83 and request_87. Only request_14 is a public sample; this does not explain the other 21 sample mismatches. Image_14 retains an explicitly unresolved handwritten transcription disagreement; it is settled and nonrecurring. Other reviewed image corrections and date-conditioned telecom amounts remain unchanged.

No remote operations were performed. output.csv and code.zip are local candidate artifacts; the existing deployment remains unchanged. Full current sample differences, evidence, estimates and binding calculations are in [sample_differences.md](sample_differences.md). Final-run model usage is zero; prior extraction usage and cost are reported separately in [usage_report.md](usage_report.md).
