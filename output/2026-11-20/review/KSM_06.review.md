# 2026-11-20 KSM_06 詳細反省（自動・実購入なし）

- 公式着順：1-10-5-7-6（上位3頭 [1, 10, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 5／2着 8／3着 4；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KSM_06.r2", "ticket_sha256": "c6bc59677510d54a19d914f2445b717cbcae6766da478eff1c20faf8f65e839b", "frozen_at": "2026-11-20T12:11:09.699074+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 7／2着 6／3着 9；W False・P2 True・P3 True
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "4e50ad8ac19696ad79f39656056030ecaa4058cc6fd110f3efc55a3c8b9d8560", "result_receipt_sha256": "1077aed8ab8376bc6b6e1b2188b12c84d116a8731c72f4c660fa75e76c92d639", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "a33f0efa6e95207a8e725a81465e699bb333c9d524e543d4ccd2aa777c0db2da", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-20T03:13:30.862166+00:00", "source_receipt_sha256": "1e54d74273432e655f7ec2fdc49d37805315620d68bda8119a405e98fa10e72a", "signed_final_at": "2026-11-20T03:13:38.238141+00:00", "delivered_ticket_sha256": "ef1f9d844c8443b31ae80217832bbd65ac4e33d181d5571d7bce19334b577c93", "settled_ticket_sha256": "4e50ad8ac19696ad79f39656056030ecaa4058cc6fd110f3efc55a3c8b9d8560"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 6, "TPI-L": 6, "SRI-L": 8, "T3I-L": 7, "HPI-L": 7}, "ruled_neutral_share": 0.111} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補5頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 7, "second_pre_rank": 6, "third_pre_rank": 9, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 10, 5], "rescues": [], "supports": ["P3_ROLE_CONFIRMED"], "misses": [ |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 7, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `5f7a3b7d8ac541aa`／Learning State `e4f4e5e6fa05`</sub>
