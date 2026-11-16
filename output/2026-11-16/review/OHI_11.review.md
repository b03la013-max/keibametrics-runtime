# 2026-11-16 OHI_11 詳細反省（自動・実購入なし）

- 公式着順：8-9-4-1-5（上位3頭 [8, 9, 4]）
- 距離帯：MIDDLE(1701-2100)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 6／2着 7／3着 1；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 470／損益 -230／PFS 67.1%
- 参照：{"revision": "OHI_11.r2", "ticket_sha256": "8a7a5e604bd663196cb411b83eb1be065887589a7cb7a6becb9a727d8242d245", "frozen_at": "2026-11-16T19:25:02.043963+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 9；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 12000／返還 0／払戻 16570／損益 4570／PFS 138.1%
- 参照：{"final_receipt_sha256": "c97004d7b930454b05dfe7d954fdadd52ce37e4863ddd38679e1f10c28b5161b", "result_receipt_sha256": "112bd16cce428460b0d3b31dc97eb5568efa7746e8599e8355d4c28004d74402", "result_receipt_verified": true, "krs_input_mode": null, "authority": null}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 3, "T3I-L": 4, "HPI-L": 6}, "ruled_neutral_share": 0.107} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（マイネルボンバー）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 9, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | UNKNOWN | {"pre_result_utility_class": null, "post_result_evaluation": {"classification": "NOT_AVAILABLE", "rescues": [], "supports": [], "misses": []}} |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | OK | {"pfs": 138.1, "profit_loss": 4570, "hit_but_loss": false, "tickets": 120} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | "automatic review krs.post_result_evaluation = NOT_AVAILABLE (utility not frozen in FINAL)" | next formal races carry krs_prediction_utility in the FINAL package | check FINAL package krs_prediction_utility_shadow presence | KRS evaluation availability rate |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `11a97fcc095f40b8`／Learning State `a0eddb142577`</sub>
