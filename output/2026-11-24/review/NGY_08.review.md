# 2026-11-24 NGY_08 詳細反省（自動・実購入なし）

- 公式着順：5-12-11-3-9（上位3頭 [5, 12, 11]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 4／2着 2／3着 1；W False・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 580／損益 -120／PFS 82.9%
- 参照：{"revision": "NGY_08.r2", "ticket_sha256": "7c04375e03f7cb4e8e94e9fbedbca0c8441b5a0257b4ed9f49a4b48fa9c1b490", "frozen_at": "2026-11-24T17:50:16.693157+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 2／3着 1；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1840／損益 -4160／PFS 30.7%
- 参照：{"final_receipt_sha256": "b68e6cd8cc20ec034e21f2f3fab5ecdcf8de00dc9076f851d4ccb73c43d72db1", "result_receipt_sha256": "eac023b880a1ff911df5b8c2ffb2a0cdabefa15d543d225a4e2bbabb94e0f14d", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "51dfadbfcbb2bdbe2f5a19e27c80fd604d512aa7bd80449fec550e8d8fe19d55", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 5030, "pfs": 32.2}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T09:25:18.932802+00:00", "source_receipt_sha256": "8b80261ec34df5dcc5d0f90b57e79783f8297205b8de19f478c3422559f0f6ab", "signed_final_at": "2026-11-24T09:25:34.056562+00:00", "delivered_ticket_sha256": "1dff046e292561e945e066af406d7b2e31541ee838d73a1c6428f90422dc6950", "settled_ticket_sha256": "b68e6cd8cc20ec034e21f2f3fab5ecdcf8de00dc9076f851d4ccb73c43d72db1"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 3, "HPI-L": 3}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ヤマカンドリーミン）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 2, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 12, 11], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROL |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 30.7, "profit_loss": -4160, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 30.7, "tickets": 60, "payout": 1840} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `e1af11c27ff8d353`／Learning State `b6b8fb293957`</sub>
