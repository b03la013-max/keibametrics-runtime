# 2026-11-25 NGY_08 詳細反省（自動・実購入なし）

- 公式着順：4-3-7-9-1（上位3頭 [4, 3, 7]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 4／2着 1／3着 8；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_08.r2", "ticket_sha256": "2cc4f594ddc9ab99fc8de858be0b969a7d19a9f1e0f665fa39f9ba8eaad8d4b5", "frozen_at": "2026-11-25T17:50:17.358890+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 4／3着 3；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 840／損益 -5160／PFS 14.0%
- 参照：{"final_receipt_sha256": "c82c7cc416dedb39de86fc9081168ed217e42008d65910d3c23f68c56a727704", "result_receipt_sha256": "25ab93923f1b44a723a6f0dce3a5e4bc999f8c1f8628f40815ae905c333f0176", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "7b94bb2ccd6dd2d88f697355778267cfe9821529c6d268e5e4103d231b2f0ac5", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 1400, "pfs": 9.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T09:25:13.262707+00:00", "source_receipt_sha256": "d1455f09967502e6c9fea7460398a92a65142a027c1341b55da42036483b12e4", "signed_final_at": "2026-11-25T09:25:26.093753+00:00", "delivered_ticket_sha256": "c895f45f6c55a0957c79109292c65ca2bf56f21bed21005dfb67a2bbfbb34337", "settled_ticket_sha256": "c82c7cc416dedb39de86fc9081168ed217e42008d65910d3c23f68c56a727704"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（スカイレックス）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 4, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [4, 3, 7], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 14.0, "profit_loss": -5160, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 14.0, "tickets": 60, "payout": 840} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `b245b9a16795036a`／Learning State `a1f68fa48f47`</sub>
