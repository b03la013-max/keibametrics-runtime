# 2026-11-23 MIZ_05 詳細反省（自動・実購入なし）

- 公式着順：7-1-3-6-4（上位3頭 [7, 1, 3]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3

## PAPER

- 1着の事前順位 9／2着 3／3着 2；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "MIZ_05.r2", "ticket_sha256": "af55d5afb85f635812547e7d499441eeb7c6dfb1b3e3ab28d87165c5fa867af0", "frozen_at": "2026-11-23T13:15:12.620196+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 9／2着 7／3着 3；W False・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "4274af31364f5cff58e66d2af39f53b2fde825e8f14e690dcaedc360a4365985", "result_receipt_sha256": "21edf6eba02134fea12fa61a703bb19d54497ecae03ac683ee3a0aeb42b10191", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "0cbb9253d44004ffa92f0aae7d6ac75de1b644f2acac1399ff00dfe543637b54", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-23T04:51:05.240895+00:00", "source_receipt_sha256": "7eff1588af7d894a1bf070417c2b6128454dd7f46ffaca2bf49d960274ed17a3", "signed_final_at": "2026-11-23T04:51:17.949667+00:00", "delivered_ticket_sha256": "896aa4ad4edf3b5cabc9a54467310580bdcb19d1cf06adb3349bd8c71cbce64d", "settled_ticket_sha256": "4274af31364f5cff58e66d2af39f53b2fde825e8f14e690dcaedc360a4365985"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 6, "TPI-L": 7, "SRI-L": 6, "T3I-L": 9, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（リンクルリンク）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 9, "second_pre_rank": 7, "third_pre_rank": 3, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [7, 1, 3], "rescues": ["P2_ROLE_RESCUE"], "supports": ["P3_ROLE_CONFIRMED |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 9, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `b7d2c5347beb09fe`／Learning State `dc6c209450cc`</sub>
