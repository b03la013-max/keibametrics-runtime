# 2026-11-22 KOC_07 詳細反省（自動・実購入なし）

- 公式着順：6-9-1-11-5（上位3頭 [6, 9, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 3／3着 2；W True・P2 False・P3 False
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 2060／損益 1360／PFS 294.3%
- 参照：{"revision": "KOC_07.r2", "ticket_sha256": "95dd46db4584a0e361025719f2cb0c5d05cb5691fcca078deabe987066ac8465", "frozen_at": "2026-11-22T18:00:10.172263+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 4；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 2200／損益 -3800／PFS 36.7%
- 参照：{"final_receipt_sha256": "a19f1eeb5a023d7e2a440f734046e780db78b3cb775d8a74a9c1fee2a034a0b2", "result_receipt_sha256": "0b60e7a27ee87c40b146117a708e7435a759eec97a8d3839d0636b38927902b6", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "a1af9e2bcb6a7c930fc534fac6f2ef192a4bce8f990f66ff7d65248b3ff23627", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 4350, "pfs": 30.2}, "effective_revision": "REVISION_2", "source_at": "2026-11-22T09:36:15.676936+00:00", "source_receipt_sha256": "7ac511c5f85314ecf366c23af7ccbbcac266a1c2bc706429da5b3d0eacaabe68", "signed_final_at": "2026-11-22T09:36:27.374605+00:00", "delivered_ticket_sha256": "15ee11b737bc7bf635c51f74e3f3b1ff44d375e8dc7596822e46278b42458dac", "settled_ticket_sha256": "a19f1eeb5a023d7e2a440f734046e780db78b3cb775d8a74a9c1fee2a034a0b2"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 2, "SRI-L": 1, "T3I-L": 5, "HPI-L": 1}, "ruled_neutral_share": 0.075} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [6, 9, 1], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 36.7, "profit_loss": -3800, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 36.7, "tickets": 60, "payout": 2200} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `cd133c83b5675e2e`／Learning State `bfd178447573`</sub>
