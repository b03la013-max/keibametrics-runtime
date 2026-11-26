# 2026-11-26 SON_10 詳細反省（自動・実購入なし）

- 公式着順：9-7-8-4-2（上位3頭 [9, 7, 8]）
- 距離帯：MIDDLE(1701-2100)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 5／2着 2／3着 1；W False・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 900／返還 0／払戻 3440／損益 2540／PFS 382.2%
- 参照：{"revision": "SON_10.r2", "ticket_sha256": "2782a75bad141f37111f210d3f6870345520294947f8efc1f61464b4e97b3ca0", "frozen_at": "2026-11-26T14:55:15.442749+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 6／2着 1／3着 2；W False・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 3140／損益 -2860／PFS 52.3%
- 参照：{"final_receipt_sha256": "1ea8555768196ed75ced1471e076c0a92dfa4b2f0d96fb35d3b05e6b2186c14a", "result_receipt_sha256": "f688c8cb9b28f2327da090618c3b9889001fcc360c3f87f21f3b4456e7fc2ed7", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "9a7b1b752264cd2792ebb253979b3ecb0866cb04fcbe541cf7093a4c728a62be", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T06:32:05.028514+00:00", "source_receipt_sha256": "d6d9e286499f64f37949195db625278e65f6ff90e5d0e2849d39e59b0482a990", "signed_final_at": "2026-11-26T06:32:15.910638+00:00", "delivered_ticket_sha256": "b196051943670f5c7fe8680c9ce8b2f4cfbde916af9a344d33cb7c382406da6b", "settled_ticket_sha256": "1ea8555768196ed75ced1471e076c0a92dfa4b2f0d96fb35d3b05e6b2186c14a"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 4, "T3I-L": 5, "HPI-L": 5}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 6, "second_pre_rank": 1, "third_pre_rank": 2, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [9, 7, 8], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 52.3, "profit_loss": -2860, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 6, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 52.3, "tickets": 60, "payout": 3140} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `00d1b8a3ef66093f`／Learning State `9048e837157f`</sub>
