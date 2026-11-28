# 2026-11-28 KOC_12 詳細反省（自動・実購入なし）

- 公式着順：9-11-2-3-7（上位3頭 [9, 11, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 7／2着 11／3着 8；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 0／損益 -900／PFS 0.0%
- 参照：{"revision": "KOC_12.r2", "ticket_sha256": "33778ef61c90e0b3eb4503eca00e4507acccee315a5a22b92bc1249cc66a9808", "frozen_at": "2026-11-28T20:05:27.011725+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 11／3着 7；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "54b9a30ceff220179971b1416447167cf111c6d48616eff670216d8f1ea90804", "result_receipt_sha256": "295a3b56e7559275dfb5b326bd1f7e9d58581b2bee503d3b6401f369ba151097", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "2bc927a885cd65cdf0c91689e74d7f715988cba77689168215ef7acf595aa724", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-28T11:41:04.356533+00:00", "source_receipt_sha256": "31b49a8f66dc4ee0be12a319de1196bd4f910635046f06e37d0115280afd1ba7", "signed_final_at": "2026-11-28T11:41:17.883913+00:00", "delivered_ticket_sha256": "881b68286d9611eb1c8657df4f38e622076aa838bd00fe88b3db4cb7281f72ae", "settled_ticket_sha256": "54b9a30ceff220179971b1416447167cf111c6d48616eff670216d8f1ea90804"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 5, "SRI-L": 2, "T3I-L": 3, "HPI-L": 5}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 2, "second_pre_rank": 11, "third_pre_rank": 7, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [9, 11, 2], "rescues": [], "supports": [], "misses": ["WINNER_ROLE_NOT_KR |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 11} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `cd46d18fb5966ac6`／Learning State `172aab1c3629`</sub>
