# 2026-11-26 SON_08 詳細反省（自動・実購入なし）

- 公式着順：7-2-8-6-1（上位3頭 [7, 2, 8]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 6／2着 2／3着 9；W False・P2 True・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SON_08.r2", "ticket_sha256": "9f3606bcb2deeae0c34ea479fb00cad21d72002e26805beefac1c1482a7bf45d", "frozen_at": "2026-11-26T13:45:05.266756+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 1／3着 7；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 2240／損益 -3760／PFS 37.3%
- 参照：{"final_receipt_sha256": "82f68c32dead8c08feb7f6ba7233eec110c164759917eab519119ceb85106ee3", "result_receipt_sha256": "6aa923ddd2bda8f0cfe80578b87e006857cd102d4c9133adce64776ba197e441", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "06a82d5619bb7abc4ff602413970491211b5dfa0c6089583da859a3ed5856bd2", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 36540, "pfs": 276.8}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T05:22:07.121330+00:00", "source_receipt_sha256": "125a2d76e4dbb70025ce0800c8958c14be479f31209bd46458657db02ed4d038", "signed_final_at": "2026-11-26T05:22:18.209471+00:00", "delivered_ticket_sha256": "abcad028eb13d00a752aec25fee08c286693c1dc4eeda5c53b89d56934f88fb0", "settled_ticket_sha256": "82f68c32dead8c08feb7f6ba7233eec110c164759917eab519119ceb85106ee3"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 4, "SRI-L": 4, "T3I-L": 1, "HPI-L": 5}, "ruled_neutral_share": 0.0} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補4頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 3, "second_pre_rank": 1, "third_pre_rank": 7, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [7, 2, 8], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "ORDERED_PAIR |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": false, "ordered_exact_ticket_c |
| CAPITAL | ISSUE | {"pfs": 37.3, "profit_loss": -3760, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 37.3, "tickets": 60, "payout": 2240} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `e4c8e3c39dfa28b0`／Learning State `5c585d3091d9`</sub>
