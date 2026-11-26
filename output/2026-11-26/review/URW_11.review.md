# 2026-11-26 URW_11 詳細反省（自動・実購入なし）

- 公式着順：13-5-2-3-4（上位3頭 [13, 5, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3

## PAPER

- 1着の事前順位 7／2着 12／3着 10；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "URW_11.r2", "ticket_sha256": "989034bb565250fefc5894512e547f89920b0efcd9a71309183fe0d8bb9f8c26", "frozen_at": "2026-11-26T17:00:03.102389+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 5／2着 12／3着 10；W False・P2 False・P3 True
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "45c5c49c38f8695619261ae7046374c5f437fedd109c8aad9ac7be9b58e4fe55", "result_receipt_sha256": "9edd71650b1bc80adc698d909011ab6c08ab664740e95113019af61ae70e0429", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "e67732de77ca7d235a4fbf68d1ec29b7658079217a9e79a7fe6b87b4a05c89d6", "signed_final_ticket_count": 180, "signed_final_total_investment": 18000, "signed_final_settlement": {"invest": 18000, "refund": 0, "effective_invest": 18000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T08:36:13.769261+00:00", "source_receipt_sha256": "cfd3f3d6df3b7c35cc8da4f37a9918ab7dd3be777015019c88a49fc8195496ef", "signed_final_at": "2026-11-26T08:36:28.342317+00:00", "delivered_ticket_sha256": "ccb015c00b341f1170d9d591e378c52c16e4b9f06b643b879af50bd74af57463", "settled_ticket_sha256": "45c5c49c38f8695619261ae7046374c5f437fedd109c8aad9ac7be9b58e4fe55"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 4, "SRI-L": 7, "T3I-L": 4, "HPI-L": 3}, "ruled_neutral_share": 0.007} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補8頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 12, "third_pre_rank": 10, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [13, 5, 2], "rescues": [], "supports": [], "misses": ["WINNER_ROLE_NOT_KR |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `a44151a0214a8278`／Learning State `acc4fae11150`</sub>
