# 2026-11-25 URW_06 詳細反省（自動・実購入なし）

- 公式着順：7-10-2-11-1（上位3頭 [7, 10, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 4／3着 5；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 800／返還 0／払戻 160／損益 -640／PFS 20.0%
- 参照：{"revision": "URW_06.r2", "ticket_sha256": "9eae4de93ed4c87ec3e8116c90923c79bbe72d5d7517b56841ebde3adebac23e", "frozen_at": "2026-11-25T14:05:03.960419+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 5／3着 7；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 270／損益 -5730／PFS 4.5%
- 参照：{"final_receipt_sha256": "b58b38d09123ae19992dd55d4bbcbb5e4ff951162375ee705564964b34516aef", "result_receipt_sha256": "37db246d39c332676854b8932c72113e99cf92c0063c56622bd1dfef6a2b29dd", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "66d32dbba46e93a1601b289c177bdc8ecdc355344bcfc0dde3bd472e5518edde", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 10270, "pfs": 65.8}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T05:42:09.890912+00:00", "source_receipt_sha256": "d29345a726a13f47ce58912439d44333f68145a77c7f1a6035da40dac6faa5c9", "signed_final_at": "2026-11-25T05:42:22.655846+00:00", "delivered_ticket_sha256": "62b288af969dec2d43574279d2b2a3e072a55519dcc68e91cc69246fb9b35f48", "settled_ticket_sha256": "b58b38d09123ae19992dd55d4bbcbb5e4ff951162375ee705564964b34516aef"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 5, "third_pre_rank": 7, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [7, 10, 2], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 4.5, "profit_loss": -5730, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 4.5, "tickets": 60, "payout": 270} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `5d2d04469fc3b995`／Learning State `52895a197cb6`</sub>
