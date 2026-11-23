# 2026-11-23 SAG_03 詳細反省（自動・実購入なし）

- 公式着順：2-8-9-1-4（上位3頭 [2, 8, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 8／2着 4／3着 9；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SAG_03.r2", "ticket_sha256": "3e21e4145a849cd521ed4f8219013422c7adca55418c5f1f82cf0e5b9f6db914", "frozen_at": "2026-11-23T15:50:12.313216+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 9／2着 1／3着 8；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "ded98680e75b07e08fdfc8bbc0f74a541e27c72183c6f19624a0a789af8e36fd", "result_receipt_sha256": "47243d4b756ae0ca7cb9f51c65df530555cbde94fb0f02d058ca0213a8f756a1", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "84516ea89520ddbde1b3311310060fad35d2f7e355f2f42c2e84c08a509a6499", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-23T06:55:41.218641+00:00", "source_receipt_sha256": "fe1cfbc7b768ca1105c033903aaacc765fb1f5602520a3eccad1a171c7fd6157", "signed_final_at": "2026-11-23T06:55:52.570788+00:00", "delivered_ticket_sha256": "27e0e60a94fae2e1572591d7b1f068149ad777014d03efbb28fe053bf010676d", "settled_ticket_sha256": "ded98680e75b07e08fdfc8bbc0f74a541e27c72183c6f19624a0a789af8e36fd"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 8, "TPI-L": 8, "SRI-L": 9, "T3I-L": 8, "HPI-L": 7}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 9, "second_pre_rank": 1, "third_pre_rank": 8, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [2, 8, 9], "rescues": [], "supports": ["P2_ROLE_CONFIRMED"], "misses": [" |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 9, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `2da9591b3d05cbce`／Learning State `edcceafa67a1`</sub>
