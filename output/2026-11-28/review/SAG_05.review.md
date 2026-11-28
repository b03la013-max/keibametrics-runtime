# 2026-11-28 SAG_05 詳細反省（自動・実購入なし）

- 公式着順：7-5-6-1-3（上位3頭 [7, 5, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 3；W False・P2 False・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 430／損益 -270／PFS 61.4%
- 参照：{"revision": "SAG_05.r2", "ticket_sha256": "4ead0c8d151a5cae8afb01b6909accd7dd25c772eb9e45f161fe3cd7d6c16448", "frozen_at": "2026-11-28T16:15:06.364064+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 1／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 710／損益 -5290／PFS 11.8%
- 参照：{"final_receipt_sha256": "83b83daa6eeb61954531ffbdd03e66367456791135349ce6eb1608960310dc58", "result_receipt_sha256": "b0b60670a46e659b28bd31bf56dee4d67c283d46c4f7cec8fc4ce59dcadf4df6", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "a9b79fc98ad441fd5aae412ffd11496db40a312844ffc3f806cf908eb24279f6", "signed_final_ticket_count": 90, "signed_final_total_investment": 9000, "signed_final_settlement": {"invest": 9000, "refund": 0, "effective_invest": 9000, "payout": 2400, "pfs": 26.7}, "effective_revision": "REVISION_1", "source_at": "2026-11-28T07:18:37.566081+00:00", "source_receipt_sha256": "d5cd77aea0f9b0974df64a0b9fe99f4993ea2c71413c0c91d70a2dadbf37c9ad", "signed_final_at": "2026-11-28T07:18:47.334262+00:00", "delivered_ticket_sha256": "96ed749171033afe9bac1b4586737c6e0f887194cf9043bd813403443513ef2b", "settled_ticket_sha256": "83b83daa6eeb61954531ffbdd03e66367456791135349ce6eb1608960310dc58"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 2, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（マイネルサハラ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 1, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [7, 5, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 11.8, "profit_loss": -5290, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 11.8, "tickets": 60, "payout": 710} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `9e0821a6d47f6c41`／Learning State `b959ea6bcb7d`</sub>
