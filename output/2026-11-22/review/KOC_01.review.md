# 2026-11-22 KOC_01 詳細反省（自動・実購入なし）

- 公式着順：5-9-8-2-7（上位3頭 [5, 9, 8]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3

## PAPER

- 1着の事前順位 7／2着 4／3着 2；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KOC_01.r2", "ticket_sha256": "b94eb805a4d7de44c099a930b70d92db3aad6683007b29cb6169ce782f4da151", "frozen_at": "2026-11-22T14:45:11.087472+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 8／3着 1；W False・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "cf184e292546888167de05e8b315401948cd4d24cf772b6c4c57c0f89005a0bf", "result_receipt_sha256": "61e6faf47ce79679d6f20ab3ae5a0afe463cc79e1eb9df0e951287397b5ef5df", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "f9aa5a444f2f875806eb8e5e0ac0620b0794c022f68927b363dbd360e8aa7663", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-22T05:48:18.458146+00:00", "source_receipt_sha256": "8b529c6e41c4fd8000881b478df621fe42f7073c1a48e9e9f96bd4395e5ac6fa", "signed_final_at": "2026-11-22T05:48:29.687078+00:00", "delivered_ticket_sha256": "c973b17f9197a4113546702eed9c589dc02597ef6fd8abc806f4bd595ba9adf5", "settled_ticket_sha256": "cf184e292546888167de05e8b315401948cd4d24cf772b6c4c57c0f89005a0bf"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 6, "SRI-L": 4, "T3I-L": 2, "HPI-L": 8}, "ruled_neutral_share": 0.076} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 8, "third_pre_rank": 1, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 9, 8], "rescues": ["P2_ROLE_RESCUE"], "supports": ["P3_ROLE_CONFIRMED |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `79d5119aaa2ec84e`／Learning State `65e79d178f9e`</sub>
