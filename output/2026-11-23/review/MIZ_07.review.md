# 2026-11-23 MIZ_07 詳細反省（自動・実購入なし）

- 公式着順：12-2-11-1-10（上位3頭 [12, 2, 11]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 7／3着 3；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 1290／損益 590／PFS 184.3%
- 参照：{"revision": "MIZ_07.r2", "ticket_sha256": "d31862fdbcceaaddc8b68451d0119c3197f3201e0749e32ee33271b66f177c01", "frozen_at": "2026-11-23T14:25:02.677764+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 7／3着 2；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "18bcf05596bf6e69499a1ccffc63de36f6a2a136a6656ca419f5e8f9e3f4547b", "result_receipt_sha256": "e052b837dddfca2912e6553b79991aee9f3a00d8d76a0c662bb2ecab847ffa3d", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "7846c7ff48a9153d82261bed93491e08ed8b9eae88a2f35dd2988e41f01e9b9b", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-23T06:02:11.798178+00:00", "source_receipt_sha256": "6e132675d8f4c2cde8d224987636e30c790db34a533607980267a323ff6d6e32", "signed_final_at": "2026-11-23T06:02:24.906090+00:00", "delivered_ticket_sha256": "0aebb953ddeff027138a3c146b071518c90c8eb3302bf7078f0189f4049e0988", "settled_ticket_sha256": "18bcf05596bf6e69499a1ccffc63de36f6a2a136a6656ca419f5e8f9e3f4547b"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 3, "T3I-L": 1, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 7, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [12, 2, 11], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROL |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 7} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `7653a54f4e244708`／Learning State `39d98b3f6ba7`</sub>
