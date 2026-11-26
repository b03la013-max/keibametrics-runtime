# 2026-11-26 NGY_09 詳細反省（自動・実購入なし）

- 公式着順：4-11-6-9-7（上位3頭 [4, 11, 6]）
- 距離帯：MILE(1301-1700)／第一実質失敗：**CAPITAL_EFFICIENCY**
- 正しく判断できた項目：winner_in_W, second_in_P2, third_in_P3, winner_is_ticket_head, head_local_p2, pair_conditioned_third, trio_set_covered, payout_positive

## PAPER

- 1着の事前順位 1／2着 6／3着 2；W True・P2 False・P3 False
- Top3捕捉 2／Top4捕捉 2；Head-local P2 False；Pair条件付き3着 None
- 投資 800／返還 0／払戻 160／損益 -640／PFS 20.0%
- 参照：{"revision": "NGY_09.r2", "ticket_sha256": "a8644a2f882b9da40567cb6707272b892c7661635fccd914e987eb97dd619326", "frozen_at": "2026-11-26T18:20:12.330993+09:00"}

## FORMAL_RECOMMENDATION

- 1着の事前順位 1／2着 6／3着 2；W True・P2 True・P3 True
- Top3捕捉 2／Top4捕捉 2；Head-local P2 True；Pair条件付き3着 True
- 投資 6000／返還 0／払戻 3830／損益 -2170／PFS 63.8%
- 参照：{"final_receipt_sha256": "70f738475002e9ab100778d834cb8d35901144163f37747ad26c20099a33ad72", "result_receipt_sha256": "348105e403accb6e54ccb7d68eb63a097e156a71c18e045cc7017a146081dc29", "result_receipt_verified": true, "krs_input_mode": "FORMAL_NUMERICAL", "authority": "KM-FAMILY-CURRENT-AUTHORITY-20261124-R55", "prediction_consumer": "KM-LOCAL-NUMERICAL-PREDICTION-CONSUMER-v1.0-20261116", "local_ticket_cap_sha256": "4ccebb6b7387ff6431de68e40f2c75ce52be211d92cf371c646639aa8278dd8a", "signed_final_ticket_count": 144, "signed_final_total_investment": 14400, "signed_final_settlement": {"invest": 14400, "refund": 0, "effective_invest": 14400, "payout": 3120, "pfs": 21.7}, "effective_revision": "REVISION_2", "source_at": "2026-11-26T09:57:08.002725+00:00", "source_receipt_sha256": "045c5d31ee90499bb591d118cd2f03943c3a8e30acd295d0ea344dcb27225145", "signed_final_at": "2026-11-26T09:57:20.520523+00:00", "delivered_ticket_sha256": "4b1113f3dd7ff2975c9b5520483901510923f64edb917242d267ce3c919d7e76", "settled_ticket_sha256": "70f738475002e9ab100778d834cb8d35901144163f37747ad26c20099a33ad72"}

## 工程別

| 工程 | 状態 | 根拠 |
|---|---|---|
| SOURCE | OK | "Signed SOURCE frozen before cutoff; runner universe matched" |
| INDEX | OBSERVED | {"winner_rank_by_index": {"F3S-L": 1, "TPI-L": 1, "SRI-L": 1, "T3I-L": 2, "HPI-L": 3}, "ruled_neutral_share": 0.069} |
| DAY_STATE | UNKNOWN | "body weight / paddock / track-bias effect not measured in the frozen artifacts" |
| PACE | UNKNOWN | {"paper_pace_view": "逃げ候補2頭・平均ペース", "note": "actual running positions not in the stored result; cannot confirm"} |
| ROLE | OK | {"winner_pre_rank": 1, "second_pre_rank": 6, "third_pre_rank": 2, "winner_in_W": true, "second_in_P2": true, "third_in_P3": true} |
| KRS | OBSERVED | {"pre_result_utility_class": "MATERIAL-ACTIONABLE-SHADOW-DELTA", "post_result_evaluation": {"actual_top3": [4, 11, 6], "rescues": [], "supports": ["WINNER_ROLE_CONFIRMED", "P3_ROLE |
| TICKET | OK | {"head_local_p2": true, "pair_conditioned_third": true, "trio_set_covered": true, "ordered_pair_ticket_coverage": true, "top3_set_ticket_coverage": true, "ordered_exact_ticket_cove |
| CAPITAL | ISSUE | {"pfs": 63.8, "profit_loss": -2170, "hit_but_loss": true, "hit_but_loss_runtime_full_mec": true, "tickets": 60} |

## 改善提案（PROPOSED・自動採用なし）

| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |
|---|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | {"pfs": 63.8, "tickets": 60, "payout": 3830} | >=30 hit races: ticket-count reduction would also remove the hit | counterfactual MEC compression on frozen settled arms (no reselection) | PFS on hit races |
| P2:CALIBRATION_BACKLOG | P2 | "calibration status UNCALIBRATED" | n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条) | accumulate frozen predictions + results per venue/distance band; Brier/ECE once  | Brier score, ECE, capture |

<sub>review sha256 `547d42259d42e9f2`／Learning State `425fd8a00d05`</sub>
