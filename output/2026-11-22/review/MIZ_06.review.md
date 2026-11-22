# 2026-11-22 MIZ_06 詳細反省（自動・実購入なし）

- 公式着順：1-9-7-6-2（上位3頭 [1, 9, 7]）
- 距離帯：SPRINT(<=1300)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 6／2着 7／3着 3；W False・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "MIZ_06.r2", "ticket_sha256": "efd195e5311a9a4384fb79b7d194a2551c752036826b381d202fd31e38c5bf9c", "frozen_at": "2026-11-22T14:05:01.427976+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 2／2着 10／3着 5；W True・P2 False・P3 True
- Top3捕捉 1／Top4捕捉 1；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "4414960029d5a322459a0733a64beb94f4b6244236a1c2f4f48391460af37f23", "result_receipt_sha256": "42947c26b4196465d5528f219953aa20d1301e47d5085eef3824054bb122546f", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "293596998eb784302e5edb2ea66f2ead9880d57244a6037b20716983fa74de1a", "signed_final_ticket_count": 132, "signed_final_total_investment": 13200, "signed_final_settlement": {"invest": 13200, "refund": 0, "effective_invest": 13200, "payout": 20740, "pfs": 157.1}, "effective_revision": "REVISION_2", "source_at": "2026-11-22T05:42:18.001772+00:00", "source_receipt_sha256": "f5701ddaf0d29b75d92868c3cdadce5d99c242d679ea1df88bd15b97dfd83ee6", "signed_final_at": "2026-11-22T05:42:30.343070+00:00", "delivered_ticket_sha256": "ce72a9eb39c80ff7c9ffb768f7b3df04d715f758feedcccf19386945d078df26", "settled_ticket_sha256": "4414960029d5a322459a0733a64beb94f4b6244236a1c2f4f48391460af37f23"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 5, "TPI-L": 6, "SRI-L": 5, "T3I-L": 3, "HPI-L": 5}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 2, "second_pre_rank": 10, "third_pre_rank": 5, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [1, 9, 7], "rescues": [], "supports": ["P3_ROLE_CONFIRMED"], "misses": [" |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 10} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `c159164c265bfe92`／Learning State `78dbc59e4bdb`</sub>
