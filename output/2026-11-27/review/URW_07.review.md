# 2026-11-27 URW_07 詳細反省（自動・実購入なし）

- 公式着順：9-8-2-12-11（上位3頭 [9, 8, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 3／3着 2；W True・P2 False・P3 False
- Top3捕捉 3／Top4捕捉 3；Head-local P2 None；Pair条件付き3着 True
- 投資 700／返還 0／払戻 750／損益 50／PFS 107.1%
- 参照：{"revision": "URW_07.r2", "ticket_sha256": "abbcd2b11c8f73bad53946e83d5192052c0f3a923e7d032fa33f9499f05956ac", "frozen_at": "2026-11-27T14:40:08.260551+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 5／3着 1；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 3270／損益 -2730／PFS 54.5%
- 参照：{"final_receipt_sha256": "d41bfec450ff78e8740497f77c2bd9224885852837385d65d408d6a41fc595a0", "result_receipt_sha256": "e135a43302198b0200fee1de28f54c33db6f51dcb53d859d77646182a081e74a", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "631fb6b37bc877e4b502c5acf1b2d5c56ad2972244ffbd4707564df605f5b63d", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 3270, "pfs": 21.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-27T06:17:09.902085+00:00", "source_receipt_sha256": "29b82f4c23ea16dc80bf8f390128f3ffdaa6a9e1c83d08422659d1136dd6d45c", "signed_final_at": "2026-11-27T06:17:22.277354+00:00", "delivered_ticket_sha256": "334248a7391a70a0c343017cf2bb77f1ff1b0e93cb1e8d375b2209eb66edbb9c", "settled_ticket_sha256": "d41bfec450ff78e8740497f77c2bd9224885852837385d65d408d6a41fc595a0"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 2, "T3I-L": 2, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 2, "second_pre_rank": 5, "third_pre_rank": 1, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [9, 8, 2], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 54.5, "profit_loss": -2730, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 54.5, "tickets": 60, "payout": 3270} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `d5abba8200ea44ab`／Learning State `4a1bc0db0916`</sub>
