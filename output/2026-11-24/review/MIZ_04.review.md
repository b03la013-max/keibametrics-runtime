# 2026-11-24 MIZ_04 詳細反省（自動・実購入なし）

- 公式着順：5-3-1-2-10（上位3頭 [5, 3, 1]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 9／3着 5；W True・P2 False・P3 False
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "MIZ_04.r2", "ticket_sha256": "24454da143e097e7fe5f2e2d51dc179e1a6e2938de936c7c3ae819779dac4afc", "frozen_at": "2026-11-24T12:41:41.059189+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 8／3着 4；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "a703baa29914de1ff9b4355e6b5e885834cfa279f993886eb6e3d9b495d02bb4", "result_receipt_sha256": "b5d91ae7c9837afa058a721f873fc308bd95687e7002e03ae6a755c2d857406f", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "4996256015df4100b20233a132d8fd7eedd15cc3b095c9670a8b08aac32f0a15", "signed_final_ticket_count": 120, "signed_final_total_investment": 12000, "signed_final_settlement": {"invest": 12000, "refund": 0, "effective_invest": 12000, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-24T04:18:33.069543+00:00", "source_receipt_sha256": "9721ccce4aa0b3eac90bc30285d8d6a05eb483e9363da3b273d336ed8d411337", "signed_final_at": "2026-11-24T04:18:46.316564+00:00", "delivered_ticket_sha256": "a8e893f7b6ab278ee16401f10d313429f3b446163889f637b70789d29cc6c281", "settled_ticket_sha256": "a703baa29914de1ff9b4355e6b5e885834cfa279f993886eb6e3d9b495d02bb4"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 4, "SRI-L": 5, "T3I-L": 7, "HPI-L": 1}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 3, "second_pre_rank": 8, "third_pre_rank": 4, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [5, 3, 1], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE_ |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 8} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `bc91f6e7268a4d5d`／Learning State `6472db5afdcb`</sub>
