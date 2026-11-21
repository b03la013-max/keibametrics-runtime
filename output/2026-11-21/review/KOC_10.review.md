# 2026-11-21 KOC_10 詳細反省（自動・実購入なし）

- 公式着順：1-2-5-9-4（上位3頭 [1, 2, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 5／2着 4／3着 7；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KOC_10.r2", "ticket_sha256": "8a903b80c3f485f68f46c2a4d473003a3d4cfeabd1ac28437e8072d780884e20", "frozen_at": "2026-11-21T19:05:04.146067+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 5／2着 3／3着 9；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "183dad15f37e483070e844338e3de2062a322043c60faf8b583e876a7b737b2a", "result_receipt_sha256": "d4a237d24244bc91e6cb25114a8fa24d8602a6cd610aeb73943e74688cb8ec0e", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "fc6d6f0a0ca65d2a2978d9c8a4fa3998a3976cc7c67719f51e6fd8588936c39b", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-21T10:40:14.384209+00:00", "source_receipt_sha256": "7e608f18c7c5dbcab444225231bf4caaebd4dbbec2fa2cf728f250d87db688bb", "signed_final_at": "2026-11-21T10:40:22.627513+00:00", "delivered_ticket_sha256": "e98f000acf9b5331054d5692a9b66de53a07ca474c53157074d7dad6c5978d04", "settled_ticket_sha256": "183dad15f37e483070e844338e3de2062a322043c60faf8b583e876a7b737b2a"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 5, "T3I-L": 7, "HPI-L": 5}, "ruled_neutral_share": 0.117} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 3, "third_pre_rank": 9, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [1, 2, 5], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "ORDERED_PAIR_CONFIRMED"] |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `c4276ee474c3bfc9`／Learning State `8d58bdbe15e1`</sub>
