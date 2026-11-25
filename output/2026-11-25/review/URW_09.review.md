# 2026-11-25 URW_09 詳細反省（自動・実購入なし）

- 公式着順：10-1-2-4-6（上位3頭 [10, 1, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3

## PAPER

- 1着の事前順位 6／2着 11／3着 10；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "URW_09.r2", "ticket_sha256": "12a4b1bc0c14fc708356382d695b87d02929f612683d5b1863a5f83d8c356bbb", "frozen_at": "2026-11-25T15:50:08.469990+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 5／2着 11／3着 10；W False・P2 False・P3 True
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "878b5cfeee32b27423986fceb06642bf53e14d13c222eeef3bde3058162ad092", "result_receipt_sha256": "2159f767d4771d3b1a645dcc5dfa969b7d5541aef436e65ba9fb9562667be144", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "3d66fc3d60735ae1ebf0c2474aae7c696abdb29b5cf15c3b4bb67551ce07743a", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-25T06:53:10.457439+00:00", "source_receipt_sha256": "6cbaa82a2cafbea77a0fb81dbbb127fe77dc43b79e78c75a5e957f9cbc81da6e", "signed_final_at": "2026-11-25T06:53:22.685901+00:00", "delivered_ticket_sha256": "a361b85114af49ecbc577b504490c63a0d3ee929bea9c5b670a6436e6c477407", "settled_ticket_sha256": "878b5cfeee32b27423986fceb06642bf53e14d13c222eeef3bde3058162ad092"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 6, "TPI-L": 5, "SRI-L": 5, "T3I-L": 6, "HPI-L": 5}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 11, "third_pre_rank": 10, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [10, 1, 2], "rescues": [], "supports": [], "misses": ["WINNER_ROLE_NOT_KR |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `175faad4b07a4687`／Learning State `f3ddd79a09d7`</sub>
