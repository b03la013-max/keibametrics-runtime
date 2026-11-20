# 2026-11-20 KSM_02 詳細反省（自動・実購入なし）

- 公式着順：2-4-9-5-10（上位3頭 [2, 4, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 5／3着 2；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 800／返還 0／払戻 120／損益 -680／PFS 15.0%
- 参照：{"revision": "KSM_02.r2", "ticket_sha256": "8c8f3175fce7d9730dd623dcfffb3aec421ddb6fc98d68341ce67856aae43f41", "frozen_at": "2026-11-20T10:12:07.490498+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 3／3着 2；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 3220／損益 -2780／PFS 53.7%
- 参照：{"final_receipt_sha256": "b726f4419697bc460f981bd3970e1f624b60db19667b33a1e0cb9bce94a5271b", "result_receipt_sha256": "a8159ca48bc3f6d857497126e2a6fa24c23a20c1a55fe093649482a04fb92cee", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "d7e1c8130f4092bc9fa02cade3488d2be5574d0f443ef1cd9f2be46f684de5b3", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 3220, "pfs": 24.4}, "effective_revision": "REVISION_2", "source_at": "2026-11-20T01:46:11.496253+00:00", "source_receipt_sha256": "028acf577407cd521b806972b5c59c804ec4940ed8d8a852b193171fe94f502d", "signed_final_at": "2026-11-20T01:46:19.367309+00:00", "delivered_ticket_sha256": "ecd440ecb6d1408ec36b2c29e75b63efe0f3b39ba2889c22cc199e5b59ef910d", "settled_ticket_sha256": "b726f4419697bc460f981bd3970e1f624b60db19667b33a1e0cb9bce94a5271b"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.117} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 3, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [2, 4, 9], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 53.7, "profit_loss": -2780, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 53.7, "tickets": 60, "payout": 3220} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `5bbef82949893782`／Learning State `f2c5042d2303`</sub>
