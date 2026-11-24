# 2026-11-24 MIZ_06 詳細反省（自動・実購入なし）

- 公式着順：1-5-7-2-4（上位3頭 [1, 5, 7]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 6／3着 5；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "MIZ_06.r2", "ticket_sha256": "e400eba8ac8843de10a02fc2187a46c83efeb8b78c8cd1ca24c3c9c1f24c6b02", "frozen_at": "2026-11-24T13:51:41.170593+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 5／3着 3；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 4290／損益 -1710／PFS 71.5%
- 参照：{"final_receipt_sha256": "973e19e08e7ff6ef030cc749339c322afa5d25ee9da4bcc1cc1f8aafa1732bfa", "result_receipt_sha256": "187ba24bf600b15343668a43388f49eb15de440d4d2ecc3f1cc940dc6363e397", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "282bb297c7c03d5aa6d5dd05ce9770b81468c1495648ec3eebb0a3d1969f5842", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 3690, "pfs": 28.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T05:28:23.163660+00:00", "source_receipt_sha256": "6f3f42872e76040e80d1e7ee67443317ae59aea327c583ae0449b0b83947d093", "signed_final_at": "2026-11-24T05:28:36.146847+00:00", "delivered_ticket_sha256": "12a50e2afbd59fe92357d5c4be68e54df6b095bf4d9dd32532a13a20e1fe7531", "settled_ticket_sha256": "973e19e08e7ff6ef030cc749339c322afa5d25ee9da4bcc1cc1f8aafa1732bfa"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 4, "T3I-L": 5, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（シャラ）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 5, "third_pre_rank": 3, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 5, 7], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 71.5, "profit_loss": -1710, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 71.5, "tickets": 60, "payout": 4290} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `7875edaa9c6f35c3`／Learning State `57ada42301f4`</sub>
