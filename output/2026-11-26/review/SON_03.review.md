# 2026-11-26 SON_03 詳細反省（自動・実購入なし）

- 公式着順：4-10-2-8-3（上位3頭 [4, 10, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 4；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 1190／損益 490／PFS 170.0%
- 参照：{"revision": "SON_03.r2", "ticket_sha256": "a18cca0f0fb95cdbff7d583d41e76946e3985161ad71c878314ab5bae7d7ede0", "frozen_at": "2026-11-26T10:55:11.228496+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 4／3着 3；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1450／損益 -4550／PFS 24.2%
- 参照：{"final_receipt_sha256": "081ce4762ea07e56f5f318446587018b4140aec5bdc94daad6059b0b84d85e6e", "result_receipt_sha256": "0e2e79c2958deb490284905f430d16cb1783d4b73b242f21bd7e353a03dafcbb", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "22d51ef3d0e06773853dd3a9d5ae7fd4a4177b2856846684ebbd832633e0f2b9", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 3100, "pfs": 23.5}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T02:30:03.339155+00:00", "source_receipt_sha256": "07c1d0abf27242abbb6352344e701871e264b6bbea406fe0f754b5f81122ae01", "signed_final_at": "2026-11-26T02:30:14.947333+00:00", "delivered_ticket_sha256": "afe0e0d8ee91aa28f425bbcd9d513842a7cd76660b920fa26b43110058438b38", "settled_ticket_sha256": "081ce4762ea07e56f5f318446587018b4140aec5bdc94daad6059b0b84d85e6e"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 4, "HPI-L": 3}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（スカイライズ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 4, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [4, 10, 2], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 24.2, "profit_loss": -4550, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 24.2, "tickets": 60, "payout": 1450} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `eb7d0f9d3742edd9`／Learning State `9fc0d6042d93`</sub>
