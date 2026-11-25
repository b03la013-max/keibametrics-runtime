# 2026-11-25 URW_08 詳細反省（自動・実購入なし）

- 公式着順：8-10-7-2-1（上位3頭 [8, 10, 7]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：third_in_P3

## PAPER

- 1着の事前順位 12／2着 9／3着 2；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 0／損益 -900／PFS 0.0%
- 参照：{"revision": "URW_08.r2", "ticket_sha256": "93e6497783dbb744395ac87c14265e1a1e2b2bb9847c709c16d2418d6f288841", "frozen_at": "2026-11-25T15:15:17.585416+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 11／2着 8／3着 4；W False・P2 False・P3 True
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "9857382b3cb5d5c4716a6a39a0221d3b4d067561ffb7826aee13bfa42877de86", "result_receipt_sha256": "8ccb5d577208de9b6874f25589567f7ee46e96e7a76a1e28a8ef3affb8bb5b9e", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "5ed5448fac315ca7523f2056fed5459221aeda620a9de97b777f1e19e4937809", "signed_final_ticket_count": 180, "signed_final_total_investment": 18000, "signed_final_settlement": {"invest": 18000, "refund": 0, "effective_invest": 18000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T06:52:10.499530+00:00", "source_receipt_sha256": "06b6d16e164753fea03e3c16e8ead5781c00700340ad567a0a78d281da120923", "signed_final_at": "2026-11-25T06:52:24.326701+00:00", "delivered_ticket_sha256": "49bf2b89497ca527254f1772f32a32b94686cfb55f166b0f31b5b657fa242f67", "settled_ticket_sha256": "9857382b3cb5d5c4716a6a39a0221d3b4d067561ffb7826aee13bfa42877de86"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 10, "TPI-L": 9, "SRI-L": 10, "T3I-L": 11, "HPI-L": 6}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補5頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 11, "second_pre_rank": 8, "third_pre_rank": 4, "winner_in_W": false, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [8, 10, 7], "rescues": [], "supports": ["P3_ROLE_CONFIRMED"], "misses": [ |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 11, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `f23c8e06e09ca5a3`／Learning State `430f0cb68b93`</sub>
