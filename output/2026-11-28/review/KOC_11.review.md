# 2026-11-28 KOC_11 詳細反省（自動・実購入なし）

- 公式着順：3-7-6-9-10（上位3頭 [3, 7, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_W**
- 正しく判断できた項目：second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2

## PAPER

- 1着の事前順位 3／2着 6／3着 1；W False・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 900／返還 0／払戻 0／損益 -900／PFS 0.0%
- 参照：{"revision": "KOC_11.r2", "ticket_sha256": "55aa40de2ea60d669270eca4bc31d70c713e775eb964c9334ab041add26a6061", "frozen_at": "2026-11-28T19:35:03.910456+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 6／2着 5／3着 7；W False・P2 True・P3 True
- Top3捕捉 0／Top4捕捉 0；Head-local P2 True；Pair条件付き3着 False
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "f318556ced47996549c6c74226df8c5283c800f87b273964fbb24ca6a2cc4fff", "result_receipt_sha256": "c6b31fc5725409c2c3ed33a3f35cabf6addf17438424a9665c88ca566d5c7e7f", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "f43cf8584213f98692757dc9aa0c1251280febb9b3984e354a6669357c023be6", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_2", "source_at": "2026-11-28T11:10:09.830604+00:00", "source_receipt_sha256": "835828906e2fd36f303b44e4d9e496a7ffd3989e6c647ef77ad2f1a86ba5744f", "signed_final_at": "2026-11-28T11:10:23.097507+00:00", "delivered_ticket_sha256": "24836b473e4ba2fe5839531f8a74231b5bf5c9fea2b4d990ac95c664ae4edea9", "settled_ticket_sha256": "f318556ced47996549c6c74226df8c5283c800f87b273964fbb24ca6a2cc4fff"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 7, "TPI-L": 5, "SRI-L": 6, "T3I-L": 5, "HPI-L": 7}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "ハイペース想定（逃げ候補3頭）", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 6, "second_pre_rank": 5, "third_pre_rank": 7, "winner_in_W": false, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [3, 7, 6], "rescues": [], "supports": ["P2_ROLE_CONFIRMED", "P3_ROLE_CONF |
| TICKET | ISSUE | {"head_local_p2": true, "pair_conditioned_third": false, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | {"winner_pre_rank": 6, "alternative_signals_that_had_winner_top": []} | over >=30 forward races at this venue/band the alternative signal top-1 does not | shadow-score the alternative signal vs current W on every forward race (frozen p | W-capture rate, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `924f10e689d4bd1d`／Learning State `521a17007278`</sub>
