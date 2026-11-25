# 2026-11-25 SON_02 詳細反省（自動・実購入なし）

- 公式着順：3-7-1-8-4（上位3頭 [3, 7, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 5／2着 6／3着 4；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 1600／返還 0／払戻 0／損益 -1600／PFS 0.0%
- 参照：{"revision": "SON_02.r2", "ticket_sha256": "c2320e4acf0c3d24cf9a346b80bbff75985ba2c589149de25127458d71d7252c", "frozen_at": "2026-11-25T10:25:08.096052+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 10／2着 3／3着 4；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "c76763d6192c74bee089a29f3520576d1b9522ec43714c6fd4fc958c9409ed91", "result_receipt_sha256": "a5250044ee376666d3b8042f809cd4ed3addc1bb4599349f14f37dfe14bc0c77", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "2f68ce4fae1b59a87eb948870f8d2c1ee5cc1a6ee3301b47e02a009d91702c41", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 22520, "pfs": 170.6}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T02:00:18.930381+00:00", "source_receipt_sha256": "e42be957bcdc749cb8f573832e0c1910dfedc7019fbea0960ebc5252dda6cfc2", "signed_final_at": "2026-11-25T02:00:29.947388+00:00", "delivered_ticket_sha256": "f4f4ba1fd0ed14f2848713c2adf7a45493189f879c5125b86de2e67130ace9ad", "settled_ticket_sha256": "c76763d6192c74bee089a29f3520576d1b9522ec43714c6fd4fc958c9409ed91"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 10, "TPI-L": 9, "SRI-L": 10, "T3I-L": 10, "HPI-L": 8}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 10, "second_pre_rank": 3, "third_pre_rank": 4, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 7, 1], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 10, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `2ed5280a163b7808`／Learning State `157a5d7d77c5`</sub>
