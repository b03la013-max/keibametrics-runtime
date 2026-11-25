# 2026-11-25 NGY_01 詳細反省（自動・実購入なし）

- 公式着順：9-4-11-5-2（上位3頭 [9, 4, 11]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 2／3着 10；W True・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 510／損益 -190／PFS 72.9%
- 参照：{"revision": "NGY_01.r2", "ticket_sha256": "8af15da33158ee8c69897f997a28a53ec9995b02d8679a47ad41dc6b063e7d3a", "frozen_at": "2026-11-25T13:55:18.225357+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 5／3着 9；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 2510／損益 -3490／PFS 41.8%
- 参照：{"final_receipt_sha256": "64d08e4e993ea4b3a322a2dfa0d6fee13a5bbc4b0b92092d09030f3553a6456c", "result_receipt_sha256": "9fb5322008276d542e04413636451bb28432da709494ffc1e005a8306c34a323", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "19e854245b369a83b140775cb822bd7b433b471c98a859184571b243fc163cc1", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 81710, "pfs": 523.8}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T05:32:20.152794+00:00", "source_receipt_sha256": "b707c22bb672f296d495eba616d07c3aa434ec43d33638b6805560a06a92cc34", "signed_final_at": "2026-11-25T05:32:32.511309+00:00", "delivered_ticket_sha256": "89807285236fea7f909bad77b7ae6255e5038c42a502712d981e42158974bca3", "settled_ticket_sha256": "64d08e4e993ea4b3a322a2dfa0d6fee13a5bbc4b0b92092d09030f3553a6456c"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 4, "HPI-L": 4}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 5, "third_pre_rank": 9, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [9, 4, 11], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 41.8, "profit_loss": -3490, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 41.8, "tickets": 60, "payout": 2510} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `74fd6d4e0003dfca`／Learning State `cb29c6a2674c`</sub>
