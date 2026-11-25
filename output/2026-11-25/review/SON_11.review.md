# 2026-11-25 SON_11 詳細反省（自動・実購入なし）

- 公式着順：9-4-8-5-6（上位3頭 [9, 4, 8]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 6／3着 1；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 2600／損益 1900／PFS 371.4%
- 参照：{"revision": "SON_11.r2", "ticket_sha256": "1b4ae12cc207bdb7175263d56f79b57f1cbac9b1e50ca4fa17cb653d9a7ff026", "frozen_at": "2026-11-25T15:25:02.259656+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 5／3着 1；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 4490／損益 -1510／PFS 74.8%
- 参照：{"final_receipt_sha256": "6a125cd094bd97650bcedd2364be2b5d11f5a7e741949d99b17e22ad0165d810", "result_receipt_sha256": "31327d1fc7e41042647b1de8fc72e0df1601e39ccd879edc994cf087601c2e6e", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "fff4ef6a182281eecbc3e6a9463ae3518bc6ffdb448305110ca063d4507d8f85", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 11220, "pfs": 85.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-25T07:02:17.275645+00:00", "source_receipt_sha256": "7a6736610b4e2712a2d362f5eb0850fed614df5c6d89f0fc39ea14b61672302d", "signed_final_at": "2026-11-25T07:02:28.446158+00:00", "delivered_ticket_sha256": "e3463c02ebd38fe388b9c4ee61edd41730d2796ec029ab08664e6776e19a2b5d", "settled_ticket_sha256": "6a125cd094bd97650bcedd2364be2b5d11f5a7e741949d99b17e22ad0165d810"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 4, "SRI-L": 4, "T3I-L": 10, "HPI-L": 4}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 5, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [9, 4, 8], "rescues": [], "supports": ["P3_ROLE_CONFIRMED"], "misses": [" |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 74.8, "profit_loss": -1510, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 74.8, "tickets": 60, "payout": 4490} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `2457fab815f7f0e6`／Learning State `62acb14be369`</sub>
