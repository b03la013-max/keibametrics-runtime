# 2026-11-23 KNZ_07 詳細反省（自動・実購入なし）

- 公式着順：5-4-1-6-7（上位3頭 [5, 4, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 5／3着 4；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KNZ_07.r2", "ticket_sha256": "73134116b76b81fc5516ed4b45917ed5e38833fd673fe840fd9ff83eb740424e", "frozen_at": "2026-11-23T16:20:13.309506+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 6／3着 4；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 2310／損益 -3690／PFS 38.5%
- 参照：{"final_receipt_sha256": "e677337d7679f9895a71d2d541635f68fd7436991c7c6fd529de62da4fe40a88", "result_receipt_sha256": "61a9f593f3d06eb63ef7897ccc3b50fadb813ac6e0ba29be512e4fd0ecbdf926", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "564e698394264f746976834dddab6bba04ae251cd842cff73f03493b1698cf2a", "signed_final_ticket_count": 90, "signed_final_total_investment": 9000, "signed_final_settlement": {"invest": 9000, "refund": 0, "effective_invest": 9000, "payout": 5370, "pfs": 59.7}, "effective_revision": "REVISION_2", "source_at": "2026-11-23T07:56:20.951369+00:00", "source_receipt_sha256": "46bc781740dbcaeecc2d84bea6721ccff533b50a34a4717c3d3ba8ee71d7cb63", "signed_final_at": "2026-11-23T07:56:31.685047+00:00", "delivered_ticket_sha256": "7c8cdf531680e4f4d68cfc17f6821838e0dd0ed60e6548dbf26990efcdb5013e", "settled_ticket_sha256": "e677337d7679f9895a71d2d541635f68fd7436991c7c6fd529de62da4fe40a88"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 3, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 6, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [5, 4, 1], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 38.5, "profit_loss": -3690, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 38.5, "tickets": 60, "payout": 2310} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `989bd900c8589e6b`／Learning State `d4266231eb84`</sub>
