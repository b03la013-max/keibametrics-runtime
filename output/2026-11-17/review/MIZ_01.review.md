# 2026-11-17 MIZ_01 詳細反省（自動・実購入なし）

- 公式着順：4-2-7-8-9（上位3頭 [4, 2, 7]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, payout_positive

## PAPER

- 1着の事前順位 2／2着 1／3着 10；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 1600／返還 0／払戻 0／損益 -1600／PFS 0.0%
- 参照：{"revision": "MIZ_01.r2", "ticket_sha256": "1652f06ba97664f2cfe77458bd0e60387a3c2e3407b651ec0a14e2a62183f505", "frozen_at": "2026-11-17T10:50:20.710787+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 3／3着 9；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 440／損益 -5560／PFS 7.3%
- 参照：{"final_receipt_sha256": "0d912c8b32f8def1c242c2a3f418393bfbc04b244891790271d1916165499e07", "result_receipt_sha256": "e71799249b4caf1c0f03d9016a37c976fd22ffe6705c0767db1dde0375b9c61d", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "5bce8c6a64b6260cdb59e3e58be62f9cf4029db17e46fda82e965f0d78a945ce", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 2910, "pfs": 18.7}}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 4, "HPI-L": 1}, "ruled_neutral_share": 0.115} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 3, "third_pre_rank": 9, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [4, 2, 7], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P2_ROLE_CONFIRMED",  |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_co |
| CAPITAL | ISSUE | {"pfs": 7.3, "profit_loss": -5560, "hit_but_loss": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 7.3, "tickets": 60, "payout": 440} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `c8095ec924a574ba`／Learning State `c8c1a46796c1`</sub>
