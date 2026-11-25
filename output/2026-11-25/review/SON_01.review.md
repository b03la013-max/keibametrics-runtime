# 2026-11-25 SON_01 詳細反省（自動・実購入なし）

- 公式着順：10-1-3-5-9（上位3頭 [10, 1, 3]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 3／2着 1／3着 5；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 1600／返還 0／払戻 0／損益 -1600／PFS 0.0%
- 参照：{"revision": "SON_01.r2", "ticket_sha256": "f033891f564f6fc744e0b15131d61a9614f31bade7e66464eda5a64cbf4e503d", "frozen_at": "2026-11-25T09:56:13.484681+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 5／2着 1／3着 3；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1580／損益 -4420／PFS 26.3%
- 参照：{"final_receipt_sha256": "76cc773761adfed77e255ba8f7c4305d4f0952aa41159d63c0312fc042345938", "result_receipt_sha256": "9be2795f8ec631624ea95e0c70deb9cc85e1613d2219f53331e0d230d170f6bb", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "2e5872464ab8d9cdaf9a915e541e76e513cce0cd7b3d767a2a0cb67cdb401103", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-25T00:59:21.783190+00:00", "source_receipt_sha256": "b4d0cffc79842ace6d4531f6948bcf7bfb5cd9e53914fea2c677e7d410372d8b", "signed_final_at": "2026-11-25T00:59:32.942027+00:00", "delivered_ticket_sha256": "f7ed1b84562fb3c80188ad2a66d88928affc424801f6d77a2b1f9c6db58f41d4", "settled_ticket_sha256": "76cc773761adfed77e255ba8f7c4305d4f0952aa41159d63c0312fc042345938"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 2, "T3I-L": 4, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 1, "third_pre_rank": 3, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [10, 1, 3], "rescues": ["WINNER_ROLE_RESCUE", "ORDERED_PAIR_RESCUE", "PAI |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 26.3, "profit_loss": -4420, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 26.3, "tickets": 60, "payout": 1580} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `b2277afc39b502cc`／Learning State `7ef067c893be`</sub>
