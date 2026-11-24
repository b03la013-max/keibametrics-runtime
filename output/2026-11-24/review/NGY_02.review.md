# 2026-11-24 NGY_02 詳細反省（自動・実購入なし）

- 公式着順：8-12-4-7-6（上位3頭 [8, 12, 4]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 7／2着 6／3着 9；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_02.r2", "ticket_sha256": "7df66ff3e072148c41329ac63726fde84f972f5d29c7d0e186124cfb527d3ca7", "frozen_at": "2026-11-24T14:16:30.443223+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 12／2着 2／3着 9；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "96a458b5de4a3c0d0da7dfaf80f4798525a05c7d421b9faeb2776d24d4d0f57e", "result_receipt_sha256": "77082694380d204cbee8952dd4ce419bf1d72e0489d5525ba9ce45a8de1f8135", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "1903ee097fa3a4f05d21cec6ec01a1322cb04299b1dcc090dba7b1de580a644e", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T05:53:25.392070+00:00", "source_receipt_sha256": "36d05a0a0354e6e8ea00e18fdcaaf234a29ec15f2199a1e50568363b42a3c047", "signed_final_at": "2026-11-24T05:53:39.565774+00:00", "delivered_ticket_sha256": "3f11282cdb57e3ba45b3f55999c1cd73412a617c248a103d11c7cfd43556df58", "settled_ticket_sha256": "96a458b5de4a3c0d0da7dfaf80f4798525a05c7d421b9faeb2776d24d4d0f57e"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 12, "TPI-L": 12, "SRI-L": 12, "T3I-L": 12, "HPI-L": 10}, "ruled_neutral_share": 0.075} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 12, "second_pre_rank": 2, "third_pre_rank": 9, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 12, 4], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 12, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `a0dc18a4cb546969`／Learning State `7bcc09cbfc47`</sub>
