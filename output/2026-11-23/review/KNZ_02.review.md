# 2026-11-23 KNZ_02 詳細反省（自動・実購入なし）

- 公式着順：8-5-7-1-9（上位3頭 [8, 5, 7]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 2／3着 4；W True・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 1270／損益 570／PFS 181.4%
- 参照：{"revision": "KNZ_02.r2", "ticket_sha256": "efb97e9bb353207d6e4095590a0eef817b0a260e72098d41b631d462d9ead443", "frozen_at": "2026-11-23T13:10:06.956608+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 5；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1350／損益 -4650／PFS 22.5%
- 参照：{"final_receipt_sha256": "e67d2120aff3ff78949a5e28b228538f313392533fd206ea4fb55de8a585e8a6", "result_receipt_sha256": "7508d2236e19cd42d27cd44147511e02ca21649344ce22868001d3e9fac4b058", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "be6e7aac8b6584097c7f5d0fcd152e64beac32d4e38cbdc55ce56c203d973348", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 2210, "pfs": 18.4}, "effective_revision": "REVISION_2", "source_at": "2026-11-23T04:47:11.459109+00:00", "source_receipt_sha256": "306464c44cb34e6e4ab063f382e4cf6d915c90c01a028ecfd2fc087a55afb196", "signed_final_at": "2026-11-23T04:47:22.747999+00:00", "delivered_ticket_sha256": "e29caad9683d8c3a8599981d413c3cad55ea36e47f2d5add4404d041548e673e", "settled_ticket_sha256": "e67d2120aff3ff78949a5e28b228538f313392533fd206ea4fb55de8a585e8a6"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 2, "T3I-L": 1, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [8, 5, 7], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 22.5, "profit_loss": -4650, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 22.5, "tickets": 60, "payout": 1350} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `512998c6c1c65099`／Learning State `4ebaa3ef05f9`</sub>
