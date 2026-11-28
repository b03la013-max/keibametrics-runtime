# 2026-11-28 SAG_09 詳細反省（自動・実購入なし）

- 公式着順：1-3-4-10-8（上位3頭 [1, 3, 4]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 6／2着 8／3着 5；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 0；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 0／損益 -900／PFS 0.0%
- 参照：{"revision": "SAG_09.r2", "ticket_sha256": "c5dc3b691d439f09f341dfde8fd9de21fe2cb4cc60877729d9ec9e315b8bdfae", "frozen_at": "2026-11-28T18:20:02.302634+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 5／2着 11／3着 4；W False・P2 False・P3 True
- Top3捕捉 0／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "c288d0ac81e8432d52e73691e643c6d9feb5e718241673fba0a426b2672eb428", "result_receipt_sha256": "89d3dbc9ef54b74fb107285e53186ddb82caaa7670d3959eb5886e37e5be2e3c", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "6897946f4c162c856d8263fbf01746b056406f82ad7180950e94d194c9f2bca0", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-28T09:22:33.037838+00:00", "source_receipt_sha256": "7cc877d664176fc15b932c8a9501d1be28b939fb9a277f2fa94758fa8f09d11a", "signed_final_at": "2026-11-28T09:22:45.264143+00:00", "delivered_ticket_sha256": "76012fbe4f76a3a4dde4e4004a31e3bcd75254956911ac167f01eb906a19c5e2", "settled_ticket_sha256": "c288d0ac81e8432d52e73691e643c6d9feb5e718241673fba0a426b2672eb428"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 5, "T3I-L": 6, "HPI-L": 4}, "ruled_neutral_share": 0.072} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 11, "third_pre_rank": 4, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 3, 4], "rescues": ["WINNER_ROLE_RESCUE"], "supports": ["P3_ROLE_CONFI |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `787a68510f8b2c18`／Learning State `2c113cb65a5e`</sub>
