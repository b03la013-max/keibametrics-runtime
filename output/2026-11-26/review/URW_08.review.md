# 2026-11-26 URW_08 詳細反省（自動・実購入なし）

- 公式着順：2-11-8-3-5（上位3頭 [2, 11, 8]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 3／3着 9；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 1600／返還 0／払戻 450／損益 -1150／PFS 28.1%
- 参照：{"revision": "URW_08.r2", "ticket_sha256": "a1488171b70e7eb7e0a10ecb2de96c8a2c3428384235d3272a23549745601776", "frozen_at": "2026-11-26T15:15:20.204835+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 8／3着 6；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "b7433e3a831c8fd812b3bc0ebc29c00c281c2701951a4d6bf6b6e050da8239c1", "result_receipt_sha256": "bddbf0976ff34b7658585b0977de502d6ca29417cc79659249c2b299e5bea8c1", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "ac81e4539aa288a40d3a775ff37779267058e2c5343f57480898e6b308099a7f", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T06:51:14.408694+00:00", "source_receipt_sha256": "31e8cf5e6f392dfa1ad71f3f919a813ebf3899fd044876dfe2d986fbb9531825", "signed_final_at": "2026-11-26T06:51:26.452825+00:00", "delivered_ticket_sha256": "cde136b91d4f70bed9abfa5de25cdc086f59f4e90b332ce6b81e0084f53bb993", "settled_ticket_sha256": "b7433e3a831c8fd812b3bc0ebc29c00c281c2701951a4d6bf6b6e050da8239c1"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 8, "third_pre_rank": 6, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [2, 11, 8], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 8} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `73ff84fef2941be1`／Learning State `1d178cffaf70`</sub>
