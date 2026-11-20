# 2026-11-20 KSM_08 詳細反省（自動・実購入なし）

- 公式着順：12-9-5-7-10（上位3頭 [12, 9, 5]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 9／2着 4／3着 6；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "KSM_08.r2", "ticket_sha256": "0abdfa55a3b02320bec8502d8ccf8489d0de806d7d09403caf9511141e5b90ac", "frozen_at": "2026-11-20T13:16:21.878138+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 12／2着 5／3着 1；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "1225e1a5cd0eb403392e6d13b12137482f2e506667e121b8cb1eb238b0c4663c", "result_receipt_sha256": "f2f7c8b47cac30dafa07f7ad7aa2baab22887b23e5365245cfa4ef1070a9cb48", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "4ec1a85cb1fc5e5dffd1ce940a9aa725c23fdd428dc7797677012d51f5576a36", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 3980, "pfs": 25.5}, "effective_revision": "REVISION_2", "source_at": "2026-11-20T04:51:50.251402+00:00", "source_receipt_sha256": "ab86f41bbccb3324a614b29b697353357c6c1074e3832dcdabc88b9d4065ac2e", "signed_final_at": "2026-11-20T04:51:59.762345+00:00", "delivered_ticket_sha256": "8faa93f176ce6c1c23004ed43825c6077b3a0eab804b28065842762962fba012", "settled_ticket_sha256": "1225e1a5cd0eb403392e6d13b12137482f2e506667e121b8cb1eb238b0c4663c"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 9, "TPI-L": 9, "SRI-L": 9, "T3I-L": 11, "HPI-L": 6}, "ruled_neutral_share": 0.124} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（カントゥータ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 12, "second_pre_rank": 5, "third_pre_rank": 1, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [12, 9, 5], "rescues": [], "supports": ["P3_ROLE_CONFIRMED"], "misses": [ |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 12, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `e4021c649afe7710`／Learning State `3d6cf69bba40`</sub>
