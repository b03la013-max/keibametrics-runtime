# 2026-11-24 MIZ_09 詳細反省（自動・実購入なし）

- 公式着順：6-4-2-1-10（上位3頭 [6, 4, 2]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 4／2着 8／3着 1；W False・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "MIZ_09.r2", "ticket_sha256": "94ecf40f3038a12a1ea91690d4bbea497a5ca3795acdca790d1d48a7d2157c8d", "frozen_at": "2026-11-24T15:35:13.874588+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 5／2着 6／3着 1；W False・P2 True・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 2420／損益 -3580／PFS 40.3%
- 参照：{"final_receipt_sha256": "c909203e149d3cf1dbab5a99d5312d0fb63f30294228b61a4164f31d79a832bd", "result_receipt_sha256": "6bc82fe198ce9b7986d8bd018d5f2cbc34a05fa3008cbd89302adc35dbbc1bcd", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "906467cb0234f814b248d1343bf16f0b720a410504ede3bd3ae15a16c2b41261", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T07:12:21.423698+00:00", "source_receipt_sha256": "0b0871fe42913b834431e5d7d2bec8111d2e1efd4c8dce5a1dcd73be9c789384", "signed_final_at": "2026-11-24T07:12:34.407003+00:00", "delivered_ticket_sha256": "6d2764bb99506ef64b87621c41ad60e25e9b8417c03f511ed633d307999182da", "settled_ticket_sha256": "c909203e149d3cf1dbab5a99d5312d0fb63f30294228b61a4164f31d79a832bd"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 5, "SRI-L": 5, "T3I-L": 6, "HPI-L": 5}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "単騎逃げ濃厚（レアグリフォン）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 5, "second_pre_rank": 6, "third_pre_rank": 1, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [6, 4, 2], "rescues": [], "supports": ["P3_ROLE_CONFIRMED"], "misses": [" |
| TICKET | OK | {"head_local_p2": null, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cov |
| CAPITAL | ISSUE | {"pfs": 40.3, "profit_loss": -3580, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 5, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P1:HIT_BUT_LOSS | P1 | {"pfs": 40.3, "tickets": 60, "payout": 2420} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `b0a64fa8b8ebb7b1`／Learning State `bbba48d8a77d`</sub>
