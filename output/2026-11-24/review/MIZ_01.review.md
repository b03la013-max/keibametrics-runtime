# 2026-11-24 MIZ_01 詳細反省（自動・実購入なし）

- 公式着順：3-1-2-4-8（上位3頭 [3, 1, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 3／3着 9；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "MIZ_01.r2", "ticket_sha256": "634f062d8b942fdd72598763b668dea1b59fc556cc2a44dbb3ae6267fd865519", "frozen_at": "2026-11-24T10:56:28.994038+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 3／3着 9；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 780／損益 -5220／PFS 13.0%
- 参照：{"final_receipt_sha256": "fd975af1b62d35bf8ce2c3e7ca4aa226cf21c9efaf1014bf165e612c00bb3408", "result_receipt_sha256": "6fd29a20cb917cd7294ec32bf4c3e6dab1c14af6e3d4e04ae3ade38630ab514c", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "fd3fcca394a2dbc8ac985ffe3fa3b3c8d16ced4b19bb8e0d966046470de524cd", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 4140, "pfs": 34.5}, "effective_revision": "REVISION_1", "source_at": "2026-11-24T02:00:24.666617+00:00", "source_receipt_sha256": "a04c266c994603016a51dd92ba53a39600b8885551ec28316643aa319f6e45f1", "signed_final_at": "2026-11-24T02:00:36.358608+00:00", "delivered_ticket_sha256": "bce260c2d9f17753ef8fb52dfdba5f7971c6f608c79de0415a8eeae3ef9276d0", "settled_ticket_sha256": "fd975af1b62d35bf8ce2c3e7ca4aa226cf21c9efaf1014bf165e612c00bb3408"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 3, "third_pre_rank": 9, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 1, 2], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 13.0, "profit_loss": -5220, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 13.0, "tickets": 60, "payout": 780} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `2278e3c2e8ee6c10`／Learning State `26238aeae3e1`</sub>
