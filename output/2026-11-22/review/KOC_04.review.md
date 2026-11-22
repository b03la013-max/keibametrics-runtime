# 2026-11-22 KOC_04 詳細反省（自動・実購入なし）

- 公式着順：8-6-2-3-4（上位3頭 [8, 6, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 2／2着 5／3着 3；W False・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KOC_04.r2", "ticket_sha256": "63f0a5e49bb98e84789efd7f31341429cbeeb44ae5862a91014f9057a454218b", "frozen_at": "2026-11-22T16:25:01.762985+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 8／2着 3／3着 4；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "0680435a4fd5a47422e3fdd3f4f6e44bf629c175ea67c660dcfe397cfab4b61e", "result_receipt_sha256": "a290c69025110d21d166291a6e10c71de06f13c13836fe7a5fd1eaff5a098684", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "9326d11b9866721508b7163af264355df0de197cd14657ced7984e8cda3e3b6d", "signed_final_ticket_count": 105, "signed_final_total_investment": 10500, "signed_final_settlement": {"invest": 10500, "refund": 0, "effective_invest": 10500, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-22T07:28:40.775377+00:00", "source_receipt_sha256": "d5b9211397c75973ea6397facd939a8078cf51cc42c83b73d4bc966fc6c0c7bb", "signed_final_at": "2026-11-22T07:28:50.988961+00:00", "delivered_ticket_sha256": "fa5d55a6a221793f941be98efe989c4434118f66448e499b4b1ceafe9591bb0e", "settled_ticket_sha256": "0680435a4fd5a47422e3fdd3f4f6e44bf629c175ea67c660dcfe397cfab4b61e"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 7, "TPI-L": 7, "SRI-L": 8, "T3I-L": 8, "HPI-L": 7}, "ruled_neutral_share": 0.078} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 8, "second_pre_rank": 3, "third_pre_rank": 4, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [8, 6, 2], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONFIRMED"], "mi |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 8, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `23a79938b7489bea`／Learning State `65da6e59e074`</sub>
