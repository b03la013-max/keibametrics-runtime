# 2026-11-25 NGY_02 詳細反省（自動・実購入なし）

- 公式着順：2-8-11-6-10（上位3頭 [2, 8, 11]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 7／2着 5／3着 2；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "NGY_02.r2", "ticket_sha256": "ffe90a91358404189e257f1dfc6121cad1a7c0c505bfba14100f1e93de4f38c7", "frozen_at": "2026-11-25T14:30:17.806828+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 6／2着 1／3着 5；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1050／損益 -4950／PFS 17.5%
- 参照：{"final_receipt_sha256": "c265cfc04eb8df970189133a9c840519fd7f71f7cef7e7ed97491577faf4a179", "result_receipt_sha256": "dc9f892a73c0c4a6dca1db7a3d6867f5712d5bf62ae0a1f90812bdb38df2a13d", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "81a2ea3a40e8fd2aef1b3b677ae0d5193f860bb61459be5f444b72004970a7b3", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T06:07:18.066709+00:00", "source_receipt_sha256": "69ea906487b095f903567684a9981937abdd1b097ca1ad2a8d893c2069424c42", "signed_final_at": "2026-11-25T06:07:30.255143+00:00", "delivered_ticket_sha256": "08444c82ffab72e92cf8ba7fe2c45478fa0b65db1a4a36acbc35f996e9c3c05b", "settled_ticket_sha256": "c265cfc04eb8df970189133a9c840519fd7f71f7cef7e7ed97491577faf4a179"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 6, "T3I-L": 9, "HPI-L": 4}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 6, "second_pre_rank": 1, "third_pre_rank": 5, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [2, 8, 11], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CON |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 17.5, "profit_loss": -4950, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 6, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 17.5, "tickets": 60, "payout": 1050} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `037613510ed94aa1`／Learning State `aa4cd80723be`</sub>
