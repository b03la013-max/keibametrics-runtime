# 2026-11-23 MIZ_06 詳細反省（自動・実購入なし）

- 公式着順：1-2-9-7-8（上位3頭 [1, 2, 9]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 7／3着 1；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 210／損益 -490／PFS 30.0%
- 参照：{"revision": "MIZ_06.r2", "ticket_sha256": "defbca59d4762a305ef02a451853b2f8bae8e963c5ac148aeac71ec26db6bd48", "frozen_at": "2026-11-23T13:50:02.748807+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 5／3着 2；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 3220／損益 -2780／PFS 53.7%
- 参照：{"final_receipt_sha256": "17def28d4a5bdc3f8c32e68a1a8785c22fd85ff32a24d1e57d48d09690c9f34b", "result_receipt_sha256": "97cd196ed31335c648262e03009b85936128ba0311b07f1c538ef598a53019db", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "21b44bce261d3675411620eb93090b43335c8354067ab5ea1604d2294aa85b8d", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 2810, "pfs": 21.3}, "effective_revision": "REVISION_2", "source_at": "2026-11-23T05:26:03.664297+00:00", "source_receipt_sha256": "97b06bb8f10ec925786fb10370de87840031b950e9cd0d326381ea812853f352", "signed_final_at": "2026-11-23T05:26:16.770364+00:00", "delivered_ticket_sha256": "44b2b30db20e1aa0c6f606fbf84bb0d20e25122461594a4127d9acbe25b7aa6a", "settled_ticket_sha256": "17def28d4a5bdc3f8c32e68a1a8785c22fd85ff32a24d1e57d48d09690c9f34b"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 1, "T3I-L": 6, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 5, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [1, 2, 9], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 53.7, "profit_loss": -2780, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 53.7, "tickets": 60, "payout": 3220} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `df3cb740eba0e9b9`／Learning State `1008902379a0`</sub>
