# Sample comparison and unresolved differences

All 25 samples are compared below. Amounts and schedules use decimal/structural comparisons. Reference fields appear only in evaluation. Full original/effective records, income associations, recurrence membership, daily balances and every candidate are in `pr8_comparison.json` and the candidate request traces.

Capacity is checked independently from cumulative balances and minimum remaining headroom. An unknown mandatory commitment prevents certification even when the quantified ledger is positive. PR #8 is a diagnostic comparator, not financial truth. Its strict variant only removes its reserve-tolerance fallback.

## request_01

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | affordable_now | affordable_now | yes |
| amount_safe_to_pay | 25256.00 | 25256 | yes |
| earliest_date_for_full_payment | 2024-03-03 | 2024-03-03 | yes |
| payment_plan | 2024-03-03:25256 | 2024-03-03:25256 | yes |
| recommended_payment_method | full_payment | full_payment | yes |
| spending_changes_needed | none | none | yes |

All six fields match. Different expense calendars do not change the recommendation because current capacity exceeds the request.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (ZAR): opening 58481.1; lowest balance 47990.85 on 2024-03-13 after series:event_31; reserve 18000; remaining headroom 29990.85. Baseline safe amount after the request cap and evidence blockers: 25256.00. First safe full-payment date: 2024-03-03.

First PR ledger divergence: 2024-03-03 debit transport, ours 0, PR #8 406.54. PR baseline lowest balance 50269.89 on 2024-03-13.
Affected source category records: event_59, event_60, event_61, event_62, event_63, event_64, event_65, event_66, event_67, event_68, event_69, event_70, event_71, event_72, event_73, event_74, event_75, event_76, event_77, event_78, event_79, event_80, event_81, event_82, event_83, event_84, event_102.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|ZAR\|regular payroll | 23320 ZAR (constant_or_income_policy) | monthly | event_25, event_103 | none |
| debit\|debt_repayment\|ZAR\|education loan instalment | 3487 ZAR (constant_or_income_policy) | monthly | event_04, event_10, event_16, event_22, event_29 | none |
| debit\|delivery_membership\|ZAR\|delivery service plan | 306.9 ZAR (constant_or_income_policy) | monthly | event_06, event_12, event_18, event_24, event_31 | none |
| debit\|dining\|ZAR\|variable category spending | 1160.42 ZAR (upper_quartile_latest_12) | 14 days | event_85, event_86, event_87, event_88, event_89, event_90, event_91, event_92, event_93, event_94, event_95, event_96, event_97 | none |
| debit\|education\|ZAR\|professional training fee | 1821.6 ZAR (constant_or_income_policy) | monthly | event_03, event_09, event_15, event_21, event_28 | none |
| debit\|groceries\|ZAR\|variable category spending | 881.22 ZAR (upper_quartile_latest_12) | 7 days | event_33, event_34, event_35, event_36, event_37, event_38, event_39, event_40, event_41, event_42, event_43, event_44, event_45, event_46, event_47, event_48, event_49, event_50, event_51, event_52, event_53, event_54, event_55, event_56, event_57, event_58 | none |
| debit\|music_subscription\|ZAR\|music service subscription | 235.4 ZAR (constant_or_income_policy) | monthly | event_05, event_11, event_17, event_23, event_30 | none |
| debit\|rent\|ZAR\|apartment rent transfer | 5148 ZAR (constant_or_income_policy) | monthly | event_01, event_07, event_13, event_19, event_26, event_32 | none |
| debit\|transport\|ZAR\|variable category spending | 488.36 ZAR (upper_quartile_latest_12) | 7 days | event_59, event_60, event_61, event_62, event_63, event_64, event_65, event_66, event_67, event_68, event_69, event_70, event_71, event_72, event_73, event_74, event_75, event_76, event_77, event_78, event_79, event_80, event_81, event_82, event_83, event_84 | none |
| debit\|utilities\|ZAR\|household utility payment | 1541.75 ZAR (upper_quartile_latest_12) | monthly | event_02, event_08, event_14, event_20, event_27 | none |

Candidate audit: 4 candidates; 3 have rejection/ranking reasons. All reasons and schedules are retained in JSON.
- full_payment: ranked below selected plan by contract priorities
- full_payment: ranked below selected plan by contract priorities
- full_payment: ranked below selected plan by contract priorities

## request_02

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | affordable_with_plan | affordable_with_plan | yes |
| amount_safe_to_pay | 17775344.19 | 17229139.2 | no |
| earliest_date_for_full_payment | 2025-09-15 | 2025-09-15 | yes |
| payment_plan | 2025-08-08:15952906.67\|2025-09-07:15952906.67\|2025-10-07:15952906.67 | 2025-08-08:15952906.67\|2025-09-07:15952906.67\|2025-10-07:15952906.67 | yes |
| recommended_payment_method | installments | installments | yes |
| spending_changes_needed | none | none | yes |

message_01 confirms salary IDR 42,750,000. That amount is retained. The remaining amount difference is at the pre-payday expense trough; both implementations recommend the supplied installment plan.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (IDR): opening 60383889.2; lowest balance 46933744.19 on 2025-08-13 after series:event_143; reserve 29158400; remaining headroom 17775344.19. Baseline safe amount after the request cap and evidence blockers: 17775344.19. First safe full-payment date: 2025-09-15.

First PR ledger divergence: 2025-08-09 debit dining, ours 0, PR #8 1204805.34. PR baseline lowest balance 47087544.21 on 2025-08-13.
Affected source category records: event_176, event_177, event_178, event_179, event_180, event_181, event_182, event_183, event_184.

Evidence resolutions:
- message_01: scoped income amendment Quote: Gaji bulanan Anda naik menjadi IDR 42750000.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|IDR\|regular payroll | 33345000 IDR (constant_or_income_policy) | monthly | event_104, event_112, event_120, event_128, event_136 | none |
| debit\|cloud_storage\|IDR\|shared storage plan | 369550 IDR (constant_or_income_policy) | monthly | event_111, event_119, event_127, event_135, event_143 | none |
| debit\|dining\|IDR\|variable category spending | 1166644.88 IDR (upper_quartile_latest_12) | 21 days | event_176, event_177, event_178, event_179, event_180, event_181, event_182, event_183, event_184 | none |
| debit\|education\|IDR\|course tuition | 3040000 IDR (constant_or_income_policy) | monthly | event_108, event_116, event_124, event_132, event_140 | none |
| debit\|entertainment\|IDR\|cinema and events | 1352563.79 IDR (upper_quartile_latest_12) | monthly | event_110, event_118, event_126, event_134, event_142 | none |
| debit\|groceries\|IDR\|variable category spending | 2192475.45 IDR (upper_quartile_latest_12) | 10 days | event_145, event_146, event_147, event_148, event_149, event_150, event_151, event_152, event_153, event_154, event_155, event_156, event_157, event_158, event_159, event_160, event_161, event_162 | none |
| debit\|healthcare\|IDR\|clinic payment | 1594883.08 IDR (upper_quartile_latest_12) | monthly | event_109, event_117, event_125, event_133, event_141 | none |
| debit\|housing\|IDR\|home repair reserve | 3534000 IDR (constant_or_income_policy) | monthly | event_105, event_113, event_121, event_129, event_137, event_144 | none |
| debit\|insurance\|IDR\|household insurance | 1132400 IDR (constant_or_income_policy) | monthly | event_107, event_115, event_123, event_131, event_139 | none |
| debit\|transport\|IDR\|variable category spending | 1327886.54 IDR (upper_quartile_latest_12) | 14 days | event_163, event_164, event_165, event_166, event_167, event_168, event_169, event_170, event_171, event_172, event_173, event_174, event_175 | none |
| debit\|utilities\|IDR\|municipal utilities | 2141849.94 IDR (upper_quartile_latest_12) | monthly | event_106, event_114, event_122, event_130, event_138 | none |

Candidate audit: 4 candidates; 3 have rejection/ranking reasons. All reasons and schedules are retained in JSON.
- installments: ranked below selected plan by contract priorities
- installments: ranked below selected plan by contract priorities
- installments: ranked below selected plan by contract priorities

## request_03

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | affordable_later | affordable_later | yes |
| amount_safe_to_pay | 920743.71 | 873000 | no |
| earliest_date_for_full_payment | 2019-11-15 | 2019-11-15 | yes |
| payment_plan | 2019-11-15:5491000 | 2019-11-15:5491000 | yes |
| recommended_payment_method | wait | wait | yes |
| spending_changes_needed | none | none | yes |

image_01 and message_02 distinguish routine payroll from a one-time adjustment. Confirmed document amounts remain authoritative. The same wait date is reached, with a different pre-payday expense estimate.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (IDR): opening 5810300; lowest balance 3589443.71 on 2019-09-14 after series:event_252; reserve 2668700; remaining headroom 920743.71. Baseline safe amount after the request cap and evidence blockers: 920743.71. First safe full-payment date: 2019-11-15.

First PR ledger divergence: 2019-09-03 debit dining, ours 0, PR #8 135718.35. PR baseline lowest balance 3591470.0700000008 on 2019-09-14.
Affected source category records: event_244, event_245, event_246, event_247, event_248, event_249, event_250, event_251, event_252.

Evidence resolutions:
- image_01: document role and settlement-date conditions
- message_02: scoped income amendment Quote: Gaji rutin untuk penggajian berikutnya sudah dikonfirmasi.
- message_02: one-time income is not recurring salary; retain actual settled cash state Quote: Slip gaji berikutnya akan menampilkan gaji rutin dan penyesuaian satu kali secara terpisah.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|IDR\|regular payroll | 4365000 IDR (constant_or_income_policy) | monthly | event_186, event_192, event_198, event_204, event_210 | none |
| debit\|cloud_storage\|IDR\|shared storage plan | 20900 IDR (constant_or_income_policy) | monthly | event_189, event_195, event_201, event_207, event_214 | none |
| debit\|dining\|IDR\|variable category spending | 171191.99 IDR (upper_quartile_latest_12) | 21 days | event_244, event_245, event_246, event_247, event_248, event_249, event_250, event_251, event_252 | none |
| debit\|groceries\|IDR\|variable category spending | 200238.72 IDR (upper_quartile_latest_12) | 10 days | event_217, event_218, event_219, event_220, event_221, event_222, event_223, event_224, event_225, event_226, event_227, event_228, event_229, event_230, event_231, event_232, event_233, event_234 | none |
| debit\|rent\|IDR\|landlord standing order | 1140000 IDR (constant_or_income_policy) | monthly | event_187, event_193, event_199, event_205, event_212 | none |
| debit\|shopping\|IDR\|clothing and household items | 180395.29 IDR (upper_quartile_latest_12) | monthly | event_191, event_197, event_203, event_209, event_216 | none |
| debit\|streaming\|IDR\|video streaming plan | 117800 IDR (constant_or_income_policy) | monthly | event_190, event_196, event_202, event_208, event_215 | none |
| debit\|transport\|IDR\|variable category spending | 106233.46 IDR (upper_quartile_latest_12) | 21 days | event_235, event_236, event_237, event_238, event_239, event_240, event_241, event_242, event_243 | none |
| debit\|utilities\|IDR\|water and power payment | 295330.29 IDR (upper_quartile_latest_12) | monthly | event_188, event_194, event_200, event_206, event_213 | none |

Candidate audit: 24 candidates; 23 have rejection/ranking reasons. All reasons and schedules are retained in JSON.
- full_payment: reserve breach or unquantified mandatory commitment
- full_payment: reserve breach or unquantified mandatory commitment
- full_payment: ranked below selected plan by contract priorities

## request_04

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | affordable_later | affordable_later | yes |
| amount_safe_to_pay | 10011485.01 | 8401800 | no |
| earliest_date_for_full_payment | 2024-06-15 | 2024-06-15 | yes |
| payment_plan | 2024-06-15:12693000 | 2024-06-15:12693000 | yes |
| recommended_payment_method | wait | wait | yes |
| spending_changes_needed | none | none | yes |

