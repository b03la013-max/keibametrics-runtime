# 2026-11-23 SAG_07 詳細反省（自動・実購入なし）

- 公式着順：3-1-5-2-8（上位3頭 [3, 1, 5]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 4／2着 3／3着 1；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SAG_07.r2", "ticket_sha256": "cadfc50ee74760ed561912c4e01c950bd35a9d2abd4536d1a5e107eda2b0fba2", "frozen_at": "2026-11-23T18:00:09.834914+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 1／3着 3；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1980／損益 -4020／PFS 33.0%
- 参照：{"final_receipt_sha256": "c766ef0bd8fdac903f27856e5d04c006e626d3e65151305abbc2c3be32e12fac", "result_receipt_sha256": "6784ed0998db5bf5ab4c5cd9319495f56fef883ee284a8043cc0c55fa8ca205b", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "b1413b111b42999465fa194aa1581c6c0cb9c2345c2266be2b2e6bb58a93bdb5", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 1750, "pfs": 13.3}, "effective_revision": "REVISION_1", "source_at": "2026-11-23T09:03:12.081431+00:00", "source_receipt_sha256": "e1e9aa4c17e3787e65d7048fbe1e6b5dd48d97149ff838eb66d1ec8affcb92f0", "signed_final_at": "2026-11-23T09:03:26.115531+00:00", "delivered_ticket_sha256": "84e856ec213b86e6307be3ba1513fbebb7d52a7d8cc0da55235353b74a48cc17", "settled_ticket_sha256": "c766ef0bd8fdac903f27856e5d04c006e626d3e65151305abbc2c3be32e12fac"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 3, "SRI-L": 3, "T3I-L": 2, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（イケノアサチャン）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 1, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 1, 5], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 33.0, "profit_loss": -4020, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 33.0, "tickets": 60, "payout": 1980} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `0f54af82aa8eb9f0`／Learning State `2b1202bd68ea`</sub>
