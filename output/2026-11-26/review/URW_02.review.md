# 2026-11-26 URW_02 詳細反省（自動・実購入なし）

- 公式着順：3-7-12-13-1（上位3頭 [3, 7, 12]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 2／2着 3／3着 11；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "URW_02.r2", "ticket_sha256": "7b2e8c4676819881ffc087cc8d7c0f28f463b2dc16b8872aa0c85610a55131f7", "frozen_at": "2026-11-26T12:05:03.608449+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 5／3着 11；W False・P2 True・P3 True
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "44ddbefba2c726f1a4b60de3a7c8cbecb0c0940251e92be763891305c95de302", "result_receipt_sha256": "5c1f96c609ac4f63f4966266c980e146ebefd7c5ca0b61f6ccd5a515dbecba69", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "df2bd1ca72f3f4e695a85367f9e84a88d89719e0e049e33e094c6de6e64a6408", "signed_final_ticket_count": 168, "signed_final_total_investment": 16800, "signed_final_settlement": {"invest": 16800, "refund": 0, "effective_invest": 16800, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T03:41:08.936178+00:00", "source_receipt_sha256": "93aefa0f88973e9a9cf1d0cbe5efcc21b359f8f4e2b09d104fff7e9071bb98cb", "signed_final_at": "2026-11-26T03:41:21.697902+00:00", "delivered_ticket_sha256": "685a7a9c10d41d8d46c444b171e14d26efcf974c20e4b2749e8e6d15e71bc1b7", "settled_ticket_sha256": "44ddbefba2c726f1a4b60de3a7c8cbecb0c0940251e92be763891305c95de302"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 3, "T3I-L": 5, "HPI-L": 3}, "ruled_neutral_share": 0.005} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補5頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 5, "third_pre_rank": 11, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 7, 12], "rescues": ["WINNER_ROLE_RESCUE"], "supports": ["P2_ROLE_CONF |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `04e32e3e8eee7a2d`／Learning State `a2f6abfb0afc`</sub>
