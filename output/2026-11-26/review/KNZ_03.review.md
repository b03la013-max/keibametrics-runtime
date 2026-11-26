# 2026-11-26 KNZ_03 詳細反省（自動・実購入なし）

- 公式着順：2-8-6-5-7（上位3頭 [2, 8, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 4／3着 3；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 510／損益 -190／PFS 72.9%
- 参照：{"revision": "KNZ_03.r2", "ticket_sha256": "d97b39de8151bc20ef5ca5f44d368418f77d5c10f153e6aafba0267c4fae6595", "frozen_at": "2026-11-26T14:35:16.745060+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 5／3着 3；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1100／損益 -4900／PFS 18.3%
- 参照：{"final_receipt_sha256": "bc9a50f645ae5c718c31d240ffcf5e8475d298aab88803ab812fd41cd4ada25d", "result_receipt_sha256": "6c659006caee50e5938c766bd8ba09c77f78cc54739d91489adb2bbde3cdad27", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "1e6963ac77b0773af15014c5f693f91a5c17863e3cbc5163fa252f230f7fd216", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 2130, "pfs": 17.8}, "effective_revision": "REVISION_1", "source_at": "2026-11-26T05:38:19.068580+00:00", "source_receipt_sha256": "8f70c8a993347a3df3737aab6dfbf6b0fbf57f4df9a344148cd1e518f7aa0a61", "signed_final_at": "2026-11-26T05:38:29.637510+00:00", "delivered_ticket_sha256": "0a30e7db534d8ebf6afb040d7ce6739009e936e3602f6e13107b0ef727ff4c1f", "settled_ticket_sha256": "bc9a50f645ae5c718c31d240ffcf5e8475d298aab88803ab812fd41cd4ada25d"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 5, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [2, 8, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 18.3, "profit_loss": -4900, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 18.3, "tickets": 60, "payout": 1100} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `4a515fab6ec95d86`／Learning State `ed7fc29948e5`</sub>
