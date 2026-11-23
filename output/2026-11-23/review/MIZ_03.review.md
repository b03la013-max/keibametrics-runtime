# 2026-11-23 MIZ_03 詳細反省（自動・実購入なし）

- 公式着順：4-2-10-6-3（上位3頭 [4, 2, 10]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 2／2着 6／3着 7；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "MIZ_03.r2", "ticket_sha256": "f257cfaa6d69d1c84891ae3ba8b8f3f9fafa61c44ee4a3a80536f96976a77285", "frozen_at": "2026-11-23T12:00:08.568783+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 8／3着 6；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "4bb7818e213a497a4dd22e77b79a938878546473ccd3cde5d1b9220ae7de067b", "result_receipt_sha256": "5914d3b0be01900df30d1038be76c93ac1241d956170f60b02306375464fccb2", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "6532a755a02025e59949b3c76f5c2345375342dc4d036fdecdf55abb8091996d", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-23T03:04:34.099696+00:00", "source_receipt_sha256": "0ed67a501c866dbaaf3a746848d83dfc32ffe3801c1b189f27eb3aa53c261421", "signed_final_at": "2026-11-23T03:04:45.721329+00:00", "delivered_ticket_sha256": "5ab2bb91b39861c8cd4dfef536f665e53efe0c936259e8153ad492c41e4cd78e", "settled_ticket_sha256": "4bb7818e213a497a4dd22e77b79a938878546473ccd3cde5d1b9220ae7de067b"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 3, "T3I-L": 5, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（キタスピエル）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 8, "third_pre_rank": 6, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [4, 2, 10], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED"] |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 8} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `31bfee7cfe95ed5f`／Learning State `6fd01fac20b3`</sub>
