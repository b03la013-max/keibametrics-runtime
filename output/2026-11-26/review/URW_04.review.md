# 2026-11-26 URW_04 詳細反省（自動・実購入なし）

- 公式着順：9-12-5-1-2（上位3頭 [9, 12, 5]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 9／3着 8；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 0／損益 -900／PFS 0.0%
- 参照：{"revision": "URW_04.r2", "ticket_sha256": "fc2e1042c87aae3ef9c1c6eeae79a6a9b6e82037416d7e41a51ef22b74dbd2b0", "frozen_at": "2026-11-26T13:05:15.642387+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 4／3着 7；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 710／損益 -5290／PFS 11.8%
- 参照：{"final_receipt_sha256": "79bf1ac3ef68289bb08c1b21e242c44aad640ff3993f93874831f34091e355ac", "result_receipt_sha256": "34c1c378973279c899c4735323b24516038d3b2cb05de342d67d44bfb55a3a05", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "4e1b0acff7746541eb12a8f79fe16c06cdff73f589080d26808309052dd1bd93", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 13600, "pfs": 87.2}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T04:40:06.177222+00:00", "source_receipt_sha256": "e73a2ebd7fdf4dad5df8bd06db67b11a1bc5966ca2467852e1e37d9df4245d8f", "signed_final_at": "2026-11-26T04:40:18.944688+00:00", "delivered_ticket_sha256": "ceda56c66f3fc6462d0ade952fca23b787ad34c09dab042ce39d4071100e22fa", "settled_ticket_sha256": "79bf1ac3ef68289bb08c1b21e242c44aad640ff3993f93874831f34091e355ac"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 4, "HPI-L": 1}, "ruled_neutral_share": 0.006} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 4, "third_pre_rank": 7, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [9, 12, 5], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 11.8, "profit_loss": -5290, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 11.8, "tickets": 60, "payout": 710} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `5cafbadbf5cf349e`／Learning State `22c402532f08`</sub>
