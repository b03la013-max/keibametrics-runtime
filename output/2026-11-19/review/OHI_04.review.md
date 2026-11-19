# 2026-11-19 OHI_04 詳細反省（自動・実購入なし）

- 公式着順：8-10-14-1-12（上位3頭 [8, 10, 14]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 2／2着 3／3着 1；W False・P2 False・P3 False
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 490／損益 -210／PFS 70.0%
- 参照：{"revision": "OHI_04.r2", "ticket_sha256": "654a30b62b556a966cef42d884ff3bf0d2e98ed1f3e1b146f14b0cc97defc5d8", "frozen_at": "2026-11-19T15:22:01.457111+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 12／2着 1／3着 5；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "50f0192b238298fac2163cd1bac9ae20d98edd2ebe5701666f4183c07fa5c79b", "result_receipt_sha256": "79f67907abea699b51cdad7838b96bd19692032551c6a7a589e8414d4d285a6c", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "297fc351287a86a6bb91ed32957561ff081ce7e111253c9a6adee1db652e6d0d", "signed_final_ticket_count": 168, "signed_final_total_investment": 16800, "signed_final_settlement": {"invest": 16800, "refund": 0, "effective_invest": 16800, "payout": 360, "pfs": 2.1}, "effective_revision": "REVISION_2", "source_at": null, "signed_final_at": "2026-11-19T06:58:34.373411+00:00", "delivered_ticket_sha256": "b997bc1353e2e50a411ac9ef074c32bc6536aec72b662c7335c810b058c2b8d3", "settled_ticket_sha256": "50f0192b238298fac2163cd1bac9ae20d98edd2ebe5701666f4183c07fa5c79b"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 8, "T3I-L": 7, "HPI-L": 4}, "ruled_neutral_share": 0.119} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 12, "second_pre_rank": 1, "third_pre_rank": 5, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 10, 14], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CO |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_co |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 12, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `1d69d10167baaafa`／Learning State `c1b7e74484a5`</sub>
