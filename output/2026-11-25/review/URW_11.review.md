# 2026-11-25 URW_11 詳細反省（自動・実購入なし）

- 公式着順：9-1-8-6-3（上位3頭 [9, 1, 8]）
- 距離帯：MIDDLE(1701-2100)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 2／2着 4／3着 8；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "URW_11.r2", "ticket_sha256": "4fb12b91154f6561076b9de681fa0e6e48b2672421cb67e23a853c2775c8a654", "frozen_at": "2026-11-25T17:00:17.082240+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 8／2着 3／3着 7；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "63cbb28f64072bb0cc6224a24e127399e4b61da04a489aea6cfcb5a513feebb0", "result_receipt_sha256": "8469b374b20aa09caf621042a3d3eff6d4e411a122aa177bc8204b1b0c33c1ce", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "440dbd18cccda40e798200e5215a1a91b164f89ff1648f13444016be318893a3", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T08:37:12.780556+00:00", "source_receipt_sha256": "1054370053dd2d1d7b7f6bde9b8faff98e875e3f2a5afe34ad6f6e2b138fdb96", "signed_final_at": "2026-11-25T08:37:23.581174+00:00", "delivered_ticket_sha256": "cb4e555353dbb0cf2f44585becf6f2f9857f27c2f8d9ae734a84804501ece451", "settled_ticket_sha256": "63cbb28f64072bb0cc6224a24e127399e4b61da04a489aea6cfcb5a513feebb0"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 5, "SRI-L": 4, "T3I-L": 9, "HPI-L": 7}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 8, "second_pre_rank": 3, "third_pre_rank": 7, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [9, 1, 8], "rescues": [], "supports": ["P2_ROLE_CONFIRMED"], "misses": [" |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 8, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `753dda27b74cae8b`／Learning State `f3ab094f559a`</sub>
