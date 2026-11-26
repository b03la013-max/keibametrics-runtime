# 2026-11-26 KNZ_02 詳細反省（自動・実購入なし）

- 公式着順：7-1-9-5-4（上位3頭 [7, 1, 9]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 3；W False・P2 False・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 800／返還 0／払戻 190／損益 -610／PFS 23.8%
- 参照：{"revision": "KNZ_02.r2", "ticket_sha256": "fc4d69a488e9e056ab8596731c63005907285fb274fa0a3a8f94b5908f1adf95", "frozen_at": "2026-11-26T14:00:12.664897+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 3／3着 2；W True・P2 True・P3 True
- Top3捕捉 3／Top4捕捉 3；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 2040／損益 -3960／PFS 34.0%
- 参照：{"final_receipt_sha256": "7789759e8c36a121b3ed73a4ebbf73de25d8e983f52eea08d9cdf6a2be70225a", "result_receipt_sha256": "f6a25b60bac84251da75e146445cbca95a03a5f857a6ca3a0021a9c9f594767c", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "d0c2d02f543badb6355b10e2bc03c27c5b77b4b0ea2f7b42cb05d55a8a03f5a5", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 1850, "pfs": 15.4}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T05:36:18.591241+00:00", "source_receipt_sha256": "a01de43e2a161deb3e776cd0c5ecb00bbd3f6a3aa0b3e5c9cfdfa96c656affc3", "signed_final_at": "2026-11-26T05:36:31.581136+00:00", "delivered_ticket_sha256": "8bb19d47c5c0deb3f81f6f0936e0ea9cb75e8ef5ce8655452762a740d0645fd6", "settled_ticket_sha256": "7789759e8c36a121b3ed73a4ebbf73de25d8e983f52eea08d9cdf6a2be70225a"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 3, "SRI-L": 1, "T3I-L": 3, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（イリノセラビア）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 3, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [7, 1, 9], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 34.0, "profit_loss": -3960, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 34.0, "tickets": 60, "payout": 2040} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `cd0934f68b19289e`／Learning State `83159b464141`</sub>
