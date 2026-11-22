# 2026-11-22 KOC_03 詳細反省（自動・実購入なし）

- 公式着順：11-2-1-10-3（上位3頭 [11, 2, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 2／3着 7；W True・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 290／損益 -410／PFS 41.4%
- 参照：{"revision": "KOC_03.r2", "ticket_sha256": "9194ddf82bdc12b7e1a22e526d2d2c6df4a534d07201dfbc1e50234250aaa7c4", "frozen_at": "2026-11-22T15:50:04.014451+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 7；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 5800／損益 -200／PFS 96.7%
- 参照：{"final_receipt_sha256": "891556219c35c3edda10886193846c441b52edaf16d311238571ad7688f2d3e7", "result_receipt_sha256": "6bc37627df8b24232d849465ae7f8ed5057d2763c26b2919fcc3e0770f327dc8", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "f4e8c9d5da0000528b749a7c008a55440112fb0ba30070058ad41d22f6c09dd8", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 5800, "pfs": 40.3}, "effective_revision": "REVISION_2", "source_at": "2026-11-22T07:27:04.031823+00:00", "source_receipt_sha256": "739016fd55422ad760242ffabaf96207dd4a48bdca6a50defdba05fcde719895", "signed_final_at": "2026-11-22T07:27:16.001305+00:00", "delivered_ticket_sha256": "d13e0a49f62bddfa90280e0db39086c5f916c3cf0660ba55a5d3a2b02ff37e6f", "settled_ticket_sha256": "891556219c35c3edda10886193846c441b52edaf16d311238571ad7688f2d3e7"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 3, "HPI-L": 1}, "ruled_neutral_share": 0.075} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ベンテンカグラ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 7, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [11, 2, 1], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 96.7, "profit_loss": -200, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 96.7, "tickets": 60, "payout": 5800} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `0dbed46fb7d61d84`／Learning State `942d1853ea83`</sub>