message_03 says the quarterly bonus is still awaiting assessment. It is not available income. Both recommendations wait; the remaining capacity difference comes from the expense ledger before salary.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (IDR): opening 52206950; lowest balance 40698085.01 on 2024-06-13 after series:event_290; reserve 30686600; remaining headroom 10011485.01. Baseline safe amount after the request cap and evidence blockers: 10011485.01. First safe full-payment date: 2024-06-15.

First PR ledger divergence: 2024-06-04 debit groceries, ours 0, PR #8 1831437.58. PR baseline lowest balance 41908741.99 on 2024-06-14.
Affected source category records: event_292, event_293, event_294, event_295, event_296, event_297, event_298, event_299, event_300, event_301, event_302, event_303, event_304, event_305, event_306, event_307, event_308, event_309, event_310, event_311, event_312, event_313, event_314, event_315, event_316, event_317.

Evidence resolutions:
- message_03: one-time income is not recurring salary; retain actual settled cash state Quote: Bonus kuartalan Anda masih menunggu hasil akhir penilaian kinerja.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|IDR\|regular payroll | 38190000 IDR (constant_or_income_policy) | monthly | event_255, event_262, event_269, event_277, event_284 | none |
| debit\|delivery_membership\|IDR\|food delivery membership | 377150 IDR (constant_or_income_policy) | monthly | event_259, event_266, event_274, event_281, event_288 | none |
| debit\|dining\|IDR\|variable category spending | 1931412.81 IDR (upper_quartile_latest_12) | 14 days | event_344, event_345, event_346, event_347, event_348, event_349, event_350, event_351, event_352, event_353, event_354, event_355, event_356 | none |
| debit\|entertainment\|IDR\|local event tickets | 1484369.68 IDR (upper_quartile_latest_12) | monthly | event_261, event_268, event_276, event_283, event_290 | none |
| debit\|groceries\|IDR\|variable category spending | 1698278.31 IDR (upper_quartile_latest_12) | 7 days | event_292, event_293, event_294, event_295, event_296, event_297, event_298, event_299, event_300, event_301, event_302, event_303, event_304, event_305, event_306, event_307, event_308, event_309, event_310, event_311, event_312, event_313, event_314, event_315, event_316, event_317 | none |
| debit\|gym\|IDR\|gym membership | 1027900 IDR (constant_or_income_policy) | monthly | event_260, event_267, event_275, event_282, event_289 | none |
| debit\|music_subscription\|IDR\|music service subscription | 332500 IDR (constant_or_income_policy) | monthly | event_258, event_265, event_273, event_280, event_287 | none |
| debit\|rent\|IDR\|residential rent payment | 12293000 IDR (constant_or_income_policy) | monthly | event_256, event_263, event_271, event_278, event_285, event_291 | none |
| debit\|transport\|IDR\|variable category spending | 935850.82 IDR (upper_quartile_latest_12) | 7 days | event_318, event_319, event_320, event_321, event_322, event_323, event_324, event_325, event_326, event_327, event_328, event_329, event_330, event_331, event_332, event_333, event_334, event_335, event_336, event_337, event_338, event_339, event_340, event_341, event_342, event_343 | none |
| debit\|utilities\|IDR\|municipal utilities | 2017103.37 IDR (upper_quartile_latest_12) | monthly | event_257, event_264, event_272, event_279, event_286 | none |

Candidate audit: 8 candidates; 7 have rejection/ranking reasons. All reasons and schedules are retained in JSON.
- full_payment: reserve breach or unquantified mandatory commitment
- full_payment: reserve breach or unquantified mandatory commitment
- full_payment: ranked below selected plan by contract priorities

## request_05

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | not_affordable | not_affordable | yes |
| amount_safe_to_pay | 0 | 737 | no |
| earliest_date_for_full_payment | <empty> | <empty> | yes |
| payment_plan | none | none | yes |
| recommended_payment_method | not_recommended | not_recommended | yes |
| spending_changes_needed | none | none | yes |

The 90-day baseline falls below reserve without any purchase. The positive sample amount cannot pass that ledger. Whether the reference used different routine spending or a shorter capacity check is unknown.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (ZAR): opening 46475.1; lowest balance 7641.65 on 2026-02-03 after series:event_424; reserve 13100; remaining headroom -5458.35. Baseline safe amount after the request cap and evidence blockers: 0. First safe full-payment date: <empty>.

First PR ledger divergence: 2025-11-11 debit groceries, ours 768.64, PR #8 0. PR baseline lowest balance 18692.649999999998 on 2026-02-02.
Affected source category records: event_399, event_400, event_401, event_402, event_403, event_404, event_405, event_406, event_407, event_408, event_409, event_410, event_411, event_412, event_413, event_414, event_415, event_416, event_417, event_418, event_419, event_420, event_421, event_422, event_423, event_424.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| debit\|cloud_storage\|ZAR\|cloud storage plan | 113.3 ZAR (constant_or_income_policy) | monthly | event_364, event_372, event_380, event_388, event_396 | none |
| debit\|debt_repayment\|ZAR\|vehicle loan payment | 968 ZAR (constant_or_income_policy) | monthly | event_361, event_369, event_377, event_385, event_393 | none |
| debit\|family_support\|ZAR\|dependent care payment | 840.4 ZAR (constant_or_income_policy) | monthly | event_363, event_371, event_379, event_387, event_395 | none |
| debit\|groceries\|ZAR\|variable category spending | 768.64 ZAR (upper_quartile_latest_12) | 7 days | event_399, event_400, event_401, event_402, event_403, event_404, event_405, event_406, event_407, event_408, event_409, event_410, event_411, event_412, event_413, event_414, event_415, event_416, event_417, event_418, event_419, event_420, event_421, event_422, event_423, event_424 | none |
| debit\|healthcare\|ZAR\|therapy appointment | 722.37 ZAR (upper_quartile_latest_12) | monthly | event_362, event_370, event_378, event_386, event_394 | none |
| debit\|rent\|ZAR\|apartment rent transfer | 4972 ZAR (constant_or_income_policy) | monthly | event_359, event_367, event_375, event_383, event_391, event_398 | none |
| debit\|shopping\|ZAR\|personal shopping | 420.31 ZAR (upper_quartile_latest_12) | monthly | event_365, event_373, event_381, event_389, event_397 | none |
| debit\|transport\|ZAR\|variable category spending | 431.81 ZAR (upper_quartile_latest_12) | 14 days | event_425, event_426, event_427, event_428, event_429, event_430, event_431, event_432, event_433, event_434, event_435, event_436, event_437 | none |
| debit\|utilities\|ZAR\|municipal utilities | 713.71 ZAR (upper_quartile_latest_12) | monthly | event_360, event_368, event_376, event_384, event_392 | none |

Candidate audit: 4 candidates; 4 have rejection/ranking reasons. All reasons and schedules are retained in JSON.
- full_payment: reserve breach or unquantified mandatory commitment
- full_payment: reserve breach or unquantified mandatory commitment
- full_payment: reserve breach or unquantified mandatory commitment

## request_06

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | not_affordable | affordable_with_plan | no |
| amount_safe_to_pay | 486.48 | 603.3 | no |
| earliest_date_for_full_payment | 2026-02-15 | 2026-01-15 | no |
| payment_plan | none | 2026-01-03:620.40 | no |
| recommended_payment_method | not_recommended | full_payment | no |
| spending_changes_needed | none | stop:event_476 | no |

message_04 limits temporary EUR 1,037.52 pay to the next payroll. Our existing interpretation resumes the historic amount afterward; PR #8 keeps reduced pay throughout. This is an unresolved duration assumption. Its immediate-pay recommendation also breaches its own reserve, so its matching answer does not demonstrate a safe fix.

Classification: comparison_implementation_reserve_violation, recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (EUR): opening 1942.4; lowest balance 1286.48 on 2026-01-13 after series:event_531; reserve 800; remaining headroom 486.48. Baseline safe amount after the request cap and evidence blockers: 486.48. First safe full-payment date: 2026-02-15.

First PR ledger divergence: 2026-01-03 debit transport, ours 30.82, PR #8 0. PR baseline lowest balance 1379.0950000000003 on 2026-01-14.
Affected source category records: event_497, event_498, event_499, event_500, event_501, event_502, event_503, event_504, event_505, event_506, event_507, event_508, event_509, event_510, event_511, event_512, event_513, event_514, event_515, event_516, event_517, event_518, event_519, event_520, event_521, event_522, event_523, event_524, event_525, event_526, event_527, event_528, event_529, event_530, event_531.

Evidence resolutions:
- message_04: scoped income amendment Quote: Your temporary monthly pay is EUR 1037.52. The reduced amount continues for the next payroll.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|EUR\|regular payroll | 1441 EUR (constant_or_income_policy) | monthly | event_439, event_447, event_455, event_463, event_471 | none |
| debit\|cloud_storage\|EUR\|shared storage plan | 5 EUR (constant_or_income_policy) | monthly | event_443, event_451, event_459, event_467, event_475 | none |
| debit\|dining\|EUR\|variable category spending | 54.09 EUR (upper_quartile_latest_12) | 7 days | event_532, event_533, event_534, event_535, event_536, event_537, event_538, event_539, event_540, event_541, event_542, event_543, event_544, event_545, event_546, event_547, event_548, event_549, event_550, event_551, event_552, event_553, event_554, event_555, event_556 | none |
| debit\|entertainment\|EUR\|monthly entertainment spend | 37.36 EUR (upper_quartile_latest_12) | monthly | event_446, event_454, event_462, event_470, event_478 | none |
| debit\|groceries\|EUR\|variable category spending | 51.4 EUR (upper_quartile_latest_12) | 10 days | event_479, event_480, event_481, event_482, event_483, event_484, event_485, event_486, event_487, event_488, event_489, event_490, event_491, event_492, event_493, event_494, event_495, event_496 | none |
| debit\|insurance\|EUR\|vehicle insurance premium | 26 EUR (constant_or_income_policy) | monthly | event_442, event_450, event_458, event_466, event_474 | none |
| debit\|rent\|EUR\|monthly rent | 254.1 EUR (constant_or_income_policy) | monthly | event_440, event_448, event_456, event_464, event_472 | none |
| debit\|shopping\|EUR\|household shopping | 41.44 EUR (upper_quartile_latest_12) | monthly | event_445, event_453, event_461, event_469, event_477 | none |
| debit\|streaming\|EUR\|family streaming plan | 19 EUR (constant_or_income_policy) | monthly | event_444, event_452, event_460, event_468, event_476 | none |
| debit\|transport\|EUR\|variable category spending | 30.82 EUR (upper_quartile_latest_12) | 5 days | event_497, event_498, event_499, event_500, event_501, event_502, event_503, event_504, event_505, event_506, event_507, event_508, event_509, event_510, event_511, event_512, event_513, event_514, event_515, event_516, event_517, event_518, event_519, event_520, event_521, event_522, event_523, event_524, event_525, event_526, event_527, event_528, event_529, event_530, event_531 | none |
| debit\|utilities\|EUR\|water and power payment | 58.34 EUR (upper_quartile_latest_12) | monthly | event_441, event_449, event_457, event_465, event_473 | none |

Candidate audit: 4 candidates; 4 have rejection/ranking reasons. All reasons and schedules are retained in JSON.
- full_payment: reserve breach or unquantified mandatory commitment
- wait: misses completion deadline
- full_payment: reserve breach or unquantified mandatory commitment

PR selected plan is unsafe even under its own ledger: minimum 777.695 versus required 800.0. It uses an impermissible reserve tolerance.

## request_07

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | affordable_with_plan | affordable_with_plan | yes |
| amount_safe_to_pay | 84037.03 | 87170.56 | no |
| earliest_date_for_full_payment | 2024-11-23 | 2024-10-23 | no |
| payment_plan | 2024-09-12:68432\|2024-10-10:68432\|2024-11-07:68432 | 2024-09-12:68432\|2024-10-10:68432\|2024-11-07:68432 | yes |
| recommended_payment_method | installments | installments | yes |
| spending_changes_needed | reduce_to:event_614:2835 | none | no |

