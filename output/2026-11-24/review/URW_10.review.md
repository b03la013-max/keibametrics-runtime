# 2026-11-24 URW_10 詳細反省（自動・実購入なし）

- 公式着順：2-3-1-4-5（上位3頭 [2, 3, 1]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 5／3着 9；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 800／返還 0／払戻 190／損益 -610／PFS 23.8%
- 参照：{"revision": "URW_10.r2", "ticket_sha256": "ded5b2f65c61be742806cbef4cc0f3675d3dd68d942ba4cc568ab49cead07ae3", "frozen_at": "2026-11-24T16:25:17.406242+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 10／3着 5；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "bcb91b6fac6ed09d38c881987b3a8629df40b14ce10cd17e0b8571f20372f0ae", "result_receipt_sha256": "1b287ebf96f92bf8447110d3eb6049de1a24b094899654f3777636498af7d479", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "d0f7eb4b2d7322bbd8b00a068f27b8a2c554a1e536a8e9cf22ba0f739de9c21d", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 2200, "pfs": 14.1}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T08:02:21.843680+00:00", "source_receipt_sha256": "e4a9b829d292707b66e75830261334c3f8c19c2a6cca4a76a5d49046b6d98ed0", "signed_final_at": "2026-11-24T08:02:37.838249+00:00", "delivered_ticket_sha256": "37b969913edec128f6da71715907d2082181c18009c00bbe2651ce86e6d4e23a", "settled_ticket_sha256": "bcb91b6fac6ed09d38c881987b3a8629df40b14ce10cd17e0b8571f20372f0ae"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 3, "HPI-L": 1}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補6頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 10, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [2, 3, 1], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "ORDERED_ |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 10} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `4dd4a667b666dbe2`／Learning State `138cb5fdcf69`</sub>
