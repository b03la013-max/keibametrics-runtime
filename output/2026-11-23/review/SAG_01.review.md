# 2026-11-23 SAG_01 詳細反省（自動・実購入なし）

- 公式着順：8-4-6-2-5（上位3頭 [8, 4, 6]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 7／2着 1／3着 9；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 800／返還 0／払戻 0／損益 -800／PFS 0.0%
- 参照：{"revision": "SAG_01.r2", "ticket_sha256": "f110c70367f3a73113700d360d798305c8fe5f9542f6449387aa63ddf83b237c", "frozen_at": "2026-11-23T14:45:16.874695+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 5／2着 1／3着 8；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "bad7c5e1b44e61e063b8d4ee9c213d97f5241f6d9a4271c0d0595c8c11bddc07", "result_receipt_sha256": "d6198456fe150ccd1c49b56e51604e82c0ca80d39f7b8c01d525d64f7d14b084", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "052357861ebb91aae04ff48a87e8ccd71d67ff5122444a208c2e66a52ce9ddf6", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-23T05:46:39.265567+00:00", "source_receipt_sha256": "4a498eb8eb5c625b2b293a10c1f7ae3d9bdc865df7a7402ea5be1276a505cd5a", "signed_final_at": "2026-11-23T05:46:51.141893+00:00", "delivered_ticket_sha256": "84472b2cd6188588115f9ea9240fe6af12cf2cb052b834208ffe95cc6ded79cd", "settled_ticket_sha256": "bad7c5e1b44e61e063b8d4ee9c213d97f5241f6d9a4271c0d0595c8c11bddc07"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 6, "TPI-L": 6, "SRI-L": 6, "T3I-L": 7, "HPI-L": 5}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（ヴィーナスベリーナ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 1, "third_pre_rank": 8, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [8, 4, 6], "rescues": [], "supports": ["P2_ROLE_CONFIRMED"], "misses": ["WINNER_ROLE_ |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `3a47639b9ccb0fb2`／Learning State `879df8df6d71`</sub>