message_05 changes the confirmed salary date to 2024-09-23. Both choose installments. The earliest lump-sum date differs by a month because later expenses still bind the full 90-day test.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (INR): opening 218945.56; lowest balance 177037.03 on 2024-09-20 after series:event_605; reserve 93000; remaining headroom 84037.03. Baseline safe amount after the request cap and evidence blockers: 84037.03. First safe full-payment date: 2024-11-23.

First PR ledger divergence: 2024-09-05 debit dining, ours 0, PR #8 6493.86. PR baseline lowest balance 185813.21 on 2024-09-13.
Affected source category records: event_606, event_607, event_608, event_609, event_610, event_611, event_612, event_613, event_614.

Evidence resolutions:
- message_05: scoped income amendment Quote: Your confirmed salary is now expected on 2024-09-23.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|INR\|regular payroll | 149000 INR (constant_or_income_policy) | monthly | event_558, event_563, event_568, event_573, event_578 | none |
| debit\|debt_repayment\|INR\|personal loan payment | 15650 INR (constant_or_income_policy) | monthly | event_561, event_566, event_571, event_576, event_581 | none |
| debit\|dining\|INR\|variable category spending | 6493.86 INR (upper_quartile_latest_12) | 21 days | event_606, event_607, event_608, event_609, event_610, event_611, event_612, event_613, event_614 | none |
| debit\|groceries\|INR\|variable category spending | 7849.54 INR (upper_quartile_latest_12) | 14 days | event_584, event_585, event_586, event_587, event_588, event_589, event_590, event_591, event_592, event_593, event_594, event_595, event_596 | none |
| debit\|music_subscription\|INR\|music subscription | 1005 INR (constant_or_income_policy) | monthly | event_562, event_567, event_572, event_577, event_582 | none |
| debit\|rent\|INR\|monthly rent | 34200 INR (constant_or_income_policy) | monthly | event_559, event_564, event_569, event_574, event_579, event_583 | none |
| debit\|transport\|INR\|variable category spending | 3690.82 INR (upper_quartile_latest_12) | 21 days | event_597, event_598, event_599, event_600, event_601, event_602, event_603, event_604, event_605 | none |
| debit\|utilities\|INR\|electricity bill | 7219.31 INR (upper_quartile_latest_12) | monthly | event_560, event_565, event_570, event_575, event_580 | none |

Candidate audit: 4 candidates; 3 have rejection/ranking reasons. All reasons and schedules are retained in JSON.
- installments: reserve breach or unquantified mandatory commitment
- installments: reserve breach or unquantified mandatory commitment
- installments: ranked below selected plan by contract priorities

## request_08

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | affordable_with_plan | affordable_later | no |
| amount_safe_to_pay | 274.84 | 284.57 | no |
| earliest_date_for_full_payment | <empty> | 2025-04-15 | no |
| payment_plan | 2025-04-15:996.6 | 2025-04-15:996.60 | yes |
| recommended_payment_method | full_payment | wait | no |
| spending_changes_needed | reduce_to:event_716:24.5\|stop:event_649\|stop:event_648 | none | no |

Both ledgers use confirmed salary EUR 1,422.85. Our April payment needs permitted spending changes; PR #8 waits without changes. The first expense date differs; no evidence establishes that its lower future spending is correct.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (EUR): opening 1536.57; lowest balance 1074.84 on 2025-02-13 after series:event_716; reserve 800; remaining headroom 274.84. Baseline safe amount after the request cap and evidence blockers: 274.84. First safe full-payment date: <empty>.

First PR ledger divergence: 2025-02-07 debit groceries, ours 0, PR #8 48.0. PR baseline lowest balance 1075.4499999999998 on 2025-02-14.
Affected source category records: event_652, event_653, event_654, event_655, event_656, event_657, event_658, event_659, event_660, event_661, event_662, event_663, event_664, event_665, event_666, event_667, event_668, event_669, event_670, event_671, event_672, event_673, event_674, event_675, event_676, event_677.

Evidence resolutions:
- message_06: scoped income amendment Quote: Your next salary is reduced to EUR 1422.85.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|EUR\|regular payroll | 1422.85 EUR (constant_or_income_policy) | monthly | event_615, event_622, event_629, event_636, event_643 | none |
| debit\|debt_repayment\|EUR\|personal loan payment | 177 EUR (constant_or_income_policy) | monthly | event_619, event_626, event_633, event_640, event_647 | none |
| debit\|delivery_membership\|EUR\|grocery delivery membership | 24 EUR (constant_or_income_policy) | monthly | event_621, event_628, event_635, event_642, event_649 | none |
| debit\|dining\|EUR\|variable category spending | 56.05 EUR (upper_quartile_latest_12) | 14 days | event_704, event_705, event_706, event_707, event_708, event_709, event_710, event_711, event_712, event_713, event_714, event_715, event_716 | none |
| debit\|education\|EUR\|school fee payment | 89 EUR (constant_or_income_policy) | monthly | event_618, event_625, event_632, event_639, event_646 | none |
| debit\|groceries\|EUR\|variable category spending | 60.11 EUR (upper_quartile_latest_12) | 7 days | event_652, event_653, event_654, event_655, event_656, event_657, event_658, event_659, event_660, event_661, event_662, event_663, event_664, event_665, event_666, event_667, event_668, event_669, event_670, event_671, event_672, event_673, event_674, event_675, event_676, event_677 | none |
| debit\|music_subscription\|EUR\|music subscription | 14 EUR (constant_or_income_policy) | monthly | event_620, event_627, event_634, event_641, event_648 | none |
| debit\|rent\|EUR\|apartment rent transfer | 467.5 EUR (constant_or_income_policy) | monthly | event_616, event_623, event_630, event_637, event_644, event_650 | none |
| debit\|transport\|EUR\|variable category spending | 41.57 EUR (upper_quartile_latest_12) | 7 days | event_678, event_679, event_680, event_681, event_682, event_683, event_684, event_685, event_686, event_687, event_688, event_689, event_690, event_691, event_692, event_693, event_694, event_695, event_696, event_697, event_698, event_699, event_700, event_701, event_702, event_703 | none |
| debit\|utilities\|EUR\|municipal utilities | 80.9 EUR (upper_quartile_latest_12) | monthly | event_617, event_624, event_631, event_638, event_645, event_651 | none |

Candidate audit: 9 candidates; 8 have rejection/ranking reasons. All reasons and schedules are retained in JSON.
- full_payment: reserve breach or unquantified mandatory commitment
- full_payment: reserve breach or unquantified mandatory commitment
- full_payment: reserve breach or unquantified mandatory commitment

## request_09

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | affordable_now | affordable_now | yes |
| amount_safe_to_pay | 166.61 | 166.61 | yes |
| earliest_date_for_full_payment | 2026-07-04 | 2026-07-04 | yes |
| payment_plan | 2026-07-04:166.61 | 2026-07-04:166.61 | yes |
| recommended_payment_method | full_payment | full_payment | yes |
| spending_changes_needed | none | none | yes |

All six fields match. The requested amount is well below baseline headroom.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (EUR): opening 2231.1; lowest balance 2164.26 on 2026-07-06 after series:event_748; reserve 600; remaining headroom 1564.26. Baseline safe amount after the request cap and evidence blockers: 166.61. First safe full-payment date: 2026-07-04.

First PR ledger divergence: 2026-07-06 debit dining, ours 0, PR #8 29.16. PR baseline lowest balance 1847.99 on 2026-09-19.
Affected source category records: event_780, event_781, event_782, event_783, event_784, event_785, event_786, event_787, event_788.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|EUR\|independent earnings day 20 | 355.99 EUR (constant_or_income_policy) | monthly | event_718, event_725, event_732, event_739, event_746 | none |
| credit\|salary\|EUR\|independent earnings day 7 | 488.8 EUR (constant_or_income_policy) | monthly | event_717, event_724, event_731, event_738, event_745 | none |
| debit\|cloud_storage\|EUR\|cloud storage plan | 5 EUR (constant_or_income_policy) | monthly | event_721, event_728, event_735, event_742, event_749 | none |
| debit\|dining\|EUR\|variable category spending | 32.86 EUR (upper_quartile_latest_12) | 21 days | event_780, event_781, event_782, event_783, event_784, event_785, event_786, event_787, event_788 | none |
| debit\|groceries\|EUR\|variable category spending | 51.03 EUR (upper_quartile_latest_12) | 10 days | event_753, event_754, event_755, event_756, event_757, event_758, event_759, event_760, event_761, event_762, event_763, event_764, event_765, event_766, event_767, event_768, event_769, event_770 | none |
| debit\|rent\|EUR\|monthly rent | 211.2 EUR (constant_or_income_policy) | monthly | event_719, event_726, event_733, event_740, event_747, event_752 | none |
| debit\|shopping\|EUR\|household shopping | 28.32 EUR (upper_quartile_latest_12) | monthly | event_723, event_730, event_737, event_744, event_751 | none |
| debit\|streaming\|EUR\|video streaming plan | 20 EUR (constant_or_income_policy) | monthly | event_722, event_729, event_736, event_743, event_750 | none |
| debit\|transport\|EUR\|variable category spending | 27.2 EUR (upper_quartile_latest_12) | 21 days | event_771, event_772, event_773, event_774, event_775, event_776, event_777, event_778, event_779 | none |
| debit\|utilities\|EUR\|water and power payment | 66.84 EUR (upper_quartile_latest_12) | monthly | event_720, event_727, event_734, event_741, event_748 | none |

Candidate audit: 1 candidates; 0 have rejection/ranking reasons. All reasons and schedules are retained in JSON.

## request_10

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | not_affordable | not_affordable | yes |
| amount_safe_to_pay | 0 | 12700 | no |
| earliest_date_for_full_payment | <empty> | <empty> | yes |
| payment_plan | none | none | yes |
| recommended_payment_method | not_recommended | not_recommended | yes |
| spending_changes_needed | none | none | yes |

message_07 says the QuickCrew payout remains pending. Excluding it leaves a future baseline shortfall, so positive capacity is uncertifiable under the retained forecast.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (INR): opening 750155; lowest balance 161057.93 on 2025-03-03 after series:event_840; reserve 225400; remaining headroom -64342.07. Baseline safe amount after the request cap and evidence blockers: 0. First safe full-payment date: <empty>.

First PR ledger divergence: 2024-12-06 debit transport, ours 6359.49, PR #8 0. PR baseline lowest balance 347800.6399999999 on 2025-03-03.
Affected source category records: event_867, event_868, event_869, event_870, event_871, event_872, event_873, event_874, event_875, event_876, event_877, event_878, event_879, event_880, event_881, event_882, event_883, event_884, event_885, event_886, event_887, event_888, event_889, event_890, event_891.

Evidence resolutions:
- message_07: unsettled credit excluded Quote: The next QuickCrew payout is still pending.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|INR\|driver platform payout | 47802.51 INR (constant_or_income_policy) | 16 days | event_821, event_829, event_831, event_839 | none |
| debit\|delivery_membership\|INR\|delivery service plan | 1895 INR (constant_or_income_policy) | monthly | event_796, event_806, event_816, event_826, event_836 | none |
| debit\|dining\|INR\|variable category spending | 9621.2 INR (upper_quartile_latest_12) | 14 days | event_892, event_893, event_894, event_895, event_896, event_897, event_898, event_899, event_900, event_901, event_902, event_903, event_904 | none |
| debit\|entertainment\|INR\|cinema and events | 4770.41 INR (upper_quartile_latest_12) | monthly | event_798, event_808, event_818, event_828, event_838 | none |
| debit\|groceries\|INR\|variable category spending | 12092.24 INR (upper_quartile_latest_12) | 7 days | event_841, event_842, event_843, event_844, event_845, event_846, event_847, event_848, event_849, event_850, event_851, event_852, event_853, event_854, event_855, event_856, event_857, event_858, event_859, event_860, event_861, event_862, event_863, event_864, event_865, event_866 | none |
| debit\|gym\|INR\|community fitness plan | 4860 INR (constant_or_income_policy) | monthly | event_797, event_807, event_817, event_827, event_837 | none |
| debit\|music_subscription\|INR\|music subscription | 2800 INR (constant_or_income_policy) | monthly | event_795, event_805, event_815, event_825, event_835 | none |
| debit\|rent\|INR\|monthly rent | 69100 INR (constant_or_income_policy) | monthly | event_793, event_803, event_813, event_823, event_833, event_840 | none |
| debit\|transport\|INR\|variable category spending | 6359.49 INR (upper_quartile_latest_12) | 7 days | event_867, event_868, event_869, event_870, event_871, event_872, event_873, event_874, event_875, event_876, event_877, event_878, event_879, event_880, event_881, event_882, event_883, event_884, event_885, event_886, event_887, event_888, event_889, event_890, event_891 | none |
| debit\|utilities\|INR\|electricity and water bill | 17771.13 INR (upper_quartile_latest_12) | monthly | event_794, event_804, event_814, event_824, event_834 | none |

