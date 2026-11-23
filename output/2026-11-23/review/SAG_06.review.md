# 2026-11-23 SAG_06 詳細反省（自動・実購入なし）

- 公式着順：7-3-1-4-8（上位3頭 [7, 3, 1]）
- 距離帯：MIDDLE(1701-2100)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 5／2着 8／3着 4；W False・P2 False・P3 False
- Top3捕捉 0／Top4捕捉 1；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 0／損益 -700／PFS 0.0%
- 参照：{"revision": "SAG_06.r2", "ticket_sha256": "02a4422167893c6d55745c27cde43039181d45997119e7ed224e98dde71a3e50", "frozen_at": "2026-11-23T17:26:11.027673+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 3／2着 8／3着 2；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "301573cc9440c19616ce887a4ffa4444fb046ae69745cea9afc1cb6699742356", "result_receipt_sha256": "59260137ca111aca4fdb0b7421e9b22a787850e44cfa7cd601c5d7178349e92a", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "46ad948c896d2545ff6c4380d7ffb4cc355ff0de9c3061384cb7b4b921a21ba3", "signed_final_ticket_count": 105, "signed_final_total_investment": 10500, "signed_final_settlement": {"invest": 10500, "refund": 0, "effective_invest": 10500, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-23T09:02:12.179228+00:00", "source_receipt_sha256": "7803ef2248c5f022b5d770aeb9aec09a198d24f9fbaa179f39bb8ef96d405f4a", "signed_final_at": "2026-11-23T09:02:27.004724+00:00", "delivered_ticket_sha256": "8123235471e3e47649ae64fc10f1ae9c259931e90b497dbef00b3973c271a903", "settled_ticket_sha256": "301573cc9440c19616ce887a4ffa4444fb046ae69745cea9afc1cb6699742356"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 4, "TPI-L": 3, "SRI-L": 4, "T3I-L": 4, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 3, "second_pre_rank": 8, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-AUDIT-DELTA", "post_result_evaluation": {"actual_top3": [7, 3, 1], "rescues": [], "supports": ["P3_ROLE_CONFIRMED"], "misses": ["WINNER_ROLE_ |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 8} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `aa9260e2cfd0846c`／Learning State `bcdda44bd245`</sub>
