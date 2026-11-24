# 2026-11-24 NGY_09 詳細反省（自動・実購入なし）

- 公式着順：2-11-9-10-8（上位3頭 [2, 11, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 6／2着 1／3着 5；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_09.r2", "ticket_sha256": "cebd63afd40dfd5dd3f02a276a82825d31d15f2ce753c85684bdb66fa31e0136", "frozen_at": "2026-11-24T18:20:14.166065+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 9／2着 3／3着 11；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "1158d37eb55c655217fde48c9918cedf7ae18128b7bb5c231c9f8b04a3ee0e11", "result_receipt_sha256": "69ebaad16a18b266167ce9e35784dffedf9a1116c94f15638304476fcce3371b", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "e1da0ad3fb46179671ffb079456370bde520c2df038f1f7311c07ded737d8842", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T09:57:16.762691+00:00", "source_receipt_sha256": "61b70e7f257b7e9ee5cbc1a106a8a28c7b46ec41b2a748cc5d1f6d686e493e53", "signed_final_at": "2026-11-24T09:57:32.449547+00:00", "delivered_ticket_sha256": "bb5579d4f49ae579d607e2eb90c248362309b2fab871ec3cda2a39f778be1b2f", "settled_ticket_sha256": "1158d37eb55c655217fde48c9918cedf7ae18128b7bb5c231c9f8b04a3ee0e11"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 8, "TPI-L": 8, "SRI-L": 8, "T3I-L": 11, "HPI-L": 4}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 9, "second_pre_rank": 3, "third_pre_rank": 11, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [2, 11, 9], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "ORDERED_PAI |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 9, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `2b145202d425cc2e`／Learning State `f187931c11a6`</sub>
