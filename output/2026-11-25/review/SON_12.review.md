# 2026-11-25 SON_12 詳細反省（自動・実購入なし）

- 公式着順：5-2-8-10-1（上位3頭 [5, 2, 8]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 6／2着 7／3着 1；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 2820／損益 1920／PFS 313.3%
- 参照：{"revision": "SON_12.r2", "ticket_sha256": "063c4eac71b90d7e1900418143bdac58caef9fc9c4736505031ef760c493dfc2", "frozen_at": "2026-11-25T16:00:24.841015+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 5／2着 6／3着 2；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 6490／損益 490／PFS 108.2%
- 参照：{"final_receipt_sha256": "755c611013fc8749fd4bc71a89d0689cbfe619f9b2bbe31aa6cf08e341be1dab", "result_receipt_sha256": "da91331aabee13d96cc70bf900540e22eb7ac5aed14293eeaa859abcf86b926d", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "69591091d108c4d25c56b75161ac6ff7426d6069f9588f6c60615c1772bbab22", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T07:36:14.967986+00:00", "source_receipt_sha256": "840d5a22d6b71976f0a47375600b2bcb51880f5c4383c40506979feaf65a457f", "signed_final_at": "2026-11-25T07:36:27.359849+00:00", "delivered_ticket_sha256": "9d8bbd6fc70143102447ba5ea173bd508b901f9d9075b09956a182d753852a78", "settled_ticket_sha256": "755c611013fc8749fd4bc71a89d0689cbfe619f9b2bbe31aa6cf08e341be1dab"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 3, "T3I-L": 3, "HPI-L": 4}, "ruled_neutral_share": 0.003} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 6, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 2, 8], "rescues": ["WINNER_ROLE_RESCUE"], "supports": ["P2_ROLE_CONFI |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 108.2, "profit_loss": 490, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `7987be84c25a2830`／Learning State `b36a2f13e0d0`</sub>
