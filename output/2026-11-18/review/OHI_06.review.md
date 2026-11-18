# 2026-11-18 OHI_06 詳細反省（自動・実購入なし）

- 公式着順：6-5-3-14-4（上位3頭 [6, 5, 3]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 1／2着 4／3着 11；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 1600／返還 0／払戻 1110／損益 -490／PFS 69.4%
- 参照：{"revision": "OHI_06.r2", "ticket_sha256": "24d01e447ff28827ec817511a140de578d8768545b2927259a501554cb9faef8", "frozen_at": "2026-11-18T16:27:07.731249+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 6／3着 8；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 1110／損益 -4890／PFS 18.5%
- 参照：{"final_receipt_sha256": "538a197f1f353cb5fe71796c1ef8eb8569d33f227c6050b8d1d72d003505f9fd", "result_receipt_sha256": "89a953c181852ed6a84c096a4592edaead4430d3adcec605ec8cf5ab13522712", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "b17ea0341750b81c6e1ddc19d4ef80c5f91f91771e3b1bb6d4ab2cdf921668be", "signed_final_ticket_count": 180, "signed_final_total_investment": 18000, "signed_final_settlement": {"invest": 18000, "refund": 0, "effective_invest": 18000, "payout": 10110, "pfs": 56.2}}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 1, "SRI-L": 2, "T3I-L": 3, "HPI-L": 1}, "ruled_neutral_share": 0.113} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 6, "third_pre_rank": 8, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [6, 5, 3], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_co |
| CAPITAL | ISSUE | {"pfs": 18.5, "profit_loss": -4890, "hit_but_loss": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 18.5, "tickets": 60, "payout": 1110} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `8769a489c5fe1efa`／Learning State `48b9e7966e71`</sub>
