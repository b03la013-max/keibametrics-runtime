# 2026-11-21 SAG_08 詳細反省（自動・実購入なし）

- 公式着順：8-5-1-2-3（上位3頭 [8, 5, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 7／2着 2／3着 6；W False・P2 True・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SAG_08.r2", "ticket_sha256": "58b853c00ecd941fa5ff929a53afbcf5161ddc49f9a0be53421879eca05f6f50", "frozen_at": "2026-11-21T18:25:03.120300+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 1／3着 6；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "4f6293dc61a2a2fdd74ba89156ecfb79bb0f31b9e0ca8e4dcd47ce744b060ece", "result_receipt_sha256": "384bdc5487595e5603c211388658b0e8c50c8dffd2ca1ad1bdc375e80c33305e", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "f49dbdb82f9603a06328fafcc08214f66c5ed397d44d5613b5ee68690e76c1d7", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-21T10:00:14.390168+00:00", "source_receipt_sha256": "acb71b8b3df7f0220c00cbaa45b29285c9bba0f7473dcd23fcea61ac6b9cd03b", "signed_final_at": "2026-11-21T10:00:23.769986+00:00", "delivered_ticket_sha256": "6e7ce6330b4acf5b09e2594230310dbbc88a3ec397059045de3ca4461a481c24", "settled_ticket_sha256": "4f6293dc61a2a2fdd74ba89156ecfb79bb0f31b9e0ca8e4dcd47ce744b060ece"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 6, "SRI-L": 5, "T3I-L": 6, "HPI-L": 6}, "ruled_neutral_share": 0.117} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 1, "third_pre_rank": 6, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 5, 1], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `56c3af9d95241768`／Learning State `2de744882945`</sub>
