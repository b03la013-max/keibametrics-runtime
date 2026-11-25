# 2026-11-25 SON_10 詳細反省（自動・実購入なし）

- 公式着順：3-7-11-8-2（上位3頭 [3, 7, 11]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3

## PAPER

- 1着の事前順位 8／2着 7／3着 11；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SON_10.r2", "ticket_sha256": "23b1e59211abea3c1bc0f954aaab2384181db7f979e712165ebc664cd8a84698", "frozen_at": "2026-11-25T14:50:02.937305+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 10／2着 9／3着 7；W False・P2 False・P3 True
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "d6f8128cd165001370471439e31b9158af51d52123918d2bdadd033979008fb9", "result_receipt_sha256": "ddb3d6c9c65748eae8b0137743bad801f109fedcd822af9e40465f53a4955824", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "b5f3a315f1a62243a02373def1124bbe5ccaf7fcce404092e6d8a9daedf64503", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T06:27:04.475179+00:00", "source_receipt_sha256": "76e37f39da981c8606c3d9581ebd40271f9a3980c2f20d5dbc82dd31d6692bbf", "signed_final_at": "2026-11-25T06:27:16.679897+00:00", "delivered_ticket_sha256": "fcd791b1b0e07a58234c2ad326509a69a9538fc78161c2d1a473a5097382bcfb", "settled_ticket_sha256": "d6f8128cd165001370471439e31b9158af51d52123918d2bdadd033979008fb9"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 10, "TPI-L": 10, "SRI-L": 10, "T3I-L": 12, "HPI-L": 10}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補7頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 10, "second_pre_rank": 9, "third_pre_rank": 7, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 7, 11], "rescues": ["P2_ROLE_RESCUE"], "supports": ["P3_ROLE_CONFIRME |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 10, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `a3b7cf9356144cba`／Learning State `94b9552395c1`</sub>
