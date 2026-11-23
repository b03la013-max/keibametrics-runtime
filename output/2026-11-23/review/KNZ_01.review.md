# 2026-11-23 KNZ_01 詳細反省（自動・実購入なし）

- 公式着順：4-9-6-2-3（上位3頭 [4, 9, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 5／3着 4；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 1600／返還 0／払戻 0／損益 -1600／PFS 0.0%
- 参照：{"revision": "KNZ_01.r2", "ticket_sha256": "7831b7e557575a77959f494e53bef342a7d0f7768f9677a4c19395115055f582", "frozen_at": "2026-11-23T12:30:01.569566+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 7／3着 8；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "9303212f44c664ed56383871bda4e233394c4546bf4c8face101033c3b3c0a6b", "result_receipt_sha256": "f14e94c43e51d6fa4328983a98f449d14096bcfb54db3600381c045a976c628a", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "eb0e98e9dac1539b3b98c539200d17edd3b9b100377e60cd1c41e429299ee220", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-23T04:06:11.774307+00:00", "source_receipt_sha256": "0fd55e64006cd4eb1a7cc64d82be07c5c282e49e4d5bf56564e12f7c9452d11c", "signed_final_at": "2026-11-23T04:06:22.786257+00:00", "delivered_ticket_sha256": "7db1581f80c186be0cd80d81474ff6bc18141a289352f60d4f6fbee5fc6b63de", "settled_ticket_sha256": "9303212f44c664ed56383871bda4e233394c4546bf4c8face101033c3b3c0a6b"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 2, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 2, "second_pre_rank": 7, "third_pre_rank": 8, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [4, 9, 6], "rescues": ["P2_ROLE_RESCUE", "ORDERED_PAIR_RESCUE"], "support |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 7} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `a6e76a4da6ab6c19`／Learning State `73dc96c20c93`</sub>