Candidate audit: 0 candidates; 0 have rejection/ranking reasons. All reasons and schedules are retained in JSON.

## request_11

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | affordable_later | affordable_with_plan | no |
| amount_safe_to_pay | 11527136.55 | 12510645 | no |
| earliest_date_for_full_payment | 2025-05-15 | 2025-07-15 | no |
| payment_plan | 2025-05-15:13110000 | 2025-05-03:13110000 | no |
| recommended_payment_method | wait | full_payment | no |
| spending_changes_needed | none | reduce_to:event_989:665950 | no |

message_08 explicitly confirms base salary IDR 38,760,000 and excludes unapproved commission. PR #8 instead projects the historical 23,256,000 salary. Its immediate-pay result also breaches its own reserve. These are comparison-implementation defects; our safe wait recommendation must not be replaced merely to match.

Classification: comparison_implementation_reserve_violation, recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (IDR): opening 63531795; lowest balance 45667736.55 on 2025-05-14 after series:event_989; reserve 34140600; remaining headroom 11527136.55. Baseline safe amount after the request cap and evidence blockers: 11527136.55. First safe full-payment date: 2025-05-15.

First PR ledger divergence: 2025-05-05 debit groceries, ours 0, PR #8 1679473.8050000002. PR baseline lowest balance 42741582.65500001 on 2025-07-14.
Affected source category records: event_950, event_951, event_952, event_953, event_954, event_955, event_956, event_957, event_958, event_959, event_960, event_961, event_962, event_963, event_964, event_965, event_966, event_967.

Evidence resolutions:
- message_08: scoped income amendment Quote: Gaji pokok yang dikonfirmasi adalah IDR 38760000.
- message_08: unsettled credit excluded Quote: Komisi dari transaksi yang masih berjalan belum disetujui.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|IDR\|regular payroll | 23256000 IDR (constant_or_income_policy) | monthly | event_905, event_914, event_923, event_932, event_941 | none |
| debit\|cloud_storage\|IDR\|cloud storage plan | 168150 IDR (constant_or_income_policy) | monthly | event_913, event_922, event_931, event_940, event_949 | none |
| debit\|dining\|IDR\|variable category spending | 1503635.49 IDR (upper_quartile_latest_12) | 21 days | event_981, event_982, event_983, event_984, event_985, event_986, event_987, event_988, event_989 | none |
| debit\|education\|IDR\|child education fee | 2544100 IDR (constant_or_income_policy) | monthly | event_910, event_919, event_928, event_937, event_946 | none |
| debit\|entertainment\|IDR\|games and recreation | 1674887.61 IDR (upper_quartile_latest_12) | monthly | event_912, event_921, event_930, event_939, event_948 | none |
| debit\|groceries\|IDR\|variable category spending | 1590529.64 IDR (upper_quartile_latest_12) | 10 days | event_950, event_951, event_952, event_953, event_954, event_955, event_956, event_957, event_958, event_959, event_960, event_961, event_962, event_963, event_964, event_965, event_966, event_967 | none |
| debit\|healthcare\|IDR\|regular medicine purchase | 3118089.32 IDR (upper_quartile_latest_12) | monthly | event_911, event_920, event_929, event_938, event_947 | none |
| debit\|housing\|IDR\|home association fee | 2954500 IDR (constant_or_income_policy) | monthly | event_907, event_916, event_925, event_934, event_943 | none |
| debit\|insurance\|IDR\|vehicle insurance premium | 1881000 IDR (constant_or_income_policy) | monthly | event_909, event_918, event_927, event_936, event_945 | none |
| debit\|transport\|IDR\|variable category spending | 1212904.33 IDR (upper_quartile_latest_12) | 14 days | event_968, event_969, event_970, event_971, event_972, event_973, event_974, event_975, event_976, event_977, event_978, event_979, event_980 | none |
| debit\|utilities\|IDR\|municipal utilities | 2891149.67 IDR (upper_quartile_latest_12) | monthly | event_908, event_917, event_926, event_935, event_944 | none |

Candidate audit: 16 candidates; 15 have rejection/ranking reasons. All reasons and schedules are retained in JSON.
- full_payment: reserve breach or unquantified mandatory commitment
- full_payment: reserve breach or unquantified mandatory commitment
- full_payment: ranked below selected plan by contract priorities

PR selected plan is unsafe even under its own ledger: minimum 30626743.635000005 versus required 34140600.0. It uses an impermissible reserve tolerance.

## request_12

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | not_affordable | affordable_with_plan | no |
| amount_safe_to_pay | 55171.93 | 65164 | no |
| earliest_date_for_full_payment | <empty> | 2026-04-05 | no |
| payment_plan | none | 2026-04-19:22590.19\|2026-05-20:22590.19\|2026-06-20:22590.19 | no |
| recommended_payment_method | not_recommended | installments | no |
| spending_changes_needed | none | none | yes |

message_09 says the seasonal contract ended and no renewal is confirmed. Both ledgers exclude future income. The first difference is the utility estimate (3,708.19 versus 3,606.20); aggregate future outgoings determine whether the supplied installments fit. The estimator remains unchanged.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (ZAR): opening 193089.89; lowest balance 98371.93 on 2026-07-01 after series:event_1018; reserve 43200; remaining headroom 55171.93. Baseline safe amount after the request cap and evidence blockers: 55171.93. First safe full-payment date: <empty>.

First PR ledger divergence: 2026-04-05 debit utilities, ours 3708.19, PR #8 3606.2. PR baseline lowest balance 118307.84000000008 on 2026-07-01.
Affected source category records: event_992, event_998, event_1004, event_1009, event_1014.

Evidence resolutions:
- message_09: income target/date unresolved; no invented income Quote: The current seasonal contract has ended.
- message_09: income is not confirmed Quote: No off-season income or renewal has been confirmed.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| debit\|cloud_storage\|ZAR\|shared storage plan | 447.7 ZAR (constant_or_income_policy) | monthly | event_993, event_999, event_1005, event_1010, event_1015 | none |
| debit\|dining\|ZAR\|variable category spending | 2452.07 ZAR (upper_quartile_latest_12) | 21 days | event_1046, event_1047, event_1048, event_1049, event_1050, event_1051, event_1052, event_1053, event_1054 | none |
| debit\|groceries\|ZAR\|variable category spending | 2448 ZAR (upper_quartile_latest_12) | 10 days | event_1019, event_1020, event_1021, event_1022, event_1023, event_1024, event_1025, event_1026, event_1027, event_1028, event_1029, event_1030, event_1031, event_1032, event_1033, event_1034, event_1035, event_1036 | none |
| debit\|rent\|ZAR\|monthly rent | 11792 ZAR (constant_or_income_policy) | monthly | event_991, event_997, event_1003, event_1008, event_1013, event_1018 | none |
| debit\|shopping\|ZAR\|monthly shopping spend | 1267.67 ZAR (upper_quartile_latest_12) | monthly | event_995, event_1001, event_1007, event_1012, event_1017 | none |
| debit\|streaming\|ZAR\|family streaming plan | 1504.8 ZAR (constant_or_income_policy) | monthly | event_994, event_1000, event_1006, event_1011, event_1016 | none |
| debit\|transport\|ZAR\|variable category spending | 1679.15 ZAR (upper_quartile_latest_12) | 21 days | event_1037, event_1038, event_1039, event_1040, event_1041, event_1042, event_1043, event_1044, event_1045 | none |
| debit\|utilities\|ZAR\|water and power payment | 3708.19 ZAR (upper_quartile_latest_12) | monthly | event_992, event_998, event_1004, event_1009, event_1014 | none |

Candidate audit: 8 candidates; 8 have rejection/ranking reasons. All reasons and schedules are retained in JSON.
- installments: reserve breach or unquantified mandatory commitment
- installments: reserve breach or unquantified mandatory commitment
- installments: reserve breach or unquantified mandatory commitment

## request_13

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | not_affordable | affordable_later | no |
| amount_safe_to_pay | 433.54 | 433.4 | no |
| earliest_date_for_full_payment | <empty> | 2024-05-15 | no |
| payment_plan | none | 2024-05-15:941.60 | no |
| recommended_payment_method | not_recommended | wait | no |
| spending_changes_needed | none | none | yes |

Our safe amount differs from the sample by only EUR 0.14, but the sample May 15 payment breaches a later reserve under our ledger. PR #8 reports capacity EUR 904.04, far from the sample EUR 433.40, despite matching its wait method. A matching method does not validate its expense forecast.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (EUR): opening 2789.52; lowest balance 1733.54 on 2024-05-14 after series:event_1121; reserve 1300; remaining headroom 433.54. Baseline safe amount after the request cap and evidence blockers: 433.54. First safe full-payment date: <empty>.

First PR ledger divergence: 2024-03-12 debit groceries, ours 98.36, PR #8 0. PR baseline lowest balance 2204.039999999999 on 2024-05-14.
Affected source category records: event_1096, event_1097, event_1098, event_1099, event_1100, event_1101, event_1102, event_1103, event_1104, event_1105, event_1106, event_1107, event_1108, event_1109, event_1110, event_1111, event_1112, event_1113, event_1114, event_1115, event_1116, event_1117, event_1118, event_1119, event_1120, event_1121.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|EUR\|primary household salary | 1343.54 EUR (constant_or_income_policy) | monthly | event_1055, event_1063, event_1071, event_1079, event_1087 | none |
| debit\|delivery_membership\|EUR\|delivery service plan | 21 EUR (constant_or_income_policy) | monthly | event_1060, event_1068, event_1076, event_1084, event_1091 | none |
| debit\|dining\|EUR\|variable category spending | 68.7 EUR (upper_quartile_latest_12) | 14 days | event_1148, event_1149, event_1150, event_1151, event_1152, event_1153, event_1154, event_1155, event_1156, event_1157, event_1158, event_1159, event_1160 | none |
| debit\|entertainment\|EUR\|local event tickets | 33.83 EUR (upper_quartile_latest_12) | monthly | event_1062, event_1070, event_1078, event_1086, event_1093 | none |
| debit\|groceries\|EUR\|variable category spending | 98.36 EUR (upper_quartile_latest_12) | 7 days | event_1096, event_1097, event_1098, event_1099, event_1100, event_1101, event_1102, event_1103, event_1104, event_1105, event_1106, event_1107, event_1108, event_1109, event_1110, event_1111, event_1112, event_1113, event_1114, event_1115, event_1116, event_1117, event_1118, event_1119, event_1120, event_1121 | none |
| debit\|gym\|EUR\|community fitness plan | 61 EUR (constant_or_income_policy) | monthly | event_1061, event_1069, event_1077, event_1085, event_1092 | none |
| debit\|music_subscription\|EUR\|music subscription | 29 EUR (constant_or_income_policy) | monthly | event_1059, event_1067, event_1075, event_1083, event_1090 | none |
| debit\|rent\|EUR\|shared housing rent | 622.6 EUR (constant_or_income_policy) | monthly | event_1057, event_1065, event_1073, event_1081, event_1088, event_1094 | none |
| debit\|transport\|EUR\|variable category spending | 49.29 EUR (upper_quartile_latest_12) | 7 days | event_1122, event_1123, event_1124, event_1125, event_1126, event_1127, event_1128, event_1129, event_1130, event_1131, event_1132, event_1133, event_1134, event_1135, event_1136, event_1137, event_1138, event_1139, event_1140, event_1141, event_1142, event_1143, event_1144, event_1145, event_1146, event_1147 | none |
| debit\|utilities\|EUR\|water and power payment | 146.33 EUR (upper_quartile_latest_12) | monthly | event_1058, event_1066, event_1074, event_1082, event_1089, event_1095 | none |

