# 2026-11-23 MIZ_09 詳細反省（自動・実購入なし）

- 公式着順：1-5-9-10-8（上位3頭 [1, 5, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 2／2着 9／3着 4；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 800／返還 0／払戻 0／損益 -800／PFS 0.0%
- 参照：{"revision": "MIZ_09.r2", "ticket_sha256": "c5907923ccef530b568eb77157c21914f5a478e1f09c69fc985999951ec6507c", "frozen_at": "2026-11-23T15:35:02.710101+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 8／3着 6；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "63f185ef05187046a35efc9a9e7d07452730401a3b7f97309419cbf728ebf425", "result_receipt_sha256": "f52f9a87d2cf191ed930abef72301cc0aa0682e5e74af14ca8880f73b645b321", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "8cc3e09824a3b71599b15d6d2d13247fe8f371862c386f4b75a6fbe0693ee6cc", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-23T06:38:04.854792+00:00", "source_receipt_sha256": "5ff6c11133999f20dd7a257c9c7fc27b5c7129820578c2fa3e681dc5e26754f6", "signed_final_at": "2026-11-23T06:38:15.612347+00:00", "delivered_ticket_sha256": "9f8838f8492b0ffb4fb51c1ef0050a65dab24abc1fc46990fd8cd29741def036", "settled_ticket_sha256": "63f185ef05187046a35efc9a9e7d07452730401a3b7f97309419cbf728ebf425"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 2, "SRI-L": 1, "T3I-L": 1, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 2, "second_pre_rank": 8, "third_pre_rank": 6, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [1, 5, 9], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED"], |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 8} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `df68a0c60178e492`／Learning State `cb9d8eeb9f84`</sub>
