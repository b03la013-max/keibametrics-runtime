# 2026-11-27 SON_03 詳細反省（自動・実購入なし）

- 公式着順：10-6-11-4-5（上位3頭 [10, 6, 11]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 2／3着 3；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 480／損益 -220／PFS 68.6%
- 参照：{"revision": "SON_03.r2", "ticket_sha256": "d84e6ea907ea8efc62d39e4c6282a0f686846e20dc319f332724c3e5955368b1", "frozen_at": "2026-11-27T10:55:08.910506+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 4／3着 6；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 460／損益 -5540／PFS 7.7%
- 参照：{"final_receipt_sha256": "fb43623ee816e5f5de84790d271d12e6db5772f06b31c4e31c7c65048413c0e8", "result_receipt_sha256": "e2b9778808226da3a6841a7928ef51b222f73369a21bd668a25f8c291083acb2", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "1be5d217f9774444c2c78a1551e5b910ecabee3ed504fc605ea62731f8a11b39", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 1600, "pfs": 10.3}, "effective_revision": "REVISION_2", "source_at": "2026-11-27T02:30:20.305470+00:00", "source_receipt_sha256": "8d3eac4e547fa57d314112d8a2820674bc5e2af387df1a1fd1a9e39d64ceda9e", "signed_final_at": "2026-11-27T02:30:33.004629+00:00", "delivered_ticket_sha256": "990591af18e4c0ff2d5a10ed43d35e7bb685327a6a692827750fc2718c7d1787", "settled_ticket_sha256": "fb43623ee816e5f5de84790d271d12e6db5772f06b31c4e31c7c65048413c0e8"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 4, "third_pre_rank": 6, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [10, 6, 11], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROL |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 7.7, "profit_loss": -5540, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 7.7, "tickets": 60, "payout": 460} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `41a25fadb5809bf6`／Learning State `79fbd32fd6b4`</sub>
