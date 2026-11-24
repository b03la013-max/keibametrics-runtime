# 2026-11-24 NGY_01 詳細反省（自動・実購入なし）

- 公式着順：5-2-10-12-7（上位3頭 [5, 2, 10]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 7／2着 5／3着 1；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_01.r2", "ticket_sha256": "66daf6c2d8822e808fae335e42b6793939cbcb1929715fe6bcae7c412d363e53", "frozen_at": "2026-11-24T13:46:36.532290+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 8／2着 5／3着 1；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "726d9bfc32c8deee030428610854512776936523b50adb538fa3d8b917c8c23a", "result_receipt_sha256": "05f0f7fb8fa6b9d1fa012e1fb5ce8709d3b1d010ed1933662b118cc7281b7213", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "67d8dd8d4d05b9f0cb7959e393ed0c4a61c8040e3dec1ad52bc8c4308ad16a4f", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T05:21:16.597325+00:00", "source_receipt_sha256": "726866cb1bd92b10bdf5fce12e780dac03e4089dbc2601a814d0a6004036a2dd", "signed_final_at": "2026-11-24T05:21:30.562817+00:00", "delivered_ticket_sha256": "c058f5a579cc9b7ccd9913ec4165d5dc619df608eb2c7e959b615da0f58dacd6", "settled_ticket_sha256": "726d9bfc32c8deee030428610854512776936523b50adb538fa3d8b917c8c23a"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 8, "TPI-L": 6, "SRI-L": 8, "T3I-L": 6, "HPI-L": 8}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 8, "second_pre_rank": 5, "third_pre_rank": 1, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 2, 10], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 8, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `14090232af8bdf7e`／Learning State `5ec761dab5a4`</sub>