Candidate audit: 8 candidates; 8 have rejection/ranking reasons. All reasons and schedules are retained in JSON.
- full_payment: reserve breach or unquantified mandatory commitment
- full_payment: reserve breach or unquantified mandatory commitment
- full_payment: reserve breach or unquantified mandatory commitment

## request_14

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | not_affordable | not_affordable | yes |
| amount_safe_to_pay | 0 | 597.74 | no |
| earliest_date_for_full_payment | <empty> | <empty> | yes |
| payment_plan | none | none | yes |
| recommended_payment_method | not_recommended | not_recommended | yes |
| spending_changes_needed | none | none | yes |

message_10 resumes salary but also announces mandatory recurring childcare with no amount or exact payment date. Ledger headroom excludes that unknown liability, so it cannot certify any positive payment. This is missing input evidence and an explicit release blocker.

Classification: missing_mandatory_evidence, recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (EUR): opening 3931.74; lowest balance 2779.00 on 2025-08-14 after series:event_1197; reserve 2200; remaining headroom 579.00. Baseline safe amount after the request cap and evidence blockers: 0. First safe full-payment date: <empty>.

First PR ledger divergence: 2025-08-08 debit groceries, ours 0, PR #8 123.41. PR baseline lowest balance 2836.41 on 2025-08-14.
Affected source category records: event_1201, event_1202, event_1203, event_1204, event_1205, event_1206, event_1207, event_1208, event_1209, event_1210, event_1211, event_1212, event_1213, event_1214, event_1215, event_1216, event_1217, event_1218, event_1219, event_1220, event_1221, event_1222, event_1223, event_1224, event_1225, event_1226.

Evidence resolutions:
- message_10: scoped income amendment Quote: Regular salary of EUR 2717 resumes on 2025-08-15.
- message_10: new mandatory commitment lacks amount/date; positive capacity cannot be certified Quote: A new recurring childcare payment begins in the same month.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|EUR\|regular payroll | 2717 EUR (constant_or_income_policy) | monthly | event_1162, event_1170, event_1192 | none |
| debit\|cloud_storage\|EUR\|cloud storage plan | 14 EUR (constant_or_income_policy) | monthly | event_1168, event_1176, event_1183, event_1190, event_1198 | none |
| debit\|debt_repayment\|EUR\|credit card repayment | 350 EUR (constant_or_income_policy) | monthly | event_1165, event_1173, event_1180, event_1187, event_1195 | none |
| debit\|family_support\|EUR\|family support payment | 226 EUR (constant_or_income_policy) | monthly | event_1167, event_1175, event_1182, event_1189, event_1197 | none |
| debit\|groceries\|EUR\|variable category spending | 123.41 EUR (upper_quartile_latest_12) | 7 days | event_1201, event_1202, event_1203, event_1204, event_1205, event_1206, event_1207, event_1208, event_1209, event_1210, event_1211, event_1212, event_1213, event_1214, event_1215, event_1216, event_1217, event_1218, event_1219, event_1220, event_1221, event_1222, event_1223, event_1224, event_1225, event_1226 | none |
| debit\|healthcare\|EUR\|family healthcare expense | 92.65 EUR (upper_quartile_latest_12) | monthly | event_1166, event_1174, event_1181, event_1188, event_1196 | none |
| debit\|rent\|EUR\|monthly rent | 688.6 EUR (constant_or_income_policy) | monthly | event_1163, event_1171, event_1178, event_1185, event_1193, event_1200 | none |
| debit\|shopping\|EUR\|online retail purchases | 137.03 EUR (upper_quartile_latest_12) | monthly | event_1169, event_1177, event_1184, event_1191, event_1199 | none |
| debit\|transport\|EUR\|variable category spending | 55.96 EUR (upper_quartile_latest_12) | 14 days | event_1227, event_1228, event_1229, event_1230, event_1231, event_1232, event_1233, event_1234, event_1235, event_1236, event_1237, event_1238, event_1239 | none |
| debit\|utilities\|EUR\|energy provider bill | 153.69 EUR (upper_quartile_latest_12) | monthly | event_1164, event_1172, event_1179, event_1186, event_1194 | none |

Candidate audit: 0 candidates; 0 have rejection/ranking reasons. All reasons and schedules are retained in JSON.

## request_15

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | not_affordable | not_affordable | yes |
| amount_safe_to_pay | 0 | 83.05 | no |
| earliest_date_for_full_payment | <empty> | <empty> | yes |
| payment_plan | none | none | yes |
| recommended_payment_method | not_recommended | not_recommended | yes |
| spending_changes_needed | none | none | yes |

message_11 confirms the first salary on January 15. The retained expense ledger breaches reserve on January 14. A later confirmed credit cannot fund that earlier shortfall.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (EUR): opening 1770.05; lowest balance 1181.54 on 2026-01-14 after series:event_1322; reserve 1200; remaining headroom -18.46. Baseline safe amount after the request cap and evidence blockers: 0. First safe full-payment date: <empty>.

First PR ledger divergence: 2026-01-06 debit groceries, ours 64.42, PR #8 0. PR baseline lowest balance 1337.11 on 2026-01-13.
Affected source category records: event_1273, event_1274, event_1275, event_1276, event_1277, event_1278, event_1279, event_1280, event_1281, event_1282, event_1283, event_1284, event_1285, event_1286, event_1287, event_1288, event_1289, event_1290, event_1291, event_1292, event_1293, event_1294, event_1295, event_1296, event_1297.

Evidence resolutions:
- message_11: scoped income amendment Quote: Your first salary will be EUR 1661. The confirmed credit date is 2026-01-15.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|EUR\|first job payroll | 1661 EUR (constant_or_income_policy) | monthly | event_1258, event_1265 | none |
| debit\|debt_repayment\|EUR\|credit card repayment | 84 EUR (constant_or_income_policy) | monthly | event_1243, event_1249, event_1255, event_1262, event_1269 | none |
| debit\|delivery_membership\|EUR\|food delivery membership | 27 EUR (constant_or_income_policy) | monthly | event_1245, event_1251, event_1257, event_1264, event_1271 | none |
| debit\|dining\|EUR\|variable category spending | 45.13 EUR (upper_quartile_latest_12) | 14 days | event_1323, event_1324, event_1325, event_1326, event_1327, event_1328, event_1329, event_1330, event_1331, event_1332, event_1333, event_1334, event_1335 | none |
| debit\|education\|EUR\|school fee payment | 159 EUR (constant_or_income_policy) | monthly | event_1242, event_1248, event_1254, event_1261, event_1268 | none |
| debit\|groceries\|EUR\|variable category spending | 64.42 EUR (upper_quartile_latest_12) | 7 days | event_1273, event_1274, event_1275, event_1276, event_1277, event_1278, event_1279, event_1280, event_1281, event_1282, event_1283, event_1284, event_1285, event_1286, event_1287, event_1288, event_1289, event_1290, event_1291, event_1292, event_1293, event_1294, event_1295, event_1296, event_1297 | none |
| debit\|music_subscription\|EUR\|music subscription | 11 EUR (constant_or_income_policy) | monthly | event_1244, event_1250, event_1256, event_1263, event_1270 | none |
| debit\|rent\|EUR\|landlord standing order | 435.6 EUR (constant_or_income_policy) | monthly | event_1240, event_1246, event_1252, event_1259, event_1266, event_1272 | none |
| debit\|transport\|EUR\|variable category spending | 36.7 EUR (upper_quartile_latest_12) | 7 days | event_1298, event_1299, event_1300, event_1301, event_1302, event_1303, event_1304, event_1305, event_1306, event_1307, event_1308, event_1309, event_1310, event_1311, event_1312, event_1313, event_1314, event_1315, event_1316, event_1317, event_1318, event_1319, event_1320, event_1321, event_1322 | none |
| debit\|utilities\|EUR\|energy provider bill | 87.14 EUR (upper_quartile_latest_12) | monthly | event_1241, event_1247, event_1253, event_1260, event_1267 | none |

Candidate audit: 0 candidates; 0 have rejection/ranking reasons. All reasons and schedules are retained in JSON.

## request_16

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | affordable_now | affordable_now | yes |
| amount_safe_to_pay | 122500.00 | 122500 | yes |
| earliest_date_for_full_payment | 2023-08-12 | 2023-08-12 | yes |
| payment_plan | 2023-08-12:122500 | 2023-08-12:122500 | yes |
| recommended_payment_method | full_payment | full_payment | yes |
| spending_changes_needed | none | none | yes |

All six fields match. The issued rent amount and lease evidence remain source-bound; the amendment is not applied twice.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (INR): opening 362370; lowest balance 261916.40 on 2023-09-14 after series:event_1428; reserve 122400; remaining headroom 139516.40. Baseline safe amount after the request cap and evidence blockers: 122500.00. First safe full-payment date: 2023-08-12.

First PR ledger divergence: 2023-08-13 debit transport, ours 0, PR #8 4643.67. PR baseline lowest balance 304825.0900000001 on 2023-09-13.
Affected source category records: event_1403, event_1404, event_1405, event_1406, event_1407, event_1408, event_1409, event_1410, event_1411, event_1412, event_1413, event_1414, event_1415, event_1416, event_1417, event_1418, event_1419, event_1420, event_1421, event_1422, event_1423, event_1424, event_1425, event_1426, event_1427, event_1428.

Evidence resolutions:
- image_02: document role and settlement-date conditions
- message_12: informational; no additional cash Quote: The renewed lease increases monthly rent by 12%.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|INR\|regular payroll | 173000 INR (constant_or_income_policy) | monthly | event_1336, event_1343, event_1350, event_1357, event_1364 | none |
| debit\|cloud_storage\|INR\|cloud storage plan | 1055 INR (constant_or_income_policy) | monthly | event_1341, event_1348, event_1355, event_1362, event_1369, event_1375 | none |
| debit\|debt_repayment\|INR\|vehicle loan payment | 17750 INR (constant_or_income_policy) | monthly | event_1339, event_1346, event_1353, event_1360, event_1367, event_1373 | none |
| debit\|dining\|INR\|variable category spending | 5905.06 INR (upper_quartile_latest_12) | 14 days | event_1429, event_1430, event_1431, event_1432, event_1433, event_1434, event_1435, event_1436, event_1437, event_1438, event_1439, event_1440, event_1441 | none |
| debit\|groceries\|INR\|variable category spending | 7181.79 INR (upper_quartile_latest_12) | 7 days | event_1377, event_1378, event_1379, event_1380, event_1381, event_1382, event_1383, event_1384, event_1385, event_1386, event_1387, event_1388, event_1389, event_1390, event_1391, event_1392, event_1393, event_1394, event_1395, event_1396, event_1397, event_1398, event_1399, event_1400, event_1401, event_1402 | none |
| debit\|rent\|INR\|monthly rent | 57100 INR (constant_or_income_policy) | monthly | event_1337, event_1344, event_1351, event_1358, event_1365, event_1371 | none |
| debit\|shopping\|INR\|clothing and household items | 9807.5 INR (upper_quartile_latest_12) | monthly | event_1342, event_1349, event_1356, event_1363, event_1370, event_1376 | none |
| debit\|streaming\|INR\|video streaming plan | 3510 INR (constant_or_income_policy) | monthly | event_1340, event_1347, event_1354, event_1361, event_1368, event_1374 | none |
| debit\|transport\|INR\|variable category spending | 5067.66 INR (upper_quartile_latest_12) | 7 days | event_1403, event_1404, event_1405, event_1406, event_1407, event_1408, event_1409, event_1410, event_1411, event_1412, event_1413, event_1414, event_1415, event_1416, event_1417, event_1418, event_1419, event_1420, event_1421, event_1422, event_1423, event_1424, event_1425, event_1426, event_1427, event_1428 | none |
| debit\|utilities\|INR\|energy provider bill | 11173.73 INR (upper_quartile_latest_12) | monthly | event_1338, event_1345, event_1352, event_1359, event_1366, event_1372 | none |

