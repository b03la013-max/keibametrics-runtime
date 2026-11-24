# 2026-11-24 NGY_06 詳細反省（自動・実購入なし）

- 公式着順：4-7-9-5-12（上位3頭 [4, 7, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3

## PAPER

- 1着の事前順位 3／2着 9／3着 2；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_06.r2", "ticket_sha256": "e789cccd94f22a78e05b06c607110763b6886010a158dc3b4912ecddfcc36a42", "frozen_at": "2026-11-24T16:35:18.179072+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 7／2着 10／3着 5；W False・P2 False・P3 True
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "12661c2812e40ba563f24a7ecf4d7cf684bdd80e417e9104dcacbeb50b5cb14a", "result_receipt_sha256": "77825576373b1f7b16714ec12d9e3577058a3d9e7ba9b01a84c12eec9ff97978", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "ef6242fe9d83ef9b4a3f1df5ab50c6fd9e0068611454db400ea7e914a8d8bce5", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T08:12:15.845967+00:00", "source_receipt_sha256": "17c1fb2895dfe24e2fc0d96da886b5f4f230db7368ac16e0f1fca8d96776ed1e", "signed_final_at": "2026-11-24T08:12:29.790595+00:00", "delivered_ticket_sha256": "f2957f505972e31532edb7d09a0eaeb50d52192ae3b007a9054e9a21ac9c9f0e", "settled_ticket_sha256": "12661c2812e40ba563f24a7ecf4d7cf684bdd80e417e9104dcacbeb50b5cb14a"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 8, "T3I-L": 7, "HPI-L": 3}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 7, "second_pre_rank": 10, "third_pre_rank": 5, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [4, 7, 9], "rescues": [], "supports": [], "misses": ["WINNER_ROLE_NOT_KRS |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 7, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `c815c34f3216a009`／Learning State `ae3a6295c46b`</sub>
