# 2026-11-25 URW_05 詳細反省（自動・実購入なし）

- 公式着順：12-9-2-10-6（上位3頭 [12, 9, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 13／2着 1／3着 9；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "URW_05.r2", "ticket_sha256": "110e59547f8a03179e1e42114206543793e5ee0ba16ddca5e54b0c4b104e638c", "frozen_at": "2026-11-25T13:35:12.908992+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 7／2着 3／3着 10；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "823298f159a478f21b5be8621b7c84d3ca4d7cf0aa68082c136ef9f76a8f2acb", "result_receipt_sha256": "9385a203d336f7bb2358b8dc3d241e45348723750d4a6a14199c102ad87563f0", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "67224418bb2676d72a8cbda6318a38669cb141e5964d3b6bfbff2b07ebad8a7a", "signed_final_ticket_count": 168, "signed_final_total_investment": 16800, "signed_final_settlement": {"invest": 16800, "refund": 0, "effective_invest": 16800, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T05:10:17.197791+00:00", "source_receipt_sha256": "9794b1aa81a1dcd02bdbdf8627c712759ffaf7f3de9b9e006c57fc9973a5de8a", "signed_final_at": "2026-11-25T05:10:30.129470+00:00", "delivered_ticket_sha256": "bc5f0158b4c2d2ab1de6128339bbf3b196cb127e317ce1e34adb8c67d81194fc", "settled_ticket_sha256": "823298f159a478f21b5be8621b7c84d3ca4d7cf0aa68082c136ef9f76a8f2acb"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 2, "SRI-L": 1, "T3I-L": 6, "HPI-L": 1}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補5頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 7, "second_pre_rank": 3, "third_pre_rank": 10, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [12, 9, 2], "rescues": ["WINNER_ROLE_RESCUE", "ORDERED_PAIR_RESCUE"], "su |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 7, "alternative_signals_that_had_winner_top": ["F3S-L ranked the winner #1", "SRI-L ranked the winne | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `b7df8058a40bc59d`／Learning State `eef03253d488`</sub>
