# 2026-11-25 NGY_07 詳細反省（自動・実購入なし）

- 公式着順：12-3-7-8-5（上位3頭 [12, 3, 7]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**PREDICTION_ROLE_P2**
- 正しく判断できた項目：winner_in_W, third_in_P3, winner_is_ticket_head

## PAPER

- 1着の事前順位 1／2着 5／3着 2；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 None；Pair条件付き3着 None
- 投資 700／返還 0／払戻 200／損益 -500／PFS 28.6%
- 参照：{"revision": "NGY_07.r2", "ticket_sha256": "05cf03cf606645c1a1c39c7004b7915c564a10a4c06667d909c11ad49d461926", "frozen_at": "2026-11-25T17:20:09.225311+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 7／3着 2；W True・P2 False・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 6000／返還 0／払戻 0／損益 -6000／PFS 0.0%
- 参照：{"final_receipt_sha256": "10df130ff2b21c4f7985532e14a07fb1d3acfa06445d846ac902c372befac2eb", "result_receipt_sha256": "901c5a6ee04bb1708ceaab3ef2307ad3cf7e2dd73f75791d4b6304860707c8b6", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261116-R54", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "4fb8858df17469ba6a460028706bd7a4bf40f7b3d131d66970d54e45133b9a3a", "signed_final_ticket_count": 156, "signed_final_total_investment": 15600, "signed_final_settlement": {"invest": 15600, "refund": 0, "effective_invest": 15600, "payout": 0, "pfs": 0.0}, "effective_revision": "REVISION_1", "source_at": "2026-11-25T08:24:41.890750+00:00", "source_receipt_sha256": "6c7084516bbdacc13ae919ff314145d906e7f4d73c660085e2fc545f65f8f4b8", "signed_final_at": "2026-11-25T08:24:54.756671+00:00", "delivered_ticket_sha256": "2994180571bd167a6cfd90bda6484638e32bc10534edc94ad36072a28076432b", "settled_ticket_sha256": "10df130ff2b21c4f7985532e14a07fb1d3acfa06445d846ac902c372befac2eb"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 2, "TPI-L": 2, "SRI-L": 1, "T3I-L": 1, "HPI-L": 2}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補0頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | ISSUE | {"winner_pre_rank": 1, "second_pre_rank": 7, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": false, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [12, 3, 7], "rescues": ["P2_ROLE_RESCUE", "ORDERED_PAIR_RESCUE"], "suppor |
| TICKET | ISSUE | {"head_local_p2": false, "pair_conditioned_third": null, "trio_set_covered": false, "ordered_pair_ticket_coverage": false, "top3_set_ticket_coverage": false, "ordered_exact_ticket_ |
| CAPITAL | ISSUE | {"pfs": 0.0, "profit_loss": -6000, "hit_but_loss": false, "hit_but_loss_runtime_full_mec": false, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | {"second_pre_rank": 7} | >=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost | counterfactual P2+1 on frozen forward races (no reselection) | P2 capture, PFS |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `882cbee2f07d7866`／Learning State `1a6ba78ec620`</sub>
