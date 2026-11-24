# 2026-11-24 URW_03 詳細反省（自動・実購入なし）

- 公式着順：5-2-1-8-7（上位3頭 [5, 2, 1]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 2／2着 3／3着 1；W False・P2 False・P3 False
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 480／損益 -220／PFS 68.6%
- 参照：{"revision": "URW_03.r2", "ticket_sha256": "f502a412314c1218560403346c3720f1d35201b012f8c2e2df8e520cfe92138b", "frozen_at": "2026-11-24T12:36:19.129626+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 6／3着 8；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 1860／損益 -4140／PFS 31.0%
- 参照：{"final_receipt_sha256": "303ff7340b1bae38f3c1977c22be7852990109fea3f8f6e3913dc26a044d9e91", "result_receipt_sha256": "15878bf0c85b3bcb7ce3474e997b130d58b1f878231b824bf8f7074ab36c61ed", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "6cc899d1934c954249c13a6e19128e25c9f7d0dfa12a1871cea17ae72ce5acb3", "signed_final_ticket_count": 105, "signed_final_total_investment": 10500, "signed_final_settlement": {"invest": 10500, "refund": 0, "effective_invest": 10500, "payout": 6390, "pfs": 60.9}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T04:11:25.261061+00:00", "source_receipt_sha256": "6e5a62c789956166cb5aef76a161550517f7c85dcd604cee861571fe31271e60", "signed_final_at": "2026-11-24T04:11:36.515284+00:00", "delivered_ticket_sha256": "05344bf17a4066e03925bc4ee53274429c675f0fc15d07f5fea675c5f1f273bb", "settled_ticket_sha256": "303ff7340b1bae38f3c1977c22be7852990109fea3f8f6e3913dc26a044d9e91"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 3, "SRI-L": 2, "T3I-L": 5, "HPI-L": 4}, "ruled_neutral_share": 0.246} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 6, "third_pre_rank": 8, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 2, 1], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 31.0, "profit_loss": -4140, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 31.0, "tickets": 60, "payout": 1860} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | {"ruled_neutral_share": 0.246} | ruled-neutral share falls below 15% without source changes | per-venue observation rate in forward_summary | CALCULATED share |

<sub>review sha256 `ec4fd760f962efb0`／Learning State `3d1ef194b242`</sub>