Candidate audit: 1 candidates; 0 have rejection/ranking reasons. All reasons and schedules are retained in JSON.

## request_17

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | affordable_with_plan | affordable_with_plan | yes |
| amount_safe_to_pay | 237187.90 | 243849.58 | no |
| earliest_date_for_full_payment | 2026-04-15 | 2026-03-15 | no |
| payment_plan | 2026-03-01:95194.67\|2026-03-31:95194.67\|2026-04-30:95194.67 | 2026-03-01:95194.67\|2026-03-31:95194.67\|2026-04-30:95194.67 | yes |
| recommended_payment_method | installments | installments | yes |
| spending_changes_needed | reduce_to:event_1542:2935 | none | no |

image_03 supplies the document amount. The installment recommendation matches, but routine expense estimates change baseline capacity and the first safe lump-sum date. No alternate authoritative forecast is supplied.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (INR): opening 550379.58; lowest balance 403287.90 on 2026-03-14 after series:event_1529; reserve 166100; remaining headroom 237187.90. Baseline safe amount after the request cap and evidence blockers: 237187.90. First safe full-payment date: 2026-04-15.

First PR ledger divergence: 2026-03-03 debit groceries, ours 0, PR #8 7187.32. PR baseline lowest balance 416387.0299999999 on 2026-03-13.
Affected source category records: event_1478, event_1479, event_1480, event_1481, event_1482, event_1483, event_1484, event_1485, event_1486, event_1487, event_1488, event_1489, event_1490, event_1491, event_1492, event_1493, event_1494, event_1495, event_1496, event_1497, event_1498, event_1499, event_1500, event_1501, event_1502, event_1503, event_1545.

Evidence resolutions:
- image_03: document role and settlement-date conditions

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|INR\|regular payroll | 206000 INR (constant_or_income_policy) | monthly | event_1443, event_1450, event_1457, event_1464, event_1471 | none |
| debit\|debt_repayment\|INR\|credit card repayment | 30200 INR (constant_or_income_policy) | monthly | event_1447, event_1454, event_1461, event_1468, event_1475 | none |
| debit\|delivery_membership\|INR\|food delivery membership | 1675 INR (constant_or_income_policy) | monthly | event_1449, event_1456, event_1463, event_1470, event_1477 | none |
| debit\|dining\|INR\|variable category spending | 6688.81 INR (upper_quartile_latest_12) | 14 days | event_1530, event_1531, event_1532, event_1533, event_1534, event_1535, event_1536, event_1537, event_1538, event_1539, event_1540, event_1541, event_1542 | none |
| debit\|education\|INR\|course tuition | 13660 INR (constant_or_income_policy) | monthly | event_1446, event_1453, event_1460, event_1467, event_1474 | none |
| debit\|groceries\|INR\|variable category spending | 10873.47 INR (upper_quartile_latest_12) | 7 days | event_1478, event_1479, event_1480, event_1481, event_1482, event_1483, event_1484, event_1485, event_1486, event_1487, event_1488, event_1489, event_1490, event_1491, event_1492, event_1493, event_1494, event_1495, event_1496, event_1497, event_1498, event_1499, event_1500, event_1501, event_1502, event_1503 | none |
| debit\|music_subscription\|INR\|music subscription | 2055 INR (constant_or_income_policy) | monthly | event_1448, event_1455, event_1462, event_1469, event_1476 | none |
| debit\|rent\|INR\|apartment rent transfer | 49600 INR (constant_or_income_policy) | monthly | event_1444, event_1451, event_1458, event_1465, event_1472 | none |
| debit\|transport\|INR\|variable category spending | 5758.89 INR (upper_quartile_latest_12) | 7 days | event_1504, event_1505, event_1506, event_1507, event_1508, event_1509, event_1510, event_1511, event_1512, event_1513, event_1514, event_1515, event_1516, event_1517, event_1518, event_1519, event_1520, event_1521, event_1522, event_1523, event_1524, event_1525, event_1526, event_1527, event_1528, event_1529 | none |
| debit\|utilities\|INR\|municipal utilities | 9948.15 INR (upper_quartile_latest_12) | monthly | event_1445, event_1452, event_1459, event_1466, event_1473 | none |

Candidate audit: 8 candidates; 7 have rejection/ranking reasons. All reasons and schedules are retained in JSON.
- installments: reserve breach or unquantified mandatory commitment
- installments: reserve breach or unquantified mandatory commitment
- installments: reserve breach or unquantified mandatory commitment

## request_18

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | affordable_later | affordable_later | yes |
| amount_safe_to_pay | 507.26 | 462 | no |
| earliest_date_for_full_payment | 2026-09-15 | 2026-09-15 | yes |
| payment_plan | 2026-09-15:3246.1 | 2026-09-15:3246.10 | yes |
| recommended_payment_method | wait | wait | yes |
| spending_changes_needed | none | none | yes |

message_13 describes an internal transfer. Historical settled records are already in opening balance; no extra income is invented. Both wait until the same date; utility and routine expense assumptions differ.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (EUR): opening 2486; lowest balance 1907.26 on 2026-07-14 after series:event_1608; reserve 1400; remaining headroom 507.26. Baseline safe amount after the request cap and evidence blockers: 507.26. First safe full-payment date: 2026-09-15.

First PR ledger divergence: 2026-07-07 debit utilities, ours 121.67, PR #8 107.43. PR baseline lowest balance 2012.43 on 2026-07-12.
Affected source category records: event_1549, event_1555, event_1561, event_1567, event_1573.

Evidence resolutions:
- message_13: internal transfer pair ambiguous; no unrelated records suppressed Quote: The matching debit and credit came from a transfer between your two accounts.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|EUR\|regular payroll | 2310 EUR (constant_or_income_policy) | monthly | event_1547, event_1553, event_1559, event_1565, event_1571 | none |
| debit\|dining\|EUR\|variable category spending | 101.82 EUR (upper_quartile_latest_12) | 14 days | event_1609, event_1610, event_1611, event_1612, event_1613, event_1614, event_1615, event_1616, event_1617, event_1618, event_1619, event_1620, event_1621 | none |
| debit\|groceries\|EUR\|variable category spending | 108.09 EUR (upper_quartile_latest_12) | 10 days | event_1578, event_1579, event_1580, event_1581, event_1582, event_1583, event_1584, event_1585, event_1586, event_1587, event_1588, event_1589, event_1590, event_1591, event_1592, event_1593, event_1594, event_1595 | none |
| debit\|healthcare\|EUR\|clinic payment | 162.41 EUR (upper_quartile_latest_12) | monthly | event_1551, event_1557, event_1563, event_1569, event_1575 | none |
| debit\|housing\|EUR\|building maintenance payment | 167 EUR (constant_or_income_policy) | monthly | event_1548, event_1554, event_1560, event_1566, event_1572, event_1577 | none |
| debit\|insurance\|EUR\|household insurance | 68 EUR (constant_or_income_policy) | monthly | event_1550, event_1556, event_1562, event_1568, event_1574 | none |
| debit\|streaming\|EUR\|family streaming plan | 68 EUR (constant_or_income_policy) | monthly | event_1552, event_1558, event_1564, event_1570, event_1576 | none |
| debit\|transport\|EUR\|variable category spending | 50.57 EUR (upper_quartile_latest_12) | 14 days | event_1596, event_1597, event_1598, event_1599, event_1600, event_1601, event_1602, event_1603, event_1604, event_1605, event_1606, event_1607, event_1608 | none |
| debit\|utilities\|EUR\|energy provider bill | 121.67 EUR (upper_quartile_latest_12) | monthly | event_1549, event_1555, event_1561, event_1567, event_1573 | none |

Candidate audit: 12 candidates; 11 have rejection/ranking reasons. All reasons and schedules are retained in JSON.
- full_payment: reserve breach or unquantified mandatory commitment
- full_payment: reserve breach or unquantified mandatory commitment
- full_payment: ranked below selected plan by contract priorities

## request_19

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | affordable_with_plan | affordable_with_plan | yes |
| amount_safe_to_pay | 23528.45 | 28820 | no |
| earliest_date_for_full_payment | 2024-09-15 | 2024-09-15 | yes |
| payment_plan | 2024-09-04:23528.45\|2024-09-15:16131.55 | 2024-09-04:28820\|2024-09-15:10840 | no |
| recommended_payment_method | partial_payment | partial_payment | yes |
| spending_changes_needed | none | none | yes |

image_04 remains authoritative for its linked transaction. Both use partial payment. Because the first leg must equal baseline safe capacity, the amount difference necessarily changes both partial-payment legs.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (INR): opening 199545; lowest balance 116328.45 on 2024-09-14 after series:event_1661; reserve 92800; remaining headroom 23528.45. Baseline safe amount after the request cap and evidence blockers: 23528.45. First safe full-payment date: 2024-09-15.

First PR ledger divergence: 2024-09-04 debit groceries, ours 5146.94, PR #8 0. PR baseline lowest balance 130994.33000000002 on 2024-09-14.
Affected source category records: event_1662, event_1663, event_1664, event_1665, event_1666, event_1667, event_1668, event_1669, event_1670, event_1671, event_1672, event_1673, event_1674, event_1675, event_1676, event_1677, event_1678, event_1679, event_1680, event_1681, event_1682, event_1683, event_1684, event_1685, event_1686, event_1700.

Evidence resolutions:
- image_04: document role and settlement-date conditions

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|INR\|regular payroll | 131000 INR (constant_or_income_policy) | monthly | event_1622, event_1630, event_1638, event_1646, event_1654 | none |
| debit\|cloud_storage\|INR\|online backup subscription | 395 INR (constant_or_income_policy) | monthly | event_1628, event_1636, event_1644, event_1652, event_1660 | none |
| debit\|debt_repayment\|INR\|loan repayment | 11850 INR (constant_or_income_policy) | monthly | event_1625, event_1633, event_1641, event_1649, event_1657 | none |
| debit\|family_support\|INR\|childcare contribution | 12650 INR (constant_or_income_policy) | monthly | event_1627, event_1635, event_1643, event_1651, event_1659 | none |
| debit\|groceries\|INR\|variable category spending | 5146.94 INR (upper_quartile_latest_12) | 7 days | event_1662, event_1663, event_1664, event_1665, event_1666, event_1667, event_1668, event_1669, event_1670, event_1671, event_1672, event_1673, event_1674, event_1675, event_1676, event_1677, event_1678, event_1679, event_1680, event_1681, event_1682, event_1683, event_1684, event_1685, event_1686 | none |
| debit\|healthcare\|INR\|clinic payment | 8946.09 INR (upper_quartile_latest_12) | monthly | event_1626, event_1634, event_1642, event_1650, event_1658 | none |
| debit\|rent\|INR\|residential rent payment | 36100 INR (constant_or_income_policy) | monthly | event_1623, event_1631, event_1639, event_1647, event_1655 | none |
| debit\|shopping\|INR\|clothing and household items | 6069.58 INR (upper_quartile_latest_12) | monthly | event_1629, event_1637, event_1645, event_1653, event_1661 | none |
| debit\|transport\|INR\|variable category spending | 3432.81 INR (upper_quartile_latest_12) | 14 days | event_1687, event_1688, event_1689, event_1690, event_1691, event_1692, event_1693, event_1694, event_1695, event_1696, event_1697, event_1698, event_1699 | none |
| debit\|utilities\|INR\|municipal utilities | 6129.19 INR (upper_quartile_latest_12) | monthly | event_1624, event_1632, event_1640, event_1648, event_1656 | none |

Candidate audit: 8 candidates; 7 have rejection/ranking reasons. All reasons and schedules are retained in JSON.
- installments: ranked below selected plan by contract priorities
- partial_payment: ranked below selected plan by contract priorities
- installments: ranked below selected plan by contract priorities

