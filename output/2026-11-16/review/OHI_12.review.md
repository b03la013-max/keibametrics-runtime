# 2026-11-16 OHI_12 詳細反省（自動・実購入なし）

- 公式着順：11-10-5-8-4（上位3頭 [11, 10, 5]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 4／3着 5；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 0／損益 -900／PFS 0.0%
- 参照：{"revision": "OHI_12.r2", "ticket_sha256": "e61479e1e0a64725bce9f8f91f707d5ce13d6ed8ff1bd1bacc623de3873d7283", "frozen_at": "2026-11-16T20:05:03.865049+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 6／3着 7；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 True；Pair条件付き3着 True
- 投資 18000／返還 0／払戻 5610／損益 -12390／PFS 31.2%
- 参照：{"final_receipt_sha256": "5ba4e0d3393223fe317e0b642ba3dd5a6d561255d3b06e1aa3463eeac87d2adb", "result_receipt_sha256": "f32aabe0bdf07b04261696f69fc6f884ac4dbe55d996b34cbdcf87d26a013f5f", "result_receipt_verified": true, "krs_input_mode": "TECHNICAL_PROXY_DIAGNOSTIC", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261012-R51"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 4, "SRI-L": 3, "T3I-L": 12, "HPI-L": 5}, "ruled_neutral_share": 0.121} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補5頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 6, "third_pre_rank": 7, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [11, 10, 5], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROL |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 31.2, "profit_loss": -12390, "hit_but_loss": true, "tickets": 180} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 31.2, "tickets": 180, "payout": 5610} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `2e9af75f2ee2b141`／Learning State `92ccb633e3a8`</sub>
