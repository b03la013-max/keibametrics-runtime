# 2026-11-26 KNZ_09 詳細反省（自動・実購入なし）

- 公式着順：7-5-3-6-9（上位3頭 [7, 5, 3]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 2／3着 5；W True・P2 True・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 1600／返還 0／払戻 1460／損益 -140／PFS 91.2%
- 参照：{"revision": "KNZ_09.r2", "ticket_sha256": "7f0ef96f79d11a8f26bb03e6a4904100e70e5759eff11cfc8b4a7a8223cf5787", "frozen_at": "2026-11-26T18:05:18.649581+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 5／3着 4；W True・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 1790／損益 -4210／PFS 29.8%
- 参照：{"final_receipt_sha256": "93629876e82f62757bd3cc31d8b5b4d562a8af419330079cc1af773cccdc9a71", "result_receipt_sha256": "e361b59d41fdd736cd2e64e8b910e6405db0937a302756ac6ce4f150e615fc4a", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "6cd350600f55f4c02319c7d723c04ba6e08a68554ad7f357add53be0edaa6951", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 1460, "pfs": 12.2}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T09:42:21.773142+00:00", "source_receipt_sha256": "040e3d54e339c6f0f869862e5e41c128dddd50faf41f8f28faea4542097c4585", "signed_final_at": "2026-11-26T09:42:33.131514+00:00", "delivered_ticket_sha256": "5636f53182e7117e86b44cdb7a6c68b5d95ea32b6754fa05e45dae6b6d83207f", "settled_ticket_sha256": "93629876e82f62757bd3cc31d8b5b4d562a8af419330079cc1af773cccdc9a71"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 1, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 5, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [7, 5, 3], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 29.8, "profit_loss": -4210, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 29.8, "tickets": 60, "payout": 1790} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `b6705e35be98641e`／Learning State `cb0ff03b501e`</sub>
