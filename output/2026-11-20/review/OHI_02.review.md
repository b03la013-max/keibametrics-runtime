# 2026-11-20 OHI_02 詳細反省（自動・実購入なし）

- 公式着順：6-4-7-11-1（上位3頭 [6, 4, 7]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**NONE**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive, pfs_at_least_100

## PAPER

- 1着の事前順位 5／2着 2／3着 4；W False・P2 True・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "OHI_02.r2", "ticket_sha256": "1f88ce6713f2834cb5f52b5a62adf43805a434f0ece62943dbf5e2a9a4dddda3", "frozen_at": "2026-11-20T14:18:34.116052+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 2／3着 7；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 33400／損益 27400／PFS 556.7%
- 参照：{"final_receipt_sha256": "778b789eb5a0aebb5049913495c20157dddb3f8251585bb8d6ef470e1fe5192e", "result_receipt_sha256": "a41d95b0b4b1f9e4f396bb50aa4eba3b06ac6bc3697a68040a3b0b04267960bf", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "ffba27921f9a435814d33efdeae7aa819f9472cf152849d2028fa63748d341ed", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 33400, "pfs": 231.9}, "effective_revision": "REVISION_2", "source_at": "2026-11-20T05:55:26.464892+00:00", "source_receipt_sha256": "0e61af0f873263c6538927bd18c5a953fccea1fca37429466eadc6ff50e60d00", "signed_final_at": "2026-11-20T05:55:35.493615+00:00", "delivered_ticket_sha256": "2c77801db56a888adb2ff4f2120fc4d801ba1a55bcf2d0e07c27c1128f559673", "settled_ticket_sha256": "778b789eb5a0aebb5049913495c20157dddb3f8251585bb8d6ef470e1fe5192e"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 3, "TPI-L": 3, "SRI-L": 3, "T3I-L": 4, "HPI-L": 3}, "ruled_neutral_share": 0.116} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 2, "third_pre_rank": 7, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [6, 4, 7], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_cov |
| CAPITAL | OK | {"pfs": 556.7, "profit_loss": 27400, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `e137a9a1e98f88ec`／Learning State `418c08cd5c5e`</sub>
