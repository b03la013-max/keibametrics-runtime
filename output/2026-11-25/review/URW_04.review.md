# 2026-11-25 URW_04 詳細反省（自動・実購入なし）

- 公式着順：5-12-8-10-2（上位3頭 [5, 12, 8]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 3／2着 2／3着 6；W False・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "URW_04.r2", "ticket_sha256": "732d680536571e5e54097cfec333a214374598764abeccccc24e93bf692792f4", "frozen_at": "2026-11-25T13:05:02.537448+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 2／3着 10；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 530／損益 -5470／PFS 8.8%
- 参照：{"final_receipt_sha256": "3eb660f89e00237cfdb4bf00d794dde94f0fec5ba8c7393d3f2e6e22cc20ed2c", "result_receipt_sha256": "f1d55b44bc282b76f8e51a59017dace246e6d39adc1702798401d2f4c2fde763", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "59d76aaf0384562bb0ad97ac42552db16643d0d243ba414ad610b7b3c160fd1c", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 980, "pfs": 6.3}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T04:40:10.569539+00:00", "source_receipt_sha256": "74acc93b8bf8e4a5f1aa845b8e0a14a6c47837e9407c54a574699823b80d7034", "signed_final_at": "2026-11-25T04:40:23.323380+00:00", "delivered_ticket_sha256": "a626b5eb6ddd9d8c094684dd1656ec5bba7a683d1d5376ecb0efb0dc3744ffa6", "settled_ticket_sha256": "3eb660f89e00237cfdb4bf00d794dde94f0fec5ba8c7393d3f2e6e22cc20ed2c"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 6, "T3I-L": 5, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 2, "third_pre_rank": 10, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 12, 8], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 8.8, "profit_loss": -5470, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 8.8, "tickets": 60, "payout": 530} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `083ce598984b00d5`／Learning State `d5ad08fadef9`</sub>
