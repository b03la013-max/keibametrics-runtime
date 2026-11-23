# 2026-11-23 MIZ_04 詳細反省（自動・実購入なし）

- 公式着順：10-1-8-3-4（上位3頭 [10, 1, 8]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 6／3着 3；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "MIZ_04.r2", "ticket_sha256": "efc047fd1adb2cd4e9a5b1b45d6900979a822a0ef3a037b52899ea799bd101e4", "frozen_at": "2026-11-23T12:40:04.004668+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 5／3着 3；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 2660／損益 -3340／PFS 44.3%
- 参照：{"final_receipt_sha256": "14148610e1c4372c868453bd27676ed3c2e3f2883747917b574eca5f844b8f87", "result_receipt_sha256": "aaabfe8a402210da4259ee8ef6f5938bb9c37f49c0d36150494d2b441a046c19", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "64a9e7a1c138bbc0bdcd9cd3ff96211b3b24f7d0c32fb7427a20cb2c47d889a8", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 1830, "pfs": 13.9}, "effective_revision": "REVISION_2", "source_at": "2026-11-23T04:16:14.858130+00:00", "source_receipt_sha256": "d8a7a3e4c56eb16c053ca668f9f2c4ac3b1113f9d05301e15525946642f8f0ee", "signed_final_at": "2026-11-23T04:16:26.385166+00:00", "delivered_ticket_sha256": "8f5422dcafcf8b35b790dac34be191054f5495b5217cd269ade62de0d6dd7ffe", "settled_ticket_sha256": "14148610e1c4372c868453bd27676ed3c2e3f2883747917b574eca5f844b8f87"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 1, "SRI-L": 2, "T3I-L": 6, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 5, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [10, 1, 8], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED", |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 44.3, "profit_loss": -3340, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 44.3, "tickets": 60, "payout": 2660} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `ce411acb07c8c279`／Learning State `7c0691455959`</sub>
