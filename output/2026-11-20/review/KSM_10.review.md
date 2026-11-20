# 2026-11-20 KSM_10 詳細反省（自動・実購入なし）

- 公式着順：7-8-10-9-5（上位3頭 [7, 8, 10]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3

## PAPER

- 1着の事前順位 1／2着 4／3着 6；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 800／返還 0／払戻 140／損益 -660／PFS 17.5%
- 参照：{"revision": "KSM_10.r2", "ticket_sha256": "7d49e854824e024cd0e4e629852019d4a795d7208dffe9a9896569f7082be0b9", "frozen_at": "2026-11-20T14:26:11.066943+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 4／2着 5／3着 2；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "f1018206055014c4a6f8ef64d92a80a377ca741845ef84d8fda1d339271973c0", "result_receipt_sha256": "d9c7549a44c96b147bbde0154d5c6afd6830674e15361ed6ee032d8c8e494648", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "defbbaa9c232e70b14616cbda95649b9373df1af2e9c604a314a0635e21bdd98", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-20T05:29:33.866658+00:00", "source_receipt_sha256": "0b5fe1b99194d2febb735fb9734bfd808e1bb35c3382e6f64306f9b4e677f0d4", "signed_final_at": "2026-11-20T05:29:42.254458+00:00", "delivered_ticket_sha256": "57acb13c8f8ffcb3edd826c81822cfec02a72a26bb46ff28b4569d186c7cc1d5", "settled_ticket_sha256": "f1018206055014c4a6f8ef64d92a80a377ca741845ef84d8fda1d339271973c0"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 2, "T3I-L": 4, "HPI-L": 1}, "ruled_neutral_share": 0.117} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 4, "second_pre_rank": 5, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [7, 8, 10], "rescues": ["WINNER_ROLE_RESCUE", "ORDERED_PAIR_RESCUE", "PAI |
| TICKET | ISSUE | {"head_local_p2": null, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 4, "alternative_signals_that_had_winner_top": ["PAPER ◎ was the winner", "F3S-L ranked the winner #1 | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `d85d9a3f645ab156`／Learning State `1ac4aff014c0`</sub>