## request_20

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | not_affordable | not_affordable | yes |
| amount_safe_to_pay | 7924.25 | 5400 | no |
| earliest_date_for_full_payment | <empty> | <empty> | yes |
| payment_plan | none | none | yes |
| recommended_payment_method | not_recommended | not_recommended | yes |
| spending_changes_needed | none | none | yes |

message_14 says the refund has not arrived, so it is excluded. Document evidence is retained. Both reject the purchase; the amount difference concerns routine expense headroom.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (INR): opening 102609.05; lowest balance 72424.25 on 2026-02-13 after series:event_1739; reserve 64500; remaining headroom 7924.25. Baseline safe amount after the request cap and evidence blockers: 7924.25. First safe full-payment date: <empty>.

First PR ledger divergence: 2026-02-09 debit dining, ours 0, PR #8 3803.95. PR baseline lowest balance 69814.61 on 2026-02-13.
Affected source category records: event_1775, event_1776, event_1777, event_1778, event_1779, event_1780, event_1781, event_1782, event_1783.

Evidence resolutions:
- image_05: document role and settlement-date conditions
- message_14: unsettled credit excluded Quote: Your refund has been initiated but has not reached your account yet.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|INR\|regular payroll | 108000 INR (constant_or_income_policy) | monthly | event_1701, event_1709, event_1717, event_1725, event_1733 | none |
| debit\|cloud_storage\|INR\|shared storage plan | 365 INR (constant_or_income_policy) | monthly | event_1708, event_1716, event_1724, event_1732, event_1740 | none |
| debit\|dining\|INR\|variable category spending | 3803.95 INR (upper_quartile_latest_12) | 21 days | event_1775, event_1776, event_1777, event_1778, event_1779, event_1780, event_1781, event_1782, event_1783 | none |
| debit\|education\|INR\|school fee payment | 8740 INR (constant_or_income_policy) | monthly | event_1705, event_1713, event_1721, event_1729, event_1737 | none |
| debit\|entertainment\|INR\|cinema and events | 2279.67 INR (upper_quartile_latest_12) | monthly | event_1707, event_1715, event_1723, event_1731, event_1739 | none |
| debit\|groceries\|INR\|variable category spending | 3796.24 INR (upper_quartile_latest_12) | 10 days | event_1744, event_1745, event_1746, event_1747, event_1748, event_1749, event_1750, event_1751, event_1752, event_1753, event_1754, event_1755, event_1756, event_1757, event_1758, event_1759, event_1760, event_1761 | none |
| debit\|healthcare\|INR\|family healthcare expense | 6648.5 INR (upper_quartile_latest_12) | monthly | event_1706, event_1714, event_1722, event_1730, event_1738 | none |
| debit\|housing\|INR\|home association fee | 7950 INR (constant_or_income_policy) | monthly | event_1702, event_1710, event_1718, event_1726, event_1734, event_1741 | none |
| debit\|insurance\|INR\|household insurance | 3290 INR (constant_or_income_policy) | monthly | event_1704, event_1712, event_1720, event_1728, event_1736, event_1743 | none |
| debit\|transport\|INR\|variable category spending | 3063.34 INR (upper_quartile_latest_12) | 14 days | event_1762, event_1763, event_1764, event_1765, event_1766, event_1767, event_1768, event_1769, event_1770, event_1771, event_1772, event_1773, event_1774 | none |
| debit\|utilities\|INR\|municipal utilities | 7977.68 INR (upper_quartile_latest_12) | monthly | event_1703, event_1711, event_1719, event_1727, event_1735, event_1742 | none |

Candidate audit: 8 candidates; 8 have rejection/ranking reasons. All reasons and schedules are retained in JSON.
- full_payment: reserve breach or unquantified mandatory commitment
- full_payment: reserve breach or unquantified mandatory commitment
- full_payment: reserve breach or unquantified mandatory commitment

## request_21

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | affordable_now | affordable_with_plan | no |
| amount_safe_to_pay | 1574.40 | 1543.35 | no |
| earliest_date_for_full_payment | 2026-04-03 | 2026-04-15 | no |
| payment_plan | 2026-04-03:1574.4 | 2026-04-03:1574.40 | yes |
| recommended_payment_method | full_payment | full_payment | yes |
| spending_changes_needed | none | stop:event_1815\|reduce_to:event_1816:23.50 | no |

Our baseline has USD 1,664.35 headroom against a USD 1,574.40 request, so full payment now needs no changes. PR #8 has USD 1,543.26 baseline capacity and proposes spending cuts. The ledgers differ before any recommendation; this remains an expense/calendar assumption.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (USD): opening 3911.35; lowest balance 3464.35 on 2026-04-12 after series:event_1817; reserve 1800; remaining headroom 1664.35. Baseline safe amount after the request cap and evidence blockers: 1574.40. First safe full-payment date: 2026-04-03.

First PR ledger divergence: 2026-04-05 debit groceries, ours 0, PR #8 85.9. PR baseline lowest balance 3343.2599999999998 on 2026-04-12.
Affected source category records: event_1819, event_1820, event_1821, event_1822, event_1823, event_1824, event_1825, event_1826, event_1827, event_1828, event_1829, event_1830, event_1831, event_1832, event_1833, event_1834, event_1835, event_1836.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|USD\|regular payroll | 2256 USD (constant_or_income_policy) | monthly | event_1788, event_1794, event_1800, event_1806, event_1812 | none |
| debit\|cloud_storage\|USD\|online backup subscription | 11 USD (constant_or_income_policy) | monthly | event_1791, event_1797, event_1803, event_1809, event_1815 | none |
| debit\|dining\|USD\|variable category spending | 97.67 USD (upper_quartile_latest_12) | 21 days | event_1846, event_1847, event_1848, event_1849, event_1850, event_1851, event_1852, event_1853, event_1854 | none |
| debit\|groceries\|USD\|variable category spending | 85.9 USD (upper_quartile_latest_12) | 10 days | event_1819, event_1820, event_1821, event_1822, event_1823, event_1824, event_1825, event_1826, event_1827, event_1828, event_1829, event_1830, event_1831, event_1832, event_1833, event_1834, event_1835, event_1836 | none |
| debit\|rent\|USD\|residential rent payment | 718.8 USD (constant_or_income_policy) | monthly | event_1789, event_1795, event_1801, event_1807, event_1813, event_1818 | none |
| debit\|shopping\|USD\|monthly shopping spend | 126.38 USD (upper_quartile_latest_12) | monthly | event_1793, event_1799, event_1805, event_1811, event_1817 | none |
| debit\|streaming\|USD\|streaming subscription | 47 USD (constant_or_income_policy) | monthly | event_1792, event_1798, event_1804, event_1810, event_1816 | none |
| debit\|transport\|USD\|variable category spending | 47.84 USD (upper_quartile_latest_12) | 21 days | event_1837, event_1838, event_1839, event_1840, event_1841, event_1842, event_1843, event_1844, event_1845 | none |
| debit\|utilities\|USD\|municipal utilities | 123.72 USD (upper_quartile_latest_12) | monthly | event_1790, event_1796, event_1802, event_1808, event_1814 | none |

Candidate audit: 22 candidates; 21 have rejection/ranking reasons. All reasons and schedules are retained in JSON.
- full_payment: ranked below selected plan by contract priorities
- full_payment: ranked below selected plan by contract priorities
- full_payment: ranked below selected plan by contract priorities

## request_22

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | affordable_with_plan | affordable_with_plan | yes |
| amount_safe_to_pay | 451.89 | 475.46 | no |
| earliest_date_for_full_payment | 2025-02-15 | 2025-01-15 | no |
| payment_plan | 2024-12-08:253.59\|2025-01-05:253.59\|2025-02-02:253.59 | 2024-12-08:253.59\|2025-01-05:253.59\|2025-02-02:253.59 | yes |
| recommended_payment_method | installments | installments | yes |
| spending_changes_needed | stop:event_1890\|stop:event_1892 | none | no |

message_15 reports unrealized portfolio value, which is not available cash. Both choose installments. Routine expense estimates determine the lower capacity and later lump-sum date in our ledger.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (EUR): opening 1132.46; lowest balance 951.89 on 2024-12-14 after series:event_1891; reserve 500; remaining headroom 451.89. Baseline safe amount after the request cap and evidence blockers: 451.89. First safe full-payment date: 2025-02-15.

First PR ledger divergence: 2024-12-05 debit transport, ours 15.65, PR #8 0. PR baseline lowest balance 1000.48 on 2024-12-14.
Affected source category records: event_1921, event_1922, event_1923, event_1924, event_1925, event_1926, event_1927, event_1928, event_1929, event_1930, event_1931, event_1932, event_1933, event_1934, event_1935, event_1936, event_1937, event_1938, event_1939, event_1940, event_1941, event_1942, event_1943, event_1944, event_1945.

Evidence resolutions:
- message_15: informational; no additional cash Quote: Your portfolio’s displayed market value has increased substantially.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|EUR\|regular payroll | 616 EUR (constant_or_income_policy) | monthly | event_1859, event_1866, event_1873, event_1880, event_1887 | none |
| debit\|delivery_membership\|EUR\|food delivery membership | 5 EUR (constant_or_income_policy) | monthly | event_1863, event_1870, event_1877, event_1884, event_1891 | none |
| debit\|dining\|EUR\|variable category spending | 18.41 EUR (upper_quartile_latest_12) | 14 days | event_1946, event_1947, event_1948, event_1949, event_1950, event_1951, event_1952, event_1953, event_1954, event_1955, event_1956, event_1957, event_1958 | none |
| debit\|entertainment\|EUR\|weekend entertainment | 22.03 EUR (upper_quartile_latest_12) | monthly | event_1865, event_1872, event_1879, event_1886, event_1893 | none |
| debit\|groceries\|EUR\|variable category spending | 27.33 EUR (upper_quartile_latest_12) | 7 days | event_1895, event_1896, event_1897, event_1898, event_1899, event_1900, event_1901, event_1902, event_1903, event_1904, event_1905, event_1906, event_1907, event_1908, event_1909, event_1910, event_1911, event_1912, event_1913, event_1914, event_1915, event_1916, event_1917, event_1918, event_1919, event_1920 | none |
| debit\|gym\|EUR\|gym membership | 17 EUR (constant_or_income_policy) | monthly | event_1864, event_1871, event_1878, event_1885, event_1892 | none |
| debit\|music_subscription\|EUR\|music service subscription | 6 EUR (constant_or_income_policy) | monthly | event_1862, event_1869, event_1876, event_1883, event_1890 | none |
| debit\|rent\|EUR\|apartment rent transfer | 178.2 EUR (constant_or_income_policy) | monthly | event_1860, event_1867, event_1874, event_1881, event_1888, event_1894 | none |
| debit\|transport\|EUR\|variable category spending | 15.65 EUR (upper_quartile_latest_12) | 7 days | event_1921, event_1922, event_1923, event_1924, event_1925, event_1926, event_1927, event_1928, event_1929, event_1930, event_1931, event_1932, event_1933, event_1934, event_1935, event_1936, event_1937, event_1938, event_1939, event_1940, event_1941, event_1942, event_1943, event_1944, event_1945 | none |
| debit\|utilities\|EUR\|electricity and water bill | 32.53 EUR (upper_quartile_latest_12) | monthly | event_1861, event_1868, event_1875, event_1882, event_1889 | none |

Candidate audit: 4 candidates; 3 have rejection/ranking reasons. All reasons and schedules are retained in JSON.
- installments: reserve breach or unquantified mandatory commitment
- installments: reserve breach or unquantified mandatory commitment
- installments: reserve breach or unquantified mandatory commitment

## request_23

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | affordable_with_plan | affordable_later | no |
| amount_safe_to_pay | 8022.15 | 9152 | no |
| earliest_date_for_full_payment | <empty> | 2025-07-15 | no |
| payment_plan | 2025-07-15:38016 | 2025-07-15:38016 | yes |
| recommended_payment_method | full_payment | wait | no |
| spending_changes_needed | stop:event_2000 | none | no |

