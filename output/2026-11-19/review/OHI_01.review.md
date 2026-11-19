# 2026-11-19 OHI_01 詳細反省（自動・実購入なし）

- 公式着順：3-8-4-10-12（上位3頭 [3, 8, 4]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 7／2着 2／3着 6；W False・P2 True・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 0／損益 -900／PFS 0.0%
- 参照：{"revision": "OHI_01.r2", "ticket_sha256": "34b0e04dad9434d6e37776f849a7ab969e9f20369b3a31fe9203a3979c8f1b69", "frozen_at": "2026-11-19T13:45:02.787554+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 5／3着 2；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 3580／損益 -2420／PFS 59.7%
- 参照：{"final_receipt_sha256": "524b8ab532e5ca6bb22d954a26f85d0cfd1a7d08bf5f0ede0de70ec00ff2530f", "result_receipt_sha256": "bf42cc02908c9c8fcbc3122557d4c16058535fc67020b6c3e90b5de96e5db36a", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "1aed8abce30c962e30dc2157d1b4ae6b923f24b5a224ff4c038b04157f5e88ce", "signed_final_ticket_count": 168, "signed_final_total_investment": 16800, "signed_final_settlement": {"invest": 16800, "refund": 0, "effective_invest": 16800, "payout": 3580, "pfs": 21.3}, "effective_revision": "REVISION_1", "source_at": null, "signed_final_at": "2026-11-19T04:46:35.696629+00:00", "delivered_ticket_sha256": "1b58e77116e31434e154e545871a2c9c5c33600013044f2f10a6fdea2cb3e191", "settled_ticket_sha256": "524b8ab532e5ca6bb22d954a26f85d0cfd1a7d08bf5f0ede0de70ec00ff2530f"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 2, "SRI-L": 1, "T3I-L": 2, "HPI-L": 1}, "ruled_neutral_share": 0.114} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 5, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 8, 4], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_ |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 59.7, "profit_loss": -2420, "hit_but_loss": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 59.7, "tickets": 60, "payout": 3580} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `098ae33153161c0a`／Learning State `a2aaabe2c146`</sub>