message_16 says the prize remains in processing. Both exclude it. Our July payment needs a subscription stop; PR #8 waits with no changes because its projected outgoings are lower. No settled prize or alternate expense facts justify changing our forecast.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (ZAR): opening 51957.9; lowest balance 35022.15 on 2025-05-14 after series:event_2027; reserve 27000; remaining headroom 8022.15. Baseline safe amount after the request cap and evidence blockers: 8022.15. First safe full-payment date: <empty>.

First PR ledger divergence: 2025-05-07 debit groceries, ours 1794.76, PR #8 0. PR baseline lowest balance 38917.43 on 2025-05-14.
Affected source category records: event_2003, event_2004, event_2005, event_2006, event_2007, event_2008, event_2009, event_2010, event_2011, event_2012, event_2013, event_2014, event_2015, event_2016, event_2017, event_2018, event_2019, event_2020, event_2021, event_2022, event_2023, event_2024, event_2025, event_2026, event_2027.

Evidence resolutions:
- message_16: unsettled credit excluded Quote: Your prize claim has been verified and is still in payment processing.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|ZAR\|regular payroll | 45760 ZAR (constant_or_income_policy) | monthly | event_1962, event_1970, event_1978, event_1986, event_1994 | none |
| debit\|cloud_storage\|ZAR\|cloud storage plan | 295.9 ZAR (constant_or_income_policy) | monthly | event_1968, event_1976, event_1984, event_1992, event_2000 | none |
| debit\|debt_repayment\|ZAR\|education loan instalment | 5852 ZAR (constant_or_income_policy) | monthly | event_1965, event_1973, event_1981, event_1989, event_1997 | none |
| debit\|family_support\|ZAR\|childcare contribution | 4270.2 ZAR (constant_or_income_policy) | monthly | event_1967, event_1975, event_1983, event_1991, event_1999 | none |
| debit\|groceries\|ZAR\|variable category spending | 1794.76 ZAR (upper_quartile_latest_12) | 7 days | event_2003, event_2004, event_2005, event_2006, event_2007, event_2008, event_2009, event_2010, event_2011, event_2012, event_2013, event_2014, event_2015, event_2016, event_2017, event_2018, event_2019, event_2020, event_2021, event_2022, event_2023, event_2024, event_2025, event_2026, event_2027 | none |
| debit\|healthcare\|ZAR\|clinic payment | 1377.89 ZAR (upper_quartile_latest_12) | monthly | event_1966, event_1974, event_1982, event_1990, event_1998 | none |
| debit\|rent\|ZAR\|shared housing rent | 15312 ZAR (constant_or_income_policy) | monthly | event_1963, event_1971, event_1979, event_1987, event_1995, event_2002 | none |
| debit\|shopping\|ZAR\|personal shopping | 1389.39 ZAR (upper_quartile_latest_12) | monthly | event_1969, event_1977, event_1985, event_1993, event_2001 | none |
| debit\|transport\|ZAR\|variable category spending | 968.71 ZAR (upper_quartile_latest_12) | 14 days | event_2028, event_2029, event_2030, event_2031, event_2032, event_2033, event_2034, event_2035, event_2036, event_2037, event_2038, event_2039, event_2040 | none |
| debit\|utilities\|ZAR\|electricity bill | 2877.85 ZAR (upper_quartile_latest_12) | monthly | event_1964, event_1972, event_1980, event_1988, event_1996 | none |

Candidate audit: 7 candidates; 6 have rejection/ranking reasons. All reasons and schedules are retained in JSON.
- full_payment: reserve breach or unquantified mandatory commitment
- full_payment: reserve breach or unquantified mandatory commitment
- full_payment: reserve breach or unquantified mandatory commitment

## request_24

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | not_affordable | not_affordable | yes |
| amount_safe_to_pay | 12960.25 | 13420 | no |
| earliest_date_for_full_payment | <empty> | <empty> | yes |
| payment_plan | none | none | yes |
| recommended_payment_method | not_recommended | not_recommended | yes |
| spending_changes_needed | none | none | yes |

message_17 confirms already-settled prize proceeds. They are represented in opening balance and are not deducted or added a second time. Both reject the request; remaining amount differences concern expense estimates.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (INR): opening 85045; lowest balance 63960.25 on 2026-01-13 after series:event_2082; reserve 51000; remaining headroom 12960.25. Baseline safe amount after the request cap and evidence blockers: 12960.25. First safe full-payment date: <empty>.

First PR ledger divergence: 2026-01-05 debit utilities, ours 3417.7, PR #8 3490.5. PR baseline lowest balance 64195.72 on 2026-01-13.
Affected source category records: event_2045, event_2053, event_2061, event_2069, event_2077.

Evidence resolutions:
- message_17: one-time income is not recurring salary; retain actual settled cash state Quote: The prize proceeds have reached your account after withholding.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|INR\|regular payroll | 61000 INR (constant_or_income_policy) | monthly | event_2043, event_2051, event_2059, event_2067, event_2075 | none |
| debit\|cloud_storage\|INR\|online backup subscription | 355 INR (constant_or_income_policy) | monthly | event_2047, event_2055, event_2063, event_2071, event_2079 | none |
| debit\|dining\|INR\|variable category spending | 1942.46 INR (upper_quartile_latest_12) | 7 days | event_2138, event_2139, event_2140, event_2141, event_2142, event_2143, event_2144, event_2145, event_2146, event_2147, event_2148, event_2149, event_2150, event_2151, event_2152, event_2153, event_2154, event_2155, event_2156, event_2157, event_2158, event_2159, event_2160, event_2161, event_2162, event_2163 | none |
| debit\|entertainment\|INR\|local event tickets | 1916.16 INR (upper_quartile_latest_12) | monthly | event_2050, event_2058, event_2066, event_2074, event_2082 | none |
| debit\|groceries\|INR\|variable category spending | 2321.31 INR (upper_quartile_latest_12) | 10 days | event_2084, event_2085, event_2086, event_2087, event_2088, event_2089, event_2090, event_2091, event_2092, event_2093, event_2094, event_2095, event_2096, event_2097, event_2098, event_2099, event_2100, event_2101 | none |
| debit\|insurance\|INR\|insurance policy payment | 2510 INR (constant_or_income_policy) | monthly | event_2046, event_2054, event_2062, event_2070, event_2078 | none |
| debit\|rent\|INR\|landlord standing order | 18600 INR (constant_or_income_policy) | monthly | event_2044, event_2052, event_2060, event_2068, event_2076, event_2083 | none |
| debit\|shopping\|INR\|monthly shopping spend | 2564 INR (upper_quartile_latest_12) | monthly | event_2049, event_2057, event_2065, event_2073, event_2081 | none |
| debit\|streaming\|INR\|family streaming plan | 1200 INR (constant_or_income_policy) | monthly | event_2048, event_2056, event_2064, event_2072, event_2080 | none |
| debit\|transport\|INR\|variable category spending | 1514.06 INR (upper_quartile_latest_12) | 5 days | event_2102, event_2103, event_2104, event_2105, event_2106, event_2107, event_2108, event_2109, event_2110, event_2111, event_2112, event_2113, event_2114, event_2115, event_2116, event_2117, event_2118, event_2119, event_2120, event_2121, event_2122, event_2123, event_2124, event_2125, event_2126, event_2127, event_2128, event_2129, event_2130, event_2131, event_2132, event_2133, event_2134, event_2135, event_2136, event_2137 | none |
| debit\|utilities\|INR\|household utility payment | 3417.7 INR (upper_quartile_latest_12) | monthly | event_2045, event_2053, event_2061, event_2069, event_2077 | none |

Candidate audit: 0 candidates; 0 have rejection/ranking reasons. All reasons and schedules are retained in JSON.

## request_25

| Field | Candidate | Public example | Match |
| --- | --- | --- | --- |
| affordability_status | not_affordable | not_affordable | yes |
| amount_safe_to_pay | 0 | 1425000 | no |
| earliest_date_for_full_payment | <empty> | <empty> | yes |
| payment_plan | none | none | yes |
| recommended_payment_method | not_recommended | not_recommended | yes |
| spending_changes_needed | none | none | yes |

Our retained ledger breaches reserve before any new purchase. The sample positive amount cannot survive that forecast. Its underlying transactions and horizon assumptions are unavailable.

Classification: recurrence_membership_timing_or_estimator_assumptions.

Quantified balance calculation (IDR): opening 32063050; lowest balance 23224629.62 on 2024-03-14 after series:event_2206; reserve 23379100; remaining headroom -154470.38. Baseline safe amount after the request cap and evidence blockers: 0. First safe full-payment date: <empty>.

First PR ledger divergence: 2024-03-06 debit dining, ours 1128974.93, PR #8 977609.8525. PR baseline lowest balance 22687937.735 on 2024-03-14.
Affected source category records: event_2262, event_2263, event_2264, event_2265, event_2266, event_2267, event_2268, event_2269, event_2270, event_2271, event_2272, event_2273, event_2274, event_2275, event_2276, event_2277, event_2278, event_2279, event_2280, event_2281, event_2282, event_2283, event_2284, event_2285, event_2286.

| Recurring series | Native estimate | Cadence | Paid members | Cancellation-only evidence |
| --- | --- | --- | --- | --- |
| credit\|salary\|USD\|international employer payroll | 1800 USD (constant_or_income_policy) | monthly | event_2167, event_2175, event_2183, event_2191, event_2199 | none |
| debit\|cloud_storage\|IDR\|cloud storage plan | 126350 IDR (constant_or_income_policy) | monthly | event_2171, event_2179, event_2187, event_2195, event_2203 | none |
| debit\|dining\|IDR\|variable category spending | 1128974.93 IDR (upper_quartile_latest_12) | 7 days | event_2262, event_2263, event_2264, event_2265, event_2266, event_2267, event_2268, event_2269, event_2270, event_2271, event_2272, event_2273, event_2274, event_2275, event_2276, event_2277, event_2278, event_2279, event_2280, event_2281, event_2282, event_2283, event_2284, event_2285, event_2286 | none |
| debit\|entertainment\|IDR\|games and recreation | 499510.22 IDR (upper_quartile_latest_12) | monthly | event_2174, event_2182, event_2190, event_2198, event_2206 | none |
| debit\|groceries\|IDR\|variable category spending | 1369082.68 IDR (upper_quartile_latest_12) | 10 days | event_2208, event_2209, event_2210, event_2211, event_2212, event_2213, event_2214, event_2215, event_2216, event_2217, event_2218, event_2219, event_2220, event_2221, event_2222, event_2223, event_2224, event_2225 | none |
| debit\|insurance\|IDR\|insurance policy payment | 904400 IDR (constant_or_income_policy) | monthly | event_2170, event_2178, event_2186, event_2194, event_2202 | none |
| debit\|rent\|IDR\|monthly rent | 6954000 IDR (constant_or_income_policy) | monthly | event_2168, event_2176, event_2184, event_2192, event_2200, event_2207 | none |
| debit\|shopping\|IDR\|monthly shopping spend | 1102784.74 IDR (upper_quartile_latest_12) | monthly | event_2173, event_2181, event_2189, event_2197, event_2205 | none |
| debit\|streaming\|IDR\|video streaming plan | 573800 IDR (constant_or_income_policy) | monthly | event_2172, event_2180, event_2188, event_2196, event_2204 | none |
| debit\|transport\|IDR\|variable category spending | 663001.49 IDR (upper_quartile_latest_12) | 5 days | event_2226, event_2227, event_2228, event_2229, event_2230, event_2231, event_2232, event_2233, event_2234, event_2235, event_2236, event_2237, event_2238, event_2239, event_2240, event_2241, event_2242, event_2243, event_2244, event_2245, event_2246, event_2247, event_2248, event_2249, event_2250, event_2251, event_2252, event_2253, event_2254, event_2255, event_2256, event_2257, event_2258, event_2259, event_2260, event_2261 | none |
| debit\|utilities\|IDR\|household utility payment | 1341541.39 IDR (upper_quartile_latest_12) | monthly | event_2169, event_2177, event_2185, event_2193, event_2201 | none |

Candidate audit: 1 candidates; 1 have rejection/ranking reasons. All reasons and schedules are retained in JSON.
- full_payment: reserve breach or unquantified mandatory commitment
